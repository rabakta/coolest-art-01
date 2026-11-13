#!/usr/bin/env python3
"""Build artwork.drawio from the SAME design spec as render.py (v2 poster).

Retro "Fly Me to the Moon" atomic-age poster: Saturn, flying red car,
rocket, big typography, tiled plaza, couple, parked cars.

Per drawio-skill references/xml-authoring.md:
- ids 0/1 are roots, user shapes start at 2, sequential, parent="1"
- no edges in this design (shapes + text cells only)
- shapes snapped to whole pixels; fillColor/strokeColor hex; opacity via style
"""
import math
import sys
from pathlib import Path
from xml.sax.saxutils import escape

sys.path.insert(0, str(Path(__file__).resolve().parent))
from render import design, W, H, SATURN_CX, SATURN_CY, SATURN_R, PLAZA_TOP  # noqa: E402

OUT = Path(__file__).resolve().parent / "artwork.drawio"

CELL = ('<mxCell id="{id}" value="{value}" style="{style}" vertex="1" parent="1">'
        '<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/>'
        '</mxCell>')


def hx(rgb):
    return "#%02X%02X%02X" % rgb


def main():
    spec = design()
    cells = []
    nid = [2]

    def add(style, x, y, w, h, value=""):
        cid = nid[0]
        nid[0] += 1
        cells.append(CELL.format(
            id=cid, value=escape(value),
            style=escape(style, {'"': '&quot;'}),
            x=round(x), y=round(y),
            w=max(1, round(w)), h=max(1, round(h))))
        return cid

    # --- sky: gradient rect night -> indigo, south ---
    add("rounded=0;html=1;fillColor=#080816;gradientColor=#0B1035;"
        "gradientDirection=south;strokeColor=none;", 0, 0, W, PLAZA_TOP)

    # --- stars: rhombus diamonds ---
    for st in spec["stars"]:
        s = st["s"]
        add(f"rhombus;html=1;fillColor={hx(st['color'])};strokeColor=none;"
            f"opacity={round(st['alpha'] / 255 * 100)};",
            st["x"] - s, st["y"] - s, 2 * s, 2 * s)
    # --- sparkles: larger rhombi ---
    for sp in spec["sparkles"]:
        s = sp["s"]
        add("rhombus;html=1;fillColor=#FFFFFF;strokeColor=none;opacity=90;",
            sp["x"] - s, sp["y"] - s, 2 * s, 2 * s)

    # --- Saturn back rings: rotated ellipse outlines ---
    for r, col, wdt in ((300, "#E8A81C", 12), (330, "#F5E9C8", 10),
                        (360, "#D42B1E", 8)):
        add(f"ellipse;html=1;fillColor=none;strokeColor={col};"
            f"strokeWidth={wdt};rotation=-18;opacity=92;",
            SATURN_CX - r, SATURN_CY - 52, 2 * r, 104)

    # --- Saturn disc + bands ---
    add("ellipse;html=1;fillColor=#F5E9C8;strokeColor=none;",
        SATURN_CX - SATURN_R, SATURN_CY - SATURN_R, 2 * SATURN_R, 2 * SATURN_R)
    for (by, bh, col, al) in ((200, 26, "#E8A81C", 43), (260, 34, "#D42B1E", 27),
                              (330, 22, "#E8A81C", 35)):
        add(f"ellipse;html=1;fillColor={col};strokeColor=none;opacity={al};",
            SATURN_CX - SATURN_R, by - bh // 2, 2 * SATURN_R, bh)

    # --- Saturn front rings: rotated thin rects across the disc's lower third ---
    for (ry, col, wdt) in ((330, "#E8A81C", 12), (352, "#F5E9C8", 10),
                           (374, "#D42B1E", 8)):
        add(f"rounded=0;html=1;fillColor={col};strokeColor=none;"
            f"opacity=92;rotation=-18;",
            SATURN_CX - 340, ry - wdt // 2, 680, wdt)

    # --- flying red car (each part rotated -14 about its own center) ---
    CAR_X, CAR_Y = 620, 140
    def car_part(style, x, y, w, h, rot=0):
        s = style + (f";rotation={rot}" if rot else "")
        add(s, CAR_X + x, CAR_Y + y, w, h)

    car_part("rounded=1;html=1;fillColor=#D42B1E;strokeColor=none;arcSize=12;",
             0, 28, 280, 60, rot=-14)
    car_part("shape=triangle;html=1;fillColor=#D42B1E;strokeColor=none;",
             236, 8, 44, 30, rot=-14)
    car_part("shape=trapezoid;html=1;fillColor=#1A3A44;strokeColor=none;",
             90, 2, 90, 30, rot=-14)
    car_part("rounded=0;html=1;fillColor=#F5E9C8;strokeColor=none;",
             4, 58, 272, 5, rot=-14)
    car_part("ellipse;html=1;fillColor=#FFF0C8;strokeColor=none;",
             -2, 42, 14, 14, rot=-14)
    for wx in (67, 213):
        car_part("ellipse;html=1;fillColor=#0A0612;strokeColor=none;",
                 wx - 16, 72, 32, 32, rot=-14)
        car_part("ellipse;html=1;fillColor=#F5E9C8;strokeColor=none;",
                 wx - 7, 81, 14, 14, rot=-14)
    for (sy, ln) in ((70, 90), (100, 120), (130, 80)):
        car_part("rounded=0;html=1;fillColor=#F5E9C8;strokeColor=none;opacity=78;",
                 350, sy, ln, 5, rot=-14)

    # --- rocket (parts rotated 38) ---
    RX, RY = 860, 470
    def rocket_part(style, x, y, w, h):
        add(style + ";rotation=38;", RX + x, RY + y, w, h)

    rocket_part("shape=triangle;html=1;fillColor=#FF6B1A;strokeColor=none;",
                -16, 96, 32, 52)
    rocket_part("shape=triangle;html=1;fillColor=#FFE88A;strokeColor=none;",
                -8, 96, 16, 32)
    rocket_part("shape=triangle;html=1;fillColor=#C81E1E;strokeColor=none;",
                -34, 50, 20, 46)
    rocket_part("shape=triangle;html=1;fillColor=#C81E1E;strokeColor=none;",
                14, 50, 20, 46)
    rocket_part("rounded=1;html=1;fillColor=#F5E9C8;strokeColor=none;arcSize=20;",
                -18, -40, 36, 136)
    rocket_part("shape=triangle;html=1;fillColor=#C81E1E;strokeColor=none;",
                -18, -86, 36, 48)
    rocket_part("ellipse;html=1;fillColor=#1E7A6B;strokeColor=none;",
                -9, -8, 18, 18)

    # --- typography: text cells ---
    def text_cell(txt, size, color, x, y, w, h):
        add(f"text;html=1;align=left;verticalAlign=top;fontSize={size};"
            f"fontColor={color};fontStyle=1;fontFamily=Helvetica;"
            "whiteSpace=wrap;strokeColor=none;", x, y, w, h, value=txt)

    text_cell("FLY", 230, "#F5E9C8", 40, 350, 460, 260)
    text_cell("ME TO THE", 64, "#2A9D8F", 52, 572, 520, 80)
    text_cell("MOON", 210, "#2A9D8F", 40, 625, 560, 240)

    # --- plaza tiles ---
    for t in spec["tiles"]:
        add(f"rounded=0;html=1;fillColor={hx(t['color'])};strokeColor=#141430;"
            "strokeWidth=2;", t["x0"], t["y0"], t["x1"] - t["x0"],
            t["y1"] - t["y0"])

    # --- couple silhouettes ---
    add("ellipse;html=1;fillColor=#141430;strokeColor=none;",
        322, 868, 16, 16)
    add("rounded=0;html=1;fillColor=#141430;strokeColor=none;",
        312, 868, 36, 6)
    add("rounded=0;html=1;fillColor=#141430;strokeColor=none;",
        320, 858, 20, 10)
    add("shape=triangle;html=1;fillColor=#141430;strokeColor=none;",
        314, 884, 32, 86)
    add("ellipse;html=1;fillColor=#141430;strokeColor=none;",
        366, 876, 14, 14)
    add("ellipse;html=1;fillColor=#141430;strokeColor=none;",
        372, 870, 10, 10)
    add("shape=triangle;html=1;fillColor=#141430;strokeColor=none;",
        354, 890, 38, 80)

    # --- parked vintage cars ---
    def parked(style, x, y, w, h):
        add(style, x, y, w, h)

    parked("rounded=1;html=1;fillColor=#1E7A6B;strokeColor=none;arcSize=12;",
           660, 896, 170, 55)
    parked("shape=trapezoid;html=1;fillColor=#1A3A44;strokeColor=none;",
           711, 881, 68, 18)
    parked("ellipse;html=1;fillColor=#0A0612;strokeColor=none;",
           685, 938, 22, 22)
    parked("ellipse;html=1;fillColor=#0A0612;strokeColor=none;",
           785, 938, 22, 22)
    parked("rounded=1;html=1;fillColor=#F5E9C8;strokeColor=none;arcSize=12;",
           780, 936, 160, 52)
    parked("shape=trapezoid;html=1;fillColor=#1A3A44;strokeColor=none;",
           828, 922, 64, 17)
    parked("ellipse;html=1;fillColor=#0A0612;strokeColor=none;",
           803, 974, 21, 21)
    parked("ellipse;html=1;fillColor=#0A0612;strokeColor=none;",
           897, 974, 21, 21)

    # --- cream poster border ---
    add("rounded=0;html=1;fillColor=none;strokeColor=#F5E9C8;strokeWidth=18;",
        9, 9, W - 18, H - 18)

    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<mxfile host="drawio" version="26.0.0">\n'
           '  <diagram name="Fly Me to the Moon">\n'
           '    <mxGraphModel dx="0" dy="0" grid="1" gridSize="10" '
           'guides="1" tooltips="1" connect="1" arrows="1" fold="1" '
           'page="1" pageScale="1" pageWidth="1024" pageHeight="1024" '
           'math="0" shadow="0" background="#080816">\n'
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
