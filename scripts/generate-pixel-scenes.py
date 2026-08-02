#!/usr/bin/env python3
"""Cenas em pixel art para o modo atração dos gabinetes.

Diferente de generate-attract-loops.py (formas abstratas), aqui cada tela
é uma CENA DE JOGO desenhada do zero, usando apenas convenções de gênero:
pista em perspectiva, horizonte, faixas correndo, carro visto por trás e
HUD de velocidade. Nada é copiado, decalcado, pixelado ou derivado de
captura de tela, sprite ou arte de jogo existente.

Técnica: desenha em resolução baixa (224x168) e amplia com vizinho mais
próximo (NEAREST) para 448x336, o que produz pixels quadrados e nítidos.
"""
import math
import os

from PIL import Image, ImageDraw

ROOT = "/home/kali/Desktop/powerarcades-games"
OUT_DIR = os.path.join(ROOT, "assets/images/games")

LW, LH = 224, 168          # resolução lógica (pixel art)
SCALE = 2                  # 224x168 -> 448x336
FRAMES = 24
DURATION_MS = 100          # 24 x 100ms = 2,4s

HORIZON = 78

# ------------------------------------------------------------------ paleta
SKY_TOP = (26, 16, 58)
SKY_MID = (92, 40, 96)
SKY_LOW = (232, 104, 60)
SUN_A = (255, 214, 96)
SUN_B = (255, 128, 72)
MOUNT_FAR = (44, 30, 74)
MOUNT_NEAR = (30, 20, 54)

GRASS_A = (38, 104, 56)
GRASS_B = (30, 86, 46)
RUMBLE_A = (226, 228, 234)
RUMBLE_B = (196, 46, 46)
ROAD_A = (74, 78, 92)
ROAD_B = (64, 68, 80)
DASH = (238, 240, 246)

CAR_BODY = (124, 58, 237)
CAR_DARK = (74, 32, 150)
CAR_GLASS = (24, 28, 48)
CAR_LIGHT = (255, 92, 64)
TIRE = (18, 18, 24)
OUTLINE = (12, 10, 20)

HUD_BG = (10, 12, 22)
HUD_FG = (241, 190, 29)
HUD_DIM = (120, 132, 156)

# Geometria do loop. O mundo avança exatamente STRIPE_LEN*2 por volta,
# então o quadro final coincide com o inicial.
STRIPE_LEN = 14.0
LOOP_DZ = STRIPE_LEN * 2.0
ROAD_K = 1500.0            # constante de perspectiva
POST_SPACING = LOOP_DZ / 2.0

# ------------------------------------------------- fonte de 3x5 (bitmap)
FONT = {
    "0": ["111", "101", "101", "101", "111"],
    "1": ["010", "110", "010", "010", "111"],
    "2": ["111", "001", "111", "100", "111"],
    "3": ["111", "001", "111", "001", "111"],
    "4": ["101", "101", "111", "001", "001"],
    "5": ["111", "100", "111", "001", "111"],
    "6": ["111", "100", "111", "101", "111"],
    "7": ["111", "001", "001", "001", "001"],
    "8": ["111", "101", "111", "101", "111"],
    "9": ["111", "101", "111", "001", "111"],
    "S": ["111", "100", "111", "001", "111"],
    "P": ["111", "101", "111", "100", "100"],
    "E": ["111", "100", "111", "100", "111"],
    "D": ["110", "101", "101", "101", "110"],
    "K": ["101", "101", "110", "101", "101"],
    "M": ["101", "111", "111", "101", "101"],
    "H": ["101", "101", "111", "101", "101"],
    "L": ["100", "100", "100", "100", "111"],
    "A": ["111", "101", "111", "101", "101"],
    "/": ["001", "001", "010", "100", "100"],
    " ": ["000", "000", "000", "000", "000"],
}


def text(px, s, x, y, color, gap=1):
    """Escreve com a fonte bitmap. px = objeto de acesso a pixels."""
    cx = x
    for ch in s.upper():
        glyph = FONT.get(ch)
        if glyph:
            for gy, row in enumerate(glyph):
                for gx, bit in enumerate(row):
                    if bit == "1":
                        tx, ty = cx + gx, y + gy
                        if 0 <= tx < LW and 0 <= ty < LH:
                            px[tx, ty] = color
        cx += 3 + gap
    return cx


def lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


# ------------------------------------------------------------------- céu
def draw_sky(d):
    """Céu em faixas (bandas propositais, estética 8 bits)."""
    bands = 14
    for b in range(bands):
        t = b / (bands - 1)
        if t < 0.55:
            col = lerp(SKY_TOP, SKY_MID, t / 0.55)
        else:
            col = lerp(SKY_MID, SKY_LOW, (t - 0.55) / 0.45)
        y0 = int(b * HORIZON / bands)
        y1 = int((b + 1) * HORIZON / bands)
        d.rectangle([0, y0, LW, y1], fill=col)


def draw_sun(d):
    """Sol com cortes horizontais — clichê do gênero, desenhado do zero."""
    cx, cy, r = LW // 2 + 34, HORIZON - 26, 26
    for y in range(cy - r, cy + r + 1):
        dy = (y - cy) / r
        if abs(dy) > 1:
            continue
        half = int(math.sqrt(max(0.0, 1 - dy * dy)) * r)
        # faixas vazadas na metade de baixo
        if y > cy and ((y - cy) // 3) % 2 == 1:
            continue
        t = (y - (cy - r)) / (2 * r)
        d.line([(cx - half, y), (cx + half, y)], fill=lerp(SUN_A, SUN_B, t))


def draw_mountains(d, drift):
    """Duas cordilheiras com deslocamento lento (paralaxe de fundo)."""
    for layer, (col, amp, step, yb, spd) in enumerate([
            (MOUNT_FAR, 26, 38, HORIZON + 1, 0.35),
            (MOUNT_NEAR, 17, 26, HORIZON + 1, 0.7)]):
        off = (drift * spd * LW) % step
        x = -step - off
        while x < LW + step:
            peak = amp if (int((x + off) // step) % 2 == 0) else amp * 0.62
            d.polygon([(x, yb), (x + step / 2, yb - peak), (x + step, yb)],
                      fill=col)
            x += step


# ------------------------------------------------------------------ pista
def road_half_width(y):
    """Meia largura da pista na linha y."""
    p = (y - HORIZON) / (LH - HORIZON)
    return 6 + p * 104


def draw_road(d, phase):
    """Pista em perspectiva com faixas correndo em direção ao observador."""
    world0 = phase * LOOP_DZ
    cx = LW / 2

    for y in range(HORIZON + 1, LH):
        dist = ROAD_K / (y - HORIZON)          # distância da câmera
        world = dist + world0
        band = int(world / STRIPE_LEN) % 2

        hw = road_half_width(y)
        grass = GRASS_A if band else GRASS_B
        road = ROAD_A if band else ROAD_B
        rumble = RUMBLE_A if band else RUMBLE_B

        d.line([(0, y), (LW, y)], fill=grass)

        rw = max(2, hw * 0.13)                 # zebra lateral
        d.line([(cx - hw - rw, y), (cx + hw + rw, y)], fill=rumble)
        d.line([(cx - hw, y), (cx + hw, y)], fill=road)

        # tracejado central: aparece em metade dos períodos
        if band and hw > 14:
            dw = max(1, hw * 0.035)
            d.line([(cx - dw, y), (cx + dw, y)], fill=DASH)


def draw_posts(d, phase):
    """Postes na beira da pista — principal pista visual de velocidade."""
    n = 8
    for i in range(n):
        dist = (i + 1 - phase) * POST_SPACING
        if dist <= 6:
            continue
        y = HORIZON + ROAD_K / dist
        if y >= LH or y <= HORIZON + 1:
            continue
        y = int(y)
        hw = road_half_width(y)
        # Marcos de beira de pista: finos e baixos. Escala limitada para
        # que os mais próximos não virem pilastras cobrindo a cena.
        h = max(2, min(30, int(620 / dist)))
        w = max(1, int(h * 0.16))
        for side in (-1, 1):
            x = int(LW / 2 + side * (hw + hw * 0.22 + 4))
            if -10 < x < LW + 10:
                d.rectangle([x - w, y - h, x + w, y], fill=(228, 228, 236))
                d.rectangle([x - w, y - h, x + w, y - h + max(1, h // 3)],
                            fill=(214, 68, 58))


# ------------------------------------------------------------------- carro
CAR = [
    "......SSSSSSSSSSSS......",
    "......S..........S......",
    ".....OOOOOOOOOOOOOO.....",
    "....OOGGGGGGGGGGGGOO....",
    "...OOBBBBBBBBBBBBBBOO...",
    "..TTTBBBBBBBBBBBBBBTTT..",
    "..TTTBLLBBBBBBBBLLBTTT..",
    "..TTTBBBBBBBBBBBBBBTTT..",
    "..TTTOOOOOOOOOOOOOOTTT..",
    "...TT..............TT...",
]

CAR_COLORS = {
    "S": CAR_DARK,
    "O": OUTLINE,
    "G": CAR_GLASS,
    "B": CAR_BODY,
    "T": TIRE,
    "L": CAR_LIGHT,
}


def draw_car(px, phase):
    """Carro genérico visto por trás, com balanço leve."""
    bob = int(round(1.5 * math.sin(phase * 2 * math.pi * 2)))
    sway = int(round(1.5 * math.sin(phase * 2 * math.pi)))
    cw = len(CAR[0]) * 2
    ox = (LW - cw) // 2 + sway
    oy = LH - len(CAR) * 2 - 26 + bob

    # sombra
    for sy in range(2):
        for sx in range(cw - 8):
            x, y = ox + 4 + sx, oy + len(CAR) * 2 + sy
            if 0 <= x < LW and 0 <= y < LH:
                px[x, y] = (26, 30, 38)

    for gy, row in enumerate(CAR):
        for gx, ch in enumerate(row):
            col = CAR_COLORS.get(ch)
            if not col:
                continue
            for dy in range(2):
                for dx in range(2):
                    x, y = ox + gx * 2 + dx, oy + gy * 2 + dy
                    if 0 <= x < LW and 0 <= y < LH:
                        px[x, y] = col


# --------------------------------------------------------------------- HUD
def draw_hud(img, px, phase):
    d = ImageDraw.Draw(img)
    d.rectangle([0, LH - 18, LW, LH], fill=HUD_BG)
    d.line([(0, LH - 18), (LW, LH - 18)], fill=HUD_FG)

    # velocidade oscilando, para dar vida
    speed = 268 + int(round(26 * math.sin(phase * 2 * math.pi)))
    text(px, "SPEED", 6, LH - 14, HUD_DIM)
    end = text(px, str(speed), 6, LH - 7, HUD_FG)
    text(px, "KM/H", end + 3, LH - 7, HUD_DIM)

    text(px, "LAP", LW - 52, LH - 14, HUD_DIM)
    text(px, "2/5", LW - 52, LH - 7, HUD_FG)

    # barra de aceleração
    bx, by, bw = LW - 92, LH - 12, 34
    d.rectangle([bx, by, bx + bw, by + 6], outline=HUD_DIM)
    fill = int(bw * (0.62 + 0.3 * abs(math.sin(phase * 2 * math.pi))))
    d.rectangle([bx + 1, by + 1, bx + max(1, fill), by + 5], fill=HUD_FG)


# ------------------------------------------------------------------- frame
def render_frame(phase):
    img = Image.new("RGB", (LW, LH), SKY_TOP)
    d = ImageDraw.Draw(img)

    draw_sky(d)
    draw_sun(d)
    draw_mountains(d, phase)
    draw_road(d, phase)
    draw_posts(d, phase)

    px = img.load()
    draw_car(px, phase)
    draw_hud(img, px, phase)

    return img.resize((LW * SCALE, LH * SCALE), Image.NEAREST)


def build(slug="top-gear-2"):
    frames = [render_frame(f / FRAMES) for f in range(FRAMES)]
    path = os.path.join(OUT_DIR, f"{slug}-loop.webp")
    frames[0].save(path, "WEBP", save_all=True, append_images=frames[1:],
                   duration=DURATION_MS, loop=0, quality=72, method=6)
    print(f"  cena   {slug}-loop.webp  {FRAMES} frames  "
          f"{os.path.getsize(path)/1024:.0f} KB")
    return path


if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    print("Gerando cena em pixel art (arte original, convenções de gênero):")
    build()
    print("OK")
