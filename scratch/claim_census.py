#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""claim_census.py — enumerate FALSIFIABLE prose claims and check the mechanical ones.

A comment or docstring that asserts a COUNT ("39 importers"), an ABSENCE ("no consumers",
"not yet in the tree"), or an EXPORT ("thin re-export shim") is a proposition the tree can
falsify. Today nothing falsifies them, so they go stale — and when the stale one sits in a
GATE it does not merely misinform, it EXEMPTS (check_public_ratchet.py grandfathers 16
baseline keys on "Graded.agda IS the public API for 39 importers"; the count is 1).

This is the exploratory census that produces (a) the fix list and (b) the predicates worth
promoting into a pre-commit advisory. It deliberately OVER-FIRES: the output is read to learn
which shapes are checkable with a low false-positive rate, not to gate anything yet.

⚑ It does NOT flag MEASUREMENTS. A dated claim with a method ("MEASURED 2026-07-26: Mod
175->116") is evidence and is the most valuable text in the tree; a bare count is a hypothesis.
The predicates below match counts and absences only.

    claim_census.py [--kind count|zero|absent|shim] [--checked-only] [--verbose]
"""
import os, re, sys, collections
import os as _oe, sys as _se
_se.path.insert(0, _oe.path.dirname(_oe.path.abspath(__file__)))
from agda_lex import agda_files as _agda_files

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AGDA = os.path.join(ROOT, "agda")
SUBSTRATE = os.path.join(AGDA, "Substrate")
SCRIPTS = os.path.join(ROOT, "scripts")

# ---------------------------------------------------------------- predicates
PRED = {
    "count": [
        re.compile(r"(?i)\b(?:~\s*)?(\d+)\s+(?:direct\s+|real\s+|live\s+)?"
                   r"(importers?|consumers?|users?|call[- ]sites?)\b"),
        re.compile(r"(?i)public\s+API\s+for\s+(?:~\s*)?(\d+)"),
    ],
    "zero": [
        re.compile(r"(?i)\b(?:no|zero)\s+(?:other\s+|external\s+|real\s+|live\s+|current\s+)?"
                   r"(importers?|consumers?|users?|call[- ]sites?)\b"),
        re.compile(r"(?i)\b(unconsumed|never imported|never consumed|dead code|zero importers)\b"),
    ],
    "absent": [
        re.compile(r"(?i)(not yet in the tree|not in the tree|does not exist|is absent|"
                   r"grep-confirmed absent|absent from the tree|no such (?:module|def|term|lemma))"),
    ],
    "shim": [
        re.compile(r"(?i)(re-?export(?:s|ing)? shim|thin re-?export|thin shim|"
                   r"preserves the public interface)"),
    ],
}

# A dated MEASUREMENT is evidence, not a hypothesis — never flag it.
MEASURED = re.compile(r"(?i)\bMEASURED\b|\bmeasured\s+\d{4}-\d{2}-\d{2}|\(measured")


# ---------------------------------------------------------------- corpus
def agda_files():
    """Delegates to `agda_lex.agda_files` — THE enumeration authority.

    ⚑ This name was defined FOUR times with FOUR DIFFERENT BODIES: two generators that
    sorted only WITHIN a directory (so the global order differed), one returning a sorted
    list WITH a `_build` guard, one sorting nothing.  A shared NAME is not a shared
    authority — it reads as reuse at every call site while silently disagreeing.
    41 of 59 enumeration sites lacked the `_build` filter; harmless only because
    `agda/_build/` holds zero `.agda` today, i.e. the agreement at 2764 is luck.
    """
    return _agda_files(SUBSTRATE)

def _scripts_dir_py():
    """The .py files DIRECTLY IN `scripts/` — one directory, not a corpus.

    ⚑ RENAMED FROM `py_files`, AND THE LESSON WAS ALREADY IN THIS FILE.  The
    docstring immediately above records `agda_files` having been "defined FOUR
    times with FOUR DIFFERENT BODIES … a shared NAME is not a shared authority",
    and this function sat directly beneath it committing the same offence
    against the PYTHON corpus.

    It is not a rival to `pycodemod.py_files`: this is `listdir` (NON-recursive)
    over one fixed directory, yields a GENERATOR, and takes no arguments — three
    incompatibilities that make "converge the bodies" the wrong repair. Its one
    caller is `main` at :144, which wants exactly the gate scripts.

    ⚑ THE FALSE SIGNAL IT PRODUCED IS THE POINT: `--rivals py_files` read
    "3 defs, 0 delegating" and an audit concluded three corpus definitions were
    drifting under two pre-commit gates. Measured, both gates call
    `pycodemod.py_files` QUALIFIED and neither rival has an off-file caller — so
    the finding was a fact about the NAME, reported as a fact about the
    substrate."""
    for fn in sorted(os.listdir(SCRIPTS)):
        if fn.endswith(".py"):
            yield os.path.join(SCRIPTS, fn)


def comment_lines(path):
    """(lineno, text) for comment/docstring lines only — never live code."""
    agda = path.endswith(".agda")
    out, in_block = [], False
    try:
        src = open(path, errors="replace").read().split("\n")
    except OSError:
        return out
    for i, ln in enumerate(src, 1):
        s = ln.strip()
        if agda:
            if s.startswith("{-"):
                in_block = not s.endswith("-}")
                out.append((i, s)); continue
            if in_block:
                out.append((i, s))
                if s.endswith("-}"):
                    in_block = False
                continue
            if s.startswith("--"):
                out.append((i, s))
        else:
            if s.startswith("#"):
                out.append((i, s))
            elif '"""' in s or "'''" in s or in_block:
                out.append((i, s))
                if s.count('"""') == 1 or s.count("'''") == 1:
                    in_block = not in_block
    return out


# ---------------------------------------------------------------- the index the checks need
IMP = re.compile(r"^\s*(?:open\s+)?import\s+(Substrate[\w.]*)")


def importer_index():
    """{module_path_rel: {importing_file_rel, …}} over the whole Agda tree."""
    idx = collections.defaultdict(set)
    for p in agda_files():
        rel = os.path.relpath(p, AGDA)
        try:
            for ln in open(p, errors="replace"):
                m = IMP.match(ln)
                if m:
                    idx[m.group(1).replace(".", "/") + ".agda"].add(rel)
        except OSError:
            continue
    return idx


def module_of(path):
    return os.path.relpath(path, AGDA)


def has_public(path):
    try:
        return any(re.search(r"\bpublic\b", ln) and not ln.strip().startswith("--")
                   for ln in open(path, errors="replace"))
    except OSError:
        return False


# ---------------------------------------------------------------- main
def main():
    kinds = [sys.argv[sys.argv.index("--kind") + 1]] if "--kind" in sys.argv else list(PRED)
    checked_only = "--checked-only" in sys.argv
    verbose = "--verbose" in sys.argv

    idx = importer_index()
    files = list(agda_files()) + list(_scripts_dir_py())
    hits = collections.defaultdict(list)

    for p in files:
        rel = os.path.relpath(p, ROOT)
        for lineno, text in comment_lines(p):
            if MEASURED.search(text):
                continue                                    # evidence, not a hypothesis
            for kind in kinds:
                for rx in PRED[kind]:
                    m = rx.search(text)
                    if not m:
                        continue
                    hits[kind].append((rel, lineno, text.strip()[:150], m, p))
                    break

    # ---- mechanical checks -------------------------------------------------
    findings = []
    for rel, lineno, text, m, path in hits.get("count", []):
        if not path.endswith(".agda"):
            continue
        claimed = int(m.group(1))
        actual = len(idx.get(module_of(path), ()))
        verdict = "OK" if claimed == actual else ("STALE" if actual else "STALE (zero)")
        if claimed != actual:
            findings.append(("count", rel, lineno, f"claims {claimed}, tree says {actual}", text))

    for rel, lineno, text, m, path in hits.get("zero", []):
        if not path.endswith(".agda"):
            continue
        actual = len(idx.get(module_of(path), ()))
        if actual:
            findings.append(("zero", rel, lineno, f"claims none, tree says {actual}", text))

    for rel, lineno, text, m, path in hits.get("shim", []):
        if not path.endswith(".agda"):
            continue
        if not has_public(path):
            findings.append(("shim", rel, lineno, "claims re-export, file has NO `public`", text))

    # ---- report ------------------------------------------------------------
    print("=== CENSUS (raw hits per predicate; over-fires by design) ===")
    for kind in kinds:
        n = len(hits.get(kind, []))
        agda_n = sum(1 for h in hits.get(kind, []) if h[4].endswith(".agda"))
        print(f"  {kind:<7} {n:>4} hits  ({agda_n} agda / {n - agda_n} scripts)")

    print(f"\n=== MECHANICALLY FALSIFIED ({len(findings)}) ===")
    for kind, rel, lineno, why, text in sorted(findings):
        print(f"  [{kind}] {rel}:{lineno} — {why}")
        if verbose:
            print(f"        {text}")

    if not checked_only and verbose:
        print("\n=== UNCHECKED HITS (need a subject-resolver or human read) ===")
        for kind in ("absent", "shim"):
            for rel, lineno, text, _m, _p in hits.get(kind, [])[:40]:
                print(f"  [{kind}] {rel}:{lineno}  {text}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
