#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The per-file line budget: a corpus threshold, HALVED once per recorded edit incident.

⚑ THE RULE IS A READING RULE, NOT A STYLE ONE (user, 2026-08-11): *"Any file sufficiently
large that you're not comfortable reading the whole thing and then writing the whole thing back
out, modified, is a file that is too large, and such a file requires decomposition."*

⚑ AND IT WAS DIAGNOSED FROM A REAL DEFECT, NOT PROPOSED IN THE ABSTRACT. An `if __name__ ==
"__main__"` block was appended to the END of `scope_fix.py` (2,823 lines) without knowing one
already existed at :1245 — because the file was never read whole. The mid-file block called
`sys.exit`, so the new one was unreachable: `--selftest` exited 0, silently, and the silence
was then misdiagnosed as import cost. The SIZE is what made the existing entry point
unfindable; every downstream error followed from that. So a second `__main__` guard is
reported AT ANY SIZE, not folded into the line count.

⚑⚑ BECAUSE DISCIPLINE IS NOT AN INSTRUMENT (user, 2026-08-11: *"Can't rely on discipline.
Instead, we cut the split threshold in half for any such affected file."*). The honest
diagnosis of an edit that breaks its own enclosing region is "I edited without reading the
enclosing def whole" — a resolution, not a measure, and resolutions do not survive the next
long session. A per-file threshold that TIGHTENS ON EVIDENCE does.

⚑ AND THE GLOBAL CAP DEMONSTRABLY MISSED THESE. A `--size` sweep over the five files edited in
the session that produced this flagged only `sppf_db.py`; both files actually broken were UNDER
the cap. One corpus-wide number cannot express "this file is harder than its length suggests",
which is exactly what an incident record is.

⚑ MATCHED ON THE REPO-RELATIVE SUFFIX, never an absolute path. The census runs from several
working directories, and an absolute key would silently never match — a ratchet that quietly
stops ratcheting is worse than none, because the number still prints.

⚑ EACH ENTRY NAMES ITS INCIDENT, so the count is EVIDENCE rather than a magic number. Add a row
when a file exhibits the class; NEVER lower a count — this is a ratchet, and paying it down
means SPLITTING the file, not editing this table.
"""

from __future__ import annotations

#: The line count above which a module is REPORTED as over-large.
#:
#: ⚑ A THRESHOLD, NOT A LAW — and stating which it is matters. 1200 is the figure the user
#: cites as commonly applied ("YMMV"), not a measured property of this corpus. It is here so
#: the census has a declared cut rather than a per-reader judgement; a file over it is a
#: REPORT, not a failure.
OVERLARGE_LINES = 1200

#: Files that have EXHIBITED the edit-breaks-its-own-region defect -> how many times.
INCIDENT_HALVINGS: dict[str, int] = {
    # x2: a retirement note placed past a closing `"""` left the module unparseable (the
    # incident that CREATED the 1200 rule); then, hours later, the identical defect in
    # `core_id_for` — prose past the closing quotes, in the file the rule was written for.
    "jea/metalanguage/schema.py": 2,
    # x1: used `_schema` at :289 while its local `import schema as _schema` sat at :315 —
    # a `NameError` 26 lines out of view, inside one 55-line function.
    "scratch/scope_store.py": 1,
    # x1: appended an `if __name__` block to a 2823-line file without knowing one existed at
    # :1245; the mid-file block called `sys.exit`, so the new entry point was unreachable and
    # `--selftest` exited 0 in silence.
    "scratch/scope_fix.py": 1,
}


def incidents_for(path: str) -> int:
    """Return how many edit-breaks-its-own-region incidents `path` has on record."""
    for rel, count in INCIDENT_HALVINGS.items():
        if path == rel or path.endswith("/" + rel):
            return count
    return 0


def budget_for(path: str, base: int = OVERLARGE_LINES) -> tuple[int, int]:
    """Return `(budget, incidents)` for `path` — `base` right-shifted once per incident."""
    hits = incidents_for(path)
    return base >> hits, hits


def explain(path: str, code: int, base: int = OVERLARGE_LINES) -> str:
    """Return why `path` is over budget at `code` lines, or the empty string when it is not.

    ⚑ THE MESSAGE SAYS *WHICH* BUDGET. "over cap" reads as a fact about size; this one is a
    fact about size AND history, and a reader who cannot see the halving will compare the count
    against the corpus number and conclude the census is broken.
    """
    cap, hits = budget_for(path, base)
    if code <= cap:
        return ""
    halved = f" (halved x{hits} — recorded edit-breaks-region incidents)" if hits else ""
    return f"{code} code lines > {cap}{halved}"


def entrypoint_finding(lines: list[int]) -> str:
    """Return why these `__main__` guard line numbers are a defect, or the empty string.

    ⚑ REPORTED AT ANY SIZE. A module has ONE entry point; a second is dead code that LOOKS
    live, and if the first one exits, everything after it is unreachable as a CLI. Folding this
    into the line threshold would hide it in exactly the files where it already hid once.
    """
    if len(lines) <= 1:
        return ""
    at = ",".join(str(n) for n in lines)
    return f"{len(lines)} __main__ guards at {at}"
