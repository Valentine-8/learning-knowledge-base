# 04 · JPA 与 MyBatis 选型

> **预计阅读**：70 min

---

## 1. 核心差异

| 维度 | JPA/Hibernate | MyBatis |
|------|---------------|---------|
| 范式 | ORM，对象导向 | SQL 映射 |
| SQL | 自动生成为主 | 手写为主 |
| 学习 | 关联、缓存、状态复杂 | SQL 简单直接 |
| 动态 SQL | Criteria/Specification | XML/注解灵活 |
| 批量/复杂报表 | 较弱 | 强 |
| 迁移成本 | 换 DB 相对易 | SQL 方言绑定 |

---

## 2. 适合 JPA 的场景

- 领域模型丰富，CRUD 为主
- 标准 REST 资源操作
- 团队熟悉 DDD + Spring Data
- 多表关联但查询不极端复杂
- 快速原型、Startup

```java
// 几行代码 CRUD + 分页
orderRepo.findByUserId(uid, pageable);
```

---

## 3. 适合 MyBatis 的场景

- 复杂 SQL、多表 join、报表统计
- DBA 深度参与 SQL 优化
- 遗留系统大量存储过程
- 需要精确控制执行计划
- 批量 ETL、异构数据源

详见 [Spring/08-MyBatis映射与缓存.md](../Spring/08-MyBatis映射与缓存.md)。

---

## 4. 对比实例

**需求**：订单列表带用户名、商品数、分页

| JPA | MyBatis |
|-----|---------|
| EntityGraph + DTO 或多次查询 | 一条 SQL join 搞定 |
| 可能 N+1 需优化 | SQL 可控 |

**需求**：简单按 ID 查订单

| JPA | MyBatis |
|-----|---------|
| `findById` 一行 | Mapper + XML 略啰嗦 |

---

## 5. 混合使用

```
Spring Boot 项目可同时引入：
- Spring Data JPA：常规 CRUD
- MyBatis：复杂查询模块
```

注意：

- 事务统一 `@Transactional`
- 不双重映射同一表到两套模型（除非清晰分层）
- 团队规范哪层用哪种

---

## 6. JPA 常见痛点

| 痛点 | 应对 |
|------|------|
| N+1 | fetch join、BatchSize |
| 懒加载异常 | 事务边界、DTO |
| 复杂查询难写 | Specification 或改 MyBatis |
| 性能黑盒 | 开 SQL 日志、explain |
| ddl-auto 误用 | 生产 validate + Flyway |

---

## 7. MyBatis 常见痛点

| 痛点 | 应对 |
|------|------|
| SQL 分散 | XML 规范、Review |
| 重复 CRUD | MyBatis-Plus（了解） |
| 映射样板代码 | MapStruct |
| 缓存一致性 | 慎用二级缓存，用 Redis |

---

## 8. 选型 ADR 模板

```markdown
## 决策：订单核心用 JPA，报表用 MyBatis
- JPA：订单 CRUD、状态机
- MyBatis：运营报表、对账 SQL
- 理由：开发效率 vs SQL 可控
```

---

## 9. Spring Boot 3 趋势

- Spring Data JPA 持续增强
- Hibernate 6：更好的 JSON、批处理
- 虚拟线程降低 ORM 阻塞 concern
- **没有绝对赢家**，看团队与场景

---

## 10. 面试要点

1. JPA 和 MyBatis 区别？
2. 各自适用场景？
3. 能否混用？
4. N+1 是 JPA 特有问题吗？
5. 复杂报表选哪个？

← [03-JPQL性能](./03-JPQL与性能N+1.md) · [05-案例题库](./05-生产案例与面试题库.md)
