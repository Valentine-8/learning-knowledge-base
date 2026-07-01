# 面试题大全 · C++ 专题（120 题）

> **适用**：C++ 后端 / 游戏 / **嵌入式** / 高频交易 / JNI  
> **嵌入式专项**：→ [本目录 C++嵌入式](./)（八股+手写+广东宏大）  
> **主库索引**：[面试题大全Q&A.md](../../01-Java/面试题大全Q&A.md)  
> **建议**：基础题 Q1～Q40 → 进阶 Q41～Q80 → 现代 C++/并发 Q81～Q120

---

## 目录

1. [语言基础与编译](#一语言基础与编译-q1q15)
2. [面向对象](#二面向对象-q16q30)
3. [内存管理](#三内存管理-q31q45)
4. [STL 标准库](#四stl-标准库-q46q60)
5. [现代 C++11/14/17/20](#五现代-c11141720-q61q75)
6. [模板与元编程](#六模板与元编程-q76q88)
7. [并发与内存模型](#七并发与内存模型-q89q100)
8. [性能、工程与场景](#八性能工程与场景-q101q120)

---

# 一、语言基础与编译（Q1～Q15）

### C1. C 和 C++ 的本质区别？

**A：** C++ 是 C 的超集（不完全兼容），增加 OOP、泛型、异常、RAII、STL、namespace 等。C++ 支持面向对象和多范式，C 面向过程。

---

### C2. 编译链接过程？

**A：** 预处理（#include/#define）→ 编译（.cpp→.o 汇编+目标码）→ 链接（符号解析、重定位、静态/动态库）。`g++ -c` 只编译，`-o` 链接。

---

### C3. 静态链接和动态链接？

**A：** 静态：.a 打进可执行文件，体积大无运行时依赖。动态：.so/.dll 运行时加载，共享节省内存，需 LD_LIBRARY_PATH。Windows DLL、Linux SO。

---

### C4. 头文件为什么用 include guard 或 `#pragma once`？

**A：** 防重复包含导致重定义。`#ifndef/#define/#endif` 或 `#pragma once`（非标准但广泛支持）。

---

### C5. `typedef` 和 `using` 区别？

**A：** C++11 起 `using T = int` 更清晰；模板别名必须 `using Vec = vector<T>`，`typedef` 模板别名语法别扭。

---

### C6. `const` 和 `#define` 区别？

**A：** `#define` 预处理文本替换无类型检查。`const` 有类型、作用域、调试符号。C++ 推荐 const/constexpr 替代宏常量。

---

### C7. 内联函数 `inline` 作用？

**A：** 建议编译器将函数体展开到调用处，减少调用开销。仅声明在头文件。过度 inline 增大代码体积。编译器可能忽略 inline 建议。

---

### C8. 函数重载和运算符重载？

**A：** 同名不同参数列表，编译期名字修饰 mangle 区分。运算符重载改变现有操作符对自定义类型行为，如 `operator+`。

---

### C9. 默认参数？

**A：** 声明中指定，从右向左。头文件与实现不要重复不一致。默认参数是编译期绑定。

---

### C10. 命名空间 namespace 用途？

**A：** 避免符号冲突，`std::`、`::` 全局。`using namespace std` 在头文件禁止。匿名 namespace 内部链接替代 static 文件作用域。

---

### C11. `extern` 关键字？

**A：** 声明变量/函数在其他翻译单元定义。`extern "C"` 取消 C++ name mangling，供 C/JNI 链接。

---

### C12. 宏的优缺点？现代替代？

**A：** 优点：条件编译、简单替换。缺点：无类型、难调试、副作用（`#define MAX(a,b) ((a)>(b)?(a):(b))` 多次求值）。用 const、inline、template、enum class 替代。

---

### C13. 前置声明 vs 包含头文件？

**A：** 指针/引用类型可用前置声明减少编译依赖。需要完整类型（继承、成员对象、sizeof）必须 include。

---

### C14. ODR（One Definition Rule）？

**A：** 每个非 inline 变量/函数整个程序唯一定义。inline 函数、模板实例化可有 ODR 例外。违反链接错误 duplicate symbol。

---

### C15. `.cpp` 和 `.h` 如何组织？

**A：** 声明放 .h，实现放 .cpp。模板实现常放 .h 或 .tpp。PIMPL 模式隐藏实现减编译依赖。

---

# 二、面向对象（Q16～Q30）

### C16. 封装继承多态？

**A：** 封装隐藏实现；继承 is-a 复用；多态基类指针调派生方法需 virtual。C++ 多继承，虚继承解决菱形。

---

### C17. 三种继承方式 public/protected/private？

**A：** public 继承：基 public→public，protected→protected。protected 继承：public 变 protected。private 继承：全变 private。常用 public 继承表达 is-a。

---

### C18. 构造函数初始化列表 vs 赋值？

**A：** 初始化列表直接构造成员；赋值先默认构造再 operator=。const/引用/无默认构造成员必须用初始化列表。效率更高。

---

### C19. 析构函数为什么常 virtual？

**A：** 通过基类指针 delete 派生对象时，非 virtual 只调基类析构，派生资源泄漏。多态基类析构应 virtual。

---

### C20. 纯虚函数和抽象类？

**A：** `= 0` 纯虚，类不可实例化。派生必须实现。接口用全纯虚类。可有非纯虚成员。

---

### C21. 虚函数表 vtable 布局？

**A：** 有 virtual 的类对象含 vptr 指向 vtable（函数指针数组）。派生 override 替换槽位。多重继承多 vptr。

---

### C22. 虚函数开销？

**A：** 每次调用间接寻址，无法 inline（除非 devirtualization）。vptr 每对象指针大小。CRTP/静态多态可避免。

---

### C23. override 和 final（C++11）？

**A：** `override` 显式重写，编译器检查签名。`final` 禁止进一步 override 或继承。

---

### C24. 多继承菱形问题？

**A：** D 继承 B、C，B/C 继承 A，D 有两份 A 子对象。虚继承 `virtual public A` 共享 A 基类，构造顺序复杂。

---

### C25. 友元 friend？

**A：** 打破封装，指定函数/类访问 private。非成员非继承。运算符重载常需 friend。

---

### C26. 静态成员变量和函数？

**A：** 静态成员类共享一份，类外定义分配存储。静态函数无 this，只能访问静态成员。单例可用 magic static。

---

### C27. 拷贝构造、拷贝赋值、移动构造、移动赋值？

**A：** Rule of Five：析构+四个。拷贝深复制资源；移动转移指针置 null 源。`= default` `= delete` 显式控制。

---

### C28. `= delete` 用途？

**A：** 禁止函数，如禁止拷贝 `MyClass(const MyClass&) = delete`、禁止隐式转换。

---

### C29. 对象模型：空类大小？

**A：** 空类 size 1（C++ 标准要求唯一地址）。有 virtual 至少 + vptr。有成员按对齐 padding。

---

### C30. RTTI 和 dynamic_cast？

**A：** Run-Time Type Information，`typeid`、`dynamic_cast`。需多态基类。有运行时开销。CRTP 静态 cast 更快。

---

# 三、内存管理（Q31～Q45）

### C31. 栈和堆区别？

**A：** 栈自动管理局部变量，LIFO，有限大小。堆 new/malloc 手动或智能指针，大小灵活，碎片化，分配慢。

---

### C32. new/delete 和 malloc/free？

**A：** new 调用构造+分配，delete 析构+释放。malloc 只分配字节不构造。混用未定义行为。数组 `new[]`/`delete[]` 配对。

---

### C33. 内存泄漏如何检测？

**A：** Valgrind、AddressSanitizer（-fsanitize=address）、Visual Studio CRT leak detection、重载 new 统计。

---

### C34. 野指针、悬空指针、双重释放？

**A：** 野指针未初始化；悬空 delete 后仍用；double free 崩溃。置 nullptr、智能指针、明确生命周期。

---

### C35. 智能指针三种？

**A：** unique_ptr 独占；shared_ptr 引用计数；weak_ptr 打破循环引用不增计数。`make_unique`/`make_shared` 异常安全。

---

### C36. shared_ptr 线程安全吗？

**A：** 引用计数原子操作线程安全。所指对象读写需另加锁。别从 this 构造 shared_ptr 用 enable_shared_from_this。

---

### C37. RAII 是什么？举例？

**A：** 构造获取资源析构释放。lock_guard、unique_ptr、fstream、Scope Guard。异常安全保证释放。

---

### C38. 右值引用和 std::move？

**A：** `T&&` 绑定临时量。move 转右值启用移动语义，不移动则拷贝。move 后源 valid但未指定状态。

---

### C39. 完美转发 perfect forwarding？

**A：** 模板 `T&&` + `std::forward<T>(arg)` 保持值类别传给构造函数。万能引用注意非转发场景不是万能引用。

---

### C40. RVO/NRVO 返回值优化？

**A：** 编译器省略拷贝直接构造到调用者。C++17 强制 copy elision 某些场景。不要 std::move 返回局部变量阻碍 NRVO。

---

### C41. placement new？

**A：** 已分配内存上构造对象，不分配。内存池、嵌入式。需手动调析构 `p->~T()`，不 delete 内存块。

---

### C42. 内存对齐 alignas alignof？

**A：** CPU 访问对齐地址更快。struct 有 padding。`alignas(16)` SIMD。`sizeof` 含 padding。

---

### C43. 自定义 allocator？

**A：** STL 容器可指定 Allocator 模板参数。内存池 allocator 减少碎片。PMR（C++17 polymorphic memory resources）。

---

### C44. 缓冲区溢出？

**A：** 数组越界写破坏栈 canary/返回地址。用 vector/string、边界检查、ASan、禁 unsafe C 函数 strcpy。

---

### C45. 为什么 delete this 危险？

**A：** delete 后对象销毁，不能再访问成员。仅特殊引用计数对象在确认无其他访问时用，极易 bug。

---

# 四、STL 标准库（Q46～Q60）

### C46. STL 六大组件？

**A：** 容器、迭代器、算法、仿函数、适配器、分配器。

---

### C47. vector 扩容机制？

**A：** 容量不足通常 2 倍 realloc，拷贝/移动所有元素，迭代器全部失效。`reserve` 预分配。`shrink_to_fit` 非强制。

---

### C48. deque 和 vector？

**A：** deque 分段连续，头尾 O(1) 插入。无 guarantee 连续内存，不能 &deque[0] 传 C API（慎用）。

---

### C49. list forward_list？

**A：** 双向/单向链表，插入 O(1) 不使其他迭代器失效（除被删元素）。无 random access。

---

### C50. map 底层？

**A：** 红黑树，key 有序 O(log n)。`map[key]` 不存在会默认构造 value。`insert`/`emplace` 更高效。

---

### C51. unordered_map 底层？

**A：** 哈希桶开链/开地址。均摊 O(1)。需 hash 和 equal。负载因子 rehash。无序。

---

### C52. set 和 bitset？

**A：** set 有序唯一集合。bitset 固定大小位集，位运算。

---

### C53. priority_queue 底层？

**A：** 默认 vector + make_heap，最大堆。`greater` 变最小堆。

---

### C54. 迭代器 category？

**A：** input/output/forward/bidirectional/random access。算法要求决定可用迭代器。list 双向，vector random。

---

### C55. 迭代器失效规则？

**A：** vector insert/resize 全失效；erase 之后失效；map erase 仅该元素；list 插入不失效（除删）。

---

### C56. emplace_back vs push_back？

**A：** emplace 原地构造传参数，避免临时对象。`push_back(T(...))` 可能多一次拷贝/移动。

---

### C57. algorithm 常用？

**A：** sort（O(n log n) introsort）、binary_search、find、transform、accumulate、lower_bound（有序）。

---

### C58. sort 自定义比较？

**A：** _lambda 或仿函数 `bool operator()(const T& a, const T& b)`。必须严格弱序，否则 UB。

---

### C59. string 小字符串优化 SSO？

**A：** 短串 buffer 放对象内无堆分配。实现定义阈值通常 15～22 字节。

---

### C60. tuple optional variant（C++17）？

**A：** tuple 异构固定组；optional 可能有值；variant 类型安全 union。visit 访问 variant。

---

# 五、现代 C++11/14/17/20（Q61～Q75）

### C61. auto 和 decltype？

**A：** auto 类型推导初始化式。decltype 表达式类型，`(x)` 若 x 是 lvalue 得 T&。尾置返回类型配合。

---

### C62. 范围 for？

**A：** `for (auto& x : container)` 基于 begin/end。别在循环中修改 vector 导致 rehash/失效。

---

### C63. lambda 捕获 `[=]` `[&]` `[this]`？

**A：** 值捕获拷贝；引用捕获注意悬空；this 捕获相当于 this 指针。mutable 可改值捕获副本。C++14 泛型 lambda auto 参数。

---

### C64. constexpr 和 const？

**A：** constexpr 编译期常量，可用于数组大小、模板参数。C++14 起 constexpr 函数可含循环。const 只读不一定编译期。

---

### C65. enum class？

**A：** 强类型枚举，不隐式转 int，需 `enum class E : uint8_t` 指定底层。避免命名污染。

---

### C66. 智能指针和 make 函数？

**A：** C++14 make_unique。make_shared 一次分配控制块+对象。异常安全：两个 new 之间可能 leak，make 单表达式。

---

### C67. 列表初始化 `{}`？

**A：** 统一初始化，防窄化转换 `int x{3.14}` 报错。initializer_list 构造函数优先可能坑 vector。

---

### C68. nullptr vs NULL？

**A：** NULL 可能是 0 或 `(void*)0`。nullptr 类型 `std::nullptr_t`， overload 解析正确。

---

### C69. 结构化绑定 C++17？

**A：** `auto [a,b] = pair/map element`。绑定 tuple、struct 成员。

---

### C70. if/switch 初始化语句 C++17？

**A：** `if (auto it = m.find(k); it != m.end())` 限制作用域。

---

### C71. std::filesystem？

**A：** 跨平台路径、遍历、copy、file_size。替代 boost::filesystem。

---

### C72. Concepts C++20？

**A：** `template<std::integral T>` 约束模板参数，错误信息清晰。requires 子句。

---

### C73. Coroutines C++20？

**A：** co_await/co_yield/co_return。异步 IO 框架可用。编译器生成状态机。

---

### C74. Modules C++20？

**A：** `import std;` 减少头文件编译时间。生态仍在演进。

---

### C75. span string_view C++17/20？

**A：** 非 owning 视图，避免拷贝。string_view 指向外部 char 需保证 lifetime。span 任意连续序列。

---

# 六、模板与元编程（Q76～Q88）

### C76. 函数模板和类模板？

**A：** `template<typename T> void f(T t)` 编译期实例化多份代码。类模板 vector<T>。

---

### C77. 模板特化和偏特化？

**A：** 全特化 `template<> class Foo<int>`。偏特化仅类模板 `template<typename T> class Foo<T*>`。函数模板仅全特化。

---

### C78. SFINAE？

**A：** Substitution Failure Is Not An Error，替换失败剔除 overload 不报错。enable_if、concept 之前常用。

---

### C79. typename 关键字在模板中？

**A：** `typename T::type` 告诉编译器 nested name 是类型。依赖名必须 typename。

---

### C80. 模板实例化时机？

**A：** 使用时隐式实例化。extern template 声明抑制实例化。显式 `template class Foo<int>`。

---

### C81. CRTP 奇异递归模板？

**A：** `class Derived : public Base<Derived>` 静态多态，编译期绑定无 vtable。Mixin 常用。

---

### C82. 类型 traits？

**A：** `is_same`、`enable_if`、`remove_reference`、`conditional`。type_traits 头文件。编译期分支。

---

### C83. 可变参数模板？

**A：** `template<typename... Args>` pack expansion。sizeof...(Args)。fold expression C++17。

---

### C84. 模板和宏选型？

**A：** 模板类型安全可调试。宏做条件编译、日志行号。能用模板不用宏。

---

### C85. 模板代码放 .h 原因？

**A：** 编译器需要完整定义实例化。分离编译需显式实例化声明。

---

### C86. ADL 参数依赖查找？

**A：** 命名空间关联函数随参数类型搜索。`using std::swap; swap(a,b)` 可找自定义 swap。

---

### C87. expression templates？

**A：** 延迟求值优化向量运算，Blitz++、Eigen 思想。避免临时 vector。

---

### C88. 模板元编程 TMP 用途？

**A：** 编译期计算斐波那契、类型列表、constexpr if 简化。Boost.MPL、Hana。

---

# 七、并发与内存模型（Q89～Q100）

### C89. std::thread 创建？

**A：** `thread t(func, args...)` join 或 detach。detach 后线程独立，析构前必须 join/detach 否则 terminate。

---

### C90. mutex lock_guard unique_lock？

**A：** lock_guard RAII 简单锁。unique_lock 可 defer_lock、try_lock、超时、配合 condition_variable。

---

### C91. condition_variable 用法？

**A：** `wait(lock, pred)` 防虚假唤醒。notify_one/notify_all。谓词检查条件。

---

### C92. atomic 内存序 memory order？

**A：** memory_order_relaxed/acquire/release/acq_rel/seq_cst。seq_cst 默认最强。无锁数据结构需仔细设计。

---

### C93. 死锁 C++ 如何避免？

**A：** std::lock 同时锁多 mutex；lock hierarchy；try_lock 退避。scoped_lock C++17 多锁。

---

### C94. future promise async？

**A：** promise 设值，future get 阻塞取。async launch policy async/deferred。packaged_task。

---

### C95. 线程池自己实现要点？

**A：** 任务队列+工作线程+条件变量+停止 flag。注意异常传播、队列上限。

---

### C96. volatile 在 C++ 中等于 atomic 吗？

**A：** **不等于**。volatile 防优化不保证原子性/同步。多线程用 atomic/mutex。volatile 用于 MMIO 硬件寄存器。

---

### C97. 读写锁 shared_mutex C++17？

**A：** shared_lock 多读，unique_lock 写。读多写少场景。

---

### C98. thread_local？

**A：** 每线程独立副本。静态 thread_local 线程结束时析构。类似 Java ThreadLocal 但类型安全。

---

### C99. 无锁编程难点？

**A：** ABA 问题、hazard pointer、内存序、调试难。除非必要用 mutex。

---

### C100. OpenMP 简要？

**A：** `#pragma omp parallel for` 数据并行。编译器支持。科学计算常用。

---

# 八、性能、工程与场景（Q101～C120）

### C101. 为什么 C++ 适合高性能场景？

**A：** 零开销抽象、无 GC 停顿、内存可控、SIMD、模板内联、确定析构时机。

---

### C102. CPU cache 友好编程？

**A：** 连续内存 vector 优于 list；结构体数组 SoA vs AoS；避免 false sharing（padding 对齐 cache line 64B）。

---

### C103. 内联汇编？

**A：** `asm` 嵌入指令。编译器 intrinsics `_mm_add_ps` 更可移植。ARM NEON、x86 SSE/AVX。

---

### C104. PIMPL 模式？

**A：** Pointer to IMPLementation，公开类只含 impl 指针，实现细节放 .cpp，减编译依赖、ABI 稳定。

---

### C105. 异常 vs 错误码？

**A：** 异常自动传播栈 unwind，RAII 清理。实时/嵌入式常禁异常用 expected/Status。Google 风格部分项目 noexcept。

---

### C106. noexcept 作用？

**A：** 承诺不抛异常，移动构造函数应 noexcept vector 才用 move。违反 terminate。

---

### C107. Google 编码规范要点？

**A：** 智能指针、RAII、禁 RTTI/异常（旧版）、命名清晰、单元测试。现代项目各异。

---

### C108. CMake 简要？

**A：** `CMakeLists.txt` 定义 project、add_library、target_link_libraries。跨平台生成 Makefile/VS。

---

### C109. sanitizers 有哪些？

**A：** ASan 内存、TSan 数据竞争、UBSan 未定义行为、MSan 未初始化。`-fsanitize=address` 编译链接。

---

### C110. JNI 与 C++ 交互注意？

**A：** JNIEnv* 线程绑定；LocalRef DeleteLocalRef；GlobalRef；FindClass GetMethodID；异常 CheckException；别缓存 jclass 不 GlobalRef。

---

### C111. 如何实现线程安全单例？

**A：** C++11 局部 static `getInstance(){ static Singleton s; return s; }` magic static 线程安全。DCL 需 memory barrier 已过时。

---

### C112. 虚继承构造顺序？

**A：** 虚基类由最派生类直接构造。非虚基类按声明顺序。成员按声明顺序构造。

---

### C113. 重载 operator= 为什么要防自赋值？

**A：** `if (this == &other) return *this;` 否则可能 delete 自身资源后拷贝。copy-and-swap 惯用法更安全。

---

### C114. copy-and-swap 惯用法？

**A：** 按值传参拷贝，swap 交换成员。自动异常安全、统一 copy/move 赋值。

---

### C115. 如何实现 LRU Cache（C++）？

**A：** unordered_map + list，map 存 key→list iterator，get/put O(1)。面试高频。

---

### C116. shared_ptr 循环引用举例？

**A：** A、B 互相 shared_ptr 成员，计数永不为 0。一方改 weak_ptr 打破。

---

### C117. 移动语义在 vector push 中的应用？

**A：** `push_back(string("large"))` 移动临时量。右值引用避免拷贝。emplace 原地构造。

---

### C118. 为什么 list sort 不能用 std::sort？

**A：** sort 需 random access iterator。list 用 list::sort 归并 O(n log n)。

---

### C119. 调试 core dump？

**A：** ulimit -c unlimited；gdb ./prog core；bt 栈；info locals。编译 -g -O0。

---

### C120. C++ 后端面试手写题常见？

**A：** 智能指针实现、字符串类、LRU、生产者消费者、线程池、shared_ptr 控制块、移动语义 String 类。

---

# 附录：与 Java 对照速查

| 概念 | Java | C++ |
|------|------|-----|
| 内存 | GC | RAII / 智能指针 |
| 字符串 | String 不可变 | std::string 可变 |
| 泛型 | 擦除 | 模板实例化 |
| 多态 | interface + 虚表类似 | virtual + 多继承 |
| 并发 | synchronized/JUC | mutex/atomic |

---

*120 题 · 建议 12 天每天 10 题 · 配合 LeetCode C++ 标签练习*
