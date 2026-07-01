# 第三章：加密与 API 安全

> **阅读目标**：理解对称/非对称加密、哈希与签名、TLS 与 API 鉴权签名、限流脱敏，满足后端安全设计与面试。
>
> **建议用时**：通读 85 min。

---

## 一、密码学基础

### 1.1  Kerckhoffs 原则

系统安全应建立在 **密钥保密** 而非算法保密。

### 1.2 威胁模型

明确防什么：窃听、篡改、冒充、重放、抵赖。

---

## 二、对称加密

### 2.1 特点

**同一密钥** 加解密；速度快，适合 **大数据量**。

| 算法 | 说明 |
|------|------|
| AES-256-GCM | 推荐，带认证 |
| ChaCha20-Poly1305 | TLS 1.3 常用 |
| DES/3DES | 已淘汰 |

### 2.2 模式

- **GCM**：认证加密 AEAD，防篡改
- **ECB**：勿用（相同块相同密文）

### 2.3 密钥管理

- 密钥 **不入库、不进 Git**
- KMS/Vault 托管；环境变量或 Secret 注入 K8s
- 定期 **轮换**

```java
// Java Cipher AES-GCM 概念
Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
cipher.init(Cipher.ENCRYPT_MODE, secretKey, gcmSpec);
byte[] cipherText = cipher.doFinal(plainText);
```

---

## 三、非对称加密

### 3.1 特点

**公钥加密、私钥解密**；或 **私钥签名、公钥验签**。

| 算法 | 用途 |
|------|------|
| RSA 2048+ | 传统，慢 |
| ECDSA / Ed25519 | 更短更快 |

### 3.2 混合加密（TLS 实际）

1. 非对称交换或协商 **对称会话密钥**（ECDHE）
2. 数据传输用 **AES-GCM**

### 3.3 JWT RS256

```
签发：私钥 sign
验证：公钥 verify（Resource Server 只需公钥）
```

---

## 四、哈希与密码存储

### 4.1 哈希函数

| 算法 | 用途 |
|------|------|
| SHA-256 | 完整性、指纹 |
| SHA-3 | 备选 |

**非加密用途**：Git commit、文件校验、区块链。

### 4.2 密码存储

**禁止**：明文、单次 MD5/SHA256（无盐、太快可彩虹表）。

**推荐**：

| 算法 | 说明 |
|------|------|
| **BCrypt** | 自适应 cost，Spring 默认 |
| Argon2 | 内存硬，新系统优选 |
| PBKDF2 | FIPS 场景 |

```java
@Bean
PasswordEncoder passwordEncoder() {
    return new BCryptPasswordEncoder(12); // strength
}

passwordEncoder.matches(raw, encodedHash);
```

**盐**：BCrypt 内置；每用户不同 hash。

### 4.3  pepper（了解）

全局秘密加在密码前，存 HSM；泄露 DB 仍难 crack。

---

## 五、消息认证与签名

### 5.1 HMAC

`HMAC-SHA256(key, message)` → 防篡改，双方共享密钥。

**API 签名**常用：`sign = HMAC(secret, method + path + timestamp + body)`。

### 5.2 数字签名

`RSA/ECDSA_sign(privateKey, hash(data))` → 任何人公钥验签，**不可抵赖**。

### 5.3 对比

| | HMAC | 数字签名 |
|--|------|----------|
| 密钥 | 对称共享 | 公私钥 |
| 速度 | 快 | 较慢 |
| 抵赖 | 双方知密钥 | 私钥持有者不可抵赖 |

---

## 六、TLS / HTTPS（传输安全）

### 6.1 保证

- **机密性**：对称加密
- **完整性**：AEAD / MAC
- **认证**：证书链

### 6.2 证书管理

- Let's Encrypt 免费 DV
- 企业 EV/OV
- **到期监控**、自动续期 cert-manager

### 6.3 双向 TLS（mTLS）

客户端也出示证书 → 服务间零信任。

---

## 七、API 安全设计

### 7.1 鉴权层次

```
1. 网络：VPC、安全组
2. 网关：JWT/API Key、WAF
3. 应用：RBAC、数据权限
4. 数据：加密存储、脱敏
```

### 7.2 API Key

简单识别调用方；**需 HTTPS**；可轮换、绑 IP。

适合 **服务器到服务器** 或公开只读 API。

### 7.3 请求签名（开放平台）

```
Headers:
  X-Timestamp: 1700000000
  X-Nonce: random-uuid
  X-Signature: HMAC-SHA256(secret, canonicalString)

canonicalString = METHOD + "\n" + PATH + "\n" + sortedQuery + "\n" + bodyHash + "\n" + timestamp + "\n" + nonce
```

**防重放**：

- timestamp 窗口 ±5 min
- nonce 存 Redis 用过即废

### 7.4 幂等与防重复提交

- `Idempotency-Key` Header + Redis 去重
- 支付回调验签 + 幂等表

---

## 八、限流与防刷

| 算法 | 说明 |
|------|------|
| 固定窗口 | 简单，边界突发 |
| 滑动窗口 | 更平滑 |
| 令牌桶 | 允许 burst |
| 漏桶 | 恒定速率 |

**实现**：Guava RateLimiter、Redis + Lua、Sentinel、网关插件。

```java
// 概念：Redis INCR + EXPIRE
if (redis.incr("rate:" + userId) == 1) redis.expire(key, 60);
if (count > 100) return 429;
```

**登录**：验证码、账号锁定、IP 限流。

---

## 九、敏感数据

### 9.1 分类

| 级别 | 例子 | 要求 |
|------|------|------|
| 公开 | 商品名 | — |
| 内部 | 订单号 | 访问控制 |
| 敏感 | 手机、身份证 | 加密存储、脱敏展示 |
| 高敏 | 密码、密钥 | 不可逆/hash、KMS |

### 9.2 脱敏

```
手机：138****8000
身份证：110***********1234
日志：禁止打印完整 cardNo、password
```

**MyBatis 拦截器** 或 Jackson `@JsonSerialize` 脱敏。

### 9.3 字段加密

DB 列 AES 加密；查询用 **确定性加密** 或 hash 索引 trade-off。

---

## 十、依赖与供应链安全

- **OWASP Dependency-Check**、Snyk、Dependabot
- 锁定版本、私有 Nexus 代理
- Log4Shell 类漏洞快速响应流程

```xml
<!-- Maven 插件扫描 -->
dependency-check-maven
```

---

## 十一、审计与合规

- **操作审计**：谁、何时、对何资源、何动作
- 等保、GDPR、个人信息保护法：**最小采集**、删除权
- 日志 **不可篡改**（append-only、SIEM）

---

## 十二、常见错误

| 错误 | 正确 |
|------|------|
| 自研加密算法 | 用标准库 AES-GCM |
| ECB 加密长数据 | GCM |
| MD5 存密码 | BCrypt |
| 日志打 token | 打 traceId |
| 签名不含 body |  canonical 含 body hash |
| HTTPS 但证书不校验 | 完整链 + hostname |

---

## 十三、面试高频问答

| 问 | 答 |
|----|-----|
| 对称和非对称？ | 对称快大量数据；非对称握手/sign |
| 为何密码用 BCrypt？ | 慢+盐防彩虹表；可调 cost |
| HMAC 和签名？ | HMAC 共享密钥；签名公私钥+抵赖 |
| HTTPS 防什么？ | 窃听、篡改（+证书防冒充） |
| 如何防 API 重放？ | timestamp+nonce+签名 |
| 限流算法？ | 令牌桶、滑动窗口 |

---

## 十四、密钥轮换流程

1. 生成 new key（RSA 新 keypair / AES 新 key）
2. 签发用 new，验证 **同时接受 old+new**（grace period）
3. 过期 old 的 token 自然失效
4. 移除 old key

**JWT kid header** 标识哪把密钥验签。

---

## 十五、国密算法（了解）

SM2/SM3/SM4 金融政务场景；国际栈仍 RSA/AES/SHA 为主。面试提 **合规场景可选国密**。

---

## 十六、Webhook 签名验证

```java
String sig = hmacSha256(webhookSecret, rawBody);
if (!MessageDigest.isEqual(sig.getBytes(), headerSig.getBytes())) {
    throw new SecurityException("invalid signature");
}
```

**Stripe/GitHub** 均用 HMAC + timestamp 防重放。

---

## 十七、PCI DSS 与支付（了解）

卡数据 **不得** 落业务库明文；用支付网关 tokenization；日志禁 PAN。

Java 集成：支付宝/微信 SDK 回调 **验签** + 幂等。

---

## 十八、Secrets 管理

| 方式 | 场景 |
|------|------|
| K8s Secret | base64，etcd 加密 at rest |
| Vault | 动态密钥、审计 |
| 云 KMS | envelope encryption |

**反模式**：密钥 commit Git；生产 dev 共用 secret。

---

## 十九、零信任架构要点

- 默认不信任内网
- 每请求鉴权 mTLS/JWT
- 最小权限 IAM
- 持续验证设备/posture

微服务 **Service Mesh**（Istio）sidecar mTLS 自动轮换 cert。

---

## 二十、加密性能

| 操作 | 相对成本 |
|------|----------|
| AES-GCM | 低，硬件加速 AES-NI |
| RSA 2048 签名 | 高 |
| ECDSA P-256 | 中低 |

**HTTPS**：会话复用、TLS 1.3、ECDHE 优先；API 批量签名考虑 Ed25519。

---

## 二十二、Envelope Encryption 信封加密

```
DEK（数据密钥）加密数据
KEK（主密钥，KMS）加密 DEK
存储：cipherText + encryptedDEK
```

云 KMS 轮转 KEK 无需重加密全量数据，只重加密 DEK。

---

## 第二十三、TLS 证书 Pinning

移动端内置 **公钥 hash**，仅信任特定证书，防企业 CA 或 compromised CA。

**缺点**：证书轮换需发版；可用 SPKI hash + backup pin。

---

## 二十四、API 版本与签名兼容

```
X-Api-Version: 2024-01-01
```

签名算法版本化：`X-Signature-Version: v2`，旧版 grace period 后下线。

---

## 二十五、敏感配置加密（Jasypt）

```yaml
spring:
  datasource:
    password: ENC(cipher...)
```

```java
@Bean
StringEncryptor encryptor() {
    return new PooledPBEStringEncryptor(); // 主密码仍要安全存放
}
```

**主密码** 来自环境变量，非配置文件。

---

## 二十六、审计日志字段

```json
{
  "timestamp": "2025-01-01T12:00:00Z",
  "actor": "user:123",
  "action": "order:delete",
  "resource": "order:456",
  "ip": "1.2.3.4",
  "result": "success",
  "traceId": "abc"
}
```

**禁止**：记录 password、完整 PAN、JWT 原文。

---

## 二十七、小结

```
存储：BCrypt 密码、敏感字段加密、KMS
传输：TLS 1.2+、mTLS 服务间
API：JWT/签名、timestamp+nonce、幂等、限流
运维：依赖扫描、审计日志、脱敏
```

下一章：[04-面试题库.md](./04-面试题库.md)

← [02-认证授权OAuthJWT](./02-认证授权OAuthJWT.md) · [README](./README.md)
