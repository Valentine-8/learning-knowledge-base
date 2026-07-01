# Java 开发者 · Python 零基础学习指南

> **你的情况**：会 Java（OOP、集合、Spring、并发都懂），**Python 一行没写过**。
> **目标**：6 周业余时间，能写脚本、能读 AI 示例，面试能讲清 Python 与 Java 差异。
> **不是**：从零学编程；**是**：把 Java 经验映射到 Python 语法和生态。

---

## 1. 你已经有什么、缺什么

| 已有（Java） | Python 里要新学的 |
|--------------|-------------------|
| 变量、if/for、方法 | **缩进**、动态类型、无 `{}` |
| ArrayList / HashMap | `list` / `dict`（用法更像，语法更短） |
| class、interface、继承 | `class` 更简单，**鸭子类型**无 interface 强制 |
| Maven、jar | **venv + pip + requirements.txt** |
| try-catch、IOException | **无 checked exception**，全 try/except |
| JUnit | **pytest** |
| Spring 调 HTTP | **requests** 写脚本即可 |
| 线程池、JUC | **GIL**、threading、asyncio（概念不同） |

**不用重学**：什么是循环、什么是 API、什么是 JSON、什么是 REST——这些 Java 里都有了。

---

## 2. 学习策略（Java 开发者专用）

| 做法 | 原因 |
|------|------|
| 每章先看 **「Java 对照」** 框 | 快速建立映射，少懵 |
| 对照文档随时翻 [附录-Java与Python对照](./附录-Java与Python对照.md) | 语法差异集中查 |
| **手敲** Java 里写过的小逻辑（如读文件统计词频） | 用 Python 重写一遍比只看语法有效 |
| 01～07 扎实，08～10 可加速 | OOP 你已懂，重点看 Python 特有写法 |
| 13 章（requests/AI）是你的**主业延伸** | 配合 [AI工程](../../AI工程/README.md) |

**别做**：按 C 语言零基础教程从「什么是变量」怀疑人生——你 Java 都会了。

---

## 3. 章节怎么读（会 Java 的读法）

| 章 | 读法 | Java 对照重点 |
|:--:|------|---------------|
| 01 | 快读 + 装环境 | `python x.py` ≈ `java Main`；无 javac |
| 02 | 重点 | 动态类型、无 int 声明、None≈null |
| 03 | 重点 | String 不可变像 Java；f-string 像 formatted |
| 04 | 快读 | list≈ArrayList；tuple≈不可变 List |
| 05 | 快读 | dict≈HashMap；set≈HashSet |
| 06 | 快读 | if/for/while 同思路，语法不同 |
| 07 | 重点 | 无 overload；默认参数陷阱；*args |
| 08 | 重点 | try-with-resources → `with`；无 checked |
| 09 | 重点 | Maven→pip；package 结构类似 |
| 10 | 快读 | 你已懂 OOP；看 `self`、`@dataclass` |
| 11 | **精读** | 推导式、生成器、装饰器——Java 没有 |
| 12 | 重点 | 标准库当 Java SE API 查 |
| 13 | **精读** | 脚本 + AI，你的目标场景 |
| 14 | 重点 | GIL vs JMM；asyncio vs NIO |
| 15 | 做项目 | 5 个小项目 + 70 题 |

---

## 4. 六周计划（Java 开发者 · 业余）

比通用路线图**快约 40%**（OOP、流程控制概念已具备）。

### 第 1 周 · 语法映射

| 天 | 内容 |
|----|------|
| D1 | 01 安装 + [附录对照](./附录-Java与Python对照.md) 通读一遍 |
| D2 | 02 变量类型 |
| D3 | 03 字符串 |
| D4 | 04 list + 05 dict（合并一天） |
| D5 | 06 流程控制（快） |
| D6 | 07 函数 |
| D7 | **练习**：用 Python 重写 Java 里「读文件数单词」 |

### 第 2 周 · 文件与工程

| 天 | 内容 |
|----|------|
| D8～D9 | 08 文件与异常 |
| D10～D11 | 09 venv / pip / 模块 |
| D12～D14 | 10 OOP（快读）+ 11 推导式/装饰器入门 |

### 第 3 周 · 标准库 + HTTP

| 天 | 内容 |
|----|------|
| D15～D17 | 12 标准库 |
| D18～D21 | 13 requests + pandas + OpenAI SDK |

### 第 4 周 · 并发与项目 A/B

| 天 | 内容 |
|----|------|
| D22～D24 | 14 GIL / asyncio / pytest |
| D25～D28 | 15 项目 A 待办 CLI + 项目 B 日志分析 |

### 第 5～6 周 · 项目 + 面试

| 内容 |
|------|
| 15 章项目 C/D/E 选做 |
| 70 面试题自测（重点 21～45 Java 差异题） |
| 读 [AI工程](../../AI工程/README.md) 时对照 Python 示例 |

---

## 5. 第一天就能跑的「Java 眼」对比

**Java**：

```java
public class Main {
    public static void main(String[] args) {
        var names = java.util.List.of("Alice", "Bob");
        for (var n : names) {
            System.out.println(n);
        }
    }
}
```

**Python**：

```python
names = ["Alice", "Bob"]
for n in names:
    print(n)
```

**Java**：

```java
Map<String, Integer> scores = new HashMap<>();
scores.put("Alice", 95);
scores.getOrDefault("Bob", 0);
```

**Python**：

```python
scores = {"Alice": 95}
scores.get("Bob", 0)
```

---

## 6. 和 Java 知识库的衔接

| Java 文档 | Python 用来干什么 |
|-----------|-------------------|
| [AI工程/](../../AI工程/README.md) | Java 写生产；Python 试 prompt、批评测 |
| [数据与中间件/MySQL/](../../数据与中间件/MySQL/README.md) | SQL 一样；Python 做导数分析脚本 |
| [Java/笔记/phase3-并发/](../../Java/笔记/phase3-并发/复习手册.md) | 对照学 GIL、asyncio |
| [扩展技能全景](../../扩展技能全景.md) | Python P1 优先级 |

---

## 7. 合格线（Java 开发者版）

- [ ] 能解释 Python 与 Java 的 5 个核心差异（动态类型、缩进、GIL、无 checked、鸭子类型）
- [ ] 独立 venv + pip + 写 100 行脚本
- [ ] 用 requests 调 API，用 pandas 读 CSV
- [ ] 读懂带 `@decorator`、`yield`、`async def` 的代码
- [ ] 15 章至少完成 2 个综合项目

---

**下一步** → [01-安装环境与第一个程序](./01-安装环境与第一个程序.md)（约 1 小时，主要是装环境）

← [Python 目录](./README.md) · 详细周计划 → [00-学习路线图](./00-学习路线图.md)
