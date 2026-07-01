# 07 · MCP 协议开发实战

> **能力层**：L3→L4　**难度**：★★★　**预计工时**：10h
> **一句话**：MCP（Model Context Protocol）是 Anthropic 2024 年底推出、2025 年迅速成为**行业标准**的"AI 工具/数据接入协议"——相当于 **AI 世界的 USB-C**。学会写 MCP Server，你的企业能力就能被 Cursor、Claude、任意 Agent 复用。
> **前置**：[06-Function Calling与Agent开发](./06-Function-Calling与Agent开发.md)。

---

## 一、MCP 解决了什么问题

上一篇的 Function Calling 有个痛点：**工具和应用绑死**。你为自己的 Agent 写的"查订单"工具，Cursor 用不了、别的团队的 Agent 也用不了，每个 AI 应用都要重复对接。

MCP 把"工具/数据/提示"标准化成协议：

```
没有 MCP（M×N 问题）：           有 MCP（M+N）：
每个 AI 应用 × 每个数据源          AI 应用 ─┐
都要单独对接                       Cursor ──┼─ MCP 协议 ─┬─ MCP Server(数据库)
= M×N 个集成                       Claude ──┘            ├─ MCP Server(订单系统)
                                                          └─ MCP Server(文件系统)
```

- **MCP Server**：暴露能力的一方（你写的，包住企业数据/工具）
- **MCP Client / Host**：使用能力的一方（Cursor、Claude Desktop、你的 Agent）
- 写一个 MCP Server，**所有支持 MCP 的 AI 应用都能用**

> 类比：MCP Server 之于 AI，就像 REST API 之于前端——标准接口，谁都能接。

---

## 二、MCP 的三种能力

一个 MCP Server 可以暴露三类东西：

| 能力 | 是什么 | 类比 | 例子 |
|------|--------|------|------|
| **Tools** | 可执行的操作（有副作用） | 函数调用 | 查订单、发邮件、执行SQL |
| **Resources** | 可读取的数据/上下文 | GET 资源 | 文件内容、数据库记录、日志 |
| **Prompts** | 预设的提示模板 | 模板 | "代码审查"、"生成周报" |

传输方式：
- **stdio**：本地进程，标准输入输出（Cursor/Claude Desktop 本地插件常用）
- **SSE / Streamable HTTP**：远程服务（企业内网部署，多客户端共享）

协议底层是 **JSON-RPC 2.0**。

---

## 三、用 Java 写 MCP Server（Spring AI MCP）

Spring AI 提供了 MCP Server/Client starter，Java 工程师可以直接把 Spring Bean 暴露成 MCP 工具。

### 3.1 依赖

```xml
<dependency>
    <groupId>org.springframework.ai</groupId>
    <artifactId>spring-ai-starter-mcp-server-webmvc</artifactId>
</dependency>
```

### 3.2 把业务方法暴露为 MCP Tool

```java
@Service
public class OrderMcpTools {

    @Tool(description = "根据订单号查询订单详情（只读）")
    public OrderInfo queryOrder(
            @ToolParam(description = "订单号") String orderId) {
        return orderService.getById(orderId);
    }

    @Tool(description = "查询某用户最近N笔订单")
    public List<OrderInfo> recentOrders(
            @ToolParam(description = "用户ID") Long userId,
            @ToolParam(description = "数量") int limit) {
        return orderService.recent(userId, limit);
    }
}
```

```java
@Configuration
public class McpConfig {
    @Bean
    public ToolCallbackProvider orderTools(OrderMcpTools tools) {
        return MethodToolCallbackProvider.builder().toolObjects(tools).build();
    }
}
```

```yaml
spring:
  ai:
    mcp:
      server:
        name: order-mcp-server
        version: 1.0.0
```

启动后，这个服务就是一个标准 MCP Server，暴露 SSE 端点。

### 3.3 暴露 Resource（只读数据）

```java
// 暴露一个"公司制度文档"资源，AI 可按 URI 读取
@Bean
public List<McpServerFeatures.SyncResourceSpecification> resources() {
    var resource = new McpSchema.Resource(
        "docs://handbook", "员工手册", "公司员工手册全文", "text/plain", null);
    return List.of(new McpServerFeatures.SyncResourceSpecification(resource,
        (exchange, req) -> new ReadResourceResult(
            List.of(new TextResourceContents(req.uri(), "text/plain", loadHandbook())))));
}
```

---

## 四、写 MCP Client（在你的 Agent 里用别人的 Server）

```xml
<dependency>
    <groupId>org.springframework.ai</groupId>
    <artifactId>spring-ai-starter-mcp-client</artifactId>
</dependency>
```

```yaml
spring:
  ai:
    mcp:
      client:
        sse:
          connections:
            order-server:
              url: http://localhost:8081
```

```java
// MCP Server 暴露的工具自动变成 ChatClient 可用的 tools
@Bean
ChatClient chatClient(ChatClient.Builder builder, ToolCallbackProvider mcpTools) {
    return builder.defaultTools(mcpTools).build();
}
// 现在你的 Agent 能自动调用 order-server 暴露的所有工具
```

---

## 五、在 Cursor 里挂载你的 MCP Server

写好的 MCP Server 可以直接给 Cursor 用（呼应 [05-工具与效率/Cursor操作手册](../00-通用/Cursor操作手册.md)）：

```json
// .cursor/mcp.json 或全局 MCP 配置
{
  "mcpServers": {
    "order-system": {
      "url": "http://localhost:8081/sse"
    },
    "local-fs": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path"]
    }
  }
}
```
挂上后，在 Cursor 里就能直接"帮我查一下订单 ORD123 的状态"，Cursor 会调用你的企业 MCP Server。

---

## 六、常见坑与安全

| 坑 | 现象 | 解法 |
|----|------|------|
| MCP Server 无鉴权 | 任何人连上就能调企业工具 | 加认证(Token/OAuth)、网络隔离、只在内网 |
| 暴露写/危险工具 | AI 客户端误操作 | 只暴露只读；写操作走确认流程，见 [06](./06-Function-Calling与Agent开发.md)/[09](./09-LLM安全与合规.md) |
| tool 描述不清 | 客户端模型调不对 | 同 Function Calling，认真写描述 |
| stdio vs SSE 选错 | 本地/远程场景不匹配 | 本地插件 stdio；企业共享 SSE/HTTP |
| 版本/协议不兼容 | 连接失败 | 关注 MCP spec 版本与 SDK 版本对齐 |
| 供应链风险 | 装了恶意第三方 MCP Server | 只用可信来源，审计其能力，最小权限 |
| 返回超大数据 | 撑爆上下文 | Resource/Tool 结果分页、截断 |

**安全原则**：MCP Server 是把企业能力对 AI 开放的门，**默认最小权限、默认只读、默认内网、默认鉴权**。

---

## 七、面试考点

- **Q：MCP 是什么？解决什么问题？**
  A：Model Context Protocol，Anthropic 提出的开放协议，标准化 AI 应用与工具/数据源的对接，把 M×N 集成变 M+N。被称为"AI 的 USB-C"。
- **Q：MCP 和 Function Calling 关系？**
  A：Function Calling 是模型调工具的能力（应用内绑定）；MCP 是把工具/数据标准化成协议供任意 AI 应用复用。MCP Server 内部常用 Function Calling 机制被客户端调用。
- **Q：MCP Server 能暴露哪几类能力？**
  A：Tools（可执行操作）、Resources（可读数据）、Prompts（提示模板）。传输用 stdio 或 SSE/HTTP，协议基于 JSON-RPC 2.0。
- **Q：MCP 的安全风险？**
  A：未鉴权暴露企业工具、暴露危险写操作、供应链（恶意 Server）。对策：鉴权、最小权限、只读优先、内网、审计。
- **Q：Java 怎么写 MCP Server？**
  A：Spring AI MCP Server starter，用 @Tool 把 Bean 方法暴露为工具，配 SSE/stdio 传输。

---

## 八、动手任务（本篇产出）

- [ ] **任务 1**：用 Spring AI MCP Server 把 [06](./06-Function-Calling与Agent开发.md) 的只读订单工具暴露成 MCP Server
- [ ] **任务 2**：把这个 Server 挂到 **Cursor** 里，在 Cursor 中用自然语言查询订单
- [ ] **任务 3**：写一个 MCP Client，让你的 Agent 消费另一个 MCP Server 的工具
- [ ] **任务 4**：给 MCP Server 加 Token 鉴权 + 只读约束
- [ ] **任务 5（了解）**：体验一个官方 MCP Server（filesystem / github），理解生态
- [ ] 记入 [项目实战清单](../00-通用/项目实战清单.md)

### 验收标准
- 你的 MCP Server 能被 Cursor 成功调用
- Client 能自动发现并使用 Server 暴露的工具
- 有鉴权，未授权连接被拒

---

## 九、延伸资源
- MCP 官方规范 modelcontextprotocol.io（spec / SDK / 官方 servers）
- Spring AI MCP 文档（server-webmvc / client starter）
- Cursor MCP 配置文档
- 下一篇：[08-AI 可观测与评测](./08-AI可观测与评测.md)

← [返回 06 索引](./README.md)
