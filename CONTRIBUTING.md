# Contribuindo — PowerArcades Games

Obrigado pelo interesse. Este projeto é um site estático publicado no GitHub
Pages, então as regras são simples e o foco é não quebrar o que já funciona.

---

## Regras inegociáveis

1. **Nenhum recurso externo.** Nada de CDN, Google Fonts, analytics, pixels,
   iframes de terceiros ou APIs remotas. Tudo é servido pelo próprio domínio.
2. **Nenhuma credencial no repositório.** Token, senha, chave privada e afins
   nunca entram — nem em exemplo, nem comentados.
3. **Nenhuma ROM baixada da internet.** As ROMs são fornecidas pelo
   proprietário. Não pesquise, não baixe, não substitua e não envie ROMs para
   serviços externos.
4. **Sem `eval`, `new Function`, `document.write` ou `innerHTML`** no código
   próprio do portal.
5. **O caminho da ROM é sempre fixo no HTML.** Nunca leia `location.search`,
   hash ou qualquer entrada do usuário para montar caminho de arquivo.
6. **Não quebre o site principal** (`brotherofjhonny.github.io`). Este
   repositório é independente e não deve alterá-lo.
7. **Sem `git push --force` e sem reescrita de histórico.**

---

## Antes de abrir um PR

Rode a bateria completa a partir da raiz do projeto:

```bash
./scripts/validate-roms.sh
./scripts/security-check.sh
./scripts/validate-links.sh
./scripts/test-site.sh
```

Os quatro precisam sair com código `0`.

---

## Adicionando um jogo

1. Coloque a ROM em `roms/`, **preservando exatamente** a capitalização do
   arquivo. O GitHub Pages diferencia maiúsculas de minúsculas.
2. Acrescente a entrada em `assets/js/catalog.js` (`slug`, `title`,
   `platform`, `genre`, `players`, `year`, `cover`, `url`, `rom`).
3. Acrescente a mesma entrada na lista `GAMES` de
   `scripts/generate-game-pages.py` e rode:

   ```bash
   python3 scripts/generate-game-pages.py
   ```

   Não edite `games/<slug>/index.html` à mão — o arquivo é gerado.
4. Gere a capa acrescentando o jogo em `scripts/generate-artwork.py` e rodando:

   ```bash
   python3 scripts/generate-artwork.py
   ```

   A arte precisa ser **original**. Não redistribua box art, sprites ou
   capturas de tela de terceiros.
5. Acrescente a URL em `sitemap.xml`.
6. Atualize os checksums:

   ```bash
   ./scripts/validate-roms.sh
   ```

7. Rode a bateria completa de validação.

---

## Estilo de código

- HTML semântico, `lang="pt-BR"`, foco visível, `aria-label` onde o texto
  visível não basta.
- CSS com as variáveis já definidas em `:root` (`--neon`, `--purple`,
  `--orange`, …). Respeite `prefers-reduced-motion`.
- JavaScript em ES5/ES6 conservador, sem build step e sem dependências.
- Fontes do sistema apenas.
- Comentários e textos de interface em português do Brasil.

---

## Commits

Mensagens no imperativo e em português, descrevendo o efeito:

```text
Adiciona página do jogo Top Gear 2
Corrige fallback de capa no catálogo
```

Não inclua arquivos temporários, backups, capturas com dados sensíveis nem
histórico de terminal.

---

## Licença

Ao contribuir, você concorda que sua contribuição seja distribuída sob a
**GPL-3.0**, a mesma licença do projeto (exigida pela redistribuição do
EmulatorJS).
