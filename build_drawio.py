#!/usr/bin/env python3
"""Build artwork.drawio from the SAME design spec as render.py.

Per drawio-skill references/xml-authoring.md:
- ids 0/1 are roots, user shapes start at 2, sequential, parent="1"
- no edges in this design (shapes only); birds/horizon are shapes/lines
  drawn as thin rectangles/vertices, so no <mxGeometry relative="1"/> needed
- shapes snapped to whole pixels; fillColor/strokeColor hex; opacity via style
"""
import math
import sys
from pathlib import Path
from xml.sax.saxutils import escape

sys.path.insert(0, str(Path(__file__).resolve().parent))
from render import design, W, H, SUN_CX, SUN_CY, SUN_R, HORIZON_Y  # noqa: E402

OUT = Path(__file__).resolve().parent / "artwork.drawio"

CELL = ('<mxCell id="{id}" value="" style="{style}" vertex="1" parent="1">'
        '<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/>'
        '</mxCell>')


def hx(rgb):
    return "#%02X%02X%02X" % rgb


def main():
    spec = design()
    cells = []
    nid = [2]

    def add(style, x, y, w, h):
        cid = nid[0]
        nid[0] += 1
        cells.append(CELL.format(id=cid, style=escape(style, {'"': '&quot;'}),
                                 x=round(x), y=round(y),
                                 w=max(1, round(w)), h=max(1, round(h))))
        return cid

    # --- sky: gradient rect indigo -> magenta, south ---
    add("rounded=0;html=1;fillColor=#0B1035;gradientColor=#C62B6B;"
        "gradientDirection=south;strokeColor=none;", 0, 0, W, HORIZON_Y)
    # violet mid band (the middle gradient stop)
    add("rounded=0;html=1;fillColor=#3B1F5E;strokeColor=none;opacity=55;",
        0, 200, W, 240)

    # --- stars: rhombus diamonds ---
    for st in spec["stars"]:
        s = st["s"]
        add(f"rhombus;html=1;fillColor={hx(st['color'])};strokeColor=none;"
            f"opacity={round(st['alpha'] / 255 * 100)};",
            st["x"] - s, st["y"] - s, 2 * s, 2 * s)

    # --- corona glow discs (faint filled ellipses) ---
    for r, op in ((262, 6), (232, 10), (204, 19)):
        add(f"ellipse;html=1;fillColor=#FF9A3D;strokeColor=none;opacity={op};",
            SUN_CX - r, SUN_CY - r, 2 * r, 2 * r)

    # --- rays: 12 triangles, rotated to point outward ---
    for ray in spec["rays"]:
        a = ray["angle"]
        mid_r = (ray["r0"] + ray["r1"]) / 2
        mx, my = SUN_CX + math.cos(a) * mid_r, SUN_CY + math.sin(a) * mid_r
        h = ray["r1"] - ray["r0"]
        # draw.io triangle points up; rotation (clockwise deg) to aim along a:
        rot = math.degrees(a) + 90
        add(f"shape=triangle;html=1;fillColor={hx(ray['color'])};"
            f"strokeColor=none;opacity=92;rotation={round(rot, 1)};",
            mx - ray["width"] / 2, my - h / 2, ray["width"], h)

    # --- corona rings ---
    for ring in spec["rings"]:
        r = ring["r"]
        add(f"ellipse;html=1;fillColor=none;strokeColor={hx(ring['color'])};"
            f"strokeWidth={ring['width']};"
            f"opacity={round(ring['alpha'] / 255 * 100)};",
            SUN_CX - r, SUN_CY - r, 2 * r, 2 * r)

    # --- eclipse disk ---
    add("ellipse;html=1;fillColor=#0A0A18;strokeColor=#FF9A3D;strokeWidth=2;",
        SUN_CX - SUN_R, SUN_CY - SUN_R, 2 * SUN_R, 2 * SUN_R)

    # --- mountains: one triangle per peak (union = jagged silhouette) ---
    def mountain_layer(pts, color):
        # pts: [(x,y)...] from (0,720) up over peaks to (1024,720)
        peaks = pts[1:-1]
        for i, (px, py) in enumerate(peaks):
            x0 = pts[i][0]
            x1 = pts[i + 2][0]
            add(f"shape=triangle;html=1;fillColor={hx(color)};strokeColor=none;",
                x0, py, x1 - x0, HORIZON_Y - py)

    mountain_layer(spec["back_mtn"], (0x2A, 0x1B, 0x4E))
    mountain_layer(spec["front_mtn"], (0x14, 0x10, 0x33))

    # --- sea: 8 horizontal gradient bands teal -> deep blue ---
    def lerp(a, b, t):
        return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))

    n_bands = 8
    band_h = (1024 - HORIZON_Y) / n_bands
    for i in range(n_bands):
        c = lerp((0x0E, 0x4A, 0x5A), (0x0A, 0x1E, 0x3F),
                 (i + 0.5) / n_bands)
        add(f"rounded=0;html=1;fillColor={hx(c)};strokeColor=none;",
            0, HORIZON_Y + i * band_h, W, band_h + 1)

    # --- gold reflection streaks ---
    for st in spec["streaks"]:
        add(f"rounded=0;html=1;fillColor=#FFD23D;strokeColor=none;"
            f"opacity={round(st['alpha'] / 255 * 100)};",
            st["x"], st["y"], st["length"], st["h"])

    # --- horizon line: 3px gold rect ---
    add("rounded=0;html=1;fillColor=#FFD23D;strokeColor=none;",
        0, HORIZON_Y - 1, W, 3)

    # --- birds: two thin rotated rectangles per chevron ---
    for b in spec["birds"]:
        x, y, s = b["x"], b["y"], b["s"]
        for sign, rot in ((-1, -25), (1, 25)):
            cx = x + sign * s / 2
            add("rounded=0;html=1;fillColor=#0A0A18;strokeColor=none;"
                f"rotation={rot};", cx - s / 2, y - 2, s, 4)

    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<mxfile host="drawio" version="26.0.0">\n'
           '  <diagram name="Eclipse over the Sea">\n'
           '    <mxGraphModel dx="0" dy="0" grid="1" gridSize="10" '
           'guides="1" tooltips="1" connect="1" arrows="1" fold="1" '
           'page="1" pageScale="1" pageWidth="1024" pageHeight="1024" '
           'math="0" shadow="0" background="#0B1035">\n'
           '      <root>\n'
           '        <mxCell id="0"/>\n'
           '        <mxCell id="1" parent="0"/>\n'
           + "\n".join("        " + c for c in cells) + "\n"
           '      </root>\n'
           '    </mxGraphModel>\n'
           '  </diagram>\n'
           '</mxfile>\n')
    OUT.write_text(xml, encoding="utf-8")
    print(f"{OUT}  {len(cells)} shapes  {OUT.stat().st_size} bytes")


if __name__ == "__main__":
    main()
