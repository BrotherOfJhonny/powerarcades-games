#!/usr/bin/env bash
#
# PowerArcades Games — validação das ROMs locais.
#
# O script NÃO baixa, NÃO renomeia, NÃO altera e NÃO envia nada para fora
# da máquina. Ele apenas lê os arquivos já presentes em roms/ e gera
# roms/checksums.sha256 com caminhos relativos.
#
set -euo pipefail

EXPECTED_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
CURRENT_ROOT="$(pwd -P)"

if [[ "$CURRENT_ROOT" != "$EXPECTED_ROOT" ]]; then
  echo "Erro: execute em $EXPECTED_ROOT"
  exit 1
fi

if [[ ! -d "roms" ]]; then
  echo "Erro: diretório roms não encontrado."
  exit 1
fi

# Nomes reais em disco. A capitalização de TopGear2.sfc é significativa
# porque o GitHub Pages diferencia maiúsculas de minúsculas.
EXPECTED_ROMS=(
  "captain-america-and-the-avengers.sfc"
  "super-mario-world.sfc"
  "tmnt-4-turtles-in-time.sfc"
  "TopGear2.sfc"
)

# Limite do GitHub para arquivo individual: 100 MB.
MAX_BYTES=$((100 * 1024 * 1024))

failures=0
echo "== Validação de ROMs =="
printf '%-42s %10s  %s\n' "ARQUIVO" "BYTES" "RESULTADO"

for rom in "${EXPECTED_ROMS[@]}"; do
  path="roms/$rom"

  # 1. Existência (sensível a maiúsculas/minúsculas).
  if [[ ! -f "$path" ]]; then
    printf '%-42s %10s  %s\n' "$rom" "-" "FALHA: arquivo ausente"
    failures=$((failures + 1))
    continue
  fi

  # 2. Extensão.
  if [[ "$rom" != *.sfc ]]; then
    printf '%-42s %10s  %s\n' "$rom" "-" "FALHA: extensão inesperada"
    failures=$((failures + 1))
    continue
  fi

  # 3. Tamanho maior que zero e dentro do limite.
  size=$(stat -c '%s' "$path")
  if [[ "$size" -le 0 ]]; then
    printf '%-42s %10s  %s\n' "$rom" "$size" "FALHA: arquivo vazio"
    failures=$((failures + 1))
    continue
  fi
  if [[ "$size" -gt "$MAX_BYTES" ]]; then
    printf '%-42s %10s  %s\n' "$rom" "$size" "FALHA: acima de 100 MB"
    failures=$((failures + 1))
    continue
  fi

  # 4. Cabeçalho SNES: libmagic pode classificar ROMs válidas como data/zlib.
  if ! python3 "$EXPECTED_ROOT/scripts/check-snes-header.py" "$path"; then
    printf '%-42s %10s  %s\n' "$rom" "$size" "FALHA: cabeçalho SNES inválido"
    failures=$((failures + 1))
    continue
  fi

  # 5. Rejeitar explicitamente HTML, XML, texto e executáveis
  #    (páginas de erro salvas por engano no lugar da ROM).
  mime=$(file -b --mime-type "$path")
  case "$mime" in
    text/html|text/xml|application/xml|text/plain|application/x-dosexec|application/x-executable|application/x-sharedlib)
      printf '%-42s %10s  %s\n' "$rom" "$size" "FALHA: tipo proibido ($mime)"
      failures=$((failures + 1))
      continue
      ;;
  esac

  printf '%-42s %10s  %s\n' "$rom" "$size" "OK"
done

# Arquivos .sfc inesperados no diretório.
while IFS= read -r extra; do
  known=0
  for rom in "${EXPECTED_ROMS[@]}"; do
    [[ "$extra" == "$rom" ]] && known=1 && break
  done
  if [[ "$known" -eq 0 ]]; then
    echo "Aviso: ROM não catalogada encontrada: $extra"
  fi
done < <(find roms -maxdepth 1 -type f -name '*.sfc' -printf '%f\n' | sort)

if [[ "$failures" -gt 0 ]]; then
  echo
  echo "Resultado: $failures falha(s). checksums.sha256 NÃO foi gerado."
  exit 1
fi

# 6. Hashes com caminhos relativos, sem qualquer caminho absoluto.
(
  cd roms
  sha256sum -- *.sfc > checksums.sha256
)

echo
echo "roms/checksums.sha256 gerado:"
sed 's/^/  /' roms/checksums.sha256

# 7. Conferência imediata dos hashes recém-gravados.
(
  cd roms
  sha256sum -c --quiet checksums.sha256
)

echo
echo "Resultado: todas as ROMs válidas e verificadas."
