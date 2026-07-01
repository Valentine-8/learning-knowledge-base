# 02 · LLM API 集成实战（Java）

> **能力层**：L3 集成者　**难度**：★★★　**预计工时**：12h
> **一句话**：不依赖任何 AI 框架，用纯 Java（`HttpClient`/WebClient）直接调 LLM API，吃透流式、Token、成本、重试、限流、多模型路由——这是理解上层框架的地基。
> **前置**：[01-Prompt工程实战](./01-Prompt工程实战.md)、Spring Boot、HTTP 基础。

---

## 一、为什么要先学"裸调 API"

很多人上来就用 Spring AI / LangChain4j，结果一出问题（流式断了、token 超了、429 限流）完全不知道底层发生了什么。**先手写一遍裸调，你才能 debug 框架。**

OpenAI 的 Chat Completions API 已成为**事实标准**：通义千问、DeepSeek、Moonshot、智谱、以及本地的 Ollama/vLLM 都提供"OpenAI 兼容接口"。**学会一套，全部通用**，只是换 `base_url` 和 `model`。

---

## 二、API 心智模型

### 2.1 一次请求的结构

```
POST {base_url}/v1/chat/completions
Authorization: Bearer {api_key}
Content-Type: application/json

{
  "model": "qwen-plus",
  "messages": [
    {"role": "system", "content": "你是资深Java工程师"},
    {"role": "user",   "content": "解释volatile"}
  ],
  "temperature": 0.2,
  "max_tokens": 1024,
  "stream": false
}
```

三种 role：`system`（设定/约束）、`user`（用户输入）、`assistant`（模型历史回复，多轮时带上）。

### 2.2 响应结构

```json
{
  "choices": [{
    "message": {"role": "assistant", "content": "volatile 保证可见性..."},
    "finish_reason": "stop"
  }],
  "usage": {"prompt_tokens": 20, "completion_tokens": 150, "total_tokens": 170}
}
```

关键字段：
- `finish_reason`：`stop`(正常) / `length`(被max_tokens截断) / `tool_calls`(要调工具) / `content_filter`(被安全过滤)
- `usage`：**算钱的依据**，一定要记录

### 2.3 主流兼容 base_url

| 提供商 | base_url | 备注 |
|--------|----------|------|
| OpenAI | `https://api.openai.com/v1` | 原版 |
| 通义千问 | `https://dashscope.aliyuncs.com/compatible-mode/v1` | 中文/国内 |
| DeepSeek | `https://api.deepseek.com/v1` | 便宜、代码强 |
| Moonshot(Kimi) | `https://api.moonshot.cn/v1` | 长上下文 |
| 智谱 GLM | `https://open.bigmodel.cn/api/paas/v4` | |
| Ollama(本地) | `http://localhost:11434/v1` | 免费、离线，见[10](./10-本地模型部署与推理优化.md) |

---

## 三、纯 Java 实现（JDK 21 HttpClient，零依赖）

### 3.1 非流式调用

```java
import java.net.URI;
import java.net.http.*;
import com.fasterxml.jackson.databind.ObjectMapper;

public class LlmClient {
    private final HttpClient http = HttpClient.newHttpClient();
    private final ObjectMapper mapper = new ObjectMapper();
    private final String baseUrl = System.getenv("LLM_BASE_URL");
    private final String apiKey  = System.getenv("LLM_API_KEY");   // 绝不硬编码！

    public String chat(String system, String user) throws Exception {
        var body = Map.of(
            "model", "qwen-plus",
            "messages", List.of(
                Map.of("role", "system", "content", system),
                Map.of("role", "user",   "content", user)
            ),
            "temperature", 0.2
        );
        HttpRequest req = HttpRequest.newBuilder()
            .uri(URI.create(baseUrl + "/chat/completions"))
            .header("Authorization", "Bearer " + apiKey)
            .header("Content-Type", "application/json")
            .timeout(Duration.ofSeconds(60))
            .POST(HttpRequest.BodyPublishers.ofString(mapper.writeValueAsString(body)))
            .build();

        HttpResponse<String> resp = http.send(req, HttpResponse.BodyHandlers.ofString());
        if (resp.statusCode() != 200) {
            throw new LlmException("LLM error " + resp.statusCode() + ": " + resp.body());
        }
        JsonNode root = mapper.readTree(resp.body());
        return root.at("/choices/0/message/content").asText();
    }
}
```

> 🔑 **API Key 管理**：用环境变量 / Vault / 配置中心，**永远不要**写进代码或提交到 Git。见 [09-安全](./09-LLM安全与合规.md)。

### 3.2 流式调用（SSE，打字机效果）

流式是 LLM 应用体验的关键——用户不用等全部生成完。响应是 `text/event-stream`，每行 `data: {...}`，最后 `data: [DONE]`。

```java
public void chatStream(String user, Consumer<String> onToken) throws Exception {
    var body = Map.of(
        "model", "qwen-plus",
        "messages", List.of(Map.of("role", "user", "content", user)),
        "stream", true                       // 关键
    );
    HttpRequest req = HttpRequest.newBuilder()
        .uri(URI.create(baseUrl + "/chat/completions"))
        .header("Authorization", "Bearer " + apiKey)
        .header("Content-Type", "application/json")
        .POST(HttpRequest.BodyPublishers.ofString(mapper.writeValueAsString(body)))
        .build();

    // 按行接收流
    http.send(req, HttpResponse.BodyHandlers.ofLines())
        .body()
        .filter(line -> line.startsWith("data: "))
        .map(line -> line.substring(6))
        .takeWhile(data -> !data.equals("[DONE]"))
        .forEach(data -> {
            try {
                JsonNode delta = mapper.readTree(data).at("/choices/0/delta/content");
                if (!delta.isMissingNode()) onToken.accept(delta.asText());
            } catch (Exception ignore) {}
        });
}
```

### 3.3 在 Spring 里把流式透传给前端（SSE）

```java
@RestController
public class ChatController {
    private final LlmClient llm;

    @GetMapping(value = "/chat/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public SseEmitter stream(@RequestParam String q) {
        SseEmitter emitter = new SseEmitter(120_000L);
        Executors.newVirtualThreadPerTaskExecutor().submit(() -> {   // JDK21 虚拟线程，IO密集完美
            try {
                llm.chatStream(q, token -> {
                    try { emitter.send(token); } catch (IOException e) { emitter.completeWithError(e); }
                });
                emitter.complete();
            } catch (Exception e) {
                emitter.completeWithError(e);
            }
        });
        return emitter;
    }
}
```

前端用 `EventSource` 或 fetch stream 接收即可实现打字机效果。

---

## 四、生产必备的横切能力

裸调只是能跑。上生产还要解决这些：

### 4.1 重试与退避（应对 429/5xx）
LLM API 经常 429（限流）、503（过载）。用指数退避 + 抖动。

```java
// 用 Resilience4j 或 Spring Retry
@Retryable(
    retryFor = {LlmRateLimitException.class, LlmServerException.class},
    maxAttempts = 4,
    backoff = @Backoff(delay = 1000, multiplier = 2, random = true)  // 1s,2s,4s + 抖动
)
public String chatWithRetry(String system, String user) { ... }
```

**注意**：只对**可重试错误**重试（429/5xx/超时）；400（你的请求错）、401（key 错）重试无意义。

### 4.2 超时
LLM 慢是常态，长文本可能几十秒。分层设：连接超时短（5s），读取超时长（60~120s）。流式场景用"首 token 超时"更合理。

### 4.3 限流（保护自己和账户）
- 客户端限流：`Semaphore` / Resilience4j RateLimiter，控制并发请求数
- 令牌预算：按 `usage` 累计，超日预算熔断（见 [12-成本](./12-AI应用架构与成本工程.md)）

### 4.4 Token 计算与成本核算
调用前预估、调用后记账。

```java
public record CostRecord(String model, int promptTokens, int completionTokens, BigDecimal cost) {}

// 计费（示例：通义 qwen-plus，价格以官方为准，元/千token）
BigDecimal INPUT_PRICE  = new BigDecimal("0.0008");
BigDecimal OUTPUT_PRICE = new BigDecimal("0.002");
BigDecimal cost = INPUT_PRICE.multiply(BigDecimal.valueOf(promptTokens))
        .add(OUTPUT_PRICE.multiply(BigDecimal.valueOf(completionTokens)))
        .divide(BigDecimal.valueOf(1000));
```

> Token 预估用 tokenizer 库（如 `jtokkit` for OpenAI 系）。中文约 **1 token ≈ 1~1.5 汉字**，英文约 **1 token ≈ 0.75 词**。

### 4.5 结构化输出（JSON Mode）
让程序能稳定解析（呼应 [01](./01-Prompt工程实战.md) §结构化输出）：

```java
var body = Map.of(
    "model", "qwen-plus",
    "messages", messages,
    "response_format", Map.of("type", "json_object"),  // 强制合法 JSON
    "temperature", 0
);
```
> 更强的是 **Structured Output**（传 JSON Schema，模型保证符合 schema），OpenAI/部分模型支持。

### 4.6 多模型路由与降级
生产要能**一键切模型**：主模型挂了降级到备用，贵模型限流时降到便宜模型。

```java
public interface ChatProvider { String chat(String s, String u); String name(); }

@Service
public class RoutingChatService {
    private final List<ChatProvider> providers;  // 按优先级：主 → 备
    public String chat(String s, String u) {
        for (ChatProvider p : providers) {
            try { return p.chat(s, u); }
            catch (Exception e) { log.warn("provider {} failed, fallback", p.name(), e); }
        }
        throw new LlmException("all providers failed");
    }
}
```

---

## 五、多轮对话与上下文管理

LLM 是**无状态**的——每次请求你都要把历史 `messages` 全发过去。所以要自己管会话。

```java
// 用 Redis 存会话，控制窗口（防止 token 无限增长）
public List<Message> buildMessages(String sessionId, String newUserMsg) {
    List<Message> history = redisTemplate.opsForList()
        .range("chat:" + sessionId, -20, -1);   // 只保留最近 N 轮
    // 或按 token 预算截断：从新到旧累加，超预算就停
    history.add(new Message("user", newUserMsg));
    return history;
}
```

窗口管理三种策略：
1. **固定轮数**：只留最近 N 轮（简单，可能丢重要信息）
2. **Token 预算**：按 token 累计截断（更精确）
3. **摘要压缩**：老对话让 LLM 总结成一段，节省 token（进阶）

---

## 六、常见坑

| 坑 | 现象 | 解法 |
|----|------|------|
| API Key 硬编码/提交 Git | 泄露被盗刷 | 环境变量/Vault + `.gitignore` + git-secrets 扫描 |
| 没处理 `finish_reason=length` | 输出被截断还当正常 | 检查 finish_reason，length 则增大 max_tokens 或续写 |
| 流式没处理断连 | 前端卡住 | SSE 心跳 + 超时 + 前端重连 |
| 多轮把全部历史发过去 | token 爆炸、越来越贵 | 窗口截断 / 摘要压缩 |
| 用普通线程池扛流式 | 线程被 IO 阻塞耗尽 | JDK21 虚拟线程 / WebFlux 响应式 |
| 429 直接失败 | 高峰全挂 | 指数退避重试 + 客户端限流 |
| 不记 usage | 月底账单爆炸不知道花哪了 | 每次调用落库 token/成本 |
| temperature 默认 | 结构化输出不稳定 | 解析类任务 temperature=0 |

---

## 七、面试考点

- **Q：LLM API 是有状态还是无状态？多轮对话怎么实现？**
  A：无状态。每次请求要携带完整 messages 历史；服务端自己用 Redis 等管理会话并做窗口截断。
- **Q：流式响应底层是什么协议？Java 怎么实现？**
  A：SSE（Server-Sent Events，`text/event-stream`）。Java 用 HttpClient 的 `ofLines()` 解析 `data:` 行，Spring 用 `SseEmitter`/WebFlux 透传给前端。
- **Q：怎么控制 LLM 调用成本？**
  A：token 预估+记账、缓存重复请求、控制上下文窗口、便宜/贵模型分级路由、日预算熔断。（详见 [12](./12-AI应用架构与成本工程.md)）
- **Q：调用失败怎么办？**
  A：区分错误类型，429/5xx/超时指数退避重试，永久错误不重试；多 provider 降级；最终失败给用户兜底文案。
- **Q：为什么用虚拟线程/响应式处理 LLM 调用？**
  A：LLM 调用是长耗时 IO，传统线程池会被阻塞占满；虚拟线程(JDK21)或 WebFlux 能用少量线程扛大量并发等待。

---

## 八、动手任务（本篇产出）

- [ ] **任务 1**：用纯 JDK HttpClient 实现非流式 + 流式两个方法，接 Ollama 本地模型（免 key）
- [ ] **任务 2**：Spring Boot 暴露 `/chat/stream` SSE 接口，前端页面看到打字机效果
- [ ] **任务 3**：加上重试(Resilience4j) + Token 记账(落库) + 多 provider 降级
- [ ] **任务 4**：Redis 多轮会话 + 窗口截断，实现一个能连续对话的 mini-chat
- [ ] **任务 5**：对比裸调 vs 下一篇的 Spring AI，写一段"框架帮我省了什么"

### 验收标准
- 流式接口能稳定输出，断连有兜底
- 每次调用都能在日志/DB 看到 model/tokens/cost
- 主模型故意配错 key，能自动降级到备用不报错给用户

---

## 九、延伸资源
- OpenAI API Reference（chat/completions、streaming、structured outputs）
- 通义千问 / DeepSeek OpenAI 兼容模式文档
- `jtokkit`（Java tokenizer）、Resilience4j 文档
- 下一篇：[03-Spring AI 与 LangChain4j 实战](./03-Spring-AI与LangChain4j实战.md)

← [返回 06 索引](./README.md)
