# 01 · 文档模型与 CRUD

> **预计阅读**：60 min · **难度**：★★★

---

## 1. BSON 与文档模型

MongoDB 存储单元是 **Document**（文档），格式为 **BSON**（Binary JSON）。

| BSON 类型 | 说明 | Java 映射 |
|-----------|------|-----------|
| ObjectId | 12 字节唯一 ID | `org.bson.types.ObjectId` |
| String | UTF-8 | `String` |
| Int32/Int64 | 整数 | `Integer` / `Long` |
| Double | 浮点 | `Double` |
| Boolean | 布尔 | `Boolean` |
| Date | UTC 毫秒 | `java.util.Date` / `Instant` |
| Array | 有序数组 | `List` |
| Document/Embedded | 嵌套文档 | 嵌套 POJO / `Document` |
| Decimal128 | 高精度小数 | `BigDecimal` |
| Null | 空值 | `null` |

**ObjectId 结构**（面试常考）：

```
4 字节时间戳 | 5 字节随机 | 3 字节计数器
→ 大致有序，利于 _id 索引插入性能
```

---

## 2. 集合与数据库

```
Database（库）
  └── Collection（集合，≈ 表）
        └── Document（文档，≈ 行）
```

| 特点 | 说明 |
|------|------|
| 无固定 Schema | 同集合文档字段可不同 |
| _id 唯一 | 默认 ObjectId，可自定义 |
| 嵌套 | 数组、子文档代替 JOIN |
| 16MB 限制 | 单文档最大 16MB |

---

## 3. Schema 设计原则

### 嵌入 vs 引用

| 嵌入（Denormalize） | 引用（Normalize） |
|--------------------|-------------------|
| 1:N 且常一起读 | N:N 或独立生命周期 |
| 子数据量小 | 子数据频繁独立更新 |
| 读多写少 | 避免文档膨胀 |

**示例 — 订单嵌入明细**：

```javascript
{
  _id: ObjectId("..."),
  userId: 1001,
  items: [
    { sku: "A001", qty: 2, price: 99.0 },
    { sku: "B002", qty: 1, price: 199.0 }
  ],
  total: 397.0,
  createdAt: ISODate("2026-01-15T08:00:00Z")
}
```

### 反模式警示

| 反模式 | 问题 |
|--------|------|
| 无限增长数组 | 文档超 16MB、重写成本高 |
| 过深嵌套 | 更新路径复杂、索引困难 |
| 把 MongoDB 当 MySQL | 大量 `$lookup` 性能差 |

---

## 4. CRUD 详解

### Create

```javascript
db.products.insertOne({ name: "手机", price: 3999, stock: 100 })
db.products.insertMany([{ name: "A" }, { name: "B" }], { ordered: false })
```

### Read

```javascript
// 投影：只返回指定字段
db.users.find({ status: 1 }, { name: 1, email: 1, _id: 0 })

// 比较：$gt $gte $lt $lte $ne $in $nin
db.orders.find({ amount: { $gte: 100, $lt: 500 } })

// 逻辑：$and $or $not $nor
db.users.find({ $or: [{ age: { $lt: 18 } }, { vip: true }] })

// 数组：$all $size $elemMatch
db.products.find({ tags: { $all: ["hot", "new"] } })
```

### Update

```javascript
// 更新运算符
db.users.updateOne(
  { _id: ObjectId("...") },
  {
    $set: { age: 30 },
    $inc: { loginCount: 1 },
    $push: { tags: "active" },
    $pull: { tags: "inactive" },
    $unset: { tempField: "" }
  }
)

// upsert：不存在则插入
db.counters.updateOne(
  { _id: "orderId" },
  { $inc: { seq: 1 } },
  { upsert: true }
)
```

### Delete

```javascript
db.logs.deleteMany({ createdAt: { $lt: ISODate("2025-01-01") } })
```

---

## 5. 查询运算符速表

| 类别 | 运算符 |
|------|--------|
| 比较 | `$eq` `$gt` `$gte` `$lt` `$lte` `$ne` `$in` `$nin` |
| 逻辑 | `$and` `$or` `$not` `$nor` |
| 元素 | `$exists` `$type` |
| 数组 | `$all` `$elemMatch` `$size` |
| 正则 | `{ field: /pattern/i }` |
| 文本 | `$text` `$search`（需文本索引） |

---

## 6. 多文档事务

MongoDB 4.0+ 副本集支持多文档 ACID 事务（4.2+ 分片集群支持）。

```javascript
const session = db.getMongo().startSession()
session.startTransaction()
try {
  const orders = session.getDatabase("shop").orders
  const inventory = session.getDatabase("shop").inventory
  orders.insertOne({ ... }, { session })
  inventory.updateOne({ sku: "A" }, { $inc: { stock: -1 } }, { session })
  session.commitTransaction()
} catch (e) {
  session.abortTransaction()
} finally {
  session.endSession()
}
```

| 注意 | 说明 |
|------|------|
| 性能 | 事务有开销，能单文档原子则不用事务 |
| 超时 | 默认 60s，长事务阻塞 oplog |
| Java | `@Transactional` + MongoTransactionManager |

---

## 7. 与 Java 开发者相关的设计建议

1. **字段命名**：camelCase 与 Java POJO 一致，避免 `_id` 映射问题用 `@Id`。
2. **时间字段**：统一 `Instant` 或 `Date`，存 UTC。
3. **金额**：用 `Decimal128` 或整数分，避免 Double 精度问题。
4. **分页**：用 `_id > lastId` 游标分页，避免深 `skip`。
5. **版本控制**：`@Version` 乐观锁，或业务字段 `version`。

---

## 8. 小结

| 要点 | 一句话 |
|------|--------|
| 模型 | 文档嵌套优先，引用次之 |
| CRUD | 更新用 `$set`/`$inc` 等运算符，避免全量替换 |
| 事务 | 需要再用，注意性能与超时 |
| 设计 | 按访问模式设计，不是按表范式 |

---

← [00 速查](./00-速查总览.md) · [02 索引与聚合 →](./02-索引与聚合.md)
