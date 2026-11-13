# Phoenix Rising — make.fun coolest-art-01 entry v2 (Python 3.13, stdlib only).
# The artwork is art.png beside this file (a phoenix with spread wings
# rising from flames under a night moon, designed as an editable draw.io
# diagram in artwork.drawio and rendered by render.py); the program copies
# it to /output/entry.png. Deterministic: the same bytes every run, no network.
#
# Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for /output:
#   mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py

import os
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
SRC = HERE / "art.png"
DST = OUT / "entry.png"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SRC, DST)
    # The gate reads exactly these bytes: confirm the copy is whole.
    assert DST.stat().st_size == SRC.stat().st_size, "entry.png copy incomplete"


if __name__ == "__main__":
    main()
