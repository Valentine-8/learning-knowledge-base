# 06 · Function Calling 与 Agent 开发

> **能力层**：L3→L4　**难度**：★★★★　**预计工时**：18h
> **一句话**：让 LLM 不只是"说"，而是能"做"——调用你的 Java 方法/API 查数据、下命令，并自主规划多步任务。这是从"聊天机器人"到"智能体(Agent)"的跃迁。
> **前置**：[03-Spring AI](./03-Spring-AI与LangChain4j实战.md)、[05-RAG](./05-RAG系统工程化实战.md)。

---

## 一、Function Calling 到底发生了什么

**误区**：以为 LLM 会自己执行代码。**真相**：LLM 只会**告诉你它想调哪个函数、传什么参数**，真正的执行是**你的 Java 代码**干的。

流程：
```
1. 你把"可用工具清单"(名字/描述/参数schema)随 prompt 发给 LLM
2. LLM 判断需要工具 → 返回 finish_reason=tool_calls + {函数名, 参数JSON}
3. 【你的代码】解析并真正执行该 Java 方法
4. 把执行结果作为一条 message 再发回 LLM
5. LLM 基于结果生成最终自然语言回答（或继续调下一个工具）
```

关键认知：**LLM 是"大脑/决策者"，你的代码是"手/执行者"**。安全边界完全在你手里——LLM 想调什么，执行不执行、怎么执行你说了算。

---

## 二、Spring AI 实现 Function Calling

### 2.1 定义工具（@Tool）

```java
@Component
public class OrderTools {

    @Tool(description = "根据订单号查询订单状态和金额")
    public OrderInfo queryOrder(
            @ToolParam(description = "订单号，如 ORD20260701001") String orderId) {
        return orderService.getById(orderId);   // 真实调用你的业务
    }

    @Tool(description = "查询指定城市今天的天气")
    public String getWeather(@ToolParam(description = "城市名") String city) {
        return weatherClient.today(city);
    }
}
```

Spring AI 自动把方法名、`description`、参数类型转成 JSON schema 给模型。**description 写得好不好直接决定模型调不调、调得对不对**——把它当 API 文档认真写。

### 2.2 注册并调用

```java
String answer = chatClient.prompt()
    .user("我的订单 ORD20260701001 到哪了？顺便看看广州天气适不适合出门取货")
    .tools(orderTools)          // 模型会自主决定调用哪个、调几次
    .call()
    .content();
// 模型可能：先调 queryOrder，再调 getWeather，最后综合回答
```

Spring AI 内部自动完成"发起→接收 tool_calls→执行→回填→再生成"的循环，你只管定义工具和发问。

### 2.3 参数校验与类型
工具参数用强类型 record/枚举，Spring AI 生成更严格的 schema：
```java
@Tool(description = "创建工单")
public Ticket createTicket(
    @ToolParam(description="优先级") Priority priority,   // 枚举，模型只能选合法值
    @ToolParam(description="标题") String title) { ... }

enum Priority { LOW, MEDIUM, HIGH, URGENT }
```

---

## 三、从 Function Calling 到 Agent

**Function Calling 是能力，Agent 是模式。** Agent = LLM + 工具 + **循环** + **记忆/状态** + **规划**，能自主完成多步任务。

### 3.1 ReAct 模式（最经典）
Reasoning + Acting 交替：
```
Thought: 我需要先查订单状态
Action: queryOrder("ORD...")
Observation: 状态=已发货, 物流单号=SF123
Thought: 已发货，我该查物流
Action: queryLogistics("SF123")
Observation: 预计明天送达
Thought: 信息够了
Answer: 您的订单已发货，预计明天送达。
```

### 3.2 Agent 的循环控制（工程重点）

```java
public String runAgent(String task) {
    List<Message> messages = new ArrayList<>();
    messages.add(new UserMessage(task));
    int maxSteps = 10;                          // 防死循环，必须设上限
    for (int step = 0; step < maxSteps; step++) {
        ChatResponse resp = chatModel.call(new Prompt(messages, toolOptions));
        if (!hasToolCalls(resp)) {
            return resp.getResult().getOutput().getContent();  // 完成
        }
        // 执行工具（下节：安全确认）
        List<ToolResponse> results = executeTools(resp.getToolCalls());
        messages.add(resp.assistantMessage());
        messages.add(new ToolResponseMessage(results));
    }
    return "任务过于复杂，已达最大步数";           // 兜底
}
```

必备护栏：**最大步数、超时、总 token 预算、工具调用次数上限**——不然 Agent 可能无限循环烧钱。

### 3.3 人审确认（Human-in-the-Loop）—— 生产铁律

工具分两类，区别对待：

| 工具类型 | 举例 | 策略 |
|----------|------|------|
| **只读** | 查订单、查天气、搜文档 | 自动执行 |
| **写/危险** | 退款、删数据、发邮件、执行命令 | **必须人工确认后才执行** |

```java
if (tool.isMutating()) {
    // 不直接执行，返回"待确认操作"给前端，用户点确认再执行
    return AgentStep.awaitConfirmation(tool, args);
}
```
这是 Agent 安全的核心。绝不能让 LLM 自主执行"删库""转账"级操作。呼应 [09-安全](./09-LLM安全与合规.md)。

---

## 四、LangChain4j 的 Agent（声明式更简洁）

```java
interface OpsAgent {
    @SystemMessage("你是运维助手，能查询服务状态、重启服务（需确认）")
    String handle(String request);
}

OpsAgent agent = AiServices.builder(OpsAgent.class)
    .chatLanguageModel(model)
    .tools(new OpsTools())               // @Tool 注解的方法
    .chatMemory(MessageWindowChatMemory.withMaxMessages(20))
    .build();
```
LangChain4j 自动处理工具循环，代码极简；Spring AI 更可控。

---

## 五、多 Agent 与工作流（进阶了解）

单 Agent 搞不定复杂任务时，用**多 Agent 协作**或**固定工作流**：

| 模式 | 说明 | 何时用 |
|------|------|--------|
| 单 Agent + 工具 | 一个 LLM 循环调工具 | 大多数场景，**首选** |
| 工作流(Workflow) | 固定 DAG，节点可含 LLM | 步骤确定、要可控可测 |
| 多 Agent(Supervisor) | 主 Agent 调度子 Agent | 任务需专业分工 |
| Planner-Executor | 先规划再逐步执行 | 长任务 |

**经验**：能用确定性工作流解决的，别用自主 Agent（更可控、可测、便宜）。Agent 的自主性是双刃剑。

---

## 六、常见坑

| 坑 | 现象 | 解法 |
|----|------|------|
| tool description 太随意 | 模型不调/调错工具 | 像写 API 文档一样写描述和参数说明 |
| 无步数上限 | Agent 死循环烧钱 | maxSteps + token 预算 + 超时 |
| 让 LLM 直接执行写操作 | 误删/误退款 | 只读自动、写操作人工确认 |
| 工具抛异常没兜底 | 整个 Agent 崩 | 工具异常转成 Observation 文本喂回，让模型自愈或放弃 |
| 参数没校验 | 模型传非法值出事 | 强类型/枚举 + Java 侧校验 |
| 工具太多 | 模型选择困难、准确率降 | 控制单次可用工具数(<10~15)，或按场景动态裁剪 |
| 敏感工具无权限控制 | 越权调用 | 工具级鉴权，按用户角色暴露 |
| prompt 注入操纵工具 | 用户诱导调危险工具 | 输入隔离 + 工具白名单 + 人审，见 [09](./09-LLM安全与合规.md) |

---

## 七、面试考点

- **Q：Function Calling 时 LLM 真的执行代码吗？**
  A：不。LLM 只返回"要调哪个函数+参数"，实际执行是应用代码；结果再回填给 LLM。安全边界在应用侧。
- **Q：Agent 和普通 LLM 调用区别？**
  A：Agent = LLM + 工具 + 循环 + 状态/记忆 + 规划，能自主多步完成任务；普通调用是一问一答。
- **Q：ReAct 是什么？**
  A：Reasoning+Acting 交替：思考→行动(调工具)→观察结果→再思考，直到得出答案。
- **Q：Agent 生产上怎么保证安全？**
  A：只读工具自动执行、写/危险操作人工确认；最大步数/超时/token 预算；工具级鉴权；输入隔离防注入；全程审计日志。
- **Q：什么时候用 Agent，什么时候用固定工作流？**
  A：步骤确定、要可控可测→工作流；任务开放、需动态决策→Agent。能用工作流别滥用自主 Agent。
- **Q：工具描述为什么重要？**
  A：模型靠描述判断何时调、传什么参数，描述质量直接决定调用准确率。

---

## 八、动手任务（本篇产出）

- [ ] **任务 1**：用 Spring AI @Tool 定义 3 个只读工具（查订单/查天气/搜知识库-复用[05](./05-RAG系统工程化实战.md)）
- [ ] **任务 2**：实现一个能自主组合多个工具回答复杂问题的助手（如"我订单到哪了+要不要带伞"）
- [ ] **任务 3**：加一个写操作工具（如"创建工单"），实现**人工确认**才执行
- [ ] **任务 4**：手写 Agent 循环，加 maxSteps/超时/token 预算护栏，工具异常能自愈
- [ ] **任务 5**：用 LangChain4j AiServices 实现同一个 Agent，对比
- [ ] **任务 6（进阶）**：做一个"数据分析 Agent"：自然语言→生成SQL(工具)→执行(只读)→解读结果
- [ ] 记入 [项目实战清单](../00-通用/12-项目实战清单.md)

### 验收标准
- Agent 能正确选择并串联多个工具完成任务
- 写操作**一定**走人工确认，只读自动执行
- 有完整护栏，故意给死循环任务不会失控
- 能画出一次 Agent 多步执行的 Thought/Action/Observation 轨迹

---

## 九、延伸资源
- OpenAI Function Calling / Anthropic Tool Use 文档
- Spring AI Tool Calling、LangChain4j Tools 文档
- 论文：ReAct、Toolformer
- Anthropic《Building Effective Agents》（工作流 vs Agent 的经典指南）
- 下一篇：[07-MCP 协议开发实战](./07-MCP协议开发实战.md) —— 让工具标准化、可跨应用复用

← [返回 06 索引](./README.md)
