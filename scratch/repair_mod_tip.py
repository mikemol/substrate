#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Repair + finish the Graded.Mod tip retirement.

A first pass rewrote the tip IMPORT correctly but, on the re-run, mis-identified
the alias (an `import … as F` line is not matched by `import \\S*\\bF\\b`, so F
looked unimported) and expanded `open F.Over` instead of `open M.Over`.

This pass:
  1. REPAIRS: any injected block of consecutive `open <PKG>.<Leaf>.Over …` lines
     is collapsed back to the single line git says it replaced.
  2. FINISHES: the genuine tip open is expanded, with the alias recovered from
     the file's HEAD blob (`import <PKG> as <alias>`) — the only reliable source
     once the import line is gone.
"""
import os, re, subprocess, sys

_SNAPPED = []


def _snapshot_once(path):
    """Arm edit_snapshot on the FIRST write of a run; a no-op thereafter.

    ⚑ This tool rewrites files it read — the shape that made 33 files
    unrecoverable (Coxeter/Core.agda 76 lines -> 3).  The write is inside a loop,
    so a per-file `guard` would arm only the first file AND shell out to `git
    stash create` on every iteration; arming once per run is both correct and
    cheap.  Recovery is per-file and MANUAL by design — edit_snapshot never
    restores anything itself.
    """
    if _SNAPPED:
        return
    _SNAPPED.append(True)
    try:
        import edit_snapshot
        edit_snapshot.guard('repair_mod_tip', [path])
    except Exception as e:
        print(f"   \u26a0 snapshot unavailable ({e}) \u2014 recover via git if needed")



PKG = "Substrate.Algebra.Polynomial.Graded.Mod"
OPEN_INJ = re.compile(r"^\s*open\s+" + re.escape(PKG) + r"\.[A-Za-z]\w*\.Over\b")


def head_blob(path):
    try:
        return subprocess.run(["git", "show", f"HEAD:agda/{path}"], cwd=ROOT,
                              capture_output=True, text=True, check=True).stdout
    except subprocess.CalledProcessError:
        return ""


def removed_for(path):
    """{added-block-first-line -> the single line it replaced}, from git diff."""
    d = subprocess.run(["git", "diff", "-U0", "--", f"agda/{path}"], cwd=ROOT,
                       capture_output=True, text=True).stdout.split("\n")
    out, minus = {}, []
    for l in d:
        if l.startswith("@@"):
            minus = []
        elif l.startswith("-") and not l.startswith("---"):
            minus.append(l[1:])
        elif l.startswith("+") and not l.startswith("+++"):
            body = l[1:]
            if OPEN_INJ.match(body):
                cand = [m for m in minus if re.match(r"\s*open\s+\S+\.Over\b", m)]
                if cand:
                    out.setdefault(body, cand[0])
    return out


def repair(path, apply):
    full = os.path.join(ROOT, "agda", path)
    lines = open(full, encoding="utf-8").read().split("\n")
    rep = removed_for(path)

    # 1. collapse each injected block back to the line it replaced
    out, i, fixed = [], 0, 0
    while i < len(lines):
        if OPEN_INJ.match(lines[i]) and lines[i] in rep:
            orig = rep[lines[i]]
            j = i
            while j < len(lines) and OPEN_INJ.match(lines[j]):
                j += 1
            out.append(orig)
            fixed += 1
            i = j
        else:
            out.append(lines[i])
            i += 1

    # 2. expand the genuine tip open (alias recovered from HEAD)
    m = re.search(r"^(?:open\s+)?import\s+" + re.escape(PKG) + r"(?:\s+as\s+(\S+))?\s*$",
                  head_blob(path), re.M)
    alias = (m.group(1) if m else None) or PKG
    mods = sorted({l.split(f"import {PKG}.", 1)[1].strip()
                   for l in out if l.startswith(f"import {PKG}.")})
    tip = re.compile(r"^(?P<ind>\s*)open\s+" + re.escape(alias) + r"\.Over\b(?P<rest>.*)$")
    done = 0
    res = []
    for l in out:
        t = tip.match(l)
        if t and mods:
            rest = t.group("rest")
            cmt = ""
            c = re.search(r"\s--.*$", rest)
            if c:
                cmt, rest = c.group(0), rest[:c.start()]
            pub = ""
            if re.search(r"\s+public\s*$", rest):
                pub, rest = " public", re.sub(r"\s+public\s*$", "", rest)
            args = rest.rstrip()
            blk = [f"{t.group('ind')}open {PKG}.{mod}.Over{args}{pub}" for mod in mods]
            blk[0] += cmt
            res += blk
            done += 1
        else:
            res.append(l)

    if apply:
        _snapshot_once(full)
        open(full, "w", encoding="utf-8").write("\n".join(res))
    return fixed, done, alias, mods


if __name__ == "__main__":
    ROOT = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                          capture_output=True, text=True, check=True).stdout.strip()
    _rel = [a for a in sys.argv[1:] if not a.startswith("-")]
    # ⚑ ONE ACT: state the intent AND snapshot, BEFORE `apply` is bound.
    # `_snapshot_once` is correct where it runs but sits under `if apply:` inside
    # `repair`, so it is consulted after the decision rather than at it.
    # ⚑ THE ARGV PATHS ARE `agda/`-RELATIVE, so they are resolved here — handing
    # `_copy_untracked` a path that does not exist from the repo root would copy
    # nothing while reporting a snapshot, which is a false assurance.
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import edit_snapshot as _es
    _es.require_at_entry("repair_mod_tip",
                         paths=[os.path.join(ROOT, "agda", p) for p in _rel])
    apply = "--apply" in sys.argv
    for p in _rel:
        f, d, a, mods = repair(p, apply)
        print(f"{p}: repaired={f} expanded={d} alias={a} -> {','.join(mods)}")
    if not apply:
        print("(dry run — pass --apply to write)")
