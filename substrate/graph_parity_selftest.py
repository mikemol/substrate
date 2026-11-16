# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The graph differential: `agda_dag.parse` (the clean model) vs the origin's `parse_tree`.

⚑⚑⚑ THE LAST PIECE THE SHIM CANNOT SWAP ON FAITH. Every other drained piece of
`gen_build_makefiles` was held byte-for-byte against its origin; the import graph is what every
compile rule's prerequisites come from, and a single missing edge is the UNSAFE direction (an edit
to an import would not mark its importer stale). So before `parse_tree` is served from the model,
this suite asserts the two agree on EVERY module and EVERY edge — and on a mismatch it names the
modules and edges that differ, because the diff is the finding.

⚑ BOTH SIDES USE THE SAME STRIPPER (`scripts/_agdatext.strip`), so a difference here is the parse
or the walk, not the comment rule.
"""

from __future__ import annotations

import sys

from substrate import flat_origin

SHOWN = 8


def _cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every case."""
    origin = flat_origin.graph(flat_origin.load())
    model = flat_origin.model_graph()
    o_mods, m_mods = set(origin.disk), set(model.disk)
    only_o, only_m = sorted(o_mods - m_mods), sorted(m_mods - o_mods)
    if only_o or only_m:
        sys.stdout.write(f"  modules only in origin: {only_o[:SHOWN]}\n")
        sys.stdout.write(f"  modules only in model:  {only_m[:SHOWN]}\n")
    same_paths = all(origin.disk[m] == model.disk[m] for m in o_mods & m_mods)
    diff_edges = [m for m in sorted(o_mods & m_mods) if origin.deps[m] != model.deps[m]]
    for m in diff_edges[:SHOWN]:
        sys.stdout.write(
            f"  {m}: origin-only {sorted(origin.deps[m] - model.deps[m])}"
            f" model-only {sorted(model.deps[m] - origin.deps[m])}\n"
        )
    return [
        ("the model and the origin see the same modules", not only_o and not only_m),
        ("and map each to the same source path", same_paths),
        (f"and give every module the same imports ({len(diff_edges)} differ)", not diff_edges),
        ("and the graph is non-trivial", len(o_mods) > 1),
    ]


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = _cases()
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            sys.stdout.write(f"  FAIL {label}\n")
    sys.stdout.write(f"graph-parity selftest: {ok}/{len(cases)}\n")
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(0 if ("--selftest" in sys.argv or len(sys.argv) == 1) and selftest() else 1)
