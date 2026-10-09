"""Shared palette, font embedding and helpers for the profile SVG assets."""
import base64
import io
import os
import subprocess
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_SRC = {
    ("Space Grotesk", 500): "node_modules/@fontsource/space-grotesk/files/space-grotesk-latin-500-normal.woff2",
    ("Space Grotesk", 700): "node_modules/@fontsource/space-grotesk/files/space-grotesk-latin-700-normal.woff2",
    ("JetBrains Mono", 400): "node_modules/@fontsource/jetbrains-mono/files/jetbrains-mono-latin-400-normal.woff2",
    ("JetBrains Mono", 500): "node_modules/@fontsource/jetbrains-mono/files/jetbrains-mono-latin-500-normal.woff2",
    ("JetBrains Mono", 700): "node_modules/@fontsource/jetbrains-mono/files/jetbrains-mono-latin-700-normal.woff2",
}

PALETTES = {
    "dark": {
        "bg0": "#070B1A", "bg1": "#0D1330", "surface": "#111936", "surface2": "#172046",
        "border": "#27315E", "grid": "#1A2350",
        "text": "#EEF2FF", "muted": "#A3AED0", "faint": "#8691B8",
        "violet": "#9B7BFF", "cyan": "#2EE6F6", "blue": "#4F8BFF", "green": "#3DDC97",
        "amber": "#FFC266", "glow1": "#6D4AFF", "glow2": "#00B8D9",
    },
    "light": {
        "bg0": "#FFFFFF", "bg1": "#F2F4FF", "surface": "#FFFFFF", "surface2": "#F5F6FD",
        "border": "#D8DDF0", "grid": "#E6E9F7",
        "text": "#0B1230", "muted": "#47517A", "faint": "#5E6890",
        "violet": "#5B32E0", "cyan": "#0B7A8F", "blue": "#2357D9", "green": "#0B7A55",
        "amber": "#9A5B00", "glow1": "#B9A6FF", "glow2": "#8BE7F2",
    },
}


def font_face_css(usage):
    """usage: dict {(family, weight): text_used}. Returns @font-face CSS with
    per-file subset fonts embedded as base64 so GitHub's <img> rendering keeps
    the typography without loading anything external."""
    css = []
    for (family, weight), text in usage.items():
        src = os.path.join(ROOT, FONT_SRC[(family, weight)])
        chars = "".join(sorted(set(text + " ")))
        with tempfile.TemporaryDirectory() as td:
            out = os.path.join(td, "f.woff2")
            txt = os.path.join(td, "chars.txt")
            with open(txt, "w", encoding="utf-8") as fh:
                fh.write(chars)
            subprocess.run(
                ["pyftsubset", src, f"--text-file={txt}", "--flavor=woff2",
                 f"--output-file={out}", "--layout-features=kern,liga,calt",
                 "--no-hinting", "--desubroutinize"],
                check=True, capture_output=True)
            data = base64.b64encode(open(out, "rb").read()).decode()
        css.append(
            f"@font-face{{font-family:'{family}';font-weight:{weight};"
            f"src:url(data:font/woff2;base64,{data}) format('woff2');}}")
    return "".join(css)


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;"))


def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)
    print(f"wrote {path} ({len(content.encode())/1024:.1f} KB)")
