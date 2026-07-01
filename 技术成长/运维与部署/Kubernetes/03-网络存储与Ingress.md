# 03 · 网络、存储与 Ingress

> **目标读者**：配置 Service/Ingress 暴露 Java API、理解 ClusterIP 与 DNS、PVC 持久化。
> **预计阅读**：50 min · **难度**：★★★★

---

## 1. 集群内网络模型

- 每个 Pod 有独立 IP
- 同一 Node 上 Pod 可通过 **CNI** 网络互通
- **Service** 提供稳定虚拟 IP（ClusterIP）和 DNS

```
Client Pod  →  order-app.prod.svc.cluster.local:80
                    ↓ kube-proxy
              Endpoints (Ready Pod IPs)
```

---

## 2. Service 详解

```yaml
apiVersion: v1
kind: Service
metadata:
  name: order-app
  namespace: prod
spec:
  type: ClusterIP
  selector:
    app: order-app
  ports:
    - name: http
      port: 80
      targetPort: 8080
      protocol: TCP
  sessionAffinity: None
```

| 字段 | 说明 |
|------|------|
| port | Service 端口 |
| targetPort | Pod 容器端口 |
| selector | 匹配 Pod label |

**DNS**：

- 同 ns：`order-app`
- 跨 ns：`order-app.prod.svc.cluster.local`

Spring Boot 连 Redis：

```yaml
SPRING_DATA_REDIS_HOST: redis.prod.svc.cluster.local
```

### 2.1 NodePort

```yaml
spec:
  type: NodePort
  ports:
    - port: 80
      targetPort: 8080
      nodePort: 30080
```

`<任意NodeIP>:30080` 访问，适合测试；生产用 LoadBalancer 或 Ingress。

### 2.2 LoadBalancer

云厂商创建 SLB，自动映射到 Service。

---

## 3. Ingress — HTTP 七层入口

需 **Ingress Controller**（Nginx Ingress、Traefik、云 ALB）。

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: api-ingress
  annotations:
    nginx.ingress.kubernetes.io/proxy-body-size: "50m"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "120"
spec:
  ingressClassName: nginx
  tls:
    - hosts:
        - api.example.com
      secretName: api-tls
  rules:
    - host: api.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: order-app
                port:
                  number: 80
    - host: www.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: frontend
                port:
                  number: 80
```

**与裸 Nginx 关系**：Ingress Controller 动态生成 nginx.conf；你学 [Nginx 章](../Nginx/README.md) 有助于调 annotation。

---

## 4. Headless Service

```yaml
spec:
  clusterIP: None
  selector:
    app: mysql
```

DNS 直接返回 **Pod IP 列表**，用于 StatefulSet  peer 发现。

---

## 5. 存储 PV / PVC

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: mysql-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 20Gi
  storageClassName: standard
```

Pod 挂载：

```yaml
volumeMounts:
  - name: data
    mountPath: /var/lib/mysql
volumes:
  - name: data
    persistentVolumeClaim:
      claimName: mysql-pvc
```

| accessMode | 含义 |
|------------|------|
| RWO | 单节点读写 |
| ROX | 多节点只读 |
| RWX | 多节点读写（需 NFS 等） |

**Java 应用** 本身无状态；日志建议 **stdout** 采集，不写本地 PVC。

---

## 6. emptyDir 与 ConfigMap 卷

```yaml
volumes:
  - name: cache
    emptyDir: {}
  - name: tmp
    emptyDir:
      medium: Memory
      sizeLimit: 256Mi
```

临时缓存；Pod 删则丢。

---

## 7. NetworkPolicy（了解）

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all-ingress
spec:
  podSelector: {}
  policyTypes:
    - Ingress
```

默认全通；零信任环境限制 Pod 间访问（需 CNI 支持）。

---

## 8. 全链路：外网到 Pod

```
Internet
  → 云 LB / Ingress Controller (Nginx)
  → Ingress 规则 host/path
  → Service ClusterIP:80
  → kube-proxy → Pod IP:8080
  → Spring Boot
```

---

## 9. 常见问题

| 问题 | 排查 |
|------|------|
| Service 无 Endpoints | selector 与 Pod label 不一致 |
| Ingress 404 | pathType、ingressClass、backend 端口 |
| 跨 ns 访问失败 | DNS 写全名或同 ns |
| 502 from Ingress | Pod not ready、探针失败、应用 crash |

```bash
kubectl get endpoints order-app -n prod
kubectl describe ingress api-ingress
```

---

## 10. 面试题

| 问 | 答 |
|----|-----|
| ClusterIP 原理？ | 虚拟 IP + kube-proxy iptables/IPVS 转 Pod |
| Ingress 和 Service？ | Ingress 七层路由到 Service；Service 四层负载 |
| PV 和 PVC 关系？ | PVC 申请，PV 供给，StorageClass 动态供给 |
| 如何让 Java 服务只集群内访问？ | ClusterIP，不建 Ingress |

---

→ 下一章：[04-Java 应用在 K8s](./04-Java应用在K8s.md)

← [02-工作负载与发布策略](./02-工作负载与发布策略.md)
