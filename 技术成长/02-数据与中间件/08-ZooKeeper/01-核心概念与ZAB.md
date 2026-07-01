# 01 · 核心概念与 ZAB

> **预计阅读**：50 min · **难度**：★★★★

---

## 1. ZooKeeper 定位

ZooKeeper 是 **协调者** 而非 **存储者**：

| 适合 | 不适合 |
|------|--------|
| 配置中心（KB 级） | 业务大数据存储 |
| 服务注册发现 | 高频写日志 |
| 分布式锁/选主 | 海量读写的缓存 |
| 集群成员管理 | 文件/对象存储 |

**设计目标**：高可用、严格顺序、快速读取、可靠观察（Watch）。

---

## 2. 数据模型 — ZNode 树

```
/
├── zookeeper
├── config
│   └── app
│       └── timeout
├── services
│   └── order-service
│       ├── instance-0000000001
│       └── instance-0000000002
└── locks
    └── payment
        └── lock-0000000003
```

| 特性 | 说明 |
|------|------|
| 路径 | 绝对路径，类似 Unix，`/` 根 |
| 数据 | 每个 ZNode 可存 ≤ 1MB 数据（默认） |
| 子节点 | 有序列表 |
| 无递归删除 | 有子节点时不能直接删父节点 |

**Stat 结构**（get 命令可见）：

| 字段 | 含义 |
|------|------|
| czxid | 创建时 zxid |
| mzxid | 最后修改 zxid |
| ctime/mtime | 创建/修改时间 |
| version | 数据版本 |
| cversion | 子节点版本 |
| aversion | ACL 版本 |
| ephemeralOwner | 临时节点所属 sessionId |
| numChildren | 子节点数 |

---

## 3. Session 与会话

客户端连接建立 **Session**，服务端维护 Session 超时。

```
Client ──connect──► Server
         ◄──heartbeat──►（默认 1/3 timeout 发 ping）
Session 超时 → 临时节点删除 → 触发 Watcher
```

| 参数 | 说明 |
|------|------|
| `sessionTimeout` | 客户端协商，服务端取允许范围内值 |
| 典型值 | 4000～40000 ms |
| 重连 | Session 未过期可恢复，临时节点仍在 |

**Java 客户端**：

```java
CuratorFramework client = CuratorFrameworkFactory.builder()
    .connectString("zk1:2181,zk2:2181,zk3:2181")
    .sessionTimeoutMs(30000)
    .retryPolicy(new ExponentialBackoffRetry(1000, 3))
    .build();
client.start();
```

---

## 4. ACL 访问控制

| 权限 | 缩写 | 说明 |
|------|------|------|
| CREATE | c | 创建子节点 |
| READ | r | 读 |
| WRITE | w | 写 |
| DELETE | d | 删子节点 |
| ADMIN | a | setACL |

**scheme**：`world`（开放）、`auth`（已认证）、`digest`（用户名密码）、`ip`。

生产环境应对 `/config` 等敏感路径设 ACL，避免 world:anyone 读写。

---

## 5. ZAB 协议详解

ZAB = **ZooKeeper Atomic Broadcast**，保证所有节点 **顺序一致** 地看到相同写操作。

### 两种模式

```
┌─────────────────────────────────────┐
│  崩溃恢复（Recovery）                │
│  选 Leader → Follower 同步差异       │
└─────────────────┬───────────────────┘
                  ▼
┌─────────────────────────────────────┐
│  消息广播（Broadcast）               │
│  Leader 写 → 过半 ACK → Commit       │
└─────────────────────────────────────┘
```

### 写流程

1. Client 写请求到任意节点
2. 非 Leader 转发给 Leader
3. Leader 生成 zxid，写入本地事务日志
4. 广播 PROPOSAL 给 Followers
5. Followers 写日志并 ACK
6. 过半 ACK 后 Leader 发 COMMIT
7. 各节点应用事务，Client 收到响应

**读请求**：Follower 可直接处理（可能略滞后，非强一致读）。

**sync()**：客户端需读己之所写时，可先调用 `sync()` 等待 Follower 追平。

---

## 6. Leader 选举（简化）

触发：Leader 宕机、集群启动。

| 概念 | 说明 |
|------|------|
| myid | 服务器 ID |
| zxid | 最大 zxid 者优先 |
| vote | 投票给 (zxid, myid) 最大的 |
| 过半 | 获过半票成为 Leader |

**Fast Leader Election**（3.4+）：基于 TCP 通信，比早期 UDP 更快。

---

## 7. 集群部署规则

| 规则 | 原因 |
|------|------|
| 奇数节点 3/5/7 | 过半容错：3 节点容忍 1 挂；4 节点也仅容忍 1 挂 |
| 跨机房 | 避免脑裂，至少 3 机房各 1 节点或 2+2+1 |
| 独立部署 | 不与 Kafka Broker 混部争资源 |
| JVM 堆 | 4～8GB 足够，过大 GC 停顿致命 |

**Observer 节点**：不参与投票，减轻 Follower 压力，适合跨地域读扩展。

---

## 8. 与 CAP

ZooKeeper 选择 **CP**：

- 分区时宁可停服（选举期间不可写）也不丢一致
- 不适合作为高可用缓存，适合协调

| 对比 | ZK | Eureka |
|------|-----|--------|
| CAP | CP | AP |
| 注册中心 | 强一致，可能短暂不可用 | 最终一致，始终可读 |

---

## 9. 小结

| 要点 | 一句话 |
|------|--------|
| 定位 | 协调小数据，不是数据库 |
| ZAB | 过半写 ACK + 顺序广播 |
| Session | 临时节点生命周期绑定 Session |
| 集群 | 奇数节点，过半容错 |

---

← [00 速查](./00-速查总览.md) · [02 节点与 Watch →](./02-节点类型与Watch.md)
