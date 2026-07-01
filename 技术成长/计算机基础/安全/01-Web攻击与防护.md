# 第一章：Web 攻击与防护

> **阅读目标**：识别 OWASP Top 10 级 Web 攻击，能在 Spring/MyBatis 栈落地防护与 Code Review 检查点。
>
> **建议用时**：通读 90 min。

---

## 一、安全思维模型

### 1.1 信任边界

```
不可信输入（用户、第三方回调、Header、文件名）
    ↓ 校验、转义、最小权限
业务逻辑 + 数据层
    ↓
不可信输出（HTML、JSON、日志、错误信息）
```

**默认拒绝**：白名单优于黑名单。

### 1.2 STRIDE（了解）

| 威胁 | 含义 |
|------|------|
| Spoofing | 冒充 |
| Tampering | 篡改 |
| Repudiation | 抵赖 |
| Information Disclosure | 泄露 |
| Denial of Service | 拒绝服务 |
| Elevation of Privilege | 提权 |

---

## 二、SQL 注入（SQLi）

### 2.1 原理

拼接 SQL：

```java
// 危险
"SELECT * FROM user WHERE name = '" + name + "'"
// name = ' OR '1'='1
```

### 2.2 防护

| 措施 | 说明 |
|------|------|
| **预编译参数化** | MyBatis `#{}`、JPA `?` |
| ORM | 避免原生 SQL 拼接 |
| 最小权限 DB 账号 | 无 DROP、仅必要表 |
| WAF | 纵深防御 |

**MyBatis**：

```xml
<!-- 安全 -->
<select id="find">SELECT * FROM user WHERE id = #{id}</select>
<!-- 危险：${} 字符串替换，仅用于列名白名单场景 -->
```

### 2.3 二次注入

存入数据库的恶意 payload 在 **另一查询** 被拼接触发 → 入库也要校验。

---

## 三、XSS（跨站脚本）

### 3.1 类型

| 类型 | 存储 | 反射 | DOM |
|------|------|------|-----|
| 持久化 | 存 DB 展示 | URL 参数回显 | 前端 JS 改 DOM |
| 危害 | 偷 Cookie、钓鱼 | 需诱骗点击 | 不经过服务端 |

### 3.2 防护

- **输出编码**：HTML、JS、URL、CSS 上下文不同编码
- **CSP** Content-Security-Policy：限制脚本源
- **HttpOnly Cookie**：JS 读不到 SessionId
- **模板引擎**：Thymeleaf 默认 HTML 转义；`th:utext` 慎用

```http
Content-Security-Policy: default-src 'self'; script-src 'self'
```

### 3.3 Java 实践

```java
// Spring 返回 JSON 一般自动转义
// 切忌把用户输入拼进 innerHTML
String safe = HtmlUtils.htmlEscape(userInput);
```

---

## 四、CSRF（跨站请求伪造）

### 4.1 原理

用户已登录 bank.com，访问 evil.com 页面：

```html
<img src="https://bank.com/transfer?to=hacker&amount=10000">
```

浏览器 **自动带 Cookie**，服务端认为是用户操作。

### 4.2 防护

| 措施 | 说明 |
|------|------|
| CSRF Token | 表单/Header 带随机 token，服务端校验 |
| SameSite Cookie | Lax/Strict 减跨站携带 |
| 验证 Referer/Origin | 辅助 |
| 二次验证 | 支付密码、短信 |

**Spring Security** 默认 CSRF 对 session 表单启用；REST + JWT 常关闭 CSRF（无 Cookie 会话）。

```java
http.csrf(csrf -> csrf
    .csrfTokenRepository(CookieCsrfTokenRepository.withHttpOnlyFalse()));
```

### 4.3 CSRF vs XSS

XSS 能 **读页面/偷 token** → CSRF token 也可被 XSS 绕过；**先防 XSS**。

---

## 五、SSRF（服务端请求伪造）

### 5.1 原理

应用根据用户 URL 发起 **服务端请求**：

```
url=http://127.0.0.1:6379/  → 打内网 Redis
url=file:///etc/passwd      → 读文件（部分库）
```

### 5.2 防护

- URL **白名单** 域名
- 禁止内网 IP 段（10/8、172.16、127、169.254 metadata）
- 禁用 redirect 跟随或二次校验
- 独立 **DMZ 网络** 出网策略

**云环境**：IMDSv2 防 metadata SSRF（AWS 169.254.169.254）。

---

## 六、文件上传

### 6.1 风险

- WebShell（`.jsp`、`.php`）
- **路径穿越** `../../../etc/passwd`
- 超大文件 DoS
- 图片马 + 解析漏洞

### 6.2 防护

| 措施 | 说明 |
|------|------|
| 扩展名+MIME 白名单 | 不只信 Content-Type |
| 重命名随机 | UUID 文件名 |
| 存对象存储 | 非 Web 根目录 |
| 病毒扫描 | ClamAV 等 |
| 大小限制 | Spring `multipart` max |

```yaml
spring:
  servlet:
    multipart:
      max-file-size: 10MB
      max-request-size: 10MB
```

---

## 七、越权（BOLA/IDOR）

### 7.1 水平越权

改 URL 中 `orderId=123` → `124` 看别人订单。

### 7.2 垂直越权

普通用户调用 `/admin/**` API。

### 7.3 防护

- **服务端校验资源归属**：`order.getUserId().equals(currentUserId)`
- **RBAC**：`@PreAuthorize("hasRole('ADMIN')")`
- 不用 **仅隐式** 依赖前端隐藏按钮

```java
@PreAuthorize("@orderAuth.canAccess(#orderId, authentication)")
public Order getOrder(Long orderId) { ... }
```

---

## 八、其他 Web 风险

| 攻击 | 简述 | 防护 |
|------|------|------|
| 点击劫持 | iframe  overlay | X-Frame-Options / CSP frame-ancestors |
| 开放重定向 | `?redirect=http://evil` | 白名单 URL |
|  mass assignment | 绑定过多字段改 role | DTO + 忽略未知字段 |
| XXE | XML 外部实体 | 禁用 DTD、用 JSON |
| 反序列化 | Java ObjectInputStream | 不接收不可信序列化、白名单 |
| 日志注入 | 换行伪造日志 |  sanitize、结构化日志 |

**Log4Shell（CVE-2021-44228）**：JNDI lookup → 升级 Log4j、禁 JNDI。

---

## 九、Spring 安全清单

- [ ] MyBatis 全 `#{}`，`${}` 仅列表白名单
- [ ] Thymeleaf 默认转义，JSON 不拼 HTML
- [ ] CSRF / SameSite 按架构选型
- [ ] `@PreAuthorize` 接口级授权
- [ ] 上传白名单 + OSS
- [ ] 全局 `@ControllerAdvice` 不泄露堆栈给前端
- [ ] Security Header：`X-Content-Type-Options`、`CSP`

```java
http.headers(h -> h
    .contentTypeOptions(Customizer.withDefaults())
    .frameOptions(f -> f.deny()));
```

---

## 十、面试高频问答

| 问 | 答 |
|----|-----|
| SQL 注入防？ | 预编译、ORM、最小权限 |
| 存储型 XSS？ | 入库转义、出库编码、CSP、HttpOnly |
| CSRF 原理？ | 借 Cookie 发 forged 请求；Token/SameSite |
| SSRF 危害？ | 打内网、云 metadata、读本地 |
| 水平越权？ | 服务端校验数据归属 |
| `#{}` 和 `${}`？ | 前者预编译；后者字符串替换有注入风险 |

---

## 十一、HTTP 安全 Header 详解

```http
Content-Security-Policy: default-src 'self'; script-src 'self' 'nonce-{random}'
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Referrer-Policy: no-referrer
Permissions-Policy: camera=(), microphone=()
```

**CSP nonce**：配合 Thymeleaf `th:attr="nonce=${nonce}"` 允许内联脚本。

---

## 十二、Deserialization 反序列化

**Java ObjectInputStream** 读不可信数据 → **RCE**（Commons Collections 链）。

**防护**：

- 禁止 Java 原生序列化跨信任边界
- 用 JSON + 白名单类型
- `ObjectInputFilter`（JEP 290）

```java
ObjectInputFilter filter = ObjectInputFilter.Config.createFilter(
    "com.myapp.**;!*");
ois.setObjectInputFilter(filter);
```

---

## 十三、XXE 与 XML 外部实体

```xml
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
<foo>&xxe;</foo>
```

**防护**：禁用 DTD、禁用 external entity；Jackson XML、`DocumentBuilderFactory` 设 `FEATURE_SECURE_PROCESSING`。

**优先 JSON** 替代 XML 接口。

---

## 十四、开放重定向

```java
// 危险
return "redirect:" + request.getParameter("url");
```

**防护**：白名单域名；仅允许相对路径 `/internal/path`。

---

## 十五、Mass Assignment 批量赋值

```java
// 危险：用户 JSON 含 "role":"ADMIN"
@Data
class UserDTO { String name; String role; }
```

**防护**：Register DTO 不含敏感字段；`@JsonIgnoreProperties(ignoreUnknown = true)`；显式 set 允许字段。

---

## 十六、Clickjacking 点击劫持

攻击者 iframe 透明 overlay 诱骗点击「转账」。

**防护**：`X-Frame-Options: DENY` 或 CSP `frame-ancestors 'none'`。

---

## 十七、安全 Code Review Checklist

- [ ] 所有 SQL 参数化
- [ ] 用户输入进 HTML 已转义
- [ ] 文件路径无 `..`
- [ ] 对外 HTTP 客户端 URL 白名单
- [ ] 日志无 token/密码
- [ ] 异常信息不返 stack 给前端
- [ ] 管理接口鉴权
- [ ] 依赖无 Critical CVE

---

## 十八、OWASP API Security Top 10（简）

1. 对象级授权失效（BOLA）
2. 用户认证失效
3. 属性级授权失效
4. 无限制资源消耗
5. 功能级授权失效
6. 未限制敏感业务流
7. SSRF
8. 安全配置错误
9. 库存管理不当
10. 不安全 API 消费

---

## 十九、实战：MyBatis ${} 误用案例

```xml
<!-- 审计发现：orderBy 来自前端 -->
<select id="list">
  SELECT * FROM orders ORDER BY ${orderBy}
</select>
```

**修复**：白名单枚举 `create_time`/`id`；或 Java 层 switch 映射。

---

## 二十一、CORS 与 CSRF 组合

SPA 用 JWT in Header → 无 Cookie → CSRF 风险低。若 **Cookie 存 JWT** → 必须 CSRF Token 或 SameSite=Strict。

**CORS 不能替代 CSRF 防护**：CORS 只阻止浏览器读跨域响应，Post 简单请求仍可发出。

---

## 二十二、模板注入 SSTI（了解）

Thymeleaf 表达式 `${...}` 若用户控制 → RCE 风险。勿将用户输入拼进模板表达式。

**Freemarker**：`<#assign ex="freemarker.template.utility.Execute"?new()>${ ex("id") }` 类攻击。

---

## 二十三、路径穿越深度

```
GET /download?file=../../../etc/passwd
GET /download?file=....//....//etc/passwd  （编码绕过）
```

**防护**：`Path.normalize()` + 校验结果仍在 baseDir 内；UUID 文件名。

```java
Path base = Paths.get("/data/uploads").normalize();
Path resolved = base.resolve(name).normalize();
if (!resolved.startsWith(base)) throw new SecurityException();
```

---

## 二十四、业务逻辑漏洞

| 漏洞 | 例子 |
|------|------|
| 价格篡改 | 前端改 price 字段 |
| 库存超卖 | 无分布式锁 |
| 优惠券叠加 | 未校验规则 |
| 验证码重用 | 未一次性 |

**防护**：服务端 **以 DB 价格为准**；Redis 预减库存；幂等券核销。

---

## 二十五、WAF 与 RASP

**WAF**：边缘规则拦 SQLi/XSS 特征。**RASP**：运行时探针（如 OpenRASP）hook JDBC/反射。

纵深防御，不能替代安全编码。

---

## 二十六、安全单元测试

```java
@Test
void orderApi_rejectsOtherUserOrder() {
    mockAuth(userA);
    assertThatThrownBy(() -> orderService.get(orderOfUserB))
        .isInstanceOf(AccessDeniedException.class);
}
```

越权、注入应用测试覆盖。

---

## 二十七、小结

```
输入：校验、参数化、白名单
输出：上下文编码、CSP
会话：HttpOnly、SameSite、CSRF Token
访问：RBAC、归属校验
上传：白名单、随机名、OSS
```

下一章：[02-认证授权OAuthJWT.md](./02-认证授权OAuthJWT.md)

← [README](./README.md) · [00-速查总览](./00-速查总览.md)
