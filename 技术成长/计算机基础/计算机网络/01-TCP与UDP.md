# 第一章：TCP 与 UDP

> **阅读目标**：深入理解 TCP 可靠传输、流量/拥塞控制、连接管理，掌握 UDP 适用场景及与 Java 网络编程的对应关系。
>
> **建议用时**：通读 80 min；结合 Wireshark 抓包三次握手（可选）。

---

## 一、传输层职责

### 1.1 端到端交付

传输层在 **IP 寻址（主机）** 之上提供 **端口（进程）** 级通信：

| 职责 | TCP | UDP |
|------|-----|-----|
| 多路复用 | 端口号 | 端口号 |
| 可靠交付 | 是 | 否 |
| 有序 | 是 | 尽力 |
| 连接 | 面向连接 | 无连接 |
| 首部开销 | 20–60 字节 | 8 字节 |

**Java**：`Socket`/`ServerSocket`（TCP）；`DatagramSocket`（UDP）。

---

## 二、TCP 报文段

### 2.1 首部字段

| 字段 | 作用 |
|------|------|
| 源/目的端口 | 16 bit |
| 序号 Sequence | 字节流编号 |
| 确认号 ACK | 期望下一字节 |
| 标志位 SYN/FIN/RST/PSH/ACK | 连接控制 |
| 窗口 Window | 流量控制 |
| 校验和 | 端到端差错检测 |
| 选项 | MSS、SACK、时间戳 |

### 2.2 序号与确认

TCP 把数据看作 **字节流**；`seq` 为本段第一个字节序号；`ack` 表示已收到 ack-1 及之前，期望 ack。

**累积确认**：ack=N 表示 N-1 及之前全收到。

---

## 三、连接建立：三次握手

```
客户端                         服务端
   |  SYN, seq=x                |
   | ------------------------> |
   |                            |
   |  SYN+ACK, seq=y, ack=x+1   |
   | <------------------------ |
   |                            |
   |  ACK, seq=x+1, ack=y+1     |
   | ------------------------> |
   |                            ESTABLISHED
 ESTABLISHED
```

### 3.1 为什么是三次

1. **双方确认收发能力**：SYN 证明客户端能发；SYN+ACK 证明服务端能收能发；ACK 证明客户端能收。
2. **同步初始序号 ISN**：双方各自选择 seq，防止旧连接报文干扰（需结合 TIME_WAIT）。
3. **两次不够**：服务端无法确认客户端收到了自己的 SYN+ACK。

### 3.2 SYN  flood 与 SYN 队列

攻击者发大量 SYN 不完成握手 → 半连接队列满。

**防护**：SYN Cookie、增大 `tcp_max_syn_backlog`、防火墙限速。

**Java/Tomcat**：`accept` 队列、`backlog` 参数与全连接队列相关。

---

## 四、连接释放：四次挥手

```
主动关闭方                    被动关闭方
   |  FIN, seq=u                |
   | ------------------------> |
   |  ACK, ack=u+1              |
   | <------------------------ |
   |                            | （可能还有数据要发）
   |  FIN, seq=v                |
   | <------------------------ |
   |  ACK, ack=v+1              |
   | ------------------------> |
 TIME_WAIT
```

### 4.1 为何四次

TCP **全双工**；关闭需双方各自关闭写方向。被动方 ACK 与 FIN 常分开发（被动方还有数据时）。

### 4.2 TIME_WAIT（2MSL）

主动关闭方发最后 ACK 后进入，通常 **1–4 分钟**。

**原因**：

1. 若最后 ACK 丢失，被动方重传 FIN，主动方需能重发 ACK。
2. 让旧连接报文在网络中消散，避免新连接误判。

**大量 TIME_WAIT**：端口耗尽 → `SO_REUSEADDR`、调整内核参数、让客户端少主动关（长连接）。

**CLOSE_WAIT 过多**：应用未 `close()`，代码 bug 或资源泄漏。

---

## 五、可靠传输机制

### 5.1 超时重传

RTT 估计 → RTO（Retransmission Timeout）；超时未 ACK 则重传。

**指数退避**：RTO 翻倍，避免网络拥塞时风暴。

### 5.2 快速重传

收到 **3 个重复 ACK**（dup ACK）→ 认为丢包，立即重传，不等 RTO。

### 5.3 滑动窗口

发送方维护 **发送窗口**；接收方通过 **窗口字段** 告知可接收字节数 → **流量控制**，防止快发送淹没慢接收。

**零窗口**：接收方忙，发送方停发；**窗口探测** 定时探询。

---

## 六、拥塞控制

### 6.1 与流量控制区别

| | 流量控制 | 拥塞控制 |
|--|----------|----------|
| 对象 | 接收方能力 | 网络能力 |
| 手段 | rwnd | cwnd |

### 6.2 四个阶段（经典）

1. **慢开始**：cwnd 从 1 MSS 指数增，到 ssthresh 转拥塞避免。
2. **拥塞避免**：cwnd 线性 +1 MSS / RTT。
3. **快重传**：3 dup ACK → 重传丢失段。
4. **快恢复**：快重传后 cwnd 减半而非从 1 开始（实现因版本而异）。

**丢包信号**：超时 → 严重，cwnd 重置慢开始；3 dup ACK → 较轻，快恢复。

### 6.3 现代算法

CUBIC（Linux 默认）、BBR（基于带宽延迟）——面试提名词即可。

---

## 七、TCP 特性补充

### 7.1 Nagle 算法

小数据合并发送，降低小包；**低延迟场景可 `TCP_NODELAY` 关闭**（游戏、RPC）。

### 7.2 延迟 ACK

接收方合并 ACK，减少报文；与 Nagle 叠加可能增加延迟。

### 7.3 Keep-Alive

探测死连接；HTTP Keep-Alive 是应用层复用 TCP 连接，概念不同。

**Java**：

```java
socket.setKeepAlive(true);
socket.setTcpNoDelay(true);
```

---

## 八、UDP

### 8.1 特点

- 无连接、无可靠、无拥塞控制
- 首部 8 字节：端口 + 长度 + 校验和
- 适合：**实时性 > 完整性**、广播/组播、简单请求响应

### 8.2 典型场景

| 场景 | 原因 |
|------|------|
| DNS | 单次小查询，丢包重试由应用做 |
| 视频/语音 | 丢帧可容忍，重传延迟大 |
| 游戏状态 | 高频更新，旧包过时 |
| QUIC/HTTP3 | 用户态可靠，基于 UDP 绕开 OS TCP |

### 8.3 UDP 可靠化

应用层实现：序列号、ACK、重传 → **QUIC**、**KCP**、自定义游戏协议。

---

## 九、TCP vs UDP 选型

| 选 TCP | 选 UDP |
|--------|--------|
| 文件、HTTP、RPC、DB | DNS、监控打点、流媒体 |
| 不能丢、顺序重要 | 可丢、要低延迟 |
| 内核成熟拥塞控制 | 需自研或 QUIC |

**Java RPC**：Dubbo 默认 TCP；gRPC HTTP/2 over TCP。

---

## 十、Socket 编程要点（Java）

### 10.1 TCP 服务端

```java
ServerSocket server = new ServerSocket(8080, backlog, bindAddr);
while (true) {
    Socket client = server.accept();
    // 线程池处理 client.getInputStream()
}
```

### 10.2 常见问题

| 现象 | 可能原因 |
|------|----------|
| Connection reset | 对端 RST、半开连接 |
| Broken pipe | 写时连接已关 |
| Address already in use | TIME_WAIT 占端口，REUSEADDR |
| Read timeout | 仅 read 超时，非连接断 |

---

## 十一、面试高频问答

| 问 | 答 |
|----|-----|
| 三次握手四次挥手？ | 见上文；关闭全双工需两 FIN |
| TIME_WAIT 作用？ | 保 ACK、清旧包；2MSL |
| 如何保证可靠？ | 序号、ACK、重传、校验 |
| 滑动窗口？ | 流量控制，接收方 rwnd |
| 拥塞控制算法阶段？ | 慢开始、拥塞避免、快重传、快恢复 |
| TCP 和 UDP 区别？ | 连接、可靠、首部、场景 |
| 为何 HTTP/3 用 UDP？ | QUIC 在用户态实现多路复用+可靠，减少队头阻塞 |

---

## 十二、内核参数（运维了解）

| 参数 | 含义 |
|------|------|
| net.ipv4.tcp_tw_reuse | 复用 TIME_WAIT 开新连接（谨慎） |
| net.core.somaxconn | 全连接队列上限 |
| tcp_max_syn_backlog | SYN 队列 |

生产由 SRE 调；开发需知 **backlog、超时、连接池** 配置。

---

## 十三、TCP 状态机详解

```
CLOSED → LISTEN（服务端）
LISTEN → SYN_SENT（客户端发 SYN）
SYN_SENT → ESTABLISHED（收到 SYN+ACK 发 ACK）
LISTEN → SYN_RCVD（收 SYN 发 SYN+ACK）
SYN_RCVD → ESTABLISHED（收 ACK）

ESTABLISHED → FIN_WAIT_1（主动 close）
FIN_WAIT_1 → FIN_WAIT_2（收 ACK）
FIN_WAIT_2 → TIME_WAIT（收 FIN 发 ACK）
TIME_WAIT → CLOSED（2MSL 后）

ESTABLISHED → CLOSE_WAIT（收 FIN 发 ACK）
CLOSE_WAIT → LAST_ACK（应用 close 发 FIN）
LAST_ACK → CLOSED（收 ACK）
```

**排查**：大量 CLOSE_WAIT → 应用未关闭 socket；大量 TIME_WAIT → 短连接频繁。

---

## 十四、RTO 与 Karn 算法

**Karn 算法**：重传段不能用于 RTT 采样（分不清原包还是重传）。

**指数退避**：RTO ← RTO × 2，上限通常 60s+。

---

## 十五、SACK 选择性确认

传统累积 ACK 丢中间包 → 后续全重传。**SACK** 告知非连续已收块，只重传丢失段。

Linux 默认开启 SACK；配合 **快速重传** 提高吞吐。

---

## 十六、UDP 广播组播与 Java

```java
MulticastSocket ms = new MulticastSocket(4446);
ms.joinGroup(InetAddress.getByName("224.0.0.1"));
```

**场景**：服务发现（部分老系统）、局域网通知；生产多用 **MQ/注册中心** 替代。

---

## 十七、Java Socket 超时与半连接

```java
socket.connect(addr, 3000);
socket.setSoTimeout(10000); // read block 超时
serverSocket.setSoTimeout(0); // accept 无限
```

**半连接队列**：SYN_RCVD 过多 → 调 `tcp_max_syn_backlog`、SYN Cookie。

---

## 十八、TCP 与 QUIC 对比（HTTP/3）

| | TCP | QUIC |
|--|-----|------|
| 连接 | 内核 | 用户态 |
| 队头阻塞 | 字节流级 | 独立 stream |
| 握手 | 3 RTT（+TLS） | 0-1 RTT |
| 迁移 | IP 变需重连 | Connection ID |

---

## 十九、实战案例

**案例 1**：微服务间 reset → 下游重启 + 客户端无重试 → Feign retry + 熔断。

**案例 2**：TIME_WAIT 65535 端口耗尽 → Keep-Alive 池化 + `SO_REUSEADDR` + 让客户端少关连接。

**案例 3**：延迟高但带宽够 → Nagle + 延迟 ACK 叠加 → `TCP_NODELAY`。

---

## 二十一、MSS 与 PMTUD

**MSS**：TCP 单段最大数据长度，通常 1460（1500 MTU - 20 IP - 20 TCP）。

**PMTUD**：Don't Fragment 探路发现路径 MTU，避免 IP 分片。

**Java**：少发超大 UDP 包避免分片丢失。

---

## 二十二、RST 触发场景

| 场景 | 说明 |
|------|------|
| 端口未监听 | Connection refused（RST） |
| 已关闭连接收数据 | RST |
| 防火墙拒绝 | 可能 drop 或 RST |
| half-open 扫描 | 安全工具 |

**Java**：对端 RST → `SocketException: Connection reset`。

---

## 二十三、长 fat pipe 与 BDP

**带宽延迟积 BDP** = 带宽 × RTT = 管道可容纳字节数。

高 BDP 链路需 **大窗口 + 拥塞控制** 才能填满；BBR 优化此类场景。

跨洋 RPC 要 **大 read buffer、连接复用**，否则吞吐低。

---

## 二十四、TCP 与 Nagle 实验

```java
socket.setTcpNoDelay(true);  // 禁用 Nagle，小包立即发
```

**适用**：低延迟 RPC、游戏；**不适用**：大量极小包需合并时。

---

## 二十五、抓包读三次握手

Wireshark 过滤 `tcp.flags.syn==1`：

1. [SYN] seq=x
2. [SYN, ACK] seq=y, ack=x+1
3. [ACK] ack=y+1

**RTT 估算**：SYN 到 SYN-ACK 时间 ≈ 单向延迟下界。

---

## 二十六、Dubbo 与 TCP 参数

```yaml
dubbo:
  protocol:
    name: dubbo
    parameters:
      tcp.no.delay: true
  consumer:
    timeout: 3000
    retries: 0  # 非幂等禁止重试
```

---

## 二十七、小结

```
TCP：可靠字节流、握手挥手、窗口、拥塞
UDP：无连接、低延迟、应用自补可靠
Java：Socket 超时、NODELAY、连接池
排查：TIME_WAIT、CLOSE_WAIT、reset
```

下一章：[02-HTTP与HTTPS.md](./02-HTTP与HTTPS.md)

← [README](./README.md) · [00-速查总览](./00-速查总览.md)
