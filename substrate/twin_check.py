#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Report which files at an OLD path have a verified promoted twin, and are safe to delete.

⚑⚑ THIS EXISTS BECAUSE THE NEXT STEP IS A DELETION, AND THE OPERATOR SCOPED IT PRECISELY:
*"we will only delete the files that have been promoted, and take care not to delete any which
have not."* Eyeballing eleven filenames against a directory listing is exactly the judgement
that belongs in a program — it evaporates when the turn ends, and its failure mode is
unrecoverable in a way a wrong census is not.

⚑⚑⚑ SAME-NAME IS NOT SAME-FILE, AND THAT IS THE WHOLE RISK. A twin must exist AND be the
module that moved — not a coincidental name collision, not a stale half-copy, not a file whose
imports were repointed while its body drifted. So this compares BODIES, ignoring only the
import lines that necessarily changed, and reports any other difference as a refusal.

⚑ IT NAMES WHAT IT WOULD KEEP, NOT ONLY WHAT IT WOULD REMOVE. `ratchet_legacy` was
deliberately NOT promoted — it is the twelve-argument adapter whose exemption exists to be
deleted with its call sites — so a report listing only removable files would make its absence
look like an oversight rather than a decision.

⚑ A REPORT, NEVER A DELETER. It prints verdicts and exits; the removal is a separate act by a
human who read them. A tool that both decides and destroys gives its own verdict nothing to
check it.

    twin_check.py                    # every module this session promoted
    twin_check.py <name> [<name>...] # just these
"""

from __future__ import annotations

import sys

from substrate import corpus

# The modules ⟡gate-island-promote moved. Named explicitly rather than discovered, because a
# DISCOVERED list would sweep in every same-named pair in the tree — and the population for a
# deletion must be the set someone intended to move, not the set that happens to match.
PROMOTED = (
    "baseline_io",
    "baseline_state",
    "proc_ancestry",
    "ratchet_flags",
    "withheld_verdict",
    "ratchet_core",
    "ratchet_core_selftest",
    "ratchet_suites",
    "gate_main",
)

# ⚑ NOT PROMOTED, AND THE REASON IS RECORDED SO THE ABSENCE READS AS A DECISION.
KEPT = {
    "ratchet_legacy": (
        "the 12-argument adapter for 20 unmigrated call sites; its pyproject exemption "
        "exists to be DELETED when they move to Census.of, so copying it would duplicate "
        "debt whose purpose is to disappear"
    ),
    "ratchet": (
        "the re-export facade 38 check_argv call sites import FROM; it was REPOINTED at the "
        "promoted island, not moved — moving it would break every consumer at once"
    ),
}

_OLD = "from scripts."
_NEW = "from substrate."
_OLD_MOD = "from scripts import"
_NEW_MOD = "from substrate import"

# Verdicts, ordered so refusals print first.
_ORDER = {"NO TWIN": 0, "DRIFTED": 1, "GONE": 2, "KEEP": 3, "REMOVABLE": 4}


def _normalise(text: str) -> str:
    """Return a body with the import rewiring undone, so only real drift remains.

    ⚑ THE IMPORT LINES ARE THE ONE DIFFERENCE A PROMOTION MUST INTRODUCE, so comparing them
    would report every correctly-moved file as drifted — and a check that always fires teaches
    a reader to ignore it. Everything else must match exactly.
    """
    return text.replace(_NEW_MOD, _OLD_MOD).replace(_NEW, _OLD)


def verdict(name: str) -> tuple[str, str]:
    """Return (state, detail) for one module: KEEP, REMOVABLE, GONE, or a refusal."""
    if name in KEPT:
        return ("KEEP", KEPT[name])
    old = corpus.ROOT / "scripts" / f"{name}.py"
    new = corpus.ROOT / "substrate" / f"{name}.py"
    if not old.is_file():
        return ("GONE", "no file at the old path — already removed, or never there")
    if not new.is_file():
        return ("NO TWIN", f"nothing at substrate/{name}.py — DO NOT DELETE")
    if _normalise(new.read_text(encoding="utf-8")) != old.read_text(encoding="utf-8"):
        return ("DRIFTED", "the twin differs beyond its import lines — DO NOT DELETE")
    return ("REMOVABLE", f"identical to substrate/{name}.py modulo imports")


def _rank(row: tuple[str, str, str]) -> tuple[int, str]:
    """Sort key: refusals first, then by name.

    ⚑ A NAMED FUNCTION, NOT A LAMBDA — the third instance today. `sort`'s `key=` is typed over
    an unbound parameter, so a lambda's row is `Any` and the tuple it builds is `Any` with it.
    Declaring the parameter types the whole expression.
    """
    return (_ORDER.get(row[1], 0), row[0])


def report(names: tuple[str, ...]) -> tuple[list[str], int]:
    """Render a verdict per module, refusals first. Returns (lines, blocked count)."""
    rows: list[tuple[str, str, str]] = [(name, *verdict(name)) for name in names]
    rows.sort(key=_rank)
    out = [f"  {state:<10} {name:<24} {detail}" for name, state, detail in rows]
    removable = sum(1 for _n, s, _d in rows if s == "REMOVABLE")
    blocked = sum(1 for _n, s, _d in rows if s in ("NO TWIN", "DRIFTED"))
    kept = sum(1 for _n, s, _d in rows if s == "KEEP")
    out.append(f"twin-check: {removable} removable · {blocked} BLOCKED · {kept} kept by decision")
    if blocked:
        out.append("  ⚑ a BLOCKED module has no verified twin. Deleting it loses the file.")
    return (out, blocked)


def main(argv: list[str]) -> int:
    """Report on the named modules, or on everything promoted. 1 if any is blocked."""
    names = tuple(a for a in argv[1:] if not a.startswith("-")) or (*PROMOTED, *KEPT)
    lines, blocked = report(names)
    sys.stdout.write("\n".join(lines) + "\n")
    return 1 if blocked else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
