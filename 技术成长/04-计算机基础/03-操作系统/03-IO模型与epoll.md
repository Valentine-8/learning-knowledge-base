# 第三章：IO 模型与 epoll

> **阅读目标**：理解阻塞/非阻塞、同步/异步、IO 多路复用与 epoll，对照 Java NIO、Netty Reactor 模型。
>
> **建议用时**：通读 90 min；结合 Netty 源码或 Echo 示例加深。

---

## 一、IO 基础

### 1.1 两阶段

1. **数据就绪**：内核缓冲区有数据 / 能写
2. **数据拷贝**：内核 → 用户缓冲区

不同模型在这两阶段的 **阻塞行为** 不同。

### 1.2 同步 vs 异步

| | 同步 | 异步 |
|--|------|------|
| 数据拷贝 | 用户自己 read | 内核完成再通知 |
| 例子 | blocking read、select+read | AIO、IOCP |

**Linux AIO** 对文件尚可；网络 IO 常用 **epoll**，非真异步 IO。

---

## 二、五种 IO 模型（Stevens）

### 2.1 阻塞 IO（BIO）

```java
// 线程卡在 read 直到有数据
InputStream in = socket.getInputStream();
int n = in.read(buf); // block
```

**一连接一线程** → C10K 问题。

### 2.2 非阻塞 IO（NIO）

`fcntl O_NONBLOCK`：read 无数据立即返回 EAGAIN。

**需轮询** → CPU 空转，很少单独用。

### 2.3 IO 多路复用

**select/poll/epoll** 监听多 fd 就绪，再 read/write。

**一个线程管多连接**，Reactor 基础。

### 2.4 信号驱动 IO

SIGIO 通知就绪，较少用。

### 2.5 异步 IO（AIO）

内核完成拷贝后通知；Windows IOCP 成熟。

---

## 三、select 与 poll

### 3.1 select

```c
fd_set readfds;
select(maxfd+1, &readfds, NULL, NULL, &timeout);
```

**缺点**：

- fd 上限 **FD_SETSIZE**（通常 1024）
- 每次 **O(n)** 扫描全集合
- 每次 **拷贝 fd_set** 到内核
- 返回后不知谁就绪，需遍历

### 3.2 poll

`pollfd` 数组，无 1024 硬限，仍 **O(n)** 扫描。

---

## 四、epoll（Linux）

### 4.1 核心 API

```c
int epfd = epoll_create1(0);
epoll_ctl(epfd, EPOLL_CTL_ADD, fd, &event);
epoll_wait(epfd, events, maxevents, timeout);
```

### 4.2 优势

- **O(1)** 就绪通知（红黑树 + 就绪链表）
- 无 fd 数量硬限（受内存）
- 边缘触发 ET 可减少 wake

### 4.3 LT vs ET

| 模式 | 行为 |
|------|------|
| LT 水平触发 | 只要就绪，wait 一直返回 |
| ET 边缘触发 | 状态变化只通知一次 |

**ET 要求**：一次 read **读到 EAGAIN**，否则丢事件。

**Netty 默认 LT**；高吞吐可调 ET +  careful read loop。

### 4.4 伪代码 Echo

```c
// LT 模式
while (1) {
    int n = epoll_wait(...);
    for (i = 0; i < n; i++) {
        if (events[i].events & EPOLLIN) {
            while (read(fd, buf, sizeof buf) > 0) { /* echo */ }
        }
    }
}
```

---

## 五、Reactor 模式

### 5.1 单 Reactor 单线程

accept + read + business + write 同线程 → 业务不能阻塞。

### 5.2 单 Reactor 多线程

Reactor 做 IO，业务丢 **线程池**。

### 5.3 主从 Reactor

**Main Reactor** accept → **Sub Reactor** 处理 IO。

**Netty**：Boss EventLoopGroup + Worker EventLoopGroup。

```
       ┌──────── Boss ────────┐
       │  accept new conn    │
       └─────────┬───────────┘
                 │ register
       ┌─────────▼───────────┐
       │  Worker EventLoop   │
       │  read/decode/encode │
       └─────────┬───────────┘
                 │ 阻塞业务
       ┌─────────▼───────────┐
       │   Business Pool    │
       └────────────────────┘
```

---

## 六、Java NIO

### 6.1 核心类

| 类 | 作用 |
|----|------|
| Channel | 双向通道 |
| Buffer | 数据容器 |
| Selector | 多路复用 |

```java
Selector selector = Selector.open();
serverChannel.configureBlocking(false);
serverChannel.register(selector, SelectionKey.OP_ACCEPT);

while (true) {
    selector.select();
    Set<SelectionKey> keys = selector.selectedKeys();
    for (SelectionKey key : keys) {
        if (key.isAcceptable()) { /* accept */ }
        if (key.isReadable()) { /* read */ }
    }
    keys.clear();
}
```

**Linux 底层**：Selector 实现用 **epoll**（`EPollSelectorImpl`）。

### 6.2 与 BIO 对比

| | BIO | NIO |
|--|-----|-----|
| 线程 | 每连接 | 少线程多连接 |
| API | 流 | Channel+Buffer |
| 阻塞 | 默认阻塞 | 可非阻塞 |

---

## 七、Netty 要点

### 7.1 为何用 Netty 而非裸 NIO

- EventLoop 线程模型
- Pipeline 责任链 Handler
- 零拷贝 `ByteBuf`、内存池
- Epoll/KQueue 原生 transport

```java
EventLoopGroup boss = new NioEventLoopGroup(1);
EventLoopGroup worker = new NioEventLoopGroup();
ServerBootstrap b = new ServerBootstrap();
b.group(boss, worker)
 .channel(NioServerSocketChannel.class)
 .childHandler(new ChannelInitializer<SocketChannel>() {
     protected void initChannel(SocketChannel ch) {
         ch.pipeline().addLast(new MyHandler());
     }
 });
```

### 7.2 业务线程

**Handler 里勿阻塞**（DB、sleep）→ 丢到业务线程池或异步 Handler。

---

## 八、零拷贝

| 技术 | 说明 |
|------|------|
| sendfile | 文件 → socket 内核态拷贝，少 user 态 |
| mmap | 文件映射 |
| DirectBuffer | 堆外，少一次拷贝 |

**Kafka、Netty、Tomcat** 文件发送常用 sendfile 思想。

---

## 九、Tomcat NIO

Tomcat 8+ **NIO Connector**：Poller 线程 select 就绪 → Worker 处理。

**APR/native** 用 OpenSSL、sendfile 优化。

---

## 十、C10K 与扩展

- **C10K**：1 万并发连接
- 路径：epoll + 非阻塞 + 事件驱动 + 多核 Reactor
- **C10M**：SO_REUSEPORT、多 epoll、内核 bypass（DPDK，超纲）

---

## 十一、面试高频问答

| 问 | 答 |
|----|-----|
| BIO/NIO/AIO？ | 阻塞等数据；多路复用+自己读；内核读完通知 |
| select 和 epoll？ | select O(n) 1024 限；epoll 事件驱动 O(1) |
| LT 和 ET？ | 水平重复通知 vs 边缘一次；ET 要读尽 |
| Reactor 和 Proactor？ | Reactor 就绪通知自己读；Proactor 异步读完回调 |
| Netty 线程模型？ | Boss/Worker EventLoop，每 Channel 绑定一个 EventLoop |
| 为何 NIO 还要多线程？ | 业务阻塞不能占 EventLoop |

---

## 十二、排查

- **连接数**：`ss -tan | wc -l`
- **EventLoop 阻塞**：Netty 慢日志 `io.netty.handler.logging.LoggingHandler`
- **CPU 高 + 少连接**：ET 未读尽、busy loop

---

## 十四、Proactor 与 AIO

**Proactor**：应用注册异步读 → 内核读完 → 完成队列通知 → 回调。

Windows **IOCP** 成熟；Linux **io_uring** 新接口（Java 逐步支持）。

Netty 5 探索 io_uring transport；7 年了解名词即可。

---

## 十五、Epoll 边缘触发完整读循环

```java
// Netty Epoll ET 思想
while (true) {
    ByteBuf buf = alloc.buffer();
    int read = channel.read(buf);
    if (read == 0) break;      // ET：无更多数据
    if (read < 0) { /* close */ break; }
    pipeline.fireChannelRead(buf);
}
```

未读尽 ET 下事件不再触发 → **bug 表现为偶发不响应**。

---

## 十六、Tomcat 线程模型对照

| Connector | 模型 |
|-----------|------|
| BIO | 一连接一线程 |
| NIO | Poller + Worker |
| NIO2 | JSR356 AIO |
| APR | Native |

Spring Boot 默认 **NIO** `TomcatWebServer`。

---

## 十七、背压（Backpressure）

生产者快于消费者 → 队列堆积 → OOM。

**Reactive Streams**：`request(n)` 控流；Netty `WRITE_BUFFER_WATER_MARK` 写缓冲高水位暂停 read。

---

## 十八、文件 IO vs 网络 IO

| | 文件 | 网络 |
|--|------|------|
| 阻塞常见 | 是 | NIO 常用非阻塞 |
| 零拷贝 | sendfile | 同 |
| Java NIO FileChannel | transferTo | SocketChannel |

---

## 十九、排查 checklist

- [ ] EventLoop 线程是否被 DB 阻塞
- [ ] 是否 LT 误用 ET 未读尽
- [ ] 连接数 vs 线程数是否合理
- [ ] DirectBuffer 泄漏（Netty leak detector）

```java
ResourceLeakDetector.setLevel(Level.PARANOID); // 开发环境
```

---

## 二十、面试扩展

**Q8：为什么 Redis 单线程还快？**  
纯内存、IO 多路复用、无锁、高效数据结构；6.0+ 多线程 IO 仍单线程命令。

**Q9：BIO 转 NIO 收益何时明显？**  
高并发长连接、连接数 >> 线程数；短连接 HTTP 1.0 风格收益小。

---

## 二十二、Channel 与 Selector 键

```java
SelectionKey key = channel.register(selector, SelectionKey.OP_READ);
key.attach(buffer); // 附加状态
key.cancel();       // 注销
```

**OP_WRITE**：写缓冲满注册 OP_WRITE，可写后写并取消 OP_WRITE。

---

## 二十三、Netty ByteBuf 与内存池

| | HeapByteBuf | DirectByteBuf |
|--|-------------|---------------|
| GC | 参与 | 堆外 |
| IO | 多一次拷贝 | 少拷贝 |
| 泄漏 | GC 回收 | 需 release |

```java
// 必须 release
ReferenceCountUtil.release(buf);
```

---

## 二十四、IO_URING 简介

Linux 5.1+ 统一异步 IO 接口，减少 syscall。Netty、Redis 未来可能更多采用。

**对比 epoll**：epoll 通知就绪仍同步 read；io_uring 可真异步读完成。

---

## 二十五、阻塞 JDBC 对虚拟线程影响

虚拟线程中 **阻塞 JDBC** 会 mount 载体，若载体不够仍瓶颈。Project Loom 目标：JDBC 驱动改非阻塞或 native mount。

**当前**：虚拟线程 + 阻塞 JDBC 仍比平台线程 1:1 省资源，但 DB 连接池大小仍要调。

---

## 二十六、Epoll 惊群（了解）

多进程 accept 同一 listen fd → 惊群唤醒多个 worker 仅一个成功。

**解决**：SO_REUSEPORT 每进程独立 listen；或主进程 accept 分发。

---

## 二十七、小结

```
阻塞 BIO → 非阻塞+轮询 → select/poll → epoll
Reactor：Main accept + Sub IO + 业务池
Java：NIO Selector、Netty EventLoop、勿阻塞 Handler
零拷贝：sendfile、DirectBuffer
```

下一章：[04-死锁与面试题库.md](./04-死锁与面试题库.md)

← [02-内存管理](./02-内存管理.md) · [README](./README.md)
