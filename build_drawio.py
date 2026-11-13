#!/usr/bin/env python3
"""Build artwork.drawio from the SAME design spec as render.py (v2 Phoenix).

Per drawio-skill references/xml-authoring.md:
- ids 0/1 are roots, user shapes start at 2, sequential, parent="1"
- no edges in this design (shapes only); feathers/flames are rotated
  triangles, ribbons are chains of small ellipses, so no
  <mxGeometry relative="1"/> needed
- shapes snapped to whole pixels; fillColor/strokeColor hex; opacity via style
"""
import math
import sys
from pathlib import Path
from xml.sax.saxutils import escape

sys.path.insert(0, str(Path(__file__).resolve().parent))
from render import design, W, H, MOON_CX, MOON_CY, MOON_R  # noqa: E402

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

    # --- sky: gradient rect indigo -> crimson, south ---
    add("rounded=0;html=1;fillColor=#0B1035;gradientColor=#2A0A18;"
        "gradientDirection=south;strokeColor=none;", 0, 0, W, H)
    # ember-dark band near the bottom
    add("rounded=0;html=1;fillColor=#3A0E08;strokeColor=none;opacity=45;",
        0, 700, W, 324)

    # --- stars: rhombus diamonds ---
    for st in spec["stars"]:
        s = st["s"]
        add(f"rhombus;html=1;fillColor={hx(st['color'])};strokeColor=none;"
            f"opacity={round(st['alpha'] / 255 * 100)};",
            st["x"] - s, st["y"] - s, 2 * s, 2 * s)

    # --- moon glow discs + disc + craters ---
    for r, op in ((110, 5), (84, 9), (66, 16)):
        add(f"ellipse;html=1;fillColor=#FFF0C8;strokeColor=none;opacity={op};",
            MOON_CX - r, MOON_CY - r, 2 * r, 2 * r)
    add("ellipse;html=1;fillColor=#FFF0C8;strokeColor=none;",
        MOON_CX - MOON_R, MOON_CY - MOON_R, 2 * MOON_R, 2 * MOON_R)
    for cx, cy, r in ((776, 148, 10), (822, 182, 13), (790, 190, 7)):
        add("ellipse;html=1;fillColor=#E8D8B0;strokeColor=none;opacity=35;",
            cx - r, cy - r, 2 * r, 2 * r)

    # --- fire glow behind the phoenix ---
    for r, op in ((330, 6), (280, 10), (225, 16)):
        add(f"ellipse;html=1;fillColor=#FF6B1A;strokeColor=none;opacity={op};",
            512 - r, 480 - r, 2 * r, 2 * r)

    # --- wing bases: one big triangle per fan (solid silhouette) ---
    add("shape=triangle;html=1;fillColor=#8B0E0E;strokeColor=none;"
        "rotation=115;", 120, 230, 360, 300)
    add("shape=triangle;html=1;fillColor=#8B0E0E;strokeColor=none;"
        "rotation=-115;", 544, 230, 360, 300)

    # --- tail ribbons: 12 ellipses each along the wavy path ---
    for rb in spec["ribbons"]:
        steps = 12
        for i in range(steps):
            t = i / (steps - 1)
            y = rb["y0"] + t * rb["length"]
            x = rb["x0"] + math.sin(t * 4.2 + rb["phase"]) * rb["amp"] * t
            r = 17 * (1 - t * 0.65) + 4
            add(f"ellipse;html=1;fillColor={hx(rb['color'])};strokeColor=none;"
                "opacity=92;", x - r, y - r, 2 * r, 2 * r)

    # --- feathers: rotated triangles (tip, b1, b2) ---
    for f in spec["feathers"]:
        (tx, ty), (b1x, b1y), (b2x, b2y) = f["poly"]
        mx, my = (b1x + b2x) / 2, (b1y + b2y) / 2
        dx, dy = tx - mx, ty - my
        h = math.hypot(dx, dy)
        rot = math.degrees(math.atan2(dx, -dy))
        cx, cy = (mx + tx) / 2, (my + ty) / 2
        w = math.hypot(b1x - b2x, b1y - b2y)
        add(f"shape=triangle;html=1;fillColor={hx(f['color'])};"
            f"strokeColor=none;opacity=92;rotation={round(rot, 1)};",
            cx - w / 2, cy - h / 2, w, h)
        add("ellipse;html=1;fillColor=#FFE88A;strokeColor=none;opacity=78;",
            tx - 4, ty - 4, 8, 8)

    # --- body: gold ellipse + red belly + chest ---
    add("ellipse;html=1;fillColor=#FF9A3D;strokeColor=none;",
        476, 330, 72, 280)
    add("ellipse;html=1;fillColor=#FFC23D;strokeColor=none;",
        492, 400, 40, 120)
    add("ellipse;html=1;fillColor=#C81E1E;strokeColor=none;opacity=70;",
        479, 490, 66, 95)

    # --- head: crest triangles + head ellipse + beak + eye ---
    for dx, ln, col in ((-14, 46, "#FFC23D"), (-4, 56, "#FF9A3D"),
                        (8, 44, "#FFC23D")):
        add(f"shape=triangle;html=1;fillColor={col};strokeColor=none;",
            512 + dx - 8, 338 - ln, 16, ln)
    add("ellipse;html=1;fillColor=#FFC23D;strokeColor=none;",
        496, 322, 32, 32)
    add("shape=triangle;html=1;fillColor=#FF6B1A;strokeColor=none;"
        "rotation=90;", 526, 336, 12, 22)
    add("ellipse;html=1;fillColor=#FFFFFF;strokeColor=none;",
        516, 332, 6, 6)
    add("ellipse;html=1;fillColor=#0A0612;strokeColor=none;",
        518, 334, 2, 2)

    # --- ridge: one triangle per peak ---
    pts = spec["ridge"]
    peaks = pts[1:-1]
    for i, (px, py) in enumerate(peaks):
        x0 = pts[i][0]
        x1 = pts[i + 2][0]
        add("shape=triangle;html=1;fillColor=#0A0612;strokeColor=none;",
            x0, py, x1 - x0, H - py)

    # --- ground flames: triangles + pale inner tongues ---
    for fl in spec["flames"]:
        x, h, w = fl["x"], fl["h"], fl["w"]
        add(f"shape=triangle;html=1;fillColor={hx(fl['color'])};"
            "strokeColor=none;opacity=92;", x - w / 2, 1010 - h, w, h)
        add("shape=triangle;html=1;fillColor=#FFE88A;strokeColor=none;"
            "opacity=86;", x - w / 4, 1010 - h * 0.62, w / 2, h * 0.62)

    # --- embers: small ellipses ---
    for em in spec["embers"]:
        r = em["r"]
        add(f"ellipse;html=1;fillColor={hx(em['color'])};strokeColor=none;"
            f"opacity={round(em['alpha'] / 255 * 100)};",
            em["x"] - r, em["y"] - r, 2 * r, 2 * r)

    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<mxfile host="drawio" version="26.0.0">\n'
           '  <diagram name="Phoenix Rising">\n'
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
