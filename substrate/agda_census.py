# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Read the build's own per-module artifacts as a census, and explain each stale verdict.

Extracted from `scratch/split_census.py` as part of ⟡drain-split-census. One
responsibility: turn the logs and cores `make` already wrote into per-module verdicts, and
name the CAUSE behind every `stale` one.

⚑ THE CENSUS ALREADY EXISTS ON DISK, AND IT WAS BEING RE-COMPUTED (operator, 2026-08-01:
*"if you want a census, a full `make` ought to be able to produce it as a side effect of an
existing optimized parallel make process that honors dependencies"*). The generated
makefile emits, per module, a `.agdai` target whose recipe redirects agda's output to
`<Mod>.agdai.log` — it calls that *"interleave-proof by construction"* precisely so
log-driven tooling can read it. MEASURED: 2810 such logs on disk, all non-empty. Every
ingredient the origin's `verify --leaves` recomputed was already there: per-module compile
output, dependency ORDER, PARALLELISM, and INCREMENTALITY. That version had none of them —
it recompiled all 1322 leaves from scratch in dependency-BLIND order, which is not merely
slower: it cannot distinguish *"this leaf is broken"* from *"its dependency was never
built"*, the exact distinction `blame` exists to draw. **A census of a build is a READ of
the build's artifacts, not a second build.**

⚑ AND A LOG IS ONLY EVIDENCE IF IT IS FRESH — TRANSITIVELY (operator, 2026-08-01: *"You'll
need to verify that the log is fresh wrt the current code state of the file it reflects and
the files that depends on"*). The first cut ignored mtimes and reported `clean=2802` of
2810 on a tree with known-broken modules: the logs described a state before that arc's
edits, so a stale artifact was about to become a confident wrong verdict — the same shape
as `fix_stale_using` reading logs that no longer described the tree (§12, R1), which cost a
47-of-53 refusal rate once measured honestly. A module whose log fails the test is reported
`stale`, never `clean`: it is UNMEASURED, and saying so is the whole point (`Guard (2)` of
the ratchet discipline — *an incomplete census is not a low count*).
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from substrate.agda_import_dag import import_dag

# The verdicts that mean `make` reported a genuine failure for a module, as opposed to never
# having reached it. Named once: a second spelling at a call site is how a blocked module
# starts being reported as merely unbuilt.
FAILED_VERDICTS = frozenset({"build-failed", "own", "dependency"})

BUILD_VER = "2.8.0"

type Blame = Callable[[str, str], tuple[str, str | None]]


def _mtime(path: Path) -> float:
    """Return `path`'s mtime, or 0.0 when it cannot be read."""
    try:
        return path.stat().st_mtime
    except OSError:
        return 0.0


def _module_of(rel: str) -> str:
    """Return the module name for a source relpath."""
    return rel[:-5].replace("/", ".") if rel.endswith(".agda") else rel


def census_from_build(
    blame: Blame,
    root: str = "agda",
) -> list[tuple[str, str, str | None]]:
    """Return `[(module_path, verdict, cited)]` read from the BUILD's own per-module logs.

    ⚑ `blame` IS INJECTED, NOT IMPORTED, AND THAT IS THE POINT. The own-vs-dependency rule
    lives in `split_pipeline.blame` and has eight call sites across three tools; a private
    copy here would be a second authority for one relation — the `agda_files()` class (§6d),
    which once existed as FOUR bodies under one name, two of them feeding pre-commit gates.
    Taking it as a parameter keeps exactly one implementation while leaving this module free
    of the driver.

    ⚑ THE IMPORT DAG COMES FROM THE MAKEFILE GENERATOR, NOT A LOCAL SCAN, so freshness here
    is judged by exactly the edges `make` judges staleness by. The origin's first cut called
    a non-existent `agda_lex.imports_of` behind a `hasattr` guard, which would have silently
    made every import set EMPTY and reduced the check to *"newer than its own source"* — **a
    guard that degrades to measuring nothing is worse than a crash.**

    ⚑ STALE IS ITS OWN VERDICT, NOT A SILENT PASS — AND IT HAS TWO CAUSES. `make -k` builds
    every branch it can, so a module whose DEPENDENCY failed is never attempted, gets no
    fresh log, and lands here. `stale` therefore conflates *"nobody rebuilt this yet"* with
    *"make could not reach it"* — only the first is a measurement gap; the second is a
    FINDING. MEASURED after a full `make -C agda -j -k`: 121 targets failed, yet the
    log-derived `own` count was 41, because a failed module leaves NO fresh log to read.
    `stale_why` is the reader that separates them.
    """
    disk, deps, _rdeps, _s2m = import_dag()
    src_of = {m: Path(root, rel) for m, rel in disk.items()}
    deepest: dict[str, float] = {}

    def newest_dep(module: str, seen: set[str] | None = None) -> float:
        """Return the newest source mtime over `module` and its transitive imports."""
        if module in deepest:
            return deepest[module]
        seen = seen if seen is not None else set()
        if module in seen or module not in src_of:
            return 0.0
        seen.add(module)
        best = _mtime(src_of[module])
        for dep in deps.get(module, ()):
            best = max(best, newest_dep(dep, seen))
        deepest[module] = best
        return best

    out: list[tuple[str, str, str | None]] = []
    for log in sorted(Path(root, "_build").rglob("*.agdai.log")):
        core = log.with_suffix("")  # strip ".log" -> the .agdai path
        text = log.read_text(encoding="utf-8", errors="replace")
        core_str = str(core)
        marker = core_str.find("/agda/Substrate/")
        rel = core_str[marker + len("/agda/") :] if marker >= 0 else core.name
        rel = rel[:-6] + ".agda" if rel.endswith(".agdai") else rel
        if _mtime(log) < newest_dep(_module_of(rel)):
            out.append((rel, "stale", ""))
            continue
        # The build's OWN success criterion: the recipe only `touch`es the core after agda
        # exits 0, so a missing core IS the failure signal.
        if core.exists():
            out.append((rel, "clean", ""))
        else:
            verdict, cited = blame(rel, text)
            out.append((rel, verdict, cited))
    return out


def stale_why(blame: Blame, root: str = "agda") -> list[tuple[str, str, str]]:
    """Return `[(module, cause, witness)]` — WHY each `stale` module is unmeasured.

    ⚑⚑ BUILT AFTER THREE UNFOUNDED THINGS WERE ASSERTED ABOUT `stale` IN ONE SESSION
    (2026-08-18): that `make -C agda -j` refreshes it, that it was flattering the clean
    count, and that it would drop to ~0. It went 78 -> 80 across a full `-k` build and two
    censuses, `clean` and `blocked` byte-identical. **The count was askable and the CAUSE was
    not, so it was guessed at — three times.**

    ⚑ AND THE CENSUS'S OWN ADVICE IS WRONG FOR MOST OF THIS POPULATION. It prints *"`make -C
    agda -j` refreshes them"*, which is true only for `unbuilt`.

    Causes, and they want different work:
      `blocked-upstream` — a transitive import FAILED, so `make -k` never attempted this
          module and it has no fresh log. Not a gap: it is the blast radius, and no number of
          rebuilds moves it. Fix the root.
      `unbuilt` — every import is clean and the log simply predates the source. THIS is the
          one a rebuild fixes.
      `no-core` — the log is fresh but the `.agdai` is absent, so the compile produced no
          core. Distinct from both: the freshness test and `make`'s own up-to-date test
          DISAGREE about this module, which is the shape worth knowing about.

    The witness is the specific failing or newer import, never a bare verdict.
    """
    _disk, deps, _rdeps, _s2m = import_dag()
    src_of = {m: Path(root, rel) for m, rel in _disk.items()}
    verdict = {_module_of(rel): v for rel, v, _c in census_from_build(blame, root)}

    out: list[tuple[str, str, str]] = []
    for module, state in sorted(verdict.items()):
        if state != "stale":
            continue
        # ⚑ THE FIRST QUESTION IS WHETHER MAKE COULD EVEN REACH IT. A transitive import that
        # is build-failed or itself stale means this module was never attempted; reporting it
        # as "needs a rebuild" would send an operator to run the build that cannot fix it.
        bad = ""
        seen: set[str] = set()
        stack = list(deps.get(module, ()))
        while stack and not bad:
            dep = stack.pop()
            if dep in seen:
                continue
            seen.add(dep)
            if verdict.get(dep) in FAILED_VERDICTS:
                bad = dep
            else:
                stack.extend(deps.get(dep, ()))
        if bad:
            out.append((module, "blocked-upstream", bad))
            continue
        core = Path(root, "_build", BUILD_VER, "agda", *module.split(".")).with_suffix(".agdai")
        if not core.exists():
            out.append((module, "no-core", "no .agdai — compile produced no core"))
            continue
        # Every import clean and a core present: the log genuinely predates a source. Name
        # WHICH source, so the claim is checkable.
        newest, who = 0.0, ""
        for candidate in [module, *sorted(seen)]:
            src = src_of.get(candidate)
            when = _mtime(src) if src is not None else 0.0
            if when > newest:
                newest, who = when, candidate
        out.append((module, "unbuilt", who or module))
    return out
