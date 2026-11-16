# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Write a `Flat.mk` rendering to a named file, so a real `make` can parse it (⟡promote-path A).

⚑⚑ THE SUITE READS THE TEXT; ONLY `make` CAN SAY THE TEXT IS A MAKEFILE. `flat_emit_selftest`
proves the parameterized rendering changes only the lines it should — a claim about STRINGS. That
the result parses, that `TSFX` expands to `.sandbox` or to nothing, and that `TENANT=bogus` stops
with the guard, are claims about MAKE, and `make -n -f <this file>` is the instrument for them.

⚑ IT WRITES ONLY WHERE IT IS TOLD, NEVER `agda/Flat.mk`. Replacing the committed makefile is the
drain's last step and goes through the generator's own `--check`; a render tool that could
overwrite it would be a second path to the build's single source of truth.
"""

from __future__ import annotations

import sys
from pathlib import Path

from substrate import corpus, flat_emit, flat_origin

USAGE = (
    "usage: python3 -m substrate.flat_render --out PATH [--parameterized]\n"
    "  renders Flat.mk from the origin's graph and constants into PATH (never agda/Flat.mk)\n"
)
PROTECTED = corpus.ROOT / "agda" / "Flat.mk"


def main(argv: list[str]) -> int:
    """Render to `--out`, refusing the committed makefile's own path."""
    known = {"--out", "--parameterized"}
    if "--out" not in argv or argv.index("--out") + 1 >= len(argv):
        sys.stderr.write(USAGE)
        return 2
    out = Path(argv[argv.index("--out") + 1]).resolve()
    stray = [a for a in argv if a.startswith("--") and a not in known]
    if stray or out == PROTECTED.resolve():
        sys.stderr.write(USAGE)
        return 2
    origin = flat_origin.load()
    text = flat_emit.text(
        flat_origin.graph(origin), flat_origin.settings(parameterized="--parameterized" in argv)
    )
    out.write_text(text + "\n", encoding="utf-8")
    sys.stdout.write(f"wrote {out}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
