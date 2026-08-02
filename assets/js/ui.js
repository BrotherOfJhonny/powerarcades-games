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

  function buildCard(game) {
    var item = el("li");

    var card = el("article", "game-card");
    card.setAttribute("aria-labelledby", "title-" + game.slug);

    /* --- capa ------------------------------------------------------- */
    var media = el("div", "game-card-media");
    var img = document.createElement("img");
    img.src = game.cover;
    img.alt = "Arte de capa do jogo " + game.title;
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

    media.appendChild(img);
    card.appendChild(media);

    /* --- corpo ------------------------------------------------------ */
    var body = el("div", "game-card-body");

    var title = el("h3", "game-card-title", game.title);
    title.id = "title-" + game.slug;
    body.appendChild(title);

    var meta = el("ul", "game-meta");
    meta.appendChild(el("li", "tag tag-platform", game.platform));
    meta.appendChild(el("li", "tag", game.genre));
    if (game.players) meta.appendChild(el("li", "tag", game.players));
    if (game.year) meta.appendChild(el("li", "tag", game.year));
    body.appendChild(meta);

    /* --- ação ------------------------------------------------------- */
    var link = el("a", "btn btn-primary", "Jogar agora");
    link.href = game.url;
    link.setAttribute("aria-label", "Jogar agora: " + game.title);
    body.appendChild(link);

    card.appendChild(body);
    item.appendChild(card);
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
