# 05 · RAG 系统工程化实战

> **能力层**：L3→L4　**难度**：★★★★　**预计工时**：20h（本目录最重的一篇）
> **一句话**：RAG（检索增强生成）= 先检索企业知识、再让 LLM 基于检索结果作答。这是 Java 工程师落地 AI 最高频、最有商业价值的场景（企业问答、客服、文档助手）。
> **前置**：[03-Spring AI](./03-Spring-AI与LangChain4j实战.md)、[04-向量数据库](./04-Embedding与向量数据库实战.md)。

---

## 一、为什么需要 RAG

LLM 有两个硬伤：① **知识截止**（不知道你公司内部文档、不知道昨天的数据）；② **幻觉**（一本正经胡编）。

三种解法对比：

| 方案 | 解决什么 | 成本 | 时效 |
|------|----------|------|------|
| 全塞进 prompt | 小知识 | token 贵、有上限 | 实时 |
| **RAG** | 大量私有/动态知识 | 中，最划算 | 改文档即生效 |
| 微调 | 风格/领域能力 | 高，要数据+算力 | 慢，要重训 |

**结论**：企业知识问答**首选 RAG**。微调解决不了"知识实时更新"。见 [12-架构决策树](./12-AI应用架构与成本工程.md)。

---

## 二、RAG 全流程架构

```
【离线：建索引】
文档(PDF/Word/MD/网页)
  → 解析提取文本(去页眉页脚)
  → 分块 Chunking(切成段)
  → Embedding 向量化
  → 存入向量库(带元数据)

【在线：问答】
用户问题
  → (可选)问题改写/扩展
  → Embedding
  → 向量检索 Top-K  ┐
  → 关键词检索(BM25)┘→ 混合融合
  → Rerank 重排序(精排)
  → 组装 Prompt(问题 + 检索片段 + grounding 指令)
  → LLM 生成答案
  → 附带来源引用返回
```

**RAG 的效果 = 检索质量 × 生成质量**，而 90% 的问题出在**检索**，不是生成。所以工程重点在"怎么检索得准"。

---

## 三、逐环节工程实战

### 3.1 文档解析
不同格式用不同工具，目标是拿到**干净的纯文本 + 结构信息**。

| 格式 | Java 工具 |
|------|-----------|
| PDF | Apache PDFBox、Tika |
| Word/Excel/PPT | Apache POI、Tika |
| HTML | Jsoup |
| Markdown | flexmark |
| 通用 | **Apache Tika**（一把梭，Spring AI 有 TikaDocumentReader）|

```java
// Spring AI 直接读
var reader = new TikaDocumentReader(new ClassPathResource("handbook.pdf"));
List<Document> docs = reader.get();
```
**坑**：PDF 的页眉页脚、目录、表格会污染文本，要清洗。扫描件 PDF 需要 OCR。

### 3.2 分块（Chunking）—— 最影响效果的一步

为什么分块：① embedding 有长度上限；② 块太大检索不精准（一块里混多个主题），块太小丢上下文。

| 策略 | 说明 | 适用 |
|------|------|------|
| 固定长度 | 按字符/token 切，如 512 token | 简单基线 |
| **重叠滑窗** | 相邻块重叠 10~20%，防切断语义 | ★常用 |
| 按结构 | 按标题/段落/章节切 | Markdown/结构化文档 |
| 语义分块 | 按语义相似度断句 | 高级，效果好但慢 |
| 父子分块 | 检索小块、返回所属大块给 LLM | 兼顾精准与上下文 |

```java
var splitter = new TokenTextSplitter(512, 100, 5, 10000, true); // 块大小512, 重叠...
List<Document> chunks = splitter.apply(docs);
```

**经验值**：中文文档 chunk **300~500 字**、重叠 **50~100 字** 是不错的起点。**没有银弹，要用评估集调**（见 §5）。

### 3.3 检索：混合检索 + 元数据过滤

纯向量检索对"精确词/编号/专有名词"弱。生产要**混合检索**：

```
向量检索(语义) ─┐
                 ├→ RRF/加权融合 → 候选集
BM25(关键词)   ─┘
```

- **向量**：语义相似（"提升性能"命中"优化响应时间"）
- **BM25/全文**：精确词（"错误码 E1234"、"张三"）
- **RRF（Reciprocal Rank Fusion）**：把两路排名融合的经典算法

元数据过滤同样关键：按部门/时间/文档类型先过滤再检索，既准又快又安全（权限隔离）。

### 3.4 Rerank（重排序，精排）

初检召回的 Top-20 里，用**专门的 rerank 模型**（如 BGE-reranker、Cohere Rerank）对"问题-片段"打分重排，取 Top-4 给 LLM。这一步对准确率提升往往很显著。

```
初检 Top20  →  Rerank 模型精排  →  Top4 送入 LLM
（快、召回全）   （慢、精准）
```
> 二阶段检索（召回+精排）是搜索/推荐的经典范式，RAG 直接复用。

### 3.5 组装 Prompt（Grounding —— 防幻觉命门）

```markdown
你是企业知识助手。**只能**根据下面【参考资料】回答问题。
如果参考资料中没有答案，明确回答"根据现有资料无法回答"，禁止编造。
在答案末尾用 [1][2] 标注引用了哪几条资料。

【参考资料】
[1] {chunk1}（来源：员工手册 p3）
[2] {chunk2}（来源：报销制度 p1）

【问题】
{question}
```

要点：① 强约束"只依据资料"；② 允许"不知道"（比编造好一万倍）；③ 强制**引用来源**（可信、可追溯）。

### 3.6 Spring AI 完整实现

```java
@Service
public class RagService {
    private final ChatClient chatClient;
    private final VectorStore vectorStore;

    public RagAnswer ask(String question) {
        // Spring AI 用 QuestionAnswerAdvisor 一步到位（检索+注入）
        String answer = chatClient.prompt()
            .advisors(new QuestionAnswerAdvisor(
                vectorStore,
                SearchRequest.query(question).withTopK(4).withSimilarityThreshold(0.5)))
            .user(question)
            .call().content();
        // 生产中通常自己控制检索以便加 rerank / 来源引用
        return new RagAnswer(answer, retrievedSources);
    }
}
```

更可控的手动流程（推荐生产用）：
```java
// 1. 检索
List<Document> hits = vectorStore.similaritySearch(
    SearchRequest.query(question).withTopK(20));
// 2. rerank（调 rerank 模型，取 top4）
List<Document> top = reranker.rerank(question, hits, 4);
// 3. 组装带来源的 prompt
String context = buildContextWithCitations(top);
// 4. 生成
String answer = chatClient.prompt()
    .system(GROUNDING_SYSTEM_PROMPT)
    .user(u -> u.text("参考资料：\n{ctx}\n\n问题：{q}").param("ctx", context).param("q", question))
    .call().content();
```

---

## 四、进阶优化技巧

| 技巧 | 解决 |
|------|------|
| **问题改写(Query Rewrite)** | 口语化/有指代的问题，先让 LLM 改写成检索友好的查询 |
| **HyDE** | 先让 LLM 生成一个"假设答案"，用它去检索（有时更准）|
| **多查询(Multi-Query)** | 一个问题生成多个变体分别检索，合并结果，提召回 |
| **父子/上下文扩展** | 检索小块，返回其前后文或所属大块给 LLM |
| **元数据路由** | 先判断问题属于哪类文档，只在对应库检索 |
| **Self-RAG/反思** | 让 LLM 判断检索够不够、要不要再检索 |

不要一上来全上，**先建评估集，用数据驱动决定加哪个**。

---

## 五、评估（RAG 工程的分水岭）

> "没有评估集的 RAG 就是玄学调参。" 这是 L3 和 L4 的分界线。

### 5.1 建评估集
准备 30~50 条 `{问题, 标准答案, 应命中的文档}`，覆盖常见问法、边界、"资料里没有"的问题。

### 5.2 检索指标（先保证检索准）
- **Recall@K**：应命中的文档在 Top-K 里的比例（最重要）
- **MRR / NDCG**：命中的排名靠不靠前
- **命中率**：有多少问题至少检索到 1 条相关

### 5.3 生成指标
- **Faithfulness（忠实度）**：答案是否忠于检索资料（不幻觉）
- **Answer Relevance**：答案是否回应了问题
- **来源正确性**：引用的来源对不对

### 5.4 怎么测
- **LLM-as-Judge**：用强模型给答案打分（见 [08-可观测与评测](./08-AI可观测与评测.md)）
- 框架：Ragas（Python 生态经典）、Spring AI Evaluator、自建脚本
- **每次改分块/检索参数，跑一遍评估集看指标涨跌**，而不是"感觉变好了"

---

## 六、常见坑

| 坑 | 现象 | 解法 |
|----|------|------|
| 分块太大/太小 | 检索不准/丢上下文 | 用评估集调 chunk size + 重叠 |
| 只用向量检索 | 精确词/编号搜不到 | 混合检索 + BM25 |
| 不做 rerank | Top-K 里噪声多 | 加 rerank 精排 |
| prompt 没 grounding | LLM 无视资料乱编 | 强约束"只依据资料"+允许"不知道"+引用 |
| 没有来源引用 | 用户不敢信 | 强制标注来源，可点开验证 |
| 没评估集 | 调参靠感觉 | 先建 30-50 条评估集 |
| 文档更新不同步 | 答案过时 | 建增量/定时重建索引管道 |
| 权限没隔离 | A 部门问出 B 部门机密 | 元数据过滤按权限，见 [09](./09-LLM安全与合规.md) |
| 上下文塞太多块 | 贵 + Lost in Middle | 精排后只给 3-5 块，重要的放两端 |

---

## 七、面试考点

- **Q：RAG 完整流程？**
  A：离线（解析→分块→embedding→入向量库）+ 在线（问题 embedding→检索→rerank→组装 grounding prompt→LLM 生成→带来源返回）。
- **Q：RAG 和微调怎么选？**
  A：知识型/需实时更新→RAG；风格/领域能力且有数据→微调；二者可结合。RAG 更便宜、可溯源、易更新。
- **Q：RAG 效果差先查哪里？**
  A：先查检索（90% 问题在这）。看 Recall@K，调分块、加混合检索、加 rerank；再看 grounding prompt 是否约束住幻觉。
- **Q：怎么防止 RAG 幻觉？**
  A：grounding prompt 强约束只依据资料、允许回答"不知道"、强制引用来源；生成侧用 faithfulness 评估。
- **Q：为什么要混合检索/rerank？**
  A：向量擅长语义弱于精确词，BM25 相反，融合互补；rerank 用精排模型对召回结果重排，显著提准。
- **Q：怎么评估 RAG？**
  A：建评估集，检索看 Recall@K/MRR/NDCG，生成看 faithfulness/relevance，用 LLM-as-Judge 或 Ragas。

---

## 八、动手任务（本篇产出——里程碑项目）

> 这是本目录的**核心作品**，建议做扎实，可写进简历和 [项目实战清单](../00-通用/项目实战清单.md)。

- [ ] **任务 1**：用 Tika 解析 5~10 篇企业文档（可用公开手册/自己项目 wiki），清洗文本
- [ ] **任务 2**：TokenTextSplitter 分块入 pgvector（复用 [04](./04-Embedding与向量数据库实战.md)）
- [ ] **任务 3**：Spring AI 实现基础 RAG 问答，带 grounding prompt + 来源引用
- [ ] **任务 4**：加混合检索（向量 + PG 全文/BM25）+ rerank（BGE-reranker 或 API）
- [ ] **任务 5**：建 30 条评估集，量化 Recall@4 与 faithfulness，调参前后对比
- [ ] **任务 6**：加文档增量更新管道（新增/删除文档同步向量库）
- [ ] **任务 7**：前端接 [02](./02-LLM-API集成实战(Java).md) 的 SSE 流式，答案带可点击来源

### 验收标准
- 能问答企业文档并**显示来源**，问库里没有的问题会说"无法回答"
- 评估集 Recall@4 ≥ 85%，能拿出"加 rerank 前后指标对比"数据
- 能完整讲清每个环节的取舍（面试级）

---

## 九、延伸资源
- Spring AI RAG / QuestionAnswerAdvisor 文档
- Ragas 评估框架、BGE-reranker
- 论文/博客：RAG 原始论文、"Lost in the Middle"、RRF
- 关联：[附录 A Spring AI RAG 概念映射](./AI时代开发者技能与概念手册.md)
- 下一篇：[06-Function Calling 与 Agent 开发](./06-Function-Calling与Agent开发.md)

← [返回 06 索引](./README.md)
