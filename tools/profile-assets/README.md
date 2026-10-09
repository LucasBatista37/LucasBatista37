# Assets do perfil

Geradores das imagens usadas no `README.md` do perfil. Tudo é gerado localmente e
versionado em `assets/`, então o README não depende de serviços de badge ou de
estatísticas de terceiros.

| Arquivo | Gera | Fonte dos dados |
| --- | --- | --- |
| `gen/hero.py` | `assets/branding/hero*.svg` | textos no próprio script |
| `gen/buttons.py` | `assets/buttons/btn-*.svg` | textos no próprio script |
| `gen/stack.py` | `assets/sections/stack*.svg` | lista `GROUPS` + [Simple Icons](https://simpleicons.org) (CC0) |
| `gen/cards.py` | `assets/projects/*.webp` | capturas em `src/` (cases públicos em lucasbatista.com, Google Play e sites no ar) |
| `previews.sh` | `assets/previews/*.webp` | vídeos públicos dos cases em lucasbatista.com |

O card de atividade e a snake **não** ficam aqui: são gerados todo dia pelo workflow
`.github/workflows/profile-assets.yml` e publicados no branch `output`.

## Regenerar

```bash
pip install playwright pillow fonttools brotli
python -m playwright install chromium
bash tools/profile-assets/build.sh      # hero, botões, stack e cards
bash tools/profile-assets/previews.sh   # prévias animadas (precisa de ffmpeg com libwebp)
```

## Atualizar um projeto

1. Troque a captura em `src/` (mantenha só dados de demonstração ou páginas públicas).
2. Edite o texto do card em `gen/cards.py` (`FEATURED` ou `CLIENTS`).
3. Rode `build.sh`, confira as imagens e atualize a descrição correspondente no `README.md`.

## Regras de conteúdo

- Status, números e funcionalidades só entram se estiverem em uma fonte pública (case, loja, site do produto ou repositório).
- Capas ilustrativas (como a do Nexo OS) são identificadas como ilustração e mostram apenas o que o projeto documenta.
- Projetos de clientes aparecem só no nível já publicado em cupcakelabs.com.br ou lucasbatista.com.

Fontes: Space Grotesk e JetBrains Mono (SIL OFL 1.1), embutidas nos SVGs em subconjuntos.
