# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""The cases for `substrate.make_emit` — the emitted gate section, parsed back and compared.

⚑⚑⚑ THE ROUND TRIP IS THE CASE, AND IT IS STRUCTURAL RATHER THAN TEXTUAL. Emitting make syntax
and diffing strings against the live file would fail on a reflowed comment and pass on a recipe
that runs the wrong command — exactly backwards. So the emitted text is PARSED BY `make_rules`
and compared as TARGETS, which is what make itself reads.

⚑⚑ AND THE COMPARISON IS AGAINST THE LIVE `agda/Makefile`, the artefact the origin generated
from its three hand-maintained lists. That makes this a differential between the derivation and
the thing derived — the only check that catches a gate silently dropped in the extraction.

⚑ ONE ROW DIVERGES BY DESIGN. `check-public` now runs the migrated package gate, so its RECIPE
differs while its NAME must still match, and the two halves are asserted separately.
"""

from __future__ import annotations

from substrate import build_targets, corpus, make_emit, make_rules


def _cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every case."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    # ── the emitted text is well-formed make ─────────────────────────────────
    emitted = make_emit.text()
    parsed = make_rules.parse(emitted)
    check("the emitted section parses as a makefile", passed=bool(parsed.rules))

    # ⚑ EVERY DECLARED GATE BECOMES A REAL TARGET. A roster row that emitted no rule would be a
    # gate that silently stops running.
    absent = [name for name in build_targets.names() if not make_rules.has_target(parsed, name)]
    check("every declared gate is emitted as a target", passed=not absent)
    check("and the aggregate is emitted too", passed=make_rules.has_target(parsed, make_emit.CHECK))
    check(
        "and the advisory target is emitted",
        passed=make_rules.has_target(parsed, build_targets.ADVISE),
    )

    # ── the aggregate depends on every gate, in roster order ─────────────────
    # ⚑⚑ THE ORIGIN'S TWO LISTS HAD ALREADY DRIFTED: its `check:` prerequisites start with
    # `check-defproof` while its recipe blocks start with `check-makefiles`. Deriving both from
    # one roster is what makes the question unaskable.
    rules = parsed.rules_for(make_emit.CHECK)
    prereqs = tuple(rules[0].prereqs) if rules else ()
    check(
        "the aggregate depends on exactly the declared gates, in order",
        passed=prereqs == build_targets.names(),
    )

    # ⚑ THE ADVISORY TARGET IS NOT A PREREQUISITE. Folding it in would train a reader to ignore
    # a red build, since each advisory check has real false positives.
    check("and the advisory target is not among them", passed=build_targets.ADVISE not in prereqs)

    # ── a recipe carries the argv the roster declared ────────────────────────
    cap = parsed.rules_for("check-cap")
    check(
        "a gate's recipe runs the command the roster declares",
        passed=bool(cap) and any("check_cap_ratchet.py" in line for line in cap[0].recipe),
    )
    # ⚑ MAKE REQUIRES A LITERAL TAB. A recipe indented with spaces is a syntax error, and a
    # reflow that "tidied" it would break the build in a way no string diff would explain.
    check(
        "and every recipe line is tab-prefixed in the raw text",
        passed=all(
            line.startswith("\t") for line in emitted.splitlines() if line.strip().startswith("@")
        ),
    )

    # ── the .PHONY line covers the roster and whatever the emitter is handed ──
    phony = make_emit.phony_line(("all", "clean"))
    check(
        "the phony line names every gate",
        passed=all(name in phony for name in build_targets.names()),
    )
    check("and the targets it was handed", passed="all" in phony and "clean" in phony)
    # ⚑ THE CLI'S OWN SPELLING, exercised separately. `phony_text` is what `--phony` dispatches
    # to, and the coverage census caught it uncovered the moment the mode was added — a gap I
    # would otherwise have left behind my own repair.
    check(
        "the --phony mode renders a terminated line",
        passed=make_emit.phony_text().endswith("\n")
        and make_emit.phony_text().startswith(".PHONY:"),
    )

    # ── agreement with the LIVE makefile ─────────────────────────────────────
    root = corpus.ROOT / "agda" / "Makefile"
    if not root.exists():
        check("the root Makefile is present to compare against", passed=False)
        return out

    live = make_rules.read(root)
    # ⚑⚑⚑ THE DIFFERENTIAL. Every gate the live build runs must appear in the emitted section;
    # a missing one is a gate the extraction would silently retire.
    lost = [
        name
        for name in build_targets.names()
        if make_rules.has_target(live, name) and not make_rules.has_target(parsed, name)
    ]
    check("no gate the live makefile runs is lost by the emitter", passed=not lost)

    # ⚑⚑ THE INTENDED DIVERGENCE, PINNED. `check-public` keeps its name and changes its recipe.
    emitted_public = parsed.rules_for("check-public")
    check(
        "check-public is emitted",
        passed=bool(emitted_public) and make_rules.has_target(live, "check-public"),
    )
    check(
        "and its recipe names the package module rather than the retiring script",
        passed=bool(emitted_public)
        and any("substrate.public_gate" in line for line in emitted_public[0].recipe)
        and not any("check_public_ratchet" in line for line in emitted_public[0].recipe),
    )

    return out


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = _cases()
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            print(f"  FAIL {label}")  # noqa: T201
    print(f"make-emit selftest: {ok}/{len(cases)}")  # noqa: T201
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    import sys

    if "--selftest" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(0 if selftest() else 1)
    raise SystemExit(0)
