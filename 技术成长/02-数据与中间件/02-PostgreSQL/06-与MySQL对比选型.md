# 06 · 与 MySQL 对比与选型

> **预计阅读**：40 min · **难度**：★★★

---

## 1. 选型矩阵

| 场景 | 更倾向 |
|------|--------|
| 复杂 SQL、窗口函数、CTE | **PG** |
| JSON 查询 + 索引 | **PG JSONB** |
| GIS | **PostGIS** |
| 国内 DBA 储备、电商 OLTP | **MySQL** |
| 主从读写分离成熟度 | 两者都可，MySQL 案例更多 |
| 开源协议 | PG 更自由（PostgreSQL License） |
| 云托管 | 阿里云 RDS 两者都有 |

---

## 2. 语法迁移对照

| 功能 | MySQL | PostgreSQL |
|------|-------|------------|
| 自增 | AUTO_INCREMENT | SERIAL / IDENTITY |
| 反引号 | `` `col` `` | `"col"`（一般小写不用） |
| 布尔 | TINYINT(1) | **BOOLEAN** |
| 字符串 | CONCAT() | `\|\|` 或 CONCAT |
| IFNULL | IFNULL(a,b) | COALESCE(a,b) |
| 分页 | LIMIT n OFFSET m | 相同 |
| UPSERT | ON DUPLICATE KEY | **ON CONFLICT** |
| 当前时间 | NOW() | NOW() / CURRENT_TIMESTAMP |

---

## 3. 从 MySQL 迁 PG 注意

1. **BOOLEAN** 真/假，非 0/1
2. **大小写**：未引号标识符 fold 小写
3. **序列**：SERIAL 与 JPA `@GeneratedValue` 策略
4. **DDL 事务**：PG DDL 可包在事务里
5. **性能**：重新 EXPLAIN，索引策略不同
6. **驱动**：换 `org.postgresql`，URL 改 `jdbc:postgresql://`

---

## 4. 双写 / 迁移策略

```
阶段1：新功能写 PG，老数据 MySQL
阶段2：历史数据迁移 + 校验
阶段3：读切 PG，MySQL 只读
阶段4：下线 MySQL
```

工具：Debezium CDC、pgloader、自研对账。

---

## 5. Java ORM

MyBatis / JPA **大部分 SQL 可移植**；注意：

- `@Query nativeQuery` 方言差异
- 分页 `Pageable` JPA 自动方言
- Flyway/Liquibase 迁移脚本 **分 dialect**

---

→ [07-生产案例与面试题库](./07-生产案例与面试题库.md)

← [05-复制与高可用](./05-复制与高可用.md)
