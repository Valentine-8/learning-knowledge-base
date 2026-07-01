# 安全

> **目标**：识别常见 Web 攻击并落地防护，设计认证授权（Session/JWT/OAuth2），理解加密与 API 安全，满足后端面试与合规要求。
>
> **速查**：[00-速查总览.md](./00-速查总览.md) · **关联**：[Phase4 Spring Security](../../01-Java/笔记/phase4-Spring/00-复习手册.md)

---

## 章节索引

| 章 | 文件 | 核心内容 | 建议用时 |
|----|------|----------|----------|
| 00 | [00-速查总览.md](./00-速查总览.md) | OWASP 速查、JWT/Session 对比 | 15 min |
| 01 | [01-Web攻击与防护.md](./01-Web攻击与防护.md) | SQLi、XSS、CSRF、SSRF、越权、文件上传 | 90 min |
| 02 | [02-认证授权OAuthJWT.md](./02-认证授权OAuthJWT.md) | Session、JWT、OAuth2 授权码、RBAC、SSO | 90 min |
| 03 | [03-加密与API安全.md](./03-加密与API安全.md) | 对称/非对称、哈希、TLS、签名、限流、脱敏 | 90 min |
| 04 | [04-面试题库.md](./04-面试题库.md) | 高频问答、场景设计、Spring Security 考点 | 60 min |

---

## 学习顺序

```
01 Web 攻击（输入输出边界）
    ↓
02 认证授权（谁可以访问什么）
    ↓
03 加密与 API（传输与接口层）
    ↓
04 面试题库巩固
```

---

## Java / Spring 对照

| 安全点 | 实践 |
|--------|------|
| SQL 注入 | MyBatis `#{}`、JPA 参数绑定 |
| XSS | Thymeleaf 默认转义、CSP Header |
| CSRF | Spring Security CSRF Token、SameSite |
| JWT | `jjwt` / Spring Resource Server |
| OAuth2 | Spring Authorization Server、网关透传 |
| 密码 | BCryptPasswordEncoder |
| HTTPS | Spring Boot SSL、反向代理终止 TLS |

---

## 面试自检清单

- [ ] SQL 注入原理与 `#{}` vs `${}`
- [ ] XSS 存储型/反射型/DOM 型区别与 CSP
- [ ] CSRF 攻击链与 Token 防护
- [ ] JWT 结构、优缺点、refresh token 方案
- [ ] OAuth2 授权码模式时序图
- [ ] 密码存储为何用 BCrypt 而非 SHA-256

← [计算机基础](../README.md)
