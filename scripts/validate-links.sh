#!/usr/bin/env bash
#
# PowerArcades Games — validação de links e referências.
#
# Confere, sem acessar a rede, se todo href/src local realmente existe
# em disco, e se os links externos pertencem à lista permitida.
#
set -uo pipefail

EXPECTED_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
CURRENT_ROOT="$(pwd -P)"

if [[ "$CURRENT_ROOT" != "$EXPECTED_ROOT" ]]; then
  echo "Erro: execute em $EXPECTED_ROOT"
  exit 1
fi

# Prefixo do projeto no GitHub Pages (usado por 404.html).
SITE_PREFIX=""

# Domínios externos aceitos (apenas links de navegação, nunca recursos).
ALLOWED_EXTERNAL=(
  "https://www.owasp.community/chapters/sjc"
  "https://www.youtube.com/@powerarcades"
  "https://www.instagram.com/powerarcades"
  "https://www.tiktok.com/@powerarcades"
  "https://github.com/BrotherOfJhonny/powerarcades-games"
  "https://github.com/EmulatorJS/EmulatorJS"
  "https://dozeroaobasico.com.br/"
  "https://arcade.dozeroaobasico.com.br/"
  "http://www.sitemaps.org/schemas/sitemap/0.9"
)

failures=0
checked=0

is_allowed_external() {
  local url="$1" allowed
  for allowed in "${ALLOWED_EXTERNAL[@]}"; do
    [[ "$url" == "$allowed"* ]] && return 0
  done
  return 1
}

resolve_and_check() {
  # $1 = arquivo html de origem, $2 = referência bruta
  local src_file="$1" ref="$2" dir target

  # Ignora âncoras puras e esquemas especiais.
  case "$ref" in
    ""|"#"*|"data:"*|"blob:"*|"mailto:"*|"javascript:"*) return ;;
  esac

  # Externo.
  if [[ "$ref" == http://* || "$ref" == https://* ]]; then
    checked=$((checked + 1))
    if is_allowed_external "$ref"; then
      printf '  %-9s %s\n' "EXTERNO" "$ref"
    else
      printf '  %-9s %s  (em %s)\n' "NEGADO" "$ref" "${src_file#./}"
      failures=$((failures + 1))
    fi
    return
  fi

  # Remove query e fragmento.
  ref="${ref%%#*}"
  ref="${ref%%\?*}"
  [[ -z "$ref" ]] && return

  dir="$(dirname "$src_file")"

  if [[ "$ref" == /* ]]; then
    # Caminho absoluto de produção: precisa começar com o prefixo do site.
    if [[ "$ref" != "$SITE_PREFIX"* ]]; then
      printf '  %-9s %s  (em %s) prefixo do projeto ausente\n' \
        "QUEBRADO" "$ref" "${src_file#./}"
      failures=$((failures + 1))
      checked=$((checked + 1))
      return
    fi
    target=".${ref#$SITE_PREFIX}"
  else
    target="$dir/$ref"
  fi

  # Diretório -> index.html
  if [[ "$target" == */ ]]; then
    target="${target}index.html"
  fi

  checked=$((checked + 1))

  if [[ -e "$target" ]]; then
    printf '  %-9s %s\n' "OK" "$(realpath --relative-to=. "$target" 2>/dev/null || echo "$target")"
  else
    printf '  %-9s %s  (referenciado em %s como "%s")\n' \
      "QUEBRADO" "$target" "${src_file#./}" "$ref"
    failures=$((failures + 1))
  fi
}

echo "== Links e recursos por página =="

while IFS= read -r html_file; do
  echo
  echo "-- ${html_file#./}"
  while IFS= read -r ref; do
    resolve_and_check "$html_file" "$ref"
  done < <(
    grep -oE '(href|src)="[^"]*"' "$html_file" \
      | sed -E 's/^(href|src)="//; s/"$//' \
      | sort -u
  )
done < <(find . -path ./.git -prune -o -path ./data -prune -o -type f -name '*.html' -print | sort)

echo
echo "== URLs do sitemap =="
SITE_BASE="https://arcade.dozeroaobasico.com.br"
while IFS= read -r loc; do
  path="${loc#$SITE_BASE}"
  target=".${path}"
  [[ "$target" == */ ]] && target="${target}index.html"
  checked=$((checked + 1))
  if [[ -e "$target" ]]; then
    printf '  %-9s %s\n' "OK" "$loc"
  else
    printf '  %-9s %s  (arquivo esperado: %s)\n' "QUEBRADO" "$loc" "$target"
    failures=$((failures + 1))
  fi
done < <(grep -oE '<loc>[^<]+</loc>' sitemap.xml | sed -E 's#</?loc>##g')

echo
echo "== Canonical de cada página =="
while IFS= read -r html_file; do
  canon=$(grep -oE 'rel="canonical" href="[^"]+"' "$html_file" \
    | sed -E 's/.*href="//; s/"$//')
  if [[ -z "$canon" ]]; then
    # 404.html não precisa de canonical.
    if [[ "$(basename "$html_file")" != "404.html" ]]; then
      printf '  %-9s %s\n' "FALTANDO" "${html_file#./}"
      failures=$((failures + 1))
    fi
  else
    printf '  %-9s %s -> %s\n' "OK" "${html_file#./}" "$canon"
  fi
done < <(find . -path ./.git -prune -o -path ./data -prune -o -type f -name '*.html' -print | sort)

echo
echo "== Arquivos obrigatórios =="
for required in \
  index.html 404.html .nojekyll robots.txt sitemap.xml \
  README.md SECURITY.md CONTRIBUTING.md LICENSE \
  roms/checksums.sha256 data/loader.js data/emulator.min.js
do
  if [[ -e "$required" ]]; then
    printf '  %-9s %s\n' "OK" "$required"
  else
    printf '  %-9s %s\n' "AUSENTE" "$required"
    failures=$((failures + 1))
  fi
done

echo
echo "=================================================="
echo "Referências verificadas: $checked"
if [[ "$failures" -gt 0 ]]; then
  echo "RESULTADO: $failures problema(s) encontrado(s)."
  exit 1
fi
echo "RESULTADO: nenhum link quebrado e nenhum domínio externo inesperado."
exit 0
