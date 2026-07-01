# 03 · JSON 与高级类型

> **预计阅读**：50 min · **难度**：★★★★

---

## 1. JSON vs JSONB

| | JSON | JSONB |
|---|------|-------|
| 存储 | 文本，保留格式 | 二进制，键去重 |
| 插入 | 略快 | 略慢（转换） |
| 查询索引 | 弱 | **GIN 索引** |
| 推荐 | 日志存档 | **业务查询** |

```sql
CREATE TABLE event (
  id BIGSERIAL PRIMARY KEY,
  payload JSONB NOT NULL
);
```

---

## 2. JSONB 操作符

| 操作符 | 含义 |
|--------|------|
| `->` | 取 JSON 对象字段（JSON） |
| `->>` | 取文本 |
| `#>` | 路径 `'{a,b}'` |
| `@>` | 左包含右 |
| `?` | 键是否存在 |
| `?|` | 任一键存在 |
| `?&` | 全部键存在 |

```sql
SELECT payload->>'type' FROM event WHERE payload @> '{"userId":100}';

SELECT * FROM event
WHERE payload->'tags' ? 'vip';

UPDATE event SET payload = jsonb_set(payload, '{status}', '"done"')
WHERE id = 1;
```

---

## 3. GIN 索引

```sql
CREATE INDEX idx_event_payload ON event USING GIN (payload);

-- 只索引某路径
CREATE INDEX idx_event_user ON event USING GIN ((payload->'userId'));
```

**Java + JPA**：可用 `@JdbcTypeCode(SqlTypes.JSON)`（Hibernate 6）：

```java
@Entity
public class Event {
    @JdbcTypeCode(SqlTypes.JSON)
    @Column(columnDefinition = "jsonb")
    private Map<String, Object> payload;
}
```

---

## 4. 数组类型

```sql
CREATE TABLE article (
  id SERIAL PRIMARY KEY,
  tags TEXT[]
);

INSERT INTO article(tags) VALUES (ARRAY['java','pg']);
SELECT * FROM article WHERE 'java' = ANY(tags);

CREATE INDEX idx_tags ON article USING GIN (tags);
```

---

## 5. 全文检索

```sql
ALTER TABLE doc ADD COLUMN tsv tsvector
  GENERATED ALWAYS AS (to_tsvector('simple', title || ' ' || body)) STORED;

CREATE INDEX idx_doc_tsv ON doc USING GIN (tsv);

SELECT * FROM doc WHERE tsv @@ to_tsquery('simple', 'PostgreSQL & 索引');
```

中文需 `zhparser` 等扩展。

---

## 6. 其他扩展（了解）

| 扩展 | 用途 |
|------|------|
| PostGIS | 地理空间 |
| pg_trgm | 模糊 LIKE 加速 |
| citext | 大小写不敏感文本 |
| uuid-ossp | UUID 生成 |

---

## 7. 场景：动态属性表

**MySQL**：EAV 表或 JSON 无索引。

**PG**：JSONB + GIN，适合 SaaS 元数据、表单配置。

```sql
-- CRM 自定义字段
SELECT * FROM contact
WHERE custom_fields @> '{"industry":"finance"}';
```

---

→ [04-事务锁与并发](./04-事务锁与并发.md)

← [02-索引与执行计划](./02-索引与执行计划.md)
