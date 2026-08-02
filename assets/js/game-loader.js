/* ==========================================================================
   PowerArcades Games — inicialização sob demanda do EmulatorJS
   --------------------------------------------------------------------------
   Regras de segurança aplicadas aqui:
     • O caminho da ROM vem SEMPRE dos atributos data-* fixos do elemento
       #stage, escritos literalmente no HTML da própria página do jogo.
       Nunca de location.search, hash, postMessage ou entrada do usuário.
     • Sem <script> inline: a CSP das páginas dispensa 'unsafe-inline'.
     • Nada do EmulatorJS (loader, core, .wasm, ROM) é baixado antes do
       clique em "Iniciar jogo".
     • Sem eval, sem new Function, sem document.write, sem innerHTML.
     • Todos os caminhos são relativos ao próprio site (mesma origem).
   ========================================================================== */

(function () {
  "use strict";

  var started = false;

  function $(id) {
    return document.getElementById(id);
  }

  /* ------------------------------------------------------ configuração --- */

  /**
   * Lê a configuração fixa gravada no HTML da página do jogo.
   * Retorna null se a página não declarar os dados obrigatórios.
   */
  function readGameConfig() {
    var stage = $("stage");
    if (!stage) return null;

    var rom = stage.getAttribute("data-rom");
    var title = stage.getAttribute("data-title");
    var core = stage.getAttribute("data-core");

    if (!rom || !title || !core) return null;

    return Object.freeze({ rom: rom, title: title, core: core });
  }

  /* ------------------------------------------------------------- erros --- */

  function showError(title, detail) {
    var inner = $("stage-overlay-inner");
    if (!inner) return;

    inner.textContent = "";

    var box = document.createElement("div");
    box.className = "stage-error";
    box.setAttribute("role", "alert");

    var strong = document.createElement("strong");
    strong.textContent = title;
    box.appendChild(strong);

    var p = document.createElement("p");
    p.textContent = detail;
    box.appendChild(p);

    if (window.location.protocol === "file:") {
      var hint = document.createElement("p");
      hint.textContent =
        "A página foi aberta com file://. O emulador precisa de um servidor " +
        "HTTP. Rode: python3 -m http.server 8080";
      box.appendChild(hint);
    }

    inner.appendChild(box);

    var retry = document.createElement("button");
    retry.type = "button";
    retry.className = "btn btn-ghost";
    retry.textContent = "Tentar novamente";
    retry.addEventListener("click", function () {
      window.location.reload();
    });
    inner.appendChild(retry);
  }

  /* ---------------------------------------------------------- progresso --- */

  function showLoading(message) {
    var inner = $("stage-overlay-inner");
    if (!inner) return;

    inner.textContent = "";

    var status = document.createElement("div");
    status.className = "stage-status";
    status.setAttribute("role", "status");
    status.setAttribute("aria-live", "polite");

    var spin = document.createElement("span");
    spin.className = "spinner";
    spin.setAttribute("aria-hidden", "true");
    status.appendChild(spin);

    var text = document.createElement("span");
    text.textContent = message;
    status.appendChild(text);

    inner.appendChild(status);
  }

  /* ------------------------------------------------------- configuração --- */

  function configureEmulator(game) {
    // Caminhos fixos, relativos a games/<slug>/
    window.EJS_player = "#game";
    window.EJS_core = game.core;
    window.EJS_gameName = game.title;
    window.EJS_gameUrl = game.rom;
    window.EJS_pathtodata = "../../data/";
    window.EJS_startOnLoaded = false;
    window.EJS_color = "#080B12";
    window.EJS_AdUrl = "";

    // Idioma da interface do emulador.
    window.EJS_language = "pt-BR";

    // Nenhum recurso externo: netplay depende de servidor de terceiros.
    window.EJS_Buttons = { netplay: false };

    // Sem servidor de netplay configurado.
    window.EJS_netplayServer = "";
  }

  /* ------------------------------------------------------------- início --- */

  function loadEmulatorScript() {
    return new Promise(function (resolve, reject) {
      var script = document.createElement("script");
      script.src = "../../data/loader.js";
      script.onload = resolve;
      script.onerror = function () {
        reject(new Error("loader.js"));
      };
      document.body.appendChild(script);
    });
  }

  function checkRom(url) {
    // Verificação leve e de mesma origem, só para dar erro legível.
    return fetch(url, { method: "HEAD" }).then(function (res) {
      if (!res.ok) throw new Error("HTTP " + res.status);
      return res;
    });
  }

  function start() {
    if (started) return;

    var game = readGameConfig();
    if (!game) {
      showError(
        "Configuração ausente",
        "Os dados do jogo não foram encontrados nesta página."
      );
      return;
    }

    started = true;

    var btn = $("start-button");
    if (btn) btn.disabled = true;

    showLoading("Preparando o emulador…");

    checkRom(game.rom)
      .then(function () {
        showLoading("Carregando o EmulatorJS…");
        configureEmulator(game);
        return loadEmulatorScript();
      })
      .then(function () {
        // A partir daqui o EmulatorJS assume o controle do palco.
        var overlay = $("stage-overlay");
        if (overlay) overlay.hidden = true;
      })
      .catch(function (err) {
        started = false;
        if (btn) btn.disabled = false;

        if (err && err.message === "loader.js") {
          showError(
            "Falha ao carregar o emulador",
            "Não foi possível carregar data/loader.js. Verifique se a pasta " +
              "data/ do EmulatorJS está presente no site."
          );
        } else {
          showError(
            "Falha ao carregar a ROM",
            "O arquivo " +
              game.rom +
              " não pôde ser lido (" +
              (err && err.message ? err.message : "erro desconhecido") +
              ")."
          );
        }
      });
  }

  /* --------------------------------------------------------- tela cheia --- */

  function toggleFullscreen() {
    var stage = $("stage");
    if (!stage) return;

    var doc = document;
    var isFull =
      doc.fullscreenElement ||
      doc.webkitFullscreenElement ||
      doc.mozFullScreenElement;

    if (isFull) {
      var exit =
        doc.exitFullscreen || doc.webkitExitFullscreen || doc.mozCancelFullScreen;
      if (exit) exit.call(doc);
      return;
    }

    var request =
      stage.requestFullscreen ||
      stage.webkitRequestFullscreen ||
      stage.mozRequestFullScreen;
    if (request) request.call(stage);
  }

  /* ---------------------------------------------------------------- init -- */

  function init() {
    var btn = $("start-button");
    if (btn) btn.addEventListener("click", start);

    var fsBtn = $("fullscreen-button");
    if (fsBtn) fsBtn.addEventListener("click", toggleFullscreen);

    // Exibe o caminho da ROM em uso (transparência, valor fixo do HTML).
    var game = readGameConfig();
    var romLabel = $("rom-path");
    if (romLabel && game) {
      romLabel.textContent = game.rom.replace("../../", "");
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
