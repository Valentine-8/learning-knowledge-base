# 第二章：认证授权 OAuth 与 JWT

> **阅读目标**：区分认证与授权，掌握 Session/JWT/OAuth2 授权码流程，能设计微服务网关鉴权方案。
>
> **建议用时**：通读 90 min。

---

## 一、认证 vs 授权

| | Authentication | Authorization |
|--|----------------|---------------|
| 问题 | 你是谁？ | 你能做什么？ |
| 手段 | 密码、MFA、证书、JWT | RBAC、ABAC、ACL |
| 失败码 | 401 Unauthorized | 403 Forbidden |

**顺序**：先认证后授权。

---

## 二、Session 认证

### 2.1 流程

```
1. 用户 POST /login 用户名密码
2. 服务端验证 → 创建 Session 存 Redis/内存
3. Set-Cookie: SESSIONID=xxx; HttpOnly; Secure
4. 后续请求带 Cookie，服务端查 Session
5.  logout 销毁 Session
```

### 2.2 优点

- **服务端可控**：随时注销、踢人
- payload 不暴露给客户端
- 改权限立即生效（Session 存 roles）

### 2.3 缺点

- **有状态**：分布式需 Redis 共享 Session
- 跨域 Cookie 麻烦（SameSite、CORS）
- 移动端 Cookie 管理弱

### 2.4 Spring Session

```xml
<!-- Redis 集中 Session -->
spring.session.store-type=redis
```

---

## 三、JWT（JSON Web Token）

### 3.1 结构

```
Header.Payload.Signature
eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0In0.xxx
```

| 部分 | 内容 |
|------|------|
| Header | alg（HS256/RS256）、typ |
| Payload | sub、exp、iat、自定义 claims |
| Signature | HMAC 或 RSA 签名 Header+Payload |

### 3.2 验证

服务端用 **密钥/公钥** 验签 + 检查 `exp`/`nbf`。

**无状态**：不查 DB 即可验身份（权限变更需额外设计）。

### 3.3 优点

- 适合 **分布式、微服务**（网关验签透传）
- 跨域 Header 携带方便
- 移动端友好

### 3.4 缺点与对策

| 问题 | 对策 |
|------|------|
| 难主动失效 | 短 exp + refresh token；黑名单 Redis |
| payload Base64 非加密 | 不存密码、PII |
| 密钥泄露 | RS256 非公钥泄露；密钥轮换 |
| 体积大 | 少塞 claims |

### 3.5 Access + Refresh

```
access token：15 min，访问 API
refresh token：7 d，仅 /refresh，HttpOnly Cookie 或 rotation
```

**Refresh Token Rotation**：每次刷新发新 refresh，旧作废，防窃取重放。

### 3.6 Java 示例（jjwt 概念）

```java
String jwt = Jwts.builder()
    .subject(userId)
    .claim("roles", roles)
    .expiration(new Date(System.currentTimeMillis() + 900_000))
    .signWith(key)
    .compact();

Claims claims = Jwts.parser()
    .verifyWith(key)
    .build()
    .parseSignedClaims(jwt)
    .getPayload();
```

---

## 四、OAuth 2.0

### 4.1 角色

| 角色 | 说明 |
|------|------|
| Resource Owner | 用户 |
| Client | 第三方应用 |
| Authorization Server | 发 token |
| Resource Server | API |

### 4.2 授权码模式（最安全，Web 后端）

```
1. 用户点击「微信登录」
2. 浏览器 redirect 到 AS /authorize?client_id&redirect_uri&scope&state
3. 用户同意
4. redirect 回 client?code=xxx&state=xxx
5. 后端用 code + client_secret 换 access_token（POST /token）
6. 用 access_token 调 Resource Server
```

**为何 code**：token 不经过浏览器；secret 仅在后端。

**state**：防 CSRF，随机串校验。

**PKCE**（公共客户端 SPA/移动端）：

```
code_challenge = BASE64URL(SHA256(code_verifier))
/token 时带 code_verifier 证明同一客户端
```

### 4.3 其他模式

| 模式 | 场景 | 风险 |
|------|------|------|
| 客户端凭证 | 服务间 M2M | secret 保管 |
| 密码模式 | 遗留 | 不推荐 |
| 隐式 | 已废弃 | token 暴露 URL |

### 4.4 OIDC（OpenID Connect）

OAuth2 + **ID Token（JWT）** → 标准化 **身份**（openid scope、userinfo）。

---

## 五、SSO 单点登录

**一次登录，多系统信任**：

- CAS：Ticket + TGT
- OAuth2 联邦：IdP（Keycloak、Okta、企业微信）

**SAML**：企业 AD 常见；XML 断言。

---

## 六、授权模型 RBAC / ABAC

### 6.1 RBAC

```
User → Role → Permission → Resource
```

Spring：`ROLE_ADMIN`、`hasAuthority('order:read')`。

```java
@PreAuthorize("hasAuthority('order:delete')")
public void deleteOrder(Long id) { ... }
```

### 6.2 ABAC

属性策略：`(subject.department == resource.ownerDept) && time.inBusinessHours`。

**Spring**： `@PreAuthorize` SpEL 或 OPA 外部策略引擎。

### 6.3 数据权限

部门树、本人数据、自定义 SQL 片段 → MyBatis 拦截器注入 `dept_id IN (...)`。

---

## 七、Spring Security 过滤器链

```
Request
  → SecurityContextPersistenceFilter
  → UsernamePasswordAuthenticationFilter（表单）
  → BearerTokenAuthenticationFilter（JWT）
  → AuthorizationFilter
  → Controller
```

**配置要点**：

```java
http
  .csrf(csrf -> csrf.disable()) // JWT 无 session 时常关
  .sessionManagement(s -> s.sessionCreationPolicy(STATELESS))
  .oauth2ResourceServer(o -> o.jwt(Customizer.withDefaults()));
```

---

## 八、微服务鉴权架构

```
Client → API Gateway（验 JWT、限流）
           → Service A（信任网关或二次验签）
           → Service B（Feign 透传 Authorization）
```

**服务间**：M2M client_credentials 或 **内部 mTLS**。

**反模式**：JWT 无限期、各服务各自解析不同密钥、网关不校验 exp。

---

## 九、MFA 与密码

- **MFA**：TOTP（Google Authenticator）、短信（弱于 TOTP）
- **密码**：BCrypt 存储；登录限流、锁定
- **找回密码**：一次性 token、邮件链接 exp

---

## 十、面试高频问答

| 问 | 答 |
|----|-----|
| Session 和 JWT？ | Session 服务端状态易注销；JWT 无状态适合分布式 |
| JWT 如何失效？ | 短 exp、黑名单、refresh rotation |
| OAuth2 授权码流程？ | redirect 拿 code，后端换 token |
| 401 和 403？ | 未认证 vs 无权限 |
| PKCE 作用？ | 公共客户端防 code 拦截 |
| OIDC 和 OAuth2？ | OIDC 在 OAuth2 上标准化身份 ID Token |

---

## 十二、Cookie 安全属性组合

```http
Set-Cookie: SESSION=xxx; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=3600
```

| SameSite | 行为 |
|----------|------|
| Strict | 跨站完全不送 |
| Lax | 顶级导航 GET 可送 |
| None | 跨站送，须 Secure |

**跨域 SPA + Cookie**：SameSite=None + Secure + CORS credentials。

---

## 十三、Keycloak / Spring Authorization Server

**Keycloak**：开源 IdP，Realm、Client、Role、OIDC/SAML。

**Spring Authorization Server**（Spring 6）：自建 OAuth2 AS，适合内网统一认证。

```java
// Resource Server 验 JWT
http.oauth2ResourceServer(oauth2 -> oauth2.jwt(Customizer.withDefaults()));
```

---

## 十四、多租户与 JWT claims

```json
{ "sub": "u1", "tenant_id": "t9", "roles": ["USER"] }
```

**网关**解析 tenant_id 路由；**Service** 数据层强制 `WHERE tenant_id = ?` 防串租户。

---

## 十五、Session 固定攻击

攻击者诱用户使用已知 SessionId → 登录后仍同一 Id → 劫持。

**防护**：登录成功 **regenerateSessionId**；Spring Security 默认换 Session。

---

## 十六、LDAP / AD 集成

企业域账号 **LDAP bind** 或 **Spring LDAP** + OAuth2 联邦。注意 LDAP 注入（转义 DN）。

---

## 十七、权限模型设计

```
User → Role → Permission（细粒度 API）
     → DataScope（部门树）
```

**缓存权限**：Redis 存 user permissions，变更时 evict；JWT 内 roles 变更滞后需短 exp。

---

## 十八、面试场景：设计登录体系

**要点**：

- HTTPS 全程
- BCrypt 密码
- 登录限流 + 验证码
- JWT access 15min + refresh HttpOnly
- 注销 refresh 加黑名单
- 敏感操作 MFA
- 审计登录 IP/设备

---

## 十九、OIDC ID Token vs Access Token

| | ID Token | Access Token |
|--|----------|--------------|
| 用途 | 身份（给谁） | 访问资源 |
| 受众 | Client | Resource Server |
| 内容 | profile、email | scope、permissions |

**勿用 access token 当 identity 解析用户**，应 userinfo 或 id_token。

---

## 二十一、Casdoor / Authing 等 SaaS IdP

中小企业常用 **托管 IdP** 快速接入 OAuth2/OIDC，减少自建 Keycloak 运维。

集成模式：Spring Security OAuth2 Client `registrationId` + redirect。

---

## 二十二、Machine-to-Machine 认证

```http
POST /oauth/token
grant_type=client_credentials
client_id=svc-a
client_secret=***
scope=api:read
```

**服务账号** 无用户参与；secret 轮换 + IP 白名单。

---

## 二十三、JWT 算法混淆攻击

攻击者改 Header `alg: none` 或 RS256→HS256（用公钥当 HMAC secret）。

**防护**：库强制验证 alg 白名单；拒绝 none；RS256 与 HS256 密钥分离。

---

## 二十四、Remember-Me 安全

Spring Security Remember-Me Cookie 含 username+expiry+签名。密钥泄露可伪造。

**推荐**：短 Session + refresh token 替代长期 Remember-Me。

---

## 二十五、权限缓存一致性

用户角色变更后 JWT 内 roles 滞后 → **方案**：

1. 短 access token（15min）
2. 权限变更发出版本号，网关比对 force logout
3. 敏感 API 查 DB 实时权限

---

## 二十六、联邦登录账号绑定

微信 openid 首次登录 → 创建本地 user 或 **绑定已有手机号**（防冒领）。

**合并账号**：同一手机号多种 OAuth provider 指向同一 userId。

---

## 二十七、小结

```
认证：Session（有状态）vs JWT（无状态+refresh）
OAuth2：授权码+PKCE；M2M 用 client_credentials
授权：RBAC @PreAuthorize、数据权限拦截
微服务：网关验签、短 token、密钥轮换
```

下一章：[03-加密与API安全.md](./03-加密与API安全.md)

← [01-Web攻击与防护](./01-Web攻击与防护.md) · [README](./README.md)
