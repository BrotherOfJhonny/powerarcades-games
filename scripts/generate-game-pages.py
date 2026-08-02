#!/usr/bin/env python3
"""Gera as paginas individuais dos jogos do PowerArcades Games."""
import html
import os

ROOT = "/home/kali/Desktop/powerarcades-games"
BASE = "https://brotherofjhonny.github.io/powerarcades-games"

# Politica das paginas de jogo.
#
# 'unsafe-eval' foi TESTADO em navegador real e e' obrigatorio: o nucleo
# snes9x compilado com Emscripten avalia codigo em tempo de execucao. Sem
# ele o Chromium aborta com:
#   "Uncaught EvalError: Refused to evaluate a string as JavaScript"
# e o canvas do jogo nunca chega a ser criado. Mantido apenas nas paginas
# de jogo -- a home e o 404 continuam sem ele.
#
# 'frame-ancestors' NAO entra aqui: e' ignorado quando entregue via <meta>
# (o proprio navegador emite erro). So funciona como cabecalho HTTP, o que
# o GitHub Pages nao permite configurar.
#
# 'wasm-unsafe-eval' e blob: seguem necessarios: WebAssembly + o script do
# nucleo instanciado a partir de Blob URL.
CSP = (
    "default-src 'self'; "
    "script-src 'self' blob: 'wasm-unsafe-eval' 'unsafe-eval'; "
    "style-src 'self' 'unsafe-inline'; "
    "img-src 'self' data: blob:; "
    "font-src 'self'; "
    "media-src 'self' blob: data:; "
    "connect-src 'self' blob:; "
    "worker-src 'self' blob:; "
    "child-src 'self' blob:; "
    "object-src 'none'; "
    "frame-src 'none'; "
    "base-uri 'self'; "
    "form-action 'self'; "
    "manifest-src 'self'; "
    "upgrade-insecure-requests"
)

GAMES = [
    {
        "slug": "captain-america-and-the-avengers",
        "title": "Captain America and the Avengers",
        "short": "Captain America and the Avengers",
        "platform": "Super Nintendo",
        "genre": "Ação",
        "players": "1–2 jogadores",
        "year": "1993",
        "rom": "captain-america-and-the-avengers.sfc",
        "cover": "captain-america-and-the-avengers.webp",
        "desc": ("Jogue Captain America and the Avengers, clássico de ação do "
                 "Super Nintendo, direto no navegador pelo PowerArcades Games."),
        "about": ("Beat 'em up de ação lançado para Super Nintendo, com os heróis "
                  "clássicos da Marvel enfrentando o Caveira Vermelha em fases "
                  "de rolagem lateral."),
    },
    {
        "slug": "super-mario-world",
        "title": "Super Mario World",
        "short": "Super Mario World",
        "platform": "Super Nintendo",
        "genre": "Plataforma",
        "players": "1–2 jogadores",
        "year": "1990",
        "rom": "super-mario-world.sfc",
        "cover": "super-mario-world.webp",
        "desc": ("Jogue Super Mario World, clássico de plataforma do Super "
                 "Nintendo, direto no navegador pelo PowerArcades Games."),
        "about": ("Plataforma que definiu uma geração, com o Mundo dos Dinossauros, "
                  "dezenas de saídas secretas e a estreia do Yoshi."),
    },
    {
        "slug": "tmnt-4-turtles-in-time",
        "title": "Teenage Mutant Ninja Turtles IV: Turtles in Time",
        "short": "TMNT IV: Turtles in Time",
        "platform": "Super Nintendo",
        "genre": "Beat 'em up",
        "players": "1–2 jogadores",
        "year": "1992",
        "rom": "tmnt-4-turtles-in-time.sfc",
        "cover": "tmnt-4-turtles-in-time.webp",
        "desc": ("Jogue Teenage Mutant Ninja Turtles IV: Turtles in Time, clássico "
                 "beat 'em up do Super Nintendo, direto no navegador pelo "
                 "PowerArcades Games."),
        "about": ("Beat 'em up cooperativo em que as tartarugas atravessam o tempo, "
                  "referência absoluta do gênero no Super Nintendo."),
    },
    {
        "slug": "top-gear-2",
        "title": "Top Gear 2",
        "short": "Top Gear 2",
        "platform": "Super Nintendo",
        "genre": "Corrida",
        "players": "1–2 jogadores",
        "year": "1993",
        # Capitalizacao preservada exatamente como o arquivo em disco.
        "rom": "TopGear2.sfc",
        "cover": "top-gear-2.webp",
        "desc": ("Jogue Top Gear 2, clássico de corrida do Super Nintendo, direto "
                 "no navegador pelo PowerArcades Games."),
        "about": ("Corrida arcade com circuitos ao redor do mundo, upgrades de "
                  "carro, nitro e uma das trilhas sonoras mais lembradas do "
                  "console."),
    },
]

CONTROLS = [
    ("Direcional", "Setas ↑ ↓ ← →"),
    ("Botão A", "X"),
    ("Botão B", "Z"),
    ("Botão X", "S"),
    ("Botão Y", "A"),
    ("Botão L", "Q"),
    ("Botão R", "W"),
    ("Start", "Enter"),
    ("Select", "Shift"),
]

TEMPLATE = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">

<!-- EmulatorJS local: WebAssembly + scripts de Blob URL. Sem 'unsafe-eval'. -->
<meta http-equiv="Content-Security-Policy" content="{csp}">
<meta name="referrer" content="no-referrer">

<title>{title_esc} — PowerArcades Games</title>
<meta name="description" content="{desc}">
<meta name="author" content="PowerArcades">
<meta name="theme-color" content="#080B12">
<link rel="canonical" href="{base}/games/{slug}/">

<link rel="icon" type="image/png" href="../../assets/images/favicon.png">
<link rel="apple-touch-icon" href="../../assets/images/favicon.png">

<meta property="og:type" content="article">
<meta property="og:site_name" content="PowerArcades Games">
<meta property="og:locale" content="pt_BR">
<meta property="og:title" content="{title_esc} — PowerArcades Games">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{base}/games/{slug}/">
<meta property="og:image" content="{base}/assets/images/games/{cover}">
<meta property="og:image:width" content="640">
<meta property="og:image:height" content="480">
<meta property="og:image:alt" content="Arte de capa de {title_esc}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title_esc} — PowerArcades Games">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{base}/assets/images/games/{cover}">

<meta name="game:platform" content="{platform}">
<meta name="game:genre" content="{genre}">
<meta name="game:players" content="{players}">
<meta name="game:year" content="{year}">

<link rel="stylesheet" href="../../assets/css/main.css">
<link rel="stylesheet" href="../../assets/css/game.css">
</head>

<body>
<a class="skip-link" href="#conteudo">Pular para o conteúdo</a>

<header class="site-header">
  <div class="wrap header-inner">
    <a class="brand" href="../../" aria-label="PowerArcades Games — página inicial">
      <img class="brand-logo" src="../../assets/images/logo-powerarcades.webp" alt="PowerArcades" width="575" height="260">
      <span class="brand-text">
        <span class="brand-name">GAMES</span>
        <span class="brand-handle">@powerarcades</span>
      </span>
    </a>

    <nav class="header-nav" aria-label="Navegação principal">
      <a class="nav-link" href="../../#catalogo">Catálogo</a>
      <span class="social-row">
        <a class="social-link" href="https://www.youtube.com/@powerarcades" target="_blank" rel="noopener noreferrer external" aria-label="YouTube @powerarcades (abre em nova aba)">
          <img src="../../assets/icons/youtube.svg" alt="" width="24" height="24" aria-hidden="true">
        </a>
        <a class="social-link" href="https://www.instagram.com/powerarcades" target="_blank" rel="noopener noreferrer external" aria-label="Instagram @powerarcades (abre em nova aba)">
          <img src="../../assets/icons/instagram.svg" alt="" width="24" height="24" aria-hidden="true">
        </a>
        <a class="social-link" href="https://www.tiktok.com/@powerarcades" target="_blank" rel="noopener noreferrer external" aria-label="TikTok @powerarcades (abre em nova aba)">
          <img src="../../assets/icons/tiktok.svg" alt="" width="24" height="24" aria-hidden="true">
        </a>
      </span>
    </nav>
  </div>
</header>

<main id="conteudo" class="wrap game-page">

  <nav class="breadcrumb" aria-label="Trilha de navegação">
    <ol>
      <li><a href="../../">Início</a></li>
      <li><a href="../../#catalogo">Catálogo</a></li>
      <li aria-current="page">{short_esc}</li>
    </ol>
  </nav>

  <div class="game-head">
    <div>
      <h1>{title_esc}</h1>
      <ul class="game-meta">
        <li class="tag tag-platform">{platform}</li>
        <li class="tag">{genre}</li>
        <li class="tag">{players}</li>
        <li class="tag">{year}</li>
      </ul>
    </div>
  </div>

  <!-- Caminho da ROM FIXO no HTML. Nunca vem de parâmetro de URL. -->
  <div class="stage"
       id="stage"
       data-core="snes"
       data-title="{title_attr}"
       data-rom="../../roms/{rom}">

    <div id="game"></div>

    <div class="stage-overlay" id="stage-overlay">
      <div class="stage-overlay-inner" id="stage-overlay-inner">
        <h2>{short_esc}</h2>
        <p>
          O emulador, o núcleo de Super Nintendo e a ROM só começam a ser
          carregados depois que você clicar no botão abaixo.
        </p>
        <button type="button" class="btn btn-primary" id="start-button">
          Iniciar jogo
        </button>
        <p class="stage-note">
          Cerca de 1&nbsp;MB de núcleo do emulador + a ROM deste jogo.
        </p>
      </div>
    </div>
  </div>

  <div class="game-toolbar">
    <button type="button" class="btn btn-ghost" id="fullscreen-button">
      Tela cheia
    </button>
    <a class="btn btn-ghost" href="../../#catalogo">Voltar ao catálogo</a>
  </div>

  <div class="game-columns">

    <article class="info-card">
      <h3>Sobre o jogo</h3>
      <p>{about}</p>
    </article>

    <article class="info-card">
      <h3>Controles do teclado</h3>
      <table class="controls-table">
        <caption>Mapeamento padrão. Pode ser alterado no menu do emulador.</caption>
        <tbody>
{controls_rows}
        </tbody>
      </table>
    </article>

    <article class="info-card">
      <h3>Instruções</h3>
      <ul>
        <li>Clique em <strong>Iniciar jogo</strong> e aguarde o download do núcleo.</li>
        <li>Quando o emulador terminar de carregar, use o botão de play dele para começar.</li>
        <li>Conecte um controle e pressione qualquer botão para que o navegador o reconheça.</li>
        <li>Use <strong>Tela cheia</strong> e pressione <kbd>Esc</kbd> para sair.</li>
        <li>Se o áudio não tocar, clique uma vez sobre a tela do jogo.</li>
      </ul>
    </article>

    <article class="info-card">
      <h3>Detalhes técnicos</h3>
      <ul>
        <li>Núcleo: <strong>snes9x</strong> (WebAssembly)</li>
        <li>Arquivo: <code id="rom-path">roms/{rom}</code></li>
        <li>Emulador servido pelo próprio site, sem CDN.</li>
        <li>Nenhuma requisição sai deste domínio.</li>
      </ul>
    </article>

  </div>

</main>

<footer class="site-footer">
  <div class="wrap">
    <div class="footer-grid">
      <div>
        <h3>PowerArcades</h3>
        <ul class="footer-links">
          <li><span class="brand-handle">@powerarcades</span></li>
          <li><a href="../../">Página inicial</a></li>
          <li><a href="../../#catalogo">Catálogo</a></li>
        </ul>
      </div>
      <div>
        <h3>Redes sociais</h3>
        <ul class="footer-links">
          <li><a href="https://www.youtube.com/@powerarcades" target="_blank" rel="noopener noreferrer external">YouTube</a></li>
          <li><a href="https://www.instagram.com/powerarcades" target="_blank" rel="noopener noreferrer external">Instagram</a></li>
          <li><a href="https://www.tiktok.com/@powerarcades" target="_blank" rel="noopener noreferrer external">TikTok</a></li>
        </ul>
      </div>
      <div>
        <h3>Projeto</h3>
        <ul class="footer-links">
          <li><a href="https://github.com/BrotherOfJhonny/powerarcades-games" target="_blank" rel="noopener noreferrer external">Código-fonte</a></li>
          <li><a href="https://brotherofjhonny.github.io/" target="_blank" rel="noopener noreferrer external">Site principal</a></li>
        </ul>
      </div>
    </div>

    <p class="disclaimer">
      Este projeto utiliza tecnologia de emulação executada no navegador.
      Jogos, marcas e personagens pertencem aos respectivos proprietários.
      Emulação por <a href="https://github.com/EmulatorJS/EmulatorJS" target="_blank" rel="noopener noreferrer external">EmulatorJS</a> (GPL-3.0), hospedado localmente.
    </p>
  </div>
</footer>

<script src="../../assets/js/frame-guard.js"></script>
<script src="../../assets/js/game-loader.js"></script>
</body>
</html>
"""


def build():
    rows = "\n".join(
        '          <tr><th scope="row">{}</th><td><kbd>{}</kbd></td></tr>'.format(
            html.escape(a), html.escape(b))
        for a, b in CONTROLS
    )

    for g in GAMES:
        out_dir = os.path.join(ROOT, "games", g["slug"])
        os.makedirs(out_dir, exist_ok=True)
        page = TEMPLATE.format(
            # A CSP nao contem &, < ou > nem aspas duplas; escapar as aspas
            # simples so deixaria o atributo ilegivel.
            csp=html.escape(CSP, quote=False),
            base=BASE,
            slug=g["slug"],
            rom=g["rom"],
            cover=g["cover"],
            title_esc=html.escape(g["title"]),
            title_attr=html.escape(g["title"], quote=True),
            short_esc=html.escape(g["short"]),
            desc=html.escape(g["desc"], quote=True),
            platform=html.escape(g["platform"]),
            genre=html.escape(g["genre"]),
            players=html.escape(g["players"]),
            year=g["year"],
            about=html.escape(g["about"]),
            controls_rows=rows,
        )
        path = os.path.join(out_dir, "index.html")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(page)
        print("  pagina", os.path.relpath(path, ROOT))


if __name__ == "__main__":
    print("Gerando paginas de jogo:")
    build()
    print("OK")
