# gRPC 深度学习（Protobuf · 微服务 RPC · 生产级）

> **适用**：7 年 Java 后端 — 理解 gRPC 是什么、与 REST 对比、Spring/gRPC 实战、面试。
> **读法**：约 8～10h；先看 [00-速查总览](./00-速查总览.md) 回答「gRPC 是什么」。

---

## gRPC 是什么？（30 秒版）

**gRPC** = Google 开源的 **高性能 RPC 框架** + 默认用 **Protocol Buffers（Protobuf）** 做接口定义与序列化，基于 **HTTP/2** 传输。

```
传统 REST：  JSON over HTTP/1.1，人可读，宽接口
gRPC：       Protobuf over HTTP/2，二进制、契约先行、强类型、支持流式
```

**典型场景**：微服务内部调用、低延迟、多语言（Java 调 Go/Python）、双向流（聊天、推送）。

**不适合**：浏览器直接调（需 grpc-web）、公开 API 给第三方（REST/OpenAPI 更友好）。

---

## 章节目录

| 章 | 文档 | 核心内容 | 预计 |
|:--:|------|----------|:----:|
| 00 | [速查总览](./00-速查总览.md) | 一图 + 与 REST/Feign 对比 | 10 min |
| 01 | [核心概念与架构](./01-核心概念与架构.md) | RPC、HTTP/2、stub、channel | 50 min |
| 02 | [Protobuf 语法与演进](./02-Protobuf语法与演进.md) | message、service、版本兼容 | 60 min |
| 03 | [四种通信模式](./03-四种通信模式.md) | Unary、流式、背压 | 50 min |
| 04 | [Java 与 Spring gRPC 实战](./04-Java与Spring-gRPC实战.md) | 代码生成、Server/Client、拦截器 | 60 min |
| 05 | [治理超时重试与网关](./05-治理超时重试与网关.md) | 负载均衡、TLS、mTLS、grpc-gateway | 50 min |
| 06 | [生产案例与面试题库](./06-生产案例与面试题库.md) | 案例、45+ 面试题 | 50 min |

---

## 配套

- Spring Cloud HTTP：[SpringCloud/Gateway与Feign](../../01-Java/05-SpringCloud/README.md)
- 计网 HTTP/2：[计算机网络](../../04-计算机基础/02-计算机网络/README.md)

← [数据与中间件](../README.md)
