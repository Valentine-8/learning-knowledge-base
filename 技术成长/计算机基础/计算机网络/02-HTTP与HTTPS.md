# 第二章：HTTP 与 HTTPS

> **阅读目标**：掌握 HTTP 语义、缓存、版本演进、TLS 握手与证书体系，能配置 Spring Boot HTTPS 与排查证书问题。
>
> **建议用时**：通读 85 min。

---

## 一、HTTP 基础

### 1.1 请求-响应模型

```
请求行：METHOD URI HTTP/1.1
请求头：Host, User-Agent, Content-Type, Cookie, Authorization...
空行
请求体（可选）

状态行：HTTP/1.1 200 OK
响应头：Content-Type, Set-Cookie, Cache-Control...
空行
响应体
```

### 1.2 常用方法

| 方法 | 语义 | 幂等 | 安全 | 典型 body |
|------|------|------|------|-----------|
| GET | 获取资源 | 是 | 是 | 无 |
| POST | 提交/创建 | 否 | 否 | 有 |
| PUT | 全量替换 | 是 | 否 | 有 |
| PATCH | 部分更新 | 否 | 否 | 有 |
| DELETE | 删除 | 是 | 否 | 可选 |
| HEAD | 同 GET 无体 | 是 | 是 | 无 |
| OPTIONS | 预检 CORS | 是 | 是 | 无 |

**幂等**：多次相同请求效果同一次（网络重试安全）。

**安全**：不改变服务器状态（理论；实际 GET 也可能有副作用如日志）。

---

## 二、状态码

| 码 | 含义 | 场景 |
|----|------|------|
| 200 | OK | 成功 |
| 201 | Created | POST 创建 |
| 204 | No Content | 删除成功无体 |
| 301 | 永久重定向 | SEO 换域名 |
| 302/307 | 临时重定向 | 登录跳转 |
| 304 | Not Modified | 协商缓存命中 |
| 400 | Bad Request | 参数错误 |
| 401 | Unauthorized | 未认证 |
| 403 | Forbidden | 无权限 |
| 404 | Not Found | 资源不存在 |
| 409 | Conflict | 冲突 |
| 429 | Too Many Requests | 限流 |
| 500 | Internal Error | 服务端异常 |
| 502 | Bad Gateway | 网关上游挂 |
| 503 | Service Unavailable | 过载/维护 |
| 504 | Gateway Timeout | 网关读超时 |

**401 vs 403**：401 需要登录/凭证；403 已识别身份但禁止访问。

---

## 三、重要 Header

### 3.1 请求

| Header | 作用 |
|--------|------|
| Host | 虚拟主机、SNI 前路由 |
| Authorization | Bearer JWT、Basic |
| Cookie | 会话 |
| Content-Type | application/json 等 |
| Accept | 可接受类型 |
| If-None-Match | ETag 协商缓存 |
| If-Modified-Since | 时间协商 |
| Origin | CORS 来源 |

### 3.2 响应

| Header | 作用 |
|--------|------|
| Set-Cookie | HttpOnly、Secure、SameSite |
| Cache-Control | max-age、no-cache |
| ETag / Last-Modified | 缓存验证 |
| Location | 重定向 URL |
| Access-Control-* | CORS |

---

## 四、HTTP 缓存

### 4.1 强缓存

`Cache-Control: max-age=3600` 或 `Expires`（HTTP/1.0）。

浏览器直接用本地副本，**不发请求**（除非 hard refresh）。

### 4.2 协商缓存

发请求带 `If-None-Match: "etag"` 或 `If-Modified-Since`；未变则 **304**，无 body。

| 优先级 | 机制 |
|--------|------|
| ETag | 内容哈希，精确 |
| Last-Modified | 秒级，可能不准 |

### 4.3 实践

- 静态资源：长 max-age + 文件名 hash
- API JSON：通常 `Cache-Control: no-store`
- CDN：边缘缓存遵循源站头

---

## 五、Cookie 与 Session

| | Cookie | Session |
|--|--------|---------|
| 存储 | 客户端 | 服务端 |
| 携带 | 自动 Cookie 头 | SessionId in Cookie |
| 扩展 | 跨域受限 | 需粘性会话/Redis |

**安全属性**：`HttpOnly` 防 XSS 读；`Secure` 仅 HTTPS；`SameSite=Lax/Strict` 减 CSRF。

---

## 六、HTTP 版本演进

### 6.1 HTTP/1.0 vs 1.1

- 1.0：每请求新 TCP
- **1.1**：**持久连接** `Connection: keep-alive`、管道化（少用）、分块传输 `Transfer-Encoding: chunked`

**队头阻塞（HOL）**：同一连接上响应顺序固定，前一响应慢阻塞后续。

### 6.2 HTTP/2

- **二进制分帧**：HEADERS/DATA 帧
- **多路复用**：单 TCP 上多 stream 并行
- **HPACK** 头部压缩
- **服务端推送**（Push，现较少用）

**仍有的 HOL**：TCP 层丢包阻塞所有 stream。

### 6.3 HTTP/3

基于 **QUIC（UDP）**：

- 连接迁移（换 IP 不断连）
- 0-RTT 握手（有重放风险需业务防护）
- stream 级独立，无 TCP 层 HOL

---

## 七、HTTPS 与 TLS

### 7.1 为何需要

HTTP 明文 → 窃听、篡改、冒充。**HTTPS = HTTP + TLS**。

### 7.2 密码学组合

| 类型 | 用途 |
|------|------|
| 对称 AES-GCM |  bulk 数据加密，快 |
| 非对称 RSA/ECDHE | 握手密钥交换、证书 |
| 哈希 SHA | 完整性 |
| 数字签名 | 证书链验证 |

### 7.3 TLS 1.2 握手（简化）

```
1. ClientHello：支持的套件、随机数
2. ServerHello：选定套件、随机数、证书
3. 客户端验证证书链 → 信任 CA
4. 密钥交换（ECDHE）→ 预主密钥
5. 双方派生会话密钥
6. Finished 加密握手完成
7. 应用数据对称加密传输
```

### 7.4 TLS 1.3 改进

- 更少往返（1-RTT，0-RTT 可选）
- 移除弱套件
- 加密更多握手消息

### 7.5 证书与 PKI

```
站点证书 ← 中间 CA ← 根 CA（预装在系统/浏览器）
```

**验证**：链完整、未过期、域名匹配（CN/SAN）、未吊销（OCSP/CRL）。

**中间人攻击**：无证书或自签不被信任 → 浏览器警告。

### 7.6 HSTS

`Strict-Transport-Security: max-age=31536000` 强制浏览器 HTTPS，防 sslstrip。

---

## 八、CORS 跨域

浏览器 **同源策略**：协议+域名+端口相同。

**简单请求**：GET/HEAD/POST + 安全头 → 直接发，响应需 `Access-Control-Allow-Origin`。

**预检**：PUT/DELETE/自定义头 → 先发 OPTIONS，`Allow-Methods/Headers/Origin`。

**凭证**：`withCredentials` 需 `Allow-Credentials: true` 且 Origin 不能 `*`。

**Spring**：

```java
@Configuration
public class CorsConfig implements WebMvcConfigurer {
    @Override
    public void addCorsMappings(CorsRegistry registry) {
        registry.addMapping("/api/**")
            .allowedOrigins("https://app.example.com")
            .allowedMethods("GET", "POST")
            .allowCredentials(true);
    }
}
```

---

## 九、Java / Spring 实践

### 9.1 RestTemplate / WebClient 超时

```yaml
spring:
  cloud:
    openfeign:
      client:
        config:
          default:
            connectTimeout: 3000
            readTimeout: 10000
```

### 9.2 HTTPS 配置

```yaml
server:
  port: 8443
  ssl:
    enabled: true
    key-store: classpath:keystore.p12
    key-store-password: ${SSL_PASSWORD}
    key-store-type: PKCS12
```

### 9.3 反向代理终止 TLS

Nginx/Ingress 解密 → 内网 HTTP → 注意 `X-Forwarded-Proto` 判断 scheme。

---

## 十、REST 设计要点

- 资源名词 URI：`/users/123/orders`
- 状态码表达结果
- 版本：`/v1/` 或 Header
- 分页：`page/size` 或 `cursor`
- 幂等：PUT/DELETE + **Idempotency-Key**（POST 支付）

---

## 十一、面试高频问答

| 问 | 答 |
|----|-----|
| GET 和 POST？ | 语义幂等安全不同；POST body 无长度理论限制；缓存行为不同 |
| 301 和 302？ | 301 永久，SEO 权重转移；302 临时 |
| HTTPS 过程？ | 证书验证 + 握手协商对称密钥 + 加密传输 |
| HTTP/2 改进？ | 多路复用、HPACK、二进制帧 |
| 强缓存和协商？ | max-age 直接用；ETag/Last-Modified 问服务器 304 |
| 对称和非对称？ | 对称快传数据；非对称握手换密钥 |

---

## 十三、HTTP 条件请求完整流程

```
首次：GET /a.js → 200 + ETag: "abc" + Cache-Control: max-age=0, must-revalidate
再次：GET /a.js + If-None-Match: "abc" → 304 无 body
强制刷新：Cache-Control: no-cache 仍发验证请求
Ctrl+F5：Cache-Control: no-cache + Pragma（绕过缓存）
```

---

## 十四、RESTful 与 GraphQL 对比

| | REST | GraphQL |
|--|------|---------|
| 资源 | URL 名词 | 单端点查询 |
| 过度获取 | 可能 | 客户端指定字段 |
| 缓存 | HTTP 缓存成熟 | 复杂 |
| Java | Spring MVC/WebFlux | Netflix DGS |

7 年工程师 **REST 为主**，GraphQL 了解适用 BFF 聚合场景。

---

## 十五、WebSocket 与 SSE

| | WebSocket | SSE |
|--|-----------|-----|
| 方向 | 双向 | 服务端推 |
| 协议 | 升级 HTTP | text/event-stream |
| Java | Spring WebSocket/STOMP | SseEmitter |

**场景**：IM、行情推送；SSE 简单单向通知。

---

## 十六、TLS 证书链验证步骤

1. 证书未过期（系统时间正确）
2. 域名匹配 SAN/CN
3. 签名链到信任根
4. 未吊销（OCSP Stapling）
5. 密钥强度合规

**Java truststore**：导入企业根 CA 才能访问内网 HTTPS。

---

## 十七、HSTS 与混合内容

**Mixed Content**：HTTPS 页加载 HTTP 资源 → 浏览器可能 block。

**升级**：全站 HTTPS + HSTS + 资源 URL 相对协议或 //。

---

## 十八、Spring Boot HTTP/2

```yaml
server:
  http2:
    enabled: true
  ssl:
    enabled: true  # HTTP/2 常需 TLS（h2c 少见）
```

Tomcat 9+ 支持 ALPN 协商 h2。

---

## 十九、常见 Header 安全组合

```http
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: geolocation=()
```

---

## 二十一、Trailer 与 grpc-web

HTTP/1.1 **Trailer**：body 后传 Header（如 grpc-status）。

**gRPC**：HTTP/2 + Protobuf；status 在 trailer；Java `ManagedChannel` + deadline。

---

## 二十二、Content Negotiation

```
Accept: application/json, application/xml;q=0.9
Accept-Language: zh-CN, en;q=0.8
Accept-Encoding: gzip, br
```

Spring `produces = MediaType.APPLICATION_JSON_VALUE` 匹配 Accept。

---

## 二十三、Range 请求与断点续传

```
GET /file.zip
Range: bytes=0-1023
→ 206 Partial Content
Content-Range: bytes 0-1023/5000
```

**实现**：RandomAccessFile + 流式输出；OSS 分片上传。

---

## 二十四、ETag 生成策略

| 策略 | 说明 |
|------|------|
| 内容 hash | MD5/SHA 精确 |
| inode+mtime | 快但不精确跨服务器 |
| 版本号 | ?v=20240101 最简单 |

**强 ETag** vs **弱 ETag**（W/"..."）：弱允许语义等价。

---

## 二十五、Spring Cache 与 HTTP 缓存

```java
@Cacheable(value = "users", key = "#id")
public User getUser(Long id) { ... }
```

**本地 Caffeine** vs **Redis** vs **HTTP CDN**：层次不同；API 用应用缓存，静态用 CDN。

---

## 二十六、HTTP 走私（了解）

CL.TE / TE.CL 歧义导致请求走私 → 使用标准解析、禁用 ambiguous 代理、升级 Nginx。

---

## 二十七、小结

```
HTTP：方法语义、状态码、Header、缓存
版本：1.1 持久连接 → 2 多路复用 → 3 QUIC
HTTPS：TLS 证书 + 密钥交换 + AES
工程：超时、CORS、Spring SSL、网关 TLS 终止
```

下一章：[03-从URL到页面.md](./03-从URL到页面.md)

← [01-TCP与UDP](./01-TCP与UDP.md) · [README](./README.md)
