# 03 · 网络、存储与 Compose

> **目标读者**：用 Compose 编排 Nginx + Spring Boot + MySQL + Redis，理解 bridge 网络与 volume。
> **预计阅读**：60 min · **难度**：★★★★

---

## 1. Docker 网络模式

| 模式 | 命令 | 场景 |
|------|------|------|
| bridge | 默认 | 单机多容器，自定义网络 DNS |
| host | `--network host` | 要极致性能或绑宿主机端口 |
| none | `--network none` | 完全隔离 |
| container | `--network container:xxx` | 共享另一容器网络栈 |

### 1.1 自定义 bridge 网络

```bash
docker network create app-net
docker run -d --name mysql --network app-net mysql:8
docker run -d --name app --network app-net myapp
# app 内 ping mysql 通，Docker 内嵌 DNS
```

**服务发现**：同一 network 内容器名 = hostname。

---

## 2. 端口映射

```bash
docker run -p 8080:8080 myapp      # 宿主机 8080 → 容器 8080
docker run -p 127.0.0.1:8080:8080 myapp   # 仅本机访问
```

```
外部请求 → 宿主机:8080 → iptables DNAT → 容器 IP:8080
```

**注意**：容器内应用 listen `0.0.0.0:8080`，不能只 bind `127.0.0.1`。

---

## 3. 数据持久化

### 3.1 Volume（推荐生产）

```bash
docker volume create mysql_data
docker run -v mysql_data:/var/lib/mysql mysql:8
```

- Docker 管理路径，易备份迁移。
- `docker volume inspect mysql_data`

### 3.2 Bind Mount（开发）

```bash
docker run -v /host/logs:/app/logs myapp
```

- 直接映射宿主机目录，改文件即时生效。

### 3.3 tmpfs（内存）

```bash
docker run --tmpfs /tmp:rw,size=100m myapp
```

---

## 4. docker-compose 全栈示例

`docker-compose.yml`：

```yaml
name: order-stack

services:
  nginx:
    image: nginx:1.25-alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx/default.conf:/etc/nginx/conf.d/default.conf:ro
    depends_on:
      app:
        condition: service_healthy
    networks:
      - front

  app:
    build:
      context: .
      dockerfile: Dockerfile
    environment:
      SPRING_PROFILES_ACTIVE: docker
      SPRING_DATASOURCE_URL: jdbc:mysql://mysql:3306/order?useSSL=false
      SPRING_DATA_REDIS_HOST: redis
    expose:
      - "8080"
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://localhost:8080/actuator/health"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 60s
    depends_on:
      mysql:
        condition: service_healthy
      redis:
        condition: service_started
    networks:
      - front
      - back

  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD:-changeme}
      MYSQL_DATABASE: order
    volumes:
      - mysql_data:/var/lib/mysql
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - back

  redis:
    image: redis:7-alpine
    networks:
      - back

volumes:
  mysql_data:

networks:
  front:
  back:
```

`nginx/default.conf`：

```nginx
upstream app {
    server app:8080;
}
server {
    listen 80;
    location / {
        proxy_pass http://app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
docker compose up -d --build
docker compose ps
docker compose logs -f app
docker compose down        # 保留 volume
docker compose down -v     # 删 volume
```

---

## 5. Spring Boot 的 docker profile

`application-docker.yml`：

```yaml
spring:
  datasource:
    url: jdbc:mysql://mysql:3306/order
    username: root
    password: ${MYSQL_ROOT_PASSWORD}
  data:
    redis:
      host: redis
      port: 6379
```

---

## 6. 环境变量与 secrets

```yaml
services:
  app:
    env_file: .env
    environment:
      JAVA_OPTS: "-Xms256m -Xmx512m"
```

**.env 不要提交 Git**（加入 `.gitignore`）。

Compose secrets（Swarm 模式更完整；纯 Compose 可用文件 mount）：

```yaml
services:
  app:
    volumes:
      - ./secrets/db_password.txt:/run/secrets/db_password:ro
```

---

## 7. 资源限制

```yaml
services:
  app:
    deploy:
      resources:
        limits:
          cpus: "1.0"
          memory: 768M
        reservations:
          memory: 512M
```

单机 `docker compose` 也支持：

```yaml
mem_limit: 768m
cpus: 1.0
```

与 JVM `-Xmx` 对齐见第 04 章。

---

## 8. 调试技巧

```bash
# 进容器
docker compose exec app sh

# 看网络
docker network inspect order-stack_back

# 从 nginx 容器 curl 后端
docker compose exec nginx wget -qO- http://app:8080/actuator/health

# 复制文件
docker cp app:/app/logs/app.log ./
```

---

## 9. 常见问题

| 问题 | 原因 |
|------|------|
| Connection refused mysql | app 先于 mysql 启动 | `depends_on` + healthcheck |
| 127.0.0.1 连不通 | 容器内 127.0.0.1 是自身 | 用服务名 `mysql` |
| 数据丢失 | `down -v` 删 volume | 备份 volume |
| 改代码不生效 | 用的是旧镜像 | `compose up --build` |

---

## 10. 与 K8s 过渡

| Compose | K8s |
|---------|-----|
| service | Deployment + Service |
| volume | PersistentVolumeClaim |
| network | Cluster DNS |
| depends_on | init container / probe |
| compose up | kubectl apply |

学完本章 → [Kubernetes/README.md](../Kubernetes/README.md)

---

→ 下一章：[04-Java 应用容器化](./04-Java应用容器化.md)

← [02-Dockerfile 与镜像优化](./02-Dockerfile与镜像优化.md)
