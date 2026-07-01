# 02 · 分支、合并与 rebase

## 分支

```bash
git switch -c feature/order
git switch main
```

分支是指向 commit 的可移动指针。

## merge

```bash
git switch main
git merge feature/order
```

- **fast-forward**：main 直接前移
- **三方合并**：产生 merge commit
- **冲突**：手动改文件 → `git add` → `git commit`

## rebase

```bash
git switch feature/order
git rebase main
```

把 feature 的 commit **接到** main 最新之后，历史线性。

**黄金法则**：**不要 rebase 已 push 到公共分支的历史**（除非团队约定）。

## cherry-pick

```bash
git cherry-pick <commit-sha>
```

只拿某个提交到当前分支（热修复常用）。

→ [03-协作工作流](./03-协作工作流.md)
