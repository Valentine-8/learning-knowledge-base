# 02 · Protobuf 语法与演进

> **预计阅读**：60 min · **难度**：★★★★

---

## 1. 基本语法 proto3

```protobuf
syntax = "proto3";

package demo.v1;

option java_package = "com.example.demo.v1";
option java_multiple_files = true;

message User {
  int64 id = 1;
  string name = 2;
  string email = 3;
  repeated string roles = 4;
  optional int32 age = 5;   // proto3 optional 显式可选
  map<string, string> attrs = 6;
}

enum Status {
  STATUS_UNSPECIFIED = 0;  // 枚举必须有 0
  STATUS_ACTIVE = 1;
  STATUS_DISABLED = 2;
}
```

---

## 2. 字段编号规则（版本兼容核心）

| 规则 | 说明 |
|------|------|
| 1～15 | 1 字节 tag，常用字段 |
| 16～2047 | 2 字节 tag |
| **永不复用已删除字段的编号** | 防旧数据解析错 |
| 新增字段 | 旧客户端 **忽略未知字段** |
| 删除字段 | `reserved 3, 5;` 或 `reserved "old_field";` |

```protobuf
message Order {
  reserved 2, 3;
  reserved "legacy_field";
  int64 id = 1;
  string status = 4;  // 新字段用新号
}
```

---

## 3. 类型映射（Java）

| Protobuf | Java |
|----------|------|
| int32/int64 | int / long |
| string | String |
| bool | boolean |
| bytes | ByteString |
| repeated T | List\<T\> |
| map<K,V> | Map\<K,V\> |
| message | 自定义类 |

**时间**：用 `google.protobuf.Timestamp` 或 int64 epoch_millis（约定）。

```protobuf
import "google/protobuf/timestamp.proto";

message Event {
  google.protobuf.Timestamp created_at = 1;
}
```

---

## 4. Service 定义

```protobuf
service UserService {
  rpc CreateUser(CreateUserRequest) returns (User);
  rpc GetUser(GetUserRequest) returns (User);
}
```

生成：

- `UserServiceGrpc.UserServiceImplBase` — 服务端继承
- `UserServiceGrpc.newBlockingStub(channel)` — 客户端

---

## 5. Well-Known Types

| 类型 | 用途 |
|------|------|
| Empty | 无参/无返回 |
| Any | 泛型包装 |
| Struct / Value | 动态 JSON 结构 |
| Timestamp / Duration | 时间间隔 |

---

## 6. 编译与 Maven

```xml
<plugin>
  <groupId>org.xolstice.maven.plugins</groupId>
  <artifactId>protobuf-maven-plugin</artifactId>
  <configuration>
    <protocArtifact>com.google.protobuf:protoc:3.25.1:exe:${os.detected.classifier}</protocArtifact>
    <pluginId>grpc-java</pluginId>
    <pluginArtifact>io.grpc:protoc-gen-grpc-java:1.60.0:exe:${os.detected.classifier}</pluginArtifact>
  </configuration>
</plugin>
```

`src/main/proto` 下 `.proto` → `target/generated-sources/protobuf`.

---

## 7. JSON 互转（网关场景）

Protobuf 与 JSON 映射规则（字段名 camelCase 可配）：

```java
String json = JsonFormat.printer().print(message);
User.Builder builder = User.newBuilder();
JsonFormat.parser().merge(json, builder);
```

用于 **grpc-gateway** 或调试。

---

## 8. 常见错误

| 错误 | 后果 |
|------|------|
| 改字段类型同号 | 解析错乱 |
| 复用 field number |  silent data corruption |
| 枚举从 1 开始 | 不符合 proto3 规范 |
| 超大 message | 默认 4MB 限制，需调 `maxInboundMessageSize` |

---

→ [03-四种通信模式](./03-四种通信模式.md)

← [01-核心概念与架构](./01-核心概念与架构.md)
