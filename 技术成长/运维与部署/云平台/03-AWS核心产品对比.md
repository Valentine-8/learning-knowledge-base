# 03 · AWS 核心产品对比

> **预计阅读**：50 min · **难度**：★★★

---

## 1. 全球基础设施

| 概念 | AWS | 阿里云 |
|------|-----|--------|
| 地域 | Region（us-east-1） | Region（cn-hangzhou） |
| 可用区 | AZ | 可用区 |
| 边缘 | CloudFront POP | CDN 节点 |

AWS 全球 Region 多，**出海业务首选**；中国区由光环新网/西云数据运营，与全球账号隔离。

---

## 2. 计算对照

| AWS | 阿里云 | 说明 |
|-----|--------|------|
| EC2 | ECS | 虚拟机 |
| EBS | ESSD 云盘 | 块存储 |
| AMI | 镜像 | OS 模板 |
| Auto Scaling | ESS | 弹性伸缩组 |
| EKS | ACK | 托管 K8s |
| Fargate | ECI | Serverless 容器 |
| Lambda | 函数计算 FC | Serverless 函数 |

**EC2 实例类型**：t 通用、m 平衡、c 计算、r 内存、i 存储优化。

---

## 3. 网络对照

| AWS | 阿里云 |
|-----|--------|
| VPC | VPC |
| Subnet | vSwitch |
| Security Group | 安全组 |
| ELB/ALB/NLB | SLB/ALB/NLB |
| Route 53 | 云解析 DNS |
| CloudFront | CDN |
| AWS WAF | WAF |
| Direct Connect | 高速通道 |
| NAT Gateway | NAT 网关 |

---

## 4. 存储对照

| AWS | 阿里云 | 场景 |
|-----|--------|------|
| S3 | OSS | 对象存储 |
| EFS | NAS | 共享文件 |
| EBS | ESSD | 块存储 |
| Glacier | 归档存储 | 冷数据 |
| DynamoDB | Tablestore | NoSQL |

**S3 存储类**：Standard、IA、Glacier、Intelligent-Tiering。

```java
// AWS SDK v2 S3
S3Client s3 = S3Client.builder().region(Region.US_EAST_1).build();
s3.putObject(PutObjectRequest.builder().bucket("b").key("k").build(),
    RequestBody.fromFile(Path.of("file.zip")));
```

---

## 5. 数据库对照

| AWS | 阿里云 |
|-----|--------|
| RDS MySQL/PostgreSQL | RDS |
| Aurora | PolarDB |
| ElastiCache Redis | Redis/Tair |
| DocumentDB | MongoDB 版 |
| MSK | Kafka 版 |

**Aurora**：AWS 自研，存储自动扩展，副本延迟低。

---

## 6. 消息与集成

| AWS | 阿里云 |
|-----|--------|
| SQS | MNS（不完全对等） |
| SNS | 消息通知 |
| MSK / Kinesis | RocketMQ / DataHub |
| EventBridge | 事件总线 |
| API Gateway | API 网关 |

Java 出海常用 **SQS + SNS** 解耦；国内更常见 RocketMQ/Kafka。

---

## 7. 可观测与安全

| AWS | 阿里云 |
|-----|--------|
| CloudWatch | 云监控 |
| X-Ray | ARMS 链路 |
| CloudTrail | 操作审计 |
| IAM | RAM |
| Secrets Manager | KMS/凭据管家 |
| GuardDuty | 安全中心 |

---

## 8. 选型对比

| 维度 | AWS | 阿里云 |
|------|-----|--------|
| 全球覆盖 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐（海外在扩） |
| 国内合规 | 中国区单独 | ⭐⭐⭐⭐⭐ |
| 文档中文 | 一般 | 丰富 |
| 价格 | 竞争充分 | 国内常更便宜 |
| 生态 | 全球最大 | 国内最大 |

**实践**：国内主站阿里云，海外 AWS；或 K8s + Terraform 抽象多云。

---

## 9. Terraform 多云抽象

```hcl
# 同一套 IaC，换 provider
provider "alicloud" { region = "cn-hangzhou" }
provider "aws" { region = "us-east-1" }

resource "alicloud_instance" "web" { /* ... */ }
resource "aws_instance" "web" { /* ... */ }
```

---

## 10. 小结

| 要点 | 一句话 |
|------|--------|
| 对照 | EC2≈ECS、S3≈OSS、RDS≈RDS |
| 出海 | AWS Region 全球 |
| 国内 | 阿里云生态成熟 |
| IaC | Terraform 降低厂商锁定 |

---

← [02 阿里云](./02-阿里云核心产品.md) · [04 生产案例 →](./04-生产案例与面试题库.md)
