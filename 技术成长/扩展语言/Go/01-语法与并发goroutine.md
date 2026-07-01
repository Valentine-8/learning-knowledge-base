# 01 · 语法与并发 goroutine

> **预计阅读**：60 min · **难度**：★★★

---

## 1. 基础语法

### 包与导入

```go
package main          // 可执行入口必须是 main

import (
    "fmt"
    "strings"
)
```

### 变量与常量

```go
var name string = "Go"
age := 25              // 短声明，函数内

const Pi = 3.14
const (
    StatusOK = 200
    StatusNotFound = 404
)
```

### 基本类型

| 类型 | 说明 |
|------|------|
| int/int64 | 整数 |
| float64 | 浮点 |
| bool | 布尔 |
| string | UTF-8 字符串 |
| byte | uint8 |
| rune | int32，Unicode 码点 |

---

## 2. 控制流

```go
// if 可带初始化
if err := do(); err != nil {
    return err
}

// for 是唯一循环
for i := 0; i < 10; i++ { }
for _, v := range slice { fmt.Println(v) }
for k, v := range m { fmt.Println(k, v) }

// switch
switch os := runtime.GOOS; os {
case "linux":
    fmt.Println("Linux")
default:
    fmt.Println(os)
}
```

**无 while**：用 `for condition {}`。

---

## 3. 函数

```go
func add(a, b int) int {
    return a + b
}

// 多返回值
func parse(s string) (int, error) {
    n, err := strconv.Atoi(s)
    return n, err
}

// 命名返回值
func split(sum int) (x, y int) {
    x = sum * 4 / 9
    y = sum - x
    return  // naked return
}

// 可变参数
func sum(nums ...int) int { /* ... */ }
```

**函数是一等公民**：可赋值、闭包、作为参数。

---

## 4. 结构体与方法

```go
type Rectangle struct {
    Width, Height float64
}

// 值接收者
func (r Rectangle) Area() float64 {
    return r.Width * r.Height
}

// 指针接收者（可修改、大 struct 避免拷贝）
func (r *Rectangle) Scale(factor float64) {
    r.Width *= factor
    r.Height *= factor
}
```

### 组合（替代继承）

```go
type Animal struct { Name string }
type Dog struct {
    Animal          // embedding
    Breed string
}

d := Dog{Animal: Animal{Name: "Rex"}, Breed: "Lab"}
fmt.Println(d.Name)  // 直接访问嵌入字段
```

---

## 5. 接口

```go
type Writer interface {
    Write(p []byte) (n int, err error)
}

// 任何有 Write 方法的类型都实现了 Writer，无需声明
type FileWriter struct{}
func (f FileWriter) Write(p []byte) (int, error) { return len(p), nil }
```

| 特点 | 说明 |
|------|------|
| 隐式实现 | 鸭子类型 |
| 小接口 | io.Reader、io.Writer 单一方法 |
| 空接口 | `interface{}` / `any`，任意类型 |

```go
func describe(i any) {
    fmt.Printf("type=%T value=%v\n", i, i)
}
```

**类型断言**：

```go
v, ok := i.(string)
switch v := i.(type) {
case int:
    fmt.Println("int", v)
case string:
    fmt.Println("string", v)
}
```

---

## 6. 错误处理

Go **无异常**，用 `error` 接口：

```go
if err != nil {
    return fmt.Errorf("parse failed: %w", err)  // Go 1.13+ wrap
}

// errors.Is / errors.As
if errors.Is(err, os.ErrNotExist) { }
```

| 对比 Java | Go |
|-----------|-----|
| try/catch | if err != nil |
| RuntimeException | panic（仅真正异常，少用） |
| 调用栈 | fmt.Errorf %w 链 |

---

## 7. goroutine

```go
go func() {
    fmt.Println("async")
}()

// WaitGroup 等待
var wg sync.WaitGroup
for i := 0; i < 5; i++ {
    wg.Add(1)
    go func(id int) {
        defer wg.Done()
        work(id)
    }(i)  // 注意闭包捕获，传参
}
wg.Wait()
```

| 对比 | Java Thread | goroutine |
|------|-------------|-----------|
| 内存 | ~1MB | ~2KB 栈起 |
| 创建成本 | 高 | 低 |
| 调度 | OS 线程 | Go runtime M:N |

---

## 8. channel

```go
ch := make(chan int)       // 无缓冲，同步
buf := make(chan int, 10)  // 有缓冲

// 发送接收
ch <- 42
v := <-ch

// 关闭
close(ch)
for v := range ch { fmt.Println(v) }  // 直到关闭

// select 多路复用
select {
case msg := <-ch1:
    handle(msg)
case ch2 <- value:
    // sent
default:
    // 非阻塞
}
```

**模式**：

| 模式 | 用法 |
|------|------|
| 生产者消费者 | channel 传递 |
| 扇出扇入 | 多 goroutine 读同一 channel |
| 超时 | select + time.After |
| 退出信号 | done channel / context |

---

## 9. sync 包

```go
var mu sync.Mutex
mu.Lock()
defer mu.Unlock()
// 临界区

var once sync.Once
once.Do(func() { initDB() })

pool := sync.Pool{ New: func() any { return make([]byte, 1024) } }
```

---

## 10. context（跨 goroutine 取消）

```go
ctx, cancel := context.WithTimeout(context.Background(), 3*time.Second)
defer cancel()

select {
case <-ctx.Done():
    return ctx.Err()
case result := <-doWork():
    return result
}
```

HTTP 请求、RPC 传递 `context.Context` 做超时和取消。

---

## 11. 小结

| 要点 | 一句话 |
|------|--------|
| 错误 | if err != nil，不用 try/catch |
| 接口 | 隐式实现，小接口组合 |
| goroutine | 轻量并发，注意闭包捕获 |
| channel | 通信共享内存，CSP 模型 |

---

← [00 速查](./00-速查总览.md) · [02 HTTP 服务 →](./02-标准库与HTTP服务.md)
