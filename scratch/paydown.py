#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""paydown.py — ⟡public-paydown at tree scale, driven to a FIXED POINT by make.

    strip every WHOLESALE `open … public`  →  make -k -j  →  fix every reported error  →  repeat

`make` decides precisely what needs rebuilding and in what order (user, 2026-07-26), so the
driver never models the dependency graph itself: it just re-runs make and consumes the error
set. Each pass is strictly smaller than the last, or the loop stops.

Fixing reuses scratch/scope_fix.py: `[NotInScope]` names its owner; `[NoParseFor*]` names none
(a missing operator/constructor makes the expression unparseable) and is resolved from a SEED —
the re-export list each stripped conduit had at HEAD.

  paydown.py --strip [PREFIX]     strip wholesale re-exports (default: all of Substrate/)
  paydown.py --fix   [--max N] {--dry-run|--apply}
                                  make → fix → repeat until green or no progress
  paydown.py --recheck {--dry-run|--apply}
                                  RE-RESOLVE every import THIS TOOL added, under the corrected
                                  shape-DB ranking. Run 1 ranked candidates by path proximity
                                  alone and wrote e.g. `Algebra.F2.+-assoc` into a ℕ context
                                  (→ `[UnequalTerms] ℕ !=< F₂`); those imports are still in the
                                  tree. It reads `git diff` + `git show HEAD:` to tell ITS OWN
                                  added lines from pre-existing ones, so it only repoints its own.
  paydown.py --status             how many wholesale sites remain

⚑ THE MUTATION INTENT IS REQUIRED, NOT DEFAULTED — `--fix` and `--recheck` each take
`--dry-run` XOR `--apply`, and neither stated is a REFUSAL (⟡explicit-mutation, operator
2026-08-24: *"one or the other must be specified at every invocation; specifying neither
is not acceptable"*).

⚑⚑ AND `--dry` — THE OLD SPELLING — IS NOW A NEAR MISS THAT REFUSES AND NAMES ITS
SUCCESSOR.  The prior reading kept `--dry` deliberately, reasoning that renaming it would
turn an operator's muscle-memory into *"an unknown-and-ignored argument on a tool whose
write path once left 33 files unrecoverable."*  That reasoning was SOUND AND ITS PREMISE
IS GONE: unknown-and-ignored was the hazard precisely because the tool then fell through
to WRITING.  It no longer falls through to anything — `edit_snapshot.NEAR_MISS_SPELLINGS`
catches `--dry` by name and prints `--dry → --dry-run`, so muscle memory now gets a
correction instead of a silent mutation.  A typo'd `--dry-run` (the live hazard: this tool
validated no argv at all) is caught by the same guard.

Run from agda/.
"""
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
import scope_fix as SF
import os as _oe, sys as _se
_se.path.insert(0, _oe.path.dirname(_oe.path.abspath(__file__)))
from agda_lex import agda_files as _agda_files

# ⚑⚑ `_snapshot_once` WAS DELETED HERE (Ⓐ49 ⟡split-8-unprotected).  Its rationale is
# KEPT AS RESIDUE — it was RIGHT about the danger, wrong only about PLACEMENT:
#
#   "This tool rewrites files it read — the shape that made 33 files unrecoverable
#    (Coxeter/Core.agda 76 lines -> 3).  The write is inside a loop, so a per-file
#    `guard` would arm only the first file AND shell out to `git stash create` on
#    every iteration; arming once per run is both correct and cheap."
#
# "Arm once per run" is now structural: the snapshot rides the single entry-point intent
# statement, over the WHOLE walk rather than from the first hit file onward.  Leaving
# this as dead code would make `--unbound-snapshot` read FALSE-RED, since it keys on a
# `guard` call site being PRESENT, not on it being REACHABLE.



# ⟡paydown-unbuffered: python buffers stdout when redirected to a file, so a multi-hour
# fixpoint run shows NO progress until it exits — indistinguishable from a hang. Flush.
try:
    sys.stdout.reconfigure(line_buffering=True)
except Exception:
    pass

OPEN_HEAD = re.compile(r"^([ \t]*)open\s+import\s+(Substrate[\w.-]*)")
PUBLIC_TOK = re.compile(r"[ \t]*(?<![\w.-])public(?![\w.-])")
ERR = re.compile(r"^(?P<file>/[^\s:]+\.agda):[\d.\-]+: error: \[(?P<kind>\w+)\]", re.M)


def agda_files(prefix="Substrate"):
    """Delegates to `agda_lex.agda_files` — THE enumeration authority.

    ⚑ This name was defined FOUR times with FOUR DIFFERENT BODIES: two generators that
    sorted only WITHIN a directory (so the global order differed), one returning a sorted
    list WITH a `_build` guard, one sorting nothing.  A shared NAME is not a shared
    authority — it reads as reuse at every call site while silently disagreeing.
    41 of 59 enumeration sites lacked the `_build` filter; harmless only because
    `agda/_build/` holds zero `.agda` today, i.e. the agreement at 2764 is luck.
    """
    return _agda_files(prefix)

def strip(prefix="Substrate"):
    """Remove `public` from EVERY `open import Substrate… ` re-export. Returns the site count.

    ⛔ POLICY (user, 2026-07-27): a policy-driven ban on ALL re-exports. There is no wholesale-vs-
    narrowed distinction to make — a NARROWED re-export is still a CONDUIT (the consumer reaches
    structure through a module that does not define it), so the old `is_wholesale` gate is GONE.

    ⚑ The statement, not the line, is the unit. Agda accepts import directives in any order and
    across continuation lines, so `public` can sit on line 1 with `using (…)` on line 2, or after
    multi-line ARGUMENTS. A line-anchored regex saw only the first line and mis-classified both
    shapes — which is how ~158 narrowed re-exports were stripped by accident (the right outcome,
    the wrong reasoning) while every multi-line-argument re-export was silently skipped.

    `open import Agda.Primitive … public` is NOT ours: the catalog does not index compiler
    builtins, so there is no owner to bind at, and `Foundation/Level.agda` re-exporting `Level`
    IS the insulation boundary working. It is excluded by the `Substrate…` match above.
    `open <Rec> … public` (a record's fields / an applied module) needs the REDO-THE-APPLICATION
    transform rather than a keyword deletion, so it is out of this driver's scope — but it IS
    counted as debt by the public ratchet, which is where the policy is enforced."""
    n = files = 0
    for f in agda_files(prefix):
        lines = open(f).read().split("\n")
        out, i, hit = [], 0, 0
        while i < len(lines):
            m = OPEN_HEAD.match(lines[i])
            if not m:
                out.append(lines[i])
                i += 1
                continue
            ind, stmt, j = len(m.group(1)), [lines[i]], i + 1
            while j < len(lines) and lines[j].strip() and \
                    (len(lines[j]) - len(lines[j].lstrip())) > ind:
                stmt.append(lines[j])
                j += 1
            block = "\n".join(stmt)
            if PUBLIC_TOK.search(block):
                block = PUBLIC_TOK.sub("", block, count=1)
                block = "\n".join(l for l in block.split("\n") if l.strip())
                hit += 1
            out.extend(block.split("\n"))
            i = j
        new = "\n".join(out)
        if hit:
            # ⚑ THE WRITE-SITE `_snapshot_once(f)` IS GONE, NOT MOVED (Ⓐ49).  It sat
            # under `if hit:`, so a run that matched nothing armed nothing — and it
            # armed on the FIRST hit file only, leaving the rest of the walk covered
            # by a snapshot taken mid-run.  Entry-bound now, over the whole walk.
            open(f, "w").write(new)
            files += 1
            n += hit
    print(f"stripped {n} `open import … public` re-export site(s) across {files} file(s)")
    return n


def seed_all():
    """Union of the former re-export lists of every file we have modified vs HEAD."""
    r = subprocess.run(["git", "diff", "--name-only"], capture_output=True, text=True)
    pre = subprocess.run(["git", "rev-parse", "--show-prefix"],
                         capture_output=True, text=True).stdout.strip()
    seed = {}
    for path in r.stdout.split():
        if not path.endswith(".agda"):
            continue
        rel = path[len(pre):] if path.startswith(pre) else path
        try:
            seed.update(SF.seed_map(rel))
        except Exception:
            pass
    return seed


def _jobs_flag():
    """⟡agda-jobs — the `-j` width from the ONE authority (`gen_build_makefiles.AGDA_JOBS`,
    env `AGDA_JOBS` overrides). Falls back to bare `-j`, the pre-⟡agda-jobs behaviour, which
    is safe: membudget's semaphore still throttles by RAM. It degrades to more processes,
    never to more memory."""
    import importlib.util
    try:
        _root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        p = os.path.join(_root, "scripts", "gen_build_makefiles.py")
        s = importlib.util.spec_from_file_location("_gbm", p)
        m = importlib.util.module_from_spec(s)
        s.loader.exec_module(m)
        return m.jobs_flag()
    except Exception:
        return ["-j"]


def make_errors(jobs=""):
    """Run make -k; return (returncode, combined output).

    ⚑ An explicit `jobs` token still wins — a caller who names a width gets it. The DEFAULT is
    ⟡agda-jobs, never a bare `-j` and never a number typed here.
    """
    cmd = ["make", "-k"] + ([jobs] if jobs else _jobs_flag())
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def fix_pass(out, seed, dry=False):
    """Exhaust each distinct erroring FILE via `SF.fix` — single-sourced, NOT re-implemented.

    ⚑ This used to duplicate scope_fix's resolution inline and read a 4 KB CHUNK of the make
    log to pair a name with a file. Both were wrong: (a) the chunk pairing is the known
    CHUNK-SCANNING ARTIFACT (the kind comes from the error header, the name from whatever
    `Not in scope:` happens to fall inside the window), and (b) the duplicated resolver never
    saw the handlers added to `SF.fix` — most importantly `fix_barrel`, which handles the
    dominant class (a stripped barrel reports a WARNING, not `[NotInScope]`). Delegating gives
    the driver every handler for free and reads each file's OWN compiler output.
    """
    fixed, seen = 0, set()
    for m in ERR.finditer(out):
        f = m.group("file")
        if f in seen:
            continue
        seen.add(f)
        rel = os.path.relpath(f, os.getcwd())
        if not os.path.exists(rel):
            continue
        before = open(rel).read()
        SF.fix(rel, 20, dry)
        if not dry and open(rel).read() != before:
            fixed += 1
    return fixed


def fix_loop(max_passes=200, dry=False):
    for i in range(1, max_passes + 1):
        rc, out = make_errors()
        errs = len({m.group("file") for m in ERR.finditer(out)})
        if rc == 0 and errs == 0:
            print(f"✓ FIXED POINT: build green after {i - 1} fix pass(es)")
            return True
        seed = seed_all()
        print(f"pass {i}: {errs} erroring file(s), seed {len(seed)} name(s)")
        n = fix_pass(out, seed, dry)
        print(f"  → {n} fix(es) applied")
        if n == 0:
            print("✗ no progress — remaining errors need a human")
            return False
    print("✗ hit max_passes")
    return False


def recheck(dry=False):
    """Re-resolve every import THIS TOOL added, under the corrected shape-DB ranking.

    Run 1 ranked candidates by path proximity alone and wrote e.g. `Algebra.F2.+-assoc` into a
    ℕ context (→ `[UnequalTerms] ℕ !=< F₂`). Those imports are still in the tree; re-resolve each
    added `open import M using (n)` and repoint any whose owner the shape data disagrees with.
    """
    pre = subprocess.run(["git", "rev-parse", "--show-prefix"],
                         capture_output=True, text=True).stdout.strip()
    changed = subprocess.run(["git", "diff", "--name-only"],
                             capture_output=True, text=True).stdout.split()
    LINE = re.compile(r"^open import ([\w.]+) using \(([^)]*)\)\s*$", re.M)
    repointed = 0
    for path in changed:
        if not path.endswith(".agda"):
            continue
        rel = path[len(pre):] if path.startswith(pre) else path
        if not os.path.exists(rel):
            continue
        head = subprocess.run(["git", "show", f"HEAD:{path}"],
                              capture_output=True, text=True).stdout
        src = open(rel).read()
        for m in list(LINE.finditer(src)):
            line, mod, names = m.group(0), m.group(1), m.group(2)
            if line in head:                       # not ours — untouched
                continue
            for n in [x.strip() for x in names.split(";") if x.strip()]:
                owner, spell = SF.owner_by_catalog(n, rel)
                if owner and owner != mod:
                    print(f"    {rel}: {n}  {mod} → {owner}")
                    repointed += 1
                    if not dry:
                        src = open(rel).read()
                        src = src.replace(line, line.replace(mod, owner), 1)
                        open(rel, "w").write(src)
    print(f"recheck: {repointed} import(s) repointed by the shape data")
    return repointed


def status():
    r = subprocess.run(["python3", "../scripts/check_public_ratchet.py"],
                       capture_output=True, text=True)
    print(r.stdout.strip() or r.stderr.strip())


if __name__ == "__main__":
    # ⚑⚑ THE GUARD MOVED ABOVE MODE DISPATCH (Ⓐ44 ⟡move-guards-to-entry).  It used to sit
    # at :293 below, gated on `"--fix" or "--recheck"` — which is a MODE CARVE-OUT, and a
    # carve-out is the tool author deciding once which invocations are read-only and
    # having every caller inherit that silently.  Two things were wrong with it, and the
    # first is a live write:
    #   · `--strip` DISPATCHES ABOVE IT and WRITES (`_snapshot_once` at :145), so
    #     `paydown.py --strip` mutated the tree without stating any intent.
    #   · `--status` was exempted as read-only.  Under this contract that exemption is
    #     not the tool's to grant: `paydown.py --status --dry-run` is the caller saying
    #     "I am not asking you to write anything", and saying it is the deliverable.
    # ⚑⚑⚑ SNAPSHOT BOUND TO THE INTENT STATEMENT (Ⓐ49 ⟡split-8-unprotected), with
    # `paths=` so the UNTRACKED half is reached.  `snapshot()` covers TRACKED content
    # whole-worktree, but `_copy_untracked(paths)` is the ONLY mechanism that copies an
    # untracked file aside — and it iterates `paths`, so an empty tuple reaches none.
    # ⚑ THE POPULATION IS THE TREE WALK, NOT argv.  `strip()` iterates
    # `agda_files(prefix)`, so the honest `paths` is that same walk — resolved HERE so
    # the snapshot covers what the run can actually touch.  Passing argv instead would
    # name the PREFIX (a string like "Substrate"), not a file, and `_copy_untracked`
    # would silently skip it: `os.path.isfile` fails and the loop `continue`s, so the
    # protection would read as present and copy nothing.  A wrong `paths` is worse than
    # none, because the printed "snapshot taken" then covers a set nobody checked.
    import edit_snapshot as _es
    _pre = "Substrate"
    if "--strip" in sys.argv:
        _i = sys.argv.index("--strip")
        if len(sys.argv) > _i + 1 and not sys.argv[_i + 1].startswith("--"):
            _pre = sys.argv[_i + 1]
    _es.require_at_entry("paydown", paths=agda_files(_pre))
    if "--strip" in sys.argv:
        i = sys.argv.index("--strip")
        pre = sys.argv[i + 1] if len(sys.argv) > i + 1 and not sys.argv[i + 1].startswith("--") else "Substrate"
        strip(pre)
    # ⚑ THE MODE-SCOPED GUARD THAT WAS HERE IS NOW AT ENTRY (see the top of this block).
    # Its rationale is KEPT, because it was right about the DIRECTION and only wrong about
    # the SCOPE: `ratchet.mutating_argv`'s docstring records that a check reached only
    # after `apply` is true can never observe the case where apply was never chosen —
    # "the entire population the ratchet exists to measure."  Guarding `--fix`/`--recheck`
    # applied that reasoning one dispatch too late to cover `--strip`.
    if "--fix" in sys.argv:
        mx = int(sys.argv[sys.argv.index("--max") + 1]) if "--max" in sys.argv else 200
        ok = fix_loop(mx, "--dry-run" in sys.argv)
        sys.exit(0 if ok else 1)
    if "--recheck" in sys.argv:
        recheck("--dry-run" in sys.argv)
    if "--status" in sys.argv:
        status()
