# 03 · 与 Java 对比与云原生

> **预计阅读**：50 min · **难度**：★★★

---

## 1. 语言哲学对比

| 维度 | Java | Go |
|------|------|-----|
| 范式 | OOP 为主 | 组合 + 接口 |
| 泛型 | 成熟（17+） | 1.18+ 基础泛型 |
| 反射 | 强大 | 有，较少用 |
| 注解 | 广泛使用 | 无，代码生成/struct tag |
| 依赖注入 | Spring 标配 | 手动/wire/fx |
| 框架 | Spring 全家桶 | 标准库 + 轻量框架 |

Go 倾向 **显式、简单、少魔法**。

---

## 2. 并发模型对比

| Java | Go |
|------|-----|
| Thread / ExecutorService | goroutine |
| synchronized / Lock | sync.Mutex / channel |
| CompletableFuture | goroutine + channel |
| Virtual Thread（21+） | goroutine 原生轻量 |

```java
// Java 虚拟线程（类似 goroutine 方向）
ExecutorService executor = Executors.newVirtualThreadPerTaskExecutor();
executor.submit(() -> doWork());
```

Go CSP：**不要通过共享内存通信，而要通过通信共享内存**。

---

## 3. 内存与 GC

| | Java | Go |
|---|------|-----|
| 堆 | 大，可调 -Xmx | 通常更小 |
| 启动 | 慢（JVM 预热） | 毫秒～百毫秒 |
| 二进制 | JAR + JRE | **单静态二进制** |
| 交叉编译 | 需目标 JRE | `GOOS=linux GOARCH=amd64 go build` |

**容器场景**：Go 镜像可 scratch 几 MB；Java 需 JRE 100MB+。

---

## 4. 错误 vs 异常

```java
// Java
try {
    user = userService.find(id);
} catch (NotFoundException e) {
    return Response.notFound();
}
```

```go
user, err := userService.Find(id)
if errors.Is(err, ErrNotFound) {
    http.NotFound(w, r)
    return
}
if err != nil {
    http.Error(w, err.Error(), 500)
    return
}
```

Go 代码 **if err != nil 多**，但控制流清晰。

---

## 5. 云原生 Go 项目

| 项目 | 作用 |
|------|------|
| Docker/Moby | 容器 |
| Kubernetes | 编排 |
| containerd | 运行时 |
| etcd | K8s 存储 |
| Prometheus | 监控 |
| Grafana | 可视化 |
| Helm | K8s 包管理 |
| Istio/Envoy（部分） | 服务网格 |
| Terraform | IaC |
| CockroachDB、TiDB | 分布式数据库 |

**读 K8s/Docker 源码**：Java 工程师学 Go 的最大动力。

---

## 6. 何时用 Go 替 Java

| 适合 Go | 继续 Java |
|---------|-----------|
| CLI、Operator | 复杂业务 CRUD |
| 网关、Sidecar | Spring 生态集成 |
| 高并发 Agent | 大量第三方 Java 库 |
| 小微服务、Job | 团队只会 Java |
| 内存/启动敏感 | 成熟事务、ORM |

---

## 7. 写一个 K8s Operator（概念）

```go
// controller-runtime 伪代码
func (r *AppReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
    var app myv1.App
    if err := r.Get(ctx, req.NamespacedName, &app); err != nil {
        return ctrl.Result{}, client.IgnoreNotFound(err)
    }
    // 调谐：Deployment/Service 与 App CR 一致
    return ctrl.Result{RequeueAfter: time.Minute}, nil
}
```

Java 也有 Fabric8 Operator SDK，但 Go 是主流。

---

## 8. 学习路径（Java 开发者）

| 周 | 内容 |
|----|------|
| 1 | 语法、error、struct、interface |
| 2 | goroutine、channel、context |
| 3 | net/http、JSON、测试 |
| 4 | 读一个 Go 小项目（如 minio、cobra CLI） |
| 5 | 写运维 CLI 或 K8s 健康检查 Sidecar |

---

## 9. 工具链

```bash
go fmt ./...           # 格式化
go vet ./...           # 静态检查
golangci-lint run      # linter 集合
delve debug            # 调试器
```

IDE：GoLand、VS Code + Go 插件。

---

## 10. 小结

| 要点 | 一句话 |
|------|--------|
| 定位 | Go 补位云原生/工具，Java 扛业务 |
| 优势 | 单二进制、快启动、并发简单 |
| 生态 | K8s 周边读 Go 源码 |
| 学习 | 4～5 周可写小服务 |

---

← [02 HTTP 服务](./02-标准库与HTTP服务.md) · [04 生产案例 →](./04-生产案例与面试题库.md)
