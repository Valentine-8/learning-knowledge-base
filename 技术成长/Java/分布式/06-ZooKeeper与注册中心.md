# 06 · ZooKeeper 与注册中心

> **目标读者**：7 年 Java 后端，能讲清 ZK 数据模型、ZAB、Watcher、Curator Recipes，并对比 Nacos 选型。
> **预计阅读**：60 min · **难度**：★★★★★

---

## 1. ZooKeeper 是什么

Apache ZooKeeper：**分布式协调服务**，提供：

- 统一命名空间（树形 znode）
- **Watcher** 变更通知
- **临时/顺序** 节点
- **CP** 强一致（ZAB 协议）

**典型用途**：注册中心（Dubbo）、分布式锁、Leader 选举、配置管理、Kafka 旧版 offset。

---

## 2. 数据模型

```
/（根）
 ├── /services
 │     └── /order-service
 │           ├── instance-0000000001  [临时顺序]
 │           └── instance-0000000002
 ├── /lock
 │     └── /order/lock-0000000001
 └── /config
       └── db.url
```

| 概念 | 说明 |
|------|------|
| **znode** | 数据节点，路径唯一 |
| **数据** | 每个节点可存少量数据（< 1MB，协调元数据非大文件） |
| **ACL** | 权限控制 |
| **Stat** | version、cversion、czxid、mtime 等 |

---

## 3. 节点类型

| 类型 | 标识 | 行为 |
|------|------|------|
| **持久 Persistent** | 默认 | 客户端断开仍存在 |
| **临时 Ephemeral** | EPHEMERAL | **会话结束自动删除** — 注册/锁核心 |
| **顺序 Sequential** | SEQUENTIAL | 名后自动加单调序号 |
| **组合** | PERSISTENT_SEQUENTIAL 等 | 锁、队列 |

**会话 Session**：客户端与集群 TCP 长连接；超时未心跳 → session 失效 → **临时节点全部删除**。

---

## 4. Watcher 机制

```java
zk.exists("/lock/order", watcher);  // 注册监听
zk.getData(path, watcher);
zk.getChildren(path, watcher);
```

| 特点 | 说明 |
|------|------|
| **一次性** | 触发后 watcher 失效，须再注册 |
| 轻量 | 仅通知「变了」，不推数据；客户端再 get |
| 顺序 | 客户端串行处理 watcher 事件 |

**生产**：直接用 **Curator** 封装 `PathChildrenCache`、`TreeCache`，自动 re-register watcher。

---

## 5. 分布式锁实现

### 5.1 临时顺序节点算法

```
1. 在 /lock/order 下创建 EPHEMERAL_SEQUENTIAL → lock-0000000003
2. 获取 children 并排序
3. 若 lock-0000000003 序号最小 → 获锁
4. 否则 watch **前一个** 节点（如 lock-0000000002）
5. 前一个删除 → 被唤醒 → 重新判断
6. 业务完成 → delete 自己 / 会话断开自动删
```

| 优点 | 缺点 |
|------|------|
| **公平** FIFO | QPS 低于 Redis |
| 无 TTL 误删 | 依赖 ZK 集群 |
| 会话断自动释放 | 网络抖动可能导致 session 过期丢锁 |

### 5.2 Curator InterProcessMutex

```java
CuratorFramework client = CuratorFrameworkFactory.newClient(
    connectString, new ExponentialBackoffRetry(1000, 3));
client.start();

InterProcessMutex lock = new InterProcessMutex(client, "/lock/order");
if (lock.acquire(10, TimeUnit.SECONDS)) {
    try {
        // business
    } finally {
        lock.release();
    }
}
```

Curator 还提供了 **读写锁、信号量、Leader 选举** 等 Recipe。

---

## 6. Leader 选举

```
/leader_select/job_name/
    candidate-0000000001
    candidate-0000000002  ← 序号最小者为 Leader
```

- Leader 节点挂掉 → 临时节点删 → 其他 watcher 触发 → 重新选最小序号
- **Kafka 旧控制器**、**HBase Master** 等曾用类似机制

`LeaderSelector`：Curator 封装，Leader 启动 `takeLeadership`，失去连接自动释放。

---

## 7. ZAB 协议与 CAP

**ZAB（ZooKeeper Atomic Broadcast）**：保证 **全局顺序** 广播。

```
Follower ──proposal──► Leader
Leader ──ack 过半──► commit
```

| 角色 | 职责 |
|------|------|
| **Leader** | 唯一写；事务顺序 |
| **Follower** | 读、投票、转发写 |
| **Observer** | 读扩展，不参与投票 |

**CP 体现**：

- 写入需 **过半 ack**
- 分区时 **少数派不可写**（甚至不可读旧 Leader）
- Leader 选举期间 **短暂不可用**

**读**：默认本地节点可能 **滞后**；强一致读可用 `sync()` 后再读（仍需注意版本）。

---

## 8. 集群部署要点

| 要点 | 说明 |
|------|------|
| **奇数节点** | 3/5/7，容忍 (N-1)/2 故障 |
| 机器数 | 独立机器，非多进程假集群 |
| JVM 堆 | 4GB 内常见（协调服务非大数据） |
| 磁盘 | 事务日志顺序写，SSD 更佳 |
| 会话超时 | 客户端 `sessionTimeout` 与网络匹配 |

**禁止**：把 ZK 当 **消息队列** 或 **大存储** 用。

---

## 9. 与 Nacos / etcd 对比

| 维度 | ZooKeeper | Nacos | etcd |
|------|-----------|-------|------|
| CAP | CP | AP/CP 可切换 | CP |
| 模型 | 树 + Watcher | 服务+配置+DNS | KV + Watch |
| 生态 | Dubbo、旧 Kafka | Spring Cloud Alibaba | K8s、云原生 |
| 运维 | 较重 | 中等 | 中等 |
| 注册场景 | 逐渐减少 | **主流** | K8s 原生 |

**选型**：

- Spring Cloud 新项目 → **Nacos**
- K8s 控制面 → **etcd**
- 已有 Dubbo + ZK → 维护或迁移 Nacos
- **强一致协调**（锁、选主）且已有 ZK → 继续用 Curator

---

## 10. Dubbo 注册中心流程（ZK 时代）

```
Provider 启动 → 创建 EPHEMERAL 节点 /dubbo/com.xxx.Service/providers/...
Consumer 订阅 → Watcher children 变化 → 更新本地 Invoker 列表
Provider 宕机 → 临时节点删 → Consumer 收到通知剔除
```

现 Dubbo 3 推荐 **Nacos** 作注册中心。

---

## 11. 常见坑

| 坑 | 说明 |
|----|------|
| Watcher 丢失 | 未 re-register；用 Curator Cache |
| 羊群效应 | 大量客户端 watch 同一节点；顺序锁 watch **前一个** 缓解 |
| Session 过期 | GC STW 或网络长断 → 临时节点删 → 锁失效 |
| 节点数据过大 | 性能下降；只存元数据 |
| 不支持递归删除 | 须子节点先删；Curator `deletingChildrenIfNeeded` |

---

## 12. Java 客户端选型

| 客户端 | 说明 |
|--------|------|
| 原生 ZK Client | 底层 API，少用 |
| **Curator** | Netflix，Recipe 丰富，**推荐** |
| zkclient | 老项目 |

---

## 13. 面试题精选

**Q：ZK 为什么适合分布式锁？**  
A：临时顺序节点 + Watcher；会话断开自动释放；全局顺序公平。

**Q：Watcher 为什么一次性？**  
A：减轻服务端压力；客户端收到通知后主动 get 并 re-watch。

**Q：ZK 集群 3 节点挂 1 台还能写吗？**  
A：能，过半（2/3）存活即可选 Leader 并写入。

**Q：ZK 和 Redis 锁选型？**  
A：ZK CP、公平、低 QPS 协调；Redis 高性能，一般业务互斥；强一致敏感看 Redis 专题边界。

---

## 14. 本章小结

- ZK = **树形命名空间 + 临时顺序节点 + Watcher + ZAB**。
- **Curator** 是 Java 标准姿势；理解 **会话与临时节点** 生命周期。
- 注册中心新项目优先 **Nacos**；ZK 重心在 **协调/锁/选主**。

← [05 服务治理](./05-服务治理与灰度.md) · [07 面试题库](./07-生产案例与面试题库.md)
