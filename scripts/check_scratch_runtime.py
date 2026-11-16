#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""check_scratch_runtime.py — Λ8b: the RUNTIME oracle to Λ8's static proxy.

Λ8 (check_scratch_independence.py) AST-scans for scratch path-strings / imports in jea/+el-atlas/
*source*. By construction it cannot see a RUNTIME reach — a path built from os.environ, a glob, an
indirect/dynamic import, a config-driven open. This is the ground-truth complement: it installs a
`sys.addaudithook` and FAILS if any `open` or `import` event resolves under <repo>/scratch/ while the
coupling-surface modules actually EXECUTE.

Proxy (Λ8, per-commit, cheap, static) + oracle (Λ8b, empirical) is the same cheap-gate +
heavy-throttled-check structure the pre-commit hook already uses for the make full build.

⚑ THIS DOCSTRING SAID "NOT wired into the per-commit fast path" UNTIL 2026-08-26, AND IT WAS FALSE.
`build_census --gates` lists `scratch-runtime (Λ8b)` as a DECLARED Phase A gate, and `.githooks/
pre-commit` runs it under the Λ8 trigger. A stale self-description in the file a reader opens FIRST
to learn what the gate is for — `fresh-comments-are-hypotheses-too`, in the gate whose defect was
that nobody could tell it had not run.

⚑⚑ AND THE GATE USED TO SELF-SKIP AT EXIT 0 FOR WANT OF `cupy`, WHICH IS THE DEFECT THIS FILE NOW
EXISTS TO NOT HAVE. A gate whose NON-EXECUTION is indistinguishable from its PASSING is worse than a
red one: it is counted GREEN in the roster while examining nothing. The skip is now a THIRD VERDICT
(exit 3, INCONCLUSIVE — distinct from 0/pass and 1/fail, the `vfs.listdir` shape), and it is
NARROWED to the half that actually needs a GPU.

⚑ WHAT ACTUALLY NEEDS `cupy` — MEASURED, not assumed (`pycodemod --imports`, 2026-08-26). Only the
AUDIT-HOOK half: `jea_edge_states:42` and `jea_navigator:29` import cupy directly, `jea_onegraph`
and `jea_agda_bridge` reach it transitively (`jea_graded:23`, `jea_generator_dag:26`). The COVERAGE
half — `uncovered_roots()`, the population/curation arithmetic — is pure set operations over ROOTS
and the discovered surface. It needs no GPU, no subprocess, and no import of the targets, so it runs
UNCONDITIONALLY and is the reason a GPU-less machine now gets a real verdict instead of silence.

Non-destructive: it does NOT `mv scratch aside` (racy, mutates the tree). The audit hook observes
access in-process — strictly an observer.

Coupling surface: DERIVED by `coupling_surface()` — run `--surface` to see it and the reason each
member was selected. Running a member transitively imports the foreign code it pulls in, so the hook
also sees whether THAT resolves under scratch. A subprocess (agda) is a separate process and is out
of scope — the invariant is that the PYTHON code of a promoted project takes no scratch dependency.

⚑ AND THE ROSTER OUTLIVED ITS OWN STATED REASON.  This paragraph used to name `jea_agda_bridge` and
`jea_agda_dag`, justified as *"subprocess agda + the EMIT_DIR open"*.  Measured 2026-08-26
(`pycodemod --binding EMIT_DIR`): **EMIT_DIR does not exist in either file — 0 bindings in 0 of 2.**
The name is gone from the tree and the two files stayed in the list anyway, defended by a sentence
about a symbol that had ceased to exist.  That is the argument for a predicate in one line: a roster
cannot notice when its justification evaporates, and a derived surface re-asks every run.

⚑ TARGETS IS NO LONGER HAND-TYPED — see `coupling_surface()`. The old roster named five files in
`jea/` top-level and covered NONE of the 7 RUNTIME couplings Λ8 reports (all in `jea/metalanguage/`),
and `el-atlas` had zero entries. Worse, every one of the five pulled `cupy`, so the curated set was
exactly the set this machine cannot execute — while `sql_lift.py`, a HARD coupling, imports no cupy
and runs here fine. A hand-picked list justified by a docstring is a frozen roster with an
explanation attached; the selection PRINCIPLE was real, so it is now spelled as a PREDICATE.

Usage: check_scratch_runtime.py [--quiet] [--full] [--strict] [--surface]
  --quiet / --check   silent on success
  --full              run each target as __main__ (the GPU/agda demos) rather than importing it
  --strict            exit 1 if a target did not run cleanly
  --surface           print the derived coupling surface and why each member was selected

EXIT CODES — three verdicts, because two cannot express this gate's state:
  0  PASS          the surface was examined and no runtime scratch/ access occurred
  1  FAIL          a runtime scratch/ access was observed (or --strict residue)
  3  INCONCLUSIVE  the audit-hook half could not run here (no cupy). NOT a pass.
"""

import ast
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# ⚑ BOTH AUTHORITIES ARE IMPORTED, NEVER RESTATED.  `ROOTS` is the promoted-project roster
# (§6d); `_dep_sites` is Λ8's OWN narrow "is this a live scratch dependency" predicate. The
# runtime oracle selecting its surface by a SECOND copy of that predicate is exactly the
# same-name-different-body hazard, and it would let the two gates disagree about the very
# coupling one exists to observe for the other.
from check_scratch_independence import ROOTS, _dep_sites

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ⚑ THE ROSTER IS GONE.  It was five hand-typed paths defended by a paragraph, which is a
# FROZEN ROSTER WITH AN EXPLANATION ATTACHED — the shape this repo refuses everywhere else.
# The defence ("the selection principle is sound, so keep the curation and derive only the
# claim") left the confusion exactly where it was: a reader still could not tell WHY a file
# was in the list, and nothing re-derived it when the tree moved.  It HAD moved.  Measured
# 2026-08-26:
#
#   * Λ8 reports 7 RUNTIME couplings, every one in `jea/metalanguage/`.  The roster named
#     five files in `jea/` top-level.  INTERSECTION: EMPTY.  This gate certified "the static
#     proxy's blind spot is empirically empty" over five files that were never the couplings.
#   * `el-atlas` — half the promoted corpus — had ZERO entries.
#   * ⚑⚑ AND EVERY ONE OF THE FIVE PULLED `cupy`, so the curated set was precisely the set
#     this machine CANNOT execute, while `jea/metalanguage/sql_lift.py` (a HARD coupling)
#     imports no cupy and runs here fine.  The curation and the skip reinforced each other:
#     the roster guaranteed the gate had nothing runnable to do, and the skip made that
#     unobservable.
#
# ⚑ THE SELECTION PRINCIPLE WAS REAL, SO IT IS SPELLED AS A PREDICATE.  The principle was
# never "these five files"; it was "a module that REACHES ACROSS, so one audit hook observes
# both sides".  That is a structural property of the import graph, and a predicate answers
# the reader's "why is this in the list" at every future call, which a roster cannot.
#
# ⚑ THE COST OBJECTION IS ANSWERED BY THE PREDICATE, NOT BY TYPING.  Deriving from ROOTS
# NAIVELY (every .py under jea/ + el-atlas/) would indeed be ~100 subprocesses — that was the
# stated reason to keep the roster.  But the predicate does not select every file; it selects
# the files with a REACH, which is a small fraction, and it computes that from the AST without
# running anything.  The third way was to make the selection cheap, not to hand-type its answer.


def _module_imports(path):
    """Top-level imported NAMES of one .py — AST only, nothing is executed."""
    try:
        with open(path, encoding="utf-8") as fh:
            tree = ast.parse(fh.read(), filename=path)
    except (SyntaxError, UnicodeDecodeError, OSError):
        return set()
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module.split(".")[0])
    return names


def _root_py(root):
    """Every .py under one promoted project, repo-relative."""
    out, base = [], os.path.join(REPO, root)
    for dirpath, _d, files in os.walk(base):
        if any(p in dirpath for p in (".venv", "__pycache__", ".git", ".edit-snapshots")):
            continue
        for f in sorted(files):
            if f.endswith(".py"):
                out.append(os.path.relpath(os.path.join(dirpath, f), REPO))
    return out


def coupling_surface(roots=None):
    """[(rel, reason)] — the modules worth observing under an audit hook, DERIVED.

    ⚑ THE PREDICATE, stated so a reader never has to ask why a file is here.  A module
    is on the coupling surface when it REACHES — when importing it pulls foreign code
    into the process, so one audit hook can observe both sides:

      `cross-root`  it imports a module that lives under a DIFFERENT promoted project
                    (the original hand-picked principle: jea → the el-atlas tools).
      `scratch-dep` Λ8's own narrow predicate says it has a live scratch/ dependency.
                    ⚑ THIS IS THE HALF THE ROSTER MISSED ENTIRELY.  A file Λ8 already
                    flags is the single most important thing for the RUNTIME oracle to
                    execute, and not one of the seven was named.

    ⚑ ASKS THE OWNING AUTHORITIES, NEVER A SECOND COPY.  Root membership comes from the
    imported `ROOTS`; "is this a scratch dependency" comes from Λ8's own `_dep_sites`.
    Restating either would rebuild the retyped-scope defect one file over.
    """
    roots = list(ROOTS if roots is None else roots)
    # module basename -> owning root, so a cross-root import is decidable by name
    owner = {}
    for r in roots:
        for rel in _root_py(r):
            owner.setdefault(os.path.basename(rel)[:-3], r)

    surface = []
    for r in roots:
        for rel in _root_py(r):
            reasons = []
            foreign = sorted(
                n for n in _module_imports(os.path.join(REPO, rel)) if owner.get(n) not in (None, r)
            )
            if foreign:
                reasons.append(f"cross-root: imports {', '.join(foreign[:3])}")
            if _dep_sites(os.path.join(REPO, rel)):
                reasons.append("scratch-dep: Λ8 flags a live scratch/ dependency")
            if reasons:
                surface.append((rel, "; ".join(reasons)))
    return surface


def uncovered_roots(targets=None):
    """[root] in ROOTS that no entry of `targets` lives under — the coverage residue.

    ⚑ ASKS ROOTS, NEVER A SECOND ROSTER.  The whole defect this closes is a scope
    retyped away from its authority, so re-listing the promoted projects here would
    reproduce it one file over.

    ⚑ KEPT THOUGH THE ROSTER IS GONE, because a DERIVED surface can still be empty for
    a root — a promoted project with no cross-root import and no scratch dependency
    contributes nothing to execute, and this gate must still say so rather than let
    silence read as a clean bill.
    """
    rels = [
        t[0] if isinstance(t, tuple) else t
        for t in (coupling_surface() if targets is None else targets)
    ]
    return [r for r in ROOTS if not any(rel == r or rel.startswith(r + "/") for rel in rels)]


# Preamble run in each child: install the audit hook BEFORE the target executes. {action} is either
# an IMPORT (default — runs module-level code: the _TOOLS path-build + el-atlas imports, where the
# scratch-coupling surface lives; ~0.1-1s/module) or a __main__ RUN (--full — also runs the GPU/agda
# DEMOS, ~5-16s/module, catching the contrived in-function dynamic reach). Pure string ops inside the
# hook (no audited calls) so it can't recurse. Emits one marker line per hit.
_PREAMBLE = r"""
import sys, os, runpy, importlib
sys.path.insert(0, os.path.dirname({target!r}))   # mimic `python <script>.py` (script-dir on path)
_SCR = os.path.normpath(os.path.join({repo!r}, "scratch")) + os.sep
_CWD = os.getcwd()
def _h(ev, a):
    p = None
    if ev == "open" and a:
        p = a[0]
    elif ev == "import" and len(a) > 1:
        p = a[1]
    if isinstance(p, str):
        ap = p if os.path.isabs(p) else os.path.join(_CWD, p)
        if os.path.normpath(ap).startswith(_SCR):
            sys.stderr.write("__SCRATCH_HIT__\t" + ev + "\t" + os.path.normpath(ap) + "\n")
sys.addaudithook(_h)
{action}
"""

MARK = "__SCRATCH_HIT__"


def run_one(rel, full):
    target = os.path.join(REPO, rel)
    if full:
        action = "runpy.run_path({target!r}, run_name='__main__')".format(target=target)
        timeout = 420
    else:
        action = "importlib.import_module({mod!r})".format(mod=os.path.basename(rel)[:-3])
        timeout = 90
    code = _PREAMBLE.format(repo=REPO, target=target, action=action)
    try:
        proc = subprocess.run(
            [sys.executable, "-c", code], cwd=REPO, capture_output=True, text=True, timeout=timeout
        )
    except subprocess.TimeoutExpired:
        return ("timeout", [])
    hits = [ln for ln in proc.stderr.splitlines() if ln.startswith(MARK)]
    parsed = [tuple(ln.split("\t")[1:]) for ln in hits]
    status = "hit" if parsed else ("ran" if proc.returncode == 0 else f"err({proc.returncode})")
    return (status, parsed)


INCONCLUSIVE = 3

# ⚑ THE TOOL HAD NO SELF-DESCRIPTION, AND `toolmodes --check` SAID SO: *"NO SELF-DESCRIPTION —
# its bare run prints no usage line"*.  A bare run EXECUTED THE GATE, so every mode here
# (`--full`, `--strict`, and the new `--surface`) dispatched while being declared nowhere a
# reader could look — the ⟡divergence-ungated shape, in the gate whose whole defect was that
# its state could not be read off its output.  The census names the tool, never a number here.
USAGE = """check_scratch_runtime.py — Λ8b: the RUNTIME oracle to Λ8's static proxy.

  check_scratch_runtime.py                 the gate over the DERIVED coupling surface
  check_scratch_runtime.py --quiet         silent on success (the alias `--check` is identical)
  check_scratch_runtime.py --check         the gate, quiet — the spelling hook callers use
  check_scratch_runtime.py --full          run each target as __main__ (the GPU/agda demos)
  check_scratch_runtime.py --strict        exit 1 if a target did not run cleanly, or if a
                                           promoted project contributes no surface module
  check_scratch_runtime.py --surface       print the derived surface + why each member was picked
  check_scratch_runtime.py --selftest      the guarded cases
  check_scratch_runtime.py --help          this block

EXIT: 0 pass · 1 fail · 3 INCONCLUSIVE (the audit-hook half could not run — NOT a pass)"""


def main():
    if "--help" in sys.argv or "-h" in sys.argv:
        print(USAGE)
        return 0
    quiet = "--quiet" in sys.argv or "--check" in sys.argv
    full = "--full" in sys.argv
    surface = coupling_surface()
    targets = [rel for rel, _why in surface]

    if "--surface" in sys.argv:
        print(
            f"scratch-runtime (Λ8b): coupling surface — {len(surface)} module(s) DERIVED "
            f"from ROOTS ({'/'.join(ROOTS)}), not curated."
        )
        for rel, why in surface:
            print(f"  {rel}\n      {why}")
        for r in uncovered_roots():
            print(
                f"  ⚑ {r}: no module reaches across and none carries a scratch dependency — "
                f"nothing for the audit hook to observe."
            )
        return 0

    # ⚑ THE COVERAGE HALF RUNS UNCONDITIONALLY, AND IT RUNS FIRST.  It is pure set arithmetic
    # over ROOTS and the derived surface — no GPU, no subprocess, no import of a target — so a
    # GPU-less machine gets a REAL verdict on the population question instead of silence. The
    # old whole-gate skip for a PARTIAL dependency was itself the defect: it discarded a
    # property that never needed cupy in the first place.
    uncovered = uncovered_roots()

    # ⚑ THE SKIP IS A THIRD VERDICT, NOT A PASS.  `find_spec("cupy") is None` used to `return 0`
    # — the gate reported success having examined NOTHING, and the roster counted it green. No
    # reader could distinguish that from a clean run. Exit 3 (INCONCLUSIVE) is distinct from
    # both 0 and 1, the `vfs.listdir` shape: "this gate could not answer" is a different fact
    # from "the answer is clean", and collapsing them is what made the gate inert for months.
    import importlib.util

    if importlib.util.find_spec("cupy") is None:
        print(
            f"scratch-runtime (Λ8b): INCONCLUSIVE (exit {INCONCLUSIVE}) — `cupy` is absent, so the "
            f"audit-hook half CANNOT RUN on this machine.",
            file=sys.stderr,
        )
        print(
            f"    NOT a pass. {len(targets)} coupling-surface module(s) were derived and NONE "
            f"were executed, so this run says NOTHING about runtime scratch/ access.",
            file=sys.stderr,
        )
        print(
            f"    The static gate Λ8 still guards this commit — but Λ8 is the PROXY whose blind "
            f"spot this gate exists to measure, so its verdict does not substitute.",
            file=sys.stderr,
        )
        print(
            f"    ↳ install cupy to run it, or `check_scratch_runtime.py --surface` to see what "
            f"went unobserved.",
            file=sys.stderr,
        )
        return INCONCLUSIVE

    violations, unverified = [], []
    mode = "full(__main__)" if full else "import"
    for rel in targets:
        status, hits = run_one(rel, full)
        if hits:
            for ev, path in hits:
                violations.append((rel, ev, path))
        elif status.startswith("err") or status == "timeout":
            unverified.append((rel, status))
        if not quiet:
            tag = "HIT" if hits else ("UNVERIFIED" if status != "ran" else "clean")
            print(f"  runtime {tag:<10} {rel}  [{status}]")

    for rel, status in unverified:
        print(
            f"  scratch-runtime: WARN {rel} did not run cleanly ({status}); runtime reach NOT verified "
            f"for it (not a violation — re-run with GPU/agda available)",
            file=sys.stderr,
        )

    if violations:
        print(
            f"scratch-runtime (Λ8b): FAILED — {len(violations)} RUNTIME scratch/ access(es) the static "
            f"gate (Λ8) could not see:",
            file=sys.stderr,
        )
        for rel, ev, path in violations:
            print(f"    {rel}  [{ev}]  {path}", file=sys.stderr)
        return 1

    # ⚑ THE COVERAGE CLAIM IS SCOPED TO WHAT WAS ACTUALLY EXAMINED.  The old verdict
    # read "the static proxy's blind spot is empirically empty" unconditionally — a
    # statement about the whole promoted corpus, earned only over the curated five.
    if not quiet:
        verified = len(targets) - len(unverified)
        scope = "/".join(ROOTS)
        print(
            f"scratch-runtime (Λ8b): OK [{mode}] ({verified}/{len(targets)} DERIVED surface "
            f"modules, 0 runtime scratch access)."
        )
        if uncovered:
            print(
                f"  ⚑ SCOPED CLAIM, NOT A CLEAN BILL for {scope}: {len(uncovered)} promoted "
                f"project(s) contribute NO surface module — {', '.join(uncovered)}. Nothing "
                f"belonging to them was executed, so this run says NOTHING about them."
            )
        else:
            print(
                f"  Every project in ROOTS ({scope}) contributes at least one surface module. "
                f"The static proxy's (Λ8) blind spot is empirically empty for the "
                f"coupling surface."
            )
    if uncovered and "--strict" in sys.argv:
        print(
            f"scratch-runtime (Λ8b): STRICT — {', '.join(uncovered)} contributes no surface "
            f"module, so this gate never executes anything belonging to it and cannot certify "
            f"it. ↳ `check_scratch_runtime.py --surface` shows what was derived.",
            file=sys.stderr,
        )
        return 1
    return 1 if unverified and "--strict" in sys.argv else 0


def _selftest():
    """⚑ THE COVERAGE CLAIM MUST BE STARVED BOTH WAYS.

    A check that never fires and one that always fires are indistinguishable from a
    green suite, so `uncovered_roots` is pinned against a set that covers everything,
    a set that covers nothing, and the live TARGETS — plus the prefix case, which is
    the one a naive `startswith` gets wrong (`jea-other/` is not under `jea/`).
    """
    sys.path.insert(0, os.path.join(REPO, "scratch"))
    import rungs

    check = rungs.Cases(key="scripts/check_scratch_runtime.py")

    # (1) ALWAYS-FIRES starve: nothing curated => every promoted project uncovered.
    check("empty targets leave every ROOTS project uncovered", uncovered_roots([]), list(ROOTS))

    # (2) NEVER-FIRES starve: one target under each root => nothing uncovered.
    check(
        "a target under every root covers them all",
        uncovered_roots([r + "/x.py" for r in ROOTS]),
        [],
    )

    # (3) ⚑ THE PREFIX CASE. `"jea-other/x.py".startswith("jea")` is True, so a
    # substring test would silently credit a DIFFERENT project as covering `jea`.
    # The predicate requires the separator, so this must still report jea uncovered.
    check(
        "a sibling directory sharing a name prefix does not cover a root",
        "jea" in uncovered_roots(["jea-other/x.py"]),
        True,
    )

    # (4) THE LIVE DEFECT, PINNED — WITHOUT NAMING A ROOT.  The derived surface still
    # reaches only ONE promoted project, so the uncovered set is a strict, non-empty
    # subset of ROOTS.
    # ⚑ Spelling the expected root literally here would plant a SECOND roster in the
    # very file whose defect was a retyped one; the property is what is pinned.
    live = uncovered_roots()
    check("the derived surface leaves at least one promoted project uncovered", bool(live), True)
    check("every uncovered project is a real ROOTS member", [r for r in live if r not in ROOTS], [])

    # (5) ⚑ THE SURFACE IS DERIVED, AND THAT MUST BE STARVED BOTH WAYS TOO.  A predicate
    # that selected EVERY file would be as useless as the roster that selected almost
    # none — both are "a fact about the method". So: non-empty (it finds something) AND
    # a strict subset (it is actually discriminating, not a directory walk in disguise).
    surface = coupling_surface()
    rels = [r for r, _w in surface]
    population = _root_py("jea") + _root_py("el-atlas")
    check("the derived surface is non-empty", bool(rels), True)
    check(
        "the derived surface is a STRICT subset of the population — it discriminates",
        0 < len(rels) < len(population),
        True,
    )
    check("every selected module carries a stated reason", [r for r, w in surface if not w], [])

    # (6) ⚑ THE REGRESSION THAT MOTIVATED THE WHOLE CHANGE.  The hand roster covered NONE
    # of Λ8's RUNTIME couplings. The derived surface must cover EVERY one of them — if a
    # future edit reintroduces a selection that misses them, this fails. Asks Λ8's own
    # predicate for the population, never a second copy and never a pinned file list.
    coupled = [rel for rel in population if _dep_sites(os.path.join(REPO, rel))]
    check(
        "every module Λ8 flags as a scratch dependency is on the runtime surface",
        [rel for rel in coupled if rel not in rels],
        [],
    )
    check("...and there is at least one such module to have missed", bool(coupled), True)

    # (7) ⚑ THE SKIP IS NOT A PASS.  The defect was `return 0` on a missing cupy, which no
    # reader could distinguish from a clean run. INCONCLUSIVE must stay distinct from BOTH
    # verdicts, or the collapse silently returns.
    check("INCONCLUSIVE is distinct from pass", INCONCLUSIVE != 0, True)
    check("INCONCLUSIVE is distinct from fail", INCONCLUSIVE != 1, True)
    return check.report()


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    sys.exit(main())
