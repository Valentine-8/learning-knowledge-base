# Cursor 操作手册

> **适用**：Windows · Cursor IDE（基于 VS Code）  
> **你**：赵晨宇 · 日常写 Java / 用 Agent 辅助开发 / Git 管理学习文档与项目  
> **最后更新**：2026-06

---

## 目录

1. [Cursor 是什么](#一cursor-是什么)
2. [界面与布局（详细）](#二界面与布局详细)
3. [快捷键（Windows）](#三快捷键windows)
4. [Git 完整指南](#四git-完整指南)
5. [AI：Chat / Agent / Composer](#五aichat--agent--composer)
6. [Rules、Skills 与项目配置](#六rulesskills-与项目配置)
7. [终端、扩展与设置](#七终端扩展与设置)
8. [推荐工作流（结合本仓库）](#八推荐工作流结合本仓库)
9. [常见问题](#九常见问题)

---

## 一、Cursor 是什么

| 项 | 说明 |
|----|------|
| 本质 | **VS Code 分支** + 内置 AI（Chat、Tab 补全、Agent 改多文件） |
| 和 VS Code 关系 | 界面、扩展、快捷键 **大部分相同**；设置文件也在 `%APPDATA%\Cursor\User\` |
| 适合你怎么用 | 写代码、让 Agent 改仓库、Git 提交、复习文档也在 Cursor 里编辑 |

**两个工作表面（2026 新版）**

| 表面 | 打开方式 | 用途 |
|------|----------|------|
| **传统编辑器** | 默认打开项目 | 写代码、看 diff、Git 面板、调试 |
| **Agents Window** | `Ctrl+Shift+P` → 输入 `Agents Window` | 多 Agent 并行、worktree 隔离任务 |

可随时在两者之间切换；**Git 提交**通常在 **编辑器 + 源代码管理** 里做最直观。

---

## 二、界面与布局（详细）

### 2.1 主要区域

```
┌──────────────────────────────────────────────────────────────┐
│  菜单栏  File  Edit  Selection  View  Go  Run  Terminal  Help │
├──────────┬───────────────────────────────┬───────────────────┤
│          │                               │                   │
│  活动栏   │      编辑器区（多 Tab）          │   侧边面板         │
│  (图标)  │                               │  Chat / Agent     │
│          │                               │  或 大纲/搜索      │
│  资源管理 │                               │                   │
│  搜索    │                               │                   │
│  源代码管理│                               │                   │
│  运行调试 │                               │                   │
│  扩展    │                               │                   │
├──────────┴───────────────────────────────┴───────────────────┤
│  面板区：终端 / 问题 / 输出 / 调试控制台                          │
└──────────────────────────────────────────────────────────────┘
│  状态栏：分支名、错误数、编码、Cursor 模型等                        │
└──────────────────────────────────────────────────────────────┘
```

### 2.2 活动栏（最左侧竖条）

| 图标 | 名称 | 作用 |
|------|------|------|
| 文件 | 资源管理器 | 看文件夹、新建/删除文件 |
| 放大镜 | 搜索 | 全局搜索文本 |
| 分支 | **源代码管理** | **Git 提交、分支、合并**（重点） |
| 播放 | 运行和调试 | Java/Node 调试 |
| 方块 | 扩展 | 安装插件 |

**隐藏/显示活动栏**：菜单 **View → Appearance → Activity Bar Position**（可放顶部/隐藏）。

### 2.3 调整布局 — 常用操作

| 需求 | 操作 |
|------|------|
| **显示/隐藏左侧栏** | `Ctrl+B` |
| **显示/隐藏底部终端** | `` Ctrl+` ``（反引号，Esc 下面） |
| **显示/隐藏右侧 AI 面板** | `Ctrl+L` 打开 Chat；或拖拽面板边缘 |
| **编辑器分屏** | 编辑器 Tab 右键 → **Split Right / Split Down**；或 `Ctrl+\` |
| **把 Chat 移到左侧/底部** | 拖拽 Chat 面板标题栏到目标位置 |
| **放大字体** | `Ctrl+=` 缩小 `Ctrl+-` |
| **Zen 专注模式** | `Ctrl+K` 然后 `Z`（连按） |
| **重置布局乱了** | `View → Appearance → Reset View Locations` |

### 2.4 布局预设（Cursor 2.3+）

1. 菜单 **View → Appearance → Layout**（或命令面板搜 `Layout`）  
2. 可 **拖拽** 面板重组  
3. 部分版本支持 **保存布局预设** — 命令面板搜 `Save Layout` / `Restore Layout`

**推荐布局（写代码 + AI）**

- 左：资源管理器  
- 中：代码（可左右分屏：代码 | diff）  
- 右：Chat/Agent（窄一点）  
- 下：终端（Git 命令、Maven、运行）

### 2.5 多根工作区（Multi-root）

你的 `d:\学习\java` 和 `D:\Users\lemon\mall` 可同时打开：

1. **File → Add Folder to Workspace…**  
2. **File → Save Workspace As…** 存成 `xxx.code-workspace`  
3. 下次双击 `.code-workspace` 一次打开多个项目  

Agent 3.2+ 在 Agents Window 里也支持 **multi-root** 跨仓库改代码。

### 2.6 状态栏

| 位置 | 信息 | 点击 |
|------|------|------|
| 左下 | 当前 **Git 分支** | 可切换分支 |
| 左下 | 同步图标 ↑↓ | pull / push |
| 右下 | 编码 UTF-8、缩进 | 可改 |

---

## 三、快捷键（Windows）

> Mac 用户把 `Ctrl` 换成 `Cmd`。

### 3.1 通用

| 快捷键 | 功能 |
|--------|------|
| `Ctrl+Shift+P` | **命令面板**（万能入口，搜任何命令） |
| `Ctrl+P` | 快速打开文件 |
| `Ctrl+Shift+F` | 全局搜索 |
| `Ctrl+Shift+E` | 聚焦资源管理器 |
| `Ctrl+Shift+G` | 聚焦 **源代码管理（Git）** |
| `Ctrl+Shift+` ` | 聚焦终端 |
| `Ctrl+S` | 保存 |
| `Ctrl+Shift+S` | 另存为 |
| `Ctrl+W` | 关闭当前 Tab |
| `Ctrl+Tab` | 切换 Tab |

### 3.2 编辑

| 快捷键 | 功能 |
|--------|------|
| `Ctrl+D` | 选中下一个相同词 |
| `Ctrl+Shift+L` | 选中所有相同词 |
| `Alt+↑/↓` | 移动当前行 |
| `Shift+Alt+↑/↓` | 复制当前行 |
| `Ctrl+/` | 行注释 |
| `Ctrl+Shift+K` | 删除行 |
| `F2` | 重命名符号 |
| `Ctrl+点击` | 跳转到定义 |

### 3.3 AI 相关

| 快捷键 | 功能 |
|--------|------|
| `Ctrl+L` | 打开 **Chat**（侧边对话） |
| `Ctrl+I` | **Composer / Inline Agent**（部分版本为行内或多文件编辑） |
| `Tab` | 接受 **Copilot 式补全**建议 |
| `Esc` | 拒绝补全 |

具体以 **Cursor Settings → Keyboard Shortcuts** 为准（会随版本微调）。

### 3.4 自定义快捷键

1. `Ctrl+K` `Ctrl+S` 打开键盘快捷方式  
2. 搜索命令名修改  
3. 或 **File → Preferences → Keyboard Shortcuts**

---

## 四、Git 完整指南

> **原则**：Agent 改完代码 → **你先 diff Review** → 再 commit（见 [AI时代程序员与代码.md](../../18-AI-Engineering/AI时代程序员与代码.md)）。

### 4.1 首次：仓库初始化 / 克隆

**已有远程仓库（clone）**

```powershell
cd D:\你想放的目录
git clone https://github.com/xxx/yyy.git
cd yyy
cursor .   # 或用 Cursor 菜单 File → Open Folder
```

**本地新项目第一次用 Git**

```powershell
cd d:\学习\java
git init
git add .
git commit -m "init: 学习文档库"
# 若已有远程：
git remote add origin https://github.com/xxx/yyy.git
git push -u origin main
```

**Cursor 里确认**：左下角状态栏应显示分支名（如 `main`）；没有则未 init 或未打开 git 根目录。

---

### 4.2 日常：查看改了什么

| 方式 | 操作 |
|------|------|
| **源代码管理** | `Ctrl+Shift+G` → 看 **Changes** 列表 |
| 单文件 diff | 点击 changed 文件 → 右侧 diff 视图 |
| 终端 | `git status` |
| 详细 diff | `git diff`（未暂存） / `git diff --staged`（已暂存） |

**颜色**：绿色新增、蓝色修改、红色删除。

---

### 4.3 提交（Commit）— 图形界面（推荐新手）

1. `Ctrl+Shift+G` 打开源代码管理  
2. 在 **Changes** 里 hover 文件 → 点 **`+`**（Stage / 暂存）  
   - 或点 **Changes** 旁 **`+`** 暂存全部  
3. 上方输入框写 **提交说明**（见 4.8 规范）  
4. 点 **`✓ Commit`** 或 `Ctrl+Enter`  

**仅提交部分行（高级）**

- 打开 diff → 选中某 hunk → 右键 **Stage Selected Ranges**

---

### 4.4 提交 — 命令行

```powershell
# 查看状态
git status

# 暂存指定文件
git add 简历.md
git add 04-C++嵌入式/

# 暂存全部（慎用，先 status）
git add .

# 提交
git commit -m "docs: 添加 Cursor 操作手册"

# 一次完成（仅跟踪过的文件修改）
git commit -am "fix: 修正 README 链接"
```

---

### 4.5 推送到远程（Push）

**图形界面**

1. 提交后源代码管理面板出现 **Sync Changes** 或 **↑ Push**  
2. 点击同步  

**命令行**

```powershell
# 第一次推送到远程 main
git push -u origin main

# 之后
git push
```

**认证**：GitHub 常用 HTTPS + Personal Access Token，或 SSH 密钥。

---

### 4.6 拉取（Pull）

```powershell
git pull          # 拉取并合并当前分支
git pull --rebase # 变基拉取（历史更直，团队有要求时用）
```

Cursor：源代码管理 **…** 菜单 → **Pull**。

**习惯**：开始干活前先 `git pull`，减少冲突。

---

### 4.7 分支（Branch）

**为什么要分支**：主分支保持稳定；新功能、面试文档整理在 **feature** 分支做。

| 操作 | 图形界面 | 命令行 |
|------|----------|--------|
| 看当前分支 | 状态栏左下角 | `git branch` |
| 新建分支 | 状态栏点击分支名 → Create new branch | `git checkout -b feature/cursor-doc` |
| 切换分支 | 同上选择 | `git checkout main` |
| 删除本地分支 | 命令面板 Git: Delete Branch | `git branch -d feature/xxx` |

**命名建议**：`feature/xxx`、`fix/xxx`、`docs/xxx`。

---

### 4.8 合并（Merge）

**场景**：在 `feature/cursor-doc` 上改完，合并回 `main`。

```powershell
git checkout main
git pull
git merge feature/cursor-doc
# 无冲突则：
git push
```

**图形界面**

1. 切换到 **main**（状态栏点分支名）  
2. 命令面板 `Git: Merge Branch...` → 选 `feature/cursor-doc`  

**合并后是否删分支**

```powershell
git branch -d feature/cursor-doc
```

---

### 4.9 冲突（Conflict）怎么处理

合并或 pull 时出现 **CONFLICT**：

1. 源代码管理里冲突文件标 **`!`**  
2. 打开文件，看到：

```
<<<<<<< HEAD
你的 main 上的内容
=======
分支上的内容
>>>>>>> feature/xxx
```

3. 点击 **Accept Current / Incoming / Both**（Cursor 和 VS Code 一样有按钮）  
4. 或手动删标记，保留正确内容  
5. 保存 → `git add 冲突文件` → `git commit`（完成合并提交）

**放弃合并**

```powershell
git merge --abort
```

---

### 4.10 暂存工作（Stash）

临时切换分支，但当前改动还不想 commit：

```powershell
git stash
git checkout other-branch
# 干别的...
git checkout original-branch
git stash pop
```

命令面板：`Git: Stash`。

---

### 4.11 撤销与回退（谨慎）

| 场景 | 命令 | 风险 |
|------|------|------|
| 未 add，丢弃单文件修改 | `git checkout -- 文件` | 改动丢失 |
| 已 add 未 commit | `git reset HEAD 文件` | 仅取消暂存 |
| 撤销最后一次 commit，保留改动 | `git reset --soft HEAD~1` | 中等 |
| 撤销 commit 且丢弃改动 | `git reset --hard HEAD~1` | **危险** |
| 已 push 的 commit | **不要 hard reset**；用 `git revert` | 安全 |

**图形界面**：文件右键 → **Discard Changes**（未提交的改动会丢）。

---

### 4.12 提交信息规范（建议）

```
类型: 简短说明（50 字内）

可选正文
```

| 类型 | 含义 | 示例 |
|------|------|------|
| `feat` | 新功能 | `feat: mall 增加 RAG 接口` |
| `fix` | 修复 | `fix: 修复库存扣减 SQL` |
| `docs` | 文档 | `docs: 更新 Cursor 操作手册` |
| `refactor` | 重构 | `refactor: 提取 ServiceUrlManager` |
| `chore` | 杂项 | `chore: 更新 gitignore` |

**本仓库**（纯 Markdown 学习库）常用：`docs:`。

---

### 4.13 .gitignore（别提交垃圾）

在项目根建 `.gitignore`：

```gitignore
# IDE
.idea/
*.iml
.vscode/
# 注意：.cursor/rules 有时要提交，.cursor 缓存不要
.cursor/projects/

# Java
target/
*.class

# 系统
Thumbs.db
Desktop.ini

# 密钥（永远不要提交）
.env
*.pem
```

---

### 4.14 Cursor Agent 与 Git 协作

| 步骤 | 做什么 |
|------|--------|
| 1 | Agent 改代码前：最好 **commit 或 stash** 当前干净状态 |
| 2 | Agent 完成后：**源代码管理看 diff** |
| 3 | 分多次 commit（不要一次 `add .`  blindly） |
| 4 | 用 **worktree** 做实验性大改（见第五节） |

**Agent Window 命令（隔离改动）**

- `/worktree` — 在独立 git worktree 里跑 Agent，不污染主工作区  
- `/apply-worktree` — 把 worktree 改动应用回主 checkout  
- `/delete-worktree` — 删除临时 worktree  

配置：项目根 `.cursor/worktrees.json`（可选 setup 脚本）。

---

## 五、AI：Chat / Agent / Composer

### 5.1 三种方式对比

| 方式 | 打开 | 适合 |
|------|------|------|
| **Tab 补全** | 打字时自动 | 单行/小片段 |
| **Chat** | `Ctrl+L` | 问问题、解释代码、小改建议 |
| **Agent / Composer** | Chat 里选 Agent 模式 / `Ctrl+I` | **多文件修改**、跑终端、实现功能 |

### 5.2 Chat 使用技巧

- 用 **`@`** 引用上下文：`@Files`、`@Folders`、`@Codebase`、`@Docs`  
- 选中代码 → `Ctrl+L` 自动带入选中内容  
- **Ask 模式**：只回答不改文件  
- **Agent 模式**：会读文件、改文件、跑命令（需你批准或开 auto-run）

### 5.3 Agent 模式注意

1. **说清约束**：语言、框架、不要改哪些文件  
2. **小步提交**：一个功能一个 commit  
3. **开 Rules**：见第六节  
4. **终端 auto-run**：Settings → Agent → 可白名单 `npm test`、`mvn compile`，**禁止** `git push --force`

### 5.4 Agents Window（多任务并行）

```
Ctrl+Shift+P → Agents Window
```

- 多个 Agent Tab 并行  
- `/multitask` 拆任务给子 Agent  
- `/best-of-n` 多模型对比（各用 worktree 隔离）  
- 适合：一边改 mall，一边整理 `d:\学习\java` 文档

### 5.5 模型选择

- Settings → **Models**  
- 复杂架构/面试文档：强推理模型  
- 日常 CRUD：快速模型  
- 注意 **用量/配额**（Pro 有 Auto + API 池）

---

## 六、Rules、Skills 与项目配置

### 6.1 项目 Rules（约束 AI）

| 位置 | 作用 |
|------|------|
| `.cursor/rules/*.mdc` | 项目级规则（推荐） |
| `.cursorrules`（根目录） | 旧式，仍可用 |
| **Cursor Settings → Rules** | 用户全局规则 |

**示例**（Java 项目）：「不提交密钥；改代码最小 diff；FollowUpAI 租户隔离必须人工 Review」。

### 6.2 Skills

- 用户级：`~/.cursor/skills/`  
- 你已有：`create-rule`、`update-cursor-settings`、`frontend-design` 等  
- Agent 会在相关任务时 **自动读 SKILL.md**

### 6.3 推荐目录（可选）

```
项目根/
├── .cursor/
│   ├── rules/
│   │   └── java-backend.mdc
│   └── worktrees.json
├── .gitignore
└── ...
```

---

## 七、终端、扩展与设置

### 7.1 集成终端

| 操作 | 快捷键 |
|------|--------|
| 打开/关闭 | `` Ctrl+` `` |
| 新建终端 | `` Ctrl+Shift+` `` |
| 杀进程 | 终端里 `Ctrl+C` |

**默认 Shell**：Settings 搜 `terminal.integrated.defaultProfile.windows` → PowerShell 或 Git Bash。

**多项目**

```powershell
cd D:\Users\lemon\mall
mvn -q -DskipTests compile
```

### 7.2 推荐扩展（Java 开发）

| 扩展 | 用途 |
|------|------|
| Extension Pack for Java | 语言支持、Maven、调试 |
| Spring Boot Extension Pack | Boot 项目 |
| GitLens | Git 历史、 blame（可选） |
| Markdown All in One | 你大量 .md 文档预览 |

安装：`Ctrl+Shift+X` → 搜索 → Install。

### 7.3 常用设置

打开：`Ctrl+,` 或 **File → Preferences → Settings**

| 设置 | 建议 |
|------|------|
| `Auto Save` | `afterDelay` 防丢 |
| `Format On Save` | Java 项目可开 |
| `Editor: Tab Size` | Java 4，前端 2 |
| `Files: Encoding` | UTF-8 |
| `Git: Enable Smart Commit` | 可按习惯 |

**settings.json 直接编辑**：命令面板 → `Preferences: Open User Settings (JSON)`。

### 7.4 用户配置路径（Windows）

```
C:\Users\lemon\AppData\Roaming\Cursor\User\settings.json
C:\Users\lemon\AppData\Roaming\Cursor\User\keybindings.json
```

---

## 八、推荐工作流（结合本仓库）

### 8.1 整理学习文档（`d:\学习\java`）

```
1. git pull
2. 改 md → Ctrl+S
3. Ctrl+Shift+G 看 diff
4. commit: docs: xxx
5. git push
```

### 8.2 公司项目 + AI

```
1. 新分支 feature/xxx
2. Agent 实现 → Review diff
3. mvn test / 手测
4. commit + push → 提 PR（若团队用 Gitee/GitLab）
```

### 8.3 面试前

- 本仓库：`03-求职面试/面试前速查.md`  
- C++ 岗：`04-C++嵌入式/面试前速查-C++嵌入式.md`  
- 在 Cursor 里 **Markdown 预览**：`Ctrl+Shift+V`

### 8.4 文档导航

| 需求 | 文档 |
|------|------|
| 阅读顺序 | [00-阅读指南.md](./阅读指南.md) |
| AI 与代码 | [AI时代程序员与代码.md](../../18-AI-Engineering/AI时代程序员与代码.md) |

---

## 九、常见问题

### Q1：Git 面板是空的 / 没有分支名？

- 当前文件夹不是 git 仓库 → `git init` 或 `clone`  
- 或打开的是子文件夹，根目录没有 `.git`

### Q2：Commit 按钮灰色？

- 没有 **暂存（Stage）** 文件  
- 或提交说明为空（部分配置要求）

### Q3：Push 被拒绝 rejected？

```powershell
git pull --rebase
git push
```

或远程有新提交，先 pull 再 push。

### Q4：Agent 改太多，想全部撤销？

```powershell
git checkout -- .
# 或
git reset --hard HEAD
```

**未 commit 的改动会丢失**，慎用。

### Q5：中文路径乱码？

- 终端：`chcp 65001`  
- Git：`git config --global core.quotepath false`  
- 文件编码 UTF-8

### Q6：Cursor 和 VS Code 能共存吗？

- 可以；扩展需分别安装  
- 不要同时用两个打开同一工作区抢锁（一般没问题）

### Q7：隐私 / 代码上传？

- Settings → **Privacy** / **Data** 查看是否开启 Privacy Mode  
- 公司代码按 **公司政策**；敏感仓库关 indexing 或用企业版

---

## 附录 A · Git 命令速查卡

```powershell
git status              # 状态
git add <file>          # 暂存
git commit -m "msg"     # 提交
git push                # 推送
git pull                # 拉取
git branch              # 分支列表
git checkout -b feat/x  # 新建并切换
git merge feat/x        # 合并
git log --oneline -10   # 最近 10 条提交
git diff                # 未暂存 diff
git stash               # 暂存工作区
```

---

## 附录 B · 本手册维护

| 版本 | 日期 | 说明 |
|------|------|------|
| 1.0 | 2026-06 | 初版：布局、Git、Agent、Windows 快捷键 |

发现 Cursor 大版本界面变化 → 更新第二节、第五节。

---

## 关联文档

| 文档 | 用途 |
|------|------|
| [AI时代程序员与代码.md](../../18-AI-Engineering/AI时代程序员与代码.md) | Agent 改代码怎么 Review |
| [00-阅读指南.md](./阅读指南.md) | 学习文档阅读顺序 |
| [Cursor 官方文档](https://cursor.com/docs) | 最新功能 |

← [05-工具与效率 README](./README.md)
