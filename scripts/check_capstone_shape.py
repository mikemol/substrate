#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""⟡capstone-not-a-barrel as a GATE.

A capstone is a **directory with a README**, never a `.agda` module.

WHY IT IS A GATE. A capstone module is a barrel BY CONSTRUCTION: its whole job is to
name a roster, and the only way a module can name a roster is to IMPORT it — so the
capstone drags its entire arc into every consumer's core, and a chain of capstones (one
re-exporting the next) compounds it. The four HC capstones were exactly that chain:
`InfCapstone` re-exported three sibling capstones, each re-exporting nine modules, none
of them defining anything. A directory cannot do that: prose names a roster without
importing it.

This is a HARD gate at zero, not a ratchet — the tree has no capstone modules left, so
there is nothing to grandfather. Prose in CLAUDE.md would be enforced by attention,
which is exactly how the barrel debt accumulated in the first place.

THE REPAIR, when this fires:

  · pure barrel (imports + comments, no definitions)
        -> scratch/capstone_to_dir.py --apply <file>
  · carries definitions
        -> scratch/split_lemmas.py --apply <file>   (one def per leaf)
           then add <dir>/README.md with the roster and the attestation.

Either way the module is DELETED and its consumers bind at the OWNER.

⚑ `absolute()`, NEVER `resolve()`. `PTH100` recommends `Path.resolve()` as
`os.path.abspath`'s replacement and it is NOT one: `resolve()` FOLLOWS SYMLINKS, so a
resolved `__file__` derives the symlink TARGET's root rather than the invoking
checkout's. That substitution shipped to five repos on 2026-08-30. The rule names the
right problem and the wrong cure.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).absolute().parent.parent
SRC = ROOT / "agda" / "Substrate"
CAPSTONE = re.compile(r"capstone", re.IGNORECASE)


def census() -> list[str]:
    """Return every `.agda` whose module name contains `capstone`, repo-relative."""
    return sorted(str(p.relative_to(ROOT)) for p in SRC.rglob("*.agda") if CAPSTONE.search(p.stem))


def main() -> int:
    """Report the census and return the gate's exit code.

    ⚑⚑ ONE STREAM, DELIBERATELY, AND A SPLIT ONE WAS TRIED AND REVERTED. Sending the
    verdict to stdout and the findings to stderr looks tidier and MEASURABLY BROKE THE
    REPORT: the two streams flush independently, so the `BROKEN — 13 …` header printed
    AFTER its own list and the reader saw thirteen bare paths introduced by nothing. A
    gate's message is a single ordered narrative — header, findings, repair — and
    interleaving is not a formatting preference, it is the message arriving scrambled.

    ⚑ SO `T201` IS SATISFIED BY WRITING TO A STREAM, NOT BY CHOOSING A DIFFERENT ONE.
    The rule objects to `print` as an unconfigurable output channel; it says nothing
    about which stream, and reading it as advice to split one was over-reading it.
    """
    quiet = "--quiet" in sys.argv
    bad = census()
    if bad:
        header = (
            f"capstone-shape: BROKEN — {len(bad)} capstone MODULE(s); a capstone "
            f"is a DIRECTORY WITH A README, never a `.agda`:"
        )
        why = (
            "  A capstone module is a barrel by construction — naming a roster from "
            "inside Agda means IMPORTING it, so the whole arc lands in every "
            "consumer's core."
        )
        repair = (
            "  Repair: scratch/capstone_to_dir.py --apply <file>  (pure barrel), "
            "or scratch/split_lemmas.py --apply <file> + a README (carries defs)."
        )
        listing = [f"    + {p}" for p in bad]
        sys.stdout.write("\n".join([header, *listing, why, repair]) + "\n")
        return 1
    if not quiet:
        sys.stdout.write("capstone-shape: clean (0 capstone modules; capstones are directories).\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
