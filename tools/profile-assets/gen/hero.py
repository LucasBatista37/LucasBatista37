"""Animated hero banner: wide (desktop) and compact (mobile), dark + light."""
import os
import sys
from common import PALETTES, font_face_css, esc, write

OUT = sys.argv[1]

NAME = "Lucas Batista"
ROLE = "Full Stack & Mobile Developer"
STATUS = "fundador da CupCakeLabs · disponível para novos projetos"
STATUS_SHORT = "fundador da CupCakeLabs"
LINES = [
    ("Vendaí", "PDV offline-first"),
    ("Petzara", "SaaS para petshops"),
    ("Trativa", "CRM com WhatsApp oficial"),
    ("QRPronto", "QR Code dinâmico"),
    ("Nexo OS", "sistema operacional em Rust"),
]
CHIPS = ["Web", "Mobile", "Desktop", "APIs", "SaaS"]
SLOT = 3.2
CYCLE = SLOT * len(LINES)

LAYOUTS = {
    # name, role, status, terminal box, chips, mono char width, diagram?
    "wide": dict(W=1200, H=420, pad=64, status_y=90, status_size=16, name_y=178, name_size=84,
                 role_y=226, role_size=26, box_y=268, box_w=590, box_h=54, line_size=20,
                 chips_y=346, chip_size=15, chip_h=34, diagram=True),
    "compact": dict(W=720, H=478, pad=48, status_y=76, status_size=22, name_y=176, name_size=92,
                    role_y=232, role_size=32, box_y=280, box_w=624, box_h=72, line_size=25,
                    chips_y=394, chip_size=20, chip_h=44, diagram=False),
}

# right-side "living architecture" diagram (wide layout only)
CLIENTS = [("Web", 112), ("Mobile", 210), ("Desktop", 308)]
CX, CW, CH = 724, 112, 50
API = (896, 182, 96, 106)
DATA = [("Banco", 132), ("Nuvem", 284)]
DX, DW = 1048, 112


def build(theme, layout):
    p = PALETTES[theme]
    L = LAYOUTS[layout]
    W, H, pad = L["W"], L["H"], L["pad"]
    status = STATUS if layout == "wide" else STATUS_SHORT
    mono_text = status + "".join(a + b for a, b in LINES) + "".join(CHIPS) + "$>· " \
        + "".join(c for c, _ in CLIENTS) + "API" + "".join(d for d, _ in DATA) + "REST · WS"
    css_fonts = font_face_css({
        ("Space Grotesk", 700): NAME,
        ("Space Grotesk", 500): ROLE,
        ("JetBrains Mono", 500): mono_text,
    })

    # --- terminal with typed product lines ----------------------------
    fs = L["line_size"]
    cw = fs * 0.602  # JetBrains Mono advance width
    bx, by, bw, bh = pad, L["box_y"], L["box_w"], L["box_h"]
    base_y = by + bh / 2 + fs * 0.36
    tx = bx + 20 + cw * 3.2
    typing_css, typing_svg = [], []
    for i, (name, desc) in enumerate(LINES):
        start = i * SLOT / CYCLE * 100
        type_end = (i * SLOT + 1.1) / CYCLE * 100
        hold_end = ((i + 1) * SLOT - 0.35) / CYCLE * 100
        end = (i + 1) * SLOT / CYCLE * 100
        n = len(name) + len(desc) + 3
        width = int(n * cw) + 30
        typing_css.append(
            f"@keyframes t{i}{{0%,{start:.2f}%{{width:0;opacity:1}}"
            f"{type_end:.2f}%{{width:{width}px;opacity:1}}"
            f"{hold_end:.2f}%{{width:{width}px;opacity:1}}"
            f"{end:.2f}%,100%{{width:{width}px;opacity:0}}}}"
            f".tl{i}{{animation:t{i} {CYCLE}s steps(1,end) infinite}}"
            f".tc{i}{{width:0;animation:t{i} {CYCLE}s linear infinite}}")
        typing_svg.append(
            f'<clipPath id="c{i}"><rect class="tc{i}" x="{tx}" y="{by}" height="{bh}"/></clipPath>'
            f'<g class="tl{i} reveal" clip-path="url(#c{i})">'
            f'<text x="{tx}" y="{base_y:.1f}" class="mono" font-size="{fs}" fill="{p["text"]}">'
            f'<tspan fill="{p["cyan"]}">{esc(name)}</tspan>'
            f'<tspan fill="{p["faint"]}"> · </tspan>{esc(desc)}</text>'
            f'<rect x="{tx + n * cw + 6:.1f}" y="{base_y - fs * 0.9:.1f}" width="{fs * 0.5:.1f}" '
            f'height="{fs * 1.1:.1f}" rx="2" fill="{p["cyan"]}" class="caret"/></g>')

    # --- chips ----------------------------------------------------------
    chips, x = [], pad
    cs, chh = L["chip_size"], L["chip_h"]
    for c in CHIPS:
        w = cs * 1.7 + len(c) * cs * 0.64
        chips.append(
            f'<rect x="{x:.1f}" y="{L["chips_y"]}" width="{w:.1f}" height="{chh}" rx="{chh / 2}" '
            f'fill="{p["surface2"]}" stroke="{p["border"]}"/>'
            f'<text x="{x + w / 2:.1f}" y="{L["chips_y"] + chh / 2 + cs * 0.36:.1f}" class="mono" '
            f'font-size="{cs}" text-anchor="middle" fill="{p["muted"]}">{c}</text>')
        x += w + cs * 0.66

    # --- diagram --------------------------------------------------------
    diagram, acx, acy = [], 0, 0
    if L["diagram"]:
        ax, ay, aw, ah = API
        acx, acy = ax + aw / 2, ay + ah / 2
        paths = []
        for _, cy in CLIENTS:
            sx, sy = CX + CW, cy + CH / 2
            paths.append(f"M{sx},{sy} C{sx + 40},{sy} {ax - 40},{acy} {ax},{acy}")
        for _, dy in DATA:
            sx, sy, ey = ax + aw, acy, dy + CH / 2
            paths.append(f"M{sx},{sy} C{sx + 30},{sy} {DX - 30},{ey} {DX},{ey}")
        for k, d in enumerate(paths):
            diagram.append(f'<path d="{d}" fill="none" stroke="{p["border"]}" stroke-width="2"/>')
            diagram.append(f'<path d="{d}" fill="none" stroke="url(#flow)" stroke-width="2" '
                           f'class="flow" style="animation-delay:{-k * 0.4:.1f}s"/>')
        for k, d in enumerate(paths):
            color = p["cyan"] if k < 3 else p["violet"]
            diagram.append(
                f'<circle r="4" fill="{color}" class="pkt" style="offset-path:path(\'{d}\');'
                f'animation-duration:{2.6 + (k % 3) * 0.5}s;animation-delay:{-k * 0.7:.1f}s"/>')

        def node(x, y, w, h, label, accent, sub=None):
            out = (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{p["surface"]}" '
                   f'stroke="{p["border"]}" stroke-width="1.5"/>'
                   f'<rect x="{x}" y="{y + 12}" width="3" height="{h - 24}" rx="1.5" fill="{accent}"/>')
            ty = y + h / 2 + (0 if sub else 5)
            out += (f'<text x="{x + w / 2}" y="{ty}" class="mono" font-size="15" text-anchor="middle" '
                    f'fill="{p["text"]}">{label}</text>')
            if sub:
                out += (f'<text x="{x + w / 2}" y="{ty + 20}" class="mono" font-size="11" '
                        f'text-anchor="middle" fill="{p["faint"]}">{sub}</text>')
            return out

        for label, cy in CLIENTS:
            diagram.append(node(CX, cy, CW, CH, label, p["blue"]))
        diagram.append(f'<rect x="{ax - 6}" y="{ay - 6}" width="{aw + 12}" height="{ah + 12}" rx="16" '
                       f'fill="none" stroke="{p["violet"]}" stroke-opacity=".35" class="pulse"/>')
        diagram.append(node(ax, ay, aw, ah, "API", p["violet"], "REST · WS"))
        for label, dy in DATA:
            diagram.append(node(DX, dy, DW, CH, label, p["cyan"]))

    glow = (f'<circle cx="{W - 190}" cy="60" r="150" fill="{p["glow1"]}" opacity=".55" filter="url(#blur)"/>'
            f'<circle cx="{W - 80}" cy="{H - 20}" r="130" fill="{p["glow2"]}" opacity=".55" filter="url(#blur)"/>'
            f'<circle cx="80" cy="{H + 10}" r="120" fill="{p["glow1"]}" opacity=".25" filter="url(#blur)"/>')
    ss = L["status_size"]
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="t d">
<title id="t">Lucas Batista — Full Stack &amp; Mobile Developer</title>
<desc id="d">Banner de apresentação: Lucas Batista, desenvolvedor full stack e mobile, fundador da CupCakeLabs. Alterna os produtos que desenvolve (Vendaí, Petzara, Trativa, QRPronto e Nexo OS){" e mostra um diagrama animado de clientes web, mobile e desktop ligados a uma API, banco de dados e nuvem" if L["diagram"] else ""}.</desc>
<defs>
<style>{css_fonts}
.sans{{font-family:'Space Grotesk',ui-sans-serif,system-ui,sans-serif}}
.mono{{font-family:'JetBrains Mono',ui-monospace,SFMono-Regular,Menlo,monospace}}
.flow{{stroke-dasharray:6 14;animation:flow 1.6s linear infinite}}
@keyframes flow{{to{{stroke-dashoffset:-40}}}}
.pkt{{offset-distance:0%;animation:pkt 3s cubic-bezier(.45,0,.25,1) infinite}}
@keyframes pkt{{0%{{offset-distance:0%;opacity:0}}10%{{opacity:1}}90%{{opacity:1}}100%{{offset-distance:100%;opacity:0}}}}
.pulse{{animation:pulse 2.4s ease-in-out infinite;transform-origin:{acx}px {acy}px}}
@keyframes pulse{{0%,100%{{opacity:.2;transform:scale(1)}}50%{{opacity:1;transform:scale(1.04)}}}}
.dot{{animation:blink 2s ease-in-out infinite}}
@keyframes blink{{0%,100%{{opacity:1}}50%{{opacity:.35}}}}
.caret{{animation:caret 1s steps(1) infinite}}
@keyframes caret{{50%{{opacity:0}}}}
{"".join(typing_css)}
@media (prefers-reduced-motion:reduce){{
.flow,.pkt,.pulse,.dot,.caret,.reveal,[class^="tc"]{{animation:none!important}}
.pkt,.reveal{{display:none}}
.tl0{{display:inline}}.tc0{{width:{W}px}}
}}
</style>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{p["bg0"]}"/><stop offset="1" stop-color="{p["bg1"]}"/></linearGradient>
<linearGradient id="flow" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{p["blue"]}"/><stop offset="1" stop-color="{p["cyan"]}"/></linearGradient>
<linearGradient id="name" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{p["text"]}"/><stop offset=".55" stop-color="{p["text"]}"/><stop offset="1" stop-color="{p["violet"]}"/></linearGradient>
<linearGradient id="edge" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{p["violet"]}" stop-opacity=".7"/><stop offset=".5" stop-color="{p["border"]}"/><stop offset="1" stop-color="{p["cyan"]}" stop-opacity=".7"/></linearGradient>
<pattern id="dots" width="24" height="24" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1.2" fill="{p["grid"]}"/></pattern>
<filter id="blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="60"/></filter>
<clipPath id="frame"><rect width="{W}" height="{H}" rx="28"/></clipPath>
</defs>
<g clip-path="url(#frame)">
<rect width="{W}" height="{H}" fill="url(#bg)"/>
<rect width="{W}" height="{H}" fill="url(#dots)" opacity="{".55" if theme == "dark" else ".9"}"/>
{glow}
</g>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="27" fill="none" stroke="url(#edge)" stroke-width="2"/>
<circle cx="{pad + 8}" cy="{L["status_y"] - ss * 0.36:.1f}" r="{ss * 0.38:.1f}" fill="{p["green"]}" class="dot"/>
<text x="{pad + 8 + ss}" y="{L["status_y"]}" class="mono" font-size="{ss}" fill="{p["muted"]}">{esc(status)}</text>
<text x="{pad - 2}" y="{L["name_y"]}" class="sans" font-size="{L["name_size"]}" font-weight="700" letter-spacing="{-L["name_size"] * 0.03:.1f}" fill="url(#name)">{NAME}</text>
<text x="{pad}" y="{L["role_y"]}" class="sans" font-size="{L["role_size"]}" font-weight="500" fill="{p["muted"]}">{esc(ROLE)}</text>
<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="12" fill="{p["surface"]}" stroke="{p["border"]}"/>
<text x="{bx + 20}" y="{base_y:.1f}" class="mono" font-size="{fs}" fill="{p["violet"]}">$&gt;</text>
{"".join(typing_svg)}
{"".join(chips)}
{"".join(diagram)}
</svg>'''
    return svg


for theme in ("dark", "light"):
    for layout in LAYOUTS:
        suffix = "" if layout == "wide" else "-mobile"
        write(os.path.join(OUT, f"hero{suffix}-{theme}.svg"), build(theme, layout))
