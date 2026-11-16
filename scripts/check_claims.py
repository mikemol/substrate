#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""check_claims.py — a prose CLAIM about the tree is DEBT unless the tree agrees.

A comment or docstring that asserts a COUNT ("39 importers") or an EXPORT ("thin
re-export shim") is a proposition the tree can falsify. Nothing falsified them, so they
went stale — and a stale claim in a GATE does not merely misinform, it EXEMPTS:
check_public_ratchet.py grandfathered 16 baseline keys on "`Graded.agda` IS the public API
for 39 importers". Measured 2026-07-28: ONE importer. A sentence was the whole defence.

TWO PREDICATES, and only two. Both were chosen by running an over-firing census
(scratch/claim_census.py) over the whole tree and READING every hit, so each carries a
measured precision rather than an intuition:

  P1 SHIM  — a comment claims re-export/shim/"preserves the public interface" and the file
             contains NO `public`. MEASURED 16/16 true. Needs no subject resolution: the
             claim is about the file and the evidence is in the file. Cause is a single
             event — ⟡public-policy stripped `public` from ~695 sites tree-wide and left
             every barrel header describing its pre-strip self. A consumer reading "thin
             re-export shim over eight submodules" imports the module and gets nothing.

  P2 COUNT — a number adjacent to importers/consumers/users/call-sites, where the subject
             resolves: a module named in backticks in the same comment, else the enclosing
             .agda file. MEASURED 3/4 true; the one false positive was tokenisation ("5 call
             sites" pulled out of `M-3.5 call sites`), fixed by the (?<![\\w.-]) guard.
             ⚑ Runs over scripts/ too — the exempting instance lived in a gate docstring.

DELIBERATELY NOT PREDICATES (measured, not guessed):
  ZERO   ("no consumers")     — 0/3 true. Every hit named a DEF or a past deletion, not the
                                enclosing module: Word.agda:66 says "No consumer uses
                                to-list / from-list" in a module with 145 importers.
  ABSENT ("does not exist")   — ~0/11 useful. Nine of eleven are MATHEMATICS (Cantor's
                                diagonal at Lawvere.agda:79, "the feared minor-of-a-
                                permutation-matrix crux does NOT exist"), not tree claims.
Both would need def-granularity subject resolution to be worth anything.

⚑ A MEASUREMENT IS NEVER FLAGGED. A dated claim with a method ("MEASURED 2026-07-26: Mod
175→116") is evidence, and is the most valuable text in the tree — Graded/Mod.agda:12-15 is
the only record that `using`-narrowing is not a partial de-parameterization. A bare count is
a hypothesis. The MEASURED skip below is what separates them; do not remove it.

CENSUS = the SET of keys `<relpath>::<predicate>::<subject>` that the tree falsifies. Keys
carry NO line number, so reflowing a comment does not churn the baseline. DEBT: paydown-only.
A NEW false claim is REFUSED — fix the claim or fix the tree, never add an exemption.

Blocking gate. Exit 0 = clean, 1 = a new false claim appeared.
Usage: check_claims.py [--quiet] [--list]
"""

import os
import re
import sys
import collections

import ratchet
import os as _oe, sys as _se

_se.path.insert(
    0, _oe.path.join(_oe.path.dirname(_oe.path.dirname(_oe.path.abspath(__file__))), "scratch")
)
from agda_lex import agda_files as _agda_files

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
AGDA = os.path.join(ROOT, "agda")
SUBSTRATE = os.path.join(AGDA, "Substrate")
BASELINE = os.path.join(HERE, "claims_baseline.txt")

# A dated MEASUREMENT is evidence, not a hypothesis — never flag it.
MEASURED = re.compile(r"(?i)\bMEASURED\b|\(measured|\bCORRECTED \d{4}-\d{2}-\d{2}")

# P2: the (?<![\w.-]) guard stops "5 call sites" being pulled out of `M-3.5 call sites`.
COUNT = re.compile(
    r"(?i)(?<![\w.-])(\d+)\s+(?:direct\s+|real\s+|live\s+)?"
    r"(?:importers?|consumers?|users?|call[- ]sites?)\b"
)
COUNT_API = re.compile(r"(?i)public\s+API\s+for\s+(?:~\s*)?(?<![\w.-])(\d+)")
# P1
SHIM = re.compile(
    r"(?i)re-?export(?:s|ing)? shim|thin re-?export|thin shim|"
    r"preserves the public interface"
)
# subject named in backticks: `Substrate.Foo.Bar` or `Bar.agda`
SUBJ = re.compile(r"`(Substrate[\w.]+|[\w.]+\.agda)`")

# ⚑ `-` is a module-name character in EVERY position (V4-Coxeter, S4-Iso, S3-on-V4). With
# [\w.]* the capture stops at the hyphen, so `import Substrate.Groups.V4-Coxeter` is credited
# to `Substrate.Groups.V4` — measured: it inflated V4's importer count from 1 to 67. This is
# a recurring class in this repo (module-name capture, the import graph, the alias boundary);
# any new module-name regex must include the hyphen.
IMP = re.compile(r"^\s*(?:open\s+)?import\s+(Substrate[\w.-]*)")


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


def scanned_files():
    yield from agda_files()
    for fn in sorted(os.listdir(HERE)):
        if fn.endswith(".py"):
            yield os.path.join(HERE, fn)


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
                out.append((i, s))
                continue
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


def importer_index():
    """{module_relpath: {importing_file_relpath, …}} over the whole Agda tree."""
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


def resolve_subject(text, path):
    """The module a count claim is ABOUT: backticked name if present, else the enclosing
    .agda file. Returns a relpath under agda/, or None when unresolvable (a bare count in a
    .py file names no subject — we refuse to guess rather than flag it)."""
    m = SUBJ.search(text)
    if m:
        s = m.group(1)
        return (s.replace(".", "/") + ".agda") if s.startswith("Substrate") else s
    return os.path.relpath(path, AGDA) if path.endswith(".agda") else None


def has_public(path):
    try:
        for ln in open(path, errors="replace"):
            s = ln.strip()
            if s.startswith("--") or s.startswith("#"):
                continue
            if re.search(r"\bpublic\b", ln):
                return True
    except OSError:
        pass
    return False


def _match_subject(subj, idx):
    """Importer count for `subj`, tolerating a bare `Foo.agda` subject by unique basename."""
    if subj in idx:
        return len(idx[subj])
    if "/" not in subj:
        cands = [k for k in idx if os.path.basename(k) == subj]
        if len(cands) == 1:
            return len(idx[cands[0]])
        return None  # ambiguous or absent — refuse to guess
    return 0


def census():
    """{key: detail} for every claim the tree FALSIFIES."""
    idx = importer_index()
    out = {}
    for p in scanned_files():
        rel = os.path.relpath(p, ROOT)
        shim_hit = None
        for lineno, text in comment_lines(p):
            # ⚑ The MEASURED skip guards SHIM only — NOT counts. A dated importer count is
            # still mechanically checkable, so it stays checked forever; otherwise writing
            # "MEASURED: 35 importers" would mint a permanent exemption, which is the very
            # move this gate exists to forbid. (COUNT is narrow enough that no real
            # measurement collides with it: "33 demanded names", "Mod 175→116 MB" and
            # "16 public-ratchet keys" all fail its noun list.)
            if (
                SHIM.search(text)
                and shim_hit is None
                and p.endswith(".agda")
                and not MEASURED.search(text)
            ):
                shim_hit = lineno
            for rx in (COUNT, COUNT_API):
                m = rx.search(text)
                if not m:
                    continue
                subj = resolve_subject(text, p)
                if subj is None:
                    continue
                actual = _match_subject(subj, idx)
                if actual is None:
                    continue
                claimed = int(m.group(1))
                if claimed != actual:
                    out[f"{rel}::count::{subj}"] = (
                        f"{rel}:{lineno} claims {claimed}, tree says {actual}  [{subj}]"
                    )
                break
        if shim_hit is not None and not has_public(p):
            out[f"{rel}::shim::self"] = f"{rel}:{shim_hit} claims re-export, file has NO `public`"
    return out


def main():
    # ⚑ ROUTED THROUGH THE AUTHORITY (T17/T11).  `--dry-run` already worked —
    # `set_ratchet` reads it from argv — but a TYPO did not fail: `--queit` was
    # accepted and the gate ran verbose-but-passing (§7e).  `--dry-run` is NOT
    # listed: `ratchet.UNIVERSAL_FLAGS` declares it for every caller.
    if (rc := ratchet.check_argv(sys.argv, {"--quiet", "--list"}, "check_claims.py")) is not None:
        return rc
    quiet = "--quiet" in sys.argv
    found = census()

    # ⚑ THE HAND-ROLLED `--list` IS GONE — `render=` CARRIES WHAT MADE IT SPECIAL.
    # It printed `found[k]`, the claim TEXT, which `set_ratchet` cannot derive from a
    # key set — and I first read that as grounds to KEEP the copy.  Wrong: the text
    # was the only difference; the flag parse, the sort, the loop and the early
    # return were duplication (user: *"they should all be lifted to a common thing"*).
    # The renderer is total on keys not in `found` — a PAID-DOWN claim is absent by
    # construction, and `.get` falling back to the key is what keeps that branch alive.
    # ⚑ AND THE VERBOSE BLOCK WAS THE SAME COPY ONE LAYER OVER — MEASURED, it made
    # `--list` print all 14 claims TWICE.  `set_ratchet` already enumerates keys on
    # every branch that has something to say (list / paid / added) and now renders
    # them through `render`, so a gate printing its own census beforehand duplicates
    # the authority's output instead of extending it.
    return ratchet.set_ratchet(
        set(found),
        BASELINE,
        "claims",
        quiet,
        list_keys="--list" in sys.argv,
        render=lambda k: found.get(k, k),
        noun="stale claim(s) the tree falsifies",
        refuse_hint="A comment or docstring asserts something the tree contradicts. FIX THE "
        "CLAIM (state the measured value, or say what the file actually does) or "
        "FIX THE TREE. Do NOT add an exemption: a stale claim in a gate EXEMPTS "
        "debt rather than merely misinforming it. If the text records a dated "
        "MEASUREMENT, say so explicitly — measurements are never flagged.",
    )


if __name__ == "__main__":
    sys.exit(main())
