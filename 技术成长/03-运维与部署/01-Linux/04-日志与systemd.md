# 04 · 日志与 systemd

> **预计阅读**：50 min · **难度**：★★★

---

## 1. 系统日志体系

```
应用日志 → /app/logs/、/var/log/app/
    │
系统日志 → journald（systemd-journald）
    │         └── journalctl 查看
    │
传统     → rsyslog → /var/log/messages、syslog
    │
logrotate → 按大小/时间轮转压缩
```

---

## 2. journalctl

```bash
journalctl -u nginx.service          # 某服务
journalctl -u order-service -f       # 实时跟踪
journalctl -u order-service --since "2026-07-01 10:00"
journalctl -u order-service --since today -p err
journalctl -k                          # 内核日志
journalctl --disk-usage
journalctl --vacuum-size=500M          # 清理
```

| 参数 | 说明 |
|------|------|
| `-f` | follow |
| `-n 100` | 最后 100 行 |
| `-p err` | 优先级 err 及以上 |
| `--since/--until` | 时间范围 |

---

## 3. rsyslog

配置 `/etc/rsyslog.conf`：

```
*.info;mail.none;authpriv.none   /var/log/messages
authpriv.*                        /var/log/secure
```

```bash
systemctl restart rsyslog
tail -f /var/log/messages
```

---

## 4. logrotate

配置 `/etc/logrotate.d/app`：

```
/app/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    missingok
    notifempty
    copytruncate
    size 100M
}
```

| 指令 | 说明 |
|------|------|
| daily/weekly | 轮转周期 |
| rotate N | 保留 N 份 |
| compress | gzip 压缩 |
| copytruncate | 复制后清空（Java 进程不重启） |
| create | 创建新文件并设权限 |

```bash
logrotate -d /etc/logrotate.d/app    # 调试
logrotate -f /etc/logrotate.d/app    # 强制轮转
```

**Java 注意**：Logback 的 `RollingFileAppender` 自带轮转，与 logrotate 二选一，避免冲突。

---

## 5. systemd 服务管理

```bash
systemctl start order-service
systemctl stop order-service
systemctl restart order-service
systemctl reload nginx
systemctl status order-service
systemctl enable order-service       # 开机自启
systemctl disable order-service
systemctl list-units --type=service
```

---

## 6. 编写 systemd Unit

`/etc/systemd/system/order-service.service`：

```ini
[Unit]
Description=Order Service
After=network.target

[Service]
Type=simple
User=app
Group=app
WorkingDirectory=/app/order-service
Environment=JAVA_OPTS=-Xms512m -Xmx512m
ExecStart=/usr/bin/java $JAVA_OPTS -jar order-service.jar
ExecStop=/bin/kill -15 $MAINPID
Restart=on-failure
RestartSec=10
LimitNOFILE=65535

[Install]
WantedBy=multi-user.target
```

```bash
systemctl daemon-reload
systemctl enable --now order-service
```

| Type | 说明 |
|------|------|
| simple | 默认，ExecStart 即主进程 |
| forking | 传统 daemon |
| notify | sd_notify 通知就绪 |
| oneshot | 一次性任务 |

---

## 7. 定时任务

### cron

```bash
crontab -e
# 分 时 日 月 周
0 2 * * * /app/scripts/backup.sh >> /var/log/backup.log 2>&1
```

```bash
crontab -l
cat /etc/cron.d/app
```

### systemd timer（推荐）

`/etc/systemd/system/backup.timer`：

```ini
[Unit]
Description=Daily Backup

[Timer]
OnCalendar=*-*-* 02:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

配合 `backup.service` 使用，可 journalctl 查日志，比 cron 可观测性更好。

---

## 8. 应用日志最佳实践

| 实践 | 说明 |
|------|------|
| 结构化 | JSON 日志便于 ELK/Loki |
| 级别 | 生产 INFO，排障临时 DEBUG |
| 脱敏 | 不打印密码、身份证 |
| 关联 ID | traceId 贯穿 |
| 分离 | access / error / business |
| 轮转 | 按大小+天数，防磁盘满 |

---

## 9. 小结

| 要点 | 一句话 |
|------|--------|
| journalctl | systemd 服务日志首选 |
| logrotate | 系统级轮转，注意与 Logback 冲突 |
| systemd | 生产 Java 服务标准托管方式 |
| timer | 替代 cron，日志可追踪 |

---

← [03 磁盘内存性能](./03-磁盘内存与性能.md) · [05 生产案例 →](./05-生产案例与面试题库.md)
