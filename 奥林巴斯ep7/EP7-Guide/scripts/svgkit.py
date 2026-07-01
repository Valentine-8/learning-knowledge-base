#!/usr/bin/env python3
"""Shared SVG toolkit for the refined EP7 Guide illustrations."""
import os

BASE = os.path.join(os.path.dirname(__file__), "..", "images")

DEFS = """
<defs>
  <linearGradient id="gPaper" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#faf6ee"/><stop offset="1" stop-color="#ece3d2"/>
  </linearGradient>
  <linearGradient id="gSilver" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#fdfdfb"/><stop offset="0.5" stop-color="#e2ded5"/><stop offset="1" stop-color="#bfb9ab"/>
  </linearGradient>
  <linearGradient id="gTop" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#d6d1c6"/>
  </linearGradient>
  <linearGradient id="gLeather" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#403c37"/><stop offset="1" stop-color="#1f1d1a"/>
  </linearGradient>
  <linearGradient id="gDial" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#f0eee8"/><stop offset="1" stop-color="#b3ada0"/>
  </linearGradient>
  <radialGradient id="gGlass" cx="0.38" cy="0.32" r="0.8">
    <stop offset="0" stop-color="#9dc2de"/><stop offset="0.4" stop-color="#33566f"/><stop offset="1" stop-color="#0b1720"/>
  </radialGradient>
  <linearGradient id="gSky" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#6fb4ff"/><stop offset="1" stop-color="#d3edff"/>
  </linearGradient>
  <linearGradient id="gSunset" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#ff6f43"/><stop offset="0.5" stop-color="#ffb74d"/><stop offset="1" stop-color="#5c6bc0"/>
  </linearGradient>
  <linearGradient id="gNight" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#0a1230"/><stop offset="1" stop-color="#24386b"/>
  </linearGradient>
  <filter id="soft" x="-30%" y="-30%" width="160%" height="160%">
    <feDropShadow dx="0" dy="5" stdDeviation="7" flood-color="#000" flood-opacity="0.20"/>
  </filter>
  <filter id="blur"><feGaussianBlur stdDeviation="6"/></filter>
  <filter id="blurLite"><feGaussianBlur stdDeviation="2.4"/></filter>
  <marker id="arrow" markerWidth="12" markerHeight="12" refX="9" refY="4" orient="auto">
    <path d="M0,0 L9,4 L0,8 Z" fill="#5c7a4a"/>
  </marker>
</defs>
"""


def wrap(rel, w, h, inner, title="", subtitle=""):
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
        f'font-family="Microsoft YaHei, Segoe UI, sans-serif">',
        DEFS,
        f'<rect width="{w}" height="{h}" fill="url(#gPaper)"/>',
    ]
    if title:
        parts.append(
            f'<text x="{w/2:.0f}" y="34" text-anchor="middle" font-size="20" '
            f'font-weight="700" fill="#2c2a24">{title}</text>'
        )
    if subtitle:
        parts.append(
            f'<text x="{w/2:.0f}" y="56" text-anchor="middle" font-size="13" '
            f'fill="#8a7f6e">{subtitle}</text>'
        )
    parts.append(inner)
    parts.append("</svg>")
    write(rel, "\n".join(parts))


def write(rel, content):
    path = os.path.join(BASE, rel.replace("/", os.sep))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print("wrote", rel)


def label(x1, y1, x2, y2, text, anchor="start", color="#2c2a24"):
    """Leader line from (x1,y1) to (x2,y2) with a dot and text at the end."""
    dx = 6 if anchor == "start" else -6
    return (
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#8a7f6e" '
        f'stroke-width="1.5"/>'
        f'<circle cx="{x1}" cy="{y1}" r="3.5" fill="#c0392b"/>'
        f'<text x="{x2+dx}" y="{y2+4}" text-anchor="{anchor}" font-size="13" '
        f'fill="{color}">{text}</text>'
    )


def camera_front(tx, ty, s=1.0, dial="A"):
    """Detailed PEN E-P7 front view. Local box ~ 300 x 200."""
    g = f'<g transform="translate({tx},{ty}) scale({s})" filter="url(#soft)">'
    body = [
        # silver body
        '<rect x="6" y="26" width="288" height="150" rx="16" fill="url(#gSilver)" stroke="#9a927f" stroke-width="2"/>',
        # top plate
        '<rect x="6" y="26" width="288" height="34" rx="16" fill="url(#gTop)" stroke="#b7b1a4" stroke-width="1"/>',
        '<rect x="6" y="48" width="288" height="14" fill="url(#gTop)"/>',
        # leatherette wrap
        '<rect x="14" y="70" width="210" height="98" rx="8" fill="url(#gLeather)"/>',
        '<rect x="14" y="70" width="210" height="98" rx="8" fill="none" stroke="#000" stroke-opacity="0.25"/>',
        # grip
        '<rect x="250" y="66" width="40" height="104" rx="12" fill="url(#gSilver)" stroke="#9a927f"/>',
        # hot shoe
        '<rect x="120" y="10" width="46" height="18" rx="3" fill="#c9c3b5" stroke="#8a7f6e"/>',
        '<rect x="128" y="14" width="30" height="10" rx="2" fill="#6f6a5e"/>',
        # mode dial (right)
        '<circle cx="248" cy="42" r="21" fill="url(#gDial)" stroke="#7d7768" stroke-width="2"/>',
        f'<text x="248" y="47" text-anchor="middle" font-size="15" font-weight="700" fill="#2c2a24">{dial}</text>',
        # shutter + front dial
        '<circle cx="206" cy="44" r="12" fill="url(#gDial)" stroke="#7d7768"/>',
        '<circle cx="206" cy="44" r="6" fill="#b5651d"/>',
        # profile dial front-left
        '<circle cx="44" cy="150" r="15" fill="url(#gDial)" stroke="#7d7768" stroke-width="1.5"/>',
        '<circle cx="44" cy="150" r="4" fill="#8a7f6e"/>',
        # lens mount ring
        '<circle cx="150" cy="120" r="58" fill="#d9d4c8" stroke="#9a927f" stroke-width="3"/>',
        '<circle cx="150" cy="120" r="50" fill="#2a2723"/>',
        # lens glass
        '<circle cx="150" cy="120" r="42" fill="url(#gGlass)" stroke="#0b1720" stroke-width="2"/>',
        '<ellipse cx="136" cy="104" rx="16" ry="10" fill="#ffffff" fill-opacity="0.35"/>',
        '<circle cx="150" cy="120" r="42" fill="none" stroke="#5c6b74" stroke-opacity="0.5"/>',
        # red alignment dot
        '<circle cx="150" cy="64" r="4" fill="#c0392b"/>',
        # logo
        '<text x="40" y="46" font-size="12" font-weight="700" fill="#4a453d" letter-spacing="1">PEN</text>',
    ]
    return g + "".join(body) + "</g>"


def camera_back(tx, ty, s=1.0):
    """PEN E-P7 back view with tilting screen. Local box ~ 300 x 200."""
    g = f'<g transform="translate({tx},{ty}) scale({s})" filter="url(#soft)">'
    body = [
        '<rect x="6" y="26" width="288" height="150" rx="16" fill="url(#gSilver)" stroke="#9a927f" stroke-width="2"/>',
        '<rect x="6" y="26" width="288" height="30" rx="16" fill="url(#gTop)"/>',
        # screen
        '<rect x="26" y="62" width="176" height="104" rx="6" fill="#12161c" stroke="#3a3f47" stroke-width="3"/>',
        '<rect x="34" y="70" width="160" height="88" rx="3" fill="#20323f"/>',
        '<ellipse cx="70" cy="92" rx="26" ry="14" fill="#ffffff" fill-opacity="0.10"/>',
        '<text x="114" y="120" text-anchor="middle" font-size="12" fill="#7fa7c9">3.0\u2033 触摸屏</text>',
        # mode dial top-right
        '<circle cx="250" cy="44" r="18" fill="url(#gDial)" stroke="#7d7768" stroke-width="2"/>',
        # rear command dial
        '<circle cx="250" cy="86" r="15" fill="url(#gDial)" stroke="#7d7768"/>',
        # 4-way pad
        '<circle cx="250" cy="130" r="24" fill="#e6e2d9" stroke="#9a927f"/>',
        '<circle cx="250" cy="130" r="8" fill="#c9c3b5" stroke="#8a7f6e"/>',
        # buttons
        '<circle cx="224" cy="70" r="5" fill="#c9c3b5"/>',
        '<circle cx="276" cy="70" r="5" fill="#c9c3b5"/>',
        '<circle cx="224" cy="160" r="5" fill="#c9c3b5"/>',
        '<circle cx="276" cy="160" r="5" fill="#c0392b"/>',
        '<text x="114" y="150" text-anchor="middle" font-size="10" fill="#5c6b74">可上翻 / 下翻自拍</text>',
    ]
    return g + "".join(body) + "</g>"


def lens(tx, ty, s=1.0, kind="zoom", ring="#c9c3b5"):
    """Draw a lens barrel. kind='pancake' (14-42) or 'tele' (40-150)."""
    g = f'<g transform="translate({tx},{ty}) scale({s})" filter="url(#soft)">'
    if kind == "pancake":
        body = [
            '<rect x="20" y="40" width="140" height="70" rx="10" fill="url(#gLeather)"/>',
            '<rect x="20" y="40" width="140" height="14" rx="6" fill="#4a453d"/>',
            f'<rect x="150" y="34" width="18" height="82" rx="6" fill="{ring}" stroke="#8a7f6e"/>',
            '<ellipse cx="168" cy="75" rx="10" ry="41" fill="url(#gGlass)"/>',
            '<ellipse cx="164" cy="60" rx="4" ry="10" fill="#ffffff" fill-opacity="0.4"/>',
        ]
    else:
        body = [
            '<rect x="10" y="46" width="150" height="58" rx="12" fill="url(#gLeather)"/>',
            '<rect x="40" y="42" width="60" height="66" rx="6" fill="#332f2a"/>',
            f'<rect x="150" y="40" width="22" height="70" rx="6" fill="{ring}" stroke="#8a7f6e"/>',
            '<ellipse cx="172" cy="75" rx="12" ry="35" fill="url(#gGlass)"/>',
            '<ellipse cx="168" cy="62" rx="5" ry="9" fill="#ffffff" fill-opacity="0.4"/>',
        ]
    return g + "".join(body) + "</g>"
