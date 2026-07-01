# 01 · Maven 核心与生命周期

> **预计阅读**：90 min

---

## 1. Maven 是什么

```
项目对象模型（POM）+ 依赖管理 + 构建生命周期 + 插件
```

**约定优于配置**：标准目录结构，团队零配置上手。

---

## 2. 标准目录结构

```
src/main/java       源码
src/main/resources  资源
src/test/java       测试
src/test/resources  测试资源
target/             输出（编译产物）
pom.xml             项目描述
```

---

## 3. POM 核心元素

```xml
<project>
  <groupId>com.example</groupId>      <!-- 组织 -->
  <artifactId>order-service</artifactId> <!-- 项目 -->
  <version>1.0.0-SNAPSHOT</version>
  <packaging>jar</packaging>          <!-- jar/war/pom -->

  <parent>...</parent>                <!-- 继承 -->
  <dependencies>...</dependencies>
  <dependencyManagement>...</dependencyManagement>
  <build><plugins>...</plugins></build>
  <profiles>...</profiles>
</project>
```

**坐标 GAV**：`groupId:artifactId:version` 唯一标识依赖。

---

## 4. 生命周期与 Phase

Maven 有三套独立生命周期，每套含多个 **Phase**：

| 生命周期 | 常用 Phase |
|----------|------------|
| clean | pre-clean, **clean**, post-clean |
| default | validate, compile, test, **package**, verify, **install**, **deploy** |
| site | site, site-deploy |

**规则**：执行某 Phase 会先执行它之前所有 Phase。

```bash
mvn package    # 触发 compile → test → package
mvn install    # 额外 install 到本地 ~/.m2
```

---

## 5. 插件 Plugin

Phase 本身不干活，由**插件目标（goal）**绑定：

| 插件 | 作用 |
|------|------|
| maven-compiler-plugin | 编译 Java 版本 |
| maven-surefire-plugin | 运行单元测试 |
| maven-jar-plugin | 打 jar |
| spring-boot-maven-plugin | 打可执行 fat jar |
| maven-deploy-plugin | 部署到私服 |

```xml
<plugin>
  <groupId>org.apache.maven.plugins</groupId>
  <artifactId>maven-compiler-plugin</artifactId>
  <version>3.11.0</version>
  <configuration>
    <source>17</source>
    <target>17</target>
  </configuration>
</plugin>
```

---

## 6. Profile

多环境配置：

```xml
<profiles>
  <profile>
    <id>prod</id>
    <properties><env>prod</env></properties>
  </profile>
</profiles>
```

```bash
mvn package -Pprod
```

Spring Boot 常用 `application-{profile}.yml` 配合。

---

## 7. 继承与聚合

| 概念 | 说明 |
|------|------|
| 继承 `<parent>` | 子 POM 继承版本、插件配置 |
| 聚合 `<modules>` | 父 POM 一次构建多个模块 |

```xml
<!-- 父 POM -->
<packaging>pom</packaging>
<modules>
  <module>order-api</module>
  <module>order-service</module>
</modules>
```

---

## 8. Spring Boot 项目特点

```xml
<parent>
  <groupId>org.springframework.boot</groupId>
  <artifactId>spring-boot-starter-parent</artifactId>
  <version>3.2.0</version>
</parent>
```

- 导入 BOM 管理依赖版本
- `spring-boot-maven-plugin` repackage 为可执行 jar

---

## 9. 常用最佳实践

- 版本统一放 `<dependencyManagement>`
- CI 用 `mvn -B`（batch mode）
- 锁定插件版本，避免构建漂移
- `.mvn/wrapper` 统一 Maven 版本

---

## 10. 面试要点

1. Maven 生命周期？
2. Phase 和 Plugin goal 关系？
3. packaging 类型有哪些？
4. parent 和 import scope BOM 区别？
5. install 和 deploy 区别？

← [00-速查](./00-速查.md) · [02-依赖管理](./02-依赖管理与冲突.md)
