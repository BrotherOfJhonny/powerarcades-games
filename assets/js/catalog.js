/* ==========================================================================
   PowerArcades Games — catálogo centralizado
   --------------------------------------------------------------------------
   Fonte única de verdade dos jogos do portal.
   Os caminhos de ROM aqui são apenas informativos (exibidos na página do
   jogo). O carregamento real usa o caminho FIXO declarado em cada
   games/<slug>/index.html — nunca um valor vindo da URL ou do usuário.
   ========================================================================== */

(function (global) {
  "use strict";

  var games = Object.freeze([
    Object.freeze({
      slug: "captain-america-and-the-avengers",
      title: "Captain America and the Avengers",
      platform: "Super Nintendo",
      genre: "Ação",
      players: "1–2 jogadores",
      year: "1993",
      cover: "assets/images/games/captain-america-and-the-avengers.webp",
      url: "games/captain-america-and-the-avengers/",
      rom: "roms/captain-america-and-the-avengers.sfc",
      description:
        "Beat 'em up de ação com os heróis clássicos da Marvel, " +
        "lançado para Super Nintendo."
    }),
    Object.freeze({
      slug: "super-mario-world",
      title: "Super Mario World",
      platform: "Super Nintendo",
      genre: "Plataforma",
      players: "1–2 jogadores",
      year: "1990",
      cover: "assets/images/games/super-mario-world.webp",
      url: "games/super-mario-world/",
      rom: "roms/super-mario-world.sfc",
      description:
        "Plataforma que definiu uma geração, com o Mundo dos Dinossauros " +
        "e a estreia do Yoshi."
    }),
    Object.freeze({
      slug: "tmnt-4-turtles-in-time",
      title: "Teenage Mutant Ninja Turtles IV: Turtles in Time",
      platform: "Super Nintendo",
      genre: "Beat 'em up",
      players: "1–2 jogadores",
      year: "1992",
      cover: "assets/images/games/tmnt-4-turtles-in-time.webp",
      url: "games/tmnt-4-turtles-in-time/",
      rom: "roms/tmnt-4-turtles-in-time.sfc",
      description:
        "Beat 'em up cooperativo em viagem no tempo, referência absoluta " +
        "do gênero no Super Nintendo."
    }),
    Object.freeze({
      slug: "top-gear-2",
      title: "Top Gear 2",
      platform: "Super Nintendo",
      genre: "Corrida",
      players: "1–2 jogadores",
      year: "1993",
      cover: "assets/images/games/top-gear-2.webp",
      url: "games/top-gear-2/",
      // Capitalização preservada exatamente como o arquivo em disco.
      // O GitHub Pages diferencia maiúsculas de minúsculas.
      rom: "roms/TopGear2.sfc",
      description:
        "Corrida arcade com upgrades de carro, nitro e trilha sonora " +
        "inesquecível."
    })
  ]);

  global.PA_CATALOG = Object.freeze({
    games: games,
    bySlug: function (slug) {
      for (var i = 0; i < games.length; i++) {
        if (games[i].slug === slug) return games[i];
      }
      return null;
    }
  });
})(window);
