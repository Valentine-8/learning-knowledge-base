# Repository Structure

> 本文档定义知识库的目录蓝图。**以中文 `技术成长/` 结构为正式标准**。文中标注 `Planned` 的条目为未来规划，未创建前不得被正式文档引用为已存在。

## 1. 顶层结构（当前正式）

```text
学习/
├── README.md
├── 规范文档/
│   ├── Repository-Specification.md
│   ├── Repository-Structure.md
│   └── 迁移说明-2026-07.md
├── 技术成长/              ★ 知识库主体
├── 前端/                  Vue2 等历史 Demo
├── 奥林巴斯ep7/           摄影专题
└── assets/                公共图片（Planned）
```

**日常入口**：[技术成长/README.md](../技术成长/README.md) · [技术成长/00-通用/阅读指南.md](../技术成长/00-通用/阅读指南.md)

**已废止**：仓库根下的 `01-Java/`、`03-Database/`、`05-Message-Queue/` 等英文编号顶层目录（2026-07-01 试验后回退）。

---

## 2. 技术成长 — 一级板块

```text
技术成长/
├── README.md
├── 00-通用/
├── Java/
├── 数据与中间件/
├── 运维与部署/
├── 计算机基础/
├── AI工程/
├── C++嵌入式/
└── 扩展语言/
```

| 板块 | 状态 | 说明 |
|------|------|------|
| `00-通用/` | Stable | 导航、进度、复盘、求职、Cursor |
| `Java/` | Stable + 演进中 | 笔记、面试、路线；phase 目录逐步迁入领域子目录 |
| `数据与中间件/` | Stable | MySQL / Redis / 消息队列 / ES 多章深度文档 |
| `运维与部署/` | Stable | Nginx / Docker / Kubernetes 多章深度文档 |
| `计算机基础/` | Stable | 算法 / 计网 / OS / 安全 |
| `AI工程/` | Stable | 12 篇实战 + 概念手册 |
| `C++嵌入式/` | Stable | 嵌入式专项 |
| `扩展语言/` | Stable | Python 多章；Go 规划 |

---

## 3. 00-通用

```text
00-通用/
├── README.md
├── 阅读指南.md              # 迷路先看
├── 统一主路线.md
├── 学习进度追踪.md
├── 个人基线评估.md
├── 错题与易忘概念.md
├── 算法刷题记录.md
├── Cursor操作手册.md
├── 资源书签.md
├── 求职追踪.md
├── 面试与晋升素材库.md
├── 工程素养-复习手册.md
├── 项目实战清单.md
├── 周复盘模板.md
├── archive/                 # 旧版路线
└── reviews/                 # 周复盘记录
```

路线类文档也可放在 `Java/`（如 `7年Java工程师学习路线.md`）。`扩展技能全景.md` 在 `技术成长/` 根下。

---

## 4. 数据与中间件（已落地）

```text
数据与中间件/
├── README.md
├── MySQL/
│   ├── README.md
│   ├── 00-速查总览.md
│   ├── 01-InnoDB架构与日志体系.md
│   ├── 02-索引原理与B+树.md
│   ├── 03-事务隔离与MVCC.md
│   ├── 04-锁机制与死锁.md
│   ├── 05-SQL优化与EXPLAIN.md
│   ├── 06-主从复制与高可用.md
│   ├── 07-分库分表与分布式ID.md
│   └── 08-生产案例与面试题库.md
├── Redis/
│   ├── README.md
│   ├── 00-速查总览.md
│   ├── 01-数据结构与底层实现.md
│   ├── …（02～06）
│   └── 06-面试题库与案例.md
├── 消息队列/
│   ├── README.md
│   ├── 00-速查总览.md
│   ├── 01-Kafka核心原理.md
│   ├── 02-RocketMQ核心原理.md
│   ├── 03-可靠性与幂等.md
│   ├── 04-Kafka与RocketMQ对比选型.md
│   └── 05-面试题库与案例.md
└── Elasticsearch/
    ├── README.md
    ├── 00-速查总览.md
    ├── 01-核心概念与倒排索引.md
    ├── 02-写入查询与聚合.md
    ├── 03-集群运维与同步方案.md
    └── 04-面试题库与案例.md
├── PostgreSQL/         # 00 速查 + 01～07
└── gRPC/               # 00 速查 + 01～06
```

**规划扩展**（Planned）：`MongoDB/` 短文。

---

## 4.1 运维与部署（已落地）

```text
运维与部署/
├── README.md
├── Nginx/          # 00 速查 + 01～06
├── Docker/         # 00 速查 + 01～05
└── Kubernetes/     # 00 速查 + 01～05
```

Java `phase8-DevOps/复习手册.md` 保留 35 min 速览，并链到本板块。

---

## 4.2 Java Spring 核心（已落地）

```text
Java/Spring/
├── README.md
├── 00-速查总览.md
├── 01-IoC与Bean生命周期.md
├── 02-循环依赖与作用域.md
├── 03-AOP与动态代理.md
├── 04-SpringBoot自动配置.md
├── 05-SpringMVC与Web层.md
├── 06-事务传播与失效.md
├── 07-SpringSecurity与JWT.md
├── 08-MyBatis映射与缓存.md
└── 09-生产案例与面试题库.md
```

`Java/笔记/phase4-Spring/复习手册.md` 保留 35 min 速览，并链到本目录。

---

## 4.3 Java Spring Cloud（已落地）

```text
Java/SpringCloud/
├── README.md
├── 00-速查总览.md
├── 01-微服务组件全景.md
├── 02-Nacos注册发现.md
├── 03-Nacos配置中心.md
├── 04-SpringCloudGateway.md
├── 05-OpenFeign与负载均衡.md
├── 06-Sentinel与Seata.md
└── 07-生产案例与面试题库.md
```

Phase4 复习手册保留 Spring Core；微服务基础设施见本目录。

---

## 5. 计算机基础（已落地）

```text
计算机基础/
├── README.md
├── 算法与数据结构/     # 00 速查 + 01～05
├── 计算机网络/         # 00 速查 + 01～04
├── 操作系统/           # 00 速查 + 01～04
└── 安全/               # 00 速查 + 01～04
```

---

## 6. Java

### 6.1 当前结构

```text
Java/
├── README.md
├── java学习.md
├── 7年工程师技能全景索引.md
├── 7年Java工程师技能清单.md
├── 7年Java工程师学习路线.md
├── 面试题大全Q&A.md
├── 面试前速查.md
├── 项目经历面试手册.md
├── 系统设计练手.md
├── 简历.md
└── 笔记/
    ├── phase1-集合/          # HashMap、ArrayList、ConcurrentHashMap
    ├── phase2-JVM/           # 复习手册（过渡）
    ├── phase3-并发/
    ├── phase4-Spring/          # 35 min 速览 → 链到 Spring/
    ├── Spring/                 # IoC AOP Boot MVC 事务 Security MyBatis（9 章）
    ├── SpringCloud/            # Nacos Gateway Feign Sentinel
    ├── phase5-数据库/
    ├── phase6-分布式/
    ├── phase7-架构/
    ├── phase8-DevOps/
    └── Java语言与IO/         # 01～05 分章
```

### 6.2 目标结构（渐进迁移，Planned）

新建正式文档优先放入领域子目录，**不再新建 phase 目录**：

```text
Java/
├── 02-面向对象/
├── 03-集合框架/              # 从 phase1 迁入
├── 06-注解与反射/
├── 07-IO与NIO/
├── 08-Lambda与Stream/
├── 08-JVM/                   # 从 phase2 拆分
├── 09-并发/
├── 10-Spring生态/            # 从 phase4 拆分
├── 11-分布式/
├── 12-架构/
└── 13-DevOps/
```

单篇专题命名：`04-HashMap.md`、`01-类加载过程.md` 等（两位数字 + 中文主题）。

---

## 7. AI工程（已落地）

```text
AI工程/
├── README.md
├── 01-Prompt工程实战.md
├── 02-LLM-API集成实战(Java).md
├── 03-Spring-AI与LangChain4j实战.md
├── 04-Embedding与向量数据库实战.md
├── 05-RAG系统工程化实战.md
├── 06-Function-Calling与Agent开发.md
├── 07-MCP协议开发实战.md
├── 08-AI可观测与评测.md
├── 09-LLM安全与合规.md
├── 10-本地模型部署与推理优化.md
├── 11-模型微调入门(LoRA).md
├── 12-AI应用架构与成本工程.md
├── AI时代开发者技能与概念手册.md
├── AI时代程序员与代码.md
└── 面试题大全-AI专题.md
```

---

## 8. C++嵌入式（已落地）

```text
C++嵌入式/
├── README.md
├── C++嵌入式复习路线.md
├── 从Java到C++嵌入式-迁移指南.md
├── 嵌入式八股速查.md
├── 手写代码题集.md
├── 复习进度追踪.md
├── 公司与岗位准备-广东宏大.md
├── 面试题大全-C++专题.md
├── 面试前速查-C++嵌入式.md
├── 简历-C++嵌入式.md
└── notes/
```

---

## 9. 扩展语言

### 9.1 Python（已落地 · 从零 15 章）

```text
扩展语言/Python/
├── README.md
├── 00-Java开发者学习指南.md   # 会 Java、Python 0 基础 · 入口
├── 00-学习路线图.md
├── 00-速查总览.md
├── 01-安装环境与第一个程序.md
├── …（02～14）
├── 15-综合练习与面试题库.md
├── 复习手册.md              # 索引页
└── 附录-Java与Python对照.md
```

### 9.2 Go（Planned）

```text
扩展语言/Go/
├── README.md
└── 复习手册.md              # Planned
```

规划详见 [扩展技能全景.md](../技术成长/扩展技能全景.md)。

---

## 10. 规范文档

```text
规范文档/
├── README.md
├── Repository-Specification.md
├── Repository-Structure.md
└── 迁移说明-2026-07.md
```

模板类文件（Markdown 风格、README 模板、AI 写作清单等）可按需增补，**不进入日常阅读路径**。

---

## 11. 个人专题与历史 Demo

```text
前端/vue/                    # Vue2 入门 Demo（历史）
奥林巴斯ep7/EP7-Guide/       # EP7 摄影指南 + images/
```

正式 Vue3 前端知识体系（Planned）：可建 `技术成长/前端工程/` 或独立 `前端学习/`，与 Demo 分离。

---

## 12. 文章命名约定

| 层级 | 约定 | 示例 |
|------|------|------|
| 板块目录 | 中文 | `数据与中间件`、`计算机基础` |
| 技术域目录 | 中文或技术专名 | `MySQL`、`消息队列` |
| 正式文章 | `两位数字-中文主题.md` | `03-事务隔离与MVCC.md` |
| 速查 | `00-速查总览.md` | 每域一篇 |
| 导航 | `README.md` | 每目录一篇 |

禁止：空格、`最终版`、`新版`、英文编号顶层目录。

---

## 13. 分阶段落地顺序

1. **已完成**：`技术成长/` 中文板块；数据与中间件 / 计算机基础 / AI 多章文档；规范迁入 `规范文档/`。
2. **进行中**：Java phase 复习手册按领域拆分；链接与 README 维护。
3. **待建**：扩展语言深度文档；PostgreSQL；Linux / Docker / K8s（可建 `技术成长/运维部署/` 或同级中文目录）。
4. **持续**：按 `Repository-Specification.md` 扩写缺失专题，一文一题。

---

## 14. 附录：英文编号方案（已废止，仅作对照）

2026-07 曾试验将内容迁至 `01-Java/`、`03-Database/` 等路径。因日常阅读成本高，**已全部回退至 `技术成长/`**。后续规划以本文档第 2～11 节为准，不再恢复英文顶层。

| 废止路径 | 当前正式路径 |
|----------|----------------|
| `03-Database/02-MySQL/` | `技术成长/数据与中间件/MySQL/` |
| `04-Redis/` | `技术成长/数据与中间件/Redis/` |
| `05-Message-Queue/` | `技术成长/数据与中间件/消息队列/` |
| `16-Computer-Science/` | `技术成长/计算机基础/` |
| `18-AI-Engineering/` | `技术成长/AI工程/` |
| `00-Governance/` | `规范文档/` |

---

*维护：结构变更时同步更新 `规范文档/迁移说明-2026-07.md` 与本节附录。*
