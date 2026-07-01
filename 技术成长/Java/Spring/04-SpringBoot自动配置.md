# 04 · Spring Boot 自动配置

> **目标读者**：理解 `@SpringBootApplication` 拆解、条件装配、自定义 Starter、配置绑定与 Actuator。
> **预计阅读**：60 min · **难度**：★★★★

---

## 1. @SpringBootApplication 拆解

```java
@SpringBootApplication
public class Application { }
```

等价于：

```java
@Configuration
@EnableAutoConfiguration   // 自动配置入口
@ComponentScan            // 扫描主类包
// 可选 @SpringBootConfiguration
```

---

## 2. 自动配置加载流程

```
SpringApplication.run
  → 准备 Environment（application.yml、profile、命令行）
  → refresh ApplicationContext
  → @EnableAutoConfiguration
       → AutoConfigurationImportSelector
       → 读取 META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports
       → 过滤 @Conditional* 不满足的配置类
  → 注册生效的 @Configuration 到容器
```

**Spring Boot 2.7+ / 3.x**：`AutoConfiguration.imports` 替代 `spring.factories` 中的 `EnableAutoConfiguration` 键。

**查看生效的自动配置**：

```bash
java -jar app.jar --debug
# 或 application.properties: debug=true
# Positive/Negative matches 日志
```

或：

```yaml
logging:
  level:
    org.springframework.boot.autoconfigure: DEBUG
```

---

## 3. 常用 @Conditional

| 注解 | 条件 |
|------|------|
| `@ConditionalOnClass` | classpath 有某类 |
| `@ConditionalOnMissingClass` | 没有某类 |
| `@ConditionalOnBean` | 容器已有某 Bean |
| `@ConditionalOnMissingBean` | 没有某 Bean |
| `@ConditionalOnProperty` | 配置项匹配 |
| `@ConditionalOnWebApplication` | Web 应用 |
| `@ConditionalOnExpression` | SpEL |

**示例**（DataSource 自动配置简化逻辑）：

```java
@Configuration
@ConditionalOnClass(DataSource.class)
@ConditionalOnMissingBean(DataSource.class)
@EnableConfigurationProperties(DataSourceProperties.class)
public class DataSourceAutoConfiguration {
    @Bean
    @ConditionalOnProperty(name = "spring.datasource.type", havingValue = "com.zaxxer.hikari.HikariDataSource", matchIfMissing = true)
    public DataSource dataSource(DataSourceProperties props) {
        return props.initializeDataSourceBuilder().build();
    }
}
```

---

## 4. 配置绑定

### 4.1 @ConfigurationProperties

```java
@ConfigurationProperties(prefix = "order")
@Validated
public record OrderProperties(
    @Min(1) int maxItems,
    Duration timeout,
    List<String> allowedChannels
) { }
```

```yaml
order:
  max-items: 100
  timeout: 30s
  allowed-channels:
    - alipay
    - wechat
```

启用：

```java
@ConfigurationPropertiesScan
// 或 @EnableConfigurationProperties(OrderProperties.class)
```

**松散绑定**：`max-items` ↔ `maxItems` ↔ `MAX_ITEMS`。

### 4.2 @Value

```java
@Value("${order.max-items:50}")
private int maxItems;
```

适合少量；复杂结构用 `@ConfigurationProperties`。

---

## 5. Profile 与环境

```yaml
spring:
  profiles:
    active: prod

---
spring:
  config:
    activate:
      on-profile: dev
server:
  port: 8081
```

```java
@Profile("prod")
@Bean
public PaymentGateway prodGateway() { ... }
```

**多环境文件**：`application-dev.yml`、`application-prod.yml`。

---

## 6. 自定义 Starter

**模块划分**：

```
my-feature-spring-boot-autoconfigure/   # 自动配置类
my-feature-spring-boot-starter/         # 空壳，依赖 autoconfigure + 可选第三方库
```

**autoconfigure**：

```java
@Configuration
@ConditionalOnClass(MyClient.class)
@EnableConfigurationProperties(MyFeatureProperties.class)
public class MyFeatureAutoConfiguration {
    @Bean
    @ConditionalOnMissingBean
    public MyClient myClient(MyFeatureProperties props) {
        return new MyClient(props.getEndpoint());
    }
}
```

**resources/META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports**：

```
com.example.MyFeatureAutoConfiguration
```

**starter/pom.xml** 只聚合依赖，无 Java 代码。

---

## 7. 内嵌容器与启动

```java
SpringApplication.run(App.class, args);
```

- 内嵌 **Tomcat**（默认）、Jetty、Undertow
- `ServletWebServerApplicationContext` 启动 Web 容器
- 端口 `server.port`、上下文 `server.servlet.context-path`

**优雅停机**：

```yaml
server:
  shutdown: graceful
spring:
  lifecycle:
    timeout-per-shutdown-phase: 30s
```

---

## 8. Actuator 监控

```xml
<dependency>
  <groupId>org.springframework.boot</groupId>
  <artifactId>spring-boot-starter-actuator</artifactId>
</dependency>
```

```yaml
management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics,prometheus
  endpoint:
    health:
      show-details: when_authorized
```

| 端点 | 用途 |
|------|------|
| `/actuator/health` | 健康检查 |
| `/actuator/metrics` | 指标 |
| `/actuator/prometheus` | Prometheus  scrape |

---

## 9. 常见扩展点

| 扩展点 | 用途 |
|--------|------|
| `ApplicationContextInitializer` | 容器 refresh 前 |
| `ApplicationListener` | 事件监听 |
| `CommandLineRunner` / `ApplicationRunner` | 启动后执行 |
| `EnvironmentPostProcessor` | 环境变量后处理 |

---

## 10. 面试题

| 问 | 答 |
|----|-----|
| 自动配置原理？ | imports 文件 + @Conditional 过滤 |
| 如何排除自动配置？ | `@SpringBootApplication(exclude = {...})` |
| Starter 作用？ | 一站式依赖 + 自动配置 |
| @ConfigurationProperties 和 @Value？ | 前者类型安全批量绑定；后者单值 |
| spring.factories 和 imports 区别？ | Boot 2.7+ 推荐 imports 文件 |

---

→ [05-Spring MVC 与 Web 层](./05-SpringMVC与Web层.md)

← [03-AOP 与动态代理](./03-AOP与动态代理.md)
