# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.flat_emit` — first and foremost, that the port IS the origin.

⚑⚑⚑ THE FIRST CASE IS DIFFERENTIAL AND IT IS THE ONE THAT MATTERS. With the origin's own graph
(`parse_tree`) and constants, `flat_emit.text` must equal the working-tree `agda/Flat.mk` byte for
byte. The graph and the constants are held fixed so that a mismatch can only be the EMITTER — which
is the thing being drained. On a mismatch the case names the first differing line, because the
diff is the finding and a bare `False` would send the next reader to re-derive it.

⚑ THE ORIGIN IS REACHED THROUGH `flat_origin`, the ONE loader `flat_render` also uses, so the
differential and the render tool cannot disagree about which module they read.
"""

from __future__ import annotations

import sys

from substrate import agda_dag, corpus, flat_emit, flat_origin

FLAT = corpus.ROOT / "agda" / "Flat.mk"


def _first_difference(got: str, want: str) -> str:
    """Name the first line where two renderings differ, or their length difference."""
    a, b = got.split("\n"), want.split("\n")
    for i, (x, y) in enumerate(zip(a, b, strict=False)):
        if x != y:
            return f"line {i + 1}:\n    port:   {x[:160]!r}\n    origin: {y[:160]!r}"
    return f"lengths differ: port {len(a)} lines, origin {len(b)} lines"


def _parameterized_cases(got: str, param: str) -> list[tuple[str, bool]]:
    """Return the cases on the tenant-parameterized rendering against the faithful one.

    ⚑ Every added line must carry the tenant or the runner, and every removed line must be one
    the parameterization had a reason to touch — so an accidental edit anywhere else in a
    ~20k-line makefile fails here rather than in a build.
    """
    was, now = set(got.split("\n")), set(param.split("\n"))
    added, removed = now - was, was - now
    touched = (
        *(f".{k}" for k in flat_emit.STAMP_KINDS),
        "sppf_db.py",
        " --live ",
        "reconcile-stamps",
    )
    return [
        (
            "every added line carries the tenant, its suffix, the runner or the venv python",
            all(any(t in x for t in ("TENANT", "TSFX", "STORE_RUN", "PYTHON")) for x in added),
        ),
        (
            "every removed line is a stamp, runner or tenant line",
            all(any(t in x for t in touched) for x in removed),
        ),
        (
            "no bare python3 sppf_db invocation survives parameterization",
            "python3 $(SCRIPTS)/sppf_db.py" not in param,
        ),
        ("no hard-coded --live survives parameterization", " --live " not in param),
        ("the tenant guard is emitted", "$(error TENANT must be live or sandbox)" in param),
        ("reconcile runs the tenant-aware reconciler", flat_emit.RECONCILE_RECIPE in param),
        (
            "the old live-only reconcile is gone from the parameterized file",
            "--reconcile-stamps" not in param,
        ),
        (
            "the stamp rule is suffixed in the parameterized makefile",
            "$(BUILD)/%.ingested$(TSFX): $(BUILD)/%.agdai" in param,
        ),
    ]


def _cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every case."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    origin = flat_origin.load()
    dag = flat_origin.graph(origin)
    settings = flat_emit_settings = flat_origin.settings()
    got = flat_emit.text(dag, flat_emit_settings)
    # ⚑⚑ THE FAITHFUL DIFFERENTIAL IS RETIRED, DELIBERATELY (t118): it held the faithful render
    # byte-for-byte against the ORIGIN generator's Flat.mk — last green 10/10 on t117, just before
    # the shim replaced the origin. The build now commits the TENANT-AWARE render, so the artefact
    # case compares THAT to the file.
    param = flat_emit.text(dag, flat_origin.settings(parameterized=True))
    want = FLAT.read_text(encoding="utf-8")
    same = param in {want, want.rstrip("\n")}
    if not same:
        sys.stdout.write(f"  DIFF {_first_difference(param, want)}\n")
    check("the committed Flat.mk IS the parameterized render", passed=same)
    out.extend(_parameterized_cases(got, param))

    cyclic = agda_dag.Dag(
        disk={"X": "X.agda", "Y": "Y.agda"}, deps={"X": frozenset({"Y"}), "Y": frozenset({"X"})}
    )
    refused = False
    try:
        flat_emit.text(cyclic, settings)
    except flat_emit.CycleError:
        refused = True
    check("a cyclic graph is refused rather than emitted", passed=refused)
    return out


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = _cases()
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            sys.stdout.write(f"  FAIL {label}\n")
    sys.stdout.write(f"flat-emit selftest: {ok}/{len(cases)}\n")
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(0 if ("--selftest" in sys.argv or len(sys.argv) == 1) and selftest() else 1)
