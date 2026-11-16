#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""borrowed_root_census.py — which readers crash when run from a BORROWING checkout.

⚑⚑⚑ THIS EXISTS BECAUSE I REPAIRED AN INSTANCE TWICE AND NEVER COUNTED THE CLASS. A peer running
substrate's tools from their own tree hit the same crash in two sibling files, one tick apart
(gate-G245, gate-G249). Both were repaired individually; `pycodemod --calls population` then read
eighteen definitions of that one function name, so the two I had touched were two of eighteen and I
had checked none of the rest.

⚑⚑ THE POPULATION SPLITS IN TWO AND THE SPLIT IS THE POINT. A LIVE site defaults its root, so a
caller in another checkout reaches it with a foreign tree and it raises. A LATENT site has the
identical body and is protected only by every caller passing a root explicitly — it becomes live
the day someone adds a default. Reporting one number for both would either overstate today's
breakage or hide the copies one edit away from it.

⚑ AND IT REPORTS `n of m`, because a bare zero cannot separate *scanned and clean* from *never
scanned*. That distinction is what this class is made of.

⚑⚑ THE FIRST CUT REACHED `Path` THROUGH `__import__` AND THE TYPE GATE REFUSED IT, correctly: a
dynamic import is `Any`, and one `Any` at the top of a pipeline makes every downstream expression
unverifiable. A census whose own types are unchecked is a poor instrument for a defect that lives
in a composition — and the second cut was refused again for an unannotated sort key, which is the
same leak one expression over.

Usage: borrowed_root_census.py [--live]      (--live lists only the sites that crash today)
"""

from __future__ import annotations

import sys
from pathlib import Path

from substrate import borrowed_root, corpus


def _order(site: borrowed_root.Site) -> tuple[str, int]:
    """Return the sort key for a site — module then line, so a reader can walk the output."""
    return (site.module, site.line)


def main(argv: list[str]) -> int:
    """Print the census, returning 1 when any site is live."""
    only_live = "--live" in argv
    files = [(Path(p), str(p)) for p in corpus.py_files()]
    found = borrowed_root.census(files)
    live = [s for s in found if s.live]

    for site in sorted(live if only_live else found, key=_order):
        print(f"  {site.why()}")  # noqa: T201

    print(
        f"borrowed-root: {len(live)} LIVE and {len(found) - len(live)} latent "  # noqa: T201
        f"root-measuring site(s), over {len(files)} file(s) scanned"
    )
    return 1 if live else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
