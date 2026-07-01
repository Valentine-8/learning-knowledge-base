#!/usr/bin/env python3
"""Update image references in EP7 Guide markdown files."""
import os
import re

GUIDE = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

REPLACEMENTS = {
    "images/body/unboxing.jpg": "images/body/unboxing.svg",
    "images/body/battery-insert.jpg": "images/body/battery-insert.svg",
    "images/lenses/mount-align.jpg": "images/lenses/mount-align.svg",
    "images/body/strap.jpg": "images/body/strap.svg",
    "images/body/first-power-on.jpg": "images/body/mode-dial.svg",
    "images/body/front-back.jpg": "images/body/front-back.svg",
    "images/body/front.jpg": "images/body/front-hero.svg",
    "images/body/size-compare.jpg": "images/body/size-compare.svg",
    "images/body/mode-dial.jpg": "images/body/mode-dial.svg",
    "images/diagrams/aperture-blur.jpg": "images/diagrams/aperture-blur.svg",
    "images/diagrams/focal-length-14-42.jpg": "images/diagrams/focal-length-14-42.svg",
    "images/diagrams/focal-length-40-150.jpg": "images/diagrams/focal-length-40-150.svg",
    "images/diagrams/six-steps.jpg": "images/diagrams/six-steps.svg",
    "images/diagrams/checklist-card.jpg": "images/diagrams/checklist-card.svg",
    "images/diagrams/iso-compare.jpg": "images/diagrams/iso-compare.svg",
    "images/diagrams/af-single-point.jpg": "images/diagrams/af-single-point.svg",
    "images/diagrams/building-lines.jpg": "images/diagrams/building-lines.svg",
    "images/diagrams/blur-exif.jpg": "images/diagrams/blur-exif.svg",
    "images/diagrams/wb-compare.jpg": "images/diagrams/wb-compare.svg",
    "images/lenses/14-42-ez.jpg": "images/lenses/14-42-ez.svg",
    "images/lenses/40-150-r.jpg": "images/lenses/40-150-r.svg",
    "images/lenses/lens-change.jpg": "images/lenses/lens-change.svg",
    "images/menu/first-setup.jpg": "images/menu/first-setup.svg",
    "images/menu/super-control-panel.jpg": "images/menu/super-control-panel.svg",
    "images/menu/menu-overview.jpg": "images/menu/menu-overview.svg",
    "images/menu/scn-modes.jpg": "images/menu/scn-modes.svg",
    "images/menu/ap-modes.jpg": "images/menu/ap-modes.svg",
    "images/menu/live-composite.jpg": "images/menu/live-composite.svg",
    "images/buttons/profile-dial.jpg": "images/body/mode-dial.svg",
    "images/samples/portrait/setup.jpg": "images/samples/portrait/setup.svg",
    "images/samples/portrait/light-compare.jpg": "images/samples/portrait/light-compare.svg",
    "images/samples/landscape/wide.jpg": "images/samples/landscape/wide.svg",
    "images/samples/landscape/sunset.jpg": "images/samples/landscape/sunset.svg",
    "images/samples/night/handheld-vs-tripod.jpg": "images/samples/night/handheld-vs-tripod.svg",
    "images/menu/scp-labeled.jpg": "images/menu/super-control-panel.svg",
    "images/samples/night/stars.jpg": "images/samples/night/stars.svg",
}


def main():
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
            for old, new_path in REPLACEMENTS.items():
                new = new.replace(old, new_path)
            if new != text:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(new)
                print("updated", fn)


if __name__ == "__main__":
    main()
