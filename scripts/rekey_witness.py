#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""rekey_witness.py — RETIRED: a re-key is now a bib-key rename, `bibstruct --rename`.

⚑⚑ WHAT THIS TOOL DID, AND WHY IT HAS NO SUBJECT LEFT. `findings.py --pairing` reported SPELLING
PAIRS (*one finding, two spellings — RE-KEY, do not file twice*), and the ledger's only write
CREATED, so the honest repair — a RENAME — needed its own tool. This one moved a witness's key in
the `WITNESSES` literal through `substrate.witness_rekey`.

⚑ THE LITERAL IS GONE (W40, the roster cleanroom): every witness is its bib entry's `check`, and
`findings.py` is a shim with no roster to edit. So a re-key is renaming the bib entry, and
repointing every `from` / `rests-on` edge that names it — which `bibstruct --rename` does across a
stated corpus, one snapshotted write per touched bib, refusing a name already taken (never a merge).

⚑ IT REFUSES RATHER THAN DISAPPEARING, so a caller following an old instruction learns where the
capability went instead of meeting "no such file".
"""

from __future__ import annotations

import sys

# What every invocation is told.
REDIRECT = (
    "rekey_witness: RETIRED with the findings roster it edited. A re-key is now a bib-key rename:\n"
    "    bibstruct --rename <old> <new> --bib .claude/agents/<oracle>.bib "
    "[--corpus <other bibs>] --apply\n"
    "  (dry run without --apply). It repoints every from/rests-on edge naming <old> across the\n"
    "  corpus and refuses a <new> that is already taken.\n"
)


def main(argv: list[str]) -> int:
    """Refuse, naming the successor."""
    del argv
    sys.stderr.write(REDIRECT)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
