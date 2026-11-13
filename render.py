#!/usr/bin/env python3
"""Eclipse over the Sea - make.fun 'coolest art' bounty entry artwork.

Single design spec (seed 42, deterministic, no network) shared by:
  - render.py  -> art.png  (PIL render, this file)
  - build_drawio.py -> artwork.drawio (same spec, draw.io XML)

Canvas: 1024x1024. Output: art.png (PNG, <=1 MiB).
"""
import hashlib
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw

W = H = 1024
SEED = 42

# --- palette ---
INDIGO = (0x0B, 0x10, 0x35)
VIOLET = (0x3B, 0x1F, 0x5E)
MAGENTA = (0xC6, 0x2B, 0x6B)
DARK_DISK = (0x0A, 0x0A, 0x18)
ORANGE = (0xFF, 0x9A, 0x3D)
GOLD = (0xFF, 0xD2, 0x3D)
BACK_MTN = (0x2A, 0x1B, 0x4E)
FRONT_MTN = (0x14, 0x10, 0x33)
TEAL = (0x0E, 0x4A, 0x5A)
DEEP_BLUE = (0x0A, 0x1E, 0x3F)
WHITE = (255, 255, 255)

SUN_CX, SUN_CY, SUN_R = 512, 430, 170
HORIZON_Y = 720
SEA_TOP, SEA_BOTTOM = 720, 1024

OUT = Path(__file__).resolve().parent / "art.png"


def _lerp(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def _hex(rgb):
    return "#%02X%02X%02X" % rgb


def design():
    """Return the full deterministic design spec (seed 42)."""
    rng = random.Random(SEED)

    # --- stars: ~90 diamonds in upper 60% of sky ---
    stars = []
    for _ in range(90):
        x = rng.uniform(8, W - 8)
        y = rng.uniform(8, 614)
        s = rng.uniform(2, 6)
        gold = rng.random() < 0.35
        alpha = rng.randint(140, 255)
        stars.append(dict(x=x, y=y, s=s,
                          color=GOLD if gold else WHITE, alpha=alpha))

    # --- corona: 3 concentric rings + 12 rays ---
    rings = [
        dict(r=188, color=ORANGE, alpha=220, width=7),
        dict(r=210, color=GOLD, alpha=150, width=5),
        dict(r=236, color=ORANGE, alpha=80, width=4),
    ]
    rays = []
    for i in range(12):
        ang = 2 * math.pi * i / 12 + math.pi / 12  # offset so none is straight up
        rays.append(dict(angle=ang, r0=248, r1=306,
                         color=GOLD if i % 2 == 0 else ORANGE,
                         width=13, alpha=235))

    # --- mountains: jagged layers, baseline at horizon ---
    def peaks(n, y_lo, y_hi):
        xs = [0.0]
        for _ in range(n - 1):
            xs.append(xs[-1] + W / n + rng.uniform(-30, 30))
        xs.append(float(W))
        pts = [(0.0, HORIZON_Y)]
        for i, x in enumerate(xs[1:-1], start=1):
            pts.append((x, rng.uniform(y_lo, y_hi)))
        pts.append((float(W), HORIZON_Y))
        return pts

    back_mtn = peaks(8, 560, 640)
    front_mtn = peaks(9, 620, 685)

    # --- sea reflection streaks under the sun ---
    streaks = []
    for _ in range(14):
        cx = rng.uniform(380, 640)
        length = rng.uniform(40, 200)
        y = rng.uniform(735, 1000)
        alpha = rng.randint(90, 230)
        streaks.append(dict(x=cx - length / 2, y=y, length=length,
                            h=rng.uniform(2.5, 4.5), alpha=alpha))

    # --- birds: 5 chevrons in upper sky ---
    birds = []
    for _ in range(5):
        birds.append(dict(x=rng.uniform(150, 850),
                          y=rng.uniform(180, 300),
                          s=rng.uniform(14, 22)))

    return dict(stars=stars, rings=rings, rays=rays,
                back_mtn=back_mtn, front_mtn=front_mtn,
                streaks=streaks, birds=birds)


def render(spec):
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)

    # --- sky: vertical gradient indigo -> violet -> magenta (0..640),
    #     holding magenta down to the horizon (720) ---
    for y in range(HORIZON_Y + 1):
        if y <= 320:
            c = _lerp(INDIGO, VIOLET, y / 320)
        elif y <= 640:
            c = _lerp(VIOLET, MAGENTA, (y - 320) / 320)
        else:
            c = MAGENTA
        d.line([(0, y), (W, y)], fill=c)

    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)

    # --- stars ---
    for st in spec["stars"]:
        x, y, s = st["x"], st["y"], st["s"]
        od.polygon([(x, y - s), (x + s, y), (x, y + s), (x - s, y)],
                   fill=st["color"] + (st["alpha"],))

    # --- corona soft glow (translucent filled discs) ---
    for r, a in ((262, 14), (232, 26), (204, 48)):
        od.ellipse([SUN_CX - r, SUN_CY - r, SUN_CX + r, SUN_CY + r],
                   fill=ORANGE + (a,))

    # --- rays (triangles radiating outward) ---
    for ray in spec["rays"]:
        a = ray["angle"]
        dx, dy = math.cos(a), math.sin(a)
        px, py = -dy, dx  # perpendicular
        tip = (SUN_CX + dx * ray["r1"], SUN_CY + dy * ray["r1"])
        b1 = (SUN_CX + dx * ray["r0"] + px * ray["width"] / 2,
              SUN_CY + dy * ray["r0"] + py * ray["width"] / 2)
        b2 = (SUN_CX + dx * ray["r0"] - px * ray["width"] / 2,
              SUN_CY + dy * ray["r0"] - py * ray["width"] / 2)
        od.polygon([tip, b1, b2], fill=ray["color"] + (ray["alpha"],))

    # --- corona rings ---
    for ring in spec["rings"]:
        r = ring["r"]
        od.ellipse([SUN_CX - r, SUN_CY - r, SUN_CX + r, SUN_CY + r],
                   outline=ring["color"] + (ring["alpha"],),
                   width=ring["width"])

    # --- eclipse disk ---
    od.ellipse([SUN_CX - SUN_R, SUN_CY - SUN_R,
                SUN_CX + SUN_R, SUN_CY + SUN_R], fill=DARK_DISK + (255,))

    img = Image.alpha_composite(img.convert("RGBA"), ov)
    d = ImageDraw.Draw(img)

    # --- mountains (polygons, baseline at horizon) ---
    d.polygon(spec["back_mtn"], fill=BACK_MTN + (255,))
    d.polygon(spec["front_mtn"], fill=FRONT_MTN + (255,))

    # --- sea: vertical gradient teal -> deep blue ---
    for y in range(SEA_TOP, SEA_BOTTOM):
        c = _lerp(TEAL, DEEP_BLUE, (y - SEA_TOP) / (SEA_BOTTOM - SEA_TOP))
        d.line([(0, y), (W, y)], fill=c)

    # --- gold reflection streaks ---
    ov2 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od2 = ImageDraw.Draw(ov2)
    for st in spec["streaks"]:
        od2.rectangle([st["x"], st["y"], st["x"] + st["length"],
                       st["y"] + st["h"]], fill=GOLD + (st["alpha"],))
    img = Image.alpha_composite(img, ov2)
    d = ImageDraw.Draw(img)

    # --- horizon line, 3px gold ---
    d.rectangle([0, HORIZON_Y - 1, W, HORIZON_Y + 1], fill=GOLD)

    # --- birds (dark chevrons, two short angled strokes each) ---
    for b in spec["birds"]:
        x, y, s = b["x"], b["y"], b["s"]
        d.line([(x - s, y - s * 0.45), (x, y), (x + s, y - s * 0.45)],
               fill=(10, 10, 24), width=3)

    return img.convert("RGB")


def main():
    img = render(design())
    img.save(OUT, format="PNG", optimize=True)
    data = OUT.read_bytes()
    print(f"{OUT}  {img.size[0]}x{img.size[1]}  {len(data)} bytes")
    print("sha256:", hashlib.sha256(data).hexdigest())


if __name__ == "__main__":
    main()
