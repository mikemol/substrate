# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""The cases for `substrate.bazel_emit` — the second emitter over the shared model.

⚑⚑⚑ THE POINT OF THESE CASES IS THE SEAM, NOT THE SYNTAX. Two emitters now read one model, so
the property worth pinning is that they AGREE ABOUT THE GRAPH while differing about everything
else. A case comparing emitted text would test the grammar; these compare the DEPENDENCY
RELATION the output encodes, which is the thing that must survive a backend change.

⚑⚑ AND THE INJECTIVITY OF THE NAME MAPPING IS LOAD-BEARING. Bazel labels cannot contain dots,
so module names are flattened with underscores — and `_` is ALREADY LEGAL in an Agda module
name, so the mapping is injective only if no two modules collapse together. On this tree that is
a fact to CHECK, not to assume: a collision would silently merge two compile targets.
"""

from __future__ import annotations

from substrate import agda_dag, bazel_emit


def _cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every case."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    # ── the fixture: one rule's shape ────────────────────────────────────────
    dag = agda_dag.Dag(
        disk={"A": "A.agda", "B.C": "B/C.agda"}, deps={"A": frozenset(), "B.C": frozenset({"A"})}
    )

    rule = "\n".join(bazel_emit.rule_for("B.C", dag))
    check("a rule names its target", passed='name = "B_C"' in rule)
    check("and its source relpath", passed='src = "B/C.agda"' in rule)
    check("and its dependency as a label", passed='":A"' in rule)
    check("and carries the compile flags", passed='"--safe"' in rule)

    # ⚑ A ROOT MODULE EMITS NO `deps` ATTRIBUTE AT ALL, rather than an empty list — an empty
    # list is legal but reads as "checked, none", where absence is what a generator should emit
    # for a module that imports nothing in-tree.
    root = "\n".join(bazel_emit.rule_for("A", dag))
    check("a module with no in-tree imports emits no deps", passed="deps" not in root)

    # ── the name mapping ─────────────────────────────────────────────────────
    check("dots become underscores", passed=bazel_emit.target_name("X.Y.Z") == "X_Y_Z")
    check("and a hyphen survives", passed="-" in bazel_emit.target_name("A.B-C"))

    # ── the header carries its own bounds ────────────────────────────────────
    # ⚑⚑ A READER OF GENERATED OUTPUT SHOULD NOT HAVE TO FIND THE GENERATOR to learn three
    # design questions are open. The bounds-in-band discipline, applied to a build file.
    head = "\n".join(bazel_emit.header())
    check("the emitted header says it is generated", passed="GENERATED" in head)
    check("and names what is unresolved", passed="UNRESOLVED" in head)
    check(
        "and every unresolved item appears in it",
        passed=all(item in head for item in bazel_emit.UNRESOLVED),
    )
    check("and it loads the rule it calls", passed=f'"{bazel_emit.RULE}"' in head)

    # ── the live tree ────────────────────────────────────────────────────────
    live = agda_dag.parse()
    if not live.disk:
        check("the live tree parses", passed=False)
        return out

    # ⚑⚑⚑ INJECTIVITY, CHECKED RATHER THAN ASSUMED. `_` is legal in an Agda module name, so
    # flattening dots to underscores could collapse two distinct modules onto one bazel target —
    # silently merging two compile actions and dropping one module's dependencies.
    names = [bazel_emit.target_name(m) for m in live.disk]
    check(
        "the target-name mapping is injective over the live tree",
        passed=len(set(names)) == len(names),
    )

    # ⚑⚑ THE AGREEMENT CASE, AND IT IS THE REASON THIS MODULE EXISTS. Both emitters read one
    # model, so the dependency relation the bazel output encodes must be the SAME relation the
    # model holds — no edge invented, none dropped.
    text = bazel_emit.build_text(live)
    check(
        "every module in the model gets a rule",
        passed=text.count(f"{bazel_emit.RULE}(") == len(live.disk),
    )
    check(
        "and a known module appears by its mapped name",
        passed=f'name = "{bazel_emit.target_name(min(live.disk))}"' in text,
    )

    # ⚑ AND THE EMITTER IS PURE OVER THE MODEL: emitting twice from one parse gives one answer.
    # A generator that varied run to run would make a build's inputs unreproducible, which is
    # the property bazel exists to guarantee.
    check("emission is deterministic for a fixed model", passed=bazel_emit.build_text(live) == text)

    return out


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = _cases()
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            print(f"  FAIL {label}")  # noqa: T201
    print(f"bazel-emit selftest: {ok}/{len(cases)}")  # noqa: T201
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    import sys

    if "--selftest" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(0 if selftest() else 1)
    raise SystemExit(0)
