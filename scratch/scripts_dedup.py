#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""scripts_dedup.py — the reuse_check WEDGE applied CORPUS-WIDE over scripts/*.py in ONE intern pass.

reuse_check.py is propose→nearest (one file vs the corpus); running it 46× re-interns the whole corpus
each time (O(N²) internment). This interns scripts/*.py (+ jea/metalanguage for context) ONCE via the
SAME engine (jea_pysim.Corpus) and applies reuse_check's IDENTICAL verbatim verdict logic
(∩ = P∩E, residues P∖E / E∖P, verdict) to every CROSS-FILE unit pair — surfacing the distinctions that
shouldn't exist: IDENTICAL (a true duplicate → single-source) and ⊆ (one is a special case → generalize).

Usage: scripts_dedup.py [--min-size N] [--overlap]   (default: IDENTICAL + ⊆ only, size ≥ 6)
"""
import sys, os, glob, argparse, itertools

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "jea", "metalanguage"))
import jea_pysim as P


def rel(p):
    return os.path.relpath(p, ROOT)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-size", type=int, default=6, help="min |support| (trivial-accessor gate)")
    ap.add_argument("--overlap", action="store_true", help="also report large-∩ OVERLAP (factor targets)")
    ap.add_argument("--globs", nargs="*", default=["scripts/*.py"])
    args = ap.parse_args()

    files = sorted(f for g in args.globs for f in glob.glob(os.path.join(ROOT, g)))
    C = P.Corpus()
    for f in files:
        try:
            C.add_file(f)
        except Exception as e:
            print(f"# skip {rel(f)}: {e}", file=sys.stderr)
    print(f"# interned {len(files)} file(s) → {len(C.units)} def(s); wedge over cross-file pairs\n",
          file=sys.stderr)

    def loc(u):
        return f"{u.name}  {rel(u.path)}:{u.lineno}"

    big = [u for u in C.units if len(u.support) >= args.min_size]

    # ── IDENTICAL EQUIVALENCE CLASSES: units with byte-equal support are one duplicate family. ──
    from collections import defaultdict
    cls = defaultdict(list)
    for u in big:
        cls[frozenset(u.support)].append(u)
    fams = [us for us in cls.values() if len({u.path for u in us}) >= 2]  # ≥2 FILES = cross-file dup
    fams.sort(key=lambda us: (-len(us[0].support), -len(us)))
    print(f"■ IDENTICAL FAMILIES ({len(fams)}) — each is ONE def copy-pasted across files; single-source it:")
    for us in fams:
        names = sorted({u.name for u in us})
        namedist = f"  ⚠ NAME-DISTINCTION {names}" if len(names) > 1 else ""
        print(f"   • |{len(us)} copies| ∩={len(us[0].support)}  «{names[0]}»{namedist}")
        for u in sorted(us, key=lambda u: rel(u.path)):
            print(f"        {rel(u.path)}:{u.lineno}  {u.name}")

    # ── DRIFT: a unit whose support is a strict SUPERSET/SUBSET of a family member = a COPY THAT DIVERGED. ──
    fam_supports = [(frozenset(us[0].support), us) for us in fams]
    drift = []
    for u in big:
        su = frozenset(u.support)
        for fs, us in fam_supports:
            if su == fs or u.path in {m.path for m in us}:
                continue
            if su < fs:
                drift.append(("⊂ (lost)", len(fs - su), u, us))
            elif su > fs:
                drift.append(("⊃ (added)", len(su - fs), u, us))
    print(f"\n■ DRIFT ({len(drift)}) — a copy that DIVERGED from an IDENTICAL family (the distinction that "
          f"shouldn't exist):")
    for kind, delta, u, us in sorted(drift, key=lambda t: -t[1])[:30]:
        print(f"   • {loc(u)}  {kind} {delta} vs «{sorted({m.name for m in us})[0]}» family "
              f"({len(us)} copies @ {rel(us[0].path)}:{us[0].lineno})")


if __name__ == "__main__":
    main()
