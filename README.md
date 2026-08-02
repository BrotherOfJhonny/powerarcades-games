# PowerArcades Games

Portal de jogos retrô da marca **PowerArcades** (`@powerarcades`), publicado
como site estático no GitHub Pages. A emulação roda inteiramente no navegador,
com o **EmulatorJS hospedado dentro do próprio repositório** — sem CDN, sem
anúncios, sem rastreadores e sem qualquer requisição para fora do domínio.

- **Portal:** <https://brotherofjhonny.github.io/powerarcades-games/>
- **Repositório:** <https://github.com/BrotherOfJhonny/powerarcades-games>

O site principal <https://brotherofjhonny.github.io/> é um projeto separado e
**não é alterado** por este repositório.

---

## Catálogo

| Jogo | Plataforma | Gênero | URL |
| --- | --- | --- | --- |
| Captain America and the Avengers | Super Nintendo | Ação | [`/games/captain-america-and-the-avengers/`](https://brotherofjhonny.github.io/powerarcades-games/games/captain-america-and-the-avengers/) |
| Super Mario World | Super Nintendo | Plataforma | [`/games/super-mario-world/`](https://brotherofjhonny.github.io/powerarcades-games/games/super-mario-world/) |
| Teenage Mutant Ninja Turtles IV: Turtles in Time | Super Nintendo | Beat 'em up | [`/games/tmnt-4-turtles-in-time/`](https://brotherofjhonny.github.io/powerarcades-games/games/tmnt-4-turtles-in-time/) |
| Top Gear 2 | Super Nintendo | Corrida | [`/games/top-gear-2/`](https://brotherofjhonny.github.io/powerarcades-games/games/top-gear-2/) |

---

## Estrutura

```text
.
├── index.html                 catálogo
├── 404.html                   página de erro (caminhos absolutos)
├── .nojekyll                  desliga o processamento Jekyll
├── robots.txt / sitemap.xml   metadados de indexação
├── assets/
│   ├── css/                   main.css (catálogo) e game.css (jogo)
│   ├── js/                    catalog.js, ui.js, game-loader.js
│   ├── images/                identidade visual + capas dos jogos
│   └── icons/                 ícones sociais em SVG
├── data/                      EmulatorJS (veja a seção abaixo)
├── games/<slug>/index.html    uma página por jogo
├── roms/                      ROMs + checksums.sha256
└── scripts/                   validação de ROMs, segredos, HTTP e links
```

---

## EmulatorJS incorporado

| Item | Valor |
| --- | --- |
| Projeto | [EmulatorJS](https://github.com/EmulatorJS/EmulatorJS) |
| Versão / release | **4.2.3** (tag `v4.2.3`, publicada em 2025-07-05) |
| Fonte oficial | `https://github.com/EmulatorJS/EmulatorJS/releases/download/v4.2.3/4.2.3.7z` |
| SHA-256 do pacote | `07d451bc06fa3ad04ab30d9b94eb63ac34ad0babee52d60357b002bde8f3850b` |
| Licença | GPL-3.0 (texto completo em `data/LICENSE-EMULATORJS`) |
| Data de obtenção | 2026-08-01 |

Somente o subconjunto necessário para Super Nintendo foi incorporado
(~5,6 MB no total, em vez dos ~300 MB do pacote completo):

```text
data/loader.js                          data/emulator.min.js
data/emulator.min.css                   data/version.json
data/localization/{pt-BR,en-US,retroarch}.json
data/compression/{extract7z.js,extractzip.js,libunrar.js,libunrar.wasm}
data/cores/snes9x-wasm.data             data/cores/snes9x-thread-wasm.data
data/cores/snes9x-legacy-wasm.data      data/cores/snes9x-thread-legacy-wasm.data
data/cores/reports/snes9x.json
```

As quatro variantes do núcleo `snes9x` são mantidas de propósito: o EmulatorJS
escolhe entre elas conforme o suporte do navegador a WebGL2 e a threads.

### Modificações aplicadas ao `data/emulator.min.js`

A GPL-3.0 exige que alterações sejam declaradas. Três trechos foram
neutralizados para garantir que **nenhuma requisição saia do domínio**:

| # | Original | Passou a ser | Motivo |
| --- | --- | --- | --- |
| 1 | `fetch("https://cdn.emulatorjs.org/stable/data/version.json")` | `Promise.resolve({ok:!1})` | Verificação de versão disparava requisição externa **em todo carregamento**. |
| 2 | `` `https://cdn.emulatorjs.org/${t}/data/${o}` `` | `` `./__core_indisponivel__/${t}/${o}` `` | Failsafe que baixaria o núcleo do CDN caso o arquivo local faltasse. Agora falha na própria origem, com mensagem de erro normal. |
| 3 | `this.config.netplayUrl \|\| "https://netplay.emulatorjs.org"` | `this.config.netplayUrl \|\| ""` | Removia o servidor de netplay de terceiros como padrão. |

As URLs que permanecem no arquivo estão apenas em textos de licença,
mensagens de console e namespaces XML (`xmlns`) — nenhuma delas gera tráfego.
O botão de netplay também é desativado em `assets/js/game-loader.js`
(`EJS_Buttons = { netplay: false }`).

---

## ROMs

As ROMs foram fornecidas pelo proprietário do projeto e já estavam em `roms/`.
**Nenhuma ROM foi baixada, pesquisada, substituída, renomeada ou enviada para
qualquer serviço externo.** Os hashes ficam em `roms/checksums.sha256` e são
gerados com caminhos relativos.

> ⚠️ A capitalização de `TopGear2.sfc` é significativa. O GitHub Pages
> diferencia maiúsculas de minúsculas, então `topgear2.sfc` e `top-gear-2.sfc`
> **não** funcionam. O script `test-site.sh` verifica isso explicitamente,
> exigindo `404` para as grafias erradas.

Verificação manual:

```bash
cd roms && sha256sum -c checksums.sha256
```

---

## Instalação e uso local

Requisitos: `python3`, `bash`, `curl`, `file`, `sha256sum`.

```bash
cd /home/kali/Desktop/powerarcades-games

# validações
./scripts/validate-roms.sh
./scripts/security-check.sh
./scripts/validate-links.sh

# teste HTTP completo (sobe e derruba o servidor sozinho)
./scripts/test-site.sh
```

Para navegar manualmente, sirva o projeto **sob o mesmo prefixo de URL usado em
produção**, senão `404.html` e seus caminhos absolutos não podem ser testados:

```bash
mkdir -p /tmp/pa-serve
ln -sfn /home/kali/Desktop/powerarcades-games /tmp/pa-serve/powerarcades-games
python3 -m http.server 8080 --directory /tmp/pa-serve
```

Depois acesse <http://localhost:8080/powerarcades-games/>.

> Abrir os arquivos com `file://` **não funciona**: o emulador precisa de HTTP
> para carregar o núcleo WebAssembly. A página detecta esse caso e exibe a
> instrução correta.

---

## Como jogar

O emulador, o núcleo SNES e a ROM **só começam a ser baixados após o clique em
"Iniciar jogo"**. A página inicial não carrega nada disso.

| Ação | Tecla |
| --- | --- |
| Direcional | ↑ ↓ ← → |
| A / B | `X` / `Z` |
| X / Y | `S` / `A` |
| L / R | `Q` / `W` |
| Start / Select | `Enter` / `Shift` |

Controles compatíveis com a Gamepad API são reconhecidos ao pressionar
qualquer botão. O mapeamento pode ser alterado no menu do próprio emulador.

---

## Publicação

Publicação por **Deploy from a branch**:

```text
Settings → Pages → Build and deployment
  Source: Deploy from a branch
  Branch: main
  Folder: /(root)
```

O arquivo `.nojekyll` evita o processamento por Jekyll.

---

## Segurança

Resumo — detalhes em [`SECURITY.md`](SECURITY.md):

- CSP restritiva em todas as páginas. `'unsafe-eval'` aparece **somente nas
  páginas de jogo** e apenas porque foi comprovado em navegador real que o
  núcleo Emscripten não roda sem ele (detalhes e evidência em `SECURITY.md`).
- A página inicial usa política mais fechada: sem `blob:`, sem `'unsafe-eval'`
  e sem `'unsafe-inline'` em `script-src`. O `404.html` usa `script-src 'none'`.
- Nenhum `<script>` inline: a configuração de cada jogo vem de atributos
  `data-*` fixos no HTML.
- O caminho da ROM nunca vem de parâmetro de URL, hash ou entrada do usuário.
- Sem `eval`, `new Function`, `document.write` ou `innerHTML` no código próprio.
- Sem Google Analytics, Tag Manager, Meta Pixel, fontes externas ou telemetria.

---

## Licença

Este repositório é distribuído sob **GPL-3.0** (arquivo [`LICENSE`](LICENSE)),
por compatibilidade com o EmulatorJS, que é GPL-3.0 e é redistribuído aqui.

A licença cobre o código do portal. **Não cobre as ROMs nem as marcas,
personagens e obras nelas contidas**, que pertencem aos respectivos
proprietários.

---

## Aviso

Este projeto utiliza tecnologia de emulação executada no navegador. Jogos,
marcas e personagens pertencem aos respectivos proprietários.

**Logotipo:** o logo PowerArcades é da marca, fornecido pelo proprietário
(`assets/images/_logo-origem.png`). O `scripts/prepare-logo.py` recorta o fundo
cinza por saturação + morfologia e deriva a versão transparente, o favicon e a
imagem de compartilhamento. Cor da marca: `#F1BE1D`.

**Capas dos jogos:** arte **original gerada proceduralmente** por
`scripts/generate-artwork.py` — motivos geométricos abstratos por gênero. Não
há box art, sprite ou captura de tela de terceiros no repositório, e nada disso
foi baixado de sites de ROM.

**Gabinetes de fliperama:** o catálogo apresenta cada jogo como uma máquina de
arcade, com marquise, tela, painel de controle e fenda de ficha. Tudo é
**desenhado em CSS** (`.cabinet` em `assets/css/main.css`) — nenhuma fotografia
de fliperama de terceiros é usada. A arte do jogo aparece na tela do gabinete.

As páginas dos jogos são geradas por `scripts/generate-game-pages.py`.
