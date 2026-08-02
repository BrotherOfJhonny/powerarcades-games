/* ==========================================================================
   PowerArcades Games — proteção contra clickjacking (frame-buster)
   --------------------------------------------------------------------------
   MITIGAÇÃO PARCIAL, não solução definitiva.

   A defesa correta é o cabeçalho HTTP `X-Frame-Options: DENY` ou a diretiva
   `frame-ancestors` da CSP. Ambos são **header-only**: foi testado em
   navegador que, entregues via <meta>, são ignorados — o Chrome inclusive
   avisa "X-Frame-Options may only be set via an HTTP header". O GitHub Pages
   não permite definir cabeçalhos de resposta, então este script cobre o
   caso comum enquanto o site estiver hospedado lá.

   Limite conhecido: um <iframe sandbox> sem "allow-top-navigation" impede a
   fuga. Por isso o script também esconde o conteúdo e oferece um link para
   abrir o site na origem correta — assim o visitante nunca interage com uma
   cópia enquadrada sem perceber.

   Ao migrar para um host com cabeçalhos (Cloudflare, Netlify, Vercel), veja
   o arquivo `_headers` na raiz e remova este script.
   ========================================================================== */

(function () {
  "use strict";

  // Página no topo: nada a fazer.
  if (window.top === window.self) return;

  var OFFICIAL = "https://brotherofjhonny.github.io/powerarcades-games/";

  // Esconde imediatamente, antes de qualquer pintura, para não servir de isca.
  // Atribuição via CSSOM não é bloqueada pela CSP (só `style="..."` no HTML).
  try {
    document.documentElement.style.visibility = "hidden";
  } catch (e) {}

  // 1. Tentativa de fuga: leva a janela do topo para a URL real.
  var escaped = false;
  try {
    if (window.top.location.href !== window.self.location.href) {
      window.top.location.replace(window.self.location.href);
      escaped = true;
    }
  } catch (e) {
    // Bloqueado por sandbox ou origem cruzada — segue para o plano B.
  }

  if (escaped) return;

  // 2. Plano B: substitui a página por um aviso com link para a origem real.
  function showNotice() {
    try {
      var doc = document;
      var body = doc.body;
      if (!body) return;

      while (body.firstChild) body.removeChild(body.firstChild);

      var box = doc.createElement("div");
      box.setAttribute("role", "alert");
      var s = box.style;
      s.fontFamily = "system-ui, -apple-system, Segoe UI, Roboto, sans-serif";
      s.background = "#080b12";
      s.color = "#f8fafc";
      s.padding = "28px 22px";
      s.textAlign = "center";
      s.minHeight = "100vh";
      s.display = "flex";
      s.flexDirection = "column";
      s.alignItems = "center";
      s.justifyContent = "center";
      s.gap = "14px";

      var h = doc.createElement("strong");
      h.textContent = "Este conteúdo está sendo exibido dentro de outro site.";
      h.style.fontSize = "1.05rem";
      box.appendChild(h);

      var p = doc.createElement("p");
      p.textContent =
        "Por segurança, o PowerArcades Games não é exibido em páginas de " +
        "terceiros. Abra o site oficial para jogar.";
      p.style.margin = "0";
      p.style.color = "#94a3b8";
      p.style.maxWidth = "460px";
      box.appendChild(p);

      var a = doc.createElement("a");
      a.href = OFFICIAL;
      a.target = "_top";
      a.rel = "noopener";
      a.textContent = "Abrir o PowerArcades Games";
      var as = a.style;
      as.display = "inline-block";
      as.background = "#f1be1d";
      as.color = "#14100a";
      as.fontWeight = "700";
      as.padding = "12px 22px";
      as.borderRadius = "999px";
      as.textDecoration = "none";
      box.appendChild(a);

      body.appendChild(box);
      doc.documentElement.style.visibility = "visible";
    } catch (e) {
      // Se nem isso for possível, o conteúdo permanece oculto — que já é
      // o comportamento seguro.
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", showNotice);
  } else {
    showNotice();
  }
})();
