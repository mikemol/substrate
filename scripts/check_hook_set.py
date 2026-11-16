#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""⟡hook-set — assert the DECLARED hook roster equals the hooks on disk.

⚑⚑ THIS EXISTS BECAUSE A MISSED MEMBER OF A SET IS THE FAILURE THAT SURVIVES REVIEW.
Measured, 2026-08-30: `from scripts import …` broke four adopter repos' fire probes, so
a root prelude was added to the hooks that import a sibling — and `hook_pycheck.py` was
MISSED. It then crashed at module load in an adopting repo whose `scripts/` is not a
package; the harness reads a hook's empty stdout as ALLOW, so it denied nothing while
reading as armed in review. paperkit-c3 found it by adopting it, not by reading it.

⚑ AND THE VERIFICATION THAT MISSED IT WAS THE OBVIOUS ONE: after editing three files, I
checked those three. A check that only covers what you just changed CANNOT SEE THE FILE
YOU DID NOT CHANGE — the same shape as a census keyed on one spelling. The population
was never enumerated, so nothing could report it incomplete.

⚑⚑ THE SET WAS ALSO MISCOUNTED IN THE REPAIR ITSELF. Reporting the fix I wrote "the
three sibling hooks" and "four hooks"; `ls scripts/hook_*.py` returns FIVE.
`hook_structural_query.py` — which refuses a textual query against a structured artifact,
and which had refused two of my own commands that same session — was never once counted.
A set named from memory is not a set.

⚑ THE SHAPE IS paperkit's, from `bnd-components`: assert set-EQUALITY of a declared
partition against the real tree. Their instance caught a new module sitting unregistered
while every derived artifact stayed self-consistently "fresh" — THE GENERATOR WAS CORRECT
AND ITS INPUT WAS INCOMPLETE. A roster nothing asserts against the filesystem is exactly
that input.

WHAT THIS ASSERTS, and the second arm is the one with teeth:

1. `HOOKS` equals `scripts/hook_*.py` on disk, as a SET — a new hook that nobody
   registers fails here rather than sitting quietly outside every roster.
2. Every hook that IMPORTS A SIBLING carries the root prelude. That predicate is
   DERIVED (does it import `scripts.*`?), never a second hand-maintained list, because
   a hand-maintained list of which-files-need-the-fix is the very thing that went wrong.

⚑ ARM 2 IS NOT `_ROOT in text`. A hook may spell its prelude differently; what must hold
is that `sys.path` is repaired BEFORE the sibling import runs. This checks for a
`sys.path` mutation textually only as a LAST resort — the AST is the authority.

⚑ NOT COVERED, stated rather than implied: this asserts the prelude EXISTS, not that it
is CORRECT. A prelude computing the wrong root passes here and fails in adoption. The
arm that would catch that is a live fire probe from outside the repo (paperkit's), which
needs a second repo and cannot run in-tree.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent

# Where the hooks live. ⚑ DERIVED FROM THIS FILE'S OWN LOCATION, NOT NAMED. The gate and
# the hooks are siblings today; writing `_ROOT / "scripts"` states a directory NAME, so a
# move that relocates the family — the installed-package extraction is the live one —
# leaves the gate globbing an emptied directory and reporting a roster/tree disagreement
# that is a fact about the MOVE rather than about the hooks. Deriving it means the gate
# follows its subject: whatever directory this gate is in is the directory it checks.
#
# ⚑⚑ AND THAT IS NOT THE SAME AS MAKING THE MOVE SAFE. Arm 1 is a set equality against a
# DECLARED roster; relocating the hooks without updating `HOOKS` still fails, correctly.
# This removes one obstacle — a hardcoded directory name — and deliberately leaves the
# roster's own assertion intact, because the roster is the thing that catches a missed
# member and that property is the whole reason this gate exists.
_HOOK_DIR = Path(__file__).resolve().parent

# ⚑ THE DECLARED ROSTER. A hook added to `scripts/` and not to this list FAILS arm 1 —
# which is the entire point: the set gets an owner, so a missed member is impossible
# rather than unlikely.
HOOKS = [
    "hook_cmdparse.py",
    # ⚑⚑ THE TWO `hook_fire_*` MEMBERS ARE NOT PreToolUse HOOKS — THEY PROBE THEM
    # (Ⓝ133c ⟡the-ritual-in-the-blind-spot), and they are registered here anyway because
    # arm 1 is a `hook_*.py` SET EQUALITY, not a judgement about what a file does. Leaving
    # them out to keep the roster "pure" would fail the gate; adding a prefix exception
    # would reintroduce the naming-convention-keyed population whose defect `manifest()`
    # records two paragraphs down. The set is the set.
    #
    # ⚑ AND ARM 2 STILL BINDS THEM USEFULLY: both import `scripts.*` siblings unguarded,
    # so both must carry the root prelude — the exact property whose absence from
    # `hook_pycheck` shipped a silently-inert gate into an adopting repo.
    "hook_fire_probe.py",
    "hook_fire_run.py",
    "hook_no_chaining.py",
    "hook_pycheck.py",
    # ⚑⚑ KEPT, AND THE REASON IS OUTSIDE THIS TREE (2026-09-22). This file was promoted to
    # mtools and deleted here — and that took down paperkit, linux-sources and
    # cassian-observability at once: they adopt it by SYMLINK into this path, armed on Bash AND
    # edits, so a dangling target failed every command closed. An importer census of this tree
    # cannot see a symlink in another. It stays until every adopter has moved to mtools'
    # `mikemol-hook-shellcheck`.
    "hook_shellcheck.py",
    "hook_structural_query.py",
]


def _on_disk() -> set[str]:
    """Return the hooks the filesystem actually holds."""
    return {p.name for p in _HOOK_DIR.iterdir() if p.name.startswith("hook_") and p.suffix == ".py"}


def _sibling_imports(tree: ast.Module) -> list[tuple[int, bool]]:
    """Every `scripts.*` import as `(lineno, is_guarded)`.

    ⚑ DERIVED, NEVER DECLARED. The whole defect was a hand-maintained notion of which
    files needed the prelude, so this asks the AST instead of a second list.

    ⚑⚑ GUARDEDNESS IS THE LOAD-BEARING DISTINCTION AND THE FIRST CUT MISSED IT.
    `hook_cmdparse` imports `hook_no_chaining` inside a `try/except` under `__main__`,
    purely to enrich one `--tokens` sub-report. An unguarded top-level import that fails
    kills the module and the harness reads that as ALLOW; a guarded one degrades a
    diagnostic and says so. Reporting both as the same finding would demand a prelude
    where none is needed — a false positive in the direction that GENERATES WORK.
    """
    found: list[tuple[int, bool]] = []
    guarded: set[int] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Try):
            for child in ast.walk(node):
                guarded.add(id(child))

    for node in ast.walk(tree):
        hit = False
        if isinstance(node, ast.ImportFrom):
            hit = (node.module or "").startswith("scripts")
        elif isinstance(node, ast.Import):
            hit = any(alias.name.startswith("scripts") for alias in node.names)
        else:
            continue
        if hit:
            found.append((node.lineno, id(node) in guarded))
    return found


# The scopes inside which an import is LAZY: it runs when the enclosing code runs, not at load.
_LAZY_SCOPES = (ast.Try, ast.FunctionDef, ast.AsyncFunctionDef)


def _package_names(node: ast.Import | ast.ImportFrom) -> list[str]:
    """Return the `substrate` package modules one import statement names."""
    if isinstance(node, ast.ImportFrom):
        module = node.module or ""
        return [module] if module == "substrate" or module.startswith("substrate.") else []
    return [a.name for a in node.names if a.name == "substrate" or a.name.startswith("substrate.")]


def _package_imports(tree: ast.Module) -> list[tuple[int, str, bool]]:
    """Every `substrate` PACKAGE import as `(lineno, dotted name, is_lazy)`.

    ⚑⚑⚑ THE AXIS THIS MANIFEST DID NOT HAVE, AND HOW gate-G403 SHIPPED FOR WEEKS (summit
    ask-hook-manifest-sees-package-imports). The manifest tracked `scripts.*` siblings — the
    files an adopter must COPY — and nothing tracked that three vendored bodies reached
    `substrate.ratchet_flags` at module scope: a PACKAGE only substrate has, which an adopter
    cannot copy and does not install. Every vendored copy died at load with
    `ModuleNotFoundError`, the harness read empty stdout as ALLOW, and the hook guarded
    nothing while reading as armed. Summit's masked-site-packages witness found it; this
    reader is the manifest's own eye for it.

    ⚑ LAZY IS THE SANCTIONED SHAPE, and it is decided by SCOPE: an import inside a `def` or a
    `try` runs when that code runs and can refuse loudly on a maintainer command; one at
    module scope runs at load and cannot. That is the shape G403 landed, so the manifest
    reports package imports and the check REFUSES only the module-scope ones.
    """
    lazy: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, _LAZY_SCOPES):
            lazy.update(id(child) for child in ast.walk(node))
    found: list[tuple[int, str, bool]] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            lineno = node.lineno
            is_lazy = id(node) in lazy
            found.extend((lineno, name, is_lazy) for name in _package_names(node))
    return found


def _repairs_syspath(tree: ast.Module) -> bool:
    """Report whether this module mutates `sys.path` at import time.

    ⚑ Matches `sys.path.insert(...)` / `sys.path.append(...)` structurally, so a
    differently-spelled prelude still counts. What matters is that the path is repaired,
    not that a particular variable name appears.
    """
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        fn = node.func
        if not isinstance(fn, ast.Attribute) or fn.attr not in ("insert", "append"):
            continue
        target = fn.value
        if (
            isinstance(target, ast.Attribute)
            and target.attr == "path"
            and isinstance(target.value, ast.Name)
            and target.value.id == "sys"
        ):
            return True
    return False


def _sibling_names(tree: ast.Module) -> set[str]:
    """Return the `scripts.<name>` modules this file imports, guarded or not.

    ⚑ GUARDEDNESS DOES NOT MATTER TO A MANIFEST. `_sibling_imports` distinguishes
    guarded from unguarded because an unguarded failure is a silent-allow; a manifest
    asks a different question — WHAT MUST BE PRESENT for this file to behave as
    designed. A guarded import that is missing degrades a diagnostic rather than
    killing the hook, and an adopter still wants to know it was left behind.
    """
    out: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            # ⚑ BOUND ONCE, NOT RE-READ. `node.module` is `str | None`, and testing it
            # in one branch does not narrow it in the next — the checker said so.
            module = node.module or ""
            if module == "scripts":
                out.update(a.name for a in node.names)
            elif module.startswith("scripts."):
                out.add(module.split(".", 1)[1])
        elif isinstance(node, ast.Import):
            out.update(a.name.split(".", 1)[1] for a in node.names if a.name.startswith("scripts."))
    return out


def manifest() -> dict[str, set[str]]:
    """Return each hook's transitive file set — what an adopter must take.

    ⚑⚑ THIS EXISTS BECAUSE THE FILES SOMEONE NEEDS WERE NEVER WRITTEN DOWN, and the
    only reason the last adoption was correct is that the person choosing the set
    happened to know the import graph. A peer vendored five hook files by name; had
    they taken four, the missing one would have surfaced as a `ModuleNotFoundError`
    at module load — and a hook that cannot load writes nothing to stdout, which the
    harness reads as ALLOW. **An incomplete adoption of a guard is a silently-absent
    guard**, not a visible breakage.

    ⚑ DERIVED FROM THE IMPORT GRAPH, NEVER DECLARED. A hand-written manifest is a
    second roster beside the code, and this repo has measured that shape repeatedly
    (`agda_files` as four bodies under one name). The graph is the authority; this
    reads it. A file that stops importing a sibling drops out of the set with no
    edit, which is what makes the manifest true rather than merely present.
    """
    # ⚑⚑ THE POPULATION IS THE WHOLE DIRECTORY, NOT `hook_*.py`, AND THAT ONE-WORD
    # DIFFERENCE WAS A SILENT INCOMPLETE MANIFEST. The closure below has always been
    # correct; it walked a graph whose non-hook nodes had NO EDGES, because the tree
    # map was built from `_on_disk()` — which selects on the `hook_` prefix. When
    # ⓝ.split-pycheck decomposed `hook_pycheck` into five `pycheck_*` siblings, the
    # walk reached `pycheck_analyze.py`, found no entry for it, and stopped — omitting
    # `pycheck_checkers.py` and `pycheck_verdict.py` from the set an adopter must take.
    #
    # ⚑⚑⚑ SO THE MANIFEST WAS INCOMPLETE IN EXACTLY THE WAY IT EXISTS TO PREVENT, and
    # it read as authoritative because the closure logic beside it is right. A census
    # keyed on a NAMING CONVENTION reports the convention's boundary as the subject's:
    # the files were on disk, imported, and load-bearing, and the only thing that made
    # them invisible was not being called `hook_*`. Two arms of this file's own defect
    # class — a set named from memory, and a spelling-keyed population — met here.
    #
    # ⚑ `_on_disk()` KEEPS ITS PREFIX FILTER, correctly: arm 1 asks *which HOOKS exist*,
    # and a `pycheck_*` helper is not a hook and must not be demanded in `HOOKS`. The
    # two questions differ, so they get two populations rather than one compromise.
    trees: dict[str, ast.Module] = {}
    for path in sorted(_HOOK_DIR.iterdir()):
        if path.suffix != ".py" or path.name == "__init__.py":
            continue
        try:
            trees[path.name] = ast.parse(path.read_text(encoding="utf-8"), filename=path.name)
        except (SyntaxError, OSError, UnicodeDecodeError):
            continue

    direct = {name: {f"{mod}.py" for mod in _sibling_names(tree)} for name, tree in trees.items()}

    # ⚑ TRANSITIVE, BECAUSE A ONE-HOP MANIFEST IS THE SAME DEFECT ONE LEVEL DOWN.
    # `hook_pycheck` imports `hook_shellcheck`, which imported `hook_no_chaining`,
    # which imports `hook_cmdparse`. An adopter taking only the direct dependency
    # gets a chain that breaks at the second hop — and breaks the same silent way.
    out: dict[str, set[str]] = {}
    for name, first_hop in direct.items():
        seen = {name}
        frontier = set(first_hop)
        while frontier:
            nxt = frontier.pop()
            if nxt in seen:
                continue
            seen.add(nxt)
            frontier |= direct.get(nxt, set())
        out[name] = seen
    return out


def _render_targets() -> dict[str, set[str]]:
    """Return the manifest rows an adopter asks about: the declared hooks.

    ⚑⚑ THE POPULATION AND THE SUBJECT ARE TWO DIFFERENT SETS, AND COLLAPSING THEM
    BROKE THIS TWICE IN OPPOSITE DIRECTIONS. `manifest()` must PARSE the whole
    directory — a node whose edges were never read looks like a leaf, which is how
    `pycheck_checkers`/`pycheck_verdict` fell out of the set. But widening the parse
    to fix the closure also widened the REPORT to 100+ unrelated scripts, burying the
    five lines anyone came for. The graph needs every node; the reader needs the hooks.
    """
    return {name: needs for name, needs in manifest().items() if name in HOOKS}


def _render_manifest() -> int:
    """Print each hook and the file set an adopter must take with it.

    ⚑⚑ THE POPULATION AND THE SUBJECT ARE TWO DIFFERENT SETS, AND COLLAPSING THEM
    BROKE THIS TWICE IN OPPOSITE DIRECTIONS. `manifest()` must PARSE the whole
    directory — a node whose edges were never read looks like a leaf, which is how
    `pycheck_checkers`/`pycheck_verdict` fell out of the set. But an adopter asks
    about HOOKS, so widening the parse to fix the closure must not widen the
    REPORT: the first cut printed 100+ unrelated scripts, burying the five lines
    anyone came for.
    """
    for name, needs in sorted(_render_targets().items()):
        others = sorted(needs - {name})
        sys.stdout.write(f"{name}\n")
        if others:
            for dep in others:
                sys.stdout.write(f"    + {dep}\n")
        else:
            sys.stdout.write("    (standalone — no sibling required)\n")
        # ⚑ THE PACKAGE ROWS ARE WHAT AN ADOPTER CANNOT COPY, reported per closure member so
        # a reach one hop down (cmdparse) shows under the hook that carries it in.
        for member in sorted(needs):
            for lineno, module, is_lazy in _package_reach(member):
                shape = "lazy" if is_lazy else "MODULE SCOPE — breaks a vendored copy"
                sys.stdout.write(f"    ~ {member}:{lineno} package {module} ({shape})\n")
    return 0


def _package_reach(name: str) -> list[tuple[int, str, bool]]:
    """Return one closure member's package imports, or nothing if it cannot be parsed."""
    try:
        tree = ast.parse((_HOOK_DIR / name).read_text(encoding="utf-8"), filename=name)
    except (SyntaxError, OSError, UnicodeDecodeError):
        return []
    return _package_imports(tree)


def check() -> list[str]:
    """Return the findings; empty means the roster and the tree agree."""
    findings: list[str] = []

    declared = set(HOOKS)
    actual = _on_disk()

    findings.extend(
        f"{name}: on disk but NOT in HOOKS. A hook outside the roster is outside "
        f"every check that iterates it — register it in check_hook_set.HOOKS."
        for name in sorted(actual - declared)
    )
    findings.extend(
        f"{name}: in HOOKS but NOT on disk. Remove it from the roster, or restore "
        f"the file if the deletion was accidental."
        for name in sorted(declared - actual)
    )

    for name in sorted(declared & actual):
        path = _HOOK_DIR / name
        source = path.read_text(encoding="utf-8")
        try:
            tree = ast.parse(source, filename=path)
        except SyntaxError as exc:
            findings.append(f"{name}: does not parse ({exc}).")
            continue
        siblings = _sibling_imports(tree)
        unguarded = [ln for ln, is_guarded in siblings if not is_guarded]
        if unguarded and not _repairs_syspath(tree):
            findings.append(
                f"{name}:{unguarded[0]}: imports a `scripts.*` sibling UNGUARDED but "
                f"does NOT repair `sys.path`. Adopted by symlink into a repo whose "
                f"`scripts/` is not a package, this raises ModuleNotFoundError AT MODULE "
                f"LOAD — and the harness reads a hook's empty stdout as ALLOW, so it "
                f"denies nothing while reading as armed. Add the root prelude (see "
                f"hook_pycheck.py)."
            )

    findings.extend(_package_findings())
    return findings


def _package_findings() -> list[str]:
    """Return one finding per MODULE-SCOPE package import anywhere in the vendored closure.

    ⚑⚑ THE POPULATION IS THE CLOSURE, NOT `HOOKS`. The third body that died at load
    (gate-G403) was `hook_cmdparse.py` — not a hook, the tokenizer both hooks import — and
    summit's witness, which runs the HOOKS, named only the two. A check over the declared
    hooks alone would have passed with the defect live one hop down.
    """
    # ⚑ THE UNION OVER THE DECLARED HOOKS' CLOSURES — NOT over `manifest()`'s keys, which
    # are every parsed script (the graph needs every node). The first cut took the latter and
    # reported 30 gates nobody vendors; the vendored population is what the hooks reach.
    files = set().union(*_render_targets().values()) if HOOKS else set()
    findings: list[str] = []
    for name in sorted(files):
        path = _HOOK_DIR / name
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=name)
        except (SyntaxError, OSError, UnicodeDecodeError):
            continue
        for lineno, module, is_lazy in _package_imports(tree):
            if is_lazy:
                continue
            findings.append(
                f"{name}:{lineno}: imports the PACKAGE `{module}` at MODULE SCOPE. A vendored "
                f"copy cannot carry a package it does not install: in an adopting checkout "
                f"this raises ModuleNotFoundError AT LOAD, the harness reads empty stdout as "
                f"ALLOW, and the hook guards nothing while reading as armed (gate-G403). "
                f"Import it lazily, inside the mode that needs it, and refuse loudly there."
            )
    return findings


# ⚑ DERIVED FROM THE ARMS, NOT TYPED. This tally read a hardcoded `7/7` while the arms
# below it were edited — a literal count cannot fall out of step with reality loudly, so
# it reports the number someone last remembered. Twelve arms, named in one place.
_CASES = 12


def _cases_manifest() -> int:
    """Return the failure count for the manifest's closure and its rendering.

    ⚑⚑ THE CLOSURE MUST REACH PAST A NON-HOOK NODE, AND NOTHING ASSERTED THAT UNTIL IT
    FAILED. `manifest()` parsed only `hook_*.py`, so a `pycheck_*` sibling entered the
    graph with NO EDGES and the walk stopped there — silently dropping two files an
    adopter must take. The closure code was correct throughout; the POPULATION it walked
    was keyed on a naming convention, which is this repo's most-filed defect wearing a
    new spelling. An incomplete manifest is the silent-adoption failure this whole file
    exists to prevent, so it now has a witness rather than a comment.
    """
    failures = 0

    reach = manifest().get("hook_pycheck.py", set())
    if "pycheck_verdict.py" not in reach:
        sys.stderr.write(
            "selftest: the manifest closure stopped at a non-hook node — "
            "pycheck_verdict.py is reached only via pycheck_analyze.py\n"
        )
        failures += 1

    # ⚑ AND THE REPORT STAYS NARROW WHILE THE PARSE IS WIDE. Widening the population to
    # fix the closure also widened the rendering to 100+ unrelated scripts, burying the
    # answer. An adopter asks about HOOKS; the graph needs every node. Two sets.
    if set(_render_targets()) != set(HOOKS):
        sys.stderr.write("selftest: --manifest renders something other than the declared hooks\n")
        failures += 1

    return failures


def _cases_package() -> int:
    """Return the failure count for the package axis (gate-G403).

    A module-scope package import reads as eager; the same import inside a def reads lazy;
    and the live vendored closure carries no eager one.
    """
    failures = 0
    tree = ast.parse("from substrate.ratchet_flags import arg_after\n")
    if [(m, lazy) for _, m, lazy in _package_imports(tree)] != [("substrate.ratchet_flags", False)]:
        sys.stderr.write("selftest: a module-scope package import did not read as eager\n")
        failures += 1
    tree = ast.parse("def f():\n    from substrate.ratchet_flags import arg_after\n")
    if [lazy for _, _, lazy in _package_imports(tree)] != [True]:
        sys.stderr.write("selftest: a def-scoped package import did not read as lazy\n")
        failures += 1
    live = _package_findings()
    if live:
        sys.stderr.write("selftest: the vendored closure carries a module-scope package import:\n")
        sys.stderr.write("".join(f"    {f}\n" for f in live))
        failures += 1
    return failures


def _selftest() -> int:
    """Run the cases and return an exit code.

    ⚑ Cases pin the PROPERTIES, not the current counts — a count-based assertion
    would pass on exactly the roster drift this file exists to catch.
    """
    failures = 0

    # The declared roster is a set, not a list with duplicates.
    if len(HOOKS) != len(set(HOOKS)):
        sys.stderr.write("selftest: HOOKS contains duplicates\n")
        failures += 1

    # A sibling import is detected, and reported UNGUARDED.
    tree = ast.parse("from scripts import hook_pycheck\n")
    if [g for _, g in _sibling_imports(tree)] != [False]:
        sys.stderr.write("selftest: _sibling_imports missed a bare `from scripts import`\n")
        failures += 1

    # A stdlib-only module yields nothing.
    tree = ast.parse("import os\nimport sys\n")
    if _sibling_imports(tree):
        sys.stderr.write("selftest: _sibling_imports false-positive on stdlib\n")
        failures += 1

    # ⚑ THE ARM THAT COST A FALSE POSITIVE: a sibling import inside try/except is
    # GUARDED — it degrades a diagnostic, it does not silently allow. `hook_cmdparse`
    # is the live instance, and the first cut of this gate demanded a prelude for it.
    tree = ast.parse(
        "try:\n"
        "    from scripts import hook_no_chaining as _nc\n"
        "except Exception as e:\n"
        "    print(e)\n"
    )
    if [g for _, g in _sibling_imports(tree)] != [True]:
        sys.stderr.write("selftest: a try/except-guarded sibling import read as unguarded\n")
        failures += 1

    # ⚑ The prelude is recognised structurally, not by variable name — this is the arm
    # that would fail if the check degraded into `"_ROOT" in text`.
    tree = ast.parse("import sys\nsys.path.insert(0, 'anything')\n")
    if not _repairs_syspath(tree):
        sys.stderr.write("selftest: _repairs_syspath missed sys.path.insert\n")
        failures += 1

    # A different container's `.insert` is not a sys.path repair.
    tree = ast.parse("xs = []\nxs.insert(0, 'x')\n")
    if _repairs_syspath(tree):
        sys.stderr.write("selftest: _repairs_syspath false-positive on a list\n")
        failures += 1

    # The roster matches the tree as it stands.
    if _on_disk() != set(HOOKS):
        sys.stderr.write(f"selftest: roster/tree mismatch: {sorted(_on_disk() ^ set(HOOKS))}\n")
        failures += 1

    failures += _cases_manifest()
    failures += _cases_package()

    if failures:
        sys.stderr.write(f"check_hook_set selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"check_hook_set selftest: {_CASES}/{_CASES}\n")
    return 0


def main(argv: list[str]) -> int:
    """CLI: bare runs the check; `--selftest` runs the cases."""
    if "--selftest" in argv:
        return _selftest()
    if "--manifest" in argv:
        return _render_manifest()

    findings = check()
    if not findings:
        sys.stdout.write(
            f"hook set: {len(HOOKS)} declared, {len(_on_disk())} on disk — roster and "
            f"tree agree; every sibling-importing hook repairs sys.path; no package "
            f"import at module scope in the vendored closure.\n"
        )
        return 0
    for line in findings:
        sys.stderr.write(f"  {line}\n")
    sys.stderr.write(f"hook set: {len(findings)} finding(s)\n")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
