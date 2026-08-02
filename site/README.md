# GitHub Pages 静态站

本仓库使用 [Docsify](https://docsify.js.org/) 将现有 Markdown **直接**渲染为可浏览网站，无需把 hundreds 篇文档再导出一遍。

## 在线地址

启用 Pages 后访问：

**https://valentine-8.github.io/learning-knowledge-base/**

（首次启用后可能需等待 1～3 分钟）

## 首次启用（GitHub 网页操作）

1. 打开 https://github.com/Valentine-8/learning-knowledge-base/settings/pages  
2. **Build and deployment → Source** 选 **Deploy from a branch**  
3. **Branch** 选 `main`，文件夹选 **`/ (root)`**  
4. 保存后等待部署完成  

## 本地预览

在项目根目录执行：

```bash
npx serve .
```

浏览器打开提示的地址（通常是 http://localhost:3000），即可预览与线上一致的 Docsify 站点。

## 站点文件说明

| 文件 | 作用 |
|------|------|
| `index.html` | Docsify 入口 |
| `_sidebar.md` | 左侧导航 |
| `_navbar.md` | 顶栏快捷链接 |
| `_coverpage.md` | 封面页 |
| `404.html` | GitHub Pages SPA 路由回退 |
| `.nojekyll` | 禁用 Jekyll，避免 `_` 开头文件被忽略 |
| `site/beige.css` | 米色阅读主题 |

## 阅读入口

站点默认首页 → [阅读指南](../技术成长/00-通用/01-阅读指南.md)

侧边栏已收录各板块 README；正文内链接点击后会在站点内跳转。左上角 **搜索框** 可全文检索（中文支持）。

## 注意事项

- 修改 `_sidebar.md` 可调整导航，无需改 HTML  
- 新增 Markdown 后 push 即可，**不用重新 build**  
- 若直接访问深层链接 404，确认 `404.html` 已随仓库部署  
