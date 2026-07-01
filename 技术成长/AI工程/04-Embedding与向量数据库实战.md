# 04 · Embedding 与向量数据库实战

> **能力层**：L3 集成者　**难度**：★★★　**预计工时**：12h
> **一句话**：把文本变成向量、存进向量库、用相似度检索——这是 RAG、语义搜索、推荐、去重的共同底座。
> **前置**：[02-LLM-API集成实战](./02-LLM-API集成实战(Java).md)、SQL 基础、Docker。

---

## 一、Embedding 是什么（Java 工程师视角）

Embedding = 把一段文本（或图片）映射成一个**定长浮点数组**（向量），语义相近的文本向量在空间里也相近。

```
"苹果手机"      → [0.12, -0.34, 0.88, ...]   (1024 维)
"iPhone"       → [0.11, -0.31, 0.90, ...]   ← 和上面很近
"苹果水果"      → [0.45,  0.20, -0.1, ...]   ← 离得较远
```

**关键认知**：
- 维度是固定的（如 1024、1536、768），由模型决定
- 相似度用**余弦相似度**或**内积**衡量，不是字面匹配
- 这让机器能做"语义搜索"——搜"如何提升接口性能"也能命中"优化 API 响应时间"的文档

### 和数据库全文检索（like/ES）的区别

| | 关键词检索(ES/like) | 向量检索 |
|--|--------------------|----------|
| 匹配 | 字面/分词匹配 | 语义相似 |
| "笔记本电脑" 能否命中 "notebook" | 否（除非同义词库） | 能 |
| 精确匹配"订单号12345" | 强 | 弱 |
| 结论 | 二者互补，生产常**混合检索** | 见 [05-RAG](./05-RAG系统工程化实战.md) |

---

## 二、生成 Embedding（Java 代码）

### 2.1 Spring AI EmbeddingModel

```java
@Service
public class EmbeddingService {
    private final EmbeddingModel embeddingModel;

    public float[] embed(String text) {
        return embeddingModel.embed(text);
    }

    public List<float[]> embedBatch(List<String> texts) {
        // 批量更省钱省时间
        return embeddingModel.embed(texts).stream()
                .map(e -> e).toList();
    }
}
```

配置（可用云 API 或本地）：
```yaml
spring:
  ai:
    openai:
      embedding:
        options:
          model: text-embedding-v3   # 通义；OpenAI 是 text-embedding-3-small
# 或本地 Ollama：
# base-url: http://localhost:11434  model: nomic-embed-text
```

### 2.2 Embedding 模型选型

| 模型 | 维度 | 特点 |
|------|------|------|
| OpenAI text-embedding-3-small | 1536 | 通用强，便宜 |
| OpenAI text-embedding-3-large | 3072 | 更准，贵 |
| 通义 text-embedding-v3 | 1024 | 中文好，国内 |
| BGE-M3（智源，可本地） | 1024 | 中英双语开源标杆，支持稠密+稀疏 |
| nomic-embed-text（Ollama） | 768 | 本地免费 |

**选型要点**：① 中文场景选中文优化模型（通义/BGE）；② **入库和查询必须用同一个模型**，换模型要全部重新 embedding；③ 维度越高越准但越占存储和计算。

---

## 三、向量数据库选型

| 方案 | 定位 | 何时选 |
|------|------|--------|
| **pgvector**（Postgres 扩展） | 在 PG 里加向量能力 | ★推荐入门/中小规模，已有 PG、想少运维、要和业务数据 join |
| **Qdrant** | 专用向量库(Rust) | 中大规模、要高级过滤、性能好 |
| **Milvus** | 分布式向量库 | 亿级向量、大规模生产 |
| **Redis (RediSearch)** | 已有 Redis 加向量 | 已重度用 Redis、低延迟 |
| **Elasticsearch** | 全文+向量 | 已有 ES、要混合检索 |
| Chroma / Weaviate | 轻量/云 | 快速原型 |

**给 Java 工程师的建议**：从 **pgvector** 学起——SQL 心智你最熟，能和现有业务表在一个库里，学完立刻能用。规模大了再上 Qdrant/Milvus。

---

## 四、pgvector 实战（从零跑通）

### 4.1 启动

```bash
docker run -d --name pgvector -p 5432:5432 \
  -e POSTGRES_PASSWORD=postgres pgvector/pgvector:pg16
```

### 4.2 建表与索引

```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE doc_chunk (
    id          BIGSERIAL PRIMARY KEY,
    doc_id      BIGINT,
    content     TEXT,
    metadata    JSONB,
    embedding   vector(1024)          -- 维度要和模型一致！
);

-- 向量索引：HNSW（推荐，查询快）或 IVFFlat
CREATE INDEX ON doc_chunk USING hnsw (embedding vector_cosine_ops);
```

### 4.3 距离运算符

| 运算符 | 含义 | 用于 |
|--------|------|------|
| `<=>` | 余弦距离 | **最常用**（配 cosine 索引）|
| `<->` | 欧氏距离(L2) | |
| `<#>` | 负内积 | 归一化向量时等价余弦 |

### 4.4 检索 SQL

```sql
-- 查与查询向量最相似的 5 条
SELECT id, content, 1 - (embedding <=> :queryVec) AS similarity
FROM doc_chunk
ORDER BY embedding <=> :queryVec     -- 距离升序 = 相似度降序
LIMIT 5;

-- 带元数据过滤（向量库最实用的能力）
SELECT content FROM doc_chunk
WHERE metadata->>'department' = 'tech'
ORDER BY embedding <=> :queryVec LIMIT 5;
```

### 4.5 Java 写入与查询

**用 Spring AI 的 VectorStore（推荐，屏蔽 SQL）**：

```java
@Bean
VectorStore vectorStore(EmbeddingModel embeddingModel, JdbcTemplate jdbcTemplate) {
    return PgVectorStore.builder(jdbcTemplate, embeddingModel)
        .dimensions(1024)
        .distanceType(COSINE_DISTANCE)
        .build();
}

// 写入
vectorStore.add(List.of(
    new Document("Spring 事务传播行为有7种...", Map.of("source", "spring.md", "page", 3)),
    new Document("MySQL 索引最左前缀原则...",   Map.of("source", "mysql.md"))
));

// 检索
List<Document> results = vectorStore.similaritySearch(
    SearchRequest.query("Spring 事务怎么配置")
        .withTopK(4)
        .withSimilarityThreshold(0.5)
        .withFilterExpression("source == 'spring.md'")   // 元数据过滤
);
```

**手写 JDBC（理解底层）**：
```java
public void save(String content, float[] embedding) {
    jdbc.update("INSERT INTO doc_chunk(content, embedding) VALUES (?, ?::vector)",
        content, toVectorLiteral(embedding));   // "[0.1,0.2,...]"
}
```

---

## 五、索引原理（面试高频）

精确 KNN（暴力算所有距离）在大数据量下太慢，生产用 **ANN（近似最近邻）**，牺牲一点点召回换巨大速度。

| 索引 | 原理 | 特点 |
|------|------|------|
| **HNSW** | 分层可导航小世界图 | 查询快、召回高、内存占用大、构建慢。**首选** |
| **IVFFlat** | 聚类分桶，只搜最近的几个桶 | 内存省、构建快、召回略低，需设 `lists`/`probes` |
| Flat(暴力) | 全量比对 | 100% 准确但慢，仅小数据 |

关键参数：
- HNSW：`m`（每节点连接数）、`ef_construction`（构建质量）、`ef_search`（查询时探索范围，越大越准越慢）
- IVFFlat：`lists`（桶数）、`probes`（查询探测桶数）

**取舍口诀**：召回率 vs 延迟 vs 内存，三者权衡；HNSW 偏性能/召回，IVFFlat 偏省内存。

---

## 六、常见坑

| 坑 | 现象 | 解法 |
|----|------|------|
| 入库/查询模型不一致 | 检索结果全乱 | 固定同一 embedding 模型；换模型全量重建 |
| 维度不匹配 | 插入报错 | 表 vector(N) 的 N 必须等于模型维度 |
| 没建索引 | 数据量大后查询巨慢 | 建 HNSW/IVFFlat 索引 |
| IVFFlat 建索引时表是空的 | 召回差 | IVFFlat 要在有数据后建索引（聚类需样本）|
| 忘了归一化 | 内积距离结果怪 | 用 cosine，或先归一化再用内积 |
| 只做向量检索 | 精确词/编号搜不准 | 混合检索(向量+BM25)，见 [05](./05-RAG系统工程化实战.md) |
| 一次 embedding 一条 | 慢、贵 | 批量 embedding |
| 大文档整篇 embedding | 检索粒度太粗 | 先分块(chunking)，见 [05](./05-RAG系统工程化实战.md) |

---

## 七、面试考点

- **Q：Embedding 是什么？为什么能做语义搜索？**
  A：把文本映射为定长向量，语义相近则向量距离近；检索时比较查询向量与库中向量的相似度（余弦/内积），从而实现语义而非字面匹配。
- **Q：向量检索和 ES 全文检索区别？生产怎么用？**
  A：全文是字面/分词匹配，向量是语义匹配；各有短板，生产常混合检索（向量召回 + 关键词召回，再融合/rerank）。
- **Q：HNSW 和 IVFFlat 区别？**
  A：HNSW 是图索引，查询快召回高但费内存；IVFFlat 是聚类倒排，省内存构建快但召回略低、需调 probes。都属于 ANN 近似检索。
- **Q：为什么要用近似最近邻(ANN)而不是精确？**
  A：精确 KNN 是 O(N) 暴力比对，海量向量下不可接受；ANN 牺牲极小召回换数量级性能提升。
- **Q：换 embedding 模型要注意什么？**
  A：入库和查询必须同模型同维度，换模型必须全量重新向量化。

---

## 八、动手任务（本篇产出）

- [ ] **任务 1**：Docker 起 pgvector，建表 + HNSW 索引，手写 SQL 插入/检索 3 条数据
- [ ] **任务 2**：Spring AI EmbeddingModel 把 20 段文本向量化，用 VectorStore 入库
- [ ] **任务 3**：实现语义搜索接口：输入一句话，返回 top-4 最相似文本 + 相似度分数
- [ ] **任务 4**：加元数据过滤（按 source/department 过滤）
- [ ] **任务 5（对比实验）**：同样的查询，用 `like` 全文匹配 vs 向量检索，对比命中差异，写笔记
- [ ] **任务 6（进阶）**：Docker 起 Qdrant，用 Spring AI 换成 QdrantVectorStore，对比 pgvector

### 验收标准
- 能解释一次相似度检索在 SQL 层发生了什么
- 语义搜索能命中"意思相近但用词不同"的文本
- 能说清 HNSW/IVFFlat 取舍

---

## 九、延伸资源
- pgvector GitHub README（索引/运算符/调参）
- Qdrant、Milvus 官方文档
- BGE-M3 / 通义 embedding 模型文档
- 下一篇：[05-RAG 系统工程化实战](./05-RAG系统工程化实战.md) —— 把向量检索组装成完整问答系统

← [返回 06 索引](./README.md)
