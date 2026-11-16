#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""DRAINED. The bib reader and writer now lives in `substrate.bibstruct_main` and its modules.

⚑⚑⚑ THIS FILE IS A SHIM, AND IT IS THE END OF Ⓑ24 ⟡bibstruct-drain. It was 2,300 lines carrying
~1,367 findings, which meant the per-file gate refused every edit to it — including the ONE-LINE
predicate change that started this arc. *"A module that cannot be edited cannot be repaired"*, so
it was decomposed and replaced rather than patched: seventeen modules, each written clean in one
pass, each with its own suite.

⚑⚑ WHERE EACH RESPONSIBILITY WENT, so a reader arriving at this path is not left searching:

    substrate.bib_parse           the ONE parser — the file is the oracle
    substrate.bib_corpus          composing several bibs; collisions; edges; orphans; mentions
    substrate.bib_roundtrip       the totality probe — what the parse fails to ACCOUNT for
    substrate.bib_argv            argv OWNERSHIP: which token belongs to which flag
    substrate.bib_modes           the mode roster, DECLARED via climode.Mode
    substrate.bib_pairs           name=value operands, where a value contains spaces
    substrate.bib_entry           validating and rendering a NEW entry
    substrate.bib_edit            editing ONE field: match on masked, slice the raw
    substrate.bib_write           the write protocol: diff, gate, snapshot, write, verify
    substrate.bib_report          rows and the `n of m` denominator
    substrate.bib_handlers        the read verbs
    substrate.bib_write_handlers  the write verbs
    substrate.bib_cli             resolve, dispatch, return
    substrate.bibstruct_main      the assembly: real parser, real engine, real snapshot guard
    substrate.witness_resolves    the `item:` guard — ASK THE RESOLVER, never scan text

⚑⚑⚑ AND THE DEFECT THAT MOTIVATED THE DRAIN IS FIXED BY CONSTRUCTION. This file's `--add` guard
text-scanned `catalog/library/items.py` for `def <KEY>(` — a file the witnesses had VACATED — so a
key that resolves perfectly at runtime was unwritable. Measured in this file's own suite:
`--add … check=item:T27` refused while `items.py T27` exits 0 and reports the item CLOSED. **A guard
refusing a key its own resolver answers.** `witness_resolves` asks the resolver.

⚑⚑⚑ THE PATH BOOTSTRAP BELOW IS NOT DECORATION — A PEER WAS BLOCKED WITHOUT IT (gate-G207,
gate-G208). The drain replaced this file's self-contained body with packaged imports, and a script
run by path puts its OWN DIRECTORY on `sys.path`, never the cwd. So `scratch/` went on the path and
`substrate/` was invisible from there, for every invoker outside this repo — and my own runs
succeeded for a reason I misattributed to cwd, which sent a peer a fix that could not work.

⚑⚑ AND THE READINESS READER CERTIFIED THE BREAK. `swap_readiness scratch/bibstruct.py` reports
*"imports: READY — every import a packaged consumer can follow"*, because it asks whether each name
is PACKAGE-SHAPED, never whether it RESOLVES for an invoker. Those are different questions and the
label collapses them. The bootstrap makes the second one true.

⚑ THE PATH IS KEPT ALIVE DELIBERATELY, NOT ABANDONED. Two importers reach `entries` by this name,
and both carry their own findings — so repointing them is blocked by the same gate that blocked
this file. The re-export below is what lets the replacement land without waiting on their drains;
this file retires when they do.

⚑ NOTHING BELOW RE-IMPLEMENTS ANYTHING. A shim that added behaviour would be a second authority for
a question the package already answers, which is the defect this whole arc was about.
"""

from __future__ import annotations

import sys
from pathlib import Path

# ⚑⚑⚑ RESOLVED FROM `__file__`, NEVER FROM THE CWD, AND THE DIFFERENCE IS THE WHOLE BUG. A peer
# invoking this by path from their own tree got `ModuleNotFoundError: No module named 'substrate'`
# and my `env -C` suggestion could not help them, because cwd is not on `sys.path` for a script
# invocation at all. The repo root is a fixed distance from this file, so deriving it here works
# from any cwd, under any invoker, with no environment variable and no install.
#
# ⚑ INSERTED ONLY IF ABSENT, so a consumer who HAS arranged the path keeps their arrangement and
# this does not shadow an installed copy with a checkout — the two-copies hazard that makes a
# bug reproduce differently for the reporter and the owner.
_ROOT = str(Path(__file__).resolve().parent.parent)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from substrate.bib_parse import read  # noqa: E402 — must follow the bootstrap above
from substrate.bibstruct_main import main  # noqa: E402 — must follow the bootstrap above


def entries(path: str | Path | list[str] | None = None) -> dict[str, dict[str, str]]:
    """Return `{key: {field: value}}` for one bib or several, composed.

    ⚑ THE LIST FORM IS PRESERVED BECAUSE CALLERS PASS IT. A composed read is the unit — a premise
    in a sibling bib resolves only when that bib is in the population — so accepting one path where
    a caller means several would silently narrow their corpus, which is the defect the composed
    reader exists to prevent.
    """
    from substrate import bib_corpus  # noqa: PLC0415 — only the list form needs it

    if path is None:
        from substrate.bib_handlers import DEFAULT_BIB  # noqa: PLC0415

        return read(Path(DEFAULT_BIB))
    if isinstance(path, list):
        return dict(bib_corpus.compose([Path(p) for p in path], read).entries)
    return read(Path(path))


def roundtrip(path: str | Path | None = None) -> list[tuple[str, str, str]]:
    """Return every construct the file holds that the parse did not account for.

    ⚑⚑⚑ THIS EXPORT WAS MISSING FROM THE SHIM'S FIRST CUT, AND THE MISS HAS A LESSON. The surface
    was measured with `attr_reads bibstruct.*`, which reported `entries` and nothing else — so the
    shim served `entries`. But `substrate/probe_kernel.py` loads this module DYNAMICALLY and checks
    `hasattr(found, "roundtrip")`, and a static attribute reader cannot see that. **Its own output
    said so on every run** — *"11 shape(s) this reader CANNOT resolve: dynamic-import …"* — and I
    read past the bound to the count.

    ⚑⚑ THE WITNESS WAS RIGHT AND I READ IT AS STALE. `D0-kernel` reported *"no --roundtrip: the bib
    reader has no totality probe"*, which I took for a witness left behind by the drain. It was a
    true statement about the module it reads: the capability had moved and the path it reads had
    not been given it. **A finding that survives a repair is evidence about the repair, not about
    the finding.**
    """
    from substrate import bib_parse, bib_roundtrip  # noqa: PLC0415 — one consumer needs it
    from substrate.bib_handlers import DEFAULT_BIB  # noqa: PLC0415

    target = Path(path) if path is not None else Path(DEFAULT_BIB)
    text = target.read_text(encoding="utf-8") if target.exists() else ""
    return [(loss.kind, loss.what, loss.detail)
            for loss in bib_roundtrip.probe(text, bib_parse.parse(text))]


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
