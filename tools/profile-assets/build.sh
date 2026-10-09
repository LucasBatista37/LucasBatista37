#!/usr/bin/env bash
# Regenera os assets estáticos do README. Requisitos: Node 20+, Python 3.10+,
# `pip install playwright pillow fonttools brotli` e `python -m playwright install chromium`.
set -euo pipefail
cd "$(dirname "$0")"
REPO="$(git rev-parse --show-toplevel)"
[ -d node_modules ] || npm ci --no-audit --no-fund || npm install --no-audit --no-fund
node export-icons.mjs
python3 gen/hero.py    "$REPO/assets/branding"
python3 gen/buttons.py "$REPO/assets/buttons"
python3 gen/stack.py   "$REPO/assets/sections"
python3 gen/cards.py   "$REPO/assets/projects"
echo "ok — confira os arquivos em $REPO/assets"
