# AI 工程实战（Java 工程师的 AI 增量硬技能训练营）

> **定位**：同目录的《[AI 时代开发者技能与概念手册](./AI时代开发者技能与概念手册.md)》是**概念词典**；本训练营（01~12）是**动手落地**。
> 每一篇都遵循统一结构：**为什么学 → 核心概念 → Java 可运行代码 → 常见坑 → 面试考点 → 动手任务 → 验收标准**。
> **前置**：Java 17+、Spring Boot 3.x、Maven、Docker 基础。会 Cursor（见 [Cursor 操作手册](../00-通用/Cursor操作手册.md)）。

---

## 为什么单独开一个板块

一个 7 年 Java 工程师在 AI 时代真正的护城河，不是"会调 ChatGPT"，而是**能把 LLM 稳定、安全、低成本地嵌入企业级 Java 系统**。这需要一批传统 Java 路线里没有的增量硬技能。这些技能在《AI 手册》里只有表格概览，本目录把它们逐个拆成可动手的实战文档。

```
概念层（已有）        →   工程层（本目录）
AI手册 Part B 词典          能写出可运行的 Spring AI / LangChain4j 代码
"RAG 是什么"                能调优分块/检索/rerank，把召回率从 60% 提到 90%
"Agent 是什么"              能实现 Function Calling + MCP，让 Agent 安全地调工具
"注意 prompt 注入"          能按 OWASP LLM Top 10 做防护并写测试
```

---

## 技能地图（12 篇 · 4 个能力层）

| # | 文档 | 能力层 | 一句话 | 难度 | 预计工时 |
|---|------|--------|--------|:----:|:----:|
| 01 | [Prompt 工程实战](./01-Prompt工程实战.md) | L2 驾驭 | 结构化 prompt、模板库、约束输出、自动评估 | ★★ | 8h |
| 02 | [LLM API 集成实战(Java)](./02-LLM-API集成实战(Java).md) | L3 集成 | 裸调 API：流式 SSE、Token/成本、重试限流、多模型路由 | ★★★ | 12h |
| 03 | [Spring AI 与 LangChain4j 实战](./03-Spring-AI与LangChain4j实战.md) | L3 集成 | 两大 Java AI 框架：ChatClient、Advisor、记忆、结构化输出 | ★★★ | 14h |
| 04 | [Embedding 与向量数据库实战](./04-Embedding与向量数据库实战.md) | L3 集成 | 向量化、pgvector/Qdrant/Milvus、相似度、索引选型 | ★★★ | 12h |
| 05 | [RAG 系统工程化实战](./05-RAG系统工程化实战.md) | L3→L4 | 分块、混合检索、rerank、grounding、评估集、生产优化 | ★★★★ | 20h |
| 06 | [Function Calling 与 Agent 开发](./06-Function-Calling与Agent开发.md) | L3→L4 | 工具调用、ReAct、多步规划、人审确认、状态机 | ★★★★ | 18h |
| 07 | [MCP 协议开发实战](./07-MCP协议开发实战.md) | L3→L4 | Model Context Protocol：写 Server/Client，暴露企业工具 | ★★★ | 10h |
| 08 | [AI 可观测与评测](./08-AI可观测与评测.md) | L4 架构 | Langfuse 链路追踪、LLM-as-Judge、离线评估集、A/B | ★★★ | 10h |
| 09 | [LLM 安全与合规](./09-LLM安全与合规.md) | L4 架构 | OWASP LLM Top 10、prompt 注入防护、PII、越狱、审计 | ★★★★ | 12h |
| 10 | [本地模型部署与推理优化](./10-本地模型部署与推理优化.md) | L4→L5 | Ollama/vLLM、量化(GGUF/AWQ)、GPU 显存、并发吞吐 | ★★★ | 12h |
| 11 | [模型微调入门(LoRA)](./11-模型微调入门(LoRA).md) | L5 建设 | 何时该微调、数据集构建、LoRA/QLoRA、评估、部署 | ★★★★ | 16h |
| 12 | [AI 应用架构与成本工程](./12-AI应用架构与成本工程.md) | L4 架构 | 分层架构、缓存/降级/限流、成本核算、选型决策、上线 checklist | ★★★★ | 12h |

> 全部完成约 **150 小时**，按每周 8～10h AI 投入，约 **4～5 个月**（与 [统一主路线](../00-通用/统一主路线.md) 的 AI 阶段 1～5 对应，可并行到 Java Phase 4 之后）。

---

## 推荐学习顺序（三条路线）

### 路线 ①：应用集成最短路径（想尽快把 LLM 用到项目里）
```
01 Prompt → 02 API 集成 → 03 Spring AI → 04 向量库 → 05 RAG
```
学完能独立交付一个"企业文档问答"产品。约 6～8 周。

### 路线 ②：Agent / 智能体方向
```
01 → 02 → 03 → 06 Function Calling/Agent → 07 MCP → 08 可观测
```
学完能做"运维助手 / 数据分析 Agent"。

### 路线 ③：平台 / 深度方向（有 GPU 资源或想做 AI 平台）
```
04 → 05 → 10 本地部署 → 11 微调 → 12 架构成本
```

**通用建议**：无论走哪条，**09 安全与合规** 和 **12 架构成本** 在真正上线前必读。

---

## 与现有知识库的关系

| 本目录 | 关联现有文档 |
|--------|--------------|
| 全部 | [AI时代开发者技能与概念手册](./AI时代开发者技能与概念手册.md)（先查概念，再来这里动手） |
| 学习节奏 | [统一主路线](../00-通用/统一主路线.md) AI 阶段 0～5 |
| 每周勾选 | [学习进度追踪](../00-通用/学习进度追踪.md) |
| Demo 记录 | [项目实战清单](../00-通用/项目实战清单.md) |
| 面试 | [面试题大全-AI专题](./面试题大全-AI专题.md) |
| 用 AI 写这些 Demo 时 | [AI时代程序员与代码](./AI时代程序员与代码.md) |

---

## 环境准备（一次性）

```bash
# 1. JDK 21（虚拟线程 + 最新 Spring AI）
sdk install java 21.0.4-tem   # 或用你现有的 JDK 17+

# 2. 本地跑一个模型（免 API Key，边学边试）
# 见 10-本地模型部署，先装 Ollama：
ollama pull qwen2.5:7b        # 通义千问 7B，中文友好
ollama pull nomic-embed-text  # Embedding 模型

# 3. 向量库（Docker 一键起 pgvector）
docker run -d --name pgvector -p 5432:5432 \
  -e POSTGRES_PASSWORD=postgres pgvector/pgvector:pg16

# 4. 可观测（Langfuse，见 08）
# docker compose 见对应文档
```

> 没有 API Key 也能学：本目录所有 Demo 都提供 **Ollama 本地** 与 **云 API（通义/DeepSeek/OpenAI）** 两套配置。

---

## 验收：学完这 12 篇你应该能

- [ ] 独立交付一个带**来源引用**的企业 RAG 问答服务，召回评估集 ≥ 85%
- [ ] 写一个安全的 Agent：只读工具自动执行、写操作人工确认、防 prompt 注入
- [ ] 用 Langfuse 看到每次调用的 token/延迟/成本，并能做离线评估
- [ ] 能对一个 AI 需求做**选型决策**（自研/API/本地/微调）并给出成本估算
- [ ] 通过 [AI专题面试题](./面试题大全-AI专题.md) 中 80% 的工程题

---

← 返回 [总入口 README](../README.md) · [阅读指南](../00-通用/阅读指南.md) · [AI 概念手册](./AI时代开发者技能与概念手册.md)
