#!/usr/bin/env python3
"""Fly Me to the Moon - make.fun 'coolest art' bounty entry artwork v2.

Retro-futuristic 1950s-60s "atomic age" poster: big bold typography,
a ringed Saturn, a red vintage car flying through space, a couple on a
tiled plaza, vintage cars, starry sky. Palette: cream, red, teal,
mustard, indigo.

Single design spec (seed 42, deterministic, no network) shared by:
  - render.py  -> art.png  (PIL render, this file)
  - build_drawio.py -> artwork.drawio (same spec, draw.io XML)

Canvas: 1024x1024. Output: art.png (PNG, <=1 MiB).
"""
import hashlib
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
SEED = 42

# --- palette ---
CREAM = (0xF5, 0xE9, 0xC8)
RED = (0xC8, 0x1E, 0x1E)
RED_BRIGHT = (0xD4, 0x2B, 0x1E)
TEAL = (0x1E, 0x7A, 0x6B)
TEAL_LIGHT = (0x2A, 0x9D, 0x8F)
MUSTARD = (0xE8, 0xA8, 0x1C)
GOLD = (0xFF, 0xD2, 0x3D)
ORANGE = (0xFF, 0x6B, 0x1A)
INDIGO = (0x0B, 0x10, 0x35)
NIGHT = (0x08, 0x08, 0x16)
SKY_LOW = (0x14, 0x1E, 0x3F)
DARK_NAVY = (0x14, 0x14, 0x30)
DARK = (0x0A, 0x06, 0x12)
WHITE = (255, 255, 255)
GLASS = (0x1A, 0x3A, 0x44)

FONT_BOLD = "/usr/share/fonts/truetype/noto/NotoSans-CondensedBold.ttf"

SATURN_CX, SATURN_CY, SATURN_R = 370, 270, 215
PLAZA_TOP = 780

OUT = Path(__file__).resolve().parent / "art.png"


def _lerp(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def _hex(rgb):
    return "#%02X%02X%02X" % rgb


def _font(size):
    return ImageFont.truetype(FONT_BOLD, size)


def design():
    """Return the full deterministic design spec (seed 42)."""
    rng = random.Random(SEED)

    # --- stars: ~85 diamonds across the sky ---
    stars = []
    for _ in range(85):
        x = rng.uniform(8, W - 8)
        y = rng.uniform(8, 760)
        s = rng.uniform(2, 6)
        gold = rng.random() < 0.35
        alpha = rng.randint(130, 255)
        stars.append(dict(x=x, y=y, s=s,
                          color=GOLD if gold else WHITE, alpha=alpha))

    # --- sparkles: 6 big 4-point stars ---
    sparkles = []
    for _ in range(6):
        sparkles.append(dict(x=rng.uniform(60, 960), y=rng.uniform(60, 700),
                             s=rng.uniform(10, 18)))

    # --- plaza tiles: 4 rows x 10 cols, alternating cream / mustard ---
    tiles = []
    rows = [(780, 820), (820, 875), (875, 950), (950, 1024)]
    for ri, (y0, y1) in enumerate(rows):
        for ci in range(10):
            x0 = ci * 102.4
            x1 = (ci + 1) * 102.4
            color = CREAM if (ri + ci) % 2 == 0 else MUSTARD
            tiles.append(dict(x0=x0, y0=y0, x1=x1, y1=y1, color=color))

    return dict(stars=stars, sparkles=sparkles, tiles=tiles)


def _draw_car(d, x, y, length, body, facing=1):
    """Simple 1950s car side profile, nose pointing `facing` (+1 right, -1 left).

    (x, y) is the top-left of the car's bounding box; height ~ length*0.42.
    Drawn facing right; mirrored when facing == -1.
    """
    h = length * 0.42
    # work in local coords, mirror by transforming x
    def X(lx):
        return x + (lx if facing > 0 else length - lx)

    # body: rounded silhouette with tail fin at the rear
    d.rounded_rectangle([min(X(0), X(length)), y + h * 0.28,
                         max(X(0), X(length)), y + h * 0.82],
                        radius=int(h * 0.16), fill=body + (255,))
    # tail fin (rear top)
    rear_x = X(length) if facing > 0 else X(0)
    d.polygon([(rear_x, y + h * 0.30),
               (rear_x + (18 if facing > 0 else -18) * 1, y + h * 0.02),
               (rear_x + (44 if facing > 0 else -44), y + h * 0.30)],
              fill=body + (255,))
    # cabin (greenhouse)
    d.polygon([(X(length * 0.30), y + h * 0.30),
               (X(length * 0.38), y + h * 0.02),
               (X(length * 0.62), y + h * 0.02),
               (X(length * 0.72), y + h * 0.30)],
              fill=GLASS + (255,))
    # chrome stripe
    d.rectangle([min(X(0), X(length)) + 4, y + h * 0.58,
                 max(X(0), X(length)) - 4, y + h * 0.63],
                fill=CREAM + (255,))
    # headlight (front)
    fx = X(2)
    d.ellipse([fx - 7, y + h * 0.42, fx + 7, y + h * 0.56],
              fill=(0xFF, 0xF0, 0xC8, 255))
    # wheels
    for wx in (length * 0.24, length * 0.76):
        cx = X(wx)
        d.ellipse([cx - h * 0.17, y + h * 0.72, cx + h * 0.17, y + h * 1.06],
                  fill=DARK + (255,))
        d.ellipse([cx - h * 0.07, y + h * 0.82, cx + h * 0.07, y + h * 0.96],
                  fill=CREAM + (255,))


def _draw_rocket(angle):
    """Small rocket with flame, on its own layer, rotated `angle` deg."""
    lay = Image.new("RGBA", (260, 260), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay)
    cx = 130
    # flame
    ld.polygon([(cx - 16, 196), (cx, 248), (cx + 16, 196)],
               fill=ORANGE + (255,))
    ld.polygon([(cx - 8, 196), (cx, 228), (cx + 8, 196)],
               fill=(0xFF, 0xE8, 0x8A, 255))
    # fins
    ld.polygon([(cx - 18, 150), (cx - 34, 196), (cx - 14, 196)],
               fill=RED + (255,))
    ld.polygon([(cx + 18, 150), (cx + 34, 196), (cx + 14, 196)],
               fill=RED + (255,))
    # body
    ld.rounded_rectangle([cx - 18, 60, cx + 18, 196], radius=18,
                         fill=CREAM + (255,))
    # nose cone
    ld.polygon([(cx - 18, 62), (cx, 14), (cx + 18, 62)], fill=RED + (255,))
    # window
    ld.ellipse([cx - 9, 92, cx + 9, 110], fill=TEAL + (255,))
    rot = lay.rotate(angle, expand=True, resample=Image.BICUBIC)
    return rot


def render(spec):
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)

    # --- sky: vertical gradient night -> indigo -> deep blue ---
    for y in range(PLAZA_TOP + 1):
        if y <= 380:
            c = _lerp(NIGHT, INDIGO, y / 380)
        else:
            c = _lerp(INDIGO, SKY_LOW, (y - 380) / (PLAZA_TOP - 380))
        d.line([(0, y), (W, y)], fill=c)

    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)

    # --- stars ---
    for st in spec["stars"]:
        x, y, s = st["x"], st["y"], st["s"]
        od.polygon([(x, y - s), (x + s, y), (x, y + s), (x - s, y)],
                   fill=st["color"] + (st["alpha"],))
    # --- sparkles: 4-point stars ---
    for sp in spec["sparkles"]:
        x, y, s = sp["x"], sp["y"], sp["s"]
        od.polygon([(x, y - s), (x + s * 0.28, y - s * 0.28), (x + s, y),
                    (x + s * 0.28, y + s * 0.28), (x, y + s),
                    (x - s * 0.28, y + s * 0.28), (x - s, y),
                    (x - s * 0.28, y - s * 0.28)],
                   fill=WHITE + (230,))

    # --- horizon glow ---
    for r, a in ((300, 12), (220, 20)):
        od.ellipse([512 - r, 780 - r, 512 + r, 780 + r],
                   fill=MUSTARD + (a,))

    # --- Saturn back rings (behind the disc) ---
    ring_lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rd = ImageDraw.Draw(ring_lay)
    for r, col, wdt in ((300, MUSTARD, 12), (330, CREAM, 10),
                        (360, RED_BRIGHT, 8)):
        rd.ellipse([SATURN_CX - r, SATURN_CY - 52, SATURN_CX + r,
                    SATURN_CY + 52], outline=col + (235,), width=wdt)
    ring_lay = ring_lay.rotate(-18, resample=Image.BICUBIC, center=(SATURN_CX, SATURN_CY))
    ov = Image.alpha_composite(ov, ring_lay)
    od = ImageDraw.Draw(ov)

    # --- Saturn disc + bands ---
    od.ellipse([SATURN_CX - SATURN_R, SATURN_CY - SATURN_R,
                SATURN_CX + SATURN_R, SATURN_CY + SATURN_R],
               fill=CREAM + (255,))
    for (by, bh, col, al) in ((200, 26, MUSTARD, 110), (260, 34, RED_BRIGHT, 70),
                              (330, 22, MUSTARD, 90)):
        od.ellipse([SATURN_CX - SATURN_R, by - bh // 2,
                    SATURN_CX + SATURN_R, by + bh // 2],
                   fill=col + (al,))

    # --- Saturn front rings (lower arc only, in front of the disc) ---
    fring = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(fring)
    for r, col, wdt in ((300, MUSTARD, 12), (330, CREAM, 10),
                        (360, RED_BRIGHT, 8)):
        fd.arc([SATURN_CX - r, SATURN_CY - 52, SATURN_CX + r,
                SATURN_CY + 52], start=0, end=180,
               fill=col + (235,), width=wdt)
    fring = fring.rotate(-18, resample=Image.BICUBIC, center=(SATURN_CX, SATURN_CY))
    ov = Image.alpha_composite(ov, fring)
    od = ImageDraw.Draw(ov)

    # --- flying red car (own layer, rotated) ---
    car_lay = Image.new("RGBA", (420, 200), (0, 0, 0, 0))
    cd = ImageDraw.Draw(car_lay)
    _draw_car(cd, 60, 50, 280, RED_BRIGHT, facing=-1)
    # motion streaks behind the car (to its right, it flies left)
    for i, (sy, ln) in enumerate(((70, 90), (100, 120), (130, 80))):
        cd.line([(350, sy), (350 + ln, sy)], fill=CREAM + (200,), width=5)
    car_lay = car_lay.rotate(-14, expand=True, resample=Image.BICUBIC)
    ov.paste(car_lay, (560, 90), car_lay)

    # --- rocket (own layer, rotated up-right) ---
    rock = _draw_rocket(38)
    ov.paste(rock, (750, 370), rock)

    img = Image.alpha_composite(img.convert("RGBA"), ov)
    d = ImageDraw.Draw(img)

    # --- plaza: checkered tiles ---
    for t in spec["tiles"]:
        d.rectangle([t["x0"], t["y0"], t["x1"], t["y1"]],
                    fill=t["color"] + (255,))
    # grout lines
    for y0, y1 in ((780, 820), (820, 875), (875, 950), (950, 1024)):
        d.line([(0, y0), (W, y0)], fill=DARK_NAVY, width=2)
    for ci in range(11):
        d.line([(ci * 102.4, 780), (ci * 102.4, 1024)], fill=DARK_NAVY, width=2)

    # --- couple silhouette on the plaza ---
    # man (hat, suit) at ~(330, 880), woman (dress) at ~(372, 888)
    d.ellipse([322, 868, 338, 884], fill=DARK_NAVY + (255,))          # man head
    d.rectangle([312, 868, 348, 874], fill=DARK_NAVY + (255,))         # hat brim
    d.rectangle([320, 858, 340, 868], fill=DARK_NAVY + (255,))         # hat top
    d.polygon([(318, 884), (342, 884), (346, 970), (314, 970)],
              fill=DARK_NAVY + (255,))                                 # man suit
    d.ellipse([366, 876, 380, 890], fill=DARK_NAVY + (255,))          # woman head
    d.ellipse([372, 870, 382, 880], fill=DARK_NAVY + (255,))          # hair bun
    d.polygon([(364, 890), (382, 890), (392, 970), (354, 970)],
              fill=DARK_NAVY + (255,))                                 # woman dress

    # --- parked vintage cars (bottom right) ---
    ov2 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od2 = ImageDraw.Draw(ov2)
    _draw_car(od2, 660, 880, 170, TEAL, facing=1)
    _draw_car(od2, 780, 920, 160, CREAM, facing=-1)
    img = Image.alpha_composite(img, ov2)
    d = ImageDraw.Draw(img)

    # --- typography: FLY / ME TO THE / MOON (over sky AND plaza, poster style) ---
    tv = Image.new("RGBA", (W, H), (0, 0, 0, 0))

    def text_block(txt, size, color, x, y, rot=0):
        f = _font(size)
        lay = Image.new("RGBA", (780, 320), (0, 0, 0, 0))
        ld = ImageDraw.Draw(lay)
        ld.text((8, 8), txt, font=f, fill=DARK_NAVY + (255,))
        ld.text((4, 4), txt, font=f, fill=color + (255,))
        if rot:
            lay = lay.rotate(rot, expand=True, resample=Image.BICUBIC)
        tv.paste(lay, (x, y), lay)

    text_block("FLY", 230, CREAM, 40, 350, rot=-1)
    text_block("ME TO THE", 64, TEAL_LIGHT, 52, 572, rot=-1)
    text_block("MOON", 210, TEAL_LIGHT, 40, 625, rot=-1)
    img = Image.alpha_composite(img, tv)
    d = ImageDraw.Draw(img)

    # --- cream poster border ---
    d.rectangle([0, 0, W - 1, H - 1], outline=CREAM, width=18)

    return img.convert("RGB")


def main():
    img = render(design())
    img.save(OUT, format="PNG", optimize=True)
    data = OUT.read_bytes()
    print(f"{OUT}  {img.size[0]}x{img.size[1]}  {len(data)} bytes")
    print("sha256:", hashlib.sha256(data).hexdigest())


if __name__ == "__main__":
    main()
