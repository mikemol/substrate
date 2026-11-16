#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Generate the FromCommRing PREFIX SLICES — the split along the BARREL axis.

⟡cap64-fcr-split.  `Graded.agda` is a pure barrel (`split_param_module.py` reports
0 units): sixteen `open Pn.Over <14 args> public` lines, P0=Defs … P15=Laws.AssocMain,
zero definitions.  `FromCommRing.agda` re-exports that barrel `public`, so EVERY
consumer that wants `_*P_`/`nth`/`Poly` (all in P0) pays for all sixteen parts.

⚑ WHY NOT THE DEF-AXIS SPLIT.  `split_param_module.py FromCommRing.agda` reports 17
units (one per adapter def) and the last one's `sibs:` list is ALL SIXTEEN others —
the 14 flat ops are a COHESIVE TELESCOPE (a consumer applying `Pn.Over` supplies all
14 at once, so it would open 14 leaves instead of 1: N leaves ≈ N× the shared parents,
the ⟡cap-residue law).  The split that pays is along the BARREL's 16 lines.

THE SHAPE.  `FromCommRing.agda` keeps the adapter and DROPS the barrel; each slice is

    module Over {A} (CR) where
      open …FromCommRing.Over CR public          -- the 14 flat ops, once
      open …Defs.Over <14 args> public           -- P0
      …                                          -- up to Pn

so a consumer binds at its MINIMAL prefix (the Laws links bind their ancestors
NON-publicly — ⟡graded-laws-noreexport — so a prefix, not a single part, is the unit).

⚑ BAN-RATCHET DISCIPLINE: every import here is BARE (no `using`/`as`) and every use is
FULLY QUALIFIED, so the 16 new files mint ZERO ban keys.  Regenerating the 5 pre-existing
hand-written slices in this form REMOVES their `as G0…G6` keys (a paydown).

USAGE: gen_fcr_slices.py            (dry run)
       gen_fcr_slices.py --apply
"""
import os, sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "agda")
PKG = "Substrate.Algebra.Polynomial.Graded"
DIR = os.path.join(ROOT, PKG.replace(".", "/"), "FromCommRing")

# P0..P15 in the barrel's own order (Graded.agda:29-44).
PARTS = [
    ("Defs",          PKG + ".Defs"),
    ("Nth",           PKG + ".Laws.Nth"),
    ("Conv",          PKG + ".Laws.Conv"),
    ("Distrib",       PKG + ".Laws.Distrib"),
    ("Scalar",        PKG + ".Laws.Scalar"),
    ("Basis",         PKG + ".Laws.Basis"),
    ("Linear",        PKG + ".Laws.Linear"),
    ("Monomial",      PKG + ".Laws.Monomial"),
    ("MonomialDelta", PKG + ".Laws.MonomialDelta"),
    ("Comm",          PKG + ".Laws.Comm"),
    ("Assoc",         PKG + ".Laws.Assoc"),
    ("AssocMono",     PKG + ".Laws.AssocMono"),
    ("AssocLinearP",  PKG + ".Laws.AssocLinearP"),
    ("AssocLinearQ",  PKG + ".Laws.AssocLinearQ"),
    ("AssocLinearR",  PKG + ".Laws.AssocLinearR"),
    ("AssocMain",     PKG + ".Laws.AssocMain"),
]

CR_MOD = "Substrate.Algebra.CommutativeRing"
FCR = PKG + ".FromCommRing"
ARGS = ("_+_ _*_ 𝟘 𝟙 +-assoc +-comm +-identityˡ +-identityʳ "
        "*-assoc *-comm *-identityˡ *-distribˡ *-absorbˡ *-absorbʳ")


def slice_text(name, upto):
    parts = PARTS[:upto + 1]
    imports = [f"import {CR_MOD}", f"import {FCR}"] + [f"import {m}" for _, m in parts]
    opens = [f"  open {m}.Over {ARGS} public" for _, m in parts]
    top = PARTS[upto][0]
    return "\n".join([
        "{-# OPTIONS --safe --without-K #-}",
        "-" * 72,
        f"-- {FCR}.{name}",
        "--",
        f"-- ⟡cap64-fcr-split: the CommutativeRing→flat-ops adapter re-exported with the",
        f"-- Graded parts P0..P{upto} ONLY (top part: Laws.{top}).  A consumer binds at its",
        "-- MINIMAL prefix instead of the retired `Graded` barrel's sixteen parts.",
        "--",
        "-- ⚑ Every import is BARE and every reference fully qualified: these files mint",
        "-- ZERO ban-ratchet keys (no `using`, no `as`).",
        "-" * 72,
        "",
        f"module {FCR}.{name} where",
        "",
    ] + imports + [
        "",
        f"module Over {{A : Set}} (CR : {CR_MOD}.CommutativeRing A) where",
        f"  open {FCR}.Over CR public",
        "",
    ] + opens + [""])


def main():
    apply = "--apply" in sys.argv
    for i, (name, _) in enumerate(PARTS):
        path = os.path.join(DIR, name + ".agda")
        txt = slice_text(name, i)
        state = "overwrite" if os.path.exists(path) else "new"
        print(f"{state:9} {name}.agda  (P0..P{i})")
        if apply:
            open(path, "w", encoding="utf-8").write(txt)
    if not apply:
        print("(dry run — pass --apply to write)")


if __name__ == "__main__":
    main()
