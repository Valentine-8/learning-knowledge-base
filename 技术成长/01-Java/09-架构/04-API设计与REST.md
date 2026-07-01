# 04 · API 设计与 REST

> **预计阅读**：70 min

---

## 1. API 设计原则

| 原则 | 说明 |
|------|------|
| 一致性 | 命名、分页、错误格式统一 |
| 可演进 | 版本策略、向后兼容 |
| 安全默认 | 鉴权、限流、输入校验 |
| 可观测 | traceId、结构化日志 |
| 文档化 | OpenAPI/Swagger |

---

## 2. RESTful 规范

### 2.1 资源与 URI

```
GET    /orders/{id}          查询
POST   /orders               创建
PUT    /orders/{id}          全量更新
PATCH  /orders/{id}          部分更新
DELETE /orders/{id}          删除
```

**好**：名词复数、层级清晰 `/users/{id}/orders`
**差**：动词 URI `/getOrder`、`/createOrder`

### 2.2 HTTP 状态码

| 码 | 含义 |
|----|------|
| 200 | 成功（GET/PUT/PATCH） |
| 201 | 创建成功 |
| 204 | 删除成功无 body |
| 400 | 客户端参数错误 |
| 401 | 未认证 |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 409 | 冲突（重复创建） |
| 429 | 限流 |
| 500 | 服务端错误 |

业务错误可用 200 + 业务码，或 4xx + 统一错误体（团队统一即可）。

---

## 3. 幂等性

| 方法 | 幂等 |
|------|------|
| GET/PUT/DELETE | 天然幂等 |
| POST | 不幂等，需额外机制 |

**POST 幂等方案**：

1. **幂等键**（Idempotency-Key Header）
2. **唯一业务键**（订单号、请求号）
3. **Token 机制**（先取 token 再提交）

```java
@PostMapping("/orders")
public Order create(@RequestHeader("Idempotency-Key") String key, ...) {
    return idempotentService.execute(key, () -> orderService.create(...));
}
```

---

## 4. 版本管理

| 方式 | 示例 | 优缺点 |
|------|------|--------|
| URI 路径 | `/v1/orders` | 直观，URL 变 |
| Header | `Accept-Version: v1` | URI 干净 |
| 参数 | `?version=1` | 易忘 |

**兼容策略**：新增字段可选；废弃字段保留一版；Breaking Change 升 major。

---

## 5. 分页与排序

### 5.1 Offset 分页

```
GET /orders?page=1&size=20
```

深分页性能差（`OFFSET 100000`）。

### 5.2 Cursor 分页（推荐）

```
GET /orders?cursor=eyJpZCI6MTIzfQ&limit=20
```

基于 `(created_at, id)` 复合游标，稳定且高效。

---

## 6. 统一响应与错误码

```json
{
  "code": "ORDER_NOT_FOUND",
  "message": "订单不存在",
  "traceId": "abc123",
  "data": null
}
```

| 要求 | 说明 |
|------|------|
| 业务码 | 机器可读，文档维护 |
| message | 人类可读，可 i18n |
| 不泄露 | 无堆栈、无 SQL |
| traceId | 关联日志排查 |

---

## 7. 安全与限流

- **认证**：JWT / OAuth2 / API Key
- **授权**：RBAC、资源级权限
- **校验**：Bean Validation、`@Valid`
- **限流**：网关 + 接口级
- **防重放**：timestamp + nonce + 签名

---

## 8. 非 REST 场景

| 场景 | 选型 |
|------|------|
| 复杂查询 | GraphQL（BFF 层） |
| 高性能 RPC | gRPC（内部服务） |
| 实时推送 | WebSocket / SSE |
| 文件上传 | multipart + 分片 |

对外 REST，对内 gRPC 是常见组合。

---

## 9. OpenAPI 实践

```yaml
openapi: 3.0.0
paths:
  /orders:
    post:
      summary: 创建订单
      parameters:
        - name: Idempotency-Key
          in: header
          required: true
```

- 契约先行或代码生成二选一
- CI 校验 Breaking Change

---

## 10. 面试要点

1. REST 和 RPC 区别？
2. 如何保证 POST 幂等？
3. cursor 分页原理？
4. 401 和 403 区别？
5. API 版本如何演进？

← [03-设计模式](./03-设计模式实战.md) · [05-系统设计](./05-系统设计方法论.md)
