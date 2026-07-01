# 02 · 标准库与 HTTP 服务

> **预计阅读**：60 min · **难度**：★★★

---

## 1. 常用标准库

| 包 | 用途 |
|----|------|
| fmt | 格式化 I/O |
| strings / strconv | 字符串 |
| encoding/json | JSON |
| os / io | 文件 I/O |
| net/http | HTTP 客户端/服务端 |
| context | 超时取消 |
| time | 时间 |
| log / log/slog | 日志（Go 1.21+ slog 结构化） |
| testing | 单元测试 |
| sync | 并发原语 |

---

## 2. JSON 处理

```go
type User struct {
    ID   int64  `json:"id"`
    Name string `json:"name"`
    Email string `json:"email,omitempty"`
}

// 序列化
data, err := json.Marshal(user)

// 反序列化
var u User
err := json.Unmarshal(data, &u)

// 流式 Encoder/Decoder（大 JSON）
enc := json.NewEncoder(w)
enc.Encode(user)
```

| tag | 说明 |
|-----|------|
| `json:"name"` | 字段名 |
| `omitempty` | 零值省略 |
| `-` | 忽略 |

---

## 3. net/http 基础服务

```go
package main

import (
    "encoding/json"
    "log"
    "net/http"
)

type HealthResponse struct {
    Status string `json:"status"`
}

func healthHandler(w http.ResponseWriter, r *http.Request) {
    if r.Method != http.MethodGet {
        http.Error(w, "method not allowed", http.StatusMethodNotAllowed)
        return
    }
    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(HealthResponse{Status: "UP"})
}

func main() {
    http.HandleFunc("/health", healthHandler)
    log.Fatal(http.ListenAndServe(":8080", nil))
}
```

---

## 4. 自定义 ServeMux（Go 1.22+）

```go
mux := http.NewServeMux()
mux.HandleFunc("GET /users/{id}", getUser)
mux.HandleFunc("POST /users", createUser)

server := &http.Server{
    Addr:         ":8080",
    Handler:      mux,
    ReadTimeout:  5 * time.Second,
    WriteTimeout: 10 * time.Second,
    IdleTimeout:  60 * time.Second,
}
log.Fatal(server.ListenAndServe())
```

---

## 5. 中间件模式

```go
func loggingMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        start := time.Now()
        next.ServeHTTP(w, r)
        log.Printf("%s %s %v", r.Method, r.URL.Path, time.Since(start))
    })
}

func main() {
    mux := http.NewServeMux()
    mux.HandleFunc("/api/", apiHandler)
    handler := loggingMiddleware(mux)
    http.ListenAndServe(":8080", handler)
}
```

类似 Java Servlet Filter / Spring Interceptor。

---

## 6. HTTP 客户端

```go
client := &http.Client{ Timeout: 10 * time.Second }

req, _ := http.NewRequestWithContext(ctx, "GET", "http://api/users/1", nil)
req.Header.Set("Authorization", "Bearer token")

resp, err := client.Do(req)
if err != nil { return err }
defer resp.Body.Close()

body, _ := io.ReadAll(resp.Body)
```

---

## 7. 流行 Web 框架（了解）

| 框架 | 特点 |
|------|------|
| net/http | 标准库，够用 |
| gin | 高性能，国内流行 |
| echo | 简洁 |
| fiber | 类 Express |
| chi | 轻量路由 |

```go
// Gin 示例
r := gin.Default()
r.GET("/users/:id", func(c *gin.Context) {
    id := c.Param("id")
    c.JSON(200, gin.H{"id": id})
})
r.Run(":8080")
```

小工具/Agent 用标准库；业务 API 可选 Gin。

---

## 8. 数据库访问

```go
import "database/sql"
import _ "github.com/go-sql-driver/mysql"

db, err := sql.Open("mysql", "user:pass@tcp(localhost:3306)/shop")
db.SetMaxOpenConns(25)
db.SetMaxIdleConns(5)

row := db.QueryRow("SELECT name FROM users WHERE id = ?", id)
var name string
err = row.Scan(&name)
```

ORM：**GORM**（类似 JPA，但 Go 风格）。

---

## 9. 测试

```go
func TestAdd(t *testing.T) {
    got := add(2, 3)
    if got != 5 {
        t.Errorf("add(2,3) = %d; want 5", got)
    }
}

// 表驱动测试
func TestParse(t *testing.T) {
    cases := []struct{ in, want string }{
        {"hello", "HELLO"},
    }
    for _, c := range cases {
        if got := strings.ToUpper(c.in); got != c.want {
            t.Errorf("got %s want %s", got, c.want)
        }
    }
}
```

```bash
go test ./...
go test -cover ./...
go test -bench=. ./...
```

**httptest**：

```go
req := httptest.NewRequest("GET", "/health", nil)
rec := httptest.NewRecorder()
healthHandler(rec, req)
if rec.Code != 200 { t.Fatal() }
```

---

## 10. 项目布局（标准）

```
myproject/
├── go.mod
├── go.sum
├── cmd/
│   └── server/
│       └── main.go      # 入口
├── internal/            # 私有包
│   ├── handler/
│   ├── service/
│   └── repository/
└── pkg/                 # 可对外暴露
```

---

## 11. 小结

| 要点 | 一句话 |
|------|--------|
| net/http | 标准库可写生产 API |
| 中间件 | Handler 包装链 |
| JSON | struct tag + Marshal |
| 测试 | 表驱动 + httptest |

---

← [01 语法并发](./01-语法与并发goroutine.md) · [03 Java 对比 →](./03-与Java对比与云原生.md)
