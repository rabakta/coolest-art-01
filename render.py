#!/usr/bin/env python3
"""Phoenix Rising - make.fun 'coolest art' bounty entry artwork v2.

Single design spec (seed 42, deterministic, no network) shared by:
  - render.py  -> art.png  (PIL render, this file)
  - build_drawio.py -> artwork.drawio (same spec, draw.io XML)

Canvas: 1024x1024. Output: art.png (PNG, <=1 MiB).
A phoenix with spread wings rising from flames: gold/orange/red fire
against a deep indigo-crimson night sky, pale moon, rising embers.
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
CRIMSON_DARK = (0x2A, 0x0A, 0x18)
EMBER_DARK = (0x3A, 0x0E, 0x08)
DEEP_RED = (0x8B, 0x0E, 0x0E)
RED = (0xC8, 0x1E, 0x1E)
ORANGE = (0xFF, 0x6B, 0x1A)
BRIGHT_ORANGE = (0xFF, 0x9A, 0x3D)
GOLD = (0xFF, 0xC2, 0x3D)
PALE_YELLOW = (0xFF, 0xE8, 0x8A)
MOON = (0xFF, 0xF0, 0xC8)
WHITE = (255, 255, 255)
DARK = (0x0A, 0x06, 0x12)

SHOULDER_L = (462, 500)
SHOULDER_R = (562, 500)
MOON_CX, MOON_CY, MOON_R = 800, 165, 58
RIDGE_Y = 940

OUT = Path(__file__).resolve().parent / "art.png"


def _lerp(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def _hex(rgb):
    return "#%02X%02X%02X" % rgb


def _feather(base, angle_deg, length, width, color, alpha):
    """A tapered feather quad from base along angle (deg, PIL coords y down)."""
    a = math.radians(angle_deg)
    dx, dy = math.cos(a), math.sin(a)
    px, py = -dy, dx
    tip = (base[0] + dx * length, base[1] + dy * length)
    b1 = (base[0] + px * width / 2, base[1] + py * width / 2)
    b2 = (base[0] - px * width / 2, base[1] - py * width / 2)
    t1 = (tip[0] + px * 3, tip[1] + py * 3)
    t2 = (tip[0] - px * 3, tip[1] - py * 3)
    return dict(poly=[tip, b1, b2], tip=tip, color=color, alpha=alpha,
                width=width, angle=angle_deg)


def design():
    """Return the full deterministic design spec (seed 42)."""
    rng = random.Random(SEED)

    # --- stars: ~55 diamonds in upper sky ---
    stars = []
    for _ in range(55):
        x = rng.uniform(8, W - 8)
        y = rng.uniform(8, 560)
        s = rng.uniform(2, 5.5)
        gold = rng.random() < 0.4
        alpha = rng.randint(130, 255)
        stars.append(dict(x=x, y=y, s=s,
                          color=GOLD if gold else WHITE, alpha=alpha))

    # --- embers: ~70 glowing dots rising across the canvas ---
    embers = []
    for _ in range(70):
        embers.append(dict(x=rng.uniform(20, W - 20),
                           y=rng.uniform(120, 1000),
                           r=rng.uniform(1.5, 4.5),
                           color=rng.choice([GOLD, BRIGHT_ORANGE, ORANGE]),
                           alpha=rng.randint(120, 255)))

    # --- wings: 3 layers x 7 feathers per side, fanning up-out ---
    # layer colors: inner deep red -> red -> orange -> gold tips
    layer_colors = [DEEP_RED, RED, ORANGE, BRIGHT_ORANGE, GOLD]
    feathers = []
    for side, shoulder in ((-1, SHOULDER_L), (1, SHOULDER_R)):
        for layer in range(3):
            for i in range(9):
                # fan: left wing 188..260 deg, right wing -80..-8 deg
                if side < 0:
                    ang = 188 + i * 9 + layer * 3
                else:
                    ang = -80 - i * 9 - layer * 3
                length = 310 - layer * 55 - abs(i - 4) * 16 + rng.uniform(-8, 8)
                width = 62 - layer * 10
                color = layer_colors[min(1 + layer + (1 if i in (0, 8) else 0), 4)]
                feathers.append(_feather(shoulder, ang, length, width,
                                         color, 235))

    # --- tail ribbons: 5 wavy flame ribbons flowing down from tail base ---
    ribbons = []
    for k in range(5):
        spread = (k - 2) * 30
        phase = rng.uniform(0, 6.28)
        amp = rng.uniform(30, 55)
        length = rng.uniform(300, 380)
        color = [RED, ORANGE, BRIGHT_ORANGE, GOLD, ORANGE][k]
        ribbons.append(dict(x0=512 + spread, y0=600, length=length,
                            phase=phase, amp=amp, color=color))

    # --- ground flames: ~16 tongues along the bottom ridge ---
    flames = []
    for i in range(16):
        x = 40 + i * 60 + rng.uniform(-14, 14)
        h = rng.uniform(50, 130)
        w = rng.uniform(34, 52)
        color = rng.choice([RED, ORANGE, BRIGHT_ORANGE, GOLD])
        flames.append(dict(x=x, h=h, w=w, color=color))

    # --- ridge: jagged dark rock silhouette at the bottom ---
    def peaks(n, y_lo, y_hi):
        xs = [0.0]
        for _ in range(n - 1):
            xs.append(xs[-1] + W / n + rng.uniform(-30, 30))
        xs.append(float(W))
        pts = [(0.0, float(H))]
        for i, x in enumerate(xs[1:-1], start=1):
            pts.append((x, rng.uniform(y_lo, y_hi)))
        pts.append((float(W), float(H)))
        return pts

    ridge = peaks(9, 900, 960)

    return dict(stars=stars, embers=embers, feathers=feathers,
                ribbons=ribbons, flames=flames, ridge=ridge)


def _body_poly():
    """Phoenix body: elegant S-curve teardrop, head at top, tail at bottom."""
    # body outline (x, y) clockwise from neck
    return [(512, 330), (536, 360), (548, 420), (545, 490), (530, 560),
            (512, 610), (494, 560), (479, 490), (476, 420), (488, 360)]


def render(spec):
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)

    # --- sky: vertical gradient indigo -> crimson -> ember dark ---
    for y in range(H):
        if y <= 380:
            c = _lerp(INDIGO, CRIMSON_DARK, y / 380)
        else:
            c = _lerp(CRIMSON_DARK, EMBER_DARK, (y - 380) / (H - 380))
        d.line([(0, y), (W, y)], fill=c)

    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)

    # --- stars ---
    for st in spec["stars"]:
        x, y, s = st["x"], st["y"], st["s"]
        od.polygon([(x, y - s), (x + s, y), (x, y + s), (x - s, y)],
                   fill=st["color"] + (st["alpha"],))

    # --- moon glow + disc (upper right) ---
    for r, a in ((110, 12), (84, 22), (66, 40)):
        od.ellipse([MOON_CX - r, MOON_CY - r, MOON_CX + r, MOON_CY + r],
                   fill=MOON + (a,))
    od.ellipse([MOON_CX - MOON_R, MOON_CY - MOON_R,
                MOON_CX + MOON_R, MOON_CY + MOON_R], fill=MOON + (255,))
    # moon shadow craters
    for cx, cy, r in ((776, 148, 10), (822, 182, 13), (790, 190, 7)):
        od.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(0xE8, 0xD8, 0xB0, 90))

    # --- fire glow behind the phoenix ---
    for r, a in ((330, 14), (280, 24), (225, 40)):
        od.ellipse([512 - r, 480 - r, 512 + r, 480 + r], fill=ORANGE + (a,))

    # --- wing bases: solid fan silhouettes behind the feathers ---
    for side, shoulder in ((-1, SHOULDER_L), (1, SHOULDER_R)):
        tips = []
        for f in spec["feathers"]:
            # layer-0 feathers of this side: longest, define the fan edge
            if f["width"] > 60 and ((side < 0) == (f["angle"] > 90)):
                tips.append(f["tip"])
        tips.sort(key=lambda p: math.atan2(p[1] - shoulder[1],
                                           p[0] - shoulder[0]))
        if len(tips) >= 3:
            od.polygon([shoulder] + tips, fill=DEEP_RED + (255,))

    # --- tail ribbons: wavy bands of overlapping circles ---
    for rb in spec["ribbons"]:
        steps = 26
        for i in range(steps):
            t = i / (steps - 1)
            y = rb["y0"] + t * rb["length"]
            x = rb["x0"] + math.sin(t * 4.2 + rb["phase"]) * rb["amp"] * t
            r = 12 * (1 - t * 0.6) + 3
            od.ellipse([x - r, y - r, x + r, y + r],
                       fill=rb["color"] + (235,))

    # --- wings: feathers back layer first (layer 0 deepest) ---
    for f in spec["feathers"]:
        od.polygon(f["poly"], fill=f["color"] + (f["alpha"],))
        # pale tip dot at feather tip
        tx, ty = f["tip"]
        od.ellipse([tx - 4, ty - 4, tx + 4, ty + 4],
                   fill=PALE_YELLOW + (200,))

    # --- body: gold-orange teardrop with red chest ---
    body = _body_poly()
    od.polygon(body, fill=BRIGHT_ORANGE + (255,))
    # chest highlight
    od.ellipse([492, 400, 532, 520], fill=GOLD + (255,))
    # belly shadow
    od.polygon([(512, 610), (530, 560), (545, 490), (530, 540), (512, 585),
                (494, 540), (479, 490)], fill=RED + (180,))

    # --- head: crest + beak + eye ---
    # crest: 3 thin flame feathers sweeping back from the head
    for dx, ln, col in ((-14, 46, GOLD), (-4, 56, BRIGHT_ORANGE), (8, 44, GOLD)):
        od.polygon([(512 + dx, 338), (512 + dx - 8, 338 - ln),
                    (512 + dx + 8, 338 - ln)],
                   fill=col + (255,))
    od.ellipse([494, 320, 530, 356], fill=GOLD + (255,))  # head
    od.polygon([(528, 334), (554, 342), (528, 350)], fill=ORANGE + (255,))  # beak
    od.ellipse([516, 332, 523, 339], fill=WHITE + (255,))  # eye
    od.ellipse([518, 334, 521, 337], fill=DARK + (255,))   # pupil

    img = Image.alpha_composite(img.convert("RGBA"), ov)
    d = ImageDraw.Draw(img)

    # --- ridge: dark rock silhouette ---
    d.polygon(spec["ridge"], fill=DARK + (255,))

    # --- ground flames: tongues rising from the ridge ---
    ov2 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od2 = ImageDraw.Draw(ov2)
    for fl in spec["flames"]:
        x, h, w = fl["x"], fl["h"], fl["w"]
        base_y = 1010
        od2.polygon([(x - w / 2, base_y), (x, base_y - h),
                     (x + w / 2, base_y)], fill=fl["color"] + (235,))
        od2.polygon([(x - w / 4, base_y), (x, base_y - h * 0.62),
                     (x + w / 4, base_y)], fill=PALE_YELLOW + (220,))
    # embers rising
    for em in spec["embers"]:
        r = em["r"]
        od2.ellipse([em["x"] - r, em["y"] - r, em["x"] + r, em["y"] + r],
                    fill=em["color"] + (em["alpha"],))
    img = Image.alpha_composite(img, ov2)

    return img.convert("RGB")


def main():
    img = render(design())
    img.save(OUT, format="PNG", optimize=True)
    data = OUT.read_bytes()
    print(f"{OUT}  {img.size[0]}x{img.size[1]}  {len(data)} bytes")
    print("sha256:", hashlib.sha256(data).hexdigest())


if __name__ == "__main__":
    main()
