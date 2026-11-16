# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""The cases for `substrate.agda_dag` — the import model, checked against the live tree.

⚑⚑⚑ THE EXTRACTION IS ONLY WORTH ANYTHING IF IT AGREES WITH THE ORIGIN, and the origin's output
is already on disk: `agda/Flat.mk` was generated from the same parse, so its declared `MODULES`
list is a witness this model can be measured against without running the generator. A rewritten
model that quietly disagrees about the build graph is worse than no model — it would reorder a
build, or drop an edge, and the failure would surface as a mysterious compile error far away.

⚑⚑ AND THE AGREEMENT IS ASSERTED AS A SUPERSET-WITH-A-REASON, not as equality. The generator
enumerates from the same walk, so the module sets should match exactly; where they could
legitimately differ is the tree ROOT (`agda/Substrate.agda` sits outside the include root and is
not a declared module), which is the same boundary `public_census` found a real violation behind.
Pinning the direction makes a future divergence readable instead of alarming.
"""

from __future__ import annotations

from substrate import agda_dag, corpus, make_rules


def _cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every case."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    # ── the fixture graph: shape, order, and the reverse relation ────────────
    # ⚑ A HAND GRAPH FIRST, because a live-tree case cannot distinguish "correct" from
    # "consistently wrong in the same way as the thing it is compared to".
    dag = agda_dag.Dag(
        disk={"A": "A.agda", "B": "B.agda", "C": "C.agda"},
        deps={"A": frozenset(), "B": frozenset({"A"}), "C": frozenset({"B"})},
    )
    got = agda_dag.topo(dag)
    check("a chain topo-sorts", passed=not isinstance(got, agda_dag.Cycle))
    if not isinstance(got, agda_dag.Cycle):
        depth, order = got
        # ⚑ THE DEPTH IS THE CHAIN LENGTH, which is the number no `-j` width can beat.
        check("and its depth is the chain length", passed=depth == len(dag.disk))
        check(
            "and a dependency precedes its dependent",
            passed=order.index("A") < order.index("B") < order.index("C"),
        )
    check("the reverse relation points the other way", passed=dag.rdeps["A"] == frozenset({"B"}))
    check("and src_to_mod inverts disk", passed=dag.src_to_mod["A.agda"] == "A")

    # ── a cycle is a VALUE, not an exit ──────────────────────────────────────
    # ⚑⚑ THE ORIGIN CALLED `sys.exit(2)` HERE, so the acyclicity question could not be asked —
    # only survived. This case cannot even be WRITTEN against the origin's shape.
    cyclic = agda_dag.Dag(
        disk={"X": "X.agda", "Y": "Y.agda"}, deps={"X": frozenset({"Y"}), "Y": frozenset({"X"})}
    )
    verdict = agda_dag.topo(cyclic)
    check("a cycle is returned rather than exiting", passed=isinstance(verdict, agda_dag.Cycle))
    check(
        "and it names its members",
        passed=isinstance(verdict, agda_dag.Cycle) and set(verdict.members) == {"X", "Y"},
    )
    check(
        "and the message says a build would hang",
        passed=isinstance(verdict, agda_dag.Cycle) and "hang" in verdict.message,
    )
    check("is_acyclic agrees with topo", passed=not agda_dag.is_acyclic(cyclic))

    # ── the import pattern: a non-ASCII module name is a WHOLE name, not a truncated one ──
    # ⚑⚑⚑ OWED SINCE t103. The pattern here was ASCII-only (`[A-Za-z0-9_.'-]+`), so
    # `IsAñeléTerminal` parsed as `IsA` — a name matching no module — and the edge vanished;
    # the origin had already measured 8 such edges over 5 modules. No case exercised it, so every
    # suite over this module was green with the defect in place. The fixture is the shape the
    # origin found; the control proves the ASCII path is unchanged.
    def names(text: str) -> set[str]:
        return {str(m.group(1)) for m in agda_dag.IMPORT_RE.finditer(text)}

    check(
        "a non-ASCII module name is captured whole",
        passed=names("open import X.IsAñeléTerminal\n") == {"X.IsAñeléTerminal"},
    )
    check(
        "an ASCII name is captured unchanged (control)",
        passed=names("import Substrate.Foundation.Eq\n") == {"Substrate.Foundation.Eq"},
    )
    check(
        "a trailing `using (…)` clause is cut at the delimiter",
        passed=names("open import A.PriorAñelé using (x)\n") == {"A.PriorAñelé"},
    )

    # ── the live tree: does the model agree with the generated makefile? ─────
    flat = corpus.ROOT / "agda" / "Flat.mk"
    if not flat.exists():
        check("Flat.mk is present to compare against", passed=False)
        return out

    live = agda_dag.parse()
    declared = set(make_rules.modules(make_rules.read(flat)))
    check("the live tree parses into many modules", passed=len(live.disk) > 1)
    check("and it is acyclic, as the build requires", passed=agda_dag.is_acyclic(live))
    # ⚑ THE POSITIVE CONTROL ON REAL DATA: the tree the origin measured HAS non-ASCII import
    # targets (e.g. `IsAñeléTerminal`), so at least one live edge must name one. Under the old
    # pattern this set was empty — the case fails exactly when the defect returns.
    check(
        "some live edge targets a non-ASCII module name",
        passed=any(not d.isascii() for deps in live.deps.values() for d in deps),
    )

    # ⚑⚑⚑ THE AGREEMENT CASE. Both sets come from the same walk, so a module the generator
    # declared and this model cannot see is a REAL divergence in the extraction.
    missing = declared - set(live.disk)
    check("every module the generated makefile declares is in the model", passed=not missing)

    # ⚑ AND THE ROOT IS THE KNOWN, NAMED EXCEPTION IN THE OTHER DIRECTION. `agda/Substrate.agda`
    # is outside the include root, so it is not a declared module — the same boundary
    # `public_census` found an unseen re-export behind.
    check(
        "the tree's top-level module is not a declared build target",
        passed="Substrate" not in declared,
    )

    return out


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = _cases()
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            print(f"  FAIL {label}")  # noqa: T201
    print(f"agda-dag selftest: {ok}/{len(cases)}")  # noqa: T201
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    import sys

    if "--selftest" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(0 if selftest() else 1)
    raise SystemExit(0)
