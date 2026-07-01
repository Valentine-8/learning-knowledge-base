# 13 · HTTP、数据处理与 AI 脚本

> **Java 对照**：`requests` ≈ 用 RestTemplate/HttpClient 写脚本更简单；pandas ≈ 没有直接 JDK 对应，做 CSV 分析用；OpenAI SDK 与 Java Spring AI 调的是同一类 API，Python 适合快速试 prompt。
>
> **本章目标**：HTTP、CSV 数据处理、LLM 脚本——**你的目标场景，精读**。
> **预计用时**：10～12 小时 · **难度**：★★★★

---

## 1. 安装

```powershell
pip install requests pandas openai httpx
pip freeze > requirements.txt
```

---

## 2. requests 基础

```python
import requests

resp = requests.get(
    "https://httpbin.org/get",
    params={"page": 1, "size": 10},
    timeout=10,
)
print(resp.status_code)
print(resp.json())

resp = requests.post(
    "https://httpbin.org/post",
    json={"name": "alice"},
    headers={"User-Agent": "my-script/1.0"},
    timeout=10,
)
resp.raise_for_status()
print(resp.json())
```

| 概念 | 说明 |
|------|------|
| status_code | 200 成功，404 不存在，500 服务器错 |
| params | URL 查询参数 |
| json= | 自动 JSON 请求体 |
| timeout | 必须设，防挂死 |
| raise_for_status | 4xx/5xx 抛异常 |

---

## 3. 调用 REST API 完整示例

```python
import os
import requests

API_URL = "https://api.example.com/v1/users"
TOKEN = os.environ.get("API_TOKEN")

def fetch_users(page: int = 1):
    if not TOKEN:
        raise RuntimeError("请设置环境变量 API_TOKEN")
    resp = requests.get(
        API_URL,
        params={"page": page},
        headers={"Authorization": f"Bearer {TOKEN}"},
        timeout=(3, 15),
    )
    resp.raise_for_status()
    return resp.json()

if __name__ == "__main__":
    data = fetch_users()
    for u in data.get("items", []):
        print(u["id"], u.get("name"))
```

**密钥不要写进代码**，用环境变量。

---

## 4. pandas 入门

```python
import pandas as pd

df = pd.read_csv("orders.csv")
print(df.head())
print(df.columns)
print(df.dtypes)

# 过滤
big = df[df["amount"] > 100]

# 新列
df["amount_yuan"] = df["amount"] / 100

# 分组
by_city = df.groupby("city")["amount_yuan"].sum()
print(by_city)

df.to_csv("out.csv", index=False)
```

**你要会的**：read_csv、条件过滤、groupby、to_csv。不必背全 API。

---

## 5. OpenAI SDK

```python
from openai import OpenAI

client = OpenAI()  # 读 OPENAI_API_KEY 环境变量

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "你是简洁的技术助手"},
        {"role": "user", "content": "用三句话解释 TCP 三次握手"},
    ],
    temperature=0.3,
)
print(response.choices[0].message.content)
```

批量问多个问题：

```python
questions = ["什么是 MVCC？", "Redis 持久化两种方式？"]

for q in questions:
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": q}],
    )
    print("Q:", q)
    print("A:", resp.choices[0].message.content)
    print("---")
```

业务系统用 Java Spring AI；Python 适合**试 prompt、批评测**。

---

## 6. 读 LangChain 示例时的关键词

| 词 | 含义 |
|----|------|
| ChatPromptTemplate | 模板化 prompt |
| Runnable / LCEL | 链式组合步骤 |
| Retriever | 从向量库检索文档 |
| Embedding | 文本转向量 |
| Tool | Agent 可调用的函数 |

深入见 [AI工程/05-RAG系统工程化实战.md](../../05-AI工程/05-RAG系统工程化实战.md)。

---

## 7. 小项目：CSV 清洗脚本

需求：读 `raw.csv`，去掉 amount 为空或 ≤0 的行，city 转大写，写 `clean.csv`。

```python
import pandas as pd

def clean(input_path: str, output_path: str) -> None:
    df = pd.read_csv(input_path)
    df = df.dropna(subset=["amount"])
    df = df[df["amount"] > 0]
    df["city"] = df["city"].str.upper()
    df.to_csv(output_path, index=False)
    print(f"保留 {len(df)} 行 -> {output_path}")

if __name__ == "__main__":
    clean("raw.csv", "clean.csv")
```

---

## 8. 小项目：调用公开 API

用 [httpbin.org](https://httpbin.org) 或 GitHub API（无需 token 的接口）练习 GET + 解析 JSON。

---

## 9. 本章练习

1. GET 请求带 3 个 query 参数，打印 JSON 里 origin 字段。
2. pandas 读 CSV，算 amount 平均值、最大值。
3. 设 OPENAI_API_KEY，问一个问题并保存回答到 txt。
4. 合并两个 CSV（同结构）为一个。
5. 写脚本：读本地 md 文件，调用 LLM 生成 100 字摘要（注意 API 费用）。

---

## 10. 本章小结

- requests + timeout + raise_for_status
- pandas 读洗写 CSV
- OpenAI SDK 快速试验
- 密钥走环境变量

---

**下一章** → [14-并发异步与测试](./14-并发异步与测试.md)
