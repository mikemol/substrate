# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
r"""Enumerate the `.agda` sources under a root — THE enumeration authority.

⚑⚑⚑ THIS IS THE LAST PIECE THE BAN-GATE SWAP NEEDS, and I deferred it twice for a reason that
turned out to be half wrong. I grouped it with `agda_root_from` as "the filesystem half", but
those are different shapes: the root-finder WALKS UPWARD GUESSING A LAYOUT, which is what makes
it the application's, while this takes `root` as a PARAMETER and assumes nothing. A parameterized
walk over a caller-supplied root is exactly as portable as the pure functions beside it.

⚑⚑⚑ AND THE ORIGIN'S ARGUMENT FOR HAVING ONE AUTHORITY IS A GATE-VS-GATE DIVERGENCE, ARMED AND
WAITING. Measured: 59 files enumerate the corpus three different ways — `glob **`, `os.walk` plus
a suffix test, `rglob` — and **41 of them carry no `_build` filter**. That is harmless only
because `agda/_build/` currently holds `.agdai` files and zero `.agda`, so *the agreement is LUCK
rather than construction.* The first `.agda` to land under `_build` — a fixture, a vendored copy,
a generated module — splits the guarded routes from the unguarded ones, and since PRE-COMMIT
GATES sit on the unguarded side their censuses inflate while the build generator's does not.

⚑⚑ A SHARED NAME IS NOT A SHARED AUTHORITY, and this one was defined FOUR TIMES with DIFFERENT
BODIES — one filtering `_build` and sorting, another doing neither — reading as reuse at every
call site. That is the defect the promotion exists to end, not merely a tidiness argument.

⚑ `root` IS A PARAMETER AND SCOPING IS LEGITIMATE. Most callers pass the `Substrate` subtree; one
passes the whole `agda/` directory, which also catches the root aggregator module. A
subdirectory-scoped tool is a COMPLIANT CALLER WITH A NARROWER ROOT, never an exception — which
is what keeps a rederivation census honest rather than exemption-ridden.

⚑⚑ THE MEMO IS THE SHARED NODE OF THE CENSUS DAG, and its absence is why a thread pool over the
gates once measured SLOWER than serial: eleven ratchet gates each walk the same tree, so
concurrency parallelised the fan-out while leaving the shared root duplicated. *Dependency
structure first, then parallelism over what actually remains independent* — the two are not
alternatives. Fixing it in the authority fixes every consumer; fixing it in a gate fixes one.

⚑ AND A COPY IS RETURNED, ALWAYS. Callers mutate what they get back — extending it, sorting it in
place — so handing out the cached object would let one consumer corrupt every later one. *A cache
that changes answers is worse than no cache.*
"""

from __future__ import annotations

import os
from pathlib import Path

#: The extension every Agda source carries. ⚑ RE-EXPORTED FROM THE NAMING AUTHORITY rather than
#: respelled, because two spellings of one suffix is how a walk and a namer stop agreeing.
from substrate.agda_naming import SUFFIX

#: The directory a walk excludes by default — the build tree, which holds interface files and no
#: sources today. That "today" is the whole point: see the module docstring.
BUILD_DIR = "_build"

# ⚑ MEMOISED PER (root, include_build) PER PROCESS, never invalidated. These tools are
# short-lived and read a tree nobody edits mid-run; a long-lived caller that EDITS the tree would
# need invalidation and is a different kind of consumer.
_CACHE: dict[tuple[str, bool], list[str]] = {}


def agda_files(root: str | Path, *, include_build: bool = False) -> list[str]:
    """Return every `.agda` source under `root`, sorted.

    ⚑⚑ THE `_build` EXCLUSION IS THE POINT, not a convenience. Most enumeration sites in this
    tree lack it, and they agree with the guarded ones only because no `.agda` currently lives
    under the build directory. The first one that does splits the two populations, and the
    unguarded side includes pre-commit gates.

    ⚑ `include_build` IS KEYWORD-ONLY, because a bare `True` at a call site says nothing about
    what it turns on, and this flag changes which population a gate censuses.

    ⚑ A COPY IS RETURNED so a caller may sort or extend it in place without corrupting the memo
    for every later caller.
    """
    key = (str(Path(root).resolve()), include_build)
    hit = _CACHE.get(key)
    if hit is not None:
        return list(hit)
    out: list[str] = []
    for dirpath, dirnames, filenames in os.walk(root):
        if not include_build:
            # ⚑ PRUNED IN PLACE, which is what stops `os.walk` DESCENDING into the build tree.
            # Filtering the results instead would still walk thousands of interface files.
            dirnames[:] = [d for d in dirnames if d != BUILD_DIR]
        here = Path(dirpath)
        out.extend(str(here / f) for f in filenames if f.endswith(SUFFIX))
    _CACHE[key] = sorted(out)
    return list(_CACHE[key])


def sources(root: str | Path, *, include_build: bool = False) -> list[tuple[str, str]]:
    """Return `(path, text)` for every `.agda` source under `root`.

    ⚑⚑ THIS IS THE SHAPE `ban_census.census` TAKES, and it exists so a gate never re-derives the
    read. The census is a pure function of `(relpath, text)` pairs precisely so it can be cased
    without a tree; this is the adapter that supplies them from one.

    ⚑ A FILE THAT CANNOT BE READ IS SKIPPED, NOT GUESSED AT. Returning an empty string for it
    would silently shrink a census — and in a paydown-only ratchet a key that vanishes lowers a
    baseline nobody can raise again.
    """
    out: list[tuple[str, str]] = []
    for path in agda_files(root, include_build=include_build):
        try:
            text = Path(path).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        out.append((path, text))
    return out
