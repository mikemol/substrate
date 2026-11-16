# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
r"""Answer whether one file can be repointed at the package — every import, not a chosen subject.

⚑⚑⚑ THIS EXISTS BECAUSE I SIZED A SWAP TWICE AND GOT IT WRONG THE SECOND TIME (gate-F77). To
decide whether a gate could be swapped I asked `attr_reads` what it read off `agda_lex`, found
four names, saw all four packaged, and called it ready. Reading the file then showed a FIFTH
dependency on its own import line — `def_index` from a module of roughly 5900 lines, with no
packaged route. **Asking one module what a consumer needs answers about that module.** The first
gate happened to have every dependency in the modules I queried, so the method looked sound
because the case was easy.

⚑⚑ SO THE QUESTION IS A READ OF THE FILE, NEVER A QUERY WHOSE SUBJECT I CHOSE. This walks the
file's own import statements and classifies each one, which is the only form that cannot miss a
dependency I did not think to ask about.

⚑⚑⚑ AND THE THIRD OUTCOME IS THE POINT. An import is PACKAGED (reached through a real package),
UNPACKAGED (a bare name that resolves only under a `sys.path` insert), EXTERNAL (stdlib), or
**UNKNOWN** — a name this reader cannot classify. Collapsing UNKNOWN into either direction is how
a readiness report becomes a false green: called packaged it hides a blocker, called unpackaged
it manufactures one. A file is READY only when nothing is unpackaged AND nothing is unknown.

⚑⚑ THE STATEMENT FORM IS PART OF THE ANSWER, AND MY FIRST CUT IGNORED IT — measured by running
this against the gate it was built to bless, which came back NOT READY. `from scripts import
ratchet` records the module as `scripts`, undotted, so a rule reading "bare name for a package
tree" flagged the *packaged* spelling as the unpackaged one. `import scripts.ratchet` and
`from scripts import ratchet` are both qualified; `import ratchet` is not. The discriminator is
whether the package is NAMED, which the statement form carries and the module string alone does
not.

⚑ EXTERNAL IS NEITHER A BLOCKER NOR A PACKAGE MEMBER. The stdlib resolves for any adopter
installing the wheel, so it does not bear on readiness — but it is REPORTED rather than silently
dropped, because a reader that hides what it dismissed cannot be audited against a case.
"""

from __future__ import annotations

import ast
import sys
from dataclasses import dataclass
from pathlib import Path

#: The trees whose modules a packaged consumer may import by a QUALIFIED name. `scripts` is here
#: because it carries an `__init__.py` and `from scripts import ratchet` resolves today —
#: measured, not assumed: two of that module's import sites already spell it that way.
PACKAGES = ("substrate", "scripts", "jea", "catalog", "tests")

#: The tree that is deliberately NOT a package — a bare name resolving here is the paydown case.
SCRATCH = "scratch"

#: What a classification can be. ⚑ FOUR, and the fourth is the honest gap.
PACKAGED = "PACKAGED"
UNPACKAGED = "UNPACKAGED"
EXTERNAL = "EXTERNAL"
UNKNOWN = "UNKNOWN"


@dataclass(frozen=True, slots=True)
class Dep:
    """One import a file makes, and whether a packaged consumer could follow it."""

    name: str
    kind: str
    line: int
    detail: str = ""

    @property
    def blocks(self) -> bool:
        """Whether this dependency stops the file being repointed.

        ⚑ UNKNOWN BLOCKS. A dependency nobody classified is not a dependency nobody needs, and
        treating it as fine is the false green this module's third outcome exists to prevent.
        """
        return self.kind in (UNPACKAGED, UNKNOWN)


def _repo_root(start: Path) -> Path:
    """Return the repository root at or above `start`.

    ⚑ FOUND BY ITS MANIFEST rather than by counting parents, so this answers correctly for a
    file at any depth and says so by construction instead of by convention.
    """
    root = start
    while root.parent != root and not (root / "pyproject.toml").exists():
        root = root.parent
    return root


def _classify(name: str, root: Path, *, qualified: bool) -> tuple[str, str]:
    """Return `(kind, detail)` for one imported module name.

    `qualified` says whether the statement NAMES the package — true for `from X import Y` and
    for a dotted `import X.Y`, false for a bare `import Y`.

    ⚑⚑ THAT FLAG IS THE DISCRIMINATOR, AND OMITTING IT MISCLASSIFIED THE ONE FILE THIS READER
    WAS BUILT TO BLESS. `from scripts import ratchet` records the module as `scripts` with no
    dot, so a rule keyed on dots alone calls the packaged spelling unpackaged.

    ⚑ THE STDLIB IS CHECKED AGAINST THE INTERPRETER'S OWN ROSTER rather than a list kept here.
    A hand-kept roster of module names is the frozen-roster defect, and this one would go stale
    with every Python release.
    """
    import importlib.util  # noqa: PLC0415 - the probe this classification needs, named at its use

    head = name.split(".", 1)[0]
    if head in PACKAGES:
        if qualified:
            return PACKAGED, "reached through the package"
        return UNPACKAGED, f"bare name for the `{head}` tree"
    if head in sys.stdlib_module_names:
        return EXTERNAL, "stdlib"
    # ⚑⚑ AN INSTALLED DISTRIBUTION IS EXTERNAL FOR THE SAME REASON THE STDLIB IS: it resolves for
    # any adopter installing the wheel, so it does not bear on readiness. Before this probe such a
    # dependency fell through to UNKNOWN and the verdict counted it among the blockers — measured
    # on `pygit2`, which is installed and reachable (`vfs.py --read … --at HEAD` resolves a real
    # revision through it), and on `panflute`, which several already-drained modules import.
    #
    # ⚑ THE PROBE IS `find_spec`, NOT AN IMPORT. Importing to classify would run the module's
    # top-level code as a side effect of a static reader — and a reader that executes what it
    # censuses cannot be pointed at an untrusted tree.
    try:
        if importlib.util.find_spec(head) is not None:
            return EXTERNAL, "installed distribution"
    except (ImportError, ValueError):
        pass
    # ⚑ A BARE NAME THAT NAMES A FILE IN A TREE is the unpackaged case — it resolves only under
    # a `sys.path` insert, which is exactly what a packaged consumer cannot do.
    for tree in (*PACKAGES, SCRATCH):
        if (root / tree / f"{head}.py").exists():
            return UNPACKAGED, f"resolves only via sys.path into `{tree}/`"
    # ⚑⚑ AND EVERYTHING ELSE IS UNKNOWN, NEVER ASSUMED THIRD-PARTY. It may be an installed
    # distribution or a module this reader cannot see; those are different facts, and a reader
    # that guessed would report a blocker as clean exactly when it was least able to tell.
    return UNKNOWN, "not resolved to a tree, the stdlib, or a dotted package"


def _dep(name: str, line: int, root: Path, *, qualified: bool) -> Dep:
    """Return one classified dependency."""
    kind, detail = _classify(name, root, qualified=qualified)
    return Dep(name=name, kind=kind, line=line, detail=detail)


def _order(dep: Dep) -> tuple[int, str]:
    """Sort dependencies by where they appear, then by name."""
    return (dep.line, dep.name)


def deps_of(path: str | Path) -> list[Dep]:
    """Return every module `path` imports, classified.

    ⚑ THE FILE'S OWN IMPORT STATEMENTS, which is what makes this unable to miss a dependency
    nobody thought to ask about — the defect it was built for.

    ⚑ A LOCAL IMPORT COUNTS. An import inside a function is still a dependency at run time, and
    a swap that missed one would fail only on the branch that reaches it.

    ⚑ EACH NODE TYPE IN ITS OWN BRANCH, because `ast.walk` yields the base `AST` and only the
    concrete classes declare `lineno`. One loop over both would read that attribute off a type
    that does not have it — the checker refused exactly that, correctly. The branches also carry
    the statement FORM, which is what the classifier needs and the module string cannot supply.
    """
    src = Path(path)
    try:
        tree = ast.parse(src.read_text(encoding="utf-8"), filename=src.name)
    except (OSError, SyntaxError, UnicodeDecodeError):
        return []
    root = _repo_root(src.resolve().parent)

    out: list[Dep] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            # ⚑ `import X.Y` NAMES THE PACKAGE; `import Y` does not.
            out.extend(_dep(a.name, node.lineno, root, qualified="." in a.name) for a in node.names)
        elif isinstance(node, ast.ImportFrom) and not node.level and node.module:
            # ⚑ A RELATIVE IMPORT NAMES NO MODULE TO RESOLVE, so classifying it would report a
            # fact about nothing. A `from X import Y` always names its package.
            out.append(_dep(node.module, node.lineno, root, qualified=True))
    return sorted(out, key=_order)


def editability(path: str) -> tuple[str, str]:
    """Return `(state, detail)` for whether the per-file gate would ACCEPT an edit here.

    ⚑⚑⚑ IMPORT-REACHABILITY IS NOT EDITABILITY, AND CONFLATING THEM COST A REFUSED EDIT
    (gate-F80). This reader ranked a gate as the nearest repoint on one blocking import; the
    edit was then refused because the file carries dozens of findings and the per-file gate has
    no partial credit. **A swap needs BOTH conjuncts** — every import followable AND the file
    writable — and reporting only the first produces a READY that cannot be acted on.

    ⚑ THE VERDICT IS DELEGATED, NEVER RE-DERIVED. `editable.verdict_for` owns "would the gate
    accept an edit", including its own third outcome for a checker that could not run. A second
    implementation here would be a rival authority for exactly the relation that refused this
    edit.
    """
    from substrate import editable  # noqa: PLC0415

    got = editable.verdict_for(path)
    if got.state == editable.CLEAN:
        return editable.CLEAN, "the per-file gate would accept an edit"
    if got.state == editable.UNKNOWN:
        return editable.UNKNOWN, got.why or "the checkers could not be run"
    return editable.DIRTY, f"{got.findings} finding(s) — the gate refuses every edit"


def render(path: str, found: list[Dep], edit: tuple[str, str] | None = None) -> str:
    """Render one file's readiness on BOTH axes, with what blocks it named.

    ⚑⚑ THE VERDICT NAMES WHAT BLOCKS, NOT JUST THAT SOMETHING DOES. A bare NOT READY sends a
    reader back to re-derive the population this reader already holds — which is the whole
    reason sizing was done by hand and got it wrong.

    ⚑⚑⚑ AND `edit` IS THE SECOND CONJUNCT. Without it a file whose imports are all followable
    reads READY while the per-file gate refuses to let anyone touch it — measured, on the very
    gate this reader ranked first (gate-F80). Passing `None` renders the import axis alone and
    SAYS SO, rather than letting a partial answer wear a whole verdict's clothes.
    """
    if not found:
        return f"{path}: no import read — a fact about the READER, not the file\n"
    blocking = [d for d in found if d.blocks]
    rows = [
        f"  {d.kind:<11} {d.name:<28} line {d.line}" + (f"  — {d.detail}" if d.detail else "")
        for d in found
    ]
    rows.append("")
    rows.append(f"swap-readiness: {path}")
    if blocking:
        rows.append(f"  imports:  NOT READY — {len(blocking)} block a repoint")
        rows.append(
            "  ⚑ UNKNOWN blocks as firmly as UNPACKAGED: a dependency nobody "
            "classified is not one nobody needs."
        )
    else:
        rows.append("  imports:  READY — every import a packaged consumer can follow")

    if edit is None:
        rows.append("  editable: NOT ASKED — this is the IMPORT axis only, not a swap verdict")
        return "\n".join(rows) + "\n"
    state, detail = edit
    rows.append(f"  editable: {state} — {detail}")
    rows.append(
        "  SWAP READY"
        if not blocking and state == "CLEAN"
        else "  NOT SWAPPABLE — both axes must hold"
    )
    return "\n".join(rows) + "\n"


def main(out: list[str], argv: list[str]) -> int:
    """Report whether each named file could be repointed at the package."""
    paths = [a for a in argv if not a.startswith("-")]
    if not paths:
        out.append(
            "usage: swap_readiness.py <file.py> [...]\n"
            "  classifies every import as PACKAGED / UNPACKAGED / EXTERNAL / UNKNOWN\n"
        )
        return 2
    # ⚑ THE EDIT AXIS IS OPT-IN because it RUNS both checkers per file, which a wide survey
    # cannot afford. `--imports` keeps the cheap ranking; the default answers the real question.
    imports_only = "--imports" in argv
    worst = 0
    for path in paths:
        found = deps_of(path)
        edit = None if imports_only else editability(path)
        out.append(render(path, found, edit))
        if any(d.blocks for d in found) or (edit is not None and edit[0] != "CLEAN"):
            worst = 1
    return worst


if __name__ == "__main__":
    # ⚑ THE SUITE IS REACHED BY FLAG SO `run_selftests.discover()` SEES THIS MODULE
    # (⟡selftest-discovery). It could not be wired when this file was written: the suite
    # referenced the module and the module referenced the suite, and the per-file gate refuses a
    # write that leaves either dangling — so neither could land first. The module went in
    # without the hook, the suite followed, and this line closes the cycle.
    if "--selftest" in sys.argv:
        from substrate import swap_readiness_selftest

        raise SystemExit(0 if swap_readiness_selftest.selftest() else 1)

    _lines: list[str] = []
    _code = main(_lines, sys.argv[1:])
    sys.stdout.write("".join(_lines))
    raise SystemExit(_code)
