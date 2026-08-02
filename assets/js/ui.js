/* ==========================================================================
   PowerArcades Games — renderização do catálogo
   --------------------------------------------------------------------------
   Constrói os cards via API do DOM (createElement + textContent).
   Nunca usa innerHTML, eval, new Function ou document.write.
   Esta página NÃO baixa ROMs nem carrega o EmulatorJS.
   ========================================================================== */

(function () {
  "use strict";

  var FALLBACK_COVER = "assets/images/default-game-cover.webp";

  function el(tag, className, text) {
    var node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined && text !== null) node.textContent = text;
    return node;
  }

  /**
   * Monta um gabinete de fliperama para o jogo.
   * A "tela" do gabinete exibe a arte do jogo, para o visitante escolher
   * qual máquina quer jogar. Tudo é desenhado em CSS — nenhuma foto de
   * fliperama de terceiros é usada.
   */
  function buildCard(game) {
    var item = el("li");

    var cab = el("article", "cabinet");
    cab.setAttribute("data-slug", game.slug);
    cab.setAttribute("aria-labelledby", "title-" + game.slug);

    /* --- marquise (letreiro superior) -------------------------------- */
    var marquee = el("div", "cab-marquee");
    var title = el("h3", "cab-marquee-title", game.title);
    title.id = "title-" + game.slug;
    marquee.appendChild(title);
    cab.appendChild(marquee);

    /* --- tela -------------------------------------------------------- */
    var screen = el("div", "cab-screen");
    var screenInner = el("div", "cab-screen-inner");

    var img = document.createElement("img");
    img.src = game.cover;
    img.alt = "Tela do fliperama exibindo " + game.title;
    img.width = 640;
    img.height = 480;
    img.loading = "lazy";
    img.decoding = "async";

    // Fallback de imagem sem handler inline.
    img.addEventListener("error", function onCoverError() {
      img.removeEventListener("error", onCoverError);
      if (img.getAttribute("src") !== FALLBACK_COVER) {
        img.src = FALLBACK_COVER;
      }
    });

    screenInner.appendChild(img);
    screen.appendChild(screenInner);
    cab.appendChild(screen);

    /* --- painel de controle (decorativo) ----------------------------- */
    var panel = el("div", "cab-panel");
    panel.setAttribute("aria-hidden", "true");

    panel.appendChild(el("div", "cab-stick"));

    var buttons = el("div", "cab-buttons");
    for (var i = 0; i < 4; i++) {
      buttons.appendChild(el("i"));
    }
    panel.appendChild(buttons);

    panel.appendChild(el("div", "cab-coin"));
    cab.appendChild(panel);

    /* --- corpo do gabinete ------------------------------------------- */
    var body = el("div", "cab-body");

    var meta = el("ul", "game-meta");
    meta.appendChild(el("li", "tag tag-platform", game.platform));
    meta.appendChild(el("li", "tag", game.genre));
    if (game.players) meta.appendChild(el("li", "tag", game.players));
    if (game.year) meta.appendChild(el("li", "tag", game.year));
    body.appendChild(meta);

    var link = el("a", "btn btn-primary", "Jogar agora");
    link.href = game.url;
    link.setAttribute("aria-label", "Jogar agora: " + game.title);
    body.appendChild(link);

    cab.appendChild(body);
    item.appendChild(cab);
    return item;
  }

  function render() {
    var mount = document.getElementById("catalog");
    if (!mount) return;

    var catalog = window.PA_CATALOG;
    if (!catalog || !catalog.games || !catalog.games.length) {
      var warn = el(
        "p",
        "stage-error",
        "Não foi possível carregar o catálogo. Recarregue a página."
      );
      mount.parentNode.insertBefore(warn, mount);
      return;
    }

    var frag = document.createDocumentFragment();
    catalog.games.forEach(function (game) {
      frag.appendChild(buildCard(game));
    });

    mount.textContent = "";
    mount.appendChild(frag);

    var count = document.getElementById("catalog-count");
    if (count) {
      count.textContent =
        catalog.games.length +
        (catalog.games.length === 1 ? " jogo disponível" : " jogos disponíveis");
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", render);
  } else {
    render();
  }
})();
