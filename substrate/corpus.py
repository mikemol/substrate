#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""THE population: which `.py` files are this repo's corpus, and how a root resolves.

⚑ THIS IS THE SEAM EVERY OTHER MODULE SITS ON, AND `--calls py_files` MEASURED IT: 71 call
sites, of which 3 are in OTHER TOOLS (`shared_cache.py`, `check_mypy_ratchet.py`,
`check_scratch_independence.py`). The corpus walk was already the toolkit's public
foundation; making it a package module names what was true.

⚑⚑ SPLIT OUT OF `scratch/_pycodemod_core.py` (⟡scratch-cluster-cut), AND THE CLUSTER IS THE
REASON. MEASURED: `_pycodemod_core` is the ONE leaf of the `scratch/` analysis toolkit — 93
own findings, zero callees — while seven of its siblings sit at an identical 4,712 closure
over an identical 20 deps, i.e. one strongly-connected component reaching itself. A cycle at
that size is not an obstacle to route around; it is the modules being too COARSE to admit an
acyclic order, and n-splitting is what creates the leaves an order needs.

⚑ THE CORE ITSELF RECORDS THE CYCLE AS ITS OWN REASON FOR EXISTING: *"HERE AND NOT IN
`pycodemod.py` because the selftest module must reach them, and `pycodemod` imports THAT —
the cycle is what places these in the core."* A module whose membership rule is "whatever
breaks a cycle" holds argv parsing, corpus enumeration, importlib probing, libcst literal
evaluation, tarfile extraction and a process pool — six concerns, which is exactly the shape
its 93 findings have (28 `PTH*`, one `S202`, three `PLW0603`, a `C901`).

⚑ IT LANDS IN `substrate/`, NOT BESIDE ITS PARENT. Operator ruling 2026-08-28: *"create a
different folder. we're trying to get stuff OUT of scratch."* Packaging in place would cement
the temporary and make `check_scratch_independence`'s invariant unstatable.

⚑ WHAT DID NOT COME WITH IT, AND WHY THAT MATTERS. `ROOT` is REBOUND by `_pycodemod_core`'s
`corpus.__enter__` under `global ROOT`, so `--archive` / `--in` swap the corpus under every
mode at once. That envelope and its global must move together or the rebind targets a name
nothing reads — the envelope goes inert while still reporting success. So this module takes
its root as a PARAMETER with a default, which is the same capability without the global: a
caller wanting a different corpus passes one, and nothing has to be rebound.
"""

from __future__ import annotations

import os
from pathlib import Path

# ⚑ `absolute()`, NEVER `resolve()`. `PTH100` recommends `Path.resolve()` as
# `os.path.abspath`'s replacement and it is NOT one: `resolve()` FOLLOWS SYMLINKS. That
# matters HERE specifically — bazel's convenience links are symlinks, and following them
# would rewrite every path into the output base where the name test can no longer see them.
ROOT = Path(__file__).absolute().parent.parent

# ⚑ DISCOVERED, NOT FROZEN — and the frozen form was silently under-reporting. This was
# `("scratch", "scripts")`, so `catalog/` (the worklist's item and figure witnesses) was
# OUTSIDE the corpus: `--attr own_agda_files_definers` returned `0 read(s)` while
# `items.py:375` plainly calls it. An empty result from a query whose scope excludes the
# subject is not a finding, it is a gap wearing a finding's clothes — and every unscoped
# question the tool answered was under-reporting by exactly that directory.
#
# THIRD OCCURRENCE OF THIS EXACT DEFECT IN THE REPO: `run_selftests.DIRS` was a frozen tuple
# twice (missing `jea/`, then missing `catalog/` — which did not exist when the tuple was
# written), and its own docstring argued against hardcoding while hardcoding one level up. A
# roster can only ever be as current as its last edit; the fix is to discover, not to add a
# fourth entry.
SKIP_DIRS = frozenset(
    {"agda", "node_modules", "__pycache__", "docs", ".venv", ".git", ".edit-snapshots"}
)

# ⚑ GENERATED OUTPUT TREES ARE NOT THE CORPUS. Same class as `.edit-snapshots` backups
# polluting a census: a MACHINE-DERIVED copy of a source file reads exactly like the source,
# so it enters every count silently. Measured: `--in <paperkit> --calls references` returned
# 135KB of hits, nearly all from `bazel-bin/.../mut_project__*.mutated.py` — mutation-testing
# artifacts, one copy per mutant per build configuration, burying the single real definition.
# These are matched as whole PATH COMPONENTS, so `rebuild/` and `buildtools/` are unaffected.
# Naming one of these trees explicitly as a root still reaches it — a different question,
# which gets a different answer.
GENERATED_DIRS = frozenset(
    {
        "bazel-bin",
        "bazel-out",
        "bazel-testlogs",
        "bazel-genfiles",
        "build",
        "dist",
        "_build",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        ".tox",
        ".nox",
        ".eggs",
    }
)

# Matched as whole path COMPONENTS, like GENERATED_DIRS above.
_SKIP_PARTS = frozenset(
    {".edit-snapshots", "__pycache__", ".venv", "site-packages", "node_modules", "_build", ".git"}
)

# bazel's convenience symlinks are named `bazel-<workspace>`, so a set cannot enumerate
# them — the workspace name is per-repo.
_BAZEL_LINK = "bazel-"


class PopulationError(Exception):
    """A requested root resolved to nothing — raised rather than silently emptied.

    ⚑ THE MESSAGE IS THE CLASS'S, NOT THE RAISE SITE'S. It must name BOTH trees that were
    searched, because the defect it reports is a caller believing one was consulted when the
    other answered. A message assembled at the raise site is one that can be assembled
    differently at the next raise site.
    """

    def __init__(self, requested: str, root: Path) -> None:
        """Name what was asked for and both trees that were searched."""
        super().__init__(f"no such path in the current directory or in {root}: {requested}")


def excluded(rel: Path) -> bool:
    """Report whether a root-relative directory is outside the corpus.

    ⚑ PUBLIC, BECAUSE THE EXCLUSION RULE IS THE CONTRACT. What counts as corpus is exactly
    what three other tools and a pre-commit gate must agree with; a private predicate says
    the answer is nobody's business while every consumer depends on it, and it makes the rule
    untestable from outside without reaching past the underscore.

    ⚑ VENDORED CODE IS NOT OUR CORPUS, AND ITS ABSENCE WAS UNTESTED. The exclusion list held
    `__pycache__` and `.edit-snapshots` but not virtualenvs, so
    `scratch/.venv/…/setuptools/…/bdist_msi.py` (PY2 syntax) entered the population and made
    mypy refuse the ENTIRE run. `--roundtrip` and `--dead` were reading it too — silently,
    because a third-party file that round-trips looks exactly like one of ours.

    ⚑ MATCH A PATH COMPONENT, NOT A SUBSTRING. `"build" in rel` would also eat `rebuild/`,
    `buildtools/` and any real package whose name merely CONTAINS the word — the class of bug
    this repo already paid for with a hand-written regex whose `.` matched any character.

    ⚑⚑ THE SKIP IS RELATIVE TO THE REQUESTED ROOT, NOT ABSOLUTE. When a caller NAMES a
    package under `site-packages`, skipping it would return an empty population for the one
    question the mode exists to answer — an absence wearing a finding's clothes. Vendored
    code stays out of the DEFAULT corpus because the default roots never reach it; asking for
    it explicitly is a different question, and gets a different answer.
    """
    parts = set(rel.parts)
    return (
        bool(parts & _SKIP_PARTS)
        or bool(parts & GENERATED_DIRS)
        or any(p.startswith(_BAZEL_LINK) for p in parts)
    )


def roots(root: Path = ROOT) -> tuple[str, ...]:
    """Discover the top-level directories that make up the corpus.

    ⚑ THE SKIP VOCABULARY MUST APPLY AT THE ROOT LEVEL TOO, AND ONCE DID NOT. `py_files`
    filtered generated trees by walking the relative path, but a generated tree that is a
    TOP-LEVEL entry becomes its own root — and then that path starts BELOW it, so the
    component check never sees the name and the whole tree is admitted. Measured on paperkit:
    `bazel-bin/` is a top-level symlink into bazel's output base, so `--in <paperkit>
    --imports` attributed `pathlib` to 1425 files (mutation-testing copies) and `--calls
    references` returned 135KB of generated hits, with the filter installed and doing
    nothing. ONE vocabulary, enforced at BOTH levels.

    ⚑ AND `is_dir()` FOLLOWS SYMLINKS. bazel's convenience links are symlinks, so a directory
    test admits them as ordinary directories; the NAME test is what excludes them, which is
    exactly why the name test has to be here.
    """
    return tuple(
        sorted(
            d.name
            for d in root.iterdir()
            if d.is_dir()
            and not d.name.startswith(".")
            and d.name not in SKIP_DIRS
            and d.name not in GENERATED_DIRS
            and not d.name.startswith(_BAZEL_LINK)
        )
    )


def resolve_root(r: str, root: Path = ROOT) -> Path:
    """Resolve one caller-supplied root: CWD FIRST, then the tool's own tree.

    ⚑⚑ IT WAS AN UNCONDITIONAL JOIN AGAINST THE TOOL'S ROOT, SO A RELATIVE PATH NAMED A FILE
    IN THE TOOL'S TREE RATHER THAN THE CALLER'S. This tooling is symlinked into other
    checkouts, and a peer running `--commentary tools/no_owner_audit.py` from their own repo
    got SUBSTRATE'S ENTIRE 6,005-line census back: the path does not exist under the tool's
    root, the walk on a missing directory yields nothing, the population came back empty, and
    every caller falls through to the default corpus. **They nearly recorded my flag count as
    their repo's**, and what stopped them was recognising my filenames — not anything the
    tool said.

    ⚑ A path like `scripts/` exists in BOTH trees, and that case is worse: it resolves
    silently to mine and the answer is well-formed, plausible and about the wrong repo.

    ⚑ CWD WINS, BECAUSE THE CALLER'S SHELL IS WHAT THEY MEANT. The root fallback stays for
    the modes and gates inside this tree that pass tree-relative paths and are invoked from
    anywhere; it is a FALLBACK, not the first reading, so it can only widen what a caller
    could already reach — never redirect it.

    ⚑ NEITHER TREE HAS IT — AND SILENTLY RETURNING THE DEFAULT CORPUS IS THE WHOLE BUG. An
    unresolvable root is a fact about the QUERY and must be raised, not absorbed.
    """
    p = Path(r)
    if p.is_absolute():
        return p
    here = (Path.cwd() / r).absolute()
    if here.exists():
        return here
    there = root / r
    if there.exists():
        return there
    raise PopulationError(r, root)


def py_files(*requested: str, root: Path = ROOT) -> list[str]:
    """Return every tool source under the given roots, sorted. Defaults to the whole corpus.

    ⚑ ONE ENUMERATION, NOT ONE PER CODEMOD — the rule `agda_lex.agda_files` enforces for the
    Agda corpus, applied to the Python corpus. (For a TRANSFORM the CLI does its own walking;
    this is for the QUESTIONS.)
    """
    out: list[str] = []
    for r in requested or roots(root):
        base = resolve_root(r, root)
        if base.is_file():
            out.append(str(base))
            continue
        for d, _sub, files in os.walk(base):
            if excluded(Path(d).relative_to(base)):
                continue
            out.extend(str(Path(d) / f) for f in files if f.endswith(".py"))
    return sorted(out)
