# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""The cases for `substrate.witness_resolves` — and three of them are the monolith's own.

⚑⚑⚑ A REPLACEMENT IS NOT READY UNTIL IT PASSES WHAT THE ORIGINAL PINNED. `scratch/bibstruct.py`'s
suite carries three cases over this guard, and they are reproduced here against the live tree
rather than paraphrased: a key with no witness must REFUSE, a hyphenated key whose witness is
UPPER_SNAKE must be ACCEPTED, and a key that is defined but NOT REGISTERED must REFUSE. Those are
the behaviour, and a drain that quietly changes one is a rewrite wearing a refactor's clothes.

⚑⚑ THE THIRD IS THE LOAD-BEARING ONE. The original needed two regexes to approximate *"defining
the function is not registering the item"*; asking the resolver honours it for free, because the
resolver IS the registry. That is why this is not a loosening: the new predicate is the same
question the gate asks at check time.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from substrate import corpus, label_lease, witness_resolves


def _cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every case."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    # ── locating the project's witness module ────────────────────────────────
    # ⚑ THE PROJECT OWNS THE VERB, and the origin hardcoded one path until the first OTHER
    # paperkit project in the tree could not file a single entry.
    beside = witness_resolves.witness_module(
        str(corpus.ROOT / ".claude" / "agents" / "gate-oracle.bib")
    )
    check(
        "a bib beside its own witness module resolves to that module",
        passed=beside is not None and beside.name == "findings.py",
    )

    fallback = witness_resolves.witness_module(
        str(corpus.ROOT / "catalog" / "worklist" / "warrants.bib")
    )
    check(
        "a bib with no sibling witness falls back to the library's items.py",
        passed=fallback is not None and fallback.name == "items.py",
    )

    # ── the three cases the monolith's suite pins ────────────────────────────
    items = corpus.ROOT / "catalog" / "library" / "items.py"
    if not items.exists():
        check("the library's items.py is present to probe", passed=False)
        return out

    # ⚑ CASE 1 — a key naming no witness must REFUSE. Such an entry is
    # ordered-but-never-closable, which is worse than absent: the ordering surfaces it forever.
    check(
        "a key with no witness does not resolve",
        passed=not witness_resolves.resolves(items, "NoSuchWitness"),
    )

    # ⚑ CASE 2 — a hyphenated key whose witness is UPPER_SNAKE must be ACCEPTED. The original
    # refused `D0-kernel` on its own correct witness, and a guard that refuses the population it
    # governs reads as strictness while being a defect.
    check(
        "a hyphenated key whose item is OPEN still resolves",
        passed=witness_resolves.resolves(items, "T28-edges"),
    )

    # ⚑⚑ CASE 3 — DEFINED IS NOT REGISTERED, and this is the one the text scan needed two regexes
    # to approximate. `_open` is not a registered item, so it must not resolve.
    check(
        "a key that is not registered does not resolve",
        passed=not witness_resolves.resolves(items, "_open"),
    )

    # ── the exit-code distinction, stated as its own case ────────────────────
    # ⚑⚑⚑ OPEN IS NOT UNRESOLVED, and conflating them would refuse the entire live worklist. An
    # open item exits 1; only an unknown key exits 2.
    check(
        "an OPEN item is allowed, not refused",
        passed=witness_resolves.resolves(items, "T28-edges")
        and not witness_resolves.resolves(items, "NoSuchWitness"),
    )

    # ── an unrunnable probe refuses rather than passing ──────────────────────
    # ⚑ THE SAFE DIRECTION. A witness nobody can reach cannot close an item, so an unreachable
    # probe must not admit the entry.
    check(
        "a probe against a missing module does not resolve",
        passed=not witness_resolves.resolves(corpus.ROOT / "no-such-module.py", "K"),
    )

    # ── the messages name what to do ─────────────────────────────────────────
    check(
        "the refusal names the key and the module",
        passed="NoSuchWitness" in witness_resolves.refusal(items, "NoSuchWitness")
        and "items.py" in witness_resolves.refusal(items, "NoSuchWitness"),
    )
    check(
        "and says the witness must exist first",
        passed="must exist FIRST" in witness_resolves.refusal(items, "K"),
    )
    check(
        "the missing-module message names where it looked",
        passed=all(
            name in witness_resolves.missing_module(str(corpus.ROOT / "x.bib"), "K")
            for name in witness_resolves.WITNESS_NAMES
        ),
    )

    # ── a hang-guard crossing is a CAUSE, never "no witness" (gate-G453) ─────
    # ⚑⚑ The G453 witness PASSES in 86 s and was refused twice as "resolves to no witness ...
    # exits 2" by a 60 s wall timeout — a reading of the box printed as a fact about the roster.
    # Driven with a one-second guard against a module that sleeps, so the arm is cheap.
    with tempfile.TemporaryDirectory() as where:
        sleeper = Path(where) / "items.py"
        sleeper.write_text("import time\ntime.sleep(30)\n", encoding="utf-8")
        crossed = witness_resolves.probe(sleeper, "K", timeout_s=1)
    check("a probe past the hang guard does not resolve", passed=not crossed.resolved)
    check(
        "and carries the crossing as its cause, with the CPU it burned",
        passed="hang guard" in crossed.cause and "CPU" in crossed.cause,
    )
    told = witness_resolves.refusal(sleeper, "K", crossed.cause)
    check(
        "the refusal with a cause does NOT claim the resolver exited 2",
        passed="hang guard" in told and f"exits {witness_resolves.UNKNOWN_KEY}" not in told,
    )
    # ⚑ AND THE RESOLVER'S OWN UNKNOWN-KEY ANSWER STILL SAYS SO — the cause is empty there, so the
    # exit-2 clause is printed exactly when the resolver produced it.
    check(
        "an unknown key carries no cause and the refusal names the exit code",
        passed=witness_resolves.probe(items, "NoSuchWitness").cause == ""
        and f"exits {witness_resolves.UNKNOWN_KEY}"
        in witness_resolves.refusal(items, "NoSuchWitness"),
    )
    check(
        "the guard is a multiple of a CPU ceiling, not a bare wall number",
        passed=witness_resolves.TIMEOUT_S
        == witness_resolves.CPU_CEILING_S * label_lease.HANG_MULTIPLE,
    )

    # ── the constant is named, not spelled at a call site ────────────────────
    check("the unknown-key exit code is declared", passed=witness_resolves.UNKNOWN_KEY == 2)  # noqa: PLR2004 — pinning the declared value

    return out


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = _cases()
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            print(f"  FAIL {label}")  # noqa: T201
    print(f"witness-resolves selftest: {ok}/{len(cases)}")  # noqa: T201
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    import sys

    if "--selftest" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(0 if selftest() else 1)
    raise SystemExit(0)
