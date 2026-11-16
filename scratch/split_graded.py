#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""⟡graded-shard — split Algebra/Polynomial/Graded.agda's law-bag into per-section modules.

The elaboration peak is per-MODULE (measured: floor 76MB + ~5MB per law-def, monolithic 333MB),
and the parameterized-module re-application is free (measured: split 75+96 vs monolithic 99). So
shard the laws at the author's OWN section boundaries (`-- N. …` comments), chaining each module
onto the previous via `open Prev.Over … public`, and make Graded.agda the re-export tip — the
public API is unchanged, so none of the 39 importers move.
"""
import os
import re
import sys

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
        edit_snapshot.guard('split_graded', [path])
    except Exception as e:
        print(f"   \u26a0 snapshot unavailable ({e}) \u2014 recover via git if needed")



ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
G = os.path.join(ROOT, "agda", "Substrate", "Algebra", "Polynomial", "Graded.agda")
OUT = os.path.join(ROOT, "agda", "Substrate", "Algebra", "Polynomial", "Graded")
NS = "Substrate.Algebra.Polynomial.Graded"

# section name per author-numbered block (2..10 become law modules; 1 is Defs)
NAMES = {1: "Defs", 2: "Nth", 3: "Conv", 4: "Distrib", 5: "Scalar",
         6: "Basis", 7: "Linear", 8: "Monomial", 9: "Comm", 10: "Assoc"}

# MEASURED rebalance: at one-module-per-section, §8 Monomial hit 130MB and §10 Assoc 201MB
# (all others ≤123). Sub-split those two at their own internal definition boundaries — the
# 1-based source lines where the sub-module starts — so every link lands under the 128 cap.
EXTRA_CUTS = {8: [368],          # x-power/convCoeff-basis-* | nth-xpower-basis-*/symm/comm
              10: [457, 510]}    # convCoeff-basis-right+nth-xpower-off | mono-assoc | *P-assoc
SUBNAMES = {(8, 1): "MonomialDelta", (10, 1): "AssocMono", (10, 2): "AssocMain"}

APPLY = ("_+_ _*_ 𝟘 𝟙 +-assoc +-comm +-identityˡ +-identityʳ "
         "*-assoc *-comm *-identityˡ *-distribˡ *-absorbˡ *-absorbʳ")


def main():
    # ⚑ ONE ACT: state the intent AND snapshot, at the ONLY entry this tool has.
    # ⚑⚑ AND THIS TOOL HAD NO DECISION AT ALL.  It takes no `--apply` and no
    # `--dry-run`: every invocation wrote `Graded.agda` plus one leaf per part.
    # `_snapshot_once` covered the LEAF writes only — the tip write at the bottom
    # of this function was unarmed, and it is the destructive one (it REPLACES the
    # monolith with a re-export stub). So the fix is not a placement move; it is
    # supplying the decision the contract needs, and putting the snapshot on it.
    # ⚑ `paths=[G]` IS THE MONOLITH, deliberately: the leaves are files this run
    # CREATES (a snapshot of a not-yet-existing path recovers nothing), while `G`
    # is the one file whose prior content a bad run destroys.
    import sys as _s2, os as _o2
    _s2.path.insert(0, _o2.path.dirname(_o2.path.abspath(__file__)))
    import edit_snapshot as _es
    _es.require_at_entry("split_graded", paths=[G])
    if "--apply" not in sys.argv:
        print(f"split_graded: WOULD split {os.path.relpath(G, ROOT)} into "
              f"Defs + Laws.* and replace it with a re-export tip.  (dry run)")
        return 0
    src = open(G, encoding="utf-8").read().splitlines()
    imports = "\n".join(src[20:30])                 # lines 21..30 (incl. the Base import)
    telescope = "\n".join(src[34:46])               # 'module Over {A} (…)' header
    privvar = "  private variable n m k : ℕ"

    # section starts from the author's own `-- N.` comments
    starts = {}
    for i, ln in enumerate(src):
        m = re.match(r"^  -- (\d+)\.", ln)
        if m:
            starts[int(m.group(1))] = i             # 0-based index of the comment line
    order = sorted(starts)
    # flatten sections (plus any measured sub-cuts) into an ordered part list
    parts = []                                    # (name, lo, hi) 0-based half-open
    for j, s in enumerate(order):
        lo = starts[s]
        hi = starts[order[j + 1]] if j + 1 < len(order) else len(src)
        cuts = [lo] + [c - 1 for c in EXTRA_CUTS.get(s, [])] + [hi]
        for i in range(len(cuts) - 1):
            nm = NAMES[s] if i == 0 else SUBNAMES[(s, i)]
            parts.append((nm, cuts[i], cuts[i + 1]))

    MOD = {}
    for i, (nm, _, _) in enumerate(parts):
        MOD[i] = f"{NS}.Defs" if i == 0 else f"{NS}.Laws.{nm}"

    os.makedirs(os.path.join(OUT, "Laws"), exist_ok=True)
    written = []
    for idx, (nm, lo, hi) in enumerate(parts):
        s = idx                                   # chain position
        body = "\n".join(src[lo:hi]).rstrip()
        head = [f"{{-# OPTIONS --safe --without-K #-}}",
                f"-- ⟡graded-shard: part {idx} ({nm}) of the graded-polynomial development, split out",
                f"-- so each module's elaboration peak stays under the 128MB cap. Re-exported by",
                f"-- `Substrate.Algebra.Polynomial.Graded` — the public API is unchanged.",
                f"module {MOD[idx]} where",
                imports]
        if idx == 0:
            # §1 already carries `private variable` + the Base open, verbatim from the original
            head += [telescope, "  where", "\n".join(src[47:50])]
        else:
            head += [f"import {MOD[idx - 1]} as Prev",
                     telescope, "  where", privvar,
                     f"  open Prev.Over {APPLY} public"]
        path = (os.path.join(OUT, "Defs.agda") if idx == 0
                else os.path.join(OUT, "Laws", nm + ".agda"))
        _snapshot_once(path)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write("\n".join(head) + "\n" + body + "\n")
        written.append((idx, nm, hi - lo, path))

    # Graded.agda becomes the re-export tip (same module name, same Over telescope, same API).
    TIP = MOD[len(parts) - 1]
    tip = [f"{{-# OPTIONS --safe --without-K #-}}",
           "-" * 72,
           "-- Substrate.Algebra.Polynomial.Graded",
           "--",
           "-- R[y], the graded polynomial ring over an arbitrary COMMUTATIVE RING. ⟡graded-shard:",
           "-- the development is SPLIT across Graded.Defs + Graded.Laws.* (one module per section),",
           "-- because the Agda elaboration peak is per-MODULE and the monolith cost 333MB — over the",
           "-- 128MB cap (⟡cap-ratchet). Each part chains onto the previous via `open … public`, and",
           "-- this module is the re-export TIP: `Graded.Over` exposes exactly what it always did, so",
           "-- every consumer (FromCommRing → Mod → Quotient → Div, and ~39 direct importers) is",
           "-- unchanged. The parameterized-module re-application is free (measured).",
           "-" * 72,
           "",
           f"module {NS} where",
           "",
           imports,
           f"import {TIP} as Parts",
           "",
           telescope,
           "  where",
           privvar,
           f"  open Parts.Over {APPLY} public",
           ""]
    with open(G, "w", encoding="utf-8") as fh:
        fh.write("\n".join(tip))

    for s, nm, n, p in written:
        print(f"  §{s:<2} {nm:<9} {n:>4} lines  →  {os.path.relpath(p, ROOT)}")
    print(f"  tip  Graded.agda  (re-export of {TIP})")


if __name__ == "__main__":
    sys.exit(main())
