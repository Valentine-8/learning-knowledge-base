# 05 · 与 Java 后端联调

> **目标读者**：Spring Boot / Tomcat 部署在 Nginx 后，能配 WebSocket、文件上传、Actuator、多实例与 Docker 网络。
> **预计阅读**：50 min · **难度**：★★★★

---

## 1. 典型部署架构

```
                    ┌──────────────┐
  Browser ─────────►│ Nginx :80/443 │
                    └──────┬───────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
         Boot:8080    Boot:8081    Boot:8082
              │            │            │
              └────────────┴────────────┘
                           │
                    MySQL / Redis
```

---

## 2. Spring Boot 反向代理完整示例

### 2.1 Nginx

```nginx
upstream spring_apps {
    least_conn;
    server 127.0.0.1:8080 max_fails=3 fail_timeout=30s;
    server 127.0.0.1:8081 max_fails=3 fail_timeout=30s;
    keepalive 64;
}

server {
    listen 443 ssl http2;
    server_name api.example.com;

    ssl_certificate     /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;

    client_max_body_size 50m;

    location / {
        proxy_pass http://spring_apps;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Connection "";

        proxy_connect_timeout 5s;
        proxy_read_timeout 120s;
    }

    location /actuator/health {
        proxy_pass http://spring_apps/actuator/health;
        access_log off;
        allow 10.0.0.0/8;
        deny all;
    }
}
```

### 2.2 application.yml

```yaml
server:
  port: 8080
  forward-headers-strategy: framework
  shutdown: graceful

spring:
  lifecycle:
    timeout-per-shutdown-phase: 30s

management:
  endpoints:
    web:
      exposure:
        include: health,info,prometheus
  endpoint:
    health:
      probes:
        enabled: true   # K8s liveness/readiness 用
```

---

## 3. context-path 与路径剥离

**场景 A**：Spring `server.servlet.context-path=/app`

```nginx
location /app/ {
    proxy_pass http://127.0.0.1:8080/app/;   # 保留 /app
}
```

**场景 B**：对外 `/api`，对内 Boot 根路径 `/`

```nginx
location /api/ {
    proxy_pass http://127.0.0.1:8080/;       # 剥离 /api
}
```

**场景 C**：Spring Cloud Gateway 已在 8080，Nginx 只做 SSL + 静态

```nginx
location / {
    proxy_pass http://gateway:8080;
}
```

---

## 4. WebSocket / STOMP

Nginx 需 HTTP/1.1 升级头：

```nginx
location /ws/ {
    proxy_pass http://spring_apps;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
    proxy_read_timeout 3600s;    # 长连接超时加大
}
```

Spring WebSocket 路径示例：`/ws/endpoint`。

**SockJS**：部分请求为普通 HTTP，同一 location 即可。

**常见 502**：缺 `Upgrade` / `Connection`；或 `proxy_read_timeout` 太短。

---

## 5. SSE（Server-Sent Events）

```nginx
location /api/sse/ {
    proxy_pass http://spring_apps;
    proxy_http_version 1.1;
    proxy_set_header Connection '';
    proxy_buffering off;          # 必须关，否则事件被缓冲
    proxy_cache off;
    chunked_transfer_encoding off;
}
```

Spring：`SseEmitter` 或 WebFlux `Flux`。

---

## 6. Tomcat 前置 Nginx（传统 WAR）

```nginx
location / {
    proxy_pass http://127.0.0.1:8080;
    proxy_set_header Host $host;
}
```

Tomcat `RemoteIpValve`（server.xml 或 Spring Boot 内嵌 Tomcat 自动处理 Forwarded）。

**AJP**：`proxy_pass ajp://127.0.0.1:8009` 曾用于 mod_jk，现 **HTTP 反向代理更常见**。

---

## 7. Docker Compose 中的服务名

```yaml
# docker-compose.yml
services:
  nginx:
    image: nginx:1.25
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
    depends_on:
      - app

  app:
    image: my-spring-app:latest
    expose:
      - "8080"
```

```nginx
upstream backend {
    server app:8080;    # Docker DNS 服务名，不是 127.0.0.1
}
```

**坑**：Nginx 容器内 `127.0.0.1:8080` 指向 **Nginx 自身**，不是 app 容器。

---

## 8. 健康检查与优雅下线

**滚动发布**：

1. 从 upstream 摘掉实例（或 K8s readiness fail）
2. 等待进行中的请求完成（Spring graceful shutdown）
3. 停进程

Nginx 开源版手动维护：

```nginx
server 10.0.0.1:8080 down;   # 改配置 reload
```

**配合 Actuator**：

```bash
curl http://app:8080/actuator/health
# {"status":"UP"}
```

---

## 9. CORS：Nginx vs Spring

**推荐**：业务 CORS 在 Spring `@CrossOrigin` 或 `WebMvcConfigurer`。

Nginx 仅在前端静态与 API 不同域且不想改 Java 时：

```nginx
add_header Access-Control-Allow-Origin $http_origin always;
add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
add_header Access-Control-Allow-Credentials true always;

if ($request_method = OPTIONS) {
    return 204;
}
```

注意 `$http_origin` 需白名单校验，避免 `*` + credentials 冲突。

---

## 10. 日志与 traceId

Java MDC 设 `traceId`，Nginx access_log 可打 `$http_x_trace_id`：

```nginx
log_format trace '$remote_addr [$time_local] "$request" $status '
                 'trace=$http_x_trace_id rt=$request_time urt=$upstream_response_time';
```

Gateway 或 Filter 生成 traceId 并向下游传递。

---

## 11. 面试综合题

**问**：用户访问 `https://api.com/order/1` 全链路？

1. DNS → 云 SLB → Nginx TLS 握手
2. Nginx location 匹配，`proxy_pass` 到某台 Boot
3. Boot DispatcherServlet → Controller → Service → MySQL
4. 响应经 Nginx 回客户端；access_log 记 `$request_time`

**问**：WebSocket 为何不能只用普通 proxy_pass？

需协议升级（HTTP → WebSocket），必须 `Upgrade` 和 `Connection: upgrade`。

---

→ 下一章：[06-生产案例与面试题库](./06-生产案例与面试题库.md)

← [04-性能优化与限流](./04-性能优化与限流.md)
