# 04 · Java 与 Spring gRPC 实战

> **预计阅读**：60 min · **难度**：★★★★

---

## 1. 项目结构

```
order-service/
├── src/main/proto/order.proto
├── src/main/java/.../OrderGrpcService.java
└── pom.xml

order-client/
└── 依赖 generated stub + @GrpcClient
```

---

## 2. 服务端（grpc-spring-boot-starter）

```yaml
grpc:
  server:
    port: 9090
    enable-reflection: true   # 开发 grpcurl 反射
```

```java
@GrpcService
@Slf4j
public class OrderGrpcService extends OrderServiceGrpc.OrderServiceImplBase {

    private final OrderApplicationService orderApp;

    @Override
    public void getOrder(GetOrderRequest request,
                         StreamObserver<OrderResponse> responseObserver) {
        try {
            Order dto = orderApp.getById(request.getOrderId());
            responseObserver.onNext(toProto(dto));
            responseObserver.onCompleted();
        } catch (NotFoundException e) {
            responseObserver.onError(
                Status.NOT_FOUND.withDescription(e.getMessage()).asRuntimeException());
        }
    }
}
```

**与 Spring MVC 并存**：HTTP 8080 + gRPC 9090。

---

## 3. 客户端

```yaml
grpc:
  client:
    order-service:
      address: static://127.0.0.1:9090
      negotiationType: plaintext
```

```java
@Service
public class PaymentClient {
    @GrpcClient("order-service")
    private OrderServiceGrpc.OrderServiceBlockingStub orderStub;

    public Order getOrder(long id) {
        return fromProto(orderStub.getOrder(
            GetOrderRequest.newBuilder().setOrderId(id).build()));
    }
}
```

---

## 4. 拦截器（Metadata / 鉴权）

```java
public class AuthServerInterceptor implements ServerInterceptor {
    @Override
    public <ReqT, RespT> ServerCall.Listener<ReqT> interceptCall(
            ServerCall<ReqT, RespT> call, Metadata headers,
            ServerCallHandler<ReqT, RespT> next) {
        String token = headers.get(Metadata.Key.of("authorization", Metadata.ASCII_STRING_MARSHALLER));
        if (!valid(token)) {
            call.close(Status.UNAUTHENTICATED.withDescription("bad token"), new Metadata());
            return new ServerCall.Listener<>() {};
        }
        return next.startCall(call, headers);
    }
}
```

客户端传 Metadata：

```java
Metadata meta = new Metadata();
meta.put(KEY, "Bearer " + token);
stub.withInterceptors(MetadataUtils.newAttachHeadersInterceptor(meta)).getOrder(req);
```

**traceId**：从 Sleuth/Micrometer 注入 Metadata，与 HTTP 链路统一。

---

## 5. 异常与全局处理

```java
@GrpcAdvice
public class GrpcExceptionHandler {

    @GrpcExceptionHandler(IllegalArgumentException.class)
    public Status handle(IllegalArgumentException e) {
        return Status.INVALID_ARGUMENT.withDescription(e.getMessage());
    }
}
```

---

## 6. 与 Nacos 集成

gRPC 服务也注册到 Nacos（**元数据标明 gRPC 端口**）：

```yaml
spring:
  cloud:
    nacos:
      discovery:
        metadata:
          gRPC_port: 9090
```

客户端用 **NacosNameResolver** 或 grpc-spring 的 `discovery://order-service`。

---

## 7. 测试

```java
@GrpcClient("inProcess")
private OrderServiceGrpc.OrderServiceBlockingStub stub;

// 或 Testcontainers + grpcurl
// grpcurl -plaintext localhost:9090 list
```

---

## 8. REST 与 gRPC 共存策略

| 边界 | 协议 |
|------|------|
| 移动端 / 第三方 | REST via Gateway |
| 服务间 | gRPC |
| BFF | HTTP 聚合，内部 gRPC |

**Anti-corruption**：DTO（REST）与 Proto 分层转换，勿一套对象两用。

---

→ [05-治理超时重试与网关](./05-治理超时重试与网关.md)

← [03-四种通信模式](./03-四种通信模式.md)
