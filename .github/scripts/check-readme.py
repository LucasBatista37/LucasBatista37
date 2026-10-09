#!/usr/bin/env python3
"""Validações estruturais do README do perfil (sem dependências externas).

- toda <img> tem alt descritivo;
- todo arquivo local referenciado (src/srcset/links relativos) existe;
- imagens locais respeitam um limite de tamanho;
- SVGs locais são XML válido, sem <script> nem recursos externos;
- imagens externas só vêm de hosts esperados;
- links internos (#ancora) apontam para títulos existentes.
"""
import os
import re
import sys
import unicodedata
import xml.etree.ElementTree as ET
from urllib.parse import urlparse

README = sys.argv[1] if len(sys.argv) > 1 else "README.md"
BASE = os.path.dirname(os.path.abspath(README))
MAX_BYTES = 1_000_000
ALLOWED_IMAGE_HOSTS = {"raw.githubusercontent.com"}

text = open(README, encoding="utf-8").read()
errors, warnings = [], []

# --- imagens ---------------------------------------------------------------
for tag in re.findall(r"<img\b[^>]*>", text, flags=re.I):
    alt = re.search(r'\balt="([^"]*)"', tag)
    if not alt or len(alt.group(1).strip()) < 3:
        errors.append(f"<img> sem alt descritivo: {tag[:90]}")

refs = re.findall(r'\b(?:src|srcset)="([^"]+)"', text)
refs += re.findall(r"!\[[^\]]*\]\(([^)\s]+)", text)
refs += [h for h in re.findall(r'\bhref="([^"]+)"', text) if not re.match(r"^(https?:|mailto:|#)", h)]
refs += [h for h in re.findall(r"\]\(([^)\s]+)\)", text) if not re.match(r"^(https?:|mailto:|#)", h)]

for ref in sorted(set(refs)):
    u = urlparse(ref)
    if u.scheme in ("http", "https"):
        if re.search(r"\.(svg|png|jpe?g|gif|webp)(\?|$)", u.path, re.I) and u.netloc not in ALLOWED_IMAGE_HOSTS:
            warnings.append(f"imagem externa fora da lista: {ref}")
        continue
    path = os.path.normpath(os.path.join(BASE, u.path))
    if not os.path.exists(path):
        errors.append(f"arquivo não encontrado: {ref}")
        continue
    if os.path.isfile(path):
        size = os.path.getsize(path)
        if re.search(r"\.(svg|png|jpe?g|gif|webp)$", path, re.I) and size > MAX_BYTES:
            errors.append(f"imagem grande demais ({size / 1024:.0f} KB > {MAX_BYTES // 1024} KB): {ref}")
        if path.endswith(".svg"):
            try:
                root = ET.parse(path).getroot()
            except ET.ParseError as exc:
                errors.append(f"SVG inválido {ref}: {exc}")
                continue
            raw = open(path, encoding="utf-8").read()
            if "<script" in raw.lower():
                errors.append(f"SVG com <script>: {ref}")
            if re.search(r'(?:href|src)="https?://', raw) or re.search(r"url\(['\"]?https?://", raw):
                errors.append(f"SVG carrega recurso externo (não funciona no GitHub): {ref}")
            if root.find("{http://www.w3.org/2000/svg}title") is None and "aria-label" not in root.attrib:
                warnings.append(f"SVG sem <title>/aria-label: {ref}")

# --- âncoras internas ------------------------------------------------------
def slug(heading):
    h = re.sub(r"<[^>]+>", "", heading).strip().lower()
    h = "".join(c for c in h if unicodedata.category(c)[0] in "LN" or c in " -_")
    return h.replace(" ", "-")

anchors = {slug(h) for h in re.findall(r"^#{1,6}\s+(.+)$", text, flags=re.M)}
anchors |= set(re.findall(r'\bid="([^"]+)"', text)) | set(re.findall(r'\bname="([^"]+)"', text))
for target in set(re.findall(r'(?:href="|\]\()#([^")]+)', text)):
    if target not in anchors:
        errors.append(f"âncora interna sem destino: #{target}")

for w in warnings:
    print(f"::warning::{w}")
for e in errors:
    print(f"::error::{e}")
print(f"{len(set(refs))} referências verificadas, {len(anchors)} âncoras, {len(errors)} erro(s), {len(warnings)} aviso(s)")
sys.exit(1 if errors else 0)
