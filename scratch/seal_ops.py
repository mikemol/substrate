#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""⟡cap128-schedule-seal cascade — opaque round/final-round/nextRoundKey + unfolding pins.
Idempotent-ish (skips if already sealed). Prints each edit."""
import os, re, sys
A = "/home/mikemol/github/substrate/agda/Substrate/Algebra/F2/AES"

# ⚑ ONE ACT, AT MODULE TOP, BECAUSE THIS TOOL HAS NO OTHER ENTRY.  There is no
# `main` and no `__main__`: the edits below run as MODULE BODY, so they fire on
# IMPORT as readily as on invocation, and there is no decision point to put a
# gate at that is not this line.  `require_at_entry` here is therefore both the
# intent gate and the snapshot, ahead of every write — which is the property the
# `guard` inside `edit()` could not have (it ran per-edit, after the decision,
# and the SEVEN direct `open(p,"w")` writes below it were never armed at all).
# ⚑ `paths=` NAMES THE WHOLE AES TREE this rewrites, resolved eagerly: the files
# are fixed targets, so the set is knowable before any edit rather than
# discovered as it goes.
_ALL = ([f"{A}/Round.agda", f"{A}/KeySchedule.agda", f"{A}/KAT.agda",
         f"{A}/KAT/KeyPins.agda", f"{A}/KAT/RoundFin.agda"]
        + [f"{A}/KAT/Round{i}.agda" for i in range(1, 10)])
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import edit_snapshot as _es
_es.require_at_entry("seal_ops", paths=[p for p in _ALL if os.path.exists(p)])
if "--apply" not in sys.argv:
    print("seal_ops: WOULD seal round / final-round / nextRoundKey opaque and pin "
          "the KAT unfoldings.  (dry run — pass --apply)")
    raise SystemExit(0)


def indent(block, n=2):
    return "\n".join((" " * n + l if l.strip() else l) for l in block.split("\n"))


def opaque(block, unfold=None):
    h = "opaque\n" + (f"  unfolding {unfold}\n" if unfold else "")
    return h + indent(block)


def edit(path, old, new, tag):
    s = open(path).read()
    if new.split("\n")[0] in s and old not in s:
        print(f"  SKIP {tag} (already done)"); return
    assert old in s, f"OLD not found in {path} for {tag}"
    import edit_snapshot as _es
    _es.guard("seal_ops", [path])
    open(path, "w").write(s.replace(old, new, 1))
    print(f"  OK   {tag}")


# ── def-sites (opaque) ──
R = f"{A}/Round.agda"
edit(R,
     "round : State → State → State\nround k s = addKey k (MixColumns (ShiftRows (SubBytes s)))",
     opaque("round : State → State → State\nround k s = addKey k (MixColumns (ShiftRows (SubBytes s)))"),
     "Round.round opaque")
edit(R,
     "final-round : State → State → State\nfinal-round k s = addKey k (ShiftRows (SubBytes s))",
     opaque("final-round : State → State → State\nfinal-round k s = addKey k (ShiftRows (SubBytes s))"),
     "Round.final-round opaque")

KS = f"{A}/KeySchedule.agda"
nrk_old = (
    "nextRoundKey : Byte → State → State\n"
    "nextRoundKey rc (w0 ∷ w1 ∷ w2 ∷ w3 ∷ []) =\n"
    "  let t   = SubWord (RotWord w3) ⊕w (rc ∷ 𝟘b ∷ 𝟘b ∷ 𝟘b ∷ [])\n"
    "      nw0 = w0 ⊕w t\n"
    "      nw1 = w1 ⊕w nw0\n"
    "      nw2 = w2 ⊕w nw1\n"
    "      nw3 = w3 ⊕w nw2\n"
    "  in nw0 ∷ nw1 ∷ nw2 ∷ nw3 ∷ []")
edit(KS, nrk_old, opaque(nrk_old), "KeySchedule.nextRoundKey opaque")

# ── pins (unfolding) ──
for i in range(1, 10):
    p = f"{A}/KAT/Round{i}.agda"
    s = open(p).read()
    if "unfolding round" in s:
        print(f"  SKIP Round{i}"); continue
    m = re.search(rf"(?m)^r{i} : [^\n]*\nr{i} = refl", s)
    assert m, f"pin r{i} not found"
    open(p, "w").write(s[:m.start()] + opaque(m.group(0), "round") + s[m.end():])
    print(f"  OK   Round{i} unfolding round")

# KeyPins: wrap the whole KP1..KP10 tail block
KP = f"{A}/KAT/KeyPins.agda"
s = open(KP).read()
if "unfolding nextRoundKey" not in s:
    m = re.search(r"(?ms)^KP1 .*?refl\s*\Z", s)
    assert m, "KP block not found"
    open(KP, "w").write(s[:m.start()] + opaque(m.group(0).rstrip("\n"), "nextRoundKey") + "\n")
    print("  OK   KeyPins unfolding nextRoundKey")
else:
    print("  SKIP KeyPins")

# RoundFin
RF = f"{A}/KAT/RoundFin.agda"
s = open(RF).read()
if "unfolding final-round" not in s:
    m = re.search(r"(?m)^fin : [^\n]*\nfin = refl", s)
    assert m, "fin not found"
    open(RF, "w").write(s[:m.start()] + opaque(m.group(0), "final-round") + s[m.end():])
    print("  OK   RoundFin unfolding final-round")
else:
    print("  SKIP RoundFin")

# KAT.agda: wrap keysched-kat (in the middle) + add nextRoundKey to the import
KAT = f"{A}/KAT.agda"
s = open(KAT).read()
if "unfolding nextRoundKey" not in s:
    m = re.search(r"(?m)^keysched-kat : [^\n]*\nkeysched-kat = refl", s)
    assert m, "keysched-kat not found"
    s = s[:m.start()] + opaque(m.group(0), "nextRoundKey") + s[m.end():]
    s = s.replace("using (keyExpansion)", "using (keyExpansion; nextRoundKey)", 1)
    open(KAT, "w").write(s)
    print("  OK   KAT.keysched-kat unfolding nextRoundKey + import")
else:
    print("  SKIP KAT")

print("done.")
