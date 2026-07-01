# 04 Stream API 与 Java 新特性

> **目标**：熟练运用 Stream/Optional/java.time，理解 Java 8→21 演进，能在架构评审中评估新特性收益与风险。

---

## 一、Lambda 与函数式接口

### 1.1 Lambda 本质

Lambda 是 **函数式接口的实例**（SAM：Single Abstract Method），编译为 `invokedynamic` + LambdaMetafactory 生成字节码。

```java
Comparator<String> cmp = (a, b) -> a.length() - b.length();
// 等价于匿名类，但无额外 class 文件
```

### 1.2 常用函数式接口

| 接口 | 方法 | 用途 |
|------|------|------|
| `Function<T,R>` | apply | 转换 |
| `Consumer<T>` | accept | 消费 |
| `Supplier<T>` | get | 供给 |
| `Predicate<T>` | test | 判断 |
| `BiFunction<T,U,R>` | apply | 双参转换 |

**方法引用**：

```java
list.forEach(System.out::println);
list.sort(String::compareToIgnoreCase);
```

### 1.3 闭包与变量捕获

Lambda 只能引用 **effectively final** 的局部变量；捕获的是值副本，不是变量本身。

---

## 二、Stream 基础

### 2.1 创建 Stream

```java
Stream.of(1, 2, 3);
list.stream();
list.parallelStream();
IntStream.range(0, 100);
Files.lines(path);
Stream.iterate(0, n -> n + 1).limit(100);
Stream.generate(Math::random).limit(10);
```

### 2.2 操作分类

**中间操作**（lazy，返回 Stream）：
- filter、map、flatMap、distinct、sorted、peek、limit、skip

**终端操作**（触发计算）：
- forEach、collect、reduce、count、min/max、findFirst、anyMatch

```java
List<String> result = orders.stream()
    .filter(o -> o.getStatus() == PAID)
    .map(Order::getCustomerName)
    .distinct()
    .sorted()
    .collect(Collectors.toList());
```

### 2.3 惰性求值

```java
Stream<Integer> s = Stream.of(1, 2, 3, 4, 5)
    .filter(n -> {
        System.out.println("filter " + n);
        return n % 2 == 0;
    });
// 此时无输出
s.forEach(n -> System.out.println("forEach " + n));
```

**短路**：`findFirst`、`anyMatch`、`limit` 可不必处理全部元素。

---

## 三、flatMap 与复杂转换

```java
List<OrderItem> allItems = orders.stream()
    .flatMap(o -> o.getItems().stream())
    .collect(Collectors.toList());
```

**Optional.flatMap** 同理，避免嵌套 Optional。

**规则**：一层结构用 map，展开集合用 flatMap。

---

## 四、Collectors 高级用法

### 4.1 groupingBy

```java
Map<Status, List<Order>> byStatus = orders.stream()
    .collect(Collectors.groupingBy(Order::getStatus));

Map<Status, Long> countByStatus = orders.stream()
    .collect(Collectors.groupingBy(Order::getStatus, Collectors.counting()));
```

### 4.2 多级分组

```java
Map<YearMonth, Map<Status, Double>> revenue = orders.stream()
    .collect(Collectors.groupingBy(
        o -> YearMonth.from(o.getCreatedAt()),
        Collectors.groupingBy(
            Order::getStatus,
            Collectors.summingDouble(Order::getAmount)
        )
    ));
```

### 4.3 toMap 陷阱

```java
// 重复 key 抛 IllegalStateException
Map<Long, Order> map = orders.stream()
    .collect(Collectors.toMap(Order::getId, Function.identity()));

// 指定 merge
.collect(Collectors.toMap(Order::getId, Function.identity(), (a, b) -> a));

// value 为 null 会 NPE（HashMap.merge 限制）
```

### 4.4 joining、summarizing

```java
String names = list.stream().collect(Collectors.joining(", ", "[", "]"));
DoubleSummaryStatistics stats = list.stream()
    .collect(Collectors.summarizingDouble(Order::getAmount));
```

---

## 五、reduce 与 collect 选型

```java
Optional<Integer> sum = numbers.stream().reduce(Integer::sum);

BigDecimal total = orders.stream()
    .map(Order::getAmount)
    .reduce(BigDecimal.ZERO, BigDecimal::add);
```

**mutable reduction**：`Collectors.toList()` 用容器累加，通常比 reduce 拼接 immutable 结构更高效。

---

## 六、Parallel Stream

### 6.1 机制

- 默认 **ForkJoinPool.commonPool()**
- 并行度 ≈ `Runtime.getRuntime().availableProcessors() - 1`
- 数据源需 **Spliterator** 可拆分（ArrayList 好，LinkedList 差）

### 6.2 适用条件

- 数据量大（通常 10万+ 元素才值得）
- 单元素计算 **CPU 密集** 且无共享 mutable 状态
- 无 IO、无锁竞争

### 6.3 反模式

```java
// 错误：并发修改共享变量
List<Integer> bad = new ArrayList<>();
list.parallelStream().forEach(bad::add);  // 线程不安全

// 错误：IO 在 parallelStream
list.parallelStream().map(id -> httpClient.get(id)).collect(toList());

// 错误：小集合
Arrays.asList(1,2,3).parallelStream()...
```

### 6.4 自定义 ForkJoinPool（Java 8+）

```java
ForkJoinPool pool = new ForkJoinPool(4);
try {
    pool.submit(() ->
        list.parallelStream().map(heavy).collect(toList())
    ).get();
} finally {
    pool.shutdown();
}
```

避免占用 common pool 影响其他并行 Stream。

---

## 七、Optional

### 7.1 正确用法

```java
return userRepository.findById(id)
    .map(User::getEmail)
    .orElseThrow(() -> new NotFoundException("user"));
```

### 7.2 反模式

| 反模式 | 问题 |
|--------|------|
| `Optional.of(nullable)` | NPE，用 ofNullable |
| 字段类型 Optional | 序列化、内存开销 |
| `get()` 不检查 | 不如 orElseThrow |
| 层层 Optional 嵌套 | 用 flatMap |
| 仅为避免 if-null | 过度设计 |

### 7.3 Java 9+ 增强

```java
optional.ifPresentOrElse(v -> log.info("{}", v), () -> log.warn("empty"));
optional.stream();  // 转 Stream，filter 链
optional.or(() -> alternative);
```

---

## 八、java.time

### 8.1 核心类型

| 类型 | 用途 |
|------|------|
| Instant | UTC 时间戳，跨系统 |
| LocalDate / LocalTime / LocalDateTime | 无时区日历时间 |
| ZonedDateTime | 带时区 |
| Duration | 时间间隔 |
| Period | 日期间隔 |

### 8.2 时区规范

```java
// 存储：UTC Instant 或 DB timestamp with time zone
Instant now = Instant.now();

// 展示：按用户时区
ZonedDateTime shanghai = now.atZone(ZoneId.of("Asia/Shanghai"));

// 解析必须带时区或明确 Local
ZonedDateTime.parse("2024-01-01T10:00:00+08:00[Asia/Shanghai]");
```

**反模式**：`new Date()`、`SimpleDateFormat`（线程不安全）；数据库用 `DATETIME` 丢时区。

### 8.3 与旧 API 互转

```java
Date date = Date.from(instant);
Instant instant = date.toInstant();
```

---

## 九、Java 9～11 精选

### 9.1 模块系统（JPMS）

```
module com.example.app {
    requires java.logging;
    exports com.example.api;
}
```

**后端影响**：JDK 内部 API 不可随意访问；反射需 `--add-opens`；fat jar 需 jlink 或 classpath 兼容。

### 9.2 var 局部变量（10）

```java
var list = new ArrayList<String>();  // 推断为 ArrayList<String>
// 禁止：字段、方法参数、lambda 无显式类型处滥用
```

### 9.3 HttpClient（11）

```java
HttpClient client = HttpClient.newBuilder()
    .connectTimeout(Duration.ofSeconds(5))
    .build();
HttpRequest req = HttpRequest.newBuilder(URI.create("https://api.example.com"))
    .timeout(Duration.ofSeconds(10))
    .GET()
    .build();
HttpResponse<String> resp = client.send(req, HttpResponse.BodyHandlers.ofString());
```

支持 HTTP/2、异步 sendAsync；生产可替代 Apache HttpClient（视生态而定）。

### 9.4 集合工厂方法

```java
List.of(1, 2, 3);       // 不可变
Map.of("k", "v");       // 最多 10 对
Set.copyOf(existingSet);
```

---

## 十、Java 14～17

### 10.1 Record（16 正式）

```java
public record Point(int x, int y) {
    public Point {
        if (x < 0 || y < 0) throw new IllegalArgumentException();
    }
}
```

- 自动生成 constructor、equals、hashCode、toString、accessor
- **不可变**；不能继承类；可实现接口
- 适合 DTO、Value Object、事件消息

**限制**：JPA Entity 慎用（需无参构造、lazy 字段）；Jackson 需模块或配置。

### 10.2 Sealed Class（17）

```java
public sealed interface Payment permits CreditPayment, WalletPayment { }

public final class CreditPayment implements Payment { }
public non-sealed class WalletPayment implements Payment { }
```

**用途**：领域模型穷举分支；配合 Pattern Matching  exhaustive。

### 10.3 Pattern Matching（17+ 逐步完善）

```java
if (obj instanceof String s && !s.isEmpty()) {
    System.out.println(s.toUpperCase());
}

// switch 21 preview 增强
switch (payment) {
    case CreditPayment c -> processCredit(c);
    case WalletPayment w -> processWallet(w);
}
```

### 10.4 Text Blocks（15）

```java
String sql = """
    SELECT id, name
    FROM users
    WHERE status = 'ACTIVE'
    """;
```

---

## 十一、Java 21 重点

### 11.1 Virtual Thread

```java
Thread.startVirtualThread(() -> service.handle(request));

try (var ex = Executors.newVirtualThreadPerTaskExecutor()) {
    List<Future<Result>> futures = tasks.stream()
        .map(t -> ex.submit(() -> process(t)))
        .toList();
}
```

**Spring Boot 3.2+**：`spring.threads.virtual.enabled=true`

### 11.2 Structured Concurrency（Preview）

```java
try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
    Subtask<User> user = scope.fork(() -> fetchUser(id));
    Subtask<Orders> orders = scope.fork(() -> fetchOrders(id));
    scope.join();
    scope.throwIfFailed();
    return combine(user.get(), orders.get());
}
```

子任务生命周期绑定父作用域，取消/失败传播更清晰。

### 11.3 Sequenced Collections

```java
SequencedCollection<String> seq = new ArrayList<>();
seq.addFirst("a");
seq.addLast("b");
seq.reversed();
```

统一首尾访问 API。

---

## 十二、新特性落地建议

| 特性 | 建议 |
|------|------|
| Record | API 响应 DTO、Domain 值对象 |
| var | 局部变量类型明显冗长时 |
| Stream | 集合转换；复杂逻辑拆 private 方法 |
| Parallel Stream | 默认不用，Profiler 证明 CPU 瓶颈再用 |
| Virtual Thread | IO 密集微服务、批量 HTTP 调用 |
| Module | 库作者优先；业务 monolith 可暂缓 |

**升级路径**：8 → 11 → 17 LTS → 21 LTS；每步跑全量测试 + 依赖兼容性矩阵。

---

## 十三、Stream 调试技巧

```java
.peek(o -> log.debug("after filter: {}", o))  // 仅调试，生产删除
```

**更好的方式**：拆步骤、单元测试中间结果；IntelliJ Stream Trace。

---

## 十四、与并发交叉

- Stream **不是**并发工具；parallelStream 与线程池隔离
- CompletableFuture + Stream 编排异步：

```java
List<CompletableFuture<Result>> futures = ids.stream()
    .map(id -> CompletableFuture.supplyAsync(() -> fetch(id), executor))
    .toList();
CompletableFuture.allOf(futures.toArray(new CompletableFuture[0])).join();
```

---

## 十五、面试自测

1. Stream 中间操作为何 lazy？
2. Collectors.toMap 重复 key 如何处理？
3. Parallel Stream 默认线程池是什么？
4. Optional 作为字段为什么不好？
5. Record 与 Lombok @Value 区别？
6. Virtual Thread 适合 CPU 密集吗？

---

## 十六、迁移 checklist

- [ ] 依赖库支持目标 JDK
- [ ] 移除 illegal reflective access
- [ ] JAXB/JavaEE 模块单独引入
- [ ] CI 多 JDK 矩阵测试
- [ ] 容器基础镜像升级（eclipse-temurin:21-jre）
- [ ] GC 选型（G1 → ZGC 评估）
- [ ] 监控 Agent 兼容（SkyWalking、Arthas）

---

← [上一章：BIO-NIO与Netty](./03-BIO-NIO与Netty.md) · [目录](./README.md) · 下一章：[05-面试题库与案例](./05-面试题库与案例.md)
