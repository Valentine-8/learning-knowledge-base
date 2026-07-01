#!/usr/bin/env python3
"""Prefer official webp over svg placeholders when files exist."""
import os

GUIDE = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
IMAGES = os.path.join(GUIDE, "images")

PREFER_WEBP = {
    "images/body/front-hero.svg": "images/body/front-hero.webp",
    "images/body/front-back.svg": "images/body/front-back.webp",
    "images/lenses/14-42-ez.svg": "images/lenses/14-42-ez.webp",
    "images/lenses/40-150-r.svg": "images/lenses/40-150-r.webp",
    "images/body/mode-dial.svg": "images/body/profile-dial.webp",
}


def exists(rel: str) -> bool:
    return os.path.isfile(os.path.join(GUIDE, rel.replace("/", os.sep)))


def main() -> None:
    for root, _, files in os.walk(GUIDE):
        if "scripts" in root.replace("\\", "/"):
            continue
        if root.replace("\\", "/").endswith("/images"):
            continue
        for fn in files:
            if not fn.endswith(".md"):
                continue
            path = os.path.join(root, fn)
            with open(path, encoding="utf-8") as f:
                text = f.read()
            new = text
            for old, new_path in PREFER_WEBP.items():
                if exists(new_path):
                    new = new.replace(old, new_path)
            if new != text:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(new)
                print("updated", fn)


if __name__ == "__main__":
    main()
