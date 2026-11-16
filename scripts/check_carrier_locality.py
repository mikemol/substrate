#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""check_carrier_locality.py — canonical operators live in dedicated, carrier-local files.

POLICY (structural; prevents fork-by-reimplementation, e.g. the Q/Z `_+ℤ_` fork):
  A canonical ENDO operator — a mixfix name `_⊕_` whose type is `T → T → T`
  (or `T → T`) over a GLOBALLY-UNIQUE carrier T (a `data`/`record` declared
  exactly once in the tree) — must obey two rules:

    (1) LOCALITY  — it is defined in T's home: the file declaring T, or a file
                    under T's home directory subtree (e.g. an ℤ operator lives
                    under Algebra/Z/, never under Algebra/Q/).

    (2) DEDICATION — a file may host operators over a carrier IT DECLARES (the
                    `data ℕ` + `_+_`/`_*_` home file, named for the carrier).
                    But a file aggregating ≥2 operators over FOREIGN carriers
                    (declared elsewhere) is a generic bucket — the place forks
                    hide, where the file name no longer identifies what is
                    canonical (the old Arithmetic.agda). Those split one-per-file.

  Together these make the home of a canonical operator unambiguous and
  name-identified, so re-declaring it elsewhere is a hard error — the only
  option is to IMPORT it. Bucket files become re-export barrels.

  Uniqueness-gated: carriers whose NAME is reused locally (e.g. several modules
  each declare their own `Word`) are ambiguous and skipped — two
  `_·_ : Word → Word → Word` in different files are usually different `Word`s,
  not a fork. We judge only carriers with a single global declaration.

Blocking gate. Exit 0 = clean, 1 = offenders. Usage: check_carrier_locality.py [--quiet]
"""

import os
import re
import sys

import ratchet
import _agdatext  # noqa: E402 (THE comment authority)
import os as _oe, sys as _se

_se.path.insert(
    0, _oe.path.join(_oe.path.dirname(_oe.path.dirname(_oe.path.abspath(__file__))), "scratch")
)
from agda_lex import agda_files as _agda_files

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "agda", "Substrate")

# The sanctioned-exemption RATCHET baseline (mirrors set1_ratchet_cores.py).
# Holds the sorted set of LIVE exemption keys ("<relpath>::<op>") that ALLOW
# currently sanctions AND that correspond to a real carrier-locality violation
# in the tree. The exemption set is DEBT: it may only be PAID DOWN (an operator
# homed → its violation disappears → its key drops), never grown. A NEW live
# exemption is refused (home the op / import it, don't add to ALLOW); a paydown
# auto-lowers + rewrites this baseline. A frozen ALLOW list is the anti-pattern
# this replaces (see scratch/carrier_locality_policy.md + the set1 ratchet).
BASELINE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "carrier_locality_baseline.txt")

# Sanctioned exceptions — "<relpath>::<op>", documented in
# scratch/carrier_locality_policy.md. These are pre-existing, cross-subsystem,
# and NOT forks (derived ops in a layered location; identity aliases; ops over
# a local type-synonym carrier). The gate blocks any NEW violation.
ALLOW = {
    # Derived ℕ arithmetic (mod/div) deliberately layered in Algebra/Nat/,
    # not re-implementations of a Foundation/Nat primitive.
    "agda/Substrate/Algebra/Nat/Mod.agda::_mod-suc_",
    "agda/Substrate/Algebra/Nat/DivMod/DivSuc.agda::_div-suc_",
    # `_·_` over a LOCAL `Word` type-synonym (Zn-Word × F-Word), distinct from
    # the Coxeter `Word`; and the canonical Coxeter `_·_` (= normalize ∘ ++),
    # historically in Core/Operations rather than under Word/.
    "agda/Substrate/Groups/Zn-x-FreeCyclic-PhaseProjection.agda::_·_",
    "agda/Substrate/Groups/Coxeter/Core/Operations.agda::_·_",
    # `_ℤ : ℤ → ℤ`, `n ℤ = n` — a local readability identity alias, not arithmetic.
    "agda/Substrate/Algebra/GL3F2/Characters.agda::_ℤ",
    # The canonical Klein-four `_·_` over V₄: `data V₄` lives in Groups/V4/Bijection.agda
    # and its operation historically in the sibling Groups/V4/Operations.agda (the
    # substrate's carrier/op/axioms/bundle split for V₄) — NOT under Bijection/. Exactly
    # the grandfathered Coxeter `_·_` pattern above. Surfaced once Ⓒ.v4 unified the
    # scattered local `data V₄` copies onto this one, making V₄ a globally-unique carrier.
    "agda/Substrate/Groups/V4/Operations.agda::_·_",
    # `_+V₄_` over a LOCAL `V₄ = Bool × Bool` type-synonym (the F₂² additive form of the
    # affine V₄ subgroup) — name-conflated with the canonical `data V₄`, not the same
    # carrier and not a fork of its op (the type-synonym-carrier exemption).
    "agda/Substrate/Cocycles/V4Signature/Codeword/ReservedToBivectorAffine/V4.agda::_+V₄_",
}


def strip_comments(s):
    """Delegates to `_agdatext.strip` -> `agda_lex.mask_comments`, the ONE authority.

    ⚑ THE DOCUMENTED FIX NEVER REACHED THE DOCUMENTED VICTIM.  `_agdatext.py` names
    THIS gate as the module broken by the weaker stripper, and its `strip` was
    repointed at the nesting-aware masker — but this file kept its own inline copy
    and never imported it.  Both bugs were live here:
      * `\\{-.*?-\\}` is NON-GREEDY, so it stops at the FIRST `-}`.  Agda block
        comments NEST: `{- x {- y -} z -}` left `z -}` as live text, and this gate
        then censused commented-out code as real declarations.
      * `--[^\\n]*` eats `-->`, which Agda's lexer reads as a NAME.
    This gate is a PRE-COMMIT blocker whose census feeds a paydown-only ratchet, so
    a mis-parse here launders itself into a baseline that can never be un-banked.
    `check_sumtype_ratchet` and `check_public_ratchet` import this function, so all
    three were parsing on the broken copy.
    """
    return _agdatext.strip(s)


# ⚑ INDENT-AWARE, matching `agda_defs.py:30`.  This was COLUMN-0 ANCHORED, so a
# `data`/`record` head INDENTED inside a parameterized `module _ (…) where` — the
# ⟡set1-paydown idiom — was invisible.  `agda_defs` fixed exactly this bug (its ⚑ at
# :24-29 records the measured import-drop it caused) and THIS gate never learned; the
# fix propagated along the "same code" axis and these two were not on it.
#
# MEASURED before converting: 142 type names (20.6% of 690) were invisible here, and
# the consequences were not cosmetic —
#   * `check_sumtype_ratchet` imports this DECL, and its whole purpose is refusing NEW
#     duplicate declarations.  It saw 25 duplicated names where the truth is 32, so a
#     new copy of `DivStr`, `GradedDivStr`, `GradedWedge`, `Trace`, `Wit`, `_≈L_` or
#     `_≈_` passed the gate.  `DivStr`/`Trace` are declared in BOTH `S5/S5EEA.agda` and
#     `Algebra/Wedge.agda` — the fork class the gate exists to prevent.
#   * `judge()` filters carriers on "declared in exactly one file", and `scan()`'s own
#     docstring warns that a subset scan "would call every carrier unique".  The col-0
#     blind spot produced precisely that failure GLOBALLY: 5 carriers (`DivStr`,
#     `Trace`, `Wit`, `_≈L_`, `_≈_`) were judged unique when they are not, and locality
#     was then enforced against a home that is not unique.
#
# ⚑ The name capture also drops `({` so a parameterized head (`data F (n : ℕ) where`)
# yields `F`, not `F(n`.  Applied per line via `.match()`, as before — not `re.M`.
DECL = re.compile(r"^\s*(?:data|record)\s+([^\s({]+)")
SIG = re.compile(r"^(\S+)\s*:\s*(.+?)\s*$")


def agda_files():
    """Delegates to `agda_lex.agda_files` — THE enumeration authority.

    ⚑ This name was defined FOUR times with FOUR DIFFERENT BODIES: two generators that
    sorted only WITHIN a directory (so the global order differed), one returning a sorted
    list WITH a `_build` guard, one sorting nothing.  A shared NAME is not a shared
    authority — it reads as reuse at every call site while silently disagreeing.
    41 of 59 enumeration sites lacked the `_build` filter; harmless only because
    `agda/_build/` holds zero `.agda` today, i.e. the agreement at 2764 is luck.
    """
    return _agda_files(SRC)


def split_top_arrows(t):
    parts, depth, cur = [], 0, ""
    for c in t:
        if c in "([{":
            depth += 1
            cur += c
        elif c in ")]}":
            depth -= 1
            cur += c
        elif c == "→" and depth == 0:
            parts.append(cur.strip())
            cur = ""
        else:
            cur += c
    parts.append(cur.strip())
    return parts


def carrier_of(t):
    """Carrier T if the type is endo `T → T → T` / `T → T`, else None."""
    prev = None
    while t != prev:  # strip leading implicit binders
        prev = t
        t = t.strip()
        if t.startswith("∀"):
            t = t[1:].strip()
        m = re.match(r"\{[^}]*\}\s*→(.*)$", t, flags=re.S)
        if m:
            t = m.group(1)
    parts = split_top_arrows(t)
    if len(parts) in (2, 3) and len(set(parts)) == 1 and parts[0]:
        return parts[0].split()[0]
    return None


def scan(paths=None):
    """(carrier_decls, opsigs) over `paths` (default: the whole tree).

    Carved out of main() so a pre-flight can reuse the exact extraction rather
    than re-implement the DECL/SIG regexes — a second implementation is how the
    gate and the pipeline drift.  Body is byte-for-byte main()'s former loop.

    ⚑ `judge` needs a WHOLE-TREE carrier_decls: its `unique` filter (a carrier
    declared in exactly one file) is a global property, so scanning a subset and
    judging it would call every carrier unique.  Subset scans are for collecting
    a pending-edit overlay, never for judging alone.
    """
    carrier_decls = {}  # carrier -> set of decl files
    opsigs = []  # (op, carrier, file)
    for path in agda_files() if paths is None else paths:
        with open(path, encoding="utf-8") as fh:
            src = strip_comments(fh.read())
        for line in src.splitlines():
            d = DECL.match(line)
            if d:
                carrier_decls.setdefault(d.group(1), set()).add(path)
            s = SIG.match(line)
            if s and "_" in s.group(1):
                T = carrier_of(s.group(2))
                if T is not None:
                    opsigs.append((s.group(1), T, path))
    return carrier_decls, opsigs


def judge(carrier_decls, opsigs):
    """(unique, canon, locality, bucket, live_exempt) — the verdict, no printing.

    Body is byte-for-byte main()'s former judgement block.
    """
    unique = {c: next(iter(fs)) for c, fs in carrier_decls.items() if len(fs) == 1}

    # canonical endo operators over unique carriers
    canon = [(op, T, path) for op, T, path in opsigs if T in unique]

    locality = []  # (op, T, relpath)
    per_file = {}  # file -> [(op, T)]
    live_exempt = set()  # ALLOW keys hit by a real violation
    for op, T, path in canon:
        rel = os.path.relpath(path, ROOT)
        per_file.setdefault(path, []).append((op, T))
        home_file = unique[T]
        home_dir = home_file[:-5]
        ok = (path == home_file) or path.startswith(home_dir + os.sep)
        if not ok:
            key = f"{rel}::{op}"
            if key in ALLOW:
                live_exempt.add(key)  # a sanctioned locality exemption, live
            else:
                locality.append((op, T, rel))

    bucket = []  # (relpath, [ops])
    for path, ops in per_file.items():
        rel = os.path.relpath(path, ROOT)
        # exempt operators over a carrier this very file DECLARES (the carrier's
        # named home), and ALLOW-grandfathered ops.
        foreign_all = [(op, T) for op, T in ops if path != unique[T]]
        foreign = [(op, T) for op, T in foreign_all if f"{rel}::{op}" not in ALLOW]
        for op, T in foreign_all:  # sanctioned bucket exemptions, live
            key = f"{rel}::{op}"
            if key in ALLOW:
                live_exempt.add(key)
        if len(foreign) >= 2:
            bucket.append((rel, foreign))

    return unique, canon, locality, bucket, live_exempt


def main():
    # ⚑ ROUTED THROUGH THE AUTHORITY (T17/T11).  `--dry-run` already worked —
    # `set_ratchet` reads it from argv — but a TYPO did not fail: `--queit` was
    # accepted and the gate ran verbose-but-passing (§7e).  `--dry-run` is NOT
    # listed: `ratchet.UNIVERSAL_FLAGS` declares it for every caller.
    if (
        rc := ratchet.check_argv(sys.argv, {"--quiet", "--list"}, "check_carrier_locality.py")
    ) is not None:
        return rc
    quiet = "--quiet" in sys.argv
    carrier_decls, opsigs = scan()
    unique, canon, locality, bucket, live_exempt = judge(carrier_decls, opsigs)

    rc = 0
    if locality or bucket:
        if locality:
            print(
                "carrier-locality: %d operator(s) defined outside their carrier's home:"
                % len(locality)
            )
            for op, T, rel in sorted(locality):
                home = os.path.relpath(unique[T], ROOT)[:-5]
                print(f"    {op}  (carrier {T}) in {rel}")
                print(f"                 → belongs under {home}/ ; import it instead.")
        if bucket:
            print(
                "carrier-locality: %d bucket file(s) defining >1 canonical operator "
                "(split one-per-file):" % len(bucket)
            )
            for rel, ops in sorted(bucket):
                print(f"    {rel}: {', '.join(op for op, _ in ops)}")
        rc = 1
    elif not quiet:
        print(
            "carrier-locality: clean (%d unique carriers, %d canonical operators, "
            "%d grandfathered)." % (len(unique), len(canon), len(ALLOW))
        )

    # The sanctioned-exemption RATCHET: the live-exemption SET is DEBT, paydown-only
    # (shared scripts/ratchet.py — the same set-ratchet as check_sumtype_ratchet.py).
    return (
        ratchet.set_ratchet(
            live_exempt,
            BASELINE,
            "carrier-locality-ratchet",
            quiet,
            list_keys="--list" in sys.argv,
            noun="sanctioned exemption(s)",
            refuse_hint="Home the operator under its carrier's directory (import it) — "
            "do NOT add to ALLOW.",
        )
        or rc
    )


if __name__ == "__main__":
    sys.exit(main())
