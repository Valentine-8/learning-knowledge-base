# 07 · Spring Security 与 JWT

> **目标读者**：理解 SecurityFilterChain、认证授权分离、JWT 无状态方案与 OAuth2 资源服务器。
> **预计阅读**：50 min · **难度**：★★★★

---

## 1. 核心概念

| 概念 | 说明 |
|------|------|
| **Authentication** | 认证：你是谁（用户名密码、JWT） |
| **Authorization** | 授权：你能做什么（角色、权限） |
| **SecurityContext** | 当前线程安全上下文，存 Authentication |
| **UserDetails** | 用户详情加载接口 |
| **GrantedAuthority** | 权限/角色 |

---

## 2. 过滤器链（Spring Security 6）

```
HTTP Request
  → SecurityContextPersistenceFilter
  → LogoutFilter
  → UsernamePasswordAuthenticationFilter（表单登录）
  → BearerTokenAuthenticationFilter（JWT/OAuth2 Resource Server）
  → AuthorizationFilter（鉴权）
  → ... 其他
  → FilterSecurityInterceptor（旧版）/ AuthorizationFilter
  → DispatcherServlet
```

**与 MVC**：Security Filter 在 **DispatcherServlet 之前**。

---

## 3. 基本配置（SecurityFilterChain）

```java
@Configuration
@EnableWebSecurity
@EnableMethodSecurity
public class SecurityConfig {

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .csrf(csrf -> csrf.disable())  // REST 常关；Cookie 场景要开
            .sessionManagement(s -> s.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/actuator/health", "/api/auth/login").permitAll()
                .requestMatchers("/api/admin/**").hasRole("ADMIN")
                .anyRequest().authenticated()
            )
            .oauth2ResourceServer(oauth2 -> oauth2.jwt(Customizer.withDefaults()));
        return http.build();
    }

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }
}
```

---

## 4. 表单登录 vs JWT

| | Session + Cookie | JWT 无状态 |
|---|------------------|------------|
| 状态 | 服务端 Session | 客户端持 Token |
| 扩展 | 需 Session 共享/Sticky | 易水平扩展 |
| 注销 | 删 Session | 黑名单 / 短过期 + Refresh |
| CSRF | 需防护 | REST 常关 CSRF |

---

## 5. JWT 流程

```
1. POST /api/auth/login {username, password}
2. 验证 UserDetailsService
3. 签发 JWT（access + refresh）
4. 客户端 Header: Authorization: Bearer <access>
5. Resource Server 验签、解析 claims → Authentication
6. @PreAuthorize 鉴权
```

**JWT 结构**：Header.Payload.Signature

```json
// Payload 示例
{
  "sub": "user123",
  "roles": ["USER", "ADMIN"],
  "exp": 1710000000,
  "iat": 1709990000
}
```

---

## 6. OAuth2 Resource Server

```yaml
spring:
  security:
    oauth2:
      resourceserver:
        jwt:
          issuer-uri: https://auth.example.com/realms/myrealm
          # 或 jwk-set-uri
```

```java
@GetMapping("/me")
public UserProfile me(@AuthenticationPrincipal Jwt jwt) {
    return new UserProfile(jwt.getSubject(), jwt.getClaimAsStringList("roles"));
}
```

**与 Spring Authorization Server**、Keycloak、Auth0 集成。

---

## 7. 方法级鉴权

```java
@Service
public class OrderService {
    @PreAuthorize("hasRole('ADMIN') or #userId == authentication.principal.id")
    public void cancel(Long orderId, Long userId) { ... }

    @PostAuthorize("returnObject.owner == authentication.name")
    public Order get(Long id) { ... }
}
```

需 `@EnableMethodSecurity`。

---

## 8. 自定义 UserDetailsService

```java
@Service
public class DbUserDetailsService implements UserDetailsService {
    @Override
    public UserDetails loadUserByUsername(String username) {
        User user = userRepo.findByUsername(username)
            .orElseThrow(() -> new UsernameNotFoundException(username));
        return org.springframework.security.core.userdetails.User
            .withUsername(user.getUsername())
            .password(user.getPasswordHash())
            .roles(user.getRoles().toArray(new String[0]))
            .build();
    }
}
```

---

## 9. 常见问题

| 问题 | 处理 |
|------|------|
| 401 vs 403 | 未认证 vs 已认证无权限 |
| CORS + Security | CorsConfigurationSource Bean |
| 静态资源被拦 | permitAll `/static/**` |
| JWT 过期 | Refresh Token 端点；前端静默刷新 |

---

## 10. 面试题

| 问 | 答 |
|----|-----|
| Spring Security 核心？ | FilterChain + SecurityContext + AuthenticationManager |
| JWT 优缺点？ | 无状态扩展好；难即时注销、payload 勿存敏感 |
| OAuth2 四种模式？ | 授权码（常用）、客户端凭证、密码（废弃）、简化 |
| 401/403？ | 未登录 / 权限不足 |
| CSRF 何时关？ | 纯 JWT Header 的 REST；Cookie Session 要开 |

---

→ [08-MyBatis 映射与缓存](./08-MyBatis映射与缓存.md)

← [06-事务传播与失效](./06-事务传播与失效.md)
