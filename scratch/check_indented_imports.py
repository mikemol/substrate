#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Post-rewire sweep: find `open import <parent>` occurrences rewire_to_leaves.py
CANNOT see.

rewire_to_leaves.py's regexes are anchored at column 0 (`^open import {P}` /
`^open import {P} using (...)`), because `re.M`'s `^` matches the start of the
LINE, not "after leading whitespace". An `open import <old-barrel>` sitting
inside a `where`/`module _ (...) where` body (indented) — or wrapped in any
other leading whitespace — slips through untouched, and the miss is invisible
until a full build fails on a now-deleted module. This tool finds those misses
in one grep-speed pass, before paying for the build.

    python3 scratch/check_indented_imports.py Substrate.Foo.Bar [Substrate.Baz ...]

Run from the REPO ROOT (paths are `agda/Substrate/...`, mirroring every other
tool in this family — see F8 in one-lemma-per-file.md). Reports file:line for
every surviving reference, tagged `indented` (rewire_to_leaves missed it) or
`top-level` (rewire_to_leaves SHOULD have caught this — a sanity check on the
rewire's own leaf-owner map: it fires when a name the file used had no entry).

Exit 0 iff every named parent has zero surviving references.
"""
import re, sys, glob

AG = "agda"


def sweep(parent):
    P = re.escape(parent)
    # `open import P` / `import P` / `open import P using (...)` / `... public`,
    # with or without a trailing comment — same statement-shape the rest of the
    # split/rewire family recognises, but WITHOUT the `^`-at-column-0 assumption.
    # ⚑ `(?![\w.-])`, NOT a bare `\b`: `.` is already a non-word char, so `\b`
    # right after P matches the word/non-word transition into a LONGER dotted
    # continuation (`P.Bool` reads as "P" followed by a boundary) — the same
    # hyphen/dot-boundary class documented repeatedly elsewhere in this repo's
    # tooling. Caught live: this flagged every leaf's own `open import P.Leaf`
    # as a false "surviving reference to P".
    # ⚑ THE PREFIX IS NOT ALWAYS WHITESPACE.  An import can be preceded on its
    # own line by a KEYWORD that opens a block — `where open import M`,
    # and in principle `private`/`abstract` — so `^[ \t]*` cannot reach it and
    # the sweep reported CLEAN over a live broken reference.  That is worse than
    # a rewriter miss: this sweep is the VERIFIER the pipeline trusts to catch
    # what the column-0 rewriter structurally cannot see (F19), so a blind spot
    # here reads as proof of absence.
    # MEASURED: `Algebra/Q/Embeddings.agda:74`,
    # `  where open import Substrate.Algebra.Q using (module ℚ)` — the split
    # deleted Q, the build died `[FileNotFound]`, and the sweep still said
    # "clean (no remaining references)".  15 such `where`-prefixed imports exist
    # tree-wide, so this hides a real class, not one file.
    stmt = re.compile(
        rf"^([ \t]*)((?:where|private|abstract)\s+)?"
        rf"((?:open\s+)?import\s+{P}(?![\w.-]))(.*)$")
    hits = []
    for path in glob.glob(f"{AG}/Substrate/**/*.agda", recursive=True):
        with open(path, encoding="utf-8") as fh:
            for i, line in enumerate(fh, 1):
                m = stmt.match(line)
                if not m:
                    continue
                # A keyword prefix means the statement is inside a block body,
                # which is the `indented` class regardless of leading columns.
                kind = "indented" if (m.group(1) or m.group(2)) else "top-level"
                hits.append((path, i, kind, line.rstrip()))
    return hits


def main(argv):
    parents = argv[1:]
    if not parents:
        print("usage: check_indented_imports.py <Parent.Module> [...]")
        return 1
    any_hits = False
    for parent in parents:
        hits = sweep(parent)
        if not hits:
            print(f"{parent}: clean (no remaining references)")
            continue
        any_hits = True
        print(f"{parent}: {len(hits)} remaining reference(s)")
        for path, i, kind, line in hits:
            print(f"   [{kind}] {path}:{i}: {line.strip()}")
    return 1 if any_hits else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
