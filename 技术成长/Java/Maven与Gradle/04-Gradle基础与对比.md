# 04 · Gradle 基础与对比

> **预计阅读**：80 min

---

## 1. Gradle 定位

```
基于 DAG 的增量构建 + Groovy/Kotlin DSL + 强扩展性
```

Android 官方构建工具；Java 后端越来越多 greenfield 项目选用。

---

## 2. 核心概念

| 概念 | 类比 Maven |
|------|------------|
| Project | 模块 |
| Task | plugin goal |
| Configuration | scope + 依赖组 |
| build.gradle(.kts) | pom.xml |

---

## 3. 基础 build.gradle.kts

```kotlin
plugins {
    java
    id("org.springframework.boot") version "3.2.0"
    id("io.spring.dependency-management") version "1.1.4"
}

group = "com.example"
version = "1.0.0-SNAPSHOT"

java {
    sourceCompatibility = JavaVersion.VERSION_17
}

repositories {
    mavenCentral()
}

dependencies {
    implementation("org.springframework.boot:spring-boot-starter-web")
    testImplementation("org.springframework.boot:spring-boot-starter-test")
}

tasks.test {
    useJUnitPlatform()
}
```

---

## 4. 依赖 Configuration

| Configuration | 类似 Maven Scope |
|---------------|------------------|
| implementation | compile（不传递 api） |
| api | compile + 传递 |
| compileOnly | provided |
| runtimeOnly | runtime |
| testImplementation | test |

---

## 5. 多模块

```kotlin
// settings.gradle.kts
rootProject.name = "order"
include("order-api", "order-web")

// 根 build.gradle.kts
subprojects {
    apply(plugin = "java")
    repositories { mavenCentral() }
}
```

---

## 6. Gradle 优势

| 特性 | 说明 |
|------|------|
| 增量构建 | 只编译变更部分 |
| 构建缓存 | 本地 + 远程缓存 |
| 并行 | `--parallel` |
| Daemon | 常驻 JVM 加速 |
| Kotlin DSL | 类型安全、IDE 补全 |

```bash
./gradlew build --parallel --build-cache
./gradlew :order-web:bootRun
```

---

## 7. Maven vs Gradle

| 维度 | Maven | Gradle |
|------|-------|--------|
| 学习曲线 | 低 | 中 |
| 配置 | XML 冗长 | DSL 简洁 |
| 构建速度 | 较慢 | 快（增量） |
| 生态 | Java 企业标准 | Android/现代 Java |
| 可定制 | 插件 | Task 任意逻辑 |

**选型建议**：

- 现有 Maven 多模块：继续 Maven，优化 CI 缓存
- 新项目 / Android：Gradle
- 大型单体迁移：评估成本，可渐进（Gradle 读 Maven BOM）

---

## 8. 从 Maven 迁移

1. 使用 `gradle init` 或 Spring Initializr 生成 Gradle 项目
2. 对照 `dependency:tree` 迁移依赖
3. 插件对照：surefire → `test` task，spring-boot-maven → boot plugin
4. CI 改用 `./gradlew`，缓存 `.gradle`

---

## 9. 版本目录（Version Catalog）

```toml
# gradle/libs.versions.toml
[versions]
spring-boot = "3.2.0"

[libraries]
spring-web = { module = "org.springframework.boot:spring-boot-starter-web", version.ref = "spring-boot" }
```

类似 Maven BOM，统一管理版本。

---

## 10. 面试要点

1. Gradle 和 Maven 区别？
2. implementation 和 api 区别？
3. Gradle 为什么更快？
4. settings.gradle 作用？
5. 如何在 Gradle 中用 Spring Boot BOM？

← [03-多模块](./03-多模块与私服.md) · [05-案例题库](./05-生产案例与面试题库.md)
