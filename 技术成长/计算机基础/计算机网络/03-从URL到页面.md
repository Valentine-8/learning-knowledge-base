# 第三章：从 URL 到页面

> **阅读目标**：完整描述浏览器输入 URL 到页面渲染的全链路，关联 DNS、TCP、TLS、HTTP、前端性能与后端 Java 服务。
>
> **建议用时**：通读 60 min；能白板画出时序图。

---

## 一、总览时序

```
用户输入 URL
    ↓
URL 解析（协议、host、port、path、query）
    ↓
DNS 解析 → IP 地址
    ↓
建立 TCP 连接（三次握手）
    ↓
HTTPS？→ TLS 握手
    ↓
发送 HTTP 请求
    ↓
服务器处理（网关、应用、DB）
    ↓
HTTP 响应
    ↓
浏览器解析渲染
    ↓
加载子资源（CSS/JS/图片）
```

---

## 二、URL 解析

### 2.1 组成部分

```
https://user:pass@www.example.com:443/path/to/page?name=value#section
  │      │         │              │   │              │           │
协议   凭证      主机            端口  路径          查询       片段
```

**片段 #**：不发送到服务器，仅前端路由/hash。

### 2.2 特殊 URL

| 输入 | 行为 |
|------|------|
| example.com | 补全 scheme（https 优先） |
| /相对路径 | 相对当前页 |
| about:blank | 空白页 |

---

## 三、DNS 解析

### 3.1 查询顺序（简化）

```
浏览器 DNS 缓存
    → 操作系统缓存 /etc/hosts
    → 本地 DNS 解析器（ISP/公司）
    → 根 → TLD(.com) → 权威 DNS
    → 返回 A/AAAA 记录
```

### 3.2 记录类型

| 类型 | 含义 |
|------|------|
| A | IPv4 |
| AAAA | IPv6 |
| CNAME | 别名 |
| MX | 邮件 |
| TXT | 验证、SPF |

### 3.3 优化

- **DNS 预解析**：`<link rel="dns-prefetch">`
- **TTL**：缓存时间；过短增加延迟，过长切换慢
- **HttpDNS**：绕过 Local DNS 防劫持（App 常见）

**Java 服务**：JVM DNS 缓存 `networkaddress.cache.ttl`；K8s 用 Service/CoreDNS。

---

## 四、建立连接

### 4.1 TCP

客户端向 **IP:port**（HTTPS 默认 443，HTTP 80）发 SYN，完成三次握手。

**Happy Eyeballs**：IPv6/IPv4 并行尝试，先成功者用。

### 4.2 TLS（HTTPS）

在 TCP 之上完成 TLS 握手（见 02 章），再发 HTTP 明文（加密传输）。

**Session 复用**：TLS session ticket / 1.3 PSK 减少握手 RTT。

---

## 五、HTTP 请求与响应

### 5.1 请求

```
GET /path?name=value HTTP/1.1
Host: www.example.com
User-Agent: ...
Accept: text/html,...
Accept-Encoding: gzip, br
Cookie: session=...
Connection: keep-alive
```

### 5.2 服务器处理链（Java 典型）

```
负载均衡（Nginx/SLB）
    ↓
API 网关（鉴权、限流）
    ↓
Spring Boot（Tomcat/Netty）
    ↓ Controller → Service → Repository
    ↓
MySQL / Redis / MQ
    ↓
JSON/HTML 响应
```

### 5.3 响应

```
HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8
Content-Encoding: gzip
Set-Cookie: ...
Cache-Control: ...

<!DOCTYPE html>...
```

---

## 六、浏览器渲染

### 6.1 关键路径

```
HTML → DOM 树
CSS  → CSSOM 树
    → 渲染树 Render Tree
    → Layout（布局）
    → Paint（绘制）
    → Composite（合成）
JS 可阻塞 HTML 解析（无 defer/async）
```

### 6.2 脚本与样式

- **CSS 阻塞渲染**：需 CSSOM 完整
- **JS 默认阻塞解析**：`defer` DOM 后执行；`async` 下载完即执行
- **关键渲染路径优化**：内联 critical CSS、延迟非关键 JS

### 6.3 子资源加载

HTML 遇 `<link>` `<script>` `<img>` 发 **并行** HTTP 请求（HTTP/2 多路复用同连接）。

**CDN**：静态资源就近边缘节点。

---

## 七、缓存再访

第二次访问同 URL：

1. 强缓存命中 → 无网络
2. 协商缓存 → 304 小响应
3. Service Worker 可拦截（PWA）

---

## 八、性能指标

| 指标 | 含义 |
|------|------|
| DNS 时间 | 解析耗时 |
| TCP/TLS | 连接建立 |
| TTFB | 首字节时间（后端+网络） |
| FCP | 首次内容绘制 |
| LCP | 最大内容绘制 |
| TTI | 可交互时间 |

**优化分工**：

- 前端：资源压缩、懒加载、HTTP/2、CDN
- 后端：接口耗时、DB 索引、缓存 Redis
- 网络：Keep-Alive、TLS 会话复用、HTTP/2

---

## 九、单页应用（SPA）

现代前端路由（Vue/React）：

1. 首次仍加载 `index.html` + JS bundle
2. 后续 **前端路由** 变 URL 但不全页刷新
3. API 调用 XHR/Fetch 取 JSON

**SEO**：SSR（Next/Nuxt）或预渲染。

**Java 后端**：提供 REST API + 静态资源分离部署。

---

## 十、移动端与 App

App 内 WebView 或原生：

- 同样 DNS/TCP/TLS/HTTP
- 可能走 **HTTP DNS**、证书 Pinning
- Deep Link 直接打开 App 非浏览器

---

## 十一、故障排查切入点

| 现象 | 查 |
|------|-----|
| 打不开 | DNS？ping/curl IP |
| 慢 | TTFB 高 → 后端；下载慢 → 带宽/体积 |
| 证书错误 | 过期、域名不匹配、链不全 |
| 间歇 502 | 上游超时、网关配置 |
| 跨域 | CORS 头、预检 OPTIONS |

**工具**：Chrome DevTools Network、curl -v、dig、traceroute。

---

## 十二、面试白板题标准答法

**问：输入 https://www.baidu.com 回车发生什么？**

分阶段答（2–3 min）：

1. URL 解析，查 DNS 得 IP
2. TCP 三次握手到 443
3. TLS 握手验证证书，协商密钥
4. 发 GET / HTTP/1.1 + Host
5. 服务器返回 302/200 + HTML
6. 解析 HTML，并行请求 CSS/JS/图片
7. 构建 DOM/CSSOM、渲染、执行 JS
8. 后续交互 AJAX 继续 HTTP 请求

**加分**：提 HTTP/2 多路复用、CDN、浏览器缓存、Service Worker。

---

## 十三、与 Java 工程师相关

| 环节 | 职责 |
|------|------|
| API 设计 | REST、分页、压缩 gzip |
| 会话 | Cookie/JWT、Redis Session |
| 静态资源 | Nginx 或 OSS+CDN，少占 Tomcat 线程 |
| 连接 | 数据库/HTTP 连接池、超时 |
| 监控 | APM 看 TTFB、链路 traceId |

---

## 十五、浏览器渲染深入

### 15.1 解析阻塞

- CSS 阻塞 DOM 构建后的渲染（CSSOM）
- JS 无 defer/async 阻塞 HTML parser
- `async` 脚本下载完立即执行，可能乱序

### 15.2 重排与重绘

| | 触发 | 成本 |
|--|------|------|
| Reflow | 几何变化 | 高 |
| Repaint | 颜色等 | 较低 |
| Composite | transform/opacity | GPU 低 |

**优化**：批量 DOM 操作、DocumentFragment、避免逐条读 offsetHeight。

---

## 十六、DNS 深入

**递归 vs 迭代**：客户端 → 本地 DNS 递归查询；本地 DNS 向根迭代。

**负缓存**：NXDOMAIN 也缓存 TTL，减少 spam 查询。

**Java 陷阱**：JVM DNS 缓存导致 K8s Service IP 变更后连旧 IP → 调 TTL 或 InetAddress 缓存策略。

---

## 十七、CDN 工作原理

```
用户 → 智能 DNS（就近 POP）
     → 边缘节点（缓存命中直接返回）
     → 回源站（miss）
```

**缓存 Key**：URL、Query、部分 Header（Vary）。

**Java 静态资源**：文件名带 contenthash，`max-age=31536000, immutable`。

---

## 十八、HTTP 缓存与 Java 网关

```java
// Spring 静态资源
registry.addResourceHandler("/static/**")
    .addResourceLocations("classpath:/static/")
    .setCacheControl(CacheControl.maxAge(365, TimeUnit.DAYS).cachePublic());
```

**API 响应**：默认 `Cache-Control: no-store` 防敏感数据缓存。

---

## 十九、全链路追踪

```
traceId 生成（网关）
  → MDC 写入日志
  → Feign Header 传递
  → DB / MQ 附带 traceId
```

与「URL 到页面」结合：浏览器 **前端 trace**（OpenTelemetry）→ 后端同一 traceId 关联。

---

## 二十、故障案例

**白屏**：JS 报错未捕获 → 看 Console；chunk 404 → 部署路径。

**首屏慢**：TTFB 高查后端；LCP 大图未 lazy；阻塞 JS 过多。

**HTTPS 混合内容**：Console 警告，改资源 URL。

---

## 二十一、Preload / Prefetch / Preconnect

```html
<link rel="preconnect" href="https://cdn.example.com">
<link rel="dns-prefetch" href="//api.example.com">
<link rel="preload" href="/font.woff2" as="font" crossorigin>
```

**Preconnect**：DNS+TCP+TLS 提前；**Preload**：高优先级拉关键资源。

---

## 二十二、Service Worker 与 PWA

SW 拦截 fetch，实现 **离线缓存**、推送。更新需 **skipWaiting + clients.claim**。

Java 后端仍提供 REST；静态资源 CDN + SW 缓存策略配合。

---

## 二十三、HTTP/3 QUIC 连接建立

```
0-RTT：已知 server config 时首包可带数据（重放风险）
1-RTT：首次完整握手
连接迁移：WiFi ↔ 4G IP 变，Connection ID 不变
```

---

## 二十四、后端渲染 SSR vs CSR

| | SSR | CSR |
|--|-----|-----|
| 首屏 | HTML 直出快 | 等 JS bundle |
| SEO | 好 | 需 prerender |
| Java | Thymeleaf、Freemarker | 前后端分离 API |

**BFF**：Backend for Frontend 聚合 API 减前端请求数。

---

## 二十五、DNS 故障切换

```java
// 客户端多 IP 重试（HttpClient 5 内置）
// 服务端：多 A 记录 + 健康检查摘除
```

**实践**：DNS TTL 60s + 多可用区 LB。

---

## 二十六、性能预算示例

| 指标 | 预算 |
|------|------|
| TTFB | < 200ms |
| FCP | < 1.8s |
| LCP | < 2.5s |
| JS bundle | < 200KB gzip |

超标则拆包、懒加载、边缘缓存。

---

## 二十七、小结

```
DNS → TCP → TLS → HTTP → 渲染 → 子资源
性能：TTFB 后端、FCP/LCP 前端、缓存、HTTP/2
排查：curl -v、DevTools、分层定位
```

下一章：[04-网络排查与面试题库.md](./04-网络排查与面试题库.md)

← [02-HTTP与HTTPS](./02-HTTP与HTTPS.md) · [README](./README.md)
