#!/usr/bin/env bash
#
# PowerArcades Games — teste HTTP local.
#
# Sobe um servidor estático na raiz do projeto e confere o código HTTP de
# cada recurso crítico. Nada é enviado para fora da máquina.
#
# Desde a migração para o subdomínio próprio (arcade.dozeroaobasico.com.br),
# o portal fica na RAIZ do site. Antes ele vivia sob /powerarcades-games/ e
# este script precisava de um espelho com symlink para reproduzir o prefixo;
# isso deixou de ser necessário.
#
set -uo pipefail

EXPECTED_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
CURRENT_ROOT="$(pwd -P)"

if [[ "$CURRENT_ROOT" != "$EXPECTED_ROOT" ]]; then
  echo "Erro: execute em $EXPECTED_ROOT"
  exit 1
fi

PORT="${PORT:-8080}"
BASE="http://127.0.0.1:${PORT}"

cleanup() {
  [[ -n "${SERVER_PID:-}" ]] && kill "$SERVER_PID" 2>/dev/null
  wait "${SERVER_PID:-}" 2>/dev/null
}
trap cleanup EXIT

python3 -m http.server "$PORT" --bind 127.0.0.1 --directory "$EXPECTED_ROOT" \
  >/dev/null 2>&1 &
SERVER_PID=$!

# Aguarda o servidor responder.
for _ in $(seq 1 40); do
  if curl -fsS -o /dev/null "$BASE/" 2>/dev/null; then break; fi
  sleep 0.25
done

if ! curl -fsS -o /dev/null "$BASE/" 2>/dev/null; then
  echo "Erro: servidor local não respondeu na porta $PORT."
  exit 1
fi

failures=0

check() {
  # $1 = caminho relativo ao BASE, $2 = código esperado
  local path="$1" want="$2" got
  got=$(curl -s -o /dev/null -w '%{http_code}' --max-time 20 "$BASE$path")
  if [[ "$got" == "$want" ]]; then
    printf '  %-3s  %-62s OK\n' "$got" "$path"
  else
    printf '  %-3s  %-62s FALHA (esperado %s)\n' "$got" "$path" "$want"
    failures=$((failures + 1))
  fi
}

echo "== Páginas =="
check "/" 200
check "/games/captain-america-and-the-avengers/" 200
check "/games/super-mario-world/" 200
check "/games/tmnt-4-turtles-in-time/" 200
check "/games/top-gear-2/" 200
check "/games/devfest-galactic/" 200
check "/games/devfest-galactic/engine.js" 200
check "/games/devfest-galactic/game.js" 200
check "/games/devfest-galactic/style.css" 200
check "/games/devfest-galactic/assets/chapter-qr.png" 200
check "/404.html" 200

echo
echo "== Estilos e scripts do portal =="
check "/assets/css/main.css" 200
check "/assets/css/game.css" 200
check "/assets/js/catalog.js" 200
check "/assets/js/ui.js" 200
check "/assets/js/game-loader.js" 200

echo
echo "== Imagens e ícones =="
check "/assets/images/logo-powerarcades.webp" 200
check "/assets/images/favicon.png" 200
check "/assets/images/social-share.webp" 200
check "/assets/images/default-game-cover.webp" 200
check "/assets/images/games/captain-america-and-the-avengers.webp" 200
check "/assets/images/games/super-mario-world.webp" 200
check "/assets/images/games/tmnt-4-turtles-in-time.webp" 200
check "/assets/images/games/top-gear-2.webp" 200
check "/assets/images/games/captain-america-and-the-avengers-loop.webp" 200
check "/assets/images/games/super-mario-world-loop.webp" 200
check "/assets/images/games/tmnt-4-turtles-in-time-loop.webp" 200
check "/assets/images/games/top-gear-2-loop.webp" 200
check "/assets/icons/youtube.svg" 200
check "/assets/icons/instagram.svg" 200
check "/assets/icons/tiktok.svg" 200

echo
echo "== EmulatorJS local =="
check "/data/loader.js" 200
check "/data/emulator.min.js" 200
check "/data/emulator.min.css" 200
check "/data/version.json" 200
check "/data/localization/pt-BR.json" 200
check "/data/cores/snes9x-wasm.data" 200
check "/data/cores/snes9x-thread-wasm.data" 200
check "/data/cores/snes9x-legacy-wasm.data" 200
check "/data/cores/snes9x-thread-legacy-wasm.data" 200
check "/data/compression/libunrar.wasm" 200

echo
echo "== ROMs (capitalização exata) =="
check "/roms/captain-america-and-the-avengers.sfc" 200
check "/roms/super-mario-world.sfc" 200
check "/roms/tmnt-4-turtles-in-time.sfc" 200
check "/roms/TopGear2.sfc" 200

echo
echo "== Sensibilidade a maiúsculas/minúsculas =="
# Deve dar 404: comprova que o nome errado não funciona em produção.
check "/roms/topgear2.sfc" 404
check "/roms/top-gear-2.sfc" 404

echo
echo "== Metadados =="
check "/robots.txt" 200
check "/sitemap.xml" 200
check "/.nojekyll" 200

echo
echo "=================================================="
if [[ "$failures" -gt 0 ]]; then
  echo "RESULTADO: $failures falha(s) HTTP."
  exit 1
fi
echo "RESULTADO: todos os recursos responderam como esperado."
exit 0
