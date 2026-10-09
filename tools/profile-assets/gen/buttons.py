"""Link buttons (dark + light) — local SVGs so the README has no badge service dependency."""
import json
import os
import sys
from common import PALETTES, font_face_css, esc, write, ROOT

OUT = sys.argv[1]
ICONS = json.load(open(os.path.join(ROOT, "icons.json")))

GLOBE = '<circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" stroke-width="2"/><path d="M3 12h18M12 3c2.8 3 2.8 15 0 18M12 3c-2.8 3-2.8 15 0 18" fill="none" stroke="currentColor" stroke-width="2"/>'
MAIL = '<rect x="3" y="5" width="18" height="14" rx="2.5" fill="none" stroke="currentColor" stroke-width="2"/><path d="m4 7 8 6 8-6" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>'
LINKEDIN = '<rect x="3" y="3" width="18" height="18" rx="4" fill="currentColor"/><path d="M7.5 10.2v6.3M7.5 7.4v.1M11 16.5v-6.3m0 2.6c0-1.6 1-2.7 2.4-2.7s2.3 1 2.3 2.8v3.6" fill="none" stroke="var(--bg)" stroke-width="2" stroke-linecap="round"/>'
CODE = '<path d="m8 7-5 5 5 5M16 7l5 5-5 5M13.5 4.5l-3 15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
ARROW = '<path d="M5 12h14m-6-6 6 6-6 6" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>'
PLAY = '<path d="M5 3.5 20 12 5 20.5z" fill="currentColor"/>'


def simple(slug):
    return f'<path d="{ICONS[slug]["p"]}" fill="currentColor"/>'


BUTTONS = {
    "portfolio": ("Portfólio", GLOBE, True),
    "cupcakelabs": ("CupCakeLabs", CODE, False),
    "linkedin": ("LinkedIn", LINKEDIN, False),
    "contato": ("Contato", ARROW, False),
    "whatsapp": ("Conversar no WhatsApp", simple("whatsapp"), True),
    "email": ("E-mail", MAIL, False),
    "github-repo": ("Ver código", simple("github"), False),
}


def build(key, theme):
    label, icon, primary = BUTTONS[key]
    p = PALETTES[theme]
    fs, h = 17, 44
    w = int(18 + 22 + 10 + len(label) * fs * 0.53 + 18)
    css = font_face_css({("Space Grotesk", 700 if primary else 500): label})
    if primary:
        bg = 'fill="url(#g)"'
        fg = "#FFFFFF"
        stroke = ""
    else:
        bg = f'fill="{p["surface"]}"'
        fg = p["text"]
        stroke = f'stroke="{p["border"]}" stroke-width="1.5"'
    g1, g2 = ("#5B32E0", "#2357D9")
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(label)}">
<title>{esc(label)}</title>
<defs><style>{css}text{{font-family:'Space Grotesk',ui-sans-serif,system-ui,sans-serif}}</style>
<linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{g1}"/><stop offset="1" stop-color="{g2}"/></linearGradient></defs>
<rect x=".75" y=".75" width="{w - 1.5}" height="{h - 1.5}" rx="12" {bg} {stroke}/>
<g transform="translate(18,{(h - 22) / 2}) scale(.9167)" style="color:{fg}">{icon.replace("var(--bg)", p["surface"] if not primary else g1)}</g>
<text x="50" y="{h / 2 + fs * 0.36:.1f}" font-size="{fs}" font-weight="{700 if primary else 500}" fill="{fg}">{esc(label)}</text>
</svg>'''


for key in BUTTONS:
    for theme in ("dark", "light"):
        write(os.path.join(OUT, f"btn-{key}-{theme}.svg"), build(key, theme))
