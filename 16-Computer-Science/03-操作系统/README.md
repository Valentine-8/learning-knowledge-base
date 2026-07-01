# 操作系统

> **目标**：掌握进程/线程/调度、虚拟内存、IO 模型（尤其 epoll），理解死锁与 Java 并发、JVM 的底层关联。
>
> **速查**：[00-速查总览.md](./00-速查总览.md) · **关联**：[计算机网络/epoll 对照](../计算机网络/04-网络排查与面试题库.md)

---

## 章节索引

| 章 | 文件 | 核心内容 | 建议用时 |
|----|------|----------|----------|
| 00 | [00-速查总览.md](./00-速查总览.md) | 进程线程、内存、IO、死锁速答 | 15 min |
| 01 | [01-进程线程与调度.md](./01-进程线程与调度.md) | PCB、状态转换、调度算法、IPC、Java 线程模型 | 90 min |
| 02 | [02-内存管理.md](./02-内存管理.md) | 虚拟内存、分页分段、置换算法、JVM 内存布局 | 90 min |
| 03 | [03-IO模型与epoll.md](./03-IO模型与epoll.md) | 阻塞/非阻塞、select/poll/epoll、Reactor、Netty | 90 min |
| 04 | [04-死锁与面试题库.md](./04-死锁与面试题库.md) | 死锁条件与处理、银行家、Java 排查、综合面试题 | 60 min |

---

## 学习顺序

```
01 进程线程（与 Java Thread、虚拟线程对照）
    ↓
02 内存管理（与 JVM 堆/GC/Direct Memory）
    ↓
03 IO/epoll（与 NIO、Netty EventLoop）
    ↓
04 死锁 + 面试综合
```

---

## Java 工程对照

| OS 概念 | Java 映射 |
|---------|-----------|
| 进程 | JVM 实例，独立堆 |
| 线程 | `Thread`、线程池、`ForkJoinPool` |
| 虚拟线程 | JDK 21+ 轻量线程，载体线程调度 |
| 互斥 | `synchronized`、`ReentrantLock` |
| 信号量 | `Semaphore` |
| 虚拟内存 | JVM 堆 + Metaspace + 堆外内存 |
| epoll | Linux 下 Netty `EpollEventLoop` |
| 死锁 | `jstack`、Thread dump 分析 |

---

## 面试自检清单

- [ ] 进程 vs 线程 vs 协程/虚拟线程
- [ ] 用户态/内核态切换、上下文切换开销
- [ ] 虚拟内存作用、页表、TLB
- [ ] LRU 置换与 Redis/Caffeine 近似 LRU
- [ ] select/poll/epoll 区别，LT vs ET
- [ ] 死锁四条件与 `jstack` 排查

← [计算机基础](../../README.md)
