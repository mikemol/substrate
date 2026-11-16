#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""⟡type-gate: a STATIC-TYPE ERROR in PROMOTED python is DEBT, payable down and never grown.

⛔ POLICY (user, 2026-08-01): *"Have we reached a point where we should be using [a type
checker] to provide typing guarantees (i.e. not None) for our functions? Because that's what
it's feeling like."* … *"I think I prefer mypy here. And gated."*

THE EVIDENCE IS AN ARC'S OWN DEFECT LOG, and every one cost a run-edit-run cycle:
`agda_lex.imports_of` reached behind a `hasattr` fallback — **the strongest case, because the
GUARD HID IT**: a fallback to an absent function degraded the check to measuring NOTHING, and
a census that measures nothing reports a clean tree. `_classify` called before it existed,
recorded at the time as *"the FOURTH invented API this session"* — they were already being
counted and still shipping. Two more invented APIs. A callable-vs-list argument error. A
2-tuple widened to a 3-tuple with four returns and a call site unchecked.

⚑ WHAT THIS GATE IS *NOT*: an annotation-coverage push. It censuses what mypy reports on the
promoted corpus, whose profile is DEFECT-SHAPED (`arg-type`, `attr-defined`, `union-attr`,
`used-before-def`). Adding a stricter flag would convert a defect census into an annotation
census and bank hundreds of keys that are not the policy. **The predicate must match the
POLICY, not the tool's maximum setting.**

⚑⚑ SPLIT FROM `scripts/check_mypy_ratchet.py` (⟡mypy-gate-cut), AND THE POINT IS THE ROSTER.
That file carries 198 findings, so it CANNOT BE EDITED — including by the edit that would
switch it to `substrate.promoted`, the clean roster that has `substrate` in it. Two population
declarations therefore disagree, and the gates compute from the old one. This module is the
half that can move.

⚑⚑⚑ AND MIGRATING IT ALMOST DELETED ITS REASON FOR EXISTING. `gate_main.run_gate` could
return 0 or 1 — pass, or debt grew — with no way to say *the census could not be taken*. That
branch is the whole reason this gate exists: **0 keys over 60 unannotated files** was once
banked as clean when a `python3` without mypy produced no error lines. A wholesale migration
would have looked like a simplification and silently dropped the refusal. `gate_main.
Unmeasurable` was added for it; the exit-2 path is not an extra, it is the load-bearing one.

    type_gate.py            # the gate: exit 1 on any NEW census key, 2 if mypy cannot run
    type_gate.py --quiet    # silent on success (hook form) — never silent on CANNOT MEASURE
    type_gate.py --list     # enumerate the census, every `<code>::<relpath>` key
"""

from __future__ import annotations

import sys
from pathlib import Path

from mikemol.corpus import tree_root
from mikemol.ratchet.render import Report

from substrate import corpus, mypy_census, promoted
from substrate.gate_main import Gate, Unmeasurable, run_gate

# ⚑ THE BASELINE STAYS WHERE THE GATES KEEP THEIRS. Moving the ledger with the code would
# orphan a recorded census and read as a paid-down gate — the baseline IS the debt, and a
# debt whose ledger moved has not been paid.
BASELINE = str(corpus.ROOT / "scripts" / "mypy_ratchet_baseline.txt")

# How much of a message to show beside its key.
_EXCERPT = 70

# ⚑ A MODULE CONSTANT BECAUSE `EM101` REFUSES A LITERAL AT THE RAISE, and correctly: the
# reason a gate cannot measure is a fact worth naming once rather than retyping.
_NOT_INSTALLED = "mypy is not installed for this interpreter"


class MypyUnavailable(Unmeasurable):
    """mypy could not produce a census — install it for THIS interpreter.

    ⚑ THE REMEDY NAMES `sys.executable`'s ENVIRONMENT, NOT A GENERIC INSTALL. The original
    defect was exactly an interpreter mismatch: under `uv run --with mypy`, mypy exists for
    THAT interpreter and a bare `python3` subprocess is a different one, so the run failed,
    the parse found no error lines, and zero keys was banked as clean.
    """

    remedy = "uv run --with mypy python3 -m substrate.type_gate"


# ⚑ THE MESSAGES ARE HELD FOR RENDERING ONLY, NEVER FOR THE VERDICT. The ratchet compares
# KEYS; two mypy runs can word one finding differently while keying identically, so a message
# in the comparison would report churn the baseline cannot see.
#
# ⚑⚑ AND THE STORE IS REACHED THROUGH `hold_messages`, NOT AS A GLOBAL A CALLER POKES. Its
# suite tripped `SLF001` reaching in to set up a render case, and that refusal named a real
# design fault rather than a test inconvenience: module state that only a private poke can
# establish is state the interface does not admit exists. A gate whose renderer cannot be
# exercised without violating its own encapsulation has an untestable renderer.
_MESSAGES: dict[str, list[str]] = {}


def hold_messages(rows: dict[str, list[str]]) -> None:
    """Replace the messages held for rendering. The verdict never reads them."""
    _MESSAGES.clear()
    _MESSAGES.update(rows)


def census() -> list[str]:
    """Return the census keys over the promoted corpus.

    ⚑ RAISES RATHER THAN RETURNING EMPTY. `mypy_census.type_errors` reports its inability to
    run as `None` or an `UNRUNNABLE` sentinel, and a caller that folds either into "no keys"
    certifies its own blind spot. The exception carries the reason mypy actually gave — "not
    importable" was once a guess printed as a fact, when a config error, a duplicate module
    name and an unreadable path all exit the same way and want different fixes.

    ⚑⚑⚑ AND THE LABEL RAISED FROM A BORROWING CHECKOUT (gate-G245 / gate-G256 / gate-G258). This
    takes NO root parameter, so it reaches `corpus.ROOT` as a module global while `corpus.py_files`
    walks the caller's cwd — two independently-derived roots, which is the whole defect. A peer
    running substrate's gates from their own tree got a `ValueError` before any verdict existed,
    so the gate could neither pass nor refuse: it died.

    ⚑⚑ IT WAS HELD BACK ONE TICK LONGER THAN THE OTHERS BY RULING, because `gate_population
    --gates` lists this file and an edit to a commit-path gate belongs to the gate review rather
    than the crash-repair lane — the lane is decided by the OBJECT touched, not the size of the
    change. Released on the measurement that the gate-side population is this ONE site: the
    intersection of the gate roster with the live borrowed-root roster is two, and the other was
    execution-refuted. `tree_root` carries one root and does both.
    """
    tree = tree_root.of(corpus.ROOT)
    files = [tree.label(Path(f)) for f in corpus.py_files(*promoted.POPULATION)]
    rows = mypy_census.type_errors(files)
    if rows is None:
        raise MypyUnavailable(_NOT_INSTALLED)
    if mypy_census.UNRUNNABLE in rows:
        raise MypyUnavailable(rows[mypy_census.UNRUNNABLE][0])
    hold_messages(rows)
    return sorted(rows)


def render(key: str) -> str:
    """Render one census key with an excerpt of its first message.

    ⚑⚑ THE COUNT USES AN ASCII `x`, AND THE FIX WAS THE NOTATION RATHER THAN A SUPPRESSION
    (operator: *"the general solution is probably to use the _other_ standard … if you use the
    encoding as I did, you probably won't trip ruf001"*). The pre-cut gate emits a
    MULTIPLICATION SIGN and is grandfathered; the first draft here treated that as a
    compatibility requirement and went looking for somewhere to hide a `RUF001` exemption.

    ⚑ BUT `RUF001` FLAGS VISUAL AMBIGUITY, AND THE ANSWER TO "THIS CHARACTER IS AMBIGUOUS" IS
    TO WRITE UNAMBIGUOUSLY — not to assert that this particular ambiguity is fine. A count
    reads identically either way, so the glyph was decoration promoted to a requirement.

    ⚑ AND THE FIRST ATTEMPT TO EXPLAIN THIS TRIPPED THE SAME RULE: the docstring arguing
    against the character contained it. A rule about a character does not exempt the prose
    about the rule, which is the same shape as a comment that documents an escaping bug and
    is broken by escaping.
    """
    msgs = _MESSAGES.get(key) or []
    if not msgs:
        return key
    return f"{key}  ({len(msgs)}x — e.g. {msgs[0][:_EXCERPT]})"


GATE = Gate(label="mypy-ratchet", census=census, baseline_path=BASELINE)

REPORT = Report(
    noun="type errors",
    render=render,
    refuse_hint=(
        "A NEW static-type error in PROMOTED python. Fix the error at the site;\n"
        "  do not add a `# type: ignore` and do not widen a signature to `Any`.\n"
        "  Enumerate the census with:  type_gate.py --list"
    ),
)


def main(argv: list[str]) -> int:
    """Run the gate. 0 = clean, 1 = the census grew, 2 = it could not be taken."""
    return run_gate(GATE, REPORT, argv)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
