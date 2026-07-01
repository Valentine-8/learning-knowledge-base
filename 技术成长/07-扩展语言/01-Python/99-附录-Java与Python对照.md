# Java 与 Python 对照速查

> **读者**：会 Java，Python 0 基础。写 Python 时随时翻这张表。
> 系统学习 → [00-Java开发者学习指南](./00-入门/01-Java开发者学习指南.md) → 01～15 章

---

## 0. 五个核心差异（面试背这表）

| # | Java | Python |
|---|------|--------|
| 1 | 静态类型，编译期检查 | 动态类型，运行时绑定；可选 type hints |
| 2 | `{ }` 代码块 | **缩进** 代码块 |
| 3 | checked + unchecked 异常 | 只有 unchecked（`try/except`） |
| 4 | interface 显式实现 | **鸭子类型**（有方法就能用） |
| 5 | 多线程 CPU 并行（无 GIL） | **GIL** 限制；CPU 密集用多进程 |

---

## 1. 程序入口

| Java | Python |
|------|--------|
| `public static void main(String[] args)` | `if __name__ == "__main__":` |
| `args[0]` | `sys.argv[1]` |

```python
import sys

def main() -> None:
  print(sys.argv)

if __name__ == "__main__":
  main()
```

---

## 2. 类型与声明

| Java | Python |
|------|--------|
| `int x = 1;` | `x = 1` |
| `final int x = 1;` | `x = 1`（约定不改，无编译器强制） |
| `String s = null;` | `s: str \| None = None` |
| `List<String>` | `list[str]` |
| `Map<String, Integer>` | `dict[str, int]` |
| `Set<String>` | `set[str]` |
| `Optional<String>` | `str \| None` |

---

## 3. 控制流

| Java | Python |
|------|--------|
| `for (int i = 0; i < n; i++)` | `for i in range(n):` |
| `for (String s : list)` | `for s in list:` |
| `switch` | `match`（3.10+）或 `if/elif` |
| `while (cond)` | `while cond:` |

```python
match status:
    case 200:
        handle_ok()
    case 404:
        handle_missing()
    case _:
        handle_error()
```

---

## 4. 集合操作

| Java | Python |
|------|--------|
| `list.add(e)` | `list.append(e)` |
| `list.size()` | `len(list)` |
| `map.get(k)` | `dict.get(k)` |
| `map.getOrDefault(k, d)` | `dict.get(k, d)` |
| `map.put(k, v)` | `dict[k] = v` |
| `Arrays.asList(1,2,3)` | `[1, 2, 3]` |
| `new HashMap<>()` | `{}` 或 `dict()` |

---

## 5. 字符串

| Java | Python |
|------|--------|
| `"a".equals("b")` | `a == b` |
| `StringBuilder` | `list` + `"".join()` 或 `io.StringIO` |
| `String.format("%s", x)` | `f"{x}"` |
| `s.substring(1, 3)` | `s[1:3]` |
| `s.length()` | `len(s)` |

---

## 6. 异常

| Java | Python |
|------|--------|
| `try/catch/finally` | `try/except/else/finally` |
| `catch (IOException e)` | `except OSError as e:` |
| checked exception | 无 |
| `throw new RuntimeException()` | `raise ValueError("msg")` |
| `try (var in = ...)` | `with open(...) as f:` |

---

## 7. 面向对象

| Java | Python |
|------|--------|
| `class Foo extends Bar` | `class Foo(Bar):` |
| `implements Runnable` | 继承或 `Protocol` |
| `@Override` | 直接重写，无注解 |
| `private int x` | `self._x`（约定） |
| `static void m()` | `@staticmethod` |
| `public final class` | 无 `final class`；可用 `@dataclass(frozen=True)` |
| Lombok `@Data` | `@dataclass` |
| `equals/hashCode` | 默认 `is`；可自定义 `__eq__` |

---

## 8. 并发

| Java | Python |
|------|--------|
| `new Thread(() -> {}).start()` | `threading.Thread(target=f).start()` |
| `ExecutorService` | `concurrent.futures.ThreadPoolExecutor` |
| `CompletableFuture` | `asyncio` / `concurrent.futures` |
| `synchronized` | `threading.Lock` |
| `volatile` | `threading` 锁或 `queue`；无直接等价 |
| 多核 CPU 并行线程 | 受 GIL 限制，CPU 密集用 `multiprocessing` |

---

## 9. 构建与依赖

| Java | Python |
|------|--------|
| Maven / Gradle | pip + requirements.txt / Poetry |
| `mvn test` | `pytest` |
| JUnit 5 | pytest |
| Checkstyle | ruff / flake8 |
| JAR 部署 | 脚本 / wheel / Docker |

---

## 10. Web 与数据（了解）

| Java | Python |
|------|--------|
| Spring Boot | FastAPI / Django |
| JPA / MyBatis | SQLAlchemy |
| Jackson | `json` / pydantic |
| JDBC | `psycopg2` / `pymysql` |

**本知识库主线**：业务仍用 Java；Python 以脚本与 AI 实验为主。

---

## 11. 按章节查对照

| 章 | Java 你已会 | Python 重点看 |
|----|-------------|---------------|
| 01 | `java Main` | `python main.py`、缩进 |
| 02 | `int x=1` | 动态类型、None |
| 04～05 | ArrayList/HashMap | list/dict 语法糖 |
| 07 | 方法重载 | 无重载、默认参数陷阱 |
| 08 | try-with-resources | `with` |
| 09 | Maven | venv + pip |
| 10 | class/interface | self、dataclass |
| 11 | Stream（部分） | 推导式、yield、@装饰器 |
| 13 | RestTemplate | requests |
| 14 | JUC 线程池 | GIL、asyncio |

---

← [00-Java开发者学习指南](./00-入门/01-Java开发者学习指南.md) · [Python 目录](./README.md)
