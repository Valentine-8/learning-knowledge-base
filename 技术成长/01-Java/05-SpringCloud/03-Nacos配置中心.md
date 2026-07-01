# 03 · Nacos 配置中心

> **预计阅读**：50 min · **难度**：★★★★

---

## 1. 为什么需要配置中心

| 痛点 | 配置中心 |
|------|----------|
| 改配置要重启 | **动态刷新** |
| 多环境 yaml 散乱 | 集中管理 |
| 敏感信息 | 加密、权限 |
| 变更审计 | 历史版本、回滚 |

---

## 2. 接入

```xml
<dependency>
  <groupId>com.alibaba.cloud</groupId>
  <artifactId>spring-cloud-starter-alibaba-nacos-config</artifactId>
</dependency>
```

```yaml
spring:
  application:
    name: order-service
  cloud:
    nacos:
      config:
        server-addr: 127.0.0.1:8848
        namespace: prod
        file-extension: yaml
        group: DEFAULT_GROUP
  config:
    import: optional:nacos:order-service.yaml
```

Nacos 上 Data ID 通常为 `order-service.yaml`（或 `-prod.yaml`）。

---

## 3. 动态刷新

```java
@RestController
@RefreshScope   // 或 @ConfigurationProperties + @RefreshScope
public class ConfigController {
    @Value("${promotion.enabled:false}")
    private boolean promotionEnabled;
}
```

配置变更 → Nacos 推送 → Spring Cloud 刷新 Context → `@RefreshScope` Bean 重建。

**@ConfigurationProperties**（推荐）：

```java
@ConfigurationProperties(prefix = "order")
@RefreshScope
public class OrderProperties {
    private int maxItems;
}
```

---

## 4. 多环境 Data ID 策略

| 策略 | Data ID 示例 |
|------|--------------|
| 单文件 + profile | order-service-prod.yaml |
| 共享配置 | common.yaml + order-service.yaml |
| extension | `extension-configs` 加载多个 |

```yaml
spring:
  cloud:
    nacos:
      config:
        shared-configs:
          - data-id: common.yaml
            refresh: true
```

---

## 5. 敏感配置

- Nacos **加密插件**（Cipher）
- 或只存 **引用**：`password: ${DB_PASSWORD}`，真实值来自 K8s Secret
- **禁止** Git 提交生产密码

---

## 6. 与本地配置优先级

```
Nacos 远程 > application-prod.yml > application.yml
```

本地保留 **结构默认**，环境差异放 Nacos。

---

## 7. 灰度配置

Nacos 支持 **Beta 发布**：指定 IP 先收到新配置，验证后全量。

---

## 8. 坑

| 坑 | 处理 |
|----|------|
| 刷新不生效 | 缺 @RefreshScope；非 Bean 字段 |
| 启动拉不到配置 | import 路径、namespace、Data ID 名 |
| 大配置推送风暴 | 批量变更合并；避免频繁改 |

---

→ [04-Spring Cloud Gateway](./04-SpringCloudGateway.md)

← [02-Nacos 注册发现](./02-Nacos注册发现.md)
