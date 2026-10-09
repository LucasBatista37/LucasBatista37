"""Tech stack panel built from Simple Icons (CC0) — wide + compact, dark + light."""
import json
import os
import sys
from common import PALETTES, font_face_css, esc, write, ROOT

OUT = sys.argv[1]
ICONS = json.load(open(os.path.join(ROOT, "icons.json")))

GROUPS = [
    ("Front-end", ["react", "typescript", "javascript", "nextdotjs", "vite", "tailwindcss"], True),
    ("Mobile & desktop", ["flutter", "dart", "electron"], True),
    ("Back-end", ["nodedotjs", "express", "nestjs", "socketdotio"], True),
    ("Dados", ["postgresql", "mongodb", "prisma", "sqlite", "firebase"], True),
    ("Produto & infra", ["stripe", "whatsapp", "vercel", "railway", "githubactions", "git"], True),
    ("Sistemas", ["rust"], True),
    ("Já usei em estudos", ["vuedotjs", "angular", "python", "php", "kotlin"], False),
]
LABELS = {"whatsapp": "WhatsApp Cloud API", "githubactions": "GitHub Actions"}


def lum(hexc):
    r, g, b = (int(hexc[i:i + 2], 16) / 255 for i in (0, 2, 4))
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def contrast(a, b):
    la, lb = sorted([lum(a), lum(b)], reverse=True)
    return (la + 0.05) / (lb + 0.05)


def build(theme, layout):
    p = PALETTES[theme]
    wide = layout == "wide"
    W = 1200 if wide else 720
    pad = 48 if wide else 40
    label_w = 210 if wide else 0
    fs = 18 if wide else 24
    chip_h = 46 if wide else 58
    icon = 22 if wide else 28
    gap = 10 if wide else 12
    texts = ""
    body = []
    y = pad + 34
    title = "Stack"
    body.append(f'<text x="{pad}" y="{y}" class="sans" font-size="{30 if wide else 38}" font-weight="700" fill="{p["text"]}">{title}</text>')
    legend = "● uso diário   ○ estudos e projetos pontuais"
    body.append(f'<text x="{W - pad}" y="{y}" class="mono" text-anchor="end" font-size="{14 if wide else 18}" fill="{p["faint"]}">{"uso diário · estudos" if not wide else legend}</text>')
    texts += title + legend + "uso diário · estudos"
    y += 34 if wide else 40
    for name, slugs, core in GROUPS:
        texts += name
        if wide:
            row_y = y
            body.append(f'<text x="{pad}" y="{row_y + chip_h / 2 + 6}" class="mono" font-size="16" fill="{p["muted"] if core else p["faint"]}">{esc(name)}</text>')
            x0 = pad + label_w
        else:
            body.append(f'<text x="{pad}" y="{y + 28}" class="mono" font-size="20" fill="{p["muted"] if core else p["faint"]}">{esc(name)}</text>')
            y += 42
            row_y = y
            x0 = pad
        x = x0
        for slug in slugs:
            ic = ICONS[slug]
            label = LABELS.get(slug, ic["t"])
            texts += label
            w = 16 + icon + 10 + len(label) * fs * 0.56 + 18
            if x + w > W - pad:
                x = x0
                row_y += chip_h + gap
            color = "#" + ic["h"]
            if contrast(ic["h"], p["surface"][1:]) < 3.0:
                color = p["text"]
            fill = p["surface"] if core else "none"
            stroke = p["border"]
            txt_color = p["text"] if core else p["muted"]
            op = "1" if core else ".75"
            scale = icon / 24
            body.append(
                f'<g opacity="{op}"><rect x="{x:.1f}" y="{row_y}" width="{w:.1f}" height="{chip_h}" rx="{chip_h / 2 if not core else 12}" '
                f'fill="{fill}" stroke="{stroke}" stroke-width="1.5"{" stroke-dasharray=\"4 4\"" if not core else ""}/>'
                f'<g transform="translate({x + 16:.1f},{row_y + (chip_h - icon) / 2:.1f}) scale({scale:.3f})">'
                f'<title>{esc(label)}</title><path d="{ic["p"]}" fill="{color if core else p["muted"]}"/></g>'
                f'<text x="{x + 16 + icon + 10:.1f}" y="{row_y + chip_h / 2 + fs * 0.36:.1f}" class="sans" font-size="{fs}" '
                f'font-weight="500" fill="{txt_color}">{esc(label)}</text></g>')
            x += w + gap
        y = row_y + chip_h + (gap + 8 if wide else 22)
    H = int(y + pad - 10)
    css_fonts = font_face_css({("Space Grotesk", 500): texts, ("Space Grotesk", 700): title,
                               ("JetBrains Mono", 500): texts})
    names = ", ".join(LABELS.get(s, ICONS[s]["t"]) for g in GROUPS if g[2] for s in g[1])
    extra = ", ".join(ICONS[s]["t"] for g in GROUPS if not g[2] for s in g[1])
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="t d">
<title id="t">Stack de Lucas Batista</title>
<desc id="d">Tecnologias de uso diário: {esc(names)}. Já usadas em estudos e projetos pontuais: {esc(extra)}.</desc>
<defs><style>{css_fonts}
.sans{{font-family:'Space Grotesk',ui-sans-serif,system-ui,sans-serif}}
.mono{{font-family:'JetBrains Mono',ui-monospace,SFMono-Regular,Menlo,monospace;font-weight:500}}
</style>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{p["bg0"]}"/><stop offset="1" stop-color="{p["bg1"]}"/></linearGradient></defs>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="24" fill="url(#bg)" stroke="{p["border"]}" stroke-width="1.5"/>
{"".join(body)}
</svg>'''


for theme in ("dark", "light"):
    for layout in ("wide", "compact"):
        suffix = "" if layout == "wide" else "-mobile"
        write(os.path.join(OUT, f"stack{suffix}-{theme}.svg"), build(theme, layout))
