#!/usr/bin/env python3
"""Gera a identidade visual original do PowerArcades Games.

Toda a arte e' gerada proceduralmente aqui. Nenhuma imagem de terceiros,
nenhuma box art licenciada, nenhum download externo.
"""
import math
import os
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = "/home/kali/Desktop/powerarcades-games"
IMG = os.path.join(ROOT, "assets/images")
GAMES_DIR = os.path.join(IMG, "games")

BG        = (8, 11, 18)
BG_SOFT   = (17, 24, 39)
NEON_BLUE = (0, 174, 239)
PURPLE    = (124, 58, 237)
ORANGE    = (255, 107, 0)
WHITE     = (248, 250, 252)
GREY      = (148, 163, 184)

F_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
F_REG  = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def vertical_gradient(size, top, bottom):
    w, h = size
    img = Image.new("RGB", (1, h))
    px = img.load()
    for y in range(h):
        px[0, y] = lerp(top, bottom, y / max(1, h - 1))
    return img.resize(size, Image.BILINEAR)


def add_glow(base, layer, radius=18, strength=1.0):
    """Compoe uma camada RGBA sobre base com halo neon."""
    glow = layer.filter(ImageFilter.GaussianBlur(radius))
    if strength != 1.0:
        a = glow.getchannel("A").point(lambda v: int(v * strength))
        glow.putalpha(a)
    base.alpha_composite(glow)
    base.alpha_composite(layer)
    return base


def perspective_grid(size, color, horizon_ratio=0.52, alpha=110):
    """Grade estilo synthwave: linhas fugindo para o horizonte."""
    w, h = size
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    hy = int(h * horizon_ratio)
    vp = w // 2
    for i in range(-14, 15):
        x_bottom = vp + i * (w // 7)
        d.line([(vp, hy), (x_bottom, h)], fill=color + (alpha,), width=2)
    y = hy
    step = 2.0
    while y < h:
        d.line([(0, int(y)), (w, int(y))], fill=color + (alpha,), width=2)
        step *= 1.34
        y += step
    return layer


def scanlines(size, alpha=26, gap=3):
    w, h = size
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for y in range(0, h, gap):
        d.line([(0, y), (w, y)], fill=(0, 0, 0, alpha), width=1)
    return layer


def fit_text(draw, text, fnt_path, max_w, start, min_size=14):
    """Reduz a fonte ate o texto caber na largura."""
    size = start
    while size > min_size:
        f = font(fnt_path, size)
        if draw.textlength(text, font=f) <= max_w:
            return f
        size -= 2
    return font(fnt_path, min_size)


def wrap(draw, text, fnt, max_w):
    words, lines, cur = text.split(), [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# --------------------------------------------------------------------------
# Capas dos jogos
# --------------------------------------------------------------------------
def cover(path, title, subtitle, accent, motif, seed):
    """Capa original 640x480, arte abstrata por genero.

    Sem texto embutido de proposito: o card do catalogo ja exibe titulo,
    plataforma e genero. Texto na imagem duplicaria a informacao.
    """
    rnd = random.Random(seed)
    W, H = 640, 480
    img = vertical_gradient((W, H), BG_SOFT, BG).convert("RGBA")

    img.alpha_composite(perspective_grid((W, H), accent, horizon_ratio=0.58,
                                         alpha=76))

    art = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(art)

    if motif == "shield":                      # acao / super-heroi
        cx, cy = W // 2, 240
        for r, col in ((110, accent), (78, WHITE), (46, accent), (16, WHITE)):
            d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=col + (235,), width=7)
        for i in range(5):
            ang = -90 + i * 72
            pts = []
            for k in (0, 144, 288):
                a = math.radians(ang + k)
                pts.append((cx + 40 * math.cos(a), cy + 40 * math.sin(a)))
            d.polygon(pts, outline=WHITE + (255,))

    elif motif == "blocks":                    # plataforma
        cx, cy = W // 2, 236
        for i in range(4):
            x = cx - 150 + i * 100
            y = cy + (18 if i % 2 else -18)
            d.rounded_rectangle([x, y, x + 74, y + 74], radius=10,
                                outline=accent + (240,), width=6)
            d.text((x + 30, y + 22), "?", font=font(F_BOLD, 34), fill=WHITE + (255,))
        for i in range(3):
            x = cx - 110 + i * 100
            d.arc([x, cy - 120, x + 80, cy - 40], 200, 340,
                  fill=WHITE + (140,), width=4)

    elif motif == "sewer":                     # beat 'em up
        cx, cy = W // 2, 232
        d.ellipse([cx - 130, cy - 66, cx + 130, cy + 66],
                  outline=accent + (240,), width=8)
        d.ellipse([cx - 96, cy - 48, cx + 96, cy + 48],
                  outline=WHITE + (160,), width=4)
        for i in range(8):
            a = math.radians(i * 45)
            d.line([(cx + 30 * math.cos(a), cy + 15 * math.sin(a)),
                    (cx + 90 * math.cos(a), cy + 45 * math.sin(a))],
                   fill=accent + (200,), width=5)
        for i in range(3):
            y = cy + 110 + i * 26
            d.arc([cx - 150 + i * 20, y, cx + 150 - i * 20, y + 40], 0, 180,
                  fill=WHITE + (90,), width=3)

    elif motif == "speed":                     # corrida
        cy = 230
        for i in range(9):
            y = cy - 120 + i * 30
            ln = rnd.randint(150, 330)
            x0 = rnd.randint(30, W - ln - 30)
            col = accent if i % 2 else WHITE
            d.rounded_rectangle([x0, y, x0 + ln, y + 11], radius=6,
                                fill=col + (rnd.randint(150, 255),))
        for i in range(2):
            x = 150 + i * 240
            d.polygon([(x, cy + 130), (x + 96, cy + 130), (x + 78, cy + 96),
                       (x + 18, cy + 96)], outline=accent + (255,), width=5)
            d.ellipse([x + 6, cy + 122, x + 34, cy + 150], outline=WHITE + (220,), width=4)
            d.ellipse([x + 62, cy + 122, x + 90, cy + 150], outline=WHITE + (220,), width=4)

    img = add_glow(img, art, radius=16, strength=0.9)

    # Vinheta discreta nas bordas, para o card nao "sangrar" no fundo.
    vign = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vd = ImageDraw.Draw(vign)
    vd.rectangle([0, 0, W, 60], fill=(8, 11, 18, 90))
    vd.rectangle([0, H - 90, W, H], fill=(8, 11, 18, 120))
    img.alpha_composite(vign.filter(ImageFilter.GaussianBlur(24)))

    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W - 1, H - 1], outline=(255, 255, 255, 26), width=2)
    img.alpha_composite(scanlines((W, H), alpha=20, gap=3))

    img.convert("RGB").save(path, "WEBP", quality=90, method=6)
    print("  capa      ", os.path.relpath(path, ROOT))


# --------------------------------------------------------------------------
# Logo, capa padrao, social share, favicon
# --------------------------------------------------------------------------
def logo(path):
    W, H = 720, 200
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    art = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(art)

    # Icone: joystick arcade estilizado
    cx, cy = 92, 100
    d.ellipse([cx - 62, cy - 62, cx + 62, cy + 62], outline=NEON_BLUE + (255,), width=8)
    d.line([(cx, cy + 26), (cx, cy - 22)], fill=WHITE + (255,), width=12)
    d.ellipse([cx - 24, cy - 52, cx + 24, cy - 4], fill=ORANGE + (255,))
    d.ellipse([cx - 40, cy + 24, cx + 40, cy + 52], outline=PURPLE + (255,), width=7)

    f1 = font(F_BOLD, 56)
    f2 = font(F_REG, 26)
    d.text((186, 40), "POWER", font=f1, fill=NEON_BLUE)
    off = d.textlength("POWER", font=f1)
    d.text((186 + off, 40), "ARCADES", font=f1, fill=ORANGE)
    d.text((190, 112), "@powerarcades", font=f2, fill=GREY)

    img = add_glow(img, art, radius=14, strength=0.75)
    img.save(path, "WEBP", quality=94, method=6, lossless=False)
    print("  logo      ", os.path.relpath(path, ROOT))


def default_cover(path):
    W, H = 640, 480
    img = vertical_gradient((W, H), BG_SOFT, BG).convert("RGBA")
    img.alpha_composite(perspective_grid((W, H), PURPLE, alpha=70))
    art = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(art)
    cx, cy = W // 2, 210
    d.rounded_rectangle([cx - 120, cy - 80, cx + 120, cy + 80], radius=22,
                        outline=NEON_BLUE + (255,), width=8)
    d.line([(cx - 74, cy), (cx - 26, cy)], fill=WHITE + (255,), width=10)
    d.line([(cx - 50, cy - 24), (cx - 50, cy + 24)], fill=WHITE + (255,), width=10)
    d.ellipse([cx + 26, cy - 34, cx + 62, cy + 2], fill=ORANGE + (255,))
    d.ellipse([cx + 62, cy + 2, cx + 98, cy + 38], fill=PURPLE + (255,))
    img = add_glow(img, art, radius=16, strength=0.85)
    d = ImageDraw.Draw(img)
    f = font(F_BOLD, 34)
    t = "PowerArcades"
    d.text(((W - d.textlength(t, font=f)) / 2, 350), t, font=f, fill=WHITE)
    f2 = font(F_REG, 20)
    t2 = "Capa indisponivel"
    d.text(((W - d.textlength(t2, font=f2)) / 2, 398), t2, font=f2, fill=GREY)
    img.alpha_composite(scanlines((W, H), alpha=20, gap=3))
    img.convert("RGB").save(path, "WEBP", quality=90, method=6)
    print("  capa pad. ", os.path.relpath(path, ROOT))


def social(path):
    W, H = 1200, 630
    img = vertical_gradient((W, H), BG_SOFT, BG).convert("RGBA")
    img.alpha_composite(perspective_grid((W, H), NEON_BLUE, horizon_ratio=0.58, alpha=64))

    art = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(art)
    cx, cy = 168, 250
    d.ellipse([cx - 84, cy - 84, cx + 84, cy + 84], outline=NEON_BLUE + (255,), width=10)
    d.line([(cx, cy + 34), (cx, cy - 30)], fill=WHITE + (255,), width=15)
    d.ellipse([cx - 32, cy - 70, cx + 32, cy - 6], fill=ORANGE + (255,))
    d.ellipse([cx - 54, cy + 32, cx + 54, cy + 70], outline=PURPLE + (255,), width=9)
    img = add_glow(img, art, radius=20, strength=0.8)

    d = ImageDraw.Draw(img)
    f1 = font(F_BOLD, 78)
    d.text((296, 186), "POWER", font=f1, fill=NEON_BLUE)
    off = d.textlength("POWER", font=f1)
    d.text((296 + off, 186), "ARCADES", font=f1, fill=ORANGE)
    d.text((300, 282), "GAMES", font=font(F_BOLD, 60), fill=WHITE)

    f3 = font(F_REG, 30)
    d.text((300, 366), "Classicos direto no navegador", font=f3, fill=GREY)
    d.text((300, 410), "@powerarcades", font=font(F_BOLD, 30), fill=PURPLE)

    d.rectangle([0, H - 12, W, H], fill=ORANGE)
    d.rectangle([0, H - 12, W // 2, H], fill=NEON_BLUE)
    img.alpha_composite(scanlines((W, H), alpha=16, gap=4))
    img.convert("RGB").save(path, "WEBP", quality=90, method=6)
    print("  social    ", os.path.relpath(path, ROOT))


def favicon(path):
    S = 256
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, S - 1, S - 1], radius=52, fill=BG)
    d.rounded_rectangle([6, 6, S - 7, S - 7], radius=48, outline=NEON_BLUE, width=7)
    cx, cy = S // 2, S // 2 + 6
    d.line([(cx, cy + 44), (cx, cy - 26)], fill=WHITE, width=20)
    d.ellipse([cx - 40, cy - 72, cx + 40, cy + 8], fill=ORANGE)
    d.ellipse([cx - 58, cy + 40, cx + 58, cy + 78], outline=PURPLE, width=13)
    img.save(path, "PNG", optimize=True)
    print("  favicon   ", os.path.relpath(path, ROOT))


COVERS = [
    ("captain-america-and-the-avengers.webp",
     "Captain America and the Avengers",
     "Super Nintendo  -  Acao", NEON_BLUE, "shield", 101),
    ("super-mario-world.webp",
     "Super Mario World",
     "Super Nintendo  -  Plataforma", ORANGE, "blocks", 202),
    ("tmnt-4-turtles-in-time.webp",
     "Teenage Mutant Ninja Turtles IV: Turtles in Time",
     "Super Nintendo  -  Beat 'em up", (34, 197, 94), "sewer", 303),
    ("top-gear-2.webp",
     "Top Gear 2",
     "Super Nintendo  -  Corrida", PURPLE, "speed", 404),
]

if __name__ == "__main__":
    os.makedirs(GAMES_DIR, exist_ok=True)
    print("Gerando identidade visual PowerArcades:")
    logo(os.path.join(IMG, "logo-powerarcades.webp"))
    favicon(os.path.join(IMG, "favicon.png"))
    social(os.path.join(IMG, "social-share.webp"))
    default_cover(os.path.join(IMG, "default-game-cover.webp"))
    for name, title, sub, accent, motif, seed in COVERS:
        cover(os.path.join(GAMES_DIR, name), title, sub, accent, motif, seed)
    print("OK")
