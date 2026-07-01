# Nginx 深度学习（反向代理 · 负载均衡 · 生产级）

> **适用**：7 年 Java 后端面试 + 线上网关配置 + 与 Spring Boot/Tomcat 联调。
> **读法**：按章顺序学（约 8～10h）；复习时先看 [00-速查总览](./00-速查总览.md)。

---

## 章节目录

| 章 | 文档 | 核心内容 | 预计 |
|:--:|------|----------|:----:|
| 00 | [速查总览](./00-速查总览.md) | 架构一图 + 常用指令 + 面试 5 分钟版 | 10 min |
| 01 | [架构与核心概念](./01-架构与核心概念.md) | Master/Worker、事件模型、配置层级、模块 | 50 min |
| 02 | [反向代理与负载均衡](./02-反向代理与负载均衡.md) | proxy_pass、upstream、算法、健康检查 | 60 min |
| 03 | [HTTPS 与 SSL 证书](./03-HTTPS与SSL证书.md) | TLS 握手、证书链、Let's Encrypt、HSTS | 50 min |
| 04 | [性能优化与限流](./04-性能优化与限流.md) | gzip、缓存、limit_req/limit_conn、调优 | 50 min |
| 05 | [与 Java 后端联调](./05-与Java后端联调.md) | Spring Boot、WebSocket、静态资源、Tomcat | 50 min |
| 06 | [生产案例与面试题库](./06-生产案例与面试题库.md) | 故障案例、50+ 面试题 | 60 min |

---

## 配套

- DevOps 速览：[phase8-DevOps](../../Java/笔记/phase8-DevOps/复习手册.md)
- 计网 TLS 基础：[计算机网络/](../../计算机基础/计算机网络/README.md)
- 下一章：[Docker/README.md](../Docker/README.md)

← [运维与部署](../README.md)
