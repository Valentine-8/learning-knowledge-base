# 01 · IoC 与 Bean 生命周期

> **目标读者**：7 年 Java 后端，能讲清容器启动流程、Bean 生命周期、依赖注入方式，并在面试中对比 `@Autowired` 与 `@Resource`。
> **预计阅读**：60 min · **难度**：★★★★

---

## 1. IoC 与 DI

| 概念 | 说明 |
|------|------|
| **IoC（控制反转）** | 对象的创建、组装、生命周期由 **Spring 容器** 管理，而非业务 `new` |
| **DI（依赖注入）** | IoC 的实现方式：容器把依赖 **注入** 到对象（构造器、setter、字段） |

**没有 Spring 时**：

```java
public class OrderService {
    private final OrderRepository repo = new OrderRepositoryImpl(); // 紧耦合
}
```

**有 Spring**：

```java
@Service
public class OrderService {
    private final OrderRepository repo;
    public OrderService(OrderRepository repo) { this.repo = repo; } // 构造器注入（推荐）
}
```

**收益**：解耦、易测试（Mock 注入）、统一生命周期（单例池化）。

---

## 2. ApplicationContext 层次

```
BeanFactory（基础）
    └── ApplicationContext
            ├── AnnotationConfigApplicationContext  // @Configuration
            ├── ClassPathXmlApplicationContext      // XML（老项目）
            └── Spring Boot → AnnotationConfigServletWebServerApplicationContext
```

**BeanFactory vs ApplicationContext**：

| | BeanFactory | ApplicationContext |
|---|-------------|-------------------|
| 加载 | 懒加载 | **预加载** 单例 Bean |
| 事件 | 无 | ApplicationEvent 发布 |
| AOP | 需额外配置 | 自动集成 |
| 国际化 | 无 | MessageSource |

生产几乎只用 **ApplicationContext**。

---

## 3. Bean 的注册方式

### 3.1 组件扫描

```java
@SpringBootApplication  // 含 @ComponentScan 扫描主类包及子包
public class App { }
```

```java
@Service
@Repository
@Controller / @RestController
@Component   // 通用
```

**自定义扫描**：

```java
@ComponentScan(basePackages = "com.example", excludeFilters = ...)
```

### 3.2 `@Configuration` + `@Bean`

```java
@Configuration
public class AppConfig {
    @Bean
    public RestTemplate restTemplate() {
        return new RestTemplate();
    }

    @Bean
    @ConditionalOnMissingBean
    public ObjectMapper objectMapper() {
        return new ObjectMapper();
    }
}
```

**`@Configuration` 的 CGLIB 增强**：`@Bean` 方法间调用会走容器单例，不是每次 new。

```java
@Configuration
public class Config {
    @Bean
    public A a() { return new A(b()); }  // b() 返回容器里同一个 B
    @Bean
    public B b() { return new B(); }
}
```

**`@Component` + `@Bean`**（Lite 模式）：方法调用 **不** 走代理，每次 new。

---

## 4. 依赖注入方式

| 方式 | 示例 | 推荐 |
|------|------|------|
| 构造器 | `public S(Dep d)` | **首选**，不可变、易测 |
| Setter | `@Autowired setDep` | 可选依赖 |
| 字段 | `@Autowired Dep d` | 简洁但难测、隐藏依赖 |

```java
@Service
public class OrderService {
    private final OrderMapper mapper;
    private final PayClient payClient;

    public OrderService(OrderMapper mapper, PayClient payClient) {
        this.mapper = mapper;
        this.payClient = payClient;
    }
}
```

Spring 4.3+ **单构造器可省略 `@Autowired`**。

### 4.1 多实现注入

```java
interface PaymentChannel { }
@Service @Primary class AlipayChannel implements PaymentChannel { }
@Service class WechatChannel implements PaymentChannel { }

@Service
class PayService {
    @Autowired
    PaymentChannel channel;  // @Primary 的 Alipay

    @Autowired
    List<PaymentChannel> all;  // 全部实现

    @Autowired
    @Qualifier("wechatChannel")
    PaymentChannel wechat;
}
```

### 4.2 `@Autowired` vs `@Resource`

| | @Autowired | @Resource (JSR-250) |
|---|----------|---------------------|
| 默认 | **byType** | **byName** |
| 来源 | Spring | Jakarta EE |
| 必填 | `required=false` | 无则报错 |

---

## 5. Bean 完整生命周期

```
1. 实例化（构造器）
2. 属性填充（@Autowired / @Value）
3. Aware 回调
   BeanNameAware / BeanFactoryAware / ApplicationContextAware
4. BeanPostProcessor.postProcessBeforeInitialization
5. @PostConstruct / InitializingBean.afterPropertiesSet / init-method
6. BeanPostProcessor.postProcessAfterInitialization  ← AOP 代理常在此
7. Bean 就绪，使用中
8. 容器关闭：
   @PreDestroy / DisposableBean.destroy / destroy-method
```

**源码关键类**：

- `AbstractAutowireCapableBeanFactory.doCreateBean`
- `initializeBean` → `applyBeanPostProcessorsBefore/After`

---

## 6. BeanPostProcessor 与 BeanFactoryPostProcessor

| 接口 | 时机 | 典型用途 |
|------|------|----------|
| **BeanFactoryPostProcessor** | BeanDefinition 加载后、Bean 实例化 **前** | 修改 Bean 定义、`PropertySourcesPlaceholderConfigurer` |
| **BeanPostProcessor** | 每个 Bean 初始化前后 | AOP 代理、`@Autowired` 注解处理（AutowiredAnnotationBeanPostProcessor） |

```java
@Component
public class TimingBeanPostProcessor implements BeanPostProcessor {
    @Override
    public Object postProcessAfterInitialization(Object bean, String name) {
        // 可包装 bean
        return bean;
    }
}
```

**ApplicationContext 自动注册** 大量 BPP，无需手动。

---

## 7. 作用域（Scope）

| Scope | 说明 |
|-------|------|
| **singleton**（默认） | 容器内一个实例 |
| **prototype** | 每次 getBean 新建 |
| **request / session / application** | Web 环境 |

```java
@Service
@Scope(value = WebApplicationContext.SCOPE_REQUEST, proxyMode = ScopedProxyMode.TARGET_CLASS)
public class RequestUserContext { }
```

**prototype 注入 singleton**：singleton 持有一个 prototype 引用会过期 → 用 `ObjectProvider<T>` 或 `@Lookup`。

---

## 8. 条件注册

```java
@Bean
@ConditionalOnProperty(name = "feature.x.enabled", havingValue = "true")
public FeatureX featureX() { return new FeatureX(); }

@Profile("prod")
@Service
public class ProdOnlyService { }
```

Boot 扩展：`@ConditionalOnClass`、`@ConditionalOnMissingBean` 等（见第 04 章）。

---

## 9. 事件机制

```java
public class OrderCreatedEvent extends ApplicationEvent {
    public OrderCreatedEvent(Object source, Long orderId) { super(source); }
}

@Component
public class OrderEventListener {
    @EventListener
    @Async
    public void onCreated(OrderCreatedEvent e) { ... }
}

// 发布
applicationContext.publishEvent(new OrderCreatedEvent(this, orderId));
```

**异步**需 `@EnableAsync` + 线程池。

---

## 10. 面试题

| 问 | 答 |
|----|-----|
| IoC 和 DI 区别？ | IoC 思想；DI 是注入手段 |
| 构造器 vs 字段注入？ | 构造器：不可变、强制依赖、易单测 |
| @Configuration 和 @Component 区别？ | 前者 @Bean 方法 CGLIB 单例；后者 Lite |
| Bean 生命周期？ | 实例化→注入→Aware→BPP→init→BPP→destroy |
| BeanPostProcessor 用途？ | AOP、注解解析、包装 Bean |

---

## 11. 自测

1. 画出 Bean 从 `doCreateBean` 到可用的流程。
2. 写 `@Configuration` 证明两个 `@Bean` 方法调用共享单例。
3. 多实现时如何用 `@Primary` 和 `@Qualifier`？

---

## 12. ApplicationContext refresh 概览（源码级）

`AbstractApplicationContext.refresh()` 是容器启动核心，简化步骤：

```
1. prepareRefresh()
2. obtainFreshBeanFactory()          // 加载 BeanDefinition（XML/注解扫描）
3. prepareBeanFactory()
4. postProcessBeanFactory()          // BeanFactoryPostProcessor
5. invokeBeanFactoryPostProcessors() // 处理 @Configuration 等
6. registerBeanPostProcessors()
7. initMessageSource / initApplicationEventMulticaster
8. onRefresh()                       // 子类扩展（如 Servlet 容器启动）
9. registerListeners()
10. finishBeanFactoryInitialization() // 实例化所有非 lazy 单例 ← getBean 发生在此
11. finishRefresh()
```

**第 10 步** 会触发所有单例 Bean 创建，包括你的 `@Service`、`@Controller`。

**BeanDefinition 是什么**：Bean 的「图纸」，含 className、scope、propertyValues、constructorArgs，**尚未实例化**。

```java
// 概念对应
BeanDefinition  →  图纸
Bean            →  实例
BeanFactory     →  工厂（getBean）
```

---

## 13. 常见扩展：FactoryBean

```java
public class MyFactoryBean implements FactoryBean<MyClient> {
    @Override
    public MyClient getObject() { return new MyClient(config); }
    @Override
    public Class<?> getObjectType() { return MyClient.class; }
}

// 容器中 getBean("myFactoryBean") 得到的是 MyClient，不是 FactoryBean 本身
// getBean("&myFactoryBean") 才得到 FactoryBean
```

MyBatis 的 `SqlSessionFactoryBean` 即 FactoryBean。

---

## 14. 生产案例

| 现象 | 根因 | 处理 |
|------|------|------|
| 注入 null | 非 Spring 管理对象里 `@Autowired` | 让 Spring 创建或 `ApplicationContextAware` |
| 同名 Bean 冲突 | 两个 `@Service` 同名 | 改 beanName 或 `@Qualifier` |
| @Value 占位符不解析 | 未注册 PropertySourcesPlaceholderConfigurer | Boot 自动；纯 Spring 需配置 |
| 多 Context 父容器 | 父子容器可见性 | 理解 Parent-Child 上下文 |

---

→ [02-循环依赖与作用域](./02-循环依赖与作用域.md)

← [速查总览](./00-速查总览.md)
