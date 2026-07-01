# 02 · 节点类型与 Watch

> **预计阅读**：50 min · **难度**：★★★

---

## 1. 四种节点类型

| 类型 | create 参数 | 行为 |
|------|-------------|------|
| 持久 PERSISTENT | 默认 | 客户端断开仍存在，需 delete |
| 临时 EPHEMERAL | `-e` | Session 结束自动删除 |
| 持久顺序 PERSISTENT_SEQUENTIAL | `-s` | 持久 + 自动序号后缀 |
| 临时顺序 EPHEMERAL_SEQUENTIAL | `-e -s` | 临时 + 自动序号后缀 |

```bash
create /config/db "jdbc:..."                    # 持久
create -e /services/192.168.1.10 "8080"         # 临时
create -e -s /locks/order ""                    # 临时顺序 → /locks/order0000000001
create -s /tasks/job ""                         # 持久顺序
```

---

## 2. 各类型的典型用途

| 类型 | 场景 |
|------|------|
| 持久 | 配置数据、元数据 |
| 临时 | 服务实例注册（宕机自动摘除） |
| 持久顺序 | 任务队列、全局唯一序号 |
| 临时顺序 | **分布式锁**、Leader 选举 |

**服务注册示例**：

```
/services/order-service/          ← 持久父节点
/services/order-service/
    ├── 192.168.1.10:8080-0000000001   ← 临时顺序，data=实例详情 JSON
    └── 192.168.1.11:8080-0000000002
```

Consumer `ls /services/order-service` 获取所有存活实例。

---

## 3. 顺序节点序号

- 10 位数字后缀，如 `lock-0000000003`
- 全局递增（每个父节点下独立计数）
- 用于 **公平锁**：序号最小者获得锁

---

## 4. Watch 机制

Watch 是 ZK **核心特性**：客户端在 ZNode 上注册监听，变化时收到 **一次性** 通知。

### 四种事件

| 事件 | 触发条件 |
|------|----------|
| NodeCreated | 节点创建 |
| NodeDeleted | 节点删除 |
| NodeDataChanged | 数据变更 |
| NodeChildrenChanged | 子节点增删 |

### 注册方式

```bash
get -w /config/app      # 监听该节点数据变化 + 删除
ls -w /services         # 监听子节点列表变化
```

**Java Curator**：

```java
client.getData().usingWatcher(watcher).forPath("/config/app");

// 推荐：CuratorCache 自动重注册
CuratorCache cache = CuratorCache.build(client, "/config");
cache.listenable().addListener((type, oldData, data) -> {
    if (type == CuratorCacheListener.Type.NODE_CHANGED) {
        reloadConfig(data.getData());
    }
});
cache.start();
```

---

## 5. Watch 重要特性

| 特性 | 说明 |
|------|------|
| **一次性** | 触发后失效，需重新 get -w |
| **轻量通知** | 只告知「变了」，不推送新数据 |
| **有序** | 客户端回调按 zxid 顺序 |
| **延迟** | 非实时，通常毫秒级 |
| **累积** | 同一节点多个 Watch 各自独立 |

**为何一次性？** 防止客户端大量 Watch 不消费导致 ZK 内存和通知队列膨胀。

---

## 6. Watch 经典模式 — 配置热更新

```
1. Client get /config/app 并 setWatcher
2. 配置变更 → NodeDataChanged 通知
3. Client 再次 get /config/app（获取新值 + 重新注册 Watch）
4. 应用新配置
```

**坑**：处理配置变更逻辑中若抛异常未重新注册 Watch，后续变更收不到。

**CuratorCache / TreeCache** 封装了自动重注册，生产推荐。

---

## 7. Watch 与临时节点联动

```
服务 A 注册临时节点 /services/app/instance-A
Consumer 对 /services/app 设 ChildWatch

A 宕机 → Session 超时 → 临时节点删 → NodeChildrenChanged
→ Consumer 重新 ls 获取最新实例列表
```

这是 Dubbo 等 **服务发现** 的经典模式（现多被 Nacos 替代，原理类似）。

---

## 8. 版本号与 CAS

`set` 和 `delete` 支持 **version** 参数，实现乐观锁：

```bash
get /config/app
# version = 3
set /config/app "new-value" 3    # 成功
set /config/app "other" 3        # 失败，version 已变 4
```

Java：

```java
client.setData().withVersion(stat.getVersion()).forPath(path, data);
// 抛出 KeeperException.BadVersionException 则需重试
```

---

## 9. 常见反模式

| 反模式 | 问题 |
|--------|------|
| 把 ZK 当消息队列大量写 | 吞吐低，Watcher 风暴 |
| 不处理 Watch 重注册 | 漏事件 |
| 大 payload | 单节点 1MB 限制，网络开销 |
| 过多临时节点 | Session 多，内存压力 |
| 递归深度过大 | 路径管理混乱 |

---

## 10. 小结

| 要点 | 一句话 |
|------|--------|
| 临时节点 | Session 生命周期，服务注册标配 |
| 顺序节点 | 公平锁、全局序号 |
| Watch | 一次性，需重注册或用 CuratorCache |
| version | CAS 防并发覆盖 |

---

← [01 核心概念与 ZAB](./01-核心概念与ZAB.md) · [03 分布式锁 →](./03-分布式锁与选主.md)
