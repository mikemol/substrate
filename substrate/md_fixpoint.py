# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Decide whether normalization is IDEMPOTENT — whether `normalize(normalize(x))` equals it.

⚑⚑⚑ THE QUESTION THAT ACTUALLY DECIDES THE WRITE PATH (operator, 2026-08-01: *"Not strictly true.
The question becomes whether or not the document can be normalized, found to be satisfactory, and
then subsequent modifications roundtrip."*). The reasoning it replaced was: pandoc reflows the
input, therefore a transform is unusable — the either/or trap, treating PRESERVES-THE-INPUT and
UNUSABLE as the only options. If `normalize(normalize(x)) == normalize(x)` then a one-time accepted
reflow moves the document TO the fixpoint and every subsequent transform round-trips exactly. The
one-time diff is a reviewable migration, not a permanent tax, and the drift measured against the
ORIGINAL is the wrong number to judge by because it is paid once.

⚑⚑ AND THE TERMINATION RULE HAS BEEN WRONG TWICE, IN OPPOSITE DIRECTIONS. Each is recorded here
because each produced a confident false verdict:

  A ROUND CAP READ A CONVERGING SEQUENCE AS DIVERGENT. Three rounds gave `[1340, 899, 561]` and
  that was called *"diverges monotonically"* — the exact opposite of what those numbers say, since
  a DECREASING delta is the signature of a sequence approaching a fixpoint. Run to convergence the
  same document gives `[1340, 899, 561, 400, 320, 176, 0]`. A cap is a CAPABILITY bound dressed as
  a termination bound, and this repo had already paid for that distinction once in
  `agda_lex.head_span`, where a `j - i < 6` limit silently dropped 136 of 401 multi-line headers.

  THEN STRICT DECREASE READ A PLATEAU AS A CYCLE. Requiring every step to be strictly smaller made
  `[…, 92, 56, 56]` a STALL, and a docstring claiming convergence is non-monotone in column width
  was written on that reading and a survey built around it. MEASURED past the guard,
  `catalog/plan.md` at `--columns=120` goes `[686, 571, 312, 114, 92, 56, 56, 56, 34, 34, 34, 0]`
  — it CONVERGES in twelve rounds, descending in PLATEAUS, because pandoc re-emits a block group at
  a time and several rounds move the same count while different blocks settle.

⚑ SO THE WELL-FOUNDED ARGUMENT NEEDS NO INCREASE PLUS EVENTUAL MOVEMENT, NOT STRICTNESS. A repeat
is progress-so-far, not a fixpoint failure. The honest stops are `n == 0` (converged) and a delta
that GROWS (genuinely diverging), with a plateau budget so a true cycle still ends.

⚑⚑ AND THE CONVERGED TEXT IS RETURNED, WHICH IS WHY THE PAYDOWN NEVER HAPPENED BEFORE. The origin
ran the document all the way to its fixpoint and returned only the DELTAS, so `--table-style` could
report *"48 rows → 0 after one pass"* while nothing could write that result — and the warnings kept
firing on every edit and got dismissed as pre-existing four times (operator: *"this shouldn't
happen; this is why we built the markdown structural manipulation tooling"*). That is what a census
with no apply trains a reader to do. The answer was one return value away, not a build.

⚑⚑⚑ THIS TAKES A NORMALIZER, NOT A PATH, AND THAT IS THE WHOLE TESTABILITY GAIN. The origin opened
the file and shelled to pandoc, so every termination rule above could only be exercised against a
real document with a real converter — which is precisely why two wrong rules survived measurement.
A caller supplies `normalize`; a case supplies a sequence it chooses, and each rule gets an arm.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, NamedTuple

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

#: How many EQUAL deltas in a row before a plateau is called a cycle. A TERMINATION bound — a
#: repeat that never breaks is genuinely stuck — never a capability bound. The measured worst
#: plateau on this corpus is three.
PLATEAU_BUDGET = 8


class Run(NamedTuple):
    """What iterating to a fixpoint found, including the text it converged on.

    ⚑ `converged` AND `deltas` ARE DIFFERENT FACTS. The verdict says whether a fixpoint exists;
    the sequence says how it got there, and the shape of that sequence is what two wrong
    termination rules were diagnosed from. Returning only the verdict would make the next wrong
    rule undiagnosable.
    """

    converged: bool
    deltas: tuple[int, ...]
    text: str
    why: str

    @property
    def rounds(self) -> int:
        """Return how many normalization rounds ran."""
        return len(self.deltas)


def changed_lines(before: str, after: str) -> int:
    """Return how many lines differ between two texts.

    ⚑ A LINE COUNT, NOT A CHARACTER COUNT, because the sequence being judged is a sequence of
    EDITS and a reflow moves whole lines. A character delta would make a rewrapped paragraph look
    like churn proportional to its width rather than to how much settled.
    """
    old, new = before.split("\n"), after.split("\n")
    width = max(len(old), len(new))
    old += [""] * (width - len(old))
    new += [""] * (width - len(new))
    return sum(1 for a, b in zip(old, new, strict=True) if a != b)


def _verdict(deltas: Sequence[int], flat: int) -> tuple[bool, str] | None:
    """Return `(converged, why)` when the sequence has decided, or None to keep going."""
    if not deltas:
        return None
    n = deltas[-1]
    if n == 0:
        return (True, f"converged after {len(deltas)} round(s)")
    if len(deltas) > 1 and n > deltas[-2]:
        return (False, f"diverging: {deltas[-2]} -> {n}")
    if flat >= PLATEAU_BUDGET:
        return (False, f"cycle: {n} unchanged across {flat} round(s)")
    return None


def run(src: str, normalize: Callable[[str], str], rounds: int | None = None) -> Run:
    """Iterate `normalize` to a fixpoint, returning the verdict, the sequence and the text.

    ⚑ `rounds` SURVIVES ONLY AS A RUNAWAY GUARD for a pathological input, defaulting to None —
    unbounded — which is the shape `agda_lex.head_span` settled on after its cap was measured to
    drop a third of its population. It is not the termination argument, which is the deltas.
    """
    cur = normalize(src)
    deltas: list[int] = []
    flat = 0
    while rounds is None or len(deltas) < rounds:
        nxt = normalize(cur)
        n = changed_lines(cur, nxt)
        flat = flat + 1 if deltas and n == deltas[-1] else 0
        deltas.append(n)
        cur = nxt
        decided = _verdict(deltas, flat)
        if decided is not None:
            return Run(decided[0], tuple(deltas), cur, decided[1])
    return Run(
        converged=False,
        deltas=tuple(deltas),
        text=cur,
        why=f"round guard hit at {rounds} — NOT a verdict about convergence",
    )
