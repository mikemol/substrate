#!/usr/bin/env python3
"""traces:<path>#<needle> — a corpus claim is TRACEABLE-TO-SOURCE.

⚑⚑⚑ ADOPTED FROM cassian's `gate-architecture/checks/traces.py`, NOT RE-DERIVED. This plan's own
headline finding is that audit-as-warrants beats audit-as-prose, and cassian is the repo that
demonstrated it; re-implementing their check verb while recommending their pattern would be the
rival-authority defect substrate files against everywhere else. The two refusals below are theirs
and are the load-bearing part: a target with no `#` and a target with an empty needle both verify
NOTHING, and an empty needle matches every file.

⚑⚑ ADOPTED IS NOT COPIED, AND SUBSTRATE'S GATE PROVED IT. The verbatim original is clean in
cassian's tree and REFUSED by substrate's per-file gate — no annotations, bare `print`. So the
adoption carries the LOGIC and conforms to the receiving repo's standards, which is what the ban on
vendoring-as-is exists to force. The refusal is the mechanism doing its job on an import.

⚑⚑ WHAT A PASS MEANS, AND IT IS NARROWER THAN IT LOOKS. This verifies that a claim is RECORDED
where the sentence says it is — never that the claim is true. Most needles here point into a PEER's
document, so a pass witnesses what that peer SAID. A peer can be wrong in their own words and this
check still passes, correctly: the gate is against DRIFT, not against error.

⚑ AND THAT IS WHY THE COMPANION KIND EXISTS. A claim with no needle in any source — this plan's own
retractions, which are facts about the author's refuted reasoning — carries `premise:` instead, and
renders as not-machine-checked. Forcing a `traces:` onto one would manufacture a witness, which is
the overclaim the corpus's honesty discipline forbids.

cwd is the project dir (paperkit runs a check from there), so paths reach peers via `../../../`.

    python3 checks/traces.py '../../../paperkit/docs/bazel-architecture.md#hint, not a bound'
"""

from __future__ import annotations

import sys
from pathlib import Path

# What the caller gets back. ⚑ 2 IS A BAD TARGET AND 1 IS A FAILED CHECK, and the split matters:
# a malformed target means the WARRANT is wrong, a missing needle means the SOURCE moved.
BAD_TARGET = 2
NOT_FOUND = 1


def _say(message: str) -> None:
    """Write one diagnostic to stderr."""
    sys.stderr.write(message + "\n")


def main(argv: list[str]) -> int:
    """Return 0 iff the needle appears in the named source."""
    if not argv:
        _say("traces: no target — want <path>#<needle>")
        return BAD_TARGET

    target = argv[0]
    if "#" not in target:
        _say(f"traces: target {target!r} has no '#<needle>' — a traceability check must name the "
             f"string it looks for, or it verifies nothing")
        return BAD_TARGET

    path_s, needle = target.split("#", 1)
    if not needle:
        _say(f"traces: empty needle in {target!r} — a whole-file grep verifies nothing "
             f"(an empty needle matches every file)")
        return BAD_TARGET

    path = Path(path_s)
    if not path.exists():
        _say(f"traces: source {path} does not exist (cwd={Path.cwd()}) — the claim names a source "
             f"that is not here. ⚑ A PEER CORPUS MOVES: an absent source may mean the artifact was "
             f"renamed or withdrawn, which is a fact about the corpus, not about the claim.")
        return NOT_FOUND

    if needle not in path.read_text(errors="replace"):
        _say(f"traces: {needle!r} NOT found in {path} — the claim has drifted from its source, or "
             f"the source was edited. Re-anchor the claim or fix the needle.")
        return NOT_FOUND

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
