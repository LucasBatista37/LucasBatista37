#!/usr/bin/env bash
# Gera as prévias animadas (WebP) a partir dos vídeos públicos dos cases em lucasbatista.com.
# Requisitos: curl e ffmpeg com libwebp.
set -euo pipefail
cd "$(dirname "$0")"
REPO="$(git rev-parse --show-toplevel)"
OUT="$REPO/assets/previews"; TMP="$(mktemp -d)"; mkdir -p "$OUT"
BASE="https://www.lucasbatista.com/projects"
# slug | vídeo do case | início (s) | duração (s)
while IFS='|' read -r slug video start dur; do
  curl -fsSL "$BASE/$slug/videos/$video" -o "$TMP/$slug.mp4"
  ffmpeg -v error -y -ss "$start" -t "$dur" -i "$TMP/$slug.mp4" \
    -vf "setpts=PTS/1.4,fps=10,scale=720:-2:flags=lanczos" \
    -c:v libwebp_anim -lossless 0 -q:v 50 -compression_level 6 -loop 0 -an "$OUT/$slug.webp"
  echo "$slug: $(du -k "$OUT/$slug.webp" | cut -f1) KB"
done <<'LIST'
vendai|02-realizacao-venda.mp4|14|16
petzara|01-hero-novo-agendamento.mp4|20|16
trativa|01-hero-pipeline-kanban.mp4|34|16
qrpronto|01-criar-qr-do-zero.mp4|14|16
ciclou|01-solicitacao-e-proposta.mp4|8|16
LIST
rm -rf "$TMP"
