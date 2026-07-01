# 03 · AOP 与动态代理

> **目标读者**：理解 JDK/CGLIB 选型、切面执行顺序、同类调用失效与事务/AOP 关系。
> **预计阅读**：60 min · **难度**：★★★★

---

## 1. AOP 核心概念

| 术语 | 说明 |
|------|------|
| **Aspect（切面）** | 横切关注点的模块化（日志、事务、权限） |
| **Join Point（连接点）** | 可拦截的点（方法执行、Spring 主要是 **方法**） |
| **Pointcut（切点）** | 匹配哪些 Join Point 的表达式 |
| **Advice（通知）** | 拦截后做什么：Before/After/Around/AfterReturning/AfterThrowing |
| **Target** | 被代理对象 |
| **Proxy** | 代理对象，客户端实际调用 |

```
Client → Proxy.logAround() → Target.businessMethod()
              ↑
         事务/日志/权限
```

---

## 2. JDK 动态代理 vs CGLIB

| | JDK Dynamic Proxy | CGLIB |
|---|-------------------|-------|
| 要求 | **目标实现接口** | 类（生成子类） |
| 原理 | `Proxy.newProxyInstance` + InvocationHandler | ASM 字节码子类 |
| 限制 | 只能代理接口方法 | **不能** proxy `final` 类/方法 |
| Spring Boot 2.x+ | 默认 **CGLIB**（`spring.aop.proxy-target-class=true`） | 默认 |

```java
// JDK：目标必须 implements XxxService
public class OrderServiceImpl implements OrderService { }

// 无接口时 CGLIB：代理 OrderServiceImpl 子类
public class OrderService { }
```

**性能**：现代 JVM 下差距不大；高频创建代理类 CGLIB 有缓存 `ClassLoader` 级别。

---

## 3. 声明式 AOP

```java
@Aspect
@Component
public class LogAspect {

    @Pointcut("execution(* com.example.service..*(..))")
    public void serviceLayer() { }

    @Around("serviceLayer()")
    public Object logAround(ProceedingJoinPoint pjp) throws Throwable {
        long start = System.currentTimeMillis();
        try {
            return pjp.proceed();
        } finally {
            log.info("{} cost {}ms", pjp.getSignature(), System.currentTimeMillis() - start);
        }
    }

    @AfterThrowing(pointcut = "serviceLayer()", throwing = "ex")
    public void afterThrow(JoinPoint jp, Exception ex) {
        log.error("error in {}", jp.getSignature(), ex);
    }
}
```

启用：`@EnableAspectJAutoProxy`（Boot 自动启用）。

---

## 4. Pointcut 表达式

```java
// execution：最常用
execution(public * com.example.service.OrderService.create(..))

// within：类型范围内
within(com.example.service..*)

// @annotation：方法上有注解
@annotation(com.example.aop.Logged)

// @within：类上有注解
@within(org.springframework.stereotype.Service)

// bean：Spring Bean 名
bean(orderService)
```

**组合**：`&&` `||` `!`

---

## 5. 通知执行顺序

同一切点多个 Advice：

```
@Around 前半
  @Before
    目标方法
  @AfterReturning / @AfterThrowing
  @After（finally 语义）
@Around 后半
```

**@Order / @Priority**：数值小优先（外层）。

**与 @Transactional**：事务也是 AOP，通常 **TransactionInterceptor 最外层**（先开事务再进业务 Aspect）。

---

## 6. 同类调用失效（高频）

```java
@Service
public class OrderService {
    public void create() {
        this.saveLog();  // 直接调用，不走代理！
    }

    @Transactional
    public void saveLog() { ... }  // 事务可能失效
}
```

**原因**：`this` 是原始对象，不是代理。

**解决**：

```java
// 1. 注入自身（推荐）
@Service
public class OrderService {
    @Lazy @Autowired
    private OrderService self;

    public void create() {
        self.saveLog();
    }
}

// 2. AopContext（需 @EnableAspectJAutoProxy(exposeProxy = true)）
((OrderService) AopContext.currentProxy()).saveLog();

// 3. 拆到另一个 Service
```

**@Transactional 失效** 80% 与 **自调用** 或 **非 public** 有关。

---

## 7. AOP 实现原理（Spring）

```
AnnotationAwareAspectJAutoProxyCreator（BeanPostProcessor）
  → postProcessAfterInitialization
  → wrapIfNecessary：匹配 Advisor
  → createProxy：JdkDynamicAopProxy 或 ObjenesisCglibAopProxy
```

**Advisor** = Pointcut + Advice；`@Transactional` 由 `BeanFactoryTransactionAttributeSourceAdvisor` 注册。

---

## 8. 实战：自定义注解 + AOP

```java
@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
public @interface Idempotent {
    String key() default "";
}

@Aspect
@Component
public class IdempotentAspect {
    @Around("@annotation(idempotent)")
    public Object around(ProceedingJoinPoint pjp, Idempotent idempotent) throws Throwable {
        String key = resolveKey(pjp, idempotent);
        if (!redis.setIfAbsent(key, "1", Duration.ofMinutes(5))) {
            throw new DuplicateRequestException();
        }
        return pjp.proceed();
    }
}
```

---

## 9. 面试题

| 问 | 答 |
|----|-----|
| AOP 原理？ | 动态代理，运行时代理对象拦截方法 |
| JDK 和 CGLIB？ | 接口 vs 子类；final 不能 CGLIB |
| 同类调用为何失效？ | this 非代理 |
| AspectJ 和 Spring AOP？ | AspectJ 编译期/加载期织入；Spring 仅运行时代理 Bean 方法 |
| 事务和 AOP 关系？ | `@Transactional` 基于 AOP 的 TransactionInterceptor |

---

→ [04-Spring Boot 自动配置](./04-SpringBoot自动配置.md)

← [02-循环依赖与作用域](./02-循环依赖与作用域.md)
