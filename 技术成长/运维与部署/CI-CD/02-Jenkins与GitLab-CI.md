# 02 · Jenkins 与 GitLab CI

> **预计阅读**：60 min · **难度**：★★★

---

## 1. Jenkins 架构

```
Jenkins Master
  ├── Agent/Node（执行器）
  │     ├── 内置 executor
  │     └── SSH/K8s/Docker agent
  ├── Plugin（Git、Maven、Docker、K8s...）
  └── Job / Pipeline
```

| 概念 | 说明 |
|------|------|
| Master | 调度、UI、配置 |
| Agent | 实际跑构建的机器/容器 |
| Executor | Agent 并发槽位 |
| Workspace | 构建工作目录 |

---

## 2. Jenkins Pipeline

### Declarative（推荐）

```groovy
pipeline {
  agent {
    kubernetes {
      yaml '''
        apiVersion: v1
        kind: Pod
        spec:
          containers:
          - name: maven
            image: maven:3.9-eclipse-temurin-17
            command: ['cat']
            tty: true
      '''
    }
  }
  environment {
    REGISTRY = 'harbor.company.com'
  }
  stages {
    stage('Checkout') {
      steps { checkout scm }
    }
    stage('Build & Test') {
      steps {
        container('maven') {
          sh 'mvn -B clean verify'
        }
      }
    }
    stage('Sonar') {
      steps {
        withSonarQubeEnv('Sonar') {
          sh 'mvn sonar:sonar'
        }
      }
    }
    stage('Quality Gate') {
      steps {
        timeout(time: 5, unit: 'MINUTES') {
          waitForQualityGate abortPipeline: true
        }
      }
    }
    stage('Docker Push') {
      steps {
        sh 'docker build -t $REGISTRY/app:$BUILD_NUMBER .'
        sh 'docker push $REGISTRY/app:$BUILD_NUMBER'
      }
    }
  }
  post {
    failure { mail to: 'team@co.com', subject: "Build Failed #${env.BUILD_NUMBER}" }
    always { cleanWs() }
  }
}
```

---

## 3. Jenkins 关键能力

| 能力 | 插件/方式 |
|------|-----------|
| 凭据 | Credentials Binding |
| 参数化 | parameters {} |
| 多分支 | Multibranch Pipeline |
| 共享库 | @Library('shared-lib') |
| 并行 | parallel {} |
| 审批 | input step |

```groovy
stage('Deploy Prod') {
  steps {
    input message: 'Deploy to production?', ok: 'Deploy'
    sh './deploy-prod.sh'
  }
}
```

---

## 4. GitLab CI 架构

```
GitLab Server
  ├── .gitlab-ci.yml（Pipeline 定义）
  ├── GitLab Runner（执行器）
  │     ├── Shell executor
  │     ├── Docker executor
  │     └── K8s executor
  └── Container Registry（内置镜像仓库）
```

---

## 5. GitLab CI 完整示例

```yaml
variables:
  MAVEN_OPTS: "-Dmaven.repo.local=$CI_PROJECT_DIR/.m2/repository"
  IMAGE: $CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA

stages:
  - build
  - test
  - docker
  - deploy

cache:
  paths:
    - .m2/repository/

build:
  stage: build
  image: maven:3.9-eclipse-temurin-17
  script:
    - mvn -B compile
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == "main"

test:
  stage: test
  image: maven:3.9-eclipse-temurin-17
  services:
    - name: mysql:8
      alias: mysql
  variables:
    MYSQL_ROOT_PASSWORD: test
  script:
    - mvn -B test
  artifacts:
    when: always
    reports:
      junit: target/surefire-reports/TEST-*.xml

docker:
  stage: docker
  image: docker:24
  services:
    - docker:24-dind
  script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
    - docker build -t $IMAGE .
    - docker push $IMAGE
  only:
    - main

deploy-staging:
  stage: deploy
  image: bitnami/kubectl
  script:
    - kubectl set image deployment/app app=$IMAGE -n staging
  environment:
    name: staging
    url: https://staging.example.com
  only:
    - main
```

---

## 6. GitLab CI 概念

| 概念 | 说明 |
|------|------|
| stage | 阶段，按序执行 |
| job | 具体任务 |
| rules/only/except | 触发条件 |
| artifacts | 阶段产物传递 |
| cache | 跨 pipeline 缓存 |
| environment | 环境追踪 |
| include | 复用 YAML 模板 |

---

## 7. Jenkins vs GitLab CI

| 维度 | Jenkins | GitLab CI |
|------|---------|-----------|
| 配置 | Groovy Jenkinsfile | YAML |
| 插件 | 极多 | 内置为主 |
| 学习曲线 | 较陡 | 较平缓 |
| 适用 | 复杂定制、异构 | GitLab 一体化 |

---

## 8. 小结

| 要点 | 一句话 |
|------|--------|
| Jenkins | 插件强，Pipeline as Code |
| GitLab CI | YAML + Runner，与 Git 一体 |
| Agent/Runner | 构建隔离用 Docker/K8s |
| 凭据 | 绝不硬编码密码 |

---

← [01 CI/CD 概念](./01-CI-CD概念与流水线.md) · [03 GitHub Actions →](./03-GitHub-Actions.md)
