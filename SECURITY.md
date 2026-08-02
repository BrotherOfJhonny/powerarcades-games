# Política de segurança — PowerArcades Games

Este é um site **estático**, sem backend, sem banco de dados, sem autenticação
e sem coleta de dados. A superfície de ataque é o conteúdo servido pelo GitHub
Pages e o emulador WebAssembly que roda no navegador do visitante.

---

## 1. Modelo de ameaça

| Ameaça | Mitigação |
| --- | --- |
| Execução de script de terceiros | Nenhum recurso externo é carregado. CSP com `default-src 'self'`. |
| XSS via conteúdo dinâmico | O catálogo é renderizado só com `createElement` + `textContent`. Nunca `innerHTML`. |
| Path traversal / troca de ROM | O caminho da ROM é literal fixo no HTML. Nenhum parâmetro de URL é lido. |
| Exfiltração de dados | `connect-src 'self' blob:`. Telemetria do EmulatorJS foi removida. |
| Clickjacking | **Não mitigado** — `frame-ancestors` só vale como cabeçalho HTTP, indisponível no GitHub Pages. Ver seção 2. |
| Vazamento por Referer | `<meta name="referrer" content="no-referrer">` e `rel="noopener noreferrer"`. |
| Vazamento de credenciais no repositório | `scripts/security-check.sh` roda antes de todo commit. |

---

## 2. Content Security Policy

### Páginas de jogo (`games/<slug>/index.html`)

```text
default-src 'self';
script-src 'self' blob: 'wasm-unsafe-eval' 'unsafe-eval';
style-src 'self' 'unsafe-inline';
img-src 'self' data: blob:;
font-src 'self';
media-src 'self' blob: data:;
connect-src 'self' blob:;
worker-src 'self' blob:;
child-src 'self' blob:;
object-src 'none';
frame-src 'none';
base-uri 'self';
form-action 'self';
manifest-src 'self';
upgrade-insecure-requests
```

### Sobre `'unsafe-eval'`

A necessidade foi **testada em navegador real**, não presumida. A primeira
versão desta política omitia `'unsafe-eval'`. O Chromium recusou o núcleo:

```text
Uncaught EvalError: Refused to evaluate a string as JavaScript because
'unsafe-eval' is not an allowed source of script in the following Content
Security Policy directive: "script-src 'self' blob: 'wasm-unsafe-eval'"
```

Com isso o canvas nunca era criado e nenhum jogo iniciava. O núcleo `snes9x`
compilado com Emscripten avalia código em tempo de execução, então
`'unsafe-eval'` é **obrigatório** e foi mantido — apenas nas páginas de jogo.
A política não foi afrouxada para esconder erro: foi ajustada ao requisito
técnico comprovado, e nada além disso foi liberado.

`'wasm-unsafe-eval'` e `blob:` também são necessários: WebAssembly e o script
do núcleo instanciado a partir de uma Blob URL.

### O que NÃO está na política

- **`'unsafe-inline'` em `script-src`** — nenhuma página tem `<script>` inline
  nem handler `on*=`. A configuração de cada jogo vem de atributos `data-*` do
  elemento `#stage`. `'unsafe-inline'` aparece só em `style-src`, porque o
  EmulatorJS estiliza seus próprios elementos de interface inline.
- **`frame-ancestors`** — foi removida porque é **ignorada quando entregue via
  `<meta>`**; o navegador emitia erro de console a cada carregamento. Ela só
  funciona como cabeçalho HTTP, e o GitHub Pages não permite configurar
  cabeçalhos. **Limitação assumida:** não há proteção contra clickjacking por
  CSP neste host. Se isso passar a importar, será preciso um host que permita
  cabeçalhos (Cloudflare Pages, Netlify) ou um proxy à frente.

### Página inicial e 404

Política mais fechada, já que não há emulação:

```text
script-src 'self'          (index.html)
script-src 'none'          (404.html)
```

sem `blob:`, sem `wasm-unsafe-eval`, `worker-src 'none'`.

---

## 2.1 Cabeçalhos HTTP — limitação do GitHub Pages

O GitHub Pages **não permite definir cabeçalhos de resposta**. Só envia
`Strict-Transport-Security`. Isso tem consequências reais e verificadas:

| Proteção | Situação | Observação |
| --- | --- | --- |
| CSP | ✅ ativa | via `<meta>`; testada em navegador com **0 violações** |
| Referrer-Policy | ✅ ativa | `<meta name="referrer">` **é** honrado pelo navegador |
| HSTS | ✅ ativa | enviada pelo GitHub |
| `X-Frame-Options` | ❌ ausente | header-only |
| `frame-ancestors` | ❌ ausente | ignorada em `<meta>` |
| `X-Content-Type-Options` | ❌ ausente | header-only |
| `Permissions-Policy` | ❌ ausente | header-only |
| COOP / COEP / CORP | ❌ ausentes | header-only |

Ferramentas como o **securityheaders.com** leem apenas cabeçalhos HTTP, então
reportam CSP e Referrer-Policy como ausentes mesmo estando ativas. A nota
subestima a postura real — mas as cinco últimas linhas da tabela são falhas
genuínas.

### Prova de que `X-Frame-Options` não funciona via `<meta>`

Teste feito em Chromium, servindo a mesma página de três formas:

| Entrega | Enquadrou? |
| --- | --- |
| `<meta http-equiv="X-Frame-Options" content="DENY">` | **sim** — ignorado |
| Cabeçalho HTTP `X-Frame-Options: DENY` | **não** — bloqueado |
| Sem proteção | sim |

O próprio navegador emite:
`X-Frame-Options may only be set via an HTTP header sent along with a
document. It may not be set inside <meta>.`

### Clickjacking: risco aceito e mitigado parcialmente

O site **pode ser enquadrado** por terceiros (confirmado por exploração).
Como não há login, formulário nem ação que altere estado, não existe clique
a ser sequestrado — o risco concreto é **uso indevido da marca**, com o
portal embutido em página de terceiros.

Mitigação atual: `assets/js/frame-guard.js`, que tenta escapar do quadro e,
se bloqueado por `sandbox`, oculta o conteúdo e oferece link para a origem
oficial. É **paliativo**, não solução.

Solução definitiva: servir o site por um host que envie cabeçalhos. O arquivo
[`_headers`](_headers) na raiz já traz o conjunto completo pronto para
Cloudflare Pages, Netlify ou Cloudflare Transform Rules à frente do Pages.

> Bônus de desempenho: `COOP` + `COEP` habilitam `SharedArrayBuffer`, o que
> permite ao EmulatorJS usar `data/cores/snes9x-thread-wasm.data` (já incluído)
> em vez do núcleo sem threads.

## 2.2 CORS aberto em todo o conteúdo

O GitHub Pages responde `access-control-allow-origin: *` em **todos** os
arquivos, incluindo `roms/*.sfc`. Qualquer site pode lê-los por `fetch`.
Não é configurável no Pages; o `_headers` corrige com
`Cross-Origin-Resource-Policy: same-origin` no host novo.

---

## 3. Alterações no EmulatorJS

O EmulatorJS 4.2.3 é redistribuído aqui sob GPL-3.0. Três pontos que geravam
tráfego externo foram neutralizados em `data/emulator.min.js`:

1. **Verificação de versão** — `fetch` para `cdn.emulatorjs.org` a cada
   carregamento de página, substituído por `Promise.resolve({ok:!1})`.
2. **Failsafe de download do núcleo pelo CDN** — reapontado para um caminho da
   própria origem, que falha com a mensagem de erro normal do emulador.
3. **Servidor de netplay padrão** — o padrão de terceiros virou string vazia,
   e o botão de netplay é desativado via `EJS_Buttons`.

O detalhamento com valores antes/depois está no `README.md`.

---

## 4. Tratamento das ROMs

- As ROMs foram fornecidas pelo proprietário e **nunca** saem da máquina/do
  domínio: nada é enviado a serviços de análise, hash público ou upload.
- `scripts/validate-roms.sh` confirma existência, tamanho, extensão e o tipo
  real do arquivo (`file`), rejeitando HTML, XML, texto e executáveis
  disfarçados de ROM.
- `roms/checksums.sha256` registra os hashes com caminhos relativos.
- `roms/` e `data/` são desindexados via `robots.txt`.

---

## 5. Verificação antes de publicar

```bash
./scripts/validate-roms.sh     # integridade das ROMs
./scripts/security-check.sh    # segredos, recursos externos, padrões perigosos
./scripts/validate-links.sh    # links quebrados e domínios inesperados
./scripts/test-site.sh         # códigos HTTP de todos os recursos
```

`security-check.sh` **interrompe o processo com código de saída 1** ao
encontrar qualquer ocorrência, e nunca imprime o valor do segredo — apenas o
arquivo, a linha e `****REDACTED****`.

### Se um segredo for encontrado

1. **Não** faça commit nem push.
2. Remova o valor do arquivo.
3. **Revogue o segredo** no provedor — considere-o comprometido.
4. Se já houver sido commitado, trate o histórico como contaminado e revise o
   GitHub Security Log.
5. Rode `./scripts/security-check.sh` de novo até sair limpo.

---

## 6. Credenciais

Este projeto **nunca** guarda credenciais. Não há token em `.env`, em script,
em workflow, no README ou na URL do remote.

Autenticação com o GitHub deve usar `gh auth login`, SSH agent ou Git
Credential Manager. Remotes no formato `https://TOKEN@github.com/...` são
proibidos — `security-check.sh` detecta e alerta sem imprimir a URL completa.

---

## 7. Privacidade do visitante

Não há cookies de rastreamento, analytics, pixels, fingerprinting ou
telemetria. O EmulatorJS usa `localStorage` e IndexedDB **apenas no navegador
do próprio usuário**, para cache do núcleo, saves e configurações de controle.
Nada disso é transmitido.

---

## 8. Reportar uma vulnerabilidade

Abra uma issue em
<https://github.com/BrotherOfJhonny/powerarcades-games/issues>.

Para algo sensível, evite detalhes públicos na issue: peça um canal privado
primeiro. Não inclua ROMs, dados pessoais ou credenciais no relato.
