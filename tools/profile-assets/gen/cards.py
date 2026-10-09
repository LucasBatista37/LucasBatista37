"""Project cards rendered with Playwright from real screenshots (dark + light).

Featured cards: 1200x860. Client cards: 800x620.
Every screenshot comes from the public portfolio case videos, the Google Play
listing or the live site. Nexo OS gets an explicitly illustrative cover built
only from what its README documents (no fake UI).
"""
import os
import sys
import tempfile
from playwright.sync_api import sync_playwright
from PIL import Image

sys.path.insert(0, os.path.dirname(__file__))
from common import PALETTES  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
OUT = sys.argv[1]
TMP = tempfile.mkdtemp()
NM = os.path.join(ROOT, "node_modules/@fontsource")

FEATURED = [
    dict(slug="vendai", name="Vendaí", kicker="Produto próprio · PDV", status=("Em produção", "green"),
         tagline="PDV offline-first com desktop, nuvem de sincronização e app de gestão",
         media=("browser", "usevendai.com.br", "vendai.jpg", "top")),
    dict(slug="petzara", name="Petzara", kicker="Produto próprio · SaaS", status=("Em produção", "green"),
         tagline="Gestão para petshops: agenda em tempo real, financeiro, equipe e assinatura",
         media=("browser", "petzara.app", "petzara.jpg", "top")),
    dict(slug="trativa", name="Trativa", kicker="Produto próprio · SaaS", status=("Beta", "amber"),
         tagline="CRM multiempresa com pipeline kanban, metas e WhatsApp oficial",
         media=("browser", "trativa.app", "trativa.jpg", "top")),
    dict(slug="qrpronto", name="QRPronto", kicker="Produto próprio · Produto digital", status=("Em produção", "green"),
         tagline="Gerador de QR grátis no navegador e painel de QR dinâmico com destino editável",
         media=("browser", "qrpronto.com", "qrpronto.jpg", "top")),
    dict(slug="ciclou", name="Ciclou", kicker="Parceria · App Android", status=("Na Google Play", "green"),
         tagline="Liga quem descarta óleo de cozinha a coletores — da proposta ao certificado",
         media=("phones", None, ["ciclou_p1.jpg", "ciclou_p2.jpg", "ciclou_p4.jpg"], None)),
    dict(slug="nexo-os", name="Nexo OS", kicker="Open source · Sistemas", status=("Em desenvolvimento", "blue"),
         tagline="Sistema operacional próprio em Rust: loader UEFI, kernel x86_64 e serviços isolados",
         media=("nexo", None, None, None)),
]

CLIENTS = [
    dict(slug="eacentral", name="EA Central", kicker="Cliente · E-commerce B2B",
         media=("browser", "eacentral.com.br", "eacentral.jpg", "top")),
    dict(slug="maisclean", name="Mais Clean", kicker="Cliente · Site institucional",
         media=("browser", "maiscleanhigienizacao.com.br", "maisclean.jpg", "top")),
    dict(slug="gesso", name="Gesso Grande Rocha", kicker="Cliente · Site institucional",
         media=("browser", "gessogranderocha.com.br", "gesso.jpg", "top")),
]

NEXO_LAYERS = [
    ("userspace", "init · svcmgr · shell · compositor"),
    ("services", "vfs · devmgr · drivers VirtIO em modo usuário"),
    ("kernel", "x86_64 · SMP · escalonador preemptivo · IPC"),
    ("boot", "loader UEFI próprio · BootInfo versionado"),
]


def fonts_css():
    return "".join(
        f"@font-face{{font-family:'{fam}';font-weight:{w};src:url('file://{NM}/{pkg}/files/{pkg}-latin-{w}-normal.woff2')}}"
        for fam, pkg, ws in [("Space Grotesk", "space-grotesk", [500, 700]),
                             ("JetBrains Mono", "jetbrains-mono", [400, 500])] for w in ws)


def media_html(m, p, theme):
    kind = m[0]
    if kind == "browser":
        _, url, img, pos = m
        return f'''<div class="browser"><div class="bar"><i></i><i></i><i></i><span class="url">{url}</span></div>
<div class="shot" style="background-image:url('file://{SRC}/{img}');background-position:center {pos}"></div></div>'''
    if kind == "phones":
        phones = "".join(f'<div class="phone p{i}"><div class="screen" style="background-image:url(\'file://{SRC}/{f}\')"></div></div>'
                         for i, f in enumerate(m[2]))
        return f'<div class="stage phones">{phones}</div>'
    if kind == "nexo":
        rows = "".join(f'<div class="layer l{i}"><b>{a}/</b><span>{b}</span></div>' for i, (a, b) in enumerate(NEXO_LAYERS))
        return f'''<div class="stage nexo"><div class="term">
<div class="tbar"><i></i><i></i><i></i><span>nexo-os · arquitetura (ilustração)</span></div>
<div class="tbody"><div class="cmd"><em>$</em> make image &amp;&amp; make run</div>{rows}
<div class="foot">Rust estável · x86_64 · QEMU · CI</div></div></div></div>'''
    raise ValueError(kind)


def page(card, theme, size):
    p = PALETTES[theme]
    W, H = size
    small = W < 1000
    status = card.get("status")
    status_html = ""
    if status:
        label, color = status
        status_html = f'<div class="status"><span style="background:{p[color]}"></span>{label}</div>'
    tagline = f'<div class="tag">{card["tagline"]}</div>' if card.get("tagline") else ""
    dark = theme == "dark"
    return f'''<html><head><style>{fonts_css()}
*{{box-sizing:border-box;margin:0}}
html,body{{background:transparent;width:{W}px;height:{H}px}}
.card{{position:relative;width:{W}px;height:{H}px;border-radius:{28 if small else 34}px;overflow:hidden;
 background:radial-gradient(120% 90% at 100% 0%, {p["glow1"]}{"55" if dark else "40"} 0%, transparent 55%),
 radial-gradient(90% 80% at 0% 100%, {p["glow2"]}{"33" if dark else "40"} 0%, transparent 60%),
 linear-gradient(160deg,{p["bg0"]},{p["bg1"]});
 border:2px solid {p["border"]};font-family:'Space Grotesk',sans-serif;color:{p["text"]}}}
.media{{position:absolute;left:{28 if small else 40}px;right:{28 if small else 40}px;top:{28 if small else 40}px;height:{(H*0.64) if not small else (H*0.63)}px}}
.browser{{width:100%;height:100%;border-radius:16px;overflow:hidden;border:1.5px solid {p["border"]};background:{p["surface"]};
 box-shadow:0 18px 50px {"#00000080" if dark else "#3b3f7a33"}}}
.bar{{height:{30 if small else 40}px;display:flex;align-items:center;gap:8px;padding:0 16px;background:{p["surface2"]};border-bottom:1px solid {p["border"]}}}
.bar i{{width:11px;height:11px;border-radius:50%;background:{p["border"]}}}
.url{{margin-left:14px;font:500 {13 if small else 16}px 'JetBrains Mono';color:{p["muted"]};background:{p["bg0"]};padding:4px 14px;border-radius:8px;border:1px solid {p["border"]}}}
.shot{{width:100%;height:calc(100% - {30 if small else 40}px);background-size:cover;background-repeat:no-repeat}}
.stage{{width:100%;height:100%;border-radius:16px;border:1.5px solid {p["border"]};overflow:hidden;position:relative}}
.phones{{background:linear-gradient(135deg,#0f7a3e,#16a34a 55%,#86efac);display:flex;justify-content:center;align-items:flex-start;gap:34px;padding-top:34px}}
.phone{{width:236px;height:500px;border-radius:34px;background:#0b0f19;padding:9px;box-shadow:0 22px 50px #00000059}}
.phone .screen{{width:100%;height:100%;border-radius:26px;background-size:cover;background-position:top center}}
.phone.p1{{margin-top:42px}}
.nexo{{background:linear-gradient(135deg,#0a0d16,#151b2e);display:flex;align-items:center;justify-content:center}}
.term{{width:88%;border-radius:14px;border:1px solid #2a3350;background:#0b0f1a;box-shadow:0 20px 60px #0009;overflow:hidden}}
.tbar{{height:38px;display:flex;align-items:center;gap:8px;padding:0 16px;background:#121828;border-bottom:1px solid #222a44}}
.tbar i{{width:11px;height:11px;border-radius:50%;background:#2a3350}}
.tbar span{{margin-left:12px;font:500 15px 'JetBrains Mono';color:#8d97b8}}
.tbody{{padding:22px 26px;font:400 19px 'JetBrains Mono';color:#cfd6ee}}
.cmd{{margin-bottom:16px;color:#e7ecff}} .cmd em{{color:#ff8a4c;font-style:normal;margin-right:8px}}
.layer{{display:flex;gap:16px;align-items:center;padding:12px 16px;margin:8px 0;border-radius:10px;border:1px solid #26304d;background:#111829}}
.layer b{{color:#ff8a4c;min-width:130px;font-weight:500}} .layer span{{color:#aeb8d8}}
.l0{{border-left:3px solid #c084fc}} .l1{{border-left:3px solid #38bdf8}} .l2{{border-left:3px solid #fb923c}} .l3{{border-left:3px solid #f43f5e}}
.foot{{margin-top:14px;font-size:15px;color:#6f7aa0}}
.info{{position:absolute;left:{30 if small else 46}px;right:{30 if small else 46}px;bottom:{26 if small else 40}px}}
.kicker{{font:500 {17 if small else 19}px 'JetBrains Mono';color:{p["violet"]};text-transform:uppercase;letter-spacing:.06em}}
.row{{display:flex;align-items:center;justify-content:space-between;gap:20px;margin-top:{4 if small else 6}px}}
.name{{font-weight:700;font-size:{52 if small else 66}px;letter-spacing:-.025em;line-height:1.05}}
.status{{display:flex;align-items:center;gap:10px;font:500 20px 'JetBrains Mono';color:{p["text"]};padding:10px 18px;border-radius:999px;background:{p["surface2"]};border:1.5px solid {p["border"]};white-space:nowrap}}
.status span{{width:12px;height:12px;border-radius:50%}}
.tag{{margin-top:8px;font-weight:500;font-size:27px;color:{p["muted"]};line-height:1.3}}
</style></head><body><div class="card">
<div class="media">{media_html(card["media"], p, theme)}</div>
<div class="info"><div class="kicker">{card["kicker"]}</div><div class="row"><div class="name">{card["name"]}</div>{status_html}</div>{tagline}</div>
</div></body></html>'''


def render(cards, size, prefix):
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page(viewport={"width": size[0], "height": size[1]}, device_scale_factor=1)
        for card in cards:
            for theme in ("dark", "light"):
                html = page(card, theme, size)
                tmp = os.path.join(TMP, "card.html")
                open(tmp, "w", encoding="utf-8").write(html)
                pg.goto(f"file://{tmp}")
                pg.wait_for_timeout(400)
                png = os.path.join(TMP, f"{prefix}{card['slug']}-{theme}.png")
                pg.screenshot(path=png, omit_background=True)
                out = os.path.join(OUT, f"{prefix}{card['slug']}-{theme}.webp")
                Image.open(png).save(out, "WEBP", quality=84, method=6)
                print(out, f"{os.path.getsize(out)/1024:.0f} KB")
        b.close()


os.makedirs(OUT, exist_ok=True)
which = sys.argv[2] if len(sys.argv) > 2 else "all"
if which in ("all", "featured"):
    render(FEATURED, (1200, 860), "")
if which in ("all", "clients"):
    render(CLIENTS, (800, 620), "client-")
