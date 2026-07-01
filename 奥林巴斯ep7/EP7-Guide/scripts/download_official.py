#!/usr/bin/env python3
"""Download official OM System product images for EP7 Guide."""
import os
import ssl
import urllib.request

BASE = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "images"))

# OM System CDN (explore.omsystem.com/e-p7)
DOWNLOADS = {
    "body/front-hero.webp": "https://cdn.sanity.io/images/ipox1240/live/1ed9c4230a3e0272315fb6ea1ed8cb4b05990128-978x697.webp",
    "body/front-back.webp": "https://cdn.sanity.io/images/ipox1240/live/cab0df147b3c7b59151dfb6afce4606cddf2037b-979x700.webp",
    "body/profile-dial.webp": "https://cdn.sanity.io/images/ipox1240/live/0ebc45050d99e9f776708a7bec4fe2e392a2e7ce-1013x698.webp",
    "lenses/14-42-ez.webp": "https://cdn.sanity.io/images/ipox1240/live/c58655fa28072e644a1579e899eaf65d4176e0ed-461x525.webp",
    "lenses/40-150-r.webp": "https://cdn.sanity.io/images/ipox1240/live/e13b77d8f070deda97f199cdf11276504355b5de-464x524.webp",
}


def download(url: str, dest: str) -> bool:
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    ctx = ssl.create_default_context()
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "EP7-Guide/1.0"})
        with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
            data = resp.read()
        with open(dest, "wb") as f:
            f.write(data)
        print(f"ok  {os.path.basename(dest)} ({len(data) // 1024} KB)")
        return True
    except Exception as exc:
        print(f"skip {os.path.basename(dest)}: {exc}")
        return False


def main() -> None:
    ok = 0
    for rel, url in DOWNLOADS.items():
        if download(url, os.path.join(BASE, rel.replace("/", os.sep))):
            ok += 1
    print(f"downloaded {ok}/{len(DOWNLOADS)}")


if __name__ == "__main__":
    main()
