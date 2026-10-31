# DevFest Galactic 2026 · Estande OWASP SJC

Página própria em `/games/devfest-galactic/`, adicionada ao catálogo e ao destaque da home. HTML/CSS/JS sem dependências, build, ROM ou EmulatorJS. Não carrega APIs, fontes ou recursos de terceiros. A edição web é mantida diretamente e não é sobrescrita pelos geradores de páginas SNES.

## Funcionalidades

Formações, ataques em mergulho, chefes de dois acertos, captura/resgate e nave dupla, fases bônus, três vidas, vida extra por score e partida de 180 segundos. Teclado, Gamepad API padrão e toque. Áudio sintetizado após interação. O mesmo botão de tiro confirma letras no teclado virtual e salva ao selecionar ✓. Os cartões PNG têm resolução nativa de 1080×1350 e 1080×1920, apelido, pontos, posição local, data/hora UTC−03 e origem SITE.

As imagens DevFest/GDG foram extraídas dos originais raster incorporados no PDF do Canva autorizado pelo usuário; detalhes em `games/devfest-galactic/assets/PROVENANCE.md`. A marca OWASP original foi fornecida pelo usuário. O destaque no jogo é a comunidade no estande OWASP São José dos Campos, com identidade DevFest/GDG. O QR direciona a https://www.owasp.community/chapters/sjc.

## Ranking e limites

`localStorage['devfest-galactic-site-v1']` guarda os resultados apenas neste navegador. Desempate por sequência de gravação, uma gravação por ID da partida. Falha de armazenamento conserva o formulário para nova tentativa; conteúdo ilegível não é substituído silenciosamente. Sair da aba encerra a partida com os pontos conquistados; não há pausa competitiva. Hora depende do relógio do dispositivo.

Origem SITE identifica a edição que gerou o cartão; não é selo antifraude. Não há backend, login, ranking global, sincronização com o bartop ou emissão de certificado verificado. O ranking presencial do estande continua separado. Um usuário pode manipular resultados locais ou editar imagens. O QR da comunidade não verifica score. Um serviço futuro deverá atribuir origem/horário, validar replay, autenticar o dispositivo do bartop e oferecer registro público verificável por ID/QR antes de usar a expressão “verificado”.

O motor web usa seed própria e porta as regras da edição Python, mas não se alega equivalência de replay entre linguagens. Não juntar as classificações das duas edições sem validar paridade.

## Validação

```sh
node --test tests/devfest-engine.cjs
./scripts/validate-roms.sh
./scripts/security-check.sh
./scripts/validate-links.sh
./scripts/test-site.sh
```

Os scripts shell calculam a raiz a partir da própria localização para funcionar em qualquer checkout. O scanner inclui o JavaScript da página web. Links externos da OWASP são navegação voluntária, não downloads automáticos. Nenhuma ROM existente ou configuração do EmulatorJS é alterada.

Os hashes dos quatro arquivos .sfc existentes foram comparados com o manifesto original e permaneceram iguais. A validação do cabeçalho SNES substitui apenas a heurística libmagic, que neste ambiente classificava esses mesmos arquivos válidos como data/zlib. Confere localização do cabeçalho, modo de mapeamento, vetor de reset e complemento de checksum.

Ensaio local em Chromium: início, tiro, encerramento, botão de tiro para letras, gravação única com origem SITE, persistência após recarregar, downloads PNG 1080×1350/1080×1920, catálogo e viewport móvel sem overflow; zero erros JavaScript. Seis testes do motor aprovados.
