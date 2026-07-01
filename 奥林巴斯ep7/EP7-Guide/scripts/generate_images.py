#!/usr/bin/env python3
"""Regenerate all EP7 Guide illustrations (refined vector art).

Implementation lives in `art.py` + `svgkit.py`. This is the canonical entry
point kept for backwards compatibility.

    python EP7-Guide/scripts/generate_images.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from art import build_all

if __name__ == "__main__":
    build_all()
    print("done — all refined SVGs regenerated")
