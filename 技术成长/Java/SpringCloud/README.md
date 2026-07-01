# Spring Cloud 深度学习（Nacos · Gateway · Sentinel · 生产级）

> **适用**：7 年 Java 后端 — 微服务注册发现、配置中心、网关、Feign、熔断限流。
> **读法**：约 10～12h；Spring 基础见 [phase4-Spring](../笔记/phase4-Spring/复习手册.md)。

---

## 章节目录

| 章 | 文档 | 核心内容 | 预计 |
|:--:|------|----------|:----:|
| 00 | [速查总览](./00-速查总览.md) | 组件一图 + Alibaba 栈 | 10 min |
| 01 | [微服务组件全景](./01-微服务组件全景.md) | 拆分、CAP、选型、版本对应 | 50 min |
| 02 | [Nacos 注册发现](./02-Nacos注册发现.md) | 服务注册、健康检查、AP/CP | 60 min |
| 03 | [Nacos 配置中心](./03-Nacos配置中心.md) | 动态配置、刷新、多环境 | 50 min |
| 04 | [Spring Cloud Gateway](./04-SpringCloudGateway.md) | 路由、过滤器、鉴权限流 | 60 min |
| 05 | [OpenFeign 与负载均衡](./05-OpenFeign与负载均衡.md) | 声明式调用、LoadBalancer | 50 min |
| 06 | [Sentinel 与 Seata](./06-Sentinel与Seata.md) | 流控熔断、分布式事务 AT | 60 min |
| 07 | [生产案例与面试题库](./07-生产案例与面试题库.md) | 案例、55+ 面试题 | 60 min |

---

## 技术栈（本专题默认）

| 组件 | 版本参考 | 说明 |
|------|----------|------|
| Spring Boot | 3.x | Jakarta EE |
| Spring Cloud | 2023.x | 版本火车 |
| Spring Cloud Alibaba | 2023.x | Nacos、Sentinel、Seata |

---

## 配套

- Spring Core：[phase4-Spring](../笔记/phase4-Spring/复习手册.md)
- gRPC 内部 RPC：[gRPC](../../数据与中间件/gRPC/README.md)
- 分布式：[phase6-分布式](../笔记/phase6-分布式/复习手册.md)

← [Java 总览](../README.md)
