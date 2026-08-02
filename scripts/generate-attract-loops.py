#!/usr/bin/env python3
"""Gera os loops animados ("modo atração") das telas dos gabinetes.

Saida: assets/images/games/<slug>-loop.webp  (WebP animado, em loop infinito)

Toda a arte e' original e desenhada aqui: grade em fuga + um motivo
abstrato por genero. Nao ha sprite, captura de tela, box art nem video
de jogo de terceiros em nenhuma etapa.

Truque do loop perfeito: cada elemento avanca exatamente um periodo
completo ao longo dos N frames, entao o quadro N e' identico ao quadro 0.
"""
import math
import os

from PIL import Image, ImageDraw, ImageFilter

ROOT = "/home/kali/Desktop/powerarcades-games"
OUT_DIR = os.path.join(ROOT, "assets/images/games")

# A tela do gabinete renderiza por volta de 330px de largura, entao 448
# ainda sobra resolucao. Combinacao medida (ver histórico): 448x336 com
# 24 frames em q58/method 6 corta ~32% do peso sem perda visivel.
W, H = 448, 336
FRAMES = 24
DURATION_MS = 100         # 24 x 100ms = 2,4s por volta

BG = (8, 11, 18)
BG_SOFT = (17, 24, 39)
WHITE = (248, 250, 252)
GOLD = (241, 190, 29)

HORIZON = int(H * 0.60)


# ---------------------------------------------------------------- utilidades
def lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def sky(accent):
    """Fundo com brilho de horizonte na cor do jogo."""
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    for y in range(H):
        t = y / (H - 1)
        if y < HORIZON:
            k = (y / max(1, HORIZON)) ** 2.2
            col = lerp(BG, lerp(BG_SOFT, accent, 0.22), k)
        else:
            col = lerp(BG_SOFT, BG, (y - HORIZON) / max(1, H - HORIZON))
        d.line([(0, y), (W, y)], fill=col)
    return img


def road(phase, accent, lines=17, alpha=150):
    """Grade em fuga. As linhas horizontais correm em direcao ao observador.

    Loop perfeito: em phase=1 o conjunto avancou exatamente um indice.
    """
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    vp = W // 2

    # Linhas verticais convergindo para o ponto de fuga (estaticas).
    for i in range(-9, 10):
        d.line([(vp, HORIZON), (vp + i * (W // 4), H)],
               fill=accent + (alpha // 2,), width=2)

    # Linhas horizontais em perspectiva, avancando.
    for i in range(lines):
        depth = (i - phase) + 0.85
        if depth <= 0.06:
            continue
        y = HORIZON + (H - HORIZON) * 1.9 / depth
        if y >= H or y < HORIZON:
            continue
        # Mais perto = mais forte e mais grossa.
        near = min(1.0, 1.6 / depth)
        a = int(alpha * (0.30 + 0.70 * near))
        d.line([(0, int(y)), (W, int(y))],
               fill=accent + (min(255, a),), width=1 + int(2 * near))

    return layer


def glow(base, layer, radius=13, strength=0.95):
    g = layer.filter(ImageFilter.GaussianBlur(radius))
    if strength != 1.0:
        g.putalpha(g.getchannel("A").point(lambda v: int(v * strength)))
    base.alpha_composite(g)
    base.alpha_composite(layer)
    return base


def scanlines(alpha=30):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for y in range(0, H, 3):
        d.line([(0, y), (W, y)], fill=(0, 0, 0, alpha))
    return layer


def vignette():
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rectangle([0, 0, W, 26], fill=(0, 0, 0, 120))
    d.rectangle([0, H - 34, W, H], fill=(0, 0, 0, 140))
    d.rectangle([0, 0, 22, H], fill=(0, 0, 0, 110))
    d.rectangle([W - 22, 0, W, H], fill=(0, 0, 0, 110))
    return layer.filter(ImageFilter.GaussianBlur(16))


# ------------------------------------------------------------------- motivos
def motif_shield(d, p, accent):
    """Ação: escudo com aneis girando e estrela pulsando."""
    cx, cy = W // 2, int(HORIZON * 0.70)
    pulse = 1.0 + 0.06 * math.sin(p * 2 * math.pi)

    for idx, (r, col) in enumerate([(100, accent), (72, WHITE),
                                    (44, accent), (16, WHITE)]):
        rr = r * pulse
        # Aneis alternados girando em sentidos opostos, em arcos.
        start = (p * 360 * (1 if idx % 2 == 0 else -1)) % 360
        for k in range(4):
            a0 = start + k * 90
            d.arc([cx - rr, cy - rr, cx + rr, cy + rr],
                  a0 + 8, a0 + 82, fill=col + (238,), width=6)

    # Estrela girando.
    ang0 = -90 + p * 360
    pts = []
    for k in range(5):
        a = math.radians(ang0 + k * 144)
        pts.append((cx + 36 * pulse * math.cos(a), cy + 36 * pulse * math.sin(a)))
    d.line(pts + [pts[0]], fill=WHITE + (255,), width=5)


def motif_blocks(d, p, accent):
    """Plataforma: blocos quicando e nuvens deslizando."""
    cy = int(HORIZON * 0.66)

    # Nuvens: deslizam uma largura inteira -> loop perfeito.
    for i in range(3):
        x = (i * (W / 3) + p * W) % (W + 130) - 65
        y = 44 + (i % 2) * 26
        for dx, dy, rr in ((0, 0, 22), (24, -8, 26), (50, 2, 20)):
            d.ellipse([x + dx - rr, y + dy - rr, x + dx + rr, y + dy + rr],
                      outline=(255, 255, 255, 92), width=3)

    # Blocos quicando com fases defasadas.
    for i in range(4):
        ph = (p + i * 0.25) % 1.0
        bob = -16 * abs(math.sin(ph * math.pi))
        x = W // 2 - 150 + i * 82
        y = cy + bob
        d.rounded_rectangle([x, y, x + 66, y + 66], radius=10,
                            outline=accent + (245,), width=6)
        # "?" desenhado a mao, para nao depender de fonte instalada.
        qx, qy = x + 33, y + 26
        # gancho superior: da esquerda, passando por cima, ate a direita
        d.arc([qx - 15, qy - 17, qx + 15, qy + 13], 180, 15,
              fill=WHITE + (255,), width=6)
        # descida do gancho ate o centro
        d.line([(qx + 13, qy + 2), (qx + 1, qy + 14)], fill=WHITE + (255,), width=6)
        # haste
        d.line([(qx + 1, qy + 13), (qx + 1, qy + 22)], fill=WHITE + (255,), width=6)
        # ponto
        d.ellipse([qx - 4, qy + 29, qx + 4, qy + 37], fill=WHITE + (255,))


def motif_sewer(d, p, accent):
    """Beat 'em up: bueiro girando e ondas se expandindo."""
    cx, cy = W // 2, int(HORIZON * 0.72)

    # Ondas concentricas nascendo e sumindo.
    for i in range(3):
        ph = (p + i / 3.0) % 1.0
        rr = 40 + ph * 130
        a = int(150 * (1 - ph))
        if a > 4:
            d.ellipse([cx - rr, cy - rr * 0.42, cx + rr, cy + rr * 0.42],
                      outline=accent + (a,), width=3)

    # Tampa do bueiro: 8 raios -> girar 45 graus fecha o loop.
    d.ellipse([cx - 112, cy - 50, cx + 112, cy + 50], outline=accent + (245,), width=9)
    d.ellipse([cx - 82, cy - 36, cx + 82, cy + 36], outline=WHITE + (165,), width=5)
    base = p * 45.0
    for i in range(8):
        a = math.radians(base + i * 45)
        d.line([(cx + 26 * math.cos(a), cy + 12 * math.sin(a)),
                (cx + 78 * math.cos(a), cy + 34 * math.sin(a))],
               fill=accent + (205,), width=6)


def motif_speed(d, p, accent):
    """Corrida: rastros de velocidade e dois carros balançando."""
    # Rastros: percorrem a largura toda -> loop perfeito.
    for i in range(9):
        seed = (i * 37) % 100
        y = 40 + i * 22
        ln = 90 + (seed % 5) * 44
        x = ((seed * 5 + p * (W + 300)) % (W + 300)) - 300
        col = accent if i % 2 else WHITE
        a = 120 + (seed % 5) * 26
        d.rounded_rectangle([x, y, x + ln, y + 8], radius=4, fill=col + (a,))

    # Carros (silhueta simples), com leve balanco.
    for i in range(2):
        bob = 5 * math.sin((p + i * 0.5) * 2 * math.pi)
        x = 96 + i * 220
        y = int(HORIZON * 0.86) + bob
        d.polygon([(x, y + 40), (x + 114, y + 40), (x + 92, y), (x + 24, y)],
                  outline=accent + (255,), width=6)
        for wx in (x + 10, x + 76):
            d.ellipse([wx, y + 30, wx + 32, y + 62], outline=WHITE + (225,), width=5)


MOTIFS = {
    "shield": motif_shield,
    "blocks": motif_blocks,
    "sewer": motif_sewer,
    "speed": motif_speed,
}


# --------------------------------------------------------------------- saida
GAMES = [
    ("captain-america-and-the-avengers", (0, 174, 239), "shield"),
    ("super-mario-world", (255, 107, 0), "blocks"),
    ("tmnt-4-turtles-in-time", (34, 197, 94), "sewer"),
    ("top-gear-2", (124, 58, 237), "speed"),
]

SCAN = scanlines()
VIGN = vignette()


def build(slug, accent, motif):
    frames = []
    for f in range(FRAMES):
        p = f / FRAMES                      # fase em [0,1)
        img = sky(accent).convert("RGBA")
        img.alpha_composite(road(p * 1.0, accent))

        art = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        MOTIFS[motif](ImageDraw.Draw(art), p, accent)
        img = glow(img, art, radius=12, strength=0.9)

        # Nem scanlines nem vinheta sao gravadas aqui: o CSS do gabinete
        # ja desenha as duas por cima. Baixar esse detalhe de alta
        # frequencia melhora muito a compressao do WebP animado.
        frames.append(img.convert("RGB"))

    path = os.path.join(OUT_DIR, f"{slug}-loop.webp")
    frames[0].save(path, "WEBP", save_all=True, append_images=frames[1:],
                   duration=DURATION_MS, loop=0, quality=58, method=6)
    kb = os.path.getsize(path) / 1024
    print(f"  loop   {slug}-loop.webp  {FRAMES} frames  {kb:.0f} KB")
    return path


if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    print("Gerando loops de atracao (arte original, sem material de terceiros):")
    total = 0
    for slug, accent, motif in GAMES:
        total += os.path.getsize(build(slug, accent, motif))
    print(f"total: {total/1024:.0f} KB")
    print("OK")
