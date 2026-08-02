#!/usr/bin/env bash
#
# PowerArcades Games — verificação de segredos e de recursos externos.
#
# Não envia nada para fora da máquina. Qualquer valor suspeito é mascarado
# no relatório: o segredo em si nunca é impresso.
#
set -uo pipefail

EXPECTED_ROOT="/home/kali/Desktop/powerarcades-games"
CURRENT_ROOT="$(pwd -P)"

if [[ "$CURRENT_ROOT" != "$EXPECTED_ROOT" ]]; then
  echo "Erro: execute em $EXPECTED_ROOT"
  exit 1
fi

findings=0

# Diretórios/arquivos que não fazem sentido varrer por segredos:
#  - .git       histórico interno
#  - roms       binários de ROM
#  - data       EmulatorJS de terceiros (auditado à parte, abaixo)
#  - assets/images  binários de imagem
PRUNE=( -path './.git' -o -path './roms' -o -path './data' -o -path './assets/images' )

scan_files() {
  find . \( "${PRUNE[@]}" \) -prune -o -type f -print
}

echo "== 1. Padrões de credenciais =="

# Padrões de alta confiança: prefixos de token reais.
HIGH_PATTERNS=(                                  # pragma: allowlist-pattern
  'ghp_[A-Za-z0-9]{16,}'                         # pragma: allowlist-pattern
  'github_pat_[A-Za-z0-9_]{20,}'                 # pragma: allowlist-pattern
  'gho_[A-Za-z0-9]{16,}'                         # pragma: allowlist-pattern
  'ghu_[A-Za-z0-9]{16,}'                         # pragma: allowlist-pattern
  'ghs_[A-Za-z0-9]{16,}'                         # pragma: allowlist-pattern
  'AKIA[0-9A-Z]{16}'                             # pragma: allowlist-pattern
  'ASIA[0-9A-Z]{16}'                             # pragma: allowlist-pattern
  'AIza[0-9A-Za-z_-]{35}'                        # pragma: allowlist-pattern
  '-----BEGIN [A-Z ]*PRIVATE KEY-----'           # pragma: allowlist-pattern
)

# Padrões contextuais: só contam se houver um valor não trivial atribuído.
CONTEXT_PATTERNS=(                               # pragma: allowlist-pattern
  'password=[^[:space:]"'"'"']{6,}'              # pragma: allowlist-pattern
  'passwd=[^[:space:]"'"'"']{6,}'                # pragma: allowlist-pattern
  'token=[^[:space:]"'"'"']{8,}'                 # pragma: allowlist-pattern
  'secret=[^[:space:]"'"'"']{8,}'                # pragma: allowlist-pattern
  'api_key=[^[:space:]"'"'"']{8,}'               # pragma: allowlist-pattern
  'client_secret=[^[:space:]"'"'"']{8,}'         # pragma: allowlist-pattern
  'access_key=[^[:space:]"'"'"']{8,}'            # pragma: allowlist-pattern
  'Authorization:[[:space:]]*(Bearer|Basic)[[:space:]]+[A-Za-z0-9._-]{8,}'  # pragma: allowlist-pattern
)

report_hit() {
  # $1 arquivo, $2 linha, $3 padrão — o valor casado NUNCA é impresso.
  echo "  ALERTA  $1:$2  padrão: $3  valor: ****REDACTED****"
  findings=$((findings + 1))
}

# Marcador de supressão para linhas que contêm o padrão por definição
# (as próprias listas de regex deste script). Toda supressão fica visível
# no código e é auditável.
ALLOW_MARKER='pragma: allowlist-pattern'

scan_pattern_set() {
  local label="$1"; shift
  local -a patterns=( "$@" )
  local file pat line content

  while IFS= read -r file; do
    # Ignora binários.
    if ! grep -Iq . "$file" 2>/dev/null; then continue; fi
    for pat in "${patterns[@]}"; do
      while IFS=: read -r line content; do
        [[ -z "$line" ]] && continue
        # Linha explicitamente marcada como definição de padrão.
        [[ "$content" == *"$ALLOW_MARKER"* ]] && continue
        report_hit "${file#./}" "$line" "$label"
      done < <(grep -nE "$pat" "$file" 2>/dev/null)
    done
  done < <(scan_files)
}

scan_pattern_set "credencial-forte" "${HIGH_PATTERNS[@]}"
scan_pattern_set "credencial-contextual" "${CONTEXT_PATTERNS[@]}"

if [[ "$findings" -eq 0 ]]; then
  echo "  Nenhum padrão de credencial encontrado."
fi

echo
echo "== 2. Arquivos sensíveis =="

SENSITIVE_GLOBS=(
  '.env' '.env.local' '.env.production'
  'credentials.json' 'secrets.json'
  'token.txt' 'github-token.txt' 'passwords.txt'
  'id_rsa' 'id_ed25519'
  '*.pem' '*.key' '*.p12' '*.pfx'
)

sensitive_found=0
for glob in "${SENSITIVE_GLOBS[@]}"; do
  while IFS= read -r hit; do
    echo "  ALERTA  arquivo sensível: ${hit#./}"
    sensitive_found=$((sensitive_found + 1))
    findings=$((findings + 1))
  done < <(find . -path ./.git -prune -o -type f -name "$glob" -print 2>/dev/null)
done

if [[ "$sensitive_found" -eq 0 ]]; then
  echo "  Nenhum arquivo sensível encontrado."
fi

echo
echo "== 3. Remote git com credencial embutida =="

if git rev-parse --git-dir >/dev/null 2>&1; then
  remote_issue=0
  while IFS= read -r url; do
    [[ -z "$url" ]] && continue
    # Detecta userinfo (algo@) antes do host em URL http(s).
    if [[ "$url" =~ ^https?://[^/@]+@ ]]; then
      echo "  ALERTA  Possível credencial incorporada na URL do remote."
      echo "          Ações recomendadas:"
      echo "            1. git remote set-url origin <URL limpa>"
      echo "            2. revogar o token exposto"
      echo "            3. revisar o histórico do repositório"
      echo "            4. revisar o GitHub Security Log"
      remote_issue=1
      findings=$((findings + 1))
    fi
  done < <(git remote 2>/dev/null | while read -r r; do git remote get-url "$r" 2>/dev/null; done)

  if [[ "$remote_issue" -eq 0 ]]; then
    echo "  Nenhum remote com credencial embutida."
  fi
else
  echo "  (ainda não é um repositório git)"
fi

echo
echo "== 4. Recursos externos nas páginas =="

ext_found=0
while IFS= read -r file; do
  while IFS=: read -r line content; do
    # Ignora links de navegação (<a href>) e metadados absolutos
    # (canonical, og:url, og:image, sitemap), que são esperados.
    case "$content" in
      *"<a "*|*rel=\"canonical\"*|*og:url*|*og:image*|*twitter:image*|*xmlns*|*"<loc>"*|*Sitemap:*) continue ;;
    esac
    echo "  ALERTA  recurso externo em ${file#./}:$line"
    ext_found=$((ext_found + 1))
    findings=$((findings + 1))
  done < <(grep -nE '(src|href)="https?://' "$file" 2>/dev/null)
done < <(find . -path ./.git -prune -o -path ./data -prune -o -type f \( -name '*.html' -o -name '*.xml' \) -print)

if [[ "$ext_found" -eq 0 ]]; then
  echo "  Nenhum script/estilo/imagem carregado de domínio externo."
fi

echo
echo "== 5. Padrões perigosos no JavaScript próprio =="

danger_found=0
while IFS= read -r file; do
  while IFS=: read -r line content; do
    echo "  ALERTA  padrão perigoso em ${file#./}:$line -> $(echo "$content" | tr -s ' ' | cut -c1-80)"
    danger_found=$((danger_found + 1))
    findings=$((findings + 1))
  done < <(grep -nE '\beval\(|new Function\(|document\.write\(|\.innerHTML[[:space:]]*=|URLSearchParams' "$file" 2>/dev/null)
done < <(find ./assets/js -type f -name '*.js' 2>/dev/null)

if [[ "$danger_found" -eq 0 ]]; then
  echo "  Nenhum eval/new Function/document.write/innerHTML/URLSearchParams."
fi

echo
echo "== 6. gitleaks (se disponível) =="
if command -v gitleaks >/dev/null 2>&1; then
  if gitleaks detect --source . --no-banner; then
    echo "  gitleaks: nenhum segredo encontrado."
  else
    echo "  ALERTA  gitleaks reportou possíveis segredos."
    findings=$((findings + 1))
  fi
else
  echo "  gitleaks não instalado — verificação local acima foi utilizada."
fi

echo
echo "=================================================="
if [[ "$findings" -gt 0 ]]; then
  echo "RESULTADO: $findings ocorrência(s). NÃO faça commit nem push."
  echo "Revise, remova o segredo, revogue-o e execute novamente."
  exit 1
fi

echo "RESULTADO: nenhuma ocorrência. Seguro para commit."
exit 0
