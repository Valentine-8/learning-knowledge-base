# 03 · HTTPS 与 SSL 证书

> **目标读者**：能在 Nginx 配置 HTTPS、理解 TLS 握手与证书链、处理混合内容与 HSTS，并与 Java 应用配合。
> **预计阅读**：50 min · **难度**：★★★★

---

## 1. 为什么需要 HTTPS

| 威胁 | HTTP | HTTPS |
|------|------|-------|
| 窃听 | 明文传输 | TLS 加密 |
| 篡改 | 中间人可改包 | 完整性校验 |
| 冒充 | 无身份验证 | 证书验证服务器身份 |

**Java 后端常见模式**：**SSL 终结在 Nginx**，Nginx ↔ Client 走 HTTPS，Nginx ↔ Spring Boot 走内网 HTTP（减 CPU、证书集中管理）。

```
Client ──TLS──► Nginx:443 ──HTTP──► Spring Boot:8080
```

---

## 2. TLS 握手简图（面试够用）

```
Client                          Server
   │── ClientHello（套件、随机数）──►│
   │◄── ServerHello + 证书 ────────│
   │── 验证证书链 ──────────────────│
   │── 密钥交换（ECDHE 等）────────►│
   │◄── Finished ──────────────────│
   │══ 对称加密应用数据 ════════════│
```

**关键概念**：

| 概念 | 说明 |
|------|------|
| 对称加密 | 会话数据用 AES 等，速度快 |
| 非对称加密 | 握手阶段交换密钥，证书含公钥 |
| 证书 | CA 对公钥 + 域名签名的数字证明 |
| SNI | 同一 IP 多域名，ClientHello 带 server_name |

深入见 [计算机网络/TLS](../../计算机基础/计算机网络/README.md)。

---

## 3. 证书类型与文件

| 文件 | 内容 |
|------|------|
| `fullchain.pem` | 服务器证书 + 中间 CA 链 |
| `privkey.pem` | 私钥（**绝不提交 Git**） |
| `chain.pem` | 仅中间 CA（部分场景） |

```bash
# 查看证书信息
openssl x509 -in fullchain.pem -text -noout
openssl s_client -connect api.example.com:443 -servername api.example.com
```

| 类型 | 说明 |
|------|------|
| DV | 域名验证，Let's Encrypt 免费 |
| OV / EV | 企业验证，EV 浏览器栏显示公司名（已弱化） |
| 通配符 | `*.example.com` |
| 自签名 | 开发用，浏览器不信任 |

---

## 4. Nginx HTTPS 配置

### 4.1 基础

```nginx
server {
    listen 443 ssl http2;
    server_name api.example.com;

    ssl_certificate     /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;

    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:50m;
    ssl_session_tickets off;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:...;
    ssl_prefer_server_ciphers off;

    location / {
        proxy_pass http://java_backend;
        proxy_set_header X-Forwarded-Proto https;
    }
}

server {
    listen 80;
    server_name api.example.com;
    return 301 https://$host$request_uri;
}
```

### 4.2 安全加固

```nginx
# HSTS：强制浏览器只用 HTTPS（谨慎，先确保 HTTPS 稳定）
add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;

# 防点击劫持
add_header X-Frame-Options SAMEORIGIN always;
add_header X-Content-Type-Options nosniff always;
```

### 4.3 TLS 1.3

- 握手更快（1-RTT），仅 AEAD 套件。
- Nginx 1.13+ / OpenSSL 1.1.1+ 支持。
- 生产推荐 **只开 TLSv1.2 + TLSv1.3**，关闭 SSLv3/TLS1.0/1.1。

---

## 5. Let's Encrypt + Certbot

```bash
# Ubuntu 示例
apt install certbot python3-certbot-nginx
certbot --nginx -d api.example.com -d www.example.com

# 自动续期（cron 或 systemd timer）
certbot renew --dry-run
```

Certbot 会修改 Nginx 配置或 webroot 验证：

```nginx
location /.well-known/acme-challenge/ {
    root /var/www/certbot;
}
```

**Docker 环境**：certbot 容器 + volume 共享证书目录，或云厂商托管证书。

---

## 6. 混合内容与后端感知 HTTPS

浏览器页面 HTTPS 但请求 `http://` 静态资源 → **Mixed Content** 被拦。

**Spring 生成正确链接**：

```yaml
server:
  forward-headers-strategy: framework
```

或：

```java
// 若未用 ForwardedHeaderFilter，检查 X-Forwarded-Proto
```

**Cookie Secure**：

```yaml
server.servlet.session.cookie.secure: true   # 仅 HTTPS 发 Cookie
```

---

## 7. 双向 TLS（mTLS，了解）

金融、服务间零信任场景：客户端也出示证书。

```nginx
ssl_client_certificate /etc/nginx/ca.crt;
ssl_verify_client optional;

location /internal/ {
    if ($ssl_client_verify != SUCCESS) {
        return 403;
    }
    proxy_pass http://backend;
}
```

---

## 8. 性能

| 优化 | 说明 |
|------|------|
| SSL session 缓存 | 复用握手，减 CPU |
| HTTP/2 | 多路复用，与 HTTPS 常一起开 |
| OCSP Stapling | 服务器代查证书吊销状态，加快客户端验证 |
| 硬件加速 | AES-NI 指令，现代 CPU 默认有 |

```nginx
ssl_stapling on;
ssl_stapling_verify on;
ssl_trusted_certificate /etc/nginx/ssl/chain.pem;
```

**为何 SSL 放 Nginx**：OpenSSL 在 C 层优化成熟；Java JSSE 也可但 JVM 额外开销，网关统一终结更常见。

---

## 9. 故障案例

| 现象 | 原因 | 处理 |
|------|------|------|
| `SSL: certificate verify failed` | 链不完整 | 用 fullchain 非仅 cert |
| 部分 Android 无法访问 | 缺中间 CA 或 TLS 版本过旧 | 补链、开 TLS1.2 |
| 重定向循环 | 后端 302 到 http，Nginx 再 301 到 https | 设 `X-Forwarded-Proto` |
| 证书过期 | 未续期 | 监控过期日、自动 renew |

---

## 10. 面试题

| 问 | 答 |
|----|-----|
| HTTPS 握手过程？ | ClientHello → ServerHello+证书 → 验链 → 密钥交换 → 对称加密通信 |
| 对称 vs 非对称？ | 握手非对称，数据传输对称 |
| 为何 Nginx 终结 SSL？ | 集中管理、减后端 CPU、统一策略 |
| HSTS 是什么？ | 响应头告诉浏览器只走 HTTPS，防降级攻击 |
| SNI 作用？ | 同一 IP 按域名选不同证书 |

---

→ 下一章：[04-性能优化与限流](./04-性能优化与限流.md)

← [02-反向代理与负载均衡](./02-反向代理与负载均衡.md)
