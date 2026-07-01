# 03 BIO、NIO 与 Netty

> **目标**：7 年后端工程师应能讲清 Linux IO 模型、Java NIO 核心组件、Reactor 线程模型，并在高并发网关/RPC 场景下正确选型与排障。

---

## 一、IO 模型全景

### 1.1 用户态与内核态

IO 操作涉及：
1. 应用发起 read/write
2. 内核将数据在 **内核缓冲区** 与 **用户缓冲区** 间拷贝
3. 网络数据经 DMA 到内核 socket buffer

**阻塞点**：等待数据就绪（网络到达、磁盘读完成） vs 数据拷贝。

### 1.2 五种模型（Stevens）

| 模型 | 阻塞阶段 | Java 对应 |
|------|----------|-----------|
| 阻塞 IO（BIO） | 等待数据 + 拷贝 | `InputStream.read()` |
| 非阻塞 IO | 轮询就绪，拷贝仍可能阻塞 | NIO `configureBlocking(false)` |
| IO 多路复用 | select/epoll 等一次等多 fd | NIO `Selector` |
| 信号驱动 | 较少用 | — |
| 异步 IO（AIO） | 内核完成后再通知 | `AsynchronousChannel` |

**关键区分**：
- **同步**：应用自己调用 read/write 完成拷贝
- **异步**：内核完成整个 IO 后回调应用（Proactor）

Java NIO + Selector 是 **多路复用 + 同步非阻塞**；AIO 在 Linux 上 epoll 模拟，生产少用。

### 1.3 后端选型直觉

| 场景 | 推荐 |
|------|------|
| 低并发、简单文件/HTTP | BIO + 线程池 |
| 高并发长连接（网关、IM、RPC） | NIO / Netty |
| 磁盘 IO 为主 | 阻塞 + 足够线程 often 更简单 |
| Java 21+ IO 密集 HTTP | 虚拟线程 + 阻塞 Servlet 可回归简单模型 |

---

## 二、Java BIO

### 2.1 典型服务端

```java
ServerSocket server = new ServerSocket(8080);
while (true) {
    Socket client = server.accept();  // 阻塞 1：等待连接
    threadPool.execute(() -> {
        try (InputStream in = client.getInputStream();
             OutputStream out = client.getOutputStream()) {
            byte[] buf = new byte[1024];
            int n;
            while ((n = in.read(buf)) != -1) {  // 阻塞 2：等待数据
                out.write(buf, 0, n);
            }
        } catch (IOException e) {
            log.error("client error", e);
        }
    });
}
```

### 2.2 问题

- **C10K**：每连接一线程，栈内存（默认 1MB）、上下文切换、调度开销
- 线程阻塞在 read，利用率低
- 适合连接数少、逻辑简单、开发成本优先

### 2.3 Tomcat 线程模型（对比）

- **BIO Connector**（已废弃）：一连接一线程
- **NIO Connector**：Poller 线程 accept + 注册 interestOps，Worker 处理请求
- **Apr**：JNI 封装 native

理解 Tomcat NIO 是过渡到 Netty 的桥梁。

---

## 三、Java NIO 核心

### 3.1 三大件

```
Channel  ←→  Buffer  ←→  内核/网络
    ↑
 Selector（多路复用）
```

| 组件 | 角色 |
|------|------|
| Buffer | 字节容器，flip/clear/compact 切换读写模式 |
| Channel | 双向通道，FileChannel、SocketChannel、ServerSocketChannel |
| Selector | 注册 Channel 与感兴趣事件，select 批量就绪 |

### 3.2 Buffer 状态机

```
allocate → write → flip → read → clear/compact → write ...
         position, limit, capacity
```

**常见坑**：
- 忘记 `flip()` 导致读 0 字节
- `compact()` 与 `clear()` 混淆
- Direct Buffer 分配慢、需手动管理或 GC 回收（Cleaner）

### 3.3 Selector 事件

```java
selectionKey.interestOps(SelectionKey.OP_READ | SelectionKey.OP_WRITE);
```

| OP | 含义 |
|----|------|
| OP_ACCEPT | ServerSocket 有新连接 |
| OP_CONNECT | 客户端连接完成 |
| OP_READ | 可读 |
| OP_WRITE | 可写（TCP 缓冲区有空间） |

**OP_WRITE 注意**：通常写不完才注册 WRITE，写完 remove OP_WRITE，否则空轮询 busy loop。

### 3.4 简易 Reactor 单线程

```java
Selector selector = Selector.open();
ServerSocketChannel ssc = ServerSocketChannel.open();
ssc.configureBlocking(false);
ssc.bind(new InetSocketAddress(8080));
ssc.register(selector, SelectionKey.OP_ACCEPT);

while (true) {
    selector.select();  // 阻塞直到有事件
    Set<SelectionKey> keys = selector.selectedKeys();
    Iterator<SelectionKey> it = keys.iterator();
    while (it.hasNext()) {
        SelectionKey key = it.next();
        it.remove();
        if (key.isAcceptable()) {
            SocketChannel sc = ssc.accept();
            sc.configureBlocking(false);
            sc.register(selector, SelectionKey.OP_READ);
        } else if (key.isReadable()) {
            // read from (SocketChannel) key.channel()
        }
    }
}
```

---

## 四、Reactor 线程模型

### 4.1 单 Reactor 单线程

```
[Selector 线程] accept + read + decode + 业务 + encode + write
```

- 优点：无锁、简单
- 缺点：业务阻塞拖死整个 loop（Redis 6.0 前类似）

### 4.2 单 Reactor 多线程

```
[Reactor] accept + read + write
    ↓ 提交任务
[Worker 线程池] 业务处理
```

Netty **默认常用变体**：Boss 只 accept，Worker 负责 read/write（主从 Reactor）。

### 4.3 主从 Reactor 多线程

```
[Boss Group]  多个 Reactor，专门 accept
[Worker Group] 多个 Reactor，IO read/write
[Business Pool] 可选，耗时业务
```

**规则**：**永远不要在 EventLoop 线程做阻塞 IO、锁竞争、Heavy CPU**。

---

## 五、零拷贝

### 5.1 传统 4 次拷贝

```
磁盘 → 内核 buffer → 用户 buffer → socket buffer → 网卡
      (DMA)        (CPU)          (CPU)
```

### 5.2 sendfile（Linux）

```
磁盘 → 内核 buffer → socket buffer → 网卡
      (DMA)         (DMA，可能 CPU 辅助)
```

Java `FileChannel.transferTo()` 在 Linux 上可走 sendfile。

### 5.3 mmap

文件映射到用户空间，减少一次拷贝；适合大文件随机读。

### 5.4 Direct ByteBuffer

堆外内存，JNI 读写 socket 时少一次堆↔堆外拷贝。

**Direct Memory 监控**：`-XX:MaxDirectMemorySize`，堆外 OOM 排查见 phase2-JVM。

---

## 六、Netty 架构概览

### 6.1 为什么用 Netty 而非裸 NIO

| 裸 NIO 痛点 | Netty 解决 |
|-------------|------------|
| API 繁琐 | 高级抽象 ChannelHandler |
| Epoll 空轮询 bug | 封装 workaround |
| 半包粘包 | 编解码框架 |
| 线程模型复杂 | EventLoopGroup 规范 |
| 内存管理 | ByteBuf 池化 |

### 6.2 核心组件

```
Bootstrap / ServerBootstrap
EventLoopGroup (Boss / Worker)
Channel (NioServerSocketChannel, NioSocketChannel)
ChannelPipeline (Handler 链)
ChannelHandler (Inbound / Outbound)
ByteBuf
Allocator (PooledByteBufAllocator)
```

### 6.3 线程模型

```java
EventLoopGroup boss = new NioEventLoopGroup(1);
EventLoopGroup worker = new NioEventLoopGroup();  // 默认 2 * CPU
ServerBootstrap b = new ServerBootstrap();
b.group(boss, worker)
 .channel(NioServerSocketChannel.class)
 .childHandler(new ChannelInitializer<SocketChannel>() {
     @Override
     protected void initChannel(SocketChannel ch) {
         ch.pipeline().addLast(new HttpServerCodec(), new MyHandler());
     }
 });
```

- 一个 **EventLoop** = 一个线程 + 一个 Selector + 多个 Channel
- 同一 Channel 的 IO 事件始终在同一线程串行 → 无需锁 Channel 状态

---

## 七、ChannelPipeline 与 Handler

### 7.1 责任链

```
Inbound:  head → decoder → business → tail
Outbound: tail → encoder → head → socket
```

- **Inbound**：channelRead、exceptionCaught
- **Outbound**：write、flush（从 tail 向 head 传播）

### 7.2 Handler 生命周期

```
handlerAdded → channelRegistered → channelActive
→ channelRead* → channelInactive → channelUnregistered → handlerRemoved
```

**Sharable**：无状态 Handler 可 `@Sharable` 单例复用；有状态必须每 Channel new。

### 7.3 示例：LengthFieldBasedFrameDecoder

解决 TCP 粘包：帧头 4 字节长度 + body。

```java
pipeline.addLast(new LengthFieldBasedFrameDecoder(65535, 0, 4, 0, 4));
pipeline.addLast(new StringDecoder(CharsetUtil.UTF_8));
pipeline.addLast(new BusinessHandler());
```

---

## 八、ByteBuf

### 8.1 vs ByteBuffer

| 特性 | ByteBuffer | ByteBuf |
|------|------------|---------|
| 读写索引 | 单一 position | readerIndex + writerIndex |
| 扩容 | 手动 | 自动 |
| 池化 | 无 | PooledByteBufAllocator |
| 引用计数 | 无 | retain/release |

### 8.2 堆内 vs 堆外

- **HeapByteBuf**：分配快，socket 写需拷贝到 Direct
- **DirectByteBuf**：分配慢，IO 性能好

### 8.3 内存泄漏

```java
// 必须 release，尤其在异常路径
try {
    ByteBuf buf = ctx.alloc().buffer();
    // ...
} finally {
    ReferenceCountUtil.release(buf);
}
```

**排查**：`-Dio.netty.leakDetection.level=paranoid`（仅开发）；生产 `simple` 或 `advanced`。

**常见泄漏**：Handler 持有 ByteBuf 引用未 release；SimpleChannelInboundHandler 自动 release 入站消息。

---

## 九、编解码与协议设计

### 9.1 粘包拆包原因

TCP 字节流无消息边界；send 两次可能一次 receive（粘包），或半条消息（拆包）。

### 9.2 方案

| 方案 | 说明 |
|------|------|
| 固定长度 | 简单，浪费 |
| 分隔符 | 如 `\n`，需转义 |
| 长度字段 | 最常用 |
| 协议头+体 | HTTP、自定义 RPC |

### 9.3 Protobuf / JSON over Netty

- 序列化后仍需要 **帧界定**
- gRPC 基于 HTTP/2 帧，底层 Netty

---

## 十、Netty 与生态对比

| 框架 | 模型 | 适用 |
|------|------|------|
| Tomcat NIO | Servlet 阻塞语义 + NIO 底层 | 传统 Web |
| Netty | Reactor | RPC、网关、IM、Redis 客户端 |
| Spring WebFlux | Reactor（Netty / Servlet 3.1 async） | 响应式 Web |
| Vert.x | Event Loop | 多语言、工具集 |

**7 年工程师**：能说 Dubbo/gRPC 底层为何选 Netty；WebFlux 适合 IO 密集而非 CPU 密集。

---

## 十一、Java 21 虚拟线程

### 11.1 模型变化

```java
try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
    executor.submit(() -> {
        InputStream in = socket.getInputStream();
        in.read();  // 阻塞时挂起虚拟线程，释放平台线程
    });
}
```

**意义**：IO 密集型可回归 **同步阻塞代码风格**，无需手写 Reactor；平台线程数可小。

### 11.2 与 Netty 关系

- 虚拟线程：**简化业务代码**
- Netty：**极致 IO 吞吐、协议栈、内存管理**
- 高并发 RPC 框架仍大量 Netty；Spring Boot 3.2+ 可选虚拟线程处理 HTTP

### 11.3 注意

- `synchronized` 在 pin 载体线程（JDK 24+ 改进中）
- 线程本地变量数量暴增时的内存
- 与 ThreadLocal 池化平台线程的库交互

---

## 十二、线上案例

### 12.1 连接泄漏

**现象**：`Too many open files`，ESTABLISHED 飙涨。

**原因**：Channel 未 close；异常路径未 release；连接池泄漏。

**排查**：`lsof -p pid`、Netty leak detection、连接数监控。

### 12.2 慢客户端（Slowloris）

**现象**：Worker 线程耗尽，服务不可用。

**防护**：读超时 IdleStateHandler、限制 header/body 大小、反向代理超时。

### 12.3 Epoll 空轮询（JDK 历史 bug）

Netty 检测 select 返回 0 次数，超阈值 rebuild Selector。

### 12.4 EventLoop 阻塞

**现象**：延迟尖刺，心跳超时。

**排查**：Arthas `thread -n` 看 EventLoop 线程栈；业务 offload 到独立线程池。

---

## 十三、性能调优 checklist

- [ ] Boss 通常 1 个即可
- [ ] Worker 默认 `2 * cores`，压测后调整
- [ ] 使用 PooledByteBufAllocator
- [ ] 合理 SO_BACKLOG、TCP_NODELAY、SO_REUSEADDR
- [ ] 写缓冲水位 `WRITE_BUFFER_WATER_MARK` 防 OOM
- [ ] 禁用不必要的 Handler
- [ ] 监控：连接数、ByteBuf 分配速率、EventLoop 任务队列延迟

---

## 十四、手写 Mini Echo Server（Netty）

```java
public final class EchoServer {
    public static void main(String[] args) throws InterruptedException {
        EventLoopGroup boss = new NioEventLoopGroup(1);
        EventLoopGroup worker = new NioEventLoopGroup();
        try {
            ServerBootstrap b = new ServerBootstrap();
            b.group(boss, worker)
             .channel(NioServerSocketChannel.class)
             .childOption(ChannelOption.TCP_NODELAY, true)
             .childHandler(new ChannelInitializer<SocketChannel>() {
                 @Override
                 protected void initChannel(SocketChannel ch) {
                     ch.pipeline().addLast(new EchoHandler());
                 }
             });
            ChannelFuture f = b.bind(8080).sync();
            f.channel().closeFuture().sync();
        } finally {
            boss.shutdownGracefully();
            worker.shutdownGracefully();
        }
    }

    static class EchoHandler extends ChannelInboundHandlerAdapter {
        @Override
        public void channelRead(ChannelHandlerContext ctx, Object msg) {
            ctx.write(msg);
        }

        @Override
        public void channelReadComplete(ChannelHandlerContext ctx) {
            ctx.flush();
        }

        @Override
        public void exceptionCaught(ChannelHandlerContext ctx, Throwable cause) {
            log.error("echo error", cause);
            ctx.close();
        }
    }
}
```

---

## 十五、面试自测

1. BIO、NIO、AIO 区别？Java NIO 是异步吗？
2. Selector 的 select/poll/epoll 在 Linux 上如何映射？
3. 为什么 Netty 用 EventLoop 而不是每 Channel 一线程？
4. ByteBuf 为什么要引用计数？
5. 粘包如何解决？LengthFieldBasedFrameDecoder 参数含义？
6. 虚拟线程会取代 Netty 吗？为什么？

---

← [上一章：注解反射与异常](./02-注解反射与异常.md) · [目录](./README.md) · 下一章：[04-Stream与新特性](./04-Stream与新特性.md)
