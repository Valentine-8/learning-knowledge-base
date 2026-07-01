#!/usr/bin/env python3
"""Refined EP7 Guide illustrations. Regenerates all SVGs at higher fidelity.

Run via generate_images.py, or directly:
    python EP7-Guide/scripts/art.py
"""
from svgkit import wrap, write, label, camera_front, camera_back, lens


# ---------------------------------------------------------------- body -------

def front_hero():
    inner = (
        camera_front(105, 70, 1.0, dial="A")
        + '<text x="240" y="300" text-anchor="middle" font-size="14" fill="#6b6355">'
        '2030 万像素 · M4/3 · 复古 PEN 造型</text>'
    )
    wrap("body/front-hero.svg", 480, 330, inner, "Olympus PEN E-P7")


def front_back():
    inner = (
        camera_front(30, 80, 0.92)
        + camera_back(390, 80, 0.92)
        + '<text x="170" y="290" text-anchor="middle" font-size="14" fill="#6b6355">正面 · 镜头 · 拨盘</text>'
        + '<text x="540" y="290" text-anchor="middle" font-size="14" fill="#6b6355">背面 · 触摸屏 · 十字键</text>'
    )
    wrap("body/front-back.svg", 720, 320, inner, "PEN E-P7 正面与背面")


def mode_dial():
    import math
    cx, cy, r = 260, 280, 168
    labels = [
        ("iAUTO", 270), ("SCN", 306), ("AP", 342), ("ART", 18),
        ("P", 54), ("A", 90), ("S", 126), ("M", 162), ("B", 198), ("视频", 234),
    ]
    parts = [
        '<g filter="url(#soft)">',
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#gDial)" stroke="#7d7768" stroke-width="4"/>',
        f'<circle cx="{cx}" cy="{cy}" r="{r-16}" fill="none" stroke="#c8c2b4" stroke-width="2"/>',
        f'<circle cx="{cx}" cy="{cy}" r="30" fill="#cfc9bb" stroke="#8a7f6e" stroke-width="2"/>',
        '</g>',
        # pointer mark at top
        f'<path d="M{cx-8} {cy-r-6} L{cx+8} {cy-r-6} L{cx} {cy-r+8} Z" fill="#c0392b"/>',
    ]
    for text, deg in labels:
        rad = math.radians(deg)
        x = cx + (r - 34) * math.cos(rad)
        y = cy + (r - 34) * math.sin(rad)
        tick_x1 = cx + (r - 8) * math.cos(rad)
        tick_y1 = cy + (r - 8) * math.sin(rad)
        tick_x2 = cx + (r - 18) * math.cos(rad)
        tick_y2 = cy + (r - 18) * math.sin(rad)
        hot = text == "A"
        parts.append(
            f'<line x1="{tick_x1:.1f}" y1="{tick_y1:.1f}" x2="{tick_x2:.1f}" y2="{tick_y2:.1f}" stroke="#8a7f6e" stroke-width="2"/>'
        )
        if hot:
            parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="17" fill="#5c7a4a"/>')
        parts.append(
            f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="middle" dominant-baseline="middle" '
            f'font-size="16" font-weight="{"700" if hot else "500"}" '
            f'fill="{"#fff" if hot else "#2c2a24"}">{text}</text>'
        )
    parts.append('<text x="260" y="482" text-anchor="middle" font-size="14" fill="#5c7a4a">新手建议：日常用 A 模式（光圈优先）</text>')
    wrap("body/mode-dial.svg", 520, 510, "\n".join(parts), "EP7 模式转盘")


def profile_dial():
    inner = (
        camera_front(40, 74, 0.8)
        + label(75, 190, 200, 150, "Profile 拨盘")
        + '<g transform="translate(300,120)" filter="url(#soft)">'
        '<circle cx="70" cy="70" r="66" fill="url(#gDial)" stroke="#7d7768" stroke-width="3"/>'
        '<circle cx="70" cy="70" r="10" fill="#8a7f6e"/>'
        '<path d="M62 12 L78 12 L70 26 Z" fill="#c0392b"/>'
        '<text x="70" y="34" text-anchor="middle" font-size="13" fill="#2c2a24">标准</text>'
        '<text x="122" y="74" text-anchor="middle" font-size="13" fill="#b5651d">色彩</text>'
        '<text x="70" y="120" text-anchor="middle" font-size="13" fill="#2c2a24">单色</text>'
        '<text x="20" y="74" text-anchor="middle" font-size="12" fill="#666">ART</text>'
        '</g>'
        + '<text x="260" y="352" text-anchor="middle" font-size="13" fill="#6b6355">拨到「色彩」试 Profile 2，直出肤色更柔</text>'
    )
    wrap("body/profile-dial.svg", 520, 380, inner, "正面 Profile 控制拨盘")


def size_compare():
    inner = (
        camera_front(40, 90, 0.7)
        + lens(250, 250, 0.0, kind="pancake")  # not used
        # phone
        + '<g transform="translate(360,90)" filter="url(#soft)">'
        '<rect x="0" y="0" width="86" height="170" rx="16" fill="#2b2a28" stroke="#111"/>'
        '<rect x="6" y="8" width="74" height="150" rx="8" fill="#1a2a3a"/>'
        '<circle cx="16" cy="20" r="5" fill="#333"/>'
        '</g>'
        + '<text x="160" y="290" text-anchor="middle" font-size="14" fill="#6b6355">EP7 + 14-42 ≈ 430g</text>'
        + '<text x="403" y="290" text-anchor="middle" font-size="14" fill="#6b6355">手机</text>'
        + '<text x="260" y="320" text-anchor="middle" font-size="13" fill="#5c7a4a">相机稍大，但远比单反轻</text>'
    )
    wrap("body/size-compare.svg", 520, 340, inner, "EP7 与手机大小对比")


def unboxing():
    items = [
        "EP7 机身（银 / 白）",
        "14-42mm EZ 电动饼干头",
        "40-150mm R 长焦",
        "BLS-50 电池 + F-5AC 充电器",
        "肩带 + Micro USB 线",
        "说明书 / 保修卡",
    ]
    parts = ['<g filter="url(#soft)">']
    parts.append(camera_front(360, 90, 0.62))
    parts.append(lens(360, 250, 0.7, kind="pancake"))
    parts.append(lens(520, 250, 0.7, kind="tele"))
    parts.append('</g>')
    for i, it in enumerate(items):
        y = 96 + i * 34
        parts.append(f'<circle cx="46" cy="{y-4}" r="5" fill="#5c7a4a"/>')
        parts.append(f'<text x="62" y="{y}" font-size="15" fill="#2c2a24">{it}</text>')
    wrap("body/unboxing.svg", 700, 340, "\n".join(parts), "EP7 双镜头套装开箱清单")


def battery_insert():
    inner = (
        '<g filter="url(#soft)">'
        '<rect x="150" y="80" width="220" height="150" rx="14" fill="url(#gSilver)" stroke="#9a927f" stroke-width="2"/>'
        '<rect x="176" y="104" width="150" height="104" rx="6" fill="#2a2723"/>'
        # battery
        '<rect x="196" y="118" width="118" height="78" rx="6" fill="#3c6fb0" stroke="#274b7a" stroke-width="2"/>'
        '<rect x="196" y="118" width="20" height="78" rx="6" fill="#274b7a"/>'
        '<polygon points="196,118 216,118 196,138" fill="#f5c542"/>'
        '<text x="255" y="163" text-anchor="middle" font-size="14" fill="#fff">BLS-50</text>'
        '</g>'
        + '<path d="M255 250 L255 210" stroke="#5c7a4a" stroke-width="3" marker-end="url(#arrow)"/>'
        + '<text x="260" y="285" text-anchor="middle" font-size="14" fill="#6b6355">缺角朝内对准，推到底再关仓盖</text>'
    )
    wrap("body/battery-insert.svg", 520, 310, inner, "BLS-50 电池插入方向")


def strap():
    inner = (
        camera_front(150, 90, 0.72)
        + '<path d="M150 130 Q260 40 372 130" fill="none" stroke="#5c7a4a" stroke-width="8" stroke-linecap="round"/>'
        + '<rect x="140" y="120" width="16" height="16" rx="4" fill="#8a7f6e"/>'
        + '<rect x="366" y="120" width="16" height="16" rx="4" fill="#8a7f6e"/>'
        + '<text x="260" y="290" text-anchor="middle" font-size="14" fill="#6b6355">从外向内穿入挂耳，防止滑脱</text>'
    )
    wrap("body/strap.svg", 520, 320, inner, "肩带穿法")


def build_body():
    front_hero()
    front_back()
    mode_dial()
    profile_dial()
    size_compare()
    unboxing()
    battery_insert()
    strap()


# --------------------------------------------------------------- lenses ------

def lens_14_42():
    inner = (
        lens(150, 40, 1.0, kind="pancake")
        + label(318, 115, 400, 90, "37mm 口径")
        + label(200, 100, 130, 70, "电子变焦环", anchor="end")
        + '<text x="240" y="250" text-anchor="middle" font-size="14" fill="#6b6355">'
        '等效 28-84mm · 93g · 开机伸出 / 关机缩回</text>'
    )
    wrap("lenses/14-42-ez.svg", 480, 280, inner, "14-42mm EZ 电动饼干头")


def lens_40_150():
    inner = (
        lens(150, 40, 1.0, kind="tele")
        + label(322, 115, 400, 90, "58mm 口径")
        + '<text x="240" y="250" text-anchor="middle" font-size="14" fill="#6b6355">'
        '等效 80-300mm · 190g · 机械变焦（手动拧）</text>'
    )
    wrap("lenses/40-150-r.svg", 480, 280, inner, "40-150mm R 长焦")


def mount_align():
    inner = (
        # body with mount
        '<g filter="url(#soft)">'
        '<rect x="40" y="80" width="230" height="200" rx="16" fill="url(#gSilver)" stroke="#9a927f" stroke-width="2"/>'
        '<circle cx="155" cy="180" r="78" fill="#2a2723"/>'
        '<circle cx="155" cy="180" r="70" fill="#3a3630"/>'
        '<circle cx="155" cy="102" r="7" fill="#fff" stroke="#c0392b" stroke-width="3"/>'
        '</g>'
        + '<text x="155" y="300" text-anchor="middle" font-size="12" fill="#c0392b">机身白点</text>'
        # lens with dot
        + '<g filter="url(#soft)">'
        '<rect x="470" y="120" width="150" height="120" rx="14" fill="url(#gLeather)"/>'
        '<circle cx="545" cy="180" r="46" fill="url(#gGlass)"/>'
        '<rect x="536" y="120" width="18" height="18" rx="3" fill="#fff" stroke="#c0392b" stroke-width="3"/>'
        '</g>'
        + '<text x="545" y="300" text-anchor="middle" font-size="12" fill="#c0392b">镜头白点</text>'
        + '<path d="M285 180 H395" stroke="#5c7a4a" stroke-width="5" marker-end="url(#arrow)"/>'
        + '<text x="340" y="168" text-anchor="middle" font-size="14" fill="#5c7a4a">对齐</text>'
        + '<text x="330" y="352" text-anchor="middle" font-size="14" fill="#6b6355">关机 → 白点对齐 → 顺时针锁紧 → 听到「咔」</text>'
    )
    wrap("lenses/mount-align.svg", 660, 380, inner, "装镜头：白点对白点")


def lens_change():
    steps = ["1. 关机", "2. 卸镜头", "3. 盖后盖", "4. 装新镜头", "5. 锁紧", "6. 开机试拍"]
    parts = []
    for i, s in enumerate(steps):
        x = 30 + i * 118
        parts.append(f'<g filter="url(#soft)"><rect x="{x}" y="70" width="104" height="86" rx="10" '
                     f'fill="#fffdf8" stroke="#d8cfbf"/></g>')
        parts.append(f'<circle cx="{x+52}" cy="100" r="15" fill="#5c7a4a"/>')
        parts.append(f'<text x="{x+52}" y="105" text-anchor="middle" font-size="14" font-weight="700" fill="#fff">{i+1}</text>')
        parts.append(f'<text x="{x+52}" y="140" text-anchor="middle" font-size="12" fill="#2c2a24">{s[3:]}</text>')
        if i < len(steps) - 1:
            parts.append(f'<text x="{x+112}" y="118" font-size="20" fill="#8a7f6e">›</text>')
    parts.append('<text x="380" y="185" text-anchor="middle" font-size="13" fill="#c0392b">户外换镜头：背风、机身朝下、快速完成</text>')
    wrap("lenses/lens-change.svg", 760, 210, "\n".join(parts), "换镜头标准流程")


def build_lenses():
    lens_14_42()
    lens_40_150()
    mount_align()
    lens_change()


# ------------------------------------------------------------- diagrams ------

def _scene(x, y, w, h, subj_w, subj_h, blur_bg, caption):
    """A framed photo scene: sky gradient, ground, tree + a person subject."""
    sx = x + w / 2
    parts = [
        f'<g filter="url(#soft)"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="url(#gSky)"/></g>',
        f'<clipPath id="clip{x}{y}"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8"/></clipPath>',
        f'<g clip-path="url(#clip{x}{y})">',
        # ground
        f'<rect x="{x}" y="{y+h-h*0.32:.0f}" width="{w}" height="{h*0.32:.0f}" fill="#7cae4e"/>',
    ]
    bg = f' filter="url(#blur)"' if blur_bg else ""
    # background trees
    parts.append(f'<g{bg}>')
    for bx in (x + 24, x + w - 40):
        parts.append(f'<rect x="{bx}" y="{y+h*0.45:.0f}" width="10" height="{h*0.3:.0f}" fill="#6b4f2a"/>')
        parts.append(f'<circle cx="{bx+5}" cy="{y+h*0.45:.0f}" r="22" fill="#5c8a3a"/>')
    parts.append('</g>')
    # subject person (sharp)
    cy = y + h - h * 0.32
    parts.append(f'<circle cx="{sx:.0f}" cy="{cy-subj_h:.0f}" r="{subj_w*0.5:.0f}" fill="#e6b98f"/>')
    parts.append(f'<rect x="{sx-subj_w*0.5:.0f}" y="{cy-subj_h+subj_w*0.5:.0f}" width="{subj_w:.0f}" height="{subj_h-subj_w*0.5:.0f}" rx="{subj_w*0.3:.0f}" fill="#c0392b"/>')
    parts.append('</g>')
    parts.append(f'<text x="{sx:.0f}" y="{y+h+24}" text-anchor="middle" font-size="14" fill="#2c2a24">{caption}</text>')
    return "".join(parts)


def focal_14_42():
    inner = (
        _scene(40, 70, 250, 160, 26, 60, False, "14mm 广角 · 容纳环境")
        + _scene(350, 70, 250, 160, 70, 130, False, "42mm · 更聚焦主体")
    )
    wrap("diagrams/focal-length-14-42.svg", 640, 270, inner, "14-42mm 视角对比（等效 28-84mm）")


def focal_40_150():
    inner = (
        _scene(40, 70, 250, 160, 34, 70, False, "40mm · 主体较小")
        + _scene(350, 70, 250, 160, 96, 140, False, "150mm · 拉近放大")
    )
    wrap("diagrams/focal-length-40-150.svg", 640, 270, inner, "40-150mm 视角对比（等效 80-300mm）")


def aperture_blur():
    def frame(x, caption, fval, blur):
        bg = ' filter="url(#blur)"' if blur else ""
        return (
            f'<g filter="url(#soft)"><rect x="{x}" y="70" width="250" height="170" rx="8" fill="url(#gSky)"/></g>'
            f'<clipPath id="ap{x}"><rect x="{x}" y="70" width="250" height="170" rx="8"/></clipPath>'
            f'<g clip-path="url(#ap{x})"><rect x="{x}" y="190" width="250" height="50" fill="#7cae4e"/>'
            f'<g{bg}><circle cx="{x+60}" cy="150" r="26" fill="#5c8a3a"/>'
            f'<circle cx="{x+200}" cy="140" r="30" fill="#4f7d2f"/></g>'
            f'<circle cx="{x+125}" cy="160" r="30" fill="#e6b98f"/>'
            f'<rect x="{x+105}" y="185" width="40" height="45" rx="10" fill="#c0392b"/></g>'
            f'<text x="{x+125}" y="262" text-anchor="middle" font-size="15" fill="#2c2a24">{caption}</text>'
            f'<text x="{x+125}" y="96" text-anchor="middle" font-size="16" font-weight="700" fill="#fff">{fval}</text>'
        )
    inner = frame(40, "背景虚化", "F3.5", True) + frame(350, "背景清晰", "F8", False)
    wrap("diagrams/aperture-blur.svg", 640, 285, inner, "光圈与背景虚化")


def iso_compare():
    import random
    random.seed(7)
    def frame(x, iso, n, note):
        parts = [f'<g filter="url(#soft)"><rect x="{x}" y="70" width="180" height="140" rx="8" fill="#4a5a68"/></g>',
                 f'<clipPath id="iso{x}"><rect x="{x}" y="70" width="180" height="140" rx="8"/></clipPath>',
                 f'<g clip-path="url(#iso{x})"><rect x="{x}" y="70" width="180" height="140" fill="#586a78"/>']
        for _ in range(n):
            gx = x + random.randint(4, 176)
            gy = 70 + random.randint(4, 136)
            parts.append(f'<circle cx="{gx}" cy="{gy}" r="{random.choice([1,1,1,2])}" fill="#{random.choice(["fff","000","c9a"])}" fill-opacity="0.5"/>')
        parts.append('</g>')
        parts.append(f'<text x="{x+90}" y="{234}" text-anchor="middle" font-size="14" font-weight="700" fill="#2c2a24">{iso}</text>')
        parts.append(f'<text x="{x+90}" y="{254}" text-anchor="middle" font-size="12" fill="#6b6355">{note}</text>')
        return "".join(parts)
    inner = frame(30, "ISO 200", 0, "干净") + frame(230, "ISO 1600", 60, "轻微颗粒") + frame(430, "ISO 6400", 260, "明显噪点")
    inner += '<text x="320" y="284" text-anchor="middle" font-size="14" fill="#5c7a4a">新手建议：AUTO 上限 3200</text>'
    wrap("diagrams/iso-compare.svg", 640, 300, inner, "ISO 噪点对比（示意）")


def six_steps():
    steps = ["举起相机", "选好焦段", "触摸对焦", "半按合焦", "完全按下", "回放检查"]
    parts = []
    for i, s in enumerate(steps):
        x = 30 + i * 112
        parts.append(f'<g filter="url(#soft)"><rect x="{x}" y="66" width="98" height="92" rx="10" fill="#fffdf8" stroke="#d8cfbf"/></g>')
        parts.append(f'<circle cx="{x+49}" cy="96" r="16" fill="#5c7a4a"/>')
        parts.append(f'<text x="{x+49}" y="101" text-anchor="middle" font-size="15" font-weight="700" fill="#fff">{i+1}</text>')
        parts.append(f'<text x="{x+49}" y="138" text-anchor="middle" font-size="12" fill="#2c2a24">{s}</text>')
        if i < 5:
            parts.append(f'<text x="{x+106}" y="116" font-size="20" fill="#8a7f6e">›</text>')
    wrap("diagrams/six-steps.svg", 720, 185, "\n".join(parts), "第一次按快门：六步法")


def af_single_point():
    inner = (
        '<g filter="url(#soft)"><rect x="60" y="70" width="360" height="220" rx="10" fill="#12161c"/></g>'
        '<rect x="70" y="80" width="340" height="200" rx="6" fill="#28323c"/>'
        # face
        '<circle cx="240" cy="180" r="70" fill="#e6b98f"/>'
        '<circle cx="215" cy="165" r="8" fill="#33291f"/>'
        '<circle cx="265" cy="165" r="8" fill="#33291f"/>'
        '<path d="M222 205 Q240 218 258 205" fill="none" stroke="#a9714a" stroke-width="3"/>'
        # green focus box on eye
        '<rect x="200" y="150" width="30" height="30" fill="none" stroke="#39d353" stroke-width="3"/>'
        '<text x="240" y="315" text-anchor="middle" font-size="14" fill="#6b6355">单点对焦：绿框对准眼睛</text>'
    )
    wrap("diagrams/af-single-point.svg", 480, 340, inner, "单点对焦示意")


def building_lines():
    inner = (
        '<g filter="url(#soft)"><rect x="60" y="70" width="220" height="180" rx="6" fill="url(#gSky)"/></g>'
        '<polygon points="120,240 120,95 210,95 210,240" fill="#cbb79a" stroke="#8a7f6e"/>'
        '<line x1="120" y1="95" x2="120" y2="240" stroke="#5c7a4a" stroke-width="2" stroke-dasharray="5 4"/>'
        '<text x="170" y="272" text-anchor="middle" font-size="13" fill="#5c7a4a">✓ 相机水平，垂直线直</text>'
        '<g filter="url(#soft)"><rect x="360" y="70" width="220" height="180" rx="6" fill="url(#gSky)"/></g>'
        '<polygon points="430,240 405,100 535,100 510,240" fill="#cbb79a" stroke="#8a7f6e"/>'
        '<text x="470" y="272" text-anchor="middle" font-size="13" fill="#c0392b">✗ 仰拍 → 向上汇聚变形</text>'
    )
    wrap("diagrams/building-lines.svg", 640, 295, inner, "建筑拍摄：保持水平")


def blur_exif():
    inner = (
        '<g filter="url(#soft)"><rect x="70" y="70" width="340" height="230" rx="10" fill="#12161c"/></g>'
        # blurred photo thumbnail
        '<g filter="url(#blur)"><circle cx="180" cy="150" r="45" fill="#8a7f6e"/><rect x="150" y="150" width="60" height="50" fill="#5c6b74"/></g>'
        '<rect x="250" y="110" width="140" height="110" rx="6" fill="#20262e"/>'
        '<text x="262" y="140" font-size="14" fill="#ff6b6b">快门 1/8 秒</text>'
        '<text x="262" y="166" font-size="13" fill="#cdd3da">光圈 F8</text>'
        '<text x="262" y="190" font-size="13" fill="#cdd3da">ISO 800</text>'
        '<text x="262" y="214" font-size="12" fill="#ffb74d">← 太慢，易糊</text>'
        '<text x="240" y="325" text-anchor="middle" font-size="14" fill="#6b6355">手持建议 ≥ 1/60（42mm）</text>'
    )
    wrap("diagrams/blur-exif.svg", 480, 350, inner, "回放检查快门速度")


def wb_compare():
    inner = (
        '<g filter="url(#soft)"><rect x="40" y="70" width="250" height="150" rx="8" fill="#f2c98a"/></g>'
        '<rect x="40" y="70" width="250" height="150" rx="8" fill="#c8801f" fill-opacity="0.28"/>'
        '<circle cx="165" cy="140" r="40" fill="#e8d3b0"/>'
        '<text x="165" y="242" text-anchor="middle" font-size="14" fill="#2c2a24">偏黄（钨丝灯）</text>'
        '<g filter="url(#soft)"><rect x="350" y="70" width="250" height="150" rx="8" fill="#fbf6ee"/></g>'
        '<circle cx="475" cy="140" r="40" fill="#f0e6d6"/>'
        '<text x="475" y="242" text-anchor="middle" font-size="14" fill="#2c2a24">校正后（白炽灯 WB）</text>'
    )
    wrap("diagrams/wb-compare.svg", 640, 265, inner, "白平衡对比（示意）")


def checklist_card():
    items = ["电池满电", "SD 卡已插", "模式 → A", "ISO AUTO 上限3200", "默认镜头 14-42", "镜头盖已摘"]
    parts = ['<g filter="url(#soft)"><rect x="30" y="60" width="360" height="270" rx="14" fill="#fffdf8" stroke="#d8cfbf" stroke-width="2"/></g>',
             '<rect x="30" y="60" width="360" height="8" rx="4" fill="#5c7a4a"/>']
    for i, it in enumerate(items):
        y = 108 + i * 36
        parts.append(f'<rect x="56" y="{y-14}" width="18" height="18" rx="4" fill="none" stroke="#5c7a4a" stroke-width="2"/>')
        parts.append(f'<path d="M59 {y-5} l4 5 l7 -10" fill="none" stroke="#5c7a4a" stroke-width="2.5"/>')
        parts.append(f'<text x="86" y="{y}" font-size="15" fill="#2c2a24">{it}</text>')
    wrap("diagrams/checklist-card.svg", 420, 350, "\n".join(parts), "出门前三分钟清单")


def build_diagrams():
    focal_14_42()
    focal_40_150()
    aperture_blur()
    iso_compare()
    six_steps()
    af_single_point()
    building_lines()
    blur_exif()
    wb_compare()
    checklist_card()


# ---------------------------------------------------------------- menu -------

def menu_mock(rel, title, items, highlight=0):
    w = 480
    h = 96 + len(items) * 40
    parts = [
        f'<g filter="url(#soft)"><rect x="20" y="70" width="440" height="{h-90}" rx="12" fill="#161b22" stroke="#2b3138" stroke-width="2"/></g>',
        f'<rect x="20" y="70" width="440" height="44" rx="12" fill="#222a33"/>',
        f'<rect x="20" y="98" width="440" height="16" fill="#222a33"/>',
        f'<text x="240" y="98" text-anchor="middle" fill="#fff" font-size="16" font-weight="600">{title}</text>',
        f'<text x="240" y="{h-20}" text-anchor="middle" fill="#5c6670" font-size="11">界面示意图（非官方截图）</text>',
    ]
    for i, it in enumerate(items):
        y = 126 + i * 40
        sel = i == highlight
        parts.append(f'<rect x="34" y="{y}" width="412" height="32" rx="6" fill="{"#2f6f4f" if sel else "#1d232b"}" stroke="{"#39d353" if sel else "#2b3138"}"/>')
        parts.append(f'<circle cx="52" cy="{y+16}" r="5" fill="{"#39d353" if sel else "#586670"}"/>')
        parts.append(f'<text x="70" y="{y+21}" fill="{"#eafbe9" if sel else "#c7cdd4"}" font-size="14">{it}</text>')
    wrap(rel, w, h, "\n".join(parts))


def build_menu():
    menu_mock("menu/super-control-panel.svg", "超级控制面板 SCP（按 OK）",
              ["ISO — AUTO 上限 3200", "WB 白平衡 — AUTO", "AF 模式 — S-AF", "AF 区域 — 单点",
               "驱动 — 单张 / 连拍", "防抖 — S-IS AUTO"], highlight=0)
    menu_mock("menu/scn-modes.svg", "SCN 场景模式",
              ["人物 → 人像 / 儿童", "夜景 → 手持星空 / 烟花", "运动 → 平移",
               "风景 → 日落 / 海滩", "室内 → 静音", "特写 → 微距"], highlight=3)
    menu_mock("menu/ap-modes.svg", "AP 高级拍摄模式",
              ["Live Composite（光轨/烟花）", "Live Time（实时长曝）", "多重曝光",
               "HDR", "静音", "全景 / 梯形校正"], highlight=0)
    menu_mock("menu/first-setup.svg", "新手第一天必改",
              ["图片质量 → LF", "ISO → AUTO 上限 3200", "对焦 → S-AF 单点",
               "防抖 → S-IS AUTO", "网格线 → 3×3", "格式化 SD 卡"], highlight=1)
    menu_mock("menu/live-composite.svg", "Live Composite 流程",
              ["① 三脚架固定", "② 光圈 F8 / ISO 200", "③ MF 对无穷远",
               "④ 按快门开始累积", "⑤ 观看屏幕光轨", "⑥ 结束再按停止"], highlight=3)
    menu_mock("menu/menu-overview.svg", "MENU 五大类",
              ["相机 — 拍摄设置", "视频 — 录像", "播放 — 回放",
               "自定义 — 按钮 / 显示", "扳手 — 设置 / 格式化"], highlight=0)


# ------------------------------------------------------------- samples -------

def sample_wide():
    inner = (
        '<clipPath id="cw"><rect x="30" y="60" width="580" height="260" rx="10"/></clipPath>'
        '<g clip-path="url(#cw)">'
        '<rect x="30" y="60" width="580" height="260" fill="url(#gSky)"/>'
        '<circle cx="510" cy="120" r="34" fill="#fff7c2"/>'
        '<path d="M30 250 Q180 190 340 235 T610 220 L610 320 L30 320 Z" fill="#8bbf5a"/>'
        '<path d="M30 285 Q220 255 420 275 T610 262 L610 320 L30 320 Z" fill="#5f9138"/>'
        '<polygon points="120,235 175,150 230,235" fill="#6b7f8a"/>'
        '<polygon points="360,235 430,135 500,235" fill="#5c6b74"/>'
        '</g>'
        '<g filter="url(#soft)"><rect x="30" y="60" width="580" height="260" rx="10" fill="none" stroke="#fff" stroke-width="4"/></g>'
        '<text x="320" y="348" text-anchor="middle" font-size="14" fill="#6b6355">14mm 广角 · F8 · ISO 200 · 前中后景层次</text>'
    )
    wrap("samples/landscape/wide.svg", 640, 372, inner, "风景广角样张（示意）")


def sample_sunset():
    inner = (
        '<clipPath id="cs"><rect x="30" y="60" width="580" height="240" rx="10"/></clipPath>'
        '<g clip-path="url(#cs)">'
        '<rect x="30" y="60" width="580" height="240" fill="url(#gSunset)"/>'
        '<circle cx="320" cy="210" r="56" fill="#fff2b0" fill-opacity="0.95"/>'
        '<rect x="30" y="250" width="580" height="50" fill="#2a2333"/>'
        '<path d="M30 250 Q320 236 610 250 L610 260 L30 260 Z" fill="#ffd27f" fill-opacity="0.5"/>'
        '</g>'
        '<g filter="url(#soft)"><rect x="30" y="60" width="580" height="240" rx="10" fill="none" stroke="#fff" stroke-width="4"/></g>'
        '<text x="320" y="330" text-anchor="middle" font-size="14" fill="#6b6355">SCN 日落 或 A · F8 · -0.3EV 保留太阳层次</text>'
    )
    wrap("samples/landscape/sunset.svg", 640, 354, inner, "日落样张（示意）")


def sample_handheld_tripod():
    def blurred_scene(x, blur, badge, note, ncolor):
        f = ' filter="url(#blur)"' if blur else ""
        parts = [
            f'<g filter="url(#soft)"><rect x="{x}" y="70" width="250" height="170" rx="10" fill="url(#gNight)"/></g>',
            f'<clipPath id="ht{x}"><rect x="{x}" y="70" width="250" height="170" rx="10"/></clipPath>',
            f'<g clip-path="url(#ht{x})"><g{f}>',
        ]
        for dx, dy, w in [(40, 90, 18), (90, 70, 14), (150, 110, 20), (200, 85, 16)]:
            parts.append(f'<rect x="{x+dx}" y="{dy+70}" width="{w}" height="70" fill="#2a3a5a"/>')
            parts.append(f'<circle cx="{x+dx+w/2}" cy="{dy+80}" r="6" fill="#ffd36b"/>')
        parts.append('</g></g>')
        parts.append(f'<text x="{x+125}" y="{262}" text-anchor="middle" font-size="14" font-weight="700" fill="#2c2a24">{badge}</text>')
        parts.append(f'<text x="{x+125}" y="{282}" text-anchor="middle" font-size="12" fill="{ncolor}">{note}</text>')
        return "".join(parts)
    inner = blurred_scene(40, True, "手持 1/15", "易糊 · 噪点多", "#c0392b") + \
        blurred_scene(350, False, "三脚架 2 秒", "清晰 · 低噪", "#5c7a4a")
    wrap("samples/night/handheld-vs-tripod.svg", 640, 300, inner, "夜景：手持 vs 三脚架")


def sample_stars():
    import random
    random.seed(3)
    parts = [
        '<g filter="url(#soft)"><rect x="40" y="60" width="400" height="220" rx="10" fill="url(#gNight)"/></g>',
        '<clipPath id="st"><rect x="40" y="60" width="400" height="220" rx="10"/></clipPath>',
        '<g clip-path="url(#st)">',
    ]
    for _ in range(90):
        sx = 40 + random.randint(6, 394)
        sy = 60 + random.randint(6, 150)
        r = random.choice([0.6, 1, 1, 1.4, 2])
        parts.append(f'<circle cx="{sx}" cy="{sy}" r="{r}" fill="#fff" fill-opacity="{random.choice([0.5,0.7,1])}"/>')
    # milky way band
    parts.append('<ellipse cx="240" cy="150" rx="180" ry="34" fill="#9fb4e0" fill-opacity="0.12"/>')
    # horizon
    parts.append('<rect x="40" y="250" width="400" height="30" fill="#0a0f1c"/>')
    parts.append('<polygon points="90,250 150,215 210,250" fill="#060a14"/>')
    parts.append('</g>')
    parts.append('<text x="240" y="304" text-anchor="middle" font-size="14" fill="#6b6355">SCN 手持星空 · 14mm 广角 · 无光污染处</text>')
    wrap("samples/night/stars.svg", 480, 320, "\n".join(parts), "星空样张（示意）")


def sample_portrait_setup():
    inner = (
        '<g filter="url(#soft)"><rect x="40" y="70" width="230" height="180" rx="10" fill="#eef2e4"/></g>'
        # sun/light source
        '<circle cx="80" cy="110" r="18" fill="#ffcf5c"/>'
        '<line x1="96" y1="120" x2="150" y2="150" stroke="#ffcf5c" stroke-width="3" marker-end="url(#arrow)"/>'
        # subject
        '<circle cx="180" cy="150" r="34" fill="#e6b98f"/>'
        '<circle cx="171" cy="145" r="4" fill="#33291f"/><circle cx="189" cy="145" r="4" fill="#33291f"/>'
        '<rect x="152" y="182" width="56" height="60" rx="14" fill="#5c7a4a"/>'
        '<text x="180" y="268" text-anchor="middle" font-size="12" fill="#6b6355">窗边侧光 · 对焦眼睛</text>'
        # params card
        '<g filter="url(#soft)"><rect x="300" y="70" width="300" height="180" rx="10" fill="#fffdf8" stroke="#d8cfbf"/></g>'
        '<text x="322" y="106" font-size="14" fill="#2c2a24">模式：A / SCN 人像</text>'
        '<text x="322" y="140" font-size="14" fill="#2c2a24">光圈：F4 ～ F5.6</text>'
        '<text x="322" y="174" font-size="14" fill="#2c2a24">焦段：35 ～ 42mm</text>'
        '<text x="322" y="208" font-size="14" fill="#2c2a24">对焦：眼睛（单点）</text>'
        '<text x="322" y="238" font-size="13" fill="#b5651d">逆光 +0.7 ～ +1.0 EV</text>'
    )
    wrap("samples/portrait/setup.svg", 640, 280, inner, "人像拍摄要点")


def sample_light_compare():
    inner = (
        '<g filter="url(#soft)"><rect x="40" y="70" width="250" height="160" rx="10" fill="#fff6dc"/></g>'
        '<circle cx="165" cy="150" r="44" fill="#eab98c"/>'
        '<circle cx="152" cy="142" r="5" fill="#33291f"/><circle cx="178" cy="142" r="5" fill="#33291f"/>'
        '<text x="165" y="252" text-anchor="middle" font-size="14" fill="#2c2a24">顺光：脸亮、肤色好</text>'
        '<g filter="url(#soft)"><rect x="350" y="70" width="250" height="160" rx="10" fill="#8a94a0"/></g>'
        '<circle cx="475" cy="150" r="44" fill="#4a463f"/>'
        '<circle cx="475" cy="110" r="16" fill="#fff2b0"/>'
        '<text x="475" y="252" text-anchor="middle" font-size="14" fill="#2c2a24">逆光：脸黑（+EV 或 HDR 救）</text>'
    )
    wrap("samples/portrait/light-compare.svg", 640, 275, inner, "顺光 vs 逆光")


def build_samples():
    sample_wide()
    sample_sunset()
    sample_handheld_tripod()
    sample_stars()
    sample_portrait_setup()
    sample_light_compare()


def build_all():
    build_body()
    build_lenses()
    build_diagrams()
    build_menu()
    build_samples()


if __name__ == "__main__":
    build_all()
    print("all refined images done")
