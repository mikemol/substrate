# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Baseline health for every ratchet gate — over every gate home, not one directory.

⚑⚑⚑ THE READING ITSELF IS NOT NEW; ITS POPULATION IS. `gate_census --baselines` already
answers "does this baseline exist, is it empty, how many keys" and its docstring is a record
of why that matters: ABSENT takes `set_ratchet`'s record-and-pass branch, so the gate exits 0
whatever it measured (a vacuous green), while EMPTY takes the normal branch against the empty
set, so every census member reads as a NEW key. Those are opposite verdicts that render as
adjacent-looking rows. What that mode cannot do is see a gate outside `scripts/`.

⚑⚑ SO A MIGRATED GATE LEAVES THE HEALTH TABLE SILENTLY. MEASURED: two gates now live in the
package — one of them running in the pre-commit hook — and neither appears. That is worse than
a wrong number, because the table's whole purpose is surfacing baselines nobody is looking at,
and a gate absent from it is exactly a baseline nobody is looking at. `gate_population` fixed
the population; this applies the existing reading to it.

⚑ THE STATE VOCABULARY IS BORROWED, NOT REDEFINED. `BaselineState` already carries
`is_defect` / `deserves_mark` / `gloss`, and its own notes record six sites re-deriving those
properties by string comparison with three getting it wrong. A second enum here would be the
seventh.

⚑⚑ AND A GATE WHOSE BASELINE CANNOT BE FOUND IS `UNREAD`, NEVER SKIPPED. That distinction is
the one the origin insists on and the one a scoped population loses: UNREAD says "this reader
could not resolve it", while omission says nothing at all. A gate that declares its baseline
in a form no regex here matches must still occupy a row.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from substrate import baseline_state, corpus, gate_population

# ⚑ TWO SPELLINGS, BOTH LIVE. A gate may declare `BASELINE = <path>` as a module constant, or
# pass the path INLINE at the `set_ratchet` call — and one gate carries TWO ratchets with two
# baselines that way, so a declaration-only reader structurally cannot see either. Matching any
# baseline literal in the file catches both without deciding which is canonical.
_LITERAL = re.compile(r"[\"']([\w.\-]*baseline[\w.\-]*\.txt)[\"']")

# Where the gates keep their ledgers. ⚑ THE BASELINE DOES NOT MOVE WITH THE CODE: a relocated
# ledger orphans a recorded census and reads as a paid-down gate, so a package gate's baseline
# still lives here.
BASELINE_DIR = "scripts"


@dataclass(frozen=True, slots=True)
class Row:
    """One gate's baseline, and what state it is in."""

    gate: str
    baseline: str
    state: baseline_state.BaselineState
    keys: int

    @property
    def is_defect(self) -> bool:
        """Whether this row is a degraded baseline rather than a healthy one."""
        return bool(self.state.is_defect)


def baselines_named(source: str) -> list[str]:
    """Return every baseline filename `source` names, in first-seen order.

    ⚑ ORDER-PRESERVING AND DE-DUPLICATED, because a gate naming its baseline in both a
    constant and a call site owns one baseline, not two — and a set would make the row order
    vary between runs, which turns a stable report into a spurious diff.
    """
    seen: list[str] = []
    for match in _LITERAL.finditer(source):
        name = match.group(1)
        if name not in seen:
            seen.append(name)
    return seen


def row_for(gate: str, baseline: str) -> Row:
    """Return the health row for one gate's baseline.

    ⚑⚑ EMPTY AND ABSENT ARE DIFFERENT AND THE DIFFERENCE DECIDES THE VERDICT. An absent file
    makes the gate record-and-pass whatever it measured; an empty one is zero-tolerance, the
    STRONGEST setting and never a defect. Collapsing them — which `Path.exists()` alone
    invites — would report the strongest configuration and the most vacuous one identically.
    """
    path = corpus.ROOT / BASELINE_DIR / baseline
    if not path.exists():
        return Row(gate, baseline, baseline_state.BaselineState.ABSENT, 0)
    text = path.read_text(encoding="utf-8", errors="replace")
    if not text.strip():
        return Row(gate, baseline, baseline_state.BaselineState.EMPTY, 0)
    keys = len([ln for ln in text.split("\n") if ln.strip()])
    return Row(gate, baseline, baseline_state.BaselineState.OK, keys)


def health() -> list[Row]:
    """Return a health row for every ratchet gate, across every declared home."""
    root = corpus.ROOT
    out: list[Row] = []
    for gate in gate_population.gates():
        source = (root / gate).read_text(encoding="utf-8", errors="replace")
        named = baselines_named(source)
        if not named:
            # ⚑ A ROW, NOT A SKIP. "This reader could not resolve it" is a finding about the
            # reader; dropping the gate would report it as a fact about the tree.
            out.append(
                Row(gate, "(no baseline literal found)", baseline_state.BaselineState.UNREAD, 0)
            )
            continue
        out.extend(row_for(gate, name) for name in named)
    return out


def degraded() -> list[Row]:
    """Return the rows whose state is a defect — the ones an operator must act on."""
    return [r for r in health() if r.is_defect]


def render() -> str:
    """Return the health table, defects marked."""
    rows = health()
    out = [f"{'gate':<44} {'baseline':<34} {'state':<7} keys"]
    out.extend(
        f"{r.gate:<44} {r.baseline:<34} {r.state!s:<7} {r.keys:<5}"
        + ("  ⚑" if r.state.deserves_mark else "")
        for r in rows
    )
    bad = len([r for r in rows if r.is_defect])
    out.append(
        f"\n{len(rows)} baseline(s) over {len(gate_population.gates())} gate(s) — {bad} degraded"
    )
    # ⚑ THE MISSES ARE PART OF THE READING. A health table that silently omits a gate is the
    # defect this module exists to correct, so its own blind spots are printed with it.
    out.extend(f"   ⚑ NOT COVERED — {path}: {why}" for path, why in gate_population.known_misses())
    return "\n".join(out) + "\n"


# ⚑⚑ THE TABLE HAD NO CLI, AND A READING NOBODY CAN ASK FOR IS ONE NOBODY READS (gate-G375).
# `render` and `degraded` were public, correct, and reachable only by importing this module —
# the missing-mode shape the standing rule names, in the module whose entire subject is
# baselines nobody is looking at. Running it bare printed NOTHING, which is indistinguishable
# from a clean tree.
USAGE = (
    "usage: baseline_health.py [--degraded]   the baseline state of every ratchet gate\n"
    "  (bare) the whole table, defects marked and blind spots named\n"
    "  --degraded  only the rows an operator must act on — exits 1 when any exist"
)

_DEGRADED = "--degraded"


if __name__ == "__main__":
    import sys

    if _DEGRADED in sys.argv:
        _bad = degraded()
        for _row in _bad:
            sys.stdout.write(f"{_row.gate:<44} {_row.baseline:<34} {_row.state!s}\n")
        # ⚑ SILENCE PLUS EXIT 0 IS THE HOUSE CONVENTION FOR CLEAN, and the denominator is said
        # out loud on the failing side so a zero is never mistaken for a census that read nothing.
        if _bad:
            sys.stdout.write(f"\n{len(_bad)} degraded baseline(s) of {len(health())} row(s)\n")
        sys.exit(1 if _bad else 0)
    sys.stdout.write(render())
    sys.exit(0)
