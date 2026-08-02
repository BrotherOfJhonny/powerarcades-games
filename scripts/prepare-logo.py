#!/usr/bin/env python3
"""Prepara o logotipo oficial do PowerArcades para uso no site.

Entrada : PNG do logo sobre fundo cinza com halo branco.
Saida   : assets/images/logo-powerarcades.webp  (fundo transparente)
          assets/images/favicon.png             (marca compacta)
          assets/images/social-share.webp       (1200x630 com o logo)

O recorte usa saturacao + morfologia: o fundo e' totalmente dessaturado
(R=G=B), enquanto o amarelo da marca e' muito saturado. O contorno preto
tambem e' dessaturado, entao ele e' recuperado por fechamento morfologico
da mascara amarela (fica dentro da silhueta das letras).
"""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = "/home/kali/Desktop/powerarcades-games"
IMG = os.path.join(ROOT, "assets/images")

SRC_CANDIDATES = [
    "/media/sf_VMCompart/logo/Logo_power.png",
    os.path.join(ROOT, "assets/images/_logo-origem.png"),
]

GOLD = (241, 190, 29)
BG = (8, 11, 18)
BG_SOFT = (17, 24, 39)
NEON = (0, 174, 239)
PURPLE = (124, 58, 237)
WHITE = (248, 250, 252)
GREY = (148, 163, 184)

F_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
F_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def find_source():
    for p in SRC_CANDIDATES:
        if os.path.isfile(p):
            return p
    sys.exit("Logo de origem nao encontrado em: " + ", ".join(SRC_CANDIDATES))


def binary_dilate(mask, r):
    img = Image.fromarray((mask * 255).astype("uint8"))
    img = img.filter(ImageFilter.MaxFilter(2 * r + 1))
    return np.array(img) > 127


def binary_erode(mask, r):
    img = Image.fromarray((mask * 255).astype("uint8"))
    img = img.filter(ImageFilter.MinFilter(2 * r + 1))
    return np.array(img) > 127


def cutout(src_path):
    """Retorna o logo em RGBA com fundo transparente, recortado no bbox."""
    im = Image.open(src_path).convert("RGB")
    a = np.asarray(im).astype(np.int16)

    mx = a.max(axis=2)
    mn = a.min(axis=2)
    sat = mx - mn                      # saturacao aproximada
    val = mx

    # Amarelo da marca: bem saturado, com R>=G>B.
    yellow = (sat > 55) & (a[:, :, 0] >= a[:, :, 1] - 10) & (a[:, :, 1] > a[:, :, 2])

    # Fechamento: une as letras e engloba o contorno preto entre elas.
    closed = binary_erode(binary_dilate(yellow, 9), 9)

    # Contorno escuro que esta DENTRO da silhueta do logo.
    dark = val < 105
    outline = closed & dark

    mask = yellow | outline

    # Limpa respingos isolados e suaviza a borda.
    mask = binary_dilate(binary_erode(mask, 1), 1)

    alpha = Image.fromarray((mask * 255).astype("uint8")).filter(
        ImageFilter.GaussianBlur(0.6))

    out = im.convert("RGBA")
    out.putalpha(alpha)

    bbox = out.getbbox()
    if bbox:
        out = out.crop(bbox)
    return out


def save_logo(logo):
    # Altura util no cabecalho: exportamos com folga para telas 2x.
    target_h = 260
    w = round(logo.width * target_h / logo.height)
    big = logo.resize((w, target_h), Image.LANCZOS)
    path = os.path.join(IMG, "logo-powerarcades.webp")
    big.save(path, "WEBP", quality=95, method=6, lossless=False)
    print(f"  logo       {os.path.relpath(path, ROOT)}  ({big.width}x{big.height})")
    return big


def save_favicon(logo):
    """Marca compacta: quadrado escuro + logo ajustado, legivel em 32px."""
    S = 256
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, S - 1, S - 1], radius=52, fill=BG)
    d.rounded_rectangle([5, 5, S - 6, S - 6], radius=48,
                        outline=GOLD + (255,), width=6)

    inner = S - 56
    scale = min(inner / logo.width, inner / logo.height)
    lw, lh = int(logo.width * scale), int(logo.height * scale)
    img.alpha_composite(logo.resize((lw, lh), Image.LANCZOS),
                        ((S - lw) // 2, (S - lh) // 2))

    path = os.path.join(IMG, "favicon.png")
    img.save(path, "PNG", optimize=True)
    print(f"  favicon    {os.path.relpath(path, ROOT)}")


def lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def vertical_gradient(size, top, bottom):
    w, h = size
    strip = Image.new("RGB", (1, h))
    p = strip.load()
    for y in range(h):
        p[0, y] = lerp(top, bottom, y / max(1, h - 1))
    return strip.resize(size, Image.BILINEAR)


def perspective_grid(size, color, horizon_ratio=0.58, alpha=64):
    w, h = size
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    hy = int(h * horizon_ratio)
    vp = w // 2
    for i in range(-14, 15):
        d.line([(vp, hy), (vp + i * (w // 7), h)], fill=color + (alpha,), width=2)
    y, step = hy, 2.0
    while y < h:
        d.line([(0, int(y)), (w, int(y))], fill=color + (alpha,), width=2)
        step *= 1.34
        y += step
    return layer


def save_social(logo):
    W, H = 1200, 630
    img = vertical_gradient((W, H), BG_SOFT, BG).convert("RGBA")
    img.alpha_composite(perspective_grid((W, H), NEON))

    scale = min((W - 220) / logo.width, 300 / logo.height)
    lw, lh = int(logo.width * scale), int(logo.height * scale)
    big = logo.resize((lw, lh), Image.LANCZOS)

    glow = big.filter(ImageFilter.GaussianBlur(22))
    pos = ((W - lw) // 2, 120)
    img.alpha_composite(glow, pos)
    img.alpha_composite(big, pos)

    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(F_BOLD, 44)
    t = "GAMES"
    d.text(((W - d.textlength(t, font=f)) / 2, 120 + lh + 18), t, font=f, fill=WHITE)

    f2 = ImageFont.truetype(F_REG, 27)
    t2 = "Classicos direto no navegador"
    d.text(((W - d.textlength(t2, font=f2)) / 2, 120 + lh + 82), t2, font=f2, fill=GREY)

    d.rectangle([0, H - 12, W, H], fill=GOLD)
    d.rectangle([0, H - 12, W // 2, H], fill=NEON)

    path = os.path.join(IMG, "social-share.webp")
    img.convert("RGB").save(path, "WEBP", quality=90, method=6)
    print(f"  social     {os.path.relpath(path, ROOT)}")


if __name__ == "__main__":
    src = find_source()
    print("Preparando logotipo a partir de:", src)

    logo = cutout(src)
    print(f"  recorte    {logo.width}x{logo.height} com alfa")

    big = save_logo(logo)
    save_favicon(logo)
    save_social(logo)
    print("OK")
