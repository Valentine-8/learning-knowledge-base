# 计算机网络

> **目标**：理解 TCP/HTTP/HTTPS 原理，能描述「从 URL 到页面」，配置超时与连接池，用工具排查网络问题。
>
> **速查**：[00-速查总览.md](./00-速查总览.md) · **关联**：[操作系统/epoll](../03-操作系统/03-IO模型与epoll.md)

---

## 章节索引

| 章 | 文件 | 核心内容 | 建议用时 |
|----|------|----------|----------|
| 00 | [00-速查总览.md](./00-速查总览.md) | 分层、TCP 握手挥手、HTTP 版本 | 15 min |
| 01 | [01-TCP与UDP.md](./01-TCP与UDP.md) | 可靠传输、滑动窗口、拥塞控制、UDP 场景 | 90 min |
| 02 | [02-HTTP与HTTPS.md](./02-HTTP与HTTPS.md) | HTTP 语义、缓存、TLS 握手、HTTP/2/3 | 90 min |
| 03 | [03-从URL到页面.md](./03-从URL到页面.md) | DNS、连接建立、渲染、性能优化 | 60 min |
| 04 | [04-网络排查与面试题库.md](./04-网络排查与面试题库.md) | curl/tcpdump、超时配置、经典面试题 | 60 min |

---

## 学习顺序

```
01 TCP/UDP（传输层基础）
    ↓
02 HTTP/HTTPS（应用层 + 安全）
    ↓
03 全链路（经典综合题）
    ↓
04 排查 + 面试题（实战）
```

配合 OS 章 **IO 多路复用** 理解 Netty、Tomcat 高并发模型。

---

## Java 工程对照

| 场景 | 实践 |
|------|------|
| HTTP 客户端 | OkHttp / Apache HttpClient 连接池、`connectTimeout`/`readTimeout` |
| 服务端 | Tomcat `maxConnections`、`acceptCount`、Keep-Alive |
| RPC | Dubbo/gRPC 基于 TCP，注意超时与重试幂等 |
| HTTPS | `keytool`、Spring Boot `server.ssl.*`、证书链校验 |
| DNS | K8s Service、Feign 负载均衡前的服务发现 |

---

## 面试自检清单

- [ ] 白板画三次握手、四次挥手，说明 TIME_WAIT
- [ ] 解释滑动窗口 vs 拥塞窗口
- [ ] GET/POST 语义、幂等、缓存行为
- [ ] HTTPS 完整握手流程（TLS 1.2/1.3 差异）
- [ ] 从 URL 输入到页面展示完整链路
- [ ] HTTP/1.1 vs HTTP/2 队头阻塞与多路复用

← [计算机基础](../README.md)
