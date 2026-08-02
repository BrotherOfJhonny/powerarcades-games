#!/usr/bin/env python3
"""Cenas em pixel art para o modo atração das telas dos gabinetes.

Cada tela é uma CENA DE JOGO desenhada do zero, usando apenas convenções
de gênero — que não são protegidas:

  corrida     pista em perspectiva, horizonte, faixas correndo, HUD
  plataforma  chão em blocos, colinas, nuvens, moedas girando
  beat'em up  corredor subterrâneo, tubulações, grades, dois lutadores
  ação urbana silhueta de prédios, telhado rolando, figura correndo

Nada aqui é decalcado, pixelado, redesenhado ou derivado de captura de
tela, sprite, cenário ou personagem de jogo existente. Os personagens
são criações genéricas (um robô, vultos encapuzados, uma figura de capa)
e não representam nem imitam personagens protegidos.

Técnica: desenha em 224x168 e amplia com vizinho mais próximo (NEAREST)
para 448x336, o que produz pixels quadrados e nítidos.
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
PERIOD = 112.0             # período do mundo em rolagem horizontal
TILE = 16                  # 112 / 16 = 7 tiles por período

HUD_H = 18
GOLD = (241, 190, 29)
HUD_BG = (10, 12, 22)
HUD_DIM = (120, 132, 156)
OUTLINE = (12, 10, 20)

# ------------------------------------------------------- fonte bitmap 3x5
_F = {
    "A": "010 101 111 101 101", "B": "110 101 110 101 110",
    "C": "011 100 100 100 011", "D": "110 101 101 101 110",
    "E": "111 100 110 100 111", "F": "111 100 110 100 100",
    "G": "011 100 101 101 011", "H": "101 101 111 101 101",
    "I": "111 010 010 010 111", "J": "001 001 001 101 010",
    "K": "101 101 110 101 101", "L": "100 100 100 100 111",
    "M": "101 111 111 101 101", "N": "101 111 111 111 101",
    "O": "010 101 101 101 010", "P": "110 101 110 100 100",
    "Q": "010 101 101 111 011", "R": "110 101 110 101 101",
    "S": "011 100 010 001 110", "T": "111 010 010 010 010",
    "U": "101 101 101 101 111", "V": "101 101 101 101 010",
    "W": "101 101 111 111 101", "X": "101 101 010 101 101",
    "Y": "101 101 010 010 010", "Z": "111 001 010 100 111",
    "0": "111 101 101 101 111", "1": "010 110 010 010 111",
    "2": "111 001 111 100 111", "3": "111 001 111 001 111",
    "4": "101 101 111 001 001", "5": "111 100 111 001 111",
    "6": "111 100 111 101 111", "7": "111 001 001 001 001",
    "8": "111 101 111 101 111", "9": "111 101 111 001 111",
    "/": "001 001 010 100 100", "-": "000 000 111 000 000",
    ":": "000 010 000 010 000", " ": "000 000 000 000 000",
}
FONT = {k: v.split() for k, v in _F.items()}


def text(px, s, x, y, color, gap=1):
    """Escreve com a fonte bitmap própria (sem depender de fonte instalada)."""
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


def bands(d, y0, y1, top, bottom, n=12):
    """Gradiente em faixas — banding proposital, estética 8 bits."""
    for b in range(n):
        t = b / max(1, n - 1)
        yy0 = int(y0 + b * (y1 - y0) / n)
        yy1 = int(y0 + (b + 1) * (y1 - y0) / n)
        d.rectangle([0, yy0, LW, yy1], fill=lerp(top, bottom, t))


def blit(px, sprite, colors, ox, oy, scale=1, flip=False):
    """Desenha um sprite definido como grade de caracteres."""
    for gy, row in enumerate(sprite):
        for gx, ch in enumerate(row):
            col = colors.get(ch)
            if not col:
                continue
            sx = (len(row) - 1 - gx) if flip else gx
            for dy in range(scale):
                for dx in range(scale):
                    x, y = ox + sx * scale + dx, oy + gy * scale + dy
                    if 0 <= x < LW and 0 <= y < LH:
                        px[x, y] = col


def hud_frame(img, accent):
    d = ImageDraw.Draw(img)
    d.rectangle([0, LH - HUD_H, LW, LH], fill=HUD_BG)
    d.line([(0, LH - HUD_H), (LW, LH - HUD_H)], fill=accent)


def hud_bar(d, x, y, w, h, frac, accent):
    d.rectangle([x, y, x + w, y + h], outline=HUD_DIM)
    fw = max(1, int((w - 2) * max(0.0, min(1.0, frac))))
    d.rectangle([x + 1, y + 1, x + fw, y + h - 1], fill=accent)


# ==========================================================================
# 1. CORRIDA
# ==========================================================================
R_SKY_TOP, R_SKY_MID, R_SKY_LOW = (26, 16, 58), (92, 40, 96), (232, 104, 60)
R_SUN_A, R_SUN_B = (255, 214, 96), (255, 128, 72)
R_MT_FAR, R_MT_NEAR = (44, 30, 74), (30, 20, 54)
R_GRASS = ((38, 104, 56), (30, 86, 46))
R_RUMBLE = ((226, 228, 234), (196, 46, 46))
R_ROAD = ((74, 78, 92), (64, 68, 80))
R_DASH = (238, 240, 246)

R_HORIZON = 78
STRIPE_LEN = 14.0
LOOP_DZ = STRIPE_LEN * 2.0
ROAD_K = 1500.0
POST_SPACING = LOOP_DZ / 2.0

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
CAR_COLORS = {"S": (74, 32, 150), "O": OUTLINE, "G": (24, 28, 48),
              "B": (124, 58, 237), "T": (18, 18, 24), "L": (255, 92, 64)}


def road_half_width(y):
    return 6 + ((y - R_HORIZON) / (LH - R_HORIZON)) * 104


def scene_racing(phase, accent):
    img = Image.new("RGB", (LW, LH), R_SKY_TOP)
    d = ImageDraw.Draw(img)

    # céu
    for b in range(14):
        t = b / 13
        col = lerp(R_SKY_TOP, R_SKY_MID, t / 0.55) if t < 0.55 \
            else lerp(R_SKY_MID, R_SKY_LOW, (t - 0.55) / 0.45)
        d.rectangle([0, int(b * R_HORIZON / 14), LW,
                     int((b + 1) * R_HORIZON / 14)], fill=col)

    # sol vazado
    cx, cy, r = LW // 2 + 34, R_HORIZON - 26, 26
    for y in range(cy - r, cy + r + 1):
        dy = (y - cy) / r
        if abs(dy) > 1 or (y > cy and ((y - cy) // 3) % 2 == 1):
            continue
        half = int(math.sqrt(max(0.0, 1 - dy * dy)) * r)
        d.line([(cx - half, y), (cx + half, y)],
               fill=lerp(R_SUN_A, R_SUN_B, (y - cy + r) / (2 * r)))

    # montanhas em duas camadas
    for col, amp, step, spd in ((R_MT_FAR, 26, 38, 0.35),
                                (R_MT_NEAR, 17, 26, 0.7)):
        off = (phase * spd * LW) % step
        x = -step - off
        while x < LW + step:
            peak = amp if int((x + off) // step) % 2 == 0 else amp * 0.62
            d.polygon([(x, R_HORIZON + 1), (x + step / 2, R_HORIZON + 1 - peak),
                       (x + step, R_HORIZON + 1)], fill=col)
            x += step

    # pista
    world0 = phase * LOOP_DZ
    for y in range(R_HORIZON + 1, LH):
        dist = ROAD_K / (y - R_HORIZON)
        band = int((dist + world0) / STRIPE_LEN) % 2
        hw = road_half_width(y)
        d.line([(0, y), (LW, y)], fill=R_GRASS[band])
        rw = max(2, hw * 0.13)
        d.line([(LW / 2 - hw - rw, y), (LW / 2 + hw + rw, y)], fill=R_RUMBLE[band])
        d.line([(LW / 2 - hw, y), (LW / 2 + hw, y)], fill=R_ROAD[band])
        if band and hw > 14:
            dw = max(1, hw * 0.035)
            d.line([(LW / 2 - dw, y), (LW / 2 + dw, y)], fill=R_DASH)

    # marcos de beira de pista
    for i in range(8):
        dist = (i + 1 - phase) * POST_SPACING
        if dist <= 6:
            continue
        y = R_HORIZON + ROAD_K / dist
        if y >= LH or y <= R_HORIZON + 1:
            continue
        y = int(y)
        hw = road_half_width(y)
        h = max(2, min(30, int(620 / dist)))
        w = max(1, int(h * 0.16))
        for side in (-1, 1):
            x = int(LW / 2 + side * (hw + hw * 0.22 + 4))
            if -10 < x < LW + 10:
                d.rectangle([x - w, y - h, x + w, y], fill=(228, 228, 236))
                d.rectangle([x - w, y - h, x + w, y - h + max(1, h // 3)],
                            fill=(214, 68, 58))

    px = img.load()
    bob = int(round(1.5 * math.sin(phase * 4 * math.pi)))
    sway = int(round(1.5 * math.sin(phase * 2 * math.pi)))
    cw = len(CAR[0]) * 2
    ox, oy = (LW - cw) // 2 + sway, LH - len(CAR) * 2 - 26 + bob
    for sx in range(cw - 8):
        for sy in range(2):
            if 0 <= ox + 4 + sx < LW and 0 <= oy + len(CAR) * 2 + sy < LH:
                px[ox + 4 + sx, oy + len(CAR) * 2 + sy] = (26, 30, 38)
    blit(px, CAR, CAR_COLORS, ox, oy, 2)

    hud_frame(img, accent)
    d = ImageDraw.Draw(img)
    speed = 268 + int(round(26 * math.sin(phase * 2 * math.pi)))
    text(px, "SPEED", 6, LH - 14, HUD_DIM)
    end = text(px, str(speed), 6, LH - 7, GOLD)
    text(px, "KM/H", end + 3, LH - 7, HUD_DIM)
    text(px, "LAP", LW - 52, LH - 14, HUD_DIM)
    text(px, "2/5", LW - 52, LH - 7, GOLD)
    hud_bar(d, LW - 92, LH - 12, 34, 6,
            0.62 + 0.3 * abs(math.sin(phase * 2 * math.pi)), GOLD)
    return img


# ==========================================================================
# 2. PLATAFORMA
# ==========================================================================
P_SKY_TOP, P_SKY_LOW = (58, 148, 230), (150, 206, 246)
P_HILL_A, P_HILL_B = (46, 138, 68), (34, 112, 54)
P_GROUND_TOP = (74, 190, 92)
P_DIRT_A, P_DIRT_B = (150, 90, 48), (122, 70, 38)
P_BRICK = (198, 120, 60)
P_COIN_A, P_COIN_B = (255, 214, 96), (214, 158, 40)

P_GROUND_Y = LH - HUD_H - 34

HERO = [   # robozinho original, sem semelhança com personagem existente
    "..OOOOOO..",
    ".OWWWWWWO.",
    ".OWEWWEWO.",
    ".OWWWWWWO.",
    ".OWWMMWWO.",
    "..OOOOOO..",
    "..ABBBBA..",
    ".AABBBBAA.",
    "..O.BB.O..",
    "..OO..OO..",
]
HERO_COLORS = {"O": OUTLINE, "W": (236, 240, 248), "E": (32, 40, 70),
               "M": (214, 76, 76), "B": (0, 174, 239), "A": (150, 160, 180)}


def scene_platform(phase, accent):
    img = Image.new("RGB", (LW, LH), P_SKY_TOP)
    d = ImageDraw.Draw(img)
    bands(d, 0, P_GROUND_Y, P_SKY_TOP, P_SKY_LOW, 10)

    off = phase * PERIOD

    # nuvens (paralaxe lenta)
    for k in range(-1, 3):
        for bx, by, w in ((14, 22, 16), (68, 36, 12), (96, 16, 20)):
            x = bx + k * PERIOD - off * 0.25
            for cx2, cy2, rr in ((0, 0, 6), (7, -3, 8), (15, 1, 6)):
                d.ellipse([x + cx2 - rr, by + cy2 - rr,
                           x + cx2 + rr, by + cy2 + rr], fill=(244, 250, 255))

    # colinas (paralaxe média)
    for k in range(-1, 3):
        for bx, rr in ((10, 34), (78, 26)):
            x = bx + k * PERIOD - off * 0.55
            d.ellipse([x - rr, P_GROUND_Y - rr, x + rr, P_GROUND_Y + rr],
                      fill=P_HILL_B)
            d.ellipse([x - rr + 6, P_GROUND_Y - rr + 5, x + rr - 6,
                       P_GROUND_Y + rr], fill=P_HILL_A)

    # plataformas flutuantes com moedas
    for k in range(-1, 3):
        for bx, by, n in ((28, P_GROUND_Y - 52, 3), (86, P_GROUND_Y - 74, 2)):
            x = bx + k * PERIOD - off
            for i in range(n):
                bxx = x + i * TILE
                d.rectangle([bxx, by, bxx + TILE - 1, by + 10], fill=P_BRICK)
                d.rectangle([bxx, by, bxx + TILE - 1, by + 10], outline=OUTLINE)
                d.line([(bxx + TILE // 2, by), (bxx + TILE // 2, by + 10)],
                       fill=OUTLINE)
            # moeda girando sobre a plataforma
            spin = (phase * 3) % 1.0
            cw = abs(math.cos(spin * 2 * math.pi))
            hwc = max(1, int(5 * cw))
            ccx, ccy = x + (n * TILE) // 2, by - 14
            d.ellipse([ccx - hwc, ccy - 6, ccx + hwc, ccy + 6], fill=P_COIN_A)
            if hwc > 2:
                d.ellipse([ccx - hwc + 1, ccy - 4, ccx + hwc - 1, ccy + 4],
                          outline=P_COIN_B)

    # chão em tiles
    d.rectangle([0, P_GROUND_Y, LW, LH], fill=P_DIRT_A)
    d.rectangle([0, P_GROUND_Y, LW, P_GROUND_Y + 5], fill=P_GROUND_TOP)
    start = -int(off) % TILE - TILE
    for x in range(start, LW + TILE, TILE):
        d.line([(x, P_GROUND_Y + 6), (x, LH)], fill=P_DIRT_B)
        for row in range(P_GROUND_Y + 6, LH, 8):
            d.line([(x, row), (x + TILE, row)], fill=P_DIRT_B)
    d.line([(0, P_GROUND_Y), (LW, P_GROUND_Y)], fill=OUTLINE)

    # herói pulando
    px = img.load()
    hop = abs(math.sin(phase * 2 * math.pi * 2))
    hy = P_GROUND_Y - len(HERO) * 2 - int(22 * hop)
    blit(px, HERO, HERO_COLORS, 40, hy, 2)

    hud_frame(img, accent)
    d = ImageDraw.Draw(img)
    coins = 18 + int(phase * 4)
    text(px, "COINS", 6, LH - 14, HUD_DIM)
    text(px, str(coins), 6, LH - 7, GOLD)
    text(px, "WORLD", 74, LH - 14, HUD_DIM)
    text(px, "1-4", 74, LH - 7, GOLD)
    text(px, "TIME", LW - 46, LH - 14, HUD_DIM)
    text(px, str(320 - int(phase * 6)), LW - 46, LH - 7, GOLD)
    return img


# ==========================================================================
# 3. BEAT 'EM UP (corredor subterrâneo)
# ==========================================================================
S_WALL_A, S_WALL_B = (38, 48, 62), (30, 39, 52)
S_BRICK = (46, 58, 74)
S_PIPE = (72, 86, 104)
S_WATER_A, S_WATER_B = (34, 96, 108), (26, 78, 90)
S_FLOOR = (54, 62, 78)
S_GRATE = (40, 48, 62)

S_FLOOR_Y = LH - HUD_H - 30

FIGHTER = [   # vulto encapuzado genérico
    "...OOOO...",
    "..OCCCCO..",
    "..OCEECO..",
    "..OCCCCO..",
    ".OOBBBBOO.",
    "OB.BBBB.BO",
    ".B.BBBB.B.",
    "...BBBB...",
    "...O..O...",
    "..OO..OO..",
]
FIGHTER_A = {"O": OUTLINE, "C": (58, 72, 92), "E": (120, 230, 140),
             "B": (34, 197, 94)}
FIGHTER_B = {"O": OUTLINE, "C": (72, 58, 92), "E": (240, 160, 90),
             "B": (150, 96, 60)}


def scene_sewer(phase, accent):
    img = Image.new("RGB", (LW, LH), S_WALL_A)
    d = ImageDraw.Draw(img)
    bands(d, 0, S_FLOOR_Y, S_WALL_A, S_WALL_B, 8)

    off = phase * PERIOD

    # parede em blocos (paralaxe lenta)
    bw, bh = 28, 14
    sx = -int(off * 0.35) % bw - bw
    for row, y in enumerate(range(6, S_FLOOR_Y - 8, bh)):
        stagger = (bw // 2) if row % 2 else 0
        for x in range(sx - bw, LW + bw, bw):
            d.rectangle([x + stagger, y, x + stagger + bw - 2, y + bh - 2],
                        outline=S_BRICK)

    # arcos ao fundo
    for k in range(-1, 3):
        x = 24 + k * PERIOD - off * 0.55
        d.arc([x, S_FLOOR_Y - 54, x + 46, S_FLOOR_Y + 6], 180, 360, fill=S_PIPE,
              width=3)
        d.rectangle([x, S_FLOOR_Y - 30, x + 46, S_FLOOR_Y], outline=S_PIPE)

    # tubulação horizontal correndo pela parede, com braçadeiras
    pipe_y = 34
    d.rectangle([0, pipe_y, LW, pipe_y + 9], fill=S_PIPE)
    d.line([(0, pipe_y), (LW, pipe_y)], fill=(104, 122, 142))
    d.line([(0, pipe_y + 9), (LW, pipe_y + 9)], fill=OUTLINE)
    for k in range(-1, 4):
        bx = int(10 + k * (PERIOD / 2) - off * 0.35)
        d.rectangle([bx, pipe_y - 2, bx + 5, pipe_y + 11], fill=(94, 110, 130))
        d.rectangle([bx, pipe_y - 2, bx + 5, pipe_y + 11], outline=OUTLINE)

    # válvulas e correntes penduradas
    for k in range(-1, 3):
        vx = int(52 + k * PERIOD - off * 0.55)
        d.ellipse([vx - 6, pipe_y - 12, vx + 6, pipe_y], fill=(88, 104, 124))
        d.ellipse([vx - 3, pipe_y - 9, vx + 3, pipe_y - 3], fill=S_WALL_B)
        cx2 = vx + 30
        for cy2 in range(pipe_y + 10, pipe_y + 40, 5):
            d.rectangle([cx2, cy2, cx2 + 2, cy2 + 3], fill=(78, 92, 110))

    # tubulação superior com gotas
    d.rectangle([0, 0, LW, 10], fill=S_PIPE)
    d.line([(0, 10), (LW, 10)], fill=OUTLINE)
    for k in range(-1, 3):
        x = int(18 + k * PERIOD - off * 0.8)
        d.rectangle([x, 2, x + 8, 8], fill=(94, 110, 130))
        drop = (phase * 2 + k * 0.3) % 1.0
        dy = int(10 + drop * (S_FLOOR_Y - 16))
        d.rectangle([x + 3, dy, x + 5, dy + 4], fill=(140, 214, 232))

    # canal de água
    d.rectangle([0, S_FLOOR_Y, LW, S_FLOOR_Y + 10], fill=S_WATER_A)
    for x in range(0, LW, 8):
        wob = int(2 * math.sin((x / 10.0) + phase * 2 * math.pi))
        d.line([(x, S_FLOOR_Y + 4 + wob), (x + 5, S_FLOOR_Y + 4 + wob)],
               fill=S_WATER_B)

    # piso gradeado rolando
    d.rectangle([0, S_FLOOR_Y + 10, LW, LH], fill=S_FLOOR)
    start = -int(off) % TILE - TILE
    for x in range(start, LW + TILE, TILE):
        d.line([(x, S_FLOOR_Y + 10), (x, LH)], fill=S_GRATE)
    for y in range(S_FLOOR_Y + 14, LH, 6):
        d.line([(0, y), (LW, y)], fill=S_GRATE)
    d.line([(0, S_FLOOR_Y + 10), (LW, S_FLOOR_Y + 10)], fill=OUTLINE)

    # dois lutadores genéricos
    px = img.load()
    bobA = int(round(2 * math.sin(phase * 2 * math.pi * 2)))
    bobB = int(round(2 * math.sin(phase * 2 * math.pi * 2 + math.pi)))
    fy = S_FLOOR_Y + 10 - len(FIGHTER) * 2
    blit(px, FIGHTER, FIGHTER_A, 46, fy + bobA, 2)
    blit(px, FIGHTER, FIGHTER_B, 146, fy + bobB, 2, flip=True)

    hud_frame(img, accent)
    d = ImageDraw.Draw(img)
    text(px, "POWER", 6, LH - 14, HUD_DIM)
    hud_bar(d, 6, LH - 8, 60, 6,
            0.75 + 0.2 * math.sin(phase * 2 * math.pi), accent)
    text(px, "SCORE", LW - 62, LH - 14, HUD_DIM)
    text(px, str(24500 + int(phase * 90) * 10), LW - 62, LH - 7, GOLD)
    return img


# ==========================================================================
# 4. AÇÃO URBANA
# ==========================================================================
C_SKY_TOP, C_SKY_LOW = (14, 16, 42), (52, 36, 92)
C_FAR = (28, 32, 66)
C_NEAR = (18, 20, 44)
C_WIN_A, C_WIN_B = (255, 214, 120), (120, 150, 220)
C_ROOF = (34, 38, 58)
C_ROOF_TOP = (58, 64, 88)

C_ROOF_Y = LH - HUD_H - 26

RUNNER = [   # figura de capa genérica
    "...OOOO...",
    "..OWWWWO..",
    "..OWEEWO..",
    "..OWWWWO..",
    ".CCOBBOC..",
    "CC.OBBO.C.",
    "C..OBBO...",
    "...OBBO...",
    "...O..O...",
    "..OO...OO.",
]
RUNNER_COLORS = {"O": OUTLINE, "W": (232, 200, 168), "E": (30, 36, 60),
                 "B": (0, 174, 239), "C": (198, 52, 62)}


def scene_city(phase, accent):
    img = Image.new("RGB", (LW, LH), C_SKY_TOP)
    d = ImageDraw.Draw(img)
    bands(d, 0, C_ROOF_Y, C_SKY_TOP, C_SKY_LOW, 10)

    off = phase * PERIOD

    # lua e estrelas
    d.ellipse([LW - 52, 12, LW - 26, 38], fill=(238, 240, 220))
    d.ellipse([LW - 46, 10, LW - 22, 34], fill=lerp(C_SKY_TOP, C_SKY_LOW, 0.25))
    for i in range(22):
        sx2 = (i * 47) % LW
        sy2 = (i * 29) % max(1, C_ROOF_Y - 30)
        tw = 0.5 + 0.5 * math.sin(phase * 2 * math.pi + i)
        if tw > 0.55:
            d.point((sx2, sy2), fill=(226, 232, 248))

    # skyline distante
    for k in range(-1, 3):
        for bx, bw2, bh2 in ((6, 26, 46), (40, 20, 62), (66, 30, 38),
                             (100, 18, 54)):
            x = bx + k * PERIOD - off * 0.3
            d.rectangle([x, C_ROOF_Y - bh2, x + bw2, C_ROOF_Y], fill=C_FAR)

    # prédios próximos com janelas acesas
    for k in range(-1, 3):
        for bx, bw2, bh2 in ((0, 34, 70), (48, 26, 52), (84, 30, 84)):
            x = bx + k * PERIOD - off * 0.7
            d.rectangle([x, C_ROOF_Y - bh2, x + bw2, C_ROOF_Y], fill=C_NEAR)
            d.rectangle([x, C_ROOF_Y - bh2, x + bw2, C_ROOF_Y], outline=OUTLINE)
            for wy in range(int(C_ROOF_Y - bh2) + 6, int(C_ROOF_Y) - 4, 10):
                for wx in range(int(x) + 5, int(x + bw2) - 4, 9):
                    lit = ((wx * 7 + wy * 3 + k * 11) % 5) != 0
                    if lit:
                        col = C_WIN_A if (wx + wy) % 3 else C_WIN_B
                        d.rectangle([wx, wy, wx + 3, wy + 4], fill=col)

    # telhado rolando
    d.rectangle([0, C_ROOF_Y, LW, LH], fill=C_ROOF)
    d.rectangle([0, C_ROOF_Y, LW, C_ROOF_Y + 4], fill=C_ROOF_TOP)
    start = -int(off) % TILE - TILE
    for x in range(start, LW + TILE, TILE):
        d.line([(x, C_ROOF_Y + 5), (x, LH)], fill=(24, 28, 44))
    d.line([(0, C_ROOF_Y), (LW, C_ROOF_Y)], fill=OUTLINE)

    # figura correndo, com capa tremulando
    px = img.load()
    stride = int(round(2 * math.sin(phase * 2 * math.pi * 3)))
    ry = C_ROOF_Y - len(RUNNER) * 2 + stride
    blit(px, RUNNER, RUNNER_COLORS, 48, ry, 2)

    hud_frame(img, accent)
    d = ImageDraw.Draw(img)
    text(px, "ENERGY", 6, LH - 14, HUD_DIM)
    hud_bar(d, 6, LH - 8, 64, 6,
            0.68 + 0.25 * abs(math.sin(phase * 2 * math.pi)), accent)
    text(px, "SCORE", LW - 62, LH - 14, HUD_DIM)
    text(px, str(31200 + int(phase * 80) * 10), LW - 62, LH - 7, GOLD)
    return img


# ==========================================================================
SCENES = {
    "top-gear-2": (scene_racing, (124, 58, 237)),
    "super-mario-world": (scene_platform, (255, 107, 0)),
    "tmnt-4-turtles-in-time": (scene_sewer, (34, 197, 94)),
    "captain-america-and-the-avengers": (scene_city, (0, 174, 239)),
}


def build(slug):
    render, accent = SCENES[slug]
    frames = [render(f / FRAMES, accent).resize((LW * SCALE, LH * SCALE),
                                                Image.NEAREST)
              for f in range(FRAMES)]
    path = os.path.join(OUT_DIR, f"{slug}-loop.webp")
    frames[0].save(path, "WEBP", save_all=True, append_images=frames[1:],
                   duration=DURATION_MS, loop=0, quality=72, method=6)
    kb = os.path.getsize(path) / 1024
    print(f"  cena   {slug}-loop.webp  {FRAMES} frames  {kb:.0f} KB")
    return os.path.getsize(path)


if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    print("Gerando cenas em pixel art (arte original, convenções de gênero):")
    total = sum(build(s) for s in SCENES)
    print(f"total: {total/1024:.0f} KB")
    print("OK")
