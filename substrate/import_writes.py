#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Whether importing a tool would WRITE — the question a read-only reader must ask first.

⚑⚑⚑ "IT ONLY IMPORTS IT" IS NOT THE SAME AS "IT DOES NOT WRITE", AND THE DIFFERENCE WAS MEASURED
HERE. A census that reads a gate's `census()` must IMPORT that gate, and a tool whose body sits
at module level RUNS on import. `scripts/sppf_node_index.py` is exactly that shape — its whole
body is top-level and its final `else:` writes — so the first live run of `commit_refusal`
regenerated `scratch/sppf_collision_index.md` while reporting itself as read-only.

⚑⚑ A READER THAT MUTATES THE TREE IT REPORTS ON IS WORSE THAN ONE THAT REPORTS NOTHING, because
its output is then a description of a tree it changed. That is not a lint concern; it is the
same class as a ratchet that banks debt on a read, which this repo has recorded twice.

⚑ THE JUDGEMENT IS DELEGATED, NEVER RE-DERIVED. `_pycodemod_census.writes_by_default` DISCOVERS
the polarity from the source — a write is guarded when it is reachable only under an explicit
opt-in, is inert, or targets a tempfile — so an allow-list here would rot exactly as the four
`agda_files()` bodies did. This module only makes that authority reachable and states the
default when it is not.

⚑⚑ AND THE DEFAULT POINTS AT "DO NOT IMPORT", WHICH IS THE CONSERVATIVE DIRECTION THE AUTHORITY
ITSELF DOCUMENTS: a false "writes" costs one skipped census, a false "safe" costs an unintended
write. ⚑ BUT UNCONDITIONAL CAUTION IS NOT SAFETY EITHER — on its first cut the detector was
looked up through `gate_module`, which resolves against `scripts/` while this authority lives in
`scratch/`, so it was never found and EVERY gate came back "do not import". A reader reporting
its whole roster as unreadable is the census-green defect wearing the opposite sign: safe, and
useless. That is why it loads by explicit LOCATION, and why the suite pairs the detection with a
pure-reader control.

⚑ EXTRACTED RATHER THAN INLINED, at the per-file gate's own instruction: the guard needs
`importlib`/`sys` at module scope and its consumer could not absorb them in one edit. The gate
that keeps firing is saying the unit is wrong.
"""

from __future__ import annotations

import importlib.util
import sys

from substrate import corpus

# The authority on write-polarity. ⚑ IT LIVES IN `scratch/`, NOT `scripts/` — which is precisely
# why `gate_module` cannot resolve it and this module names the location instead.
NAME = "_pycodemod_census"
WHERE = ("scratch", f"{NAME}.py")

# What to say when the authority cannot be reached at all.
UNAVAILABLE = "write-polarity detector unavailable — not imported, to avoid a stray write"


def detector() -> object | None:
    """Load the write-polarity authority by explicit location, or None when it is unreachable.

    ⚑ BY LOCATION, NOT BY `sys.path`. Path mutation is refused in this tree and would be the
    wrong fix anyway: it makes an import work by rearranging global interpreter state instead of
    by saying where the file is. `gate_module` resolves the same way and for the same reason.
    """
    if NAME in sys.modules:
        return sys.modules[NAME]
    path = corpus.ROOT.joinpath(*WHERE)
    if not path.exists():
        return None
    spec = importlib.util.spec_from_file_location(NAME, str(path))
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    # ⚑ REGISTERED BEFORE EXECUTION, because a module importing its own siblings by bare name
    # must find itself mid-import; the registration is undone on failure so a half-executed
    # module is never left for the next caller to find.
    sys.modules[NAME] = module
    try:
        spec.loader.exec_module(module)
    except BaseException:  # noqa: BLE001 — a tool may SystemExit at import
        sys.modules.pop(NAME, None)
        return None
    return module


def _pair(got: object, index: int) -> object:
    """Read one field of the authority's `(bool, why)` answer across the untyped boundary."""
    if isinstance(got, (list, tuple)) and index < len(got):
        return got[index]
    return None


def why_not_import(script: str) -> str:
    """Return why importing `script` would write, or the empty string when it is safe to read.

    ⚑ THE RETURN IS A REASON, NOT A BOOLEAN, because a caller that skips a gate must be able to
    say WHY it skipped one. A bare False would leave the skipped gate rendering as a blank —
    which reads like "no finding", the exact collapse this whole surface exists to prevent.

    ⚑⚑ AN UNREADABLE SPECIMEN IS NOT A SAFE ONE, AND THE FIRST CUT GOT THIS BACKWARDS. The
    authority answers `(False, "unreadable: …")` for a file it cannot open — a False that means
    "could not tell", not "does not write". Reading it as safe would let a path typo authorise
    the import this guard exists to withhold, so the reason is inspected and not just the flag.
    """
    reader: object = getattr(detector(), "writes_by_default", None)
    if not callable(reader):
        return UNAVAILABLE
    path = corpus.ROOT / script
    if not path.exists():
        return f"{script} does not exist — not imported"
    got: object = reader(str(path))
    why = str(_pair(got, 1) or "")
    if _pair(got, 0) is not True:
        return (
            f"polarity undetermined ({why}) — not imported" if why.startswith("unreadable") else ""
        )
    return f"writes on a bare run ({why}) — not imported"
