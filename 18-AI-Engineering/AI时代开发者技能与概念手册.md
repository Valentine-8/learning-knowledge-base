# AI 时代开发者技能清单与概念详解手册

> **适用人群**：Java / 后端 / 全栈工程师（尤其 3～7 年经验），希望在 AI 时代从「用 AI 写代码」升级到「用 AI 构建产品 + 把 AI 嵌入业务系统」。  
> **文档结构**：Part A 技能清单 → Part B 概念百科 → Part C 工具栈 → Part D 学习路线 → Part E 风险与伦理。

---

## 文档导航

| 文档 | 用途 |
|------|------|
| [README.md](../../README.md) | 总入口 |
| [统一主路线.md](../00-通用/统一主路线.md) | Java + AI 并行时间表 |
| [7年Java工程师学习路线.md](../../01-Java/7年Java工程师学习路线.md) | Java 主线 |
| [个人基线评估.md](../00-通用/个人基线评估.md) | AI 技能自评（第十节） |
| [学习进度追踪.md](../00-通用/学习进度追踪.md) | AI 阶段勾选 |
| [项目实战清单.md](../00-通用/项目实战清单.md) | P13～P15 AI 项目 |
| [资源书签.md](../00-通用/资源书签.md) | AI 工具链接 |

---

# Part A：AI 时代开发者应掌握的技能清单

## 技能分层说明

| 层级 | 含义 | 7 年工程师目标 |
|------|------|----------------|
| L1 使用者 | 会用 ChatGPT/Cursor 辅助日常编码 | 必须 |
| L2 驾驭者 | 能设计 Prompt、Review AI 代码、建立个人工作流 | 必须 |
| L3 集成者 | 能在 Java/Spring 应用中集成 LLM、RAG、Agent | 应该 |
| L4 架构者 | 能设计 AI 系统架构、评估成本/效果/风险 | 进阶 |
| L5 建设者 | 能训练/微调、部署模型、构建 AI 平台 | 按方向选 1 项深入 |

---

## 一、AI 辅助编程（L1～L2，必须精通）

### 1.1 IDE 内 AI 编程工具

| 技能项 | 等级 | 具体能力 |
|--------|------|----------|
| Cursor / GitHub Copilot / 通义灵码 等 | L2 | 熟练 Tab 补全、Chat、Composer/Agent 模式 |
| 多文件编辑（Agent 模式） | L2 | 能描述需求让 AI 跨文件修改，并 Review diff |
| Cursor Rules（`.cursor/rules`） | L2 | 为项目写编码规范、架构约束，让 AI 输出符合团队风格 |
| Cursor Skills | L2 | 理解 Skill 是「可复用的任务 SOP」，会编写 SKILL.md |
| Cursor Hooks | L1→L2 | 自动化：保存时检查、提交前 lint、Agent 事件触发 |
| @ 引用上下文 | L2 | 精准引用文件、文件夹、文档、Git diff、终端输出 |
| .cursorignore | L2 | 排除 node_modules、密钥文件、大二进制，避免污染上下文 |

**实战标准**
- 用自然语言完成一个 CRUD 模块，但 **每一行 diff 都人工 Review**
- 为当前 Java 项目写一份 `.cursor/rules`，包含：包结构、异常处理、日志规范
- 能在 30 分钟内用 AI 完成：单元测试生成 + Bug 定位 + 修复，并说明验证了哪些点

---

### 1.2 Prompt 工程（面向 coding）

| 技能项 | 等级 | 具体能力 |
|--------|------|----------|
| 任务分解 | L2 | 大需求拆成：分析 → 设计 → 实现 → 测试，逐步 Prompt |
| 上下文供给 | L2 | 提供：目标、约束、现有代码、错误日志、期望输出格式 |
| 角色设定 | L2 | 「你是资深 Java 架构师，项目使用 Spring Boot 3 + MyBatis」 |
| 输出格式约束 | L2 | 要求 JSON / Markdown 表格 / 仅输出 diff / 分步骤编号 |
| Few-shot 示例 | L2 | 给 1～2 个「输入→期望输出」样例，统一代码风格 |
| Chain-of-Thought | L2 | 「先分析原因，再给出方案，最后写代码」 |
| 反向 Prompt | L2 | 让 AI 先提问澄清需求，再动手 |
| Prompt 迭代 | L2 | 同一任务 3 轮优化 Prompt，记录哪句指令最有效 |

**常用 Prompt 模板（Coding）**

```markdown
## 背景
[业务场景 1～2 句]

## 技术栈
Java 17, Spring Boot 3.2, MyBatis-Plus, Redis

## 现有代码
@OrderService.java @OrderMapper.xml

## 任务
实现订单超时自动取消，要求：
1. 延迟消息（RocketMQ）而非定时扫表
2. 幂等
3. 单元测试覆盖核心路径

## 约束
- 不引入新中间件
- 遵循项目现有异常类 BizException
- 先输出设计方案（300 字内），我确认后再写代码

## 输出格式
方案 → 类图（Mermaid）→ 代码 → 测试
```

**实战标准**
- 维护个人「Prompt 模板库」至少 10 条（CR、重构、排错、写测试、写设计文档）
- 知道何时 **不用 AI**：安全敏感逻辑、核心算法、未读 diff 就合并

---

### 1.3 AI 代码 Review 与质量把控

| 技能项 | 等级 | 说明 |
|--------|------|------|
| AI 产出可信度判断 | L2 | 识别：幻觉 API、过时语法、逻辑漏洞、安全漏洞 |
| 差异 Review | L2 | 逐文件看 diff，不整包接受 |
| 测试驱动验证 | L2 | AI 写代码 → 你必须写/跑测试，不信任「应该没问题」 |
| 安全审查 | L2 | SQL 注入、硬编码密钥、依赖漏洞、日志泄露 PII |
| 许可证合规 | L1 | AI 生成代码的版权与开源协议风险（公司政策） |
| 技术债识别 | L2 | AI 爱过度抽象、重复代码、忽略边界条件 |

**必须人工检查的 8 类 AI 代码问题**
1. 编造不存在的方法/类/依赖版本  
2. 错误的事务边界与并发安全  
3. 吞异常、空 catch  
4. N+1 查询、缺失索引  
5. 硬编码配置与密钥  
6. 测试 Mock 过度导致假绿  
7. 忽略幂等与重复提交  
8. 日志打印敏感字段  

---

### 1.4 AI 增强的开发工作流

| 场景 | AI 用法 | 技能要求 |
|------|---------|----------|
| 读源码 | 让 AI 解释 Spring 启动流程，对照源码验证 | L2 |
| 写单元测试 | Mockito + JUnit5 批量生成，人工补边界 | L2 |
| 写集成测试 | Testcontainers 场景描述 | L2 |
| 性能分析 | 贴 GC 日志 / 火焰图让 AI 辅助解读 | L2 |
| 写 SQL | 贴 explain 结果，要求 AI 解释并优化 | L2 |
| 写文档 | API 文档、README、ADR，人工校对事实 | L2 |
| Git Commit | 生成 message，符合团队规范 | L1 |
| Code Review | AI 初筛 + 人工终审 | L2 |
| 故障排查 | 贴 stack trace + 相关代码，结构化排查 | L2 |
| 遗留系统 | 先让 AI 画调用链、数据流，再改 | L2 |

---

## 二、AI 应用开发（L3，Java 工程师核心增量）

### 2.1 LLM API 集成

| 技能项 | 等级 | 说明 |
|--------|------|------|
| OpenAI 兼容 API 调用 | L3 | Chat Completions、Streaming、Function Calling |
| 国内模型 API | L3 | 通义千问、文心、智谱、DeepSeek、Moonshot 等 |
| Spring AI | L3 | ChatClient、Prompt、Advisor、VectorStore 抽象 |
| LangChain4j | L3 | Java 版 Agent、Tool、Memory、RAG 链 |
| 流式响应 SSE | L3 | WebFlux / SseEmitter 向前端推送 token |
| 重试与降级 | L3 | 超时、限流、备用模型、缓存常见问题 |
| Token 成本估算 | L3 | 按输入/输出 token 粗算单次请求成本 |

**Spring AI 最小能力**
```java
// 概念性示例 — 需按实际版本调整
ChatResponse response = chatClient.prompt()
    .user("根据订单号查询物流，订单号：{orderId}", orderId)
    .call()
    .chatResponse();
```

---

### 2.2 RAG（检索增强生成）

| 技能项 | 等级 | 说明 |
|--------|------|------|
| RAG 全流程 | L3 | 加载 → 切分 → 向量化 → 存储 → 检索 → 重排 → 生成 |
| 文档切分策略 | L3 | 固定长度、按标题、Recursive、语义切分 |
| Embedding 模型选型 | L3 | text-embedding-3-small、BGE、M3E 等 |
| 向量数据库 | L3 | Milvus、Qdrant、Pgvector、Elasticsearch kNN |
| 混合检索 | L3 | 向量 + BM25 关键词 + RRF 融合 |
| Reranker | L3 | Cohere Rerank、BGE-Reranker 提升 Top-K 质量 |
| 引用溯源 | L3 | 回答标注 chunk 来源，减少胡编 |
| 评估 RAG | L3 | 命中率、答案相关性、幻觉率 |

---

### 2.3 Agent 与工具调用

| 技能项 | 等级 | 说明 |
|--------|------|------|
| Agent 循环 | L3 | Thought → Action → Observation → 直到完成 |
| Function Calling / Tool Use | L3 | 模型决定调用哪个 Java 方法/API |
| ReAct 模式 | L3 | Reasoning + Acting 提示结构 |
| Plan-and-Execute | L3 | 先规划步骤再逐步执行 |
| Multi-Agent | L4 | 多角色协作（研究员、编码员、审查员） |
| Human-in-the-loop | L3 | 敏感操作需人工确认 |
| MCP（Model Context Protocol） | L3 | 标准化「模型 ↔ 工具/数据源」连接协议 |
| 工具设计原则 | L3 | 原子性、幂等、清晰描述、错误可观测 |

**Java 后端常见 Tool 示例**
- 查询订单/库存（内部 RPC）
- 执行只读 SQL
- 发送钉钉/邮件通知
- 检索知识库（RAG）
- 创建 Jira Ticket

---

### 2.4 记忆与上下文管理

| 技能项 | 等级 | 说明 |
|--------|------|------|
| Context Window 限制 | L3 | 理解 8K/32K/128K/1M 差异与成本 |
| 短期记忆 | L3 | 滑动窗口、摘要压缩 |
| 长期记忆 | L3 | 向量库存用户偏好/历史对话 |
| Session 管理 | L3 | Redis 存 conversationId → messages |
| System Prompt 设计 | L3 | 角色、边界、拒绝策略、输出格式 |

---

### 2.5 Prompt 工程（面向产品）

| 技能项 | 等级 | 说明 |
|--------|------|------|
| System / User / Assistant 消息结构 | L3 | |
| JSON Mode / Structured Output | L3 | 强制输出 schema，便于程序解析 |
| Prompt 版本管理 | L3 | Git 管理 template，A/B 测试 |
| Prompt 注入防护 | L3 | 输入过滤、分隔符、权限隔离 |
| 多语言 / 多租户 Prompt | L3 | 模板参数化 |

---

## 三、模型与训练基础（L4～L5，理解 + 选修）

| 技能项 | 等级 | 说明 |
|--------|------|------|
| Transformer 基本原理 | L3 理解 | Self-Attention、Encoder-Decoder |
| 预训练 / 微调 / RLHF 区别 | L3 | 知道何时该微调而非 RAG |
| SFT（监督微调） | L4 | 领域语料、指令数据集 |
| LoRA / QLoRA | L4 | 低成本微调，Java 工程师了解即可 |
| 量化（INT8/INT4/GPTQ） | L4 | 推理加速、降显存 |
| 模型部署 | L4 | Ollama、vLLM、TGI、Triton |
| GPU / NPU 基础 | L4 | 显存、batch、吞吐 vs 延迟 |
| 模型评估 | L4 | BLEU、ROUGE、人工评估、LLM-as-Judge |
| 开源模型 | L3 | Llama、Qwen、DeepSeek、Mistral 能力边界 |

**决策树：该用哪种方案？**
```
私有数据问答
├── 知识更新频繁？ → RAG（首选）
├── 固定格式输出/领域术语多？ → Prompt + Few-shot
├── 需要改变模型行为/风格？ → 微调（SFT/LoRA）
└── 需要实时工具操作？ → Agent + Function Calling
```

---

## 四、AI 系统架构（L4）

| 技能项 | 等级 | 说明 |
|--------|------|------|
| AI 网关 | L4 | 统一鉴权、限流、路由多模型、审计 |
| 异步任务队列 | L4 | 长文档解析、批量 Embedding 走 MQ |
| 缓存策略 | L4 | 相同问题缓存、Embedding 缓存 |
| 可观测性 | L4 | Trace 每次 LLM 调用的 latency、token、prompt 版本 |
| 成本治理 | L4 | 按部门/用户配额、用小模型做路由 |
| 安全架构 | L4 | 数据不出域、VPC、私有化部署 |
| 降级方案 | L4 | 模型不可用 → 规则引擎 / 人工客服 |

---

## 五、数据工程（AI 应用相关）

| 技能项 | 等级 | 说明 |
|--------|------|------|
| 文档解析 | L3 | PDF/Word/HTML → 纯文本/Markdown |
| OCR | L3 | 扫描件、票据识别（Tesseract、PaddleOCR、云 API） |
| 数据清洗 | L3 | 去重、去噪、PII 脱敏 |
| 知识库建设 | L3 | Confluence/语雀/Git → 同步 pipeline |
| 标注与评估集 | L4 | 构建 100～500 条 golden QA 集 |

---

## 六、前端与全栈（AI 产品必备）

| 技能项 | 等级 | 说明 |
|--------|------|------|
| Chat UI | L3 | 流式打字机效果、Markdown 渲染、代码高亮 |
| 文件上传 | L3 | 用户上传 PDF 做 RAG |
| SSE / WebSocket | L3 | 流式对话 |
| Vue/React 基础 | L2 | 能改 AI 对话前端或配合前端 |

---

## 七、DevOps for AI（L3～L4）

| 技能项 | 等级 | 说明 |
|--------|------|------|
| Docker 部署推理服务 | L3 | Ollama / vLLM 容器化 |
| K8s + GPU 调度 | L4 | GPU 节点、HPA |
| CI 中的 AI | L3 | Cursor SDK / Copilot 做 PR Review Bot |
| 密钥管理 | L3 | API Key 放 Vault/KMS，禁止进 Git |
| 模型版本管理 | L4 | MLflow、模型 registry |

---

## 八、Cursor 生态专项（强烈推荐）

| 技能项 | 等级 | 说明 |
|--------|------|------|
| Agent 模式 vs Chat vs Inline | L2 | 场景选型 |
| Plan Mode | L2 | 大改前先出方案 |
| Background Agent | L2 | 长任务后台跑 |
| MCP Server 配置 | L3 | 接数据库、Jira、Slack、自定义 API |
| Cursor SDK | L4 | 脚本/CI 中 programmatic 调用 Agent |
| Cloud Agent vs Local Agent | L3 | 本地 cwd vs 云端克隆仓库 |
| Bugbot / 自动化 Review | L2 | PR 自动审查 |

**Cursor SDK 三种调用模式（概念）**
1. `Agent.prompt()` — 一次性脚本、CI 步骤  
2. `Agent.create()` + `agent.send()` — 多轮、流式、可取消  
3. Cloud runtime — 在 Cursor VM 上跑，适合 GitHub Action  

---

## 九、软技能（AI 时代放大器）

| 技能项 | 说明 |
|--------|------|
| 问题定义能力 | AI 放大执行力，不放大方向感；先想清楚再生成 |
| 验证习惯 | 「Trust but verify」— 永远跑测试、查文档 |
| 学习速度 | 技术栈 6 个月一变，会用 AI 快速读论文/文档 |
| 产品思维 | 用户要的是结果，不是 Chatbot；减少交互步骤 |
| 沟通 | 向非技术经理解释：幻觉、成本、延迟、数据安全 |

---

## 十、自我评估（1～5 分）

| 分数 | 含义 |
|------|------|
| 1 | 只用过 ChatGPT 聊天 |
| 2 | 日常 Copilot 补全 |
| 3 | 有体系化 Prompt + Review 流程，做过简单 API 调用 |
| 4 | 独立交付 RAG/Agent 功能上线 |
| 5 | 设计 AI 平台、成本/效果优化、团队规范制定 |

**2026 年 Java 7 年工程师建议目标**
- L2 全部 ≥ 4 分  
- L3 核心项（Spring AI / RAG / Agent / MCP）≥ 3 分，至少一项 ≥ 4 分  
- L4 了解架构与成本，能在方案评审中发言  

---

# Part B：AI 相关概念详解百科

## B1. 人工智能（AI）层次结构

```
人工智能 (AI)
├── 机器学习 (ML)
│   ├── 监督学习（分类、回归）
│   ├── 无监督学习（聚类、降维）
│   └── 强化学习 (RL)
└── 深度学习 (DL)
    └── 大语言模型 (LLM) ← 当前应用热点
        ├── 多模态模型 (MLLM)
        └── Agent 系统
```

**作为应用开发者你需要知道的**：日常说的「AI 编程/AI 应用」≈ **调用 LLM API + RAG + Agent**，不必先学反向传播，但要理解能力边界。

---

## B2. 大语言模型（LLM）核心概念

### Token
- 模型处理文本的**最小单位**（不是严格的一个字，中文常 1～2 字符 ≈ 1 token）
- **计费、上下文长度、速度**都与 token 数相关
- 英文约 4 字符 ≈ 1 token；代码 token 密度更高

### Context Window（上下文窗口）
- 模型一次能「看见」的最大 token 数（输入 + 输出总和）
- 例：8K、32K、128K、1M
- 超出需：截断、摘要、RAG 外挂知识

### Temperature（温度）
- 控制随机性：0 → 确定性高（适合代码/JSON）；0.7～1 → 创意写作
- Coding 建议 **0～0.3**

### Top-p / Top-k
- 核采样，限制候选 token 集合
- 与 temperature 配合调节多样性

### Hallucination（幻觉）
- 模型**自信地生成错误事实**
- 原因：训练目标是「像人说话」而非「说真话」
- 缓解：RAG  grounding、Structured Output、人工审核、低 temperature

### Grounding（接地/溯源）
- 让回答基于**检索到的真实文档**，而非纯记忆
- RAG 的核心价值之一

### System Prompt vs User Prompt
| 类型 | 作用 |
|------|------|
| System | 定义角色、规则、边界，优先级高 |
| User | 用户当前问题 |
| Assistant | 模型历史回复 |

### Streaming（流式输出）
- 逐 token 返回，降低首字延迟（TTFT）
- 前端 SSE 展示「打字机效果」

### Function Calling / Tool Use
- 模型输出**结构化 JSON**，指明要调用的函数及参数
- 你的程序执行函数，把结果塞回对话，模型继续推理
- Agent 的基石

---

## B3. Transformer 与 Attention（理解级）

### Self-Attention
- 每个词「关注」句子中其他词，计算关联权重
- 并行计算，适合 GPU 大规模训练
- 「Attention Is All You Need」(2017) 提出

### Encoder vs Decoder
| 架构 | 代表 | 特点 |
|------|------|------|
| Encoder-only | BERT | 理解任务：分类、Embedding |
| Decoder-only | GPT、Llama、Qwen | 生成任务：对话、代码 |
| Encoder-Decoder | T5、BART | 翻译、摘要 |

**当前主流 LLM 多为 Decoder-only**。

### 参数量与能力
- 7B、14B、32B、70B… 参数量越大，通常推理能力与成本越高
- **小模型 + RAG** 在很多企业场景足够

---

## B4. 模型生命周期概念

### 预训练（Pre-training）
- 海量文本无监督学习，获得「语言统计规律」
- 成本高，仅大厂/研究机构做

### 微调（Fine-tuning）
- 在预训练模型上用**特定领域数据**继续训练
- **SFT**：监督微调，用 instruction-response 对
- **RLHF**：人类反馈强化学习，让输出更符合人类偏好（ChatGPT 关键步骤）
- **DPO**：RLHF 的简化替代

### LoRA / QLoRA
- **低秩适配**：只训练少量附加参数，冻结主模型
- 单卡可微调 7B 模型，适合企业私有领域

### 量化（Quantization）
- FP16 → INT8 → INT4，降低显存与加速推理
- 略损精度，多数业务可接受

### 蒸馏（Distillation）
- 大模型教小模型，小模型模仿大模型输出
- 降成本、降延迟

---

## B5. RAG 深度解析

### 为什么需要 RAG
| 问题 | LLM 原生局限 | RAG 解决 |
|------|--------------|----------|
| 私有数据 | 训练数据不包含 | 检索企业文档 |
| 知识过时 | 训练 cutoff 日期 | 更新知识库即可 |
| 幻觉 | 胡编法条/接口 | 基于 chunk 回答 |
| 溯源 | 无法引用 | 标注文档出处 |

### RAG 流程详解

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│ 原始文档     │ → │ 切分 Chunk    │ → │ Embedding   │
│ PDF/MD/HTML │    │ 512～1024 字 │    │ 向量 1536维 │
└─────────────┘    └──────────────┘    └──────┬──────┘
                                              ↓
用户问题 ──→ Embedding ──→ 向量检索 Top-K ──→ 拼进 Prompt ──→ LLM ──→ 答案
                              ↑
                         向量数据库
                    (Milvus/Qdrant/Pgvector)
```

### Embedding（嵌入）
- 把文本映射到**高维向量空间**，语义相近的文本向量距离近
- 同一 Embedding 模型用于索引与查询

### Chunk 策略
| 策略 | 优点 | 缺点 |
|------|------|------|
| 固定长度 | 简单 | 切断语义 |
| 按段落/标题 | 语义完整 | 长度不均 |
| Recursive | 递归切大块 | 常用默认 |
| 语义切分 | 质量高 | 计算贵 |

### 检索方式
- **Dense Retrieval**：纯向量相似度
- **Sparse Retrieval**：BM25 关键词
- **Hybrid**：两者融合（RRF），**生产推荐**

### Rerank（重排序）
- 向量检索 Top-50 → Reranker 精排到 Top-5
- 显著提升答案质量，增加少量延迟

### RAG 常见问题
| 现象 | 原因 | 对策 |
|------|------|------|
| 检索不到 | chunk 太大/太小、Embedding 模型不匹配 | 调 chunk、换模型 |
| 答非所问 | Top-K 噪声多 | Rerank、提高阈值 |
| 仍胡编 | Prompt 未强制「仅依据上下文」 | 加强 system prompt |
| 慢 | 串行检索+生成 | 缓存、并行、小模型 |

---

## B6. Agent 深度解析

### 什么是 Agent
> **LLM + 规划能力 + 工具调用 + 记忆** = 能自主完成多步任务的系统

与「单次问答」对比：
- Chat：一问一答  
- Agent：分解任务 → 调 API → 看结果 → 再决策 → 循环直到完成  

### ReAct 框架
```
Thought: 用户要查订单 12345 的物流，我需要调用 getOrder 工具
Action: getOrder(orderId="12345")
Observation: {"status":"SHIPPED", "trackingNo":"SF123"}
Thought: 已有物流单号，调用 getTracking
Action: getTracking(trackingNo="SF123")
Observation: {"location":"北京转运中心"}
Answer: 您的订单已发货，目前在...
```

### Agent 类型
| 类型 | 说明 | 示例 |
|------|------|------|
| Tool Agent | 调用预定义函数 | 查库、下单 |
| RAG Agent | 先检索再回答 | 企业知识助手 |
| Code Agent | 读代码、改代码、跑测试 | Cursor Agent |
| Multi-Agent | 多角色分工 | 规划者+执行者+审查者 |

### MCP（Model Context Protocol）

**是什么**：Anthropic 推动的开放协议，标准化 AI 应用如何连接**外部工具和数据源**。

**解决什么问题**
- 以前：每个 IDE/Agent 各自对接 GitHub、Slack、DB，重复造轮子  
- MCP：统一「Server 暴露能力 → Client（Cursor/Claude）调用」

**架构**
```
┌──────────────┐     MCP 协议      ┌──────────────┐
│ Cursor/Claude│ ←──────────────→ │ MCP Server   │
│ (MCP Client) │                   │ - 数据库     │
└──────────────┘                   │ - 文件系统   │
                                   │ - Jira API   │
                                   └──────────────┘
```

**与 Function Calling 关系**
- Function Calling：模型层「决定调什么函数」
- MCP：工具层的「标准连接方式」，可暴露多个 Resources + Tools

**Java 开发者实践**：可为内部 REST API 写 MCP Server，让 Cursor Agent 直接查订单/改配置。

---

## B7. Prompt 工程概念集

| 术语 | 解释 |
|------|------|
| Zero-shot | 不给示例，直接任务描述 |
| Few-shot | 给 1～5 个输入输出示例 |
| Chain-of-Thought (CoT) | 要求逐步推理，提升复杂题准确率 |
| Tree of Thoughts | 多路径探索，选最优（高级 Agent） |
| Self-Consistency | 多次采样取多数答案 |
| Prompt Injection | 用户输入恶意指令覆盖 system prompt |
| Jailbreak | 绕过安全限制 |
| Guardrails | 输入输出过滤、话题限制 |

---

## B8. 向量数据库概念

| 概念 | 说明 |
|------|------|
| 向量维度 | 通常 384～1536，与 Embedding 模型一致 |
| 相似度度量 | Cosine、L2、Inner Product |
| HNSW | 近似最近邻索引算法，快但略损精度 |
| Metadata Filter | 按部门/日期过滤后再向量检索 |
| Collection/Index | 逻辑隔离不同知识库 |

**选型简表**
| 产品 | 特点 |
|------|------|
| Milvus | 专业向量库，大规模 |
| Qdrant | Rust，易部署，过滤强 |
| Pgvector | PostgreSQL 扩展，运维简单 |
| Elasticsearch | 已有 ES 时可 hybrid search |

---

## B9. 多模态（Multimodal）

- **视觉**：GPT-4V、Qwen-VL — 图片理解、UI 截图转代码  
- **语音**：Whisper 转写、TTS 播报  
- **文档**：PDF 版面分析 + OCR + LLM 摘要  

**开发者场景**：上传架构图让 AI 解释、上传报错截图排错、发票 OCR 入账。

---

## B10. 评估与指标

| 指标 | 用途 |
|------|------|
| 准确率 / F1 | 分类任务 |
| BLEU / ROUGE | 文本生成（参考译文） |
| RAGAS | RAG 专用：faithfulness、answer relevance |
| 人工评估 | 金标准，抽样打分 |
| LLM-as-Judge | 用强模型评弱模型输出 |
| 业务指标 | 客服解决率、用户满意度、人均 token 成本 |

---

## B11. 安全、合规与伦理

| 概念 | 说明 |
|------|------|
| PII | 个人身份信息，禁止进 prompt 或需脱敏 |
| 数据驻留 | 数据是否出境、是否经第三方 API |
| 私有化部署 | 本地 Ollama/vLLM，数据不出内网 |
| 内容安全 | 涉政涉黄过滤、输出审核 |
| 偏见 | 模型训练数据偏见，招聘/信贷场景慎用 |
| 深度伪造 | 图像/语音伪造风险 |
| EU AI Act | 欧盟 AI 法案（了解） |

---

## B12. 常见缩写速查

| 缩写 | 全称 | 一句话 |
|------|------|--------|
| AI | Artificial Intelligence | 人工智能 |
| ML | Machine Learning | 机器学习 |
| DL | Deep Learning | 深度学习 |
| LLM | Large Language Model | 大语言模型 |
| GPT | Generative Pre-trained Transformer | 生成式预训练 Transformer |
| RAG | Retrieval-Augmented Generation | 检索增强生成 |
| RLHF | Reinforcement Learning from Human Feedback | 人类反馈强化学习 |
| SFT | Supervised Fine-Tuning | 监督微调 |
| LoRA | Low-Rank Adaptation | 低秩微调 |
| MCP | Model Context Protocol | 模型上下文协议 |
| SSE | Server-Sent Events | 服务端推送流 |
| TTFT | Time To First Token | 首 token 延迟 |
| TPS | Tokens Per Second | 每秒生成 token 数 |
| CoT | Chain of Thought | 思维链 |
| JSON Schema | - | 结构化输出约束 |
| HNSW | Hierarchical Navigable Small World | 向量索引算法 |
| OCR | Optical Character Recognition | 光学字符识别 |
| ASR | Automatic Speech Recognition | 自动语音识别 |
| TTS | Text To Speech | 文本转语音 |
| MLLM | Multimodal LLM | 多模态大模型 |
| AGI | Artificial General Intelligence | 通用人工智能（尚未实现） |

---

# Part C：推荐工具栈（2026）

## C1. AI 编程 IDE
| 工具 | 适用 |
|------|------|
| Cursor | 最强 Agent 编程体验，Rules/Skills/MCP |
| GitHub Copilot | VS Code/JetBrains 生态 |
| 通义灵码 | 国内 JetBrains/VS Code |
| Windsurf | Cursor 竞品 |
| Claude Code | 终端 Agent |

## C2. Java AI 框架
| 框架 | 说明 |
|------|------|
| Spring AI | Spring 官方，ChatClient、VectorStore、Advisor |
| LangChain4j | Java 版 LangChain，社区活跃 |
| Semantic Kernel | 微软，Java 支持 |

## C3. 模型 API / 本地
| 类型 | 选项 |
|------|------|
| 国际 | OpenAI、Anthropic Claude、Google Gemini |
| 国内 | 通义、DeepSeek、智谱、文心、Kimi |
| 本地 | Ollama + Qwen2.5/Llama3、vLLM 生产部署 |

## C4. 向量库
Milvus、Qdrant、Pgvector、Weaviate、Elasticsearch

## C5. 文档处理
Apache Tika、Unstructured、MinerU（PDF）、PaddleOCR

## C6. 可观测
Langfuse、LangSmith、Phoenix（Arize）、自建 Prometheus 指标

---

# Part D：AI 技能学习路线（12 个月）

## 阶段 0：AI 编程工作流（第 1～4 周）

| 周 | 任务 | 产出 |
|----|------|------|
| W1 | 安装 Cursor，完成官方教程；每日用 AI 写 1 个小功能并 Review | 个人 Prompt 模板 5 条 |
| W2 | 为 Java 项目写 `.cursor/rules` | rules 文件 1 套 |
| W3 | 学习 @ 引用、Agent 模式、Plan 模式 | 用 Agent 完成 1 个完整模块 |
| W4 | 配置 1 个 MCP Server（如 filesystem / postgres） | MCP 配置文档 |

**验收**：一周内 50% 以上代码由 AI 辅助生成，但 **零未经 Review 的合并**。

---

## 阶段 1：LLM 基础 + API（第 5～8 周）

| 周 | 任务 | 产出 |
|----|------|------|
| W5 | 读 OpenAI/DeepSeek API 文档；理解 token、temperature、streaming | 笔记 1 篇 |
| W6 | 用 Spring AI 或纯 HttpClient 实现 Chat API | `ai-chat-demo` 项目 |
| W7 | 实现 SSE 流式对话接口 + 简单 Vue/HTML 前端 | 可浏览器对话 |
| W8 | 加会话历史（Redis）；统计 token 用量 | 多轮对话 Demo |

**推荐资源**
- Spring AI 官方 Reference
- DeepSeek API 文档（性价比高，适合练手）
- 吴恩达《ChatGPT Prompt Engineering for Developers》（短课）

---

## 阶段 2：RAG 实战（第 9～16 周）

| 周 | 任务 | 产出 |
|----|------|------|
| W9 | 理解 Embedding；本地跑 Ollama embedding 或调 API | Embedding Demo |
| W10 | 文档加载 + Tika 解析 PDF/Markdown | 文档 pipeline |
| W11 | 接入 Pgvector 或 Qdrant；入库 + 检索 | 向量库 Demo |
| W12 | 完整 RAG 问答；Prompt 加强 grounding | 企业知识问答 MVP |
| W13 | Hybrid Search（ES BM25 + 向量） | 检索质量对比报告 |
| W14 | 加 Reranker | A/B 对比笔记 |
| W15 | 引用溯源 UI（显示来源 chunk） | 前端带来源的回答 |
| W16 | 构建 50 条评估集，算命中率 | 评估报告 |

**综合项目**：**企业内部 Java 技术文档助手**
- 数据源：团队 Confluence/Markdown 仓库
- 后端：Spring Boot + Spring AI + Pgvector
- 能力：流式问答 + 来源引用 + 会话历史

---

## 阶段 3：Agent + Tool（第 17～22 周）

| 周 | 任务 | 产出 |
|----|------|------|
| W17 | Function Calling 原理；Spring AI Function 或 LangChain4j Tool | 天气/计算器 Tool Demo |
| W18 | 封装内部 REST API 为 Tool（查订单） | 业务 Tool |
| W19 | ReAct 循环；错误重试 | Agent 日志可观测 |
| W20 | Human-in-the-loop（敏感操作确认） | 审批流 Demo |
| W21 | MCP Server 包装内部 API | Java MCP Server |
| W22 | Cursor SDK：CI 中自动 Review PR | GitHub Action 脚本 |

**综合项目**：**运维助手 Agent**
- 工具：查 K8s Pod 状态、查慢 SQL、发钉钉告警
- 限制：只读操作自动执行，写操作需确认

---

## 阶段 4：架构与生产化（第 23～28 周）

| 周 | 任务 | 产出 |
|----|------|------|
| W23 | AI 网关：多模型路由、限流、鉴权 | 网关设计文档 |
| W24 | Langfuse 接入；Trace 每次调用 | 可观测大盘 |
| W25 | 成本分析：按用户/部门 token 报表 | 成本 Dashboard |
| W26 | 安全：Prompt 注入测试、PII 脱敏 | 安全 checklist |
| W27 | 降级：模型超时 → 缓存答案 / 人工 | 降级方案 ADR |
| W28 | 压力测试：100 并发对话 | 性能报告 |

---

## 阶段 5：进阶选修（第 29～52 周，选 1～2 方向）

| 方向 | 内容 |
|------|------|
| 微调 | LoRA 微调 Qwen2.5-7B 做领域术语 |
| 推理部署 | vLLM + K8s GPU 部署 |
| Multi-Agent | LangGraph4j 多角色协作 |
| 多模态 | 图片问答、PDF 版面分析 |
| AI + 大数据 | Flink + LLM 实时摘要 |
| Cursor 自动化 | Skills + Hooks + SDK 全链路 |

---

# Part E：Java 工程师的 AI 时代定位

## 不会被 AI 替代的能力
- 业务建模与领域理解  
- 分布式系统经验与线上排障  
- 架构取舍与安全合规  
- 对 AI 输出的**责任承担**（上线的是你，不是模型）  

## AI 会放大你的能力
- 编码速度 2～5 倍（Review 后）  
- 快速原型验证想法  
- 文档、测试、CR 自动化  
- 把 LLM 嵌入现有 Java 系统创造新产品  

## 一句话总结
> **7 年 Java 工程师 + AI 时代 = 原深厚工程功底 × AI 加速执行 × RAG/Agent 产品化能力**  
> 只做 L1 会被会用 L3 的同行超越；做到 L3 可将 AI 变成职业护城河。

---

# 附录 A：Spring AI RAG 概念映射

| Spring AI 概念 | 通用概念 |
|----------------|----------|
| Document | 原始文档/Chunk |
| DocumentReader | 加载器 |
| TextSplitter | Chunk 切分 |
| EmbeddingModel | Embedding 模型 |
| VectorStore | 向量数据库 |
| RetrievalAugmentationAdvisor | RAG  Advisor |
| ChatClient | LLM 对话客户端 |
| FunctionCallback | Tool / Function Calling |

---

# 附录 B：每日学习记录模板

```markdown
## 日期

### 今日 AI 概念（1 个）
- 名称：
- 一句话：
- 与 Java 项目的关系：

### 动手实验
- [ ] 

### Prompt 技巧沉淀
- 有效的一句指令：

### 疑问
- 
```

---

# 附录 C：与 Java 学习路线衔接

建议 **并行** 而非 **替代** 原 [7年Java工程师学习路线.md](../../01-Java/7年Java工程师学习路线.md)：

| 原路线 Phase | 叠加 AI 技能 |
|--------------|--------------|
| Phase 1 Java 核心 | 用 Cursor 读源码 + 让 AI 出题检验 |
| Phase 4 Spring | Spring AI 并入，理解 Advisor 与 AOP 相似性 |
| Phase 5 数据库 | Pgvector、ES hybrid search |
| Phase 6 分布式 | MQ 异步 Embedding、AI 网关 |
| Phase 7 架构 | AI 系统方案设计、成本评估 |
| Phase 8 DevOps | Cursor SDK CI、vLLM 容器部署 |

**时间分配建议**：在职每周 **70% 传统工程深度 + 30% AI 应用技能**，持续 12 个月。

---

## 附录 D：关联执行文档

| 动作 | 文档 |
|------|------|
| AI 技能自评 | [个人基线评估.md](../00-通用/个人基线评估.md) 第十节 |
| AI 阶段勾选 | [学习进度追踪.md](../00-通用/学习进度追踪.md) AI 进度 |
| AI 项目 | [项目实战清单.md](../00-通用/项目实战清单.md) P13～P15 |
| AI 写代码 / Review | [AI时代程序员与代码.md](./AI时代程序员与代码.md) |
| Prompt/概念踩坑 | [错题与易忘概念.md](../00-通用/错题与易忘概念.md) AI 章节 |
| 每周复盘 | [周复盘模板.md](../00-通用/周复盘模板.md) |

---

*文档版本：2026-06 | 可根据模型/API 变化每季度小幅更新*
