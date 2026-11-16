#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""⟡dep-addressing: every declared dependency must resolve from an index or a git URL.

⚑⚑⚑ THE ASK, AND ITS REACH PAST THE INSTANCE (operator, 2026-09-02: *"set a repo gate on saying
'you can't have a dependency not pulled from github or pypy'"*). It is written against a shipped
defect — `pyproject.toml` declared `paperkit` as a bare name for a distribution on no index, so
an adopter's install failed while naming the wrong cause — but the gate is not about paperkit.
It catches the NEXT sibling repo declared by bare name, which is the failure that made this tree
uninstallable without anyone noticing for two days.

⚑⚑ WHAT MAKES IT NOTICEABLE AT ALL IS THAT THE DECLARATION IS THE SURFACE. The manifest is one
finite, reviewable file, and every dependency edge an adopter must satisfy passes through it — so
the question can be asked completely, statically, and offline. That is deliberate: see
`substrate/dep_addressing`, which owns the reading and records why hitting the network here would
convert a machine fact into a repo verdict.

⚑ NOT A RATCHET — A BIJECTION, the framing `check_stub_authority` establishes. There is no
baseline file and no paydown ledger, because a requirement either carries an address or it does
not; there is no meaningful "existing debt" in that correspondence. The baseline is EMPTY by
construction rather than by grandfathering, which is the polarity `policy_is_a_ratchet_over_census`
warns is otherwise inverted.

⚑ AND THE RELIEF IS ENUMERABLE AND LIVES IN THE READER. `dep_addressing.UNPUBLISHED` names the
distributions this repo knows are on no index; it lists the KNOWN-UNPUBLISHED rather than the
permitted, so each entry makes the gate STRICTER and nothing is admitted by accretion. There is
no allowlist here.

⚑ PROVEN ABLE TO FAIL, which is the property this repo most often finds missing. The selftest
runs a synthetic manifest carrying the shipped defect through the whole reader and requires it be
caught, beside the repaired manifest which must go clean — so a predicate that stopped
discriminating fails a case instead of going quietly green.

⚑⚑⚑ AND IT ACCEPTED A MANIFEST PATH AND THREW IT AWAY (Ⓝ124a ⟡dep-gate-ignores-its-operand,
2026-09-03). Passed `pyproject.toml`, it exited 0 having read its own fixed file — a CONFIDENT
answer to a question it was never asked, which is `ratchet_flags.check_argv`'s own wording for a
silently-dropped FLAG. The flag half was guarded here by a HAND-ROLLED copy of that check while
the authority itself sat unused two imports away, and the operand half was guarded by nothing.
Both are now `check_argv`'s, and `dep_addressing.operand` reads the path.

Blocking gate (proposed Phase A — NOT yet wired into .githooks/pre-commit; wiring is the
operator's call). Exit 0 = every dependency is addressed, 1 = at least one is not, 2 = cannot run.
Usage: check_dep_addressing.py [--quiet] [--list] [--selftest] [<manifest>]
"""

from __future__ import annotations

import sys

from substrate import dep_addressing, dep_addressing_selftest
from substrate.ratchet_flags import check_argv

# ⚑ THE FLAGS THIS GATE ANSWERS TO. An unknown flag is REFUSED rather than ignored, so a
# mistyped invocation cannot read as a clean run — the shape `check_stub_authority.main` sets.
#
# ⚑⚑ THE REFUSAL IS NOW `check_argv`'S RATHER THAN A LOCAL COPY OF IT. The hand-rolled version
# here worked and was still the `agda_files()`-had-four-bodies shape: a shared capability
# re-spelled per gate, so `--dry-run` (which the authority admits universally) was refused here
# and nowhere else, and any future refinement would have to find this copy to reach it.
_FLAGS = frozenset({"--quiet", "--list", "--selftest"})


def main(argv: list[str]) -> int:
    """Check a manifest's dependency addressing; 1 when any resolves from nowhere.

    ⚑ THE OPERAND IS READ BY `dep_addressing.operand`, NOT RE-PARSED HERE. A second spelling of
    "which file did we mean" at the wrapper is how a gate starts disagreeing with its own reader
    about what it read — the reason `MANIFEST` is named once.
    """
    if (rc := check_argv(argv, _FLAGS, "check_dep_addressing.py")) is not None:
        return rc
    return dep_addressing.main(argv)


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(dep_addressing_selftest.selftest())
    sys.exit(main(sys.argv))
