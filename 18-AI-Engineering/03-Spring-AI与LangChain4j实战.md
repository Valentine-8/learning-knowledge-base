# 03 · Spring AI 与 LangChain4j 实战

> **能力层**：L3 集成者　**难度**：★★★　**预计工时**：14h
> **一句话**：Java 生态两大 AI 框架，把上一篇的裸调 API 封装成优雅、可测试、可扩展的工程组件——ChatClient、Advisor、记忆、结构化输出、RAG、Tool 一站式。
> **前置**：[02-LLM-API集成实战](./02-LLM-API集成实战(Java).md)、Spring Boot 3.x。

---

## 一、两个框架怎么选

| 维度 | Spring AI | LangChain4j |
|------|-----------|-------------|
| 出身 | Spring 官方（Pivotal/VMware） | 社区（对标 Python LangChain） |
| 风格 | Spring 原生，`ChatClient` 流式 API | 更贴近 LangChain，`AiServices` 声明式 |
| 集成 | 与 Spring Boot/Cloud 无缝，自动配置 | 也有 spring-boot-starter |
| 抽象 | ChatClient / Advisor / VectorStore | ChatModel / AiServices / Tools |
| 适合 | 已有 Spring 全家桶项目（**你的主场**） | 想要 LangChain 心智、多框架迁移 |
| 版本 | 1.0 GA（2025） | 1.0（2025） |

**建议**：你是 Spring 背景，**主学 Spring AI**，LangChain4j 了解其声明式 `AiServices`（很优雅）作为补充。本篇两者都给例子。

---

## 二、Spring AI 快速上手

### 2.1 依赖与配置

```xml
<dependency>
    <groupId>org.springframework.ai</groupId>
    <artifactId>spring-ai-openai-spring-boot-starter</artifactId>
</dependency>
```

```yaml
# application.yml  —— 用 OpenAI 兼容接口接通义/DeepSeek/Ollama
spring:
  ai:
    openai:
      base-url: https://dashscope.aliyuncs.com/compatible-mode
      api-key: ${LLM_API_KEY}
      chat:
        options:
          model: qwen-plus
          temperature: 0.3
```

### 2.2 ChatClient —— 核心入口

```java
@Service
public class AssistantService {
    private final ChatClient chatClient;

    public AssistantService(ChatClient.Builder builder) {
        this.chatClient = builder
            .defaultSystem("你是资深 Java 架构师，回答简洁准确。")
            .build();
    }

    // 最简单一次问答
    public String ask(String question) {
        return chatClient.prompt()
            .user(question)
            .call()
            .content();
    }

    // 流式
    public Flux<String> askStream(String question) {
        return chatClient.prompt().user(question).stream().content();
    }
}
```

### 2.3 结构化输出（`.entity()` —— 杀手锏）

Spring AI 自动把 LLM 输出映射成 Java 对象，无需手动解析 JSON。

```java
public record Recipe(String name, List<String> ingredients, List<String> steps) {}

public Recipe getRecipe(String dish) {
    return chatClient.prompt()
        .user("给我" + dish + "的菜谱")
        .call()
        .entity(Recipe.class);     // 自动生成 schema + 解析
}

// 也支持泛型集合
List<Recipe> list = chatClient.prompt().user("给3个川菜菜谱")
    .call().entity(new ParameterizedTypeReference<List<Recipe>>() {});
```

> 底层：Spring AI 把 record 结构转成 JSON schema 塞进 prompt，并要求 JSON 输出，再用 Jackson 反序列化。呼应 [01](./01-Prompt工程实战.md)/[02](./02-LLM-API集成实战(Java).md) 的结构化输出。

---

## 三、Advisor 机制（Spring AI 的 AOP）

Advisor 是 Spring AI 的**拦截器/责任链**，在请求前后做增强：记忆、RAG、日志、安全过滤都靠它。这是 Spring AI 设计的精髓。

```java
chatClient.prompt()
    .advisors(
        new MessageChatMemoryAdvisor(chatMemory),         // 自动带上历史（记忆）
        new QuestionAnswerAdvisor(vectorStore),           // 自动 RAG 检索注入
        new SimpleLoggerAdvisor()                         // 打印请求/响应日志
    )
    .user(question)
    .call().content();
```

### 3.1 对话记忆（Chat Memory）
不用再像裸调那样手写 Redis 会话管理：

```java
@Bean
ChatMemory chatMemory() {
    return new InMemoryChatMemory();   // 或自定义 Redis/JDBC 实现
}

// 调用时带上 conversationId
chatClient.prompt()
    .advisors(a -> a.param(CHAT_MEMORY_CONVERSATION_ID_KEY, sessionId)
                    .param(CHAT_MEMORY_RETRIEVE_SIZE_KEY, 20))
    .user(msg).call().content();
```

### 3.2 自定义 Advisor（比如敏感词/成本记账）

```java
public class CostLoggingAdvisor implements CallAroundAdvisor {
    @Override
    public AdvisedResponse aroundCall(AdvisedRequest req, CallAroundAdvisorChain chain) {
        long start = System.currentTimeMillis();
        AdvisedResponse resp = chain.nextAroundCall(req);
        Usage usage = resp.response().getMetadata().getUsage();
        log.info("tokens in={} out={} cost estimate...", usage.getPromptTokens(), usage.getGenerationTokens());
        return resp;
    }
    @Override public String getName() { return "cost-logging"; }
    @Override public int getOrder() { return 0; }
}
```

---

## 四、Spring AI 集成 RAG（预告，详见 05）

一旦有了 VectorStore，RAG 只是加一个 Advisor：

```java
@Bean
VectorStore vectorStore(EmbeddingModel embeddingModel, JdbcTemplate jdbc) {
    return new PgVectorStore(jdbc, embeddingModel);   // 见 04
}

// 问答自动检索相关文档并注入 prompt
String answer = chatClient.prompt()
    .advisors(new QuestionAnswerAdvisor(vectorStore, SearchRequest.defaults().withTopK(4)))
    .user(question)
    .call().content();
```

完整 RAG 工程化（分块、rerank、评估）见 [05-RAG系统工程化](./05-RAG系统工程化实战.md)。

---

## 五、Spring AI 集成 Tool / Function Calling（预告，详见 06）

```java
@Service
public class WeatherTools {
    @Tool(description = "查询指定城市的实时天气")
    public String getWeather(@ToolParam(description = "城市名") String city) {
        return weatherApi.query(city);   // 真实调用你的服务
    }
}

// 注册工具，模型会在需要时自动调用
String result = chatClient.prompt()
    .user("北京今天天气怎么样，适合跑步吗？")
    .tools(weatherTools)
    .call().content();
```

Agent、多步规划、人审确认见 [06-Function Calling与Agent开发](./06-Function-Calling与Agent开发.md)。

---

## 六、LangChain4j 对照（声明式 AiServices 很优雅）

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-open-ai-spring-boot-starter</artifactId>
</dependency>
```

**声明式接口**——你只定义接口，LangChain4j 生成实现：

```java
interface Assistant {
    @SystemMessage("你是资深Java架构师")
    String chat(String userMessage);

    // 自动结构化输出
    @UserMessage("从下面文本抽取人名和公司：{{it}}")
    PersonInfo extract(String text);
}

// 一行创建
Assistant assistant = AiServices.builder(Assistant.class)
    .chatLanguageModel(model)
    .chatMemory(MessageWindowChatMemory.withMaxMessages(20))
    .contentRetriever(retriever)     // RAG
    .tools(new WeatherTools())       // 工具
    .build();

String answer = assistant.chat("解释一下CAP理论");
```

对比：Spring AI 是**流式 builder API**，LangChain4j 是**注解声明式**。声明式代码更少，Spring AI 与 Spring 生态贴合更紧。

---

## 七、常见坑

| 坑 | 现象 | 解法 |
|----|------|------|
| `.entity()` 解析失败 | 模型没返回合法 JSON | temperature=0；prompt 强调格式；用支持 structured output 的模型 |
| 记忆无限增长 | token 越来越多变贵/超限 | Advisor 设 retrieve size / 窗口；或摘要压缩 |
| Advisor 顺序错 | RAG 检索没生效/记忆错乱 | 注意 `getOrder()`，记忆和RAG advisor 顺序有讲究 |
| base-url 配错路径 | 404 | 通义兼容模式 base-url 不含 `/v1`，Spring AI 会自动补 |
| 版本混用 | 编译/运行报错 | Spring AI 1.0 GA 与 Boot 3.3/3.4 版本对齐，用 BOM |
| 同步阻塞用错 | 高并发线程耗尽 | 流式用 `.stream()` 返回 Flux；配合虚拟线程 |
| 工具无限循环 | 模型反复调用工具 | 限制最大工具调用轮数 |

---

## 八、面试考点

- **Q：Spring AI 的 ChatClient 和 Advisor 分别是什么？**
  A：ChatClient 是统一的对话入口（流式 builder API）；Advisor 是责任链拦截器，用来插入记忆、RAG、日志、安全等横切能力，类似 Spring 的拦截器/AOP。
- **Q：Spring AI 怎么实现结构化输出？**
  A：`.entity(Xxx.class)`，框架把目标类型转成 JSON schema 注入 prompt，要求模型返回 JSON，再用 Jackson 反序列化。
- **Q：Spring AI 和 LangChain4j 区别？**
  A：Spring AI 官方、流式 builder、Spring 生态无缝；LangChain4j 社区、声明式 AiServices、对标 Python LangChain。功能大致对等，Spring 项目优先 Spring AI。
- **Q：框架相比裸调 API 帮你解决了什么？**
  A：统一多模型抽象、结构化输出、记忆管理、RAG/Tool 集成、可观测、重试——把 02 篇里手写的横切能力标准化了。
- **Q：对话记忆怎么做，如何防止 token 爆炸？**
  A：ChatMemory + conversationId，配窗口大小/token 预算/摘要压缩。

---

## 九、动手任务（本篇产出）

- [ ] **任务 1**：Spring AI 起一个 ChatClient，接通义/Ollama，实现同步+流式两个接口
- [ ] **任务 2**：用 `.entity()` 做一个"文本→结构化对象"抽取服务（如简历解析成 record）
- [ ] **任务 3**：加 MessageChatMemoryAdvisor 实现多轮记忆 + SimpleLoggerAdvisor
- [ ] **任务 4**：写一个自定义 Advisor 做 token 成本记账
- [ ] **任务 5**：用 LangChain4j 的 AiServices 实现同样的抽取接口，对比代码量与体验
- [ ] **任务 6**：把成果记入 [项目实战清单](../00-通用/项目实战清单.md)

### 验收标准
- 能画出 Spring AI 请求经过 Advisor 链的流程图
- `.entity()` 抽取服务解析成功率 100%
- 多轮对话记得住上文，且 token 有上限控制

---

## 十、延伸资源
- Spring AI 官方文档 docs.spring.io/spring-ai（ChatClient / Advisors / VectorStore）
- LangChain4j 官方文档 docs.langchain4j.dev（AiServices / Tools / RAG）
- 下一篇：[04-Embedding 与向量数据库实战](./04-Embedding与向量数据库实战.md)

← [返回 06 索引](./README.md)
