#!/usr/bin/env python3
"""Build a single self-contained, offline HTML reader for the EP7 Guide.

Reads all Markdown chapters, renders them with the `markdown` library, and
writes `EP7-Guide/index.html` (placed at the guide root so relative image
paths like `images/...` resolve correctly).

Usage:
    python EP7-Guide/scripts/build_html.py
"""
import html
import os
import re

import markdown

ROOT = os.path.join(os.path.dirname(__file__), "..")

HOME = "README"
BASE_CHAPTERS = [
    "01-第一次拿到EP7",
    "02-认识EP7",
    "03-第一次开机设置",
    "04-模式转盘",
    "05-14-42EZ镜头",
    "06-40-150R镜头",
    "07-第一次出去拍照",
    "08-拍人像",
    "09-拍风景",
    "10-夜景",
    "11-菜单详解",
    "12-常见问题",
]
ADV_CHAPTERS = [
    "13-RAW后期入门",
    "14-视频与Vlog",
    "15-旅行摄影",
    "16-术语表",
]

MD = markdown.Markdown(
    extensions=["tables", "fenced_code", "sane_lists", "attr_list", "md_in_html"]
)


def read(stem: str) -> str:
    path = os.path.join(ROOT, stem + ".md")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def first_heading(text: str, fallback: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


def strip_prefix(stem: str) -> str:
    return re.sub(r"^\d+-", "", stem)


def render(stem: str) -> tuple[str, str]:
    raw = read(stem)
    title = first_heading(raw, strip_prefix(stem))
    MD.reset()
    body = MD.convert(raw)
    # Rewrite internal .md links to in-page anchors
    body = re.sub(
        r'href="([0-9A-Za-z\-\u4e00-\u9fff]+)\.md"',
        lambda m: f'href="#{slug(m.group(1))}"',
        body,
    )
    body = body.replace('href="README.md"', f'href="#{slug(HOME)}"')
    return title, body


def slug(stem: str) -> str:
    m = re.match(r"(\d+)-", stem)
    if m:
        return "ch" + m.group(1)
    if stem == HOME:
        return "home"
    return "sec-" + (re.sub(r"[^0-9A-Za-z]+", "-", stem).strip("-").lower() or "x")


def nav_item(stem: str, title: str) -> str:
    return f'<li><a class="nav-link" data-target="{slug(stem)}" href="#{slug(stem)}">{html.escape(title)}</a></li>'


def build() -> None:
    sections = []
    nav_home = ""
    nav_base = []
    nav_adv = []

    # Home
    t, b = render(HOME)
    nav_home = nav_item(HOME, "首页 · 总览")
    sections.append(section_html(HOME, b))

    for i, stem in enumerate(BASE_CHAPTERS):
        t, b = render(stem)
        nav_base.append(nav_item(stem, t))
        sections.append(section_html(stem, b))

    for stem in ADV_CHAPTERS:
        t, b = render(stem)
        nav_adv.append(nav_item(stem, t))
        sections.append(section_html(stem, b))

    nav = f"""
      <ul class="nav-group">{nav_home}</ul>
      <div class="nav-title">基础篇</div>
      <ul class="nav-group">{''.join(nav_base)}</ul>
      <div class="nav-title">进阶篇</div>
      <ul class="nav-group">{''.join(nav_adv)}</ul>
    """

    out = PAGE.replace("{{NAV}}", nav).replace("{{SECTIONS}}", "\n".join(sections))
    dest = os.path.join(ROOT, "index.html")
    with open(dest, "w", encoding="utf-8") as f:
        f.write(out)
    print("wrote", os.path.abspath(dest))
    print("chapters:", 1 + len(BASE_CHAPTERS) + len(ADV_CHAPTERS))


def section_html(stem: str, body: str) -> str:
    return f'<article class="chapter" id="{slug(stem)}">\n{body}\n</article>'


PAGE = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>从零开始使用 Olympus PEN E-P7 · 网页版</title>
<style>
:root{
  --paper:#f5f0e6; --ink:#2c2a24; --muted:#6b6355; --line:#d8cfbf;
  --brown:#8a7f6e; --accent:#5c7a4a; --warm:#b5651d; --card:#fffdf8;
  --sidebar:#efe8da; --code-bg:#2b2a26; --code-ink:#f0ead9;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{
  margin:0; background:var(--paper); color:var(--ink);
  font-family:"Microsoft YaHei","PingFang SC","Segoe UI",system-ui,sans-serif;
  line-height:1.75; font-size:16px;
}
a{color:var(--warm); text-decoration:none}
a:hover{text-decoration:underline}

/* Layout */
.app{display:flex; min-height:100vh}
.sidebar{
  width:290px; flex:0 0 290px; background:var(--sidebar);
  border-right:1px solid var(--line); position:sticky; top:0; height:100vh;
  overflow-y:auto; padding:22px 16px 60px;
}
.brand{font-weight:700; font-size:18px; margin:4px 8px 6px; color:var(--ink)}
.brand small{display:block; font-weight:400; font-size:12px; color:var(--muted); margin-top:4px}
.nav-title{font-size:12px; letter-spacing:.12em; color:var(--muted); margin:18px 10px 6px; text-transform:uppercase}
.nav-group{list-style:none; margin:0; padding:0}
.nav-group li{margin:1px 0}
.nav-link{
  display:block; padding:8px 12px; border-radius:8px; color:var(--ink);
  font-size:14px; transition:background .15s, color .15s;
}
.nav-link:hover{background:#e4dbca; text-decoration:none}
.nav-link.active{background:var(--brown); color:#fff}

.main{flex:1 1 auto; min-width:0; display:flex; justify-content:center}
.reader{width:100%; max-width:860px; padding:40px 44px 120px}

.topbar{
  display:none; position:sticky; top:0; z-index:20; background:var(--sidebar);
  border-bottom:1px solid var(--line); padding:10px 16px; align-items:center; gap:12px;
}
.topbar .t{font-weight:700}
.menu-btn{
  border:1px solid var(--brown); background:transparent; color:var(--ink);
  border-radius:8px; padding:6px 12px; font-size:14px; cursor:pointer;
}

/* Chapter content */
.chapter{display:none; animation:fade .25s ease}
.chapter.active{display:block}
@keyframes fade{from{opacity:0; transform:translateY(6px)}to{opacity:1; transform:none}}
.chapter h1{font-size:30px; line-height:1.3; border-bottom:3px solid var(--brown); padding-bottom:14px; margin:0 0 22px}
.chapter h2{font-size:23px; margin:36px 0 12px; color:var(--ink); border-left:5px solid var(--accent); padding-left:12px}
.chapter h3{font-size:18px; margin:26px 0 10px; color:var(--warm)}
.chapter p{margin:12px 0}
.chapter img{max-width:100%; height:auto; display:block; margin:18px auto; border-radius:10px; box-shadow:0 4px 16px rgba(0,0,0,.08); background:#fff}

.chapter blockquote{
  margin:16px 0; padding:12px 18px; background:var(--card);
  border-left:4px solid var(--warm); border-radius:0 8px 8px 0; color:var(--muted);
}
.chapter blockquote p{margin:6px 0}

.chapter code{background:#ece4d4; padding:2px 6px; border-radius:5px; font-size:.9em; font-family:"Cascadia Code",Consolas,monospace}
.chapter pre{background:var(--code-bg); color:var(--code-ink); padding:16px 18px; border-radius:10px; overflow-x:auto; line-height:1.6}
.chapter pre code{background:transparent; color:inherit; padding:0}

.chapter table{border-collapse:collapse; width:100%; margin:18px 0; font-size:14.5px; background:var(--card); border-radius:10px; overflow:hidden; box-shadow:0 2px 10px rgba(0,0,0,.05)}
.chapter th,.chapter td{border:1px solid var(--line); padding:9px 12px; text-align:left; vertical-align:top}
.chapter th{background:var(--brown); color:#fff; font-weight:600}
.chapter tr:nth-child(even) td{background:#faf6ee}

.chapter hr{border:none; border-top:1px dashed var(--line); margin:30px 0}
.chapter ul,.chapter ol{padding-left:26px}
.chapter li{margin:5px 0}

.pager{display:flex; justify-content:space-between; margin-top:60px; gap:12px}
.pager a{
  flex:1; padding:14px 18px; background:var(--card); border:1px solid var(--line);
  border-radius:10px; color:var(--ink); font-size:14px;
}
.pager a:hover{border-color:var(--brown); text-decoration:none}
.pager a.next{text-align:right}
.pager .lbl{display:block; font-size:12px; color:var(--muted)}
.pager a.disabled{visibility:hidden}

.scrolltop{
  position:fixed; right:26px; bottom:26px; width:46px; height:46px; border-radius:50%;
  background:var(--brown); color:#fff; border:none; font-size:20px; cursor:pointer;
  box-shadow:0 4px 14px rgba(0,0,0,.2); display:none;
}

@media (max-width:900px){
  .sidebar{position:fixed; z-index:30; transform:translateX(-100%); transition:transform .25s; box-shadow:4px 0 20px rgba(0,0,0,.15)}
  .sidebar.open{transform:none}
  .topbar{display:flex}
  .reader{padding:24px 18px 100px}
  .chapter h1{font-size:24px}
}
</style>
</head>
<body>
<div class="app">
  <aside class="sidebar" id="sidebar">
    <div class="brand">Olympus PEN E-P7<small>从零开始 · 新手实用教程（网页版）</small></div>
    <nav id="nav">{{NAV}}</nav>
  </aside>
  <div class="main">
    <div style="width:100%">
      <div class="topbar">
        <button class="menu-btn" id="menuBtn">☰ 目录</button>
        <span class="t">EP7 新手教程</span>
      </div>
      <div class="reader" id="reader">
        {{SECTIONS}}
        <div class="pager" id="pager">
          <a class="prev" href="#" id="prevLink"><span class="lbl">上一章</span><span id="prevTitle"></span></a>
          <a class="next" href="#" id="nextLink"><span class="lbl">下一章</span><span id="nextTitle"></span></a>
        </div>
      </div>
    </div>
  </div>
</div>
<button class="scrolltop" id="scrollTop">↑</button>
<script>
(function(){
  var links = Array.prototype.slice.call(document.querySelectorAll('.nav-link'));
  var chapters = Array.prototype.slice.call(document.querySelectorAll('.chapter'));
  var order = links.map(function(l){return l.getAttribute('data-target');});
  var sidebar = document.getElementById('sidebar');
  var reader = document.getElementById('reader');
  var prevLink = document.getElementById('prevLink');
  var nextLink = document.getElementById('nextLink');
  var prevTitle = document.getElementById('prevTitle');
  var nextTitle = document.getElementById('nextTitle');

  function titleOf(id){
    var l = links.filter(function(x){return x.getAttribute('data-target')===id;})[0];
    return l ? l.textContent : '';
  }

  function show(id, push){
    if(order.indexOf(id) === -1){ id = order[0]; }
    chapters.forEach(function(c){ c.classList.toggle('active', c.id===id); });
    links.forEach(function(l){ l.classList.toggle('active', l.getAttribute('data-target')===id); });
    var idx = order.indexOf(id);
    setPager(prevLink, prevTitle, order[idx-1]);
    setPager(nextLink, nextTitle, order[idx+1]);
    if(push){ history.replaceState(null,'', '#'+id); }
    reader.scrollIntoView({block:'start'});
    window.scrollTo(0,0);
    sidebar.classList.remove('open');
  }

  function setPager(link, label, id){
    if(id){ link.classList.remove('disabled'); link.setAttribute('data-target', id); label.textContent = titleOf(id); }
    else { link.classList.add('disabled'); label.textContent=''; }
  }

  document.getElementById('nav').addEventListener('click', function(e){
    var a = e.target.closest('.nav-link'); if(!a) return;
    e.preventDefault(); show(a.getAttribute('data-target'), true);
  });
  document.getElementById('pager').addEventListener('click', function(e){
    var a = e.target.closest('a'); if(!a || a.classList.contains('disabled')) return;
    e.preventDefault(); show(a.getAttribute('data-target'), true);
  });
  reader.addEventListener('click', function(e){
    var a = e.target.closest('a[href^="#sec-"]'); if(!a) return;
    e.preventDefault(); show(a.getAttribute('href').slice(1), true);
  });

  var menuBtn = document.getElementById('menuBtn');
  if(menuBtn){ menuBtn.addEventListener('click', function(){ sidebar.classList.toggle('open'); }); }

  var st = document.getElementById('scrollTop');
  window.addEventListener('scroll', function(){ st.style.display = window.scrollY>400 ? 'block':'none'; });
  st.addEventListener('click', function(){ window.scrollTo({top:0,behavior:'smooth'}); });

  var initial = location.hash ? location.hash.slice(1) : order[0];
  show(initial, false);
})();
</script>
</body>
</html>
"""


if __name__ == "__main__":
    build()
