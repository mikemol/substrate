#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""set1_sweep.py — ⟡held-family-sweep ENGINE. Enumerate every remaining Set₁ (level≥1) def from the
.agdai cores (the ratchet shim's {unit,level} data), CLASSIFY each by its collapse-clothes
(set1-is-grade-collapse in different clothes), and report per-class counts + targets + the dissolution
recipe. The standing sweep tool: re-run to watch the class buckets drain toward 0.

Classes (mechanical-first → semantic-last):
  M1 object-carrier  — the object TYPE is itself a held-family (`X : Set₁ = Set × Set`, a stored Set-tuple/Σ)
  M2 placeholder     — a `*-stated : Set`/`Set₁` obligation carrier (lower like descent-/commute-stated)
  M3 carrier-field   — a record/constructor fielding a Set/relation (parameterize)
  S1 data-family     — `<X>Gen/<X>Term/_∷_/lift` free-category term-algebra (ℕ-index = SEMANTIC decision)
  S1 legit-large     — presheaf/sheaf/allegory-power/charter records over an infinite object index
"""
import os, sys, subprocess, json, glob, re
from collections import Counter, defaultdict

ROOT = "/home/mikemol/github/substrate"
AGDA = os.path.join(ROOT, "agda")
BUILD = os.path.join(AGDA, "_build", "2.8.0", "agda")
SHIM = os.environ.get("AGDAI_SHIM", os.path.join(ROOT, "jea", "metalanguage", "agdai_shim"))
env = dict(os.environ, LC_ALL="C.UTF-8", LANG="C.UTF-8")


def classify(short, module):
    """bucket a Set₁ def by its NAME/MODULE clothes (the census showed these patterns are clean)."""
    s = short
    if re.search(r'(Gen|Term)$', s) or s in ("_∷_", "[]", "lift") or re.match(r'(_∷_|lift-|_\+\+)', s) \
       or s.startswith("_∷_-") or re.match(r'.*(Gen|Term)\.', s):
        return "S1 data-family (term-algebra)"
    if s.endswith("-stated") or s.endswith("-stated'"):
        return "M2 placeholder (*-stated)"
    if "ConjugationCoalgebra" in s or s.startswith("IsSimple") or s.startswith("¬witness"):
        return "M3 carrier-field (conjugation-coalgebra)"
    if s.startswith("mk") or s.endswith("Witness") or s.endswith("AlgebraClass"):
        return "M3 carrier-field (witness/mk-record)"
    if s in ("_†", "_⨾_", "idR", "P", "Φ", "BWedge") or s.startswith("Set-") or "Allegory" in module or "Power" in module:
        return "S1 legit-large (allegory/power)"
    if s.startswith("charter-") or s in ("reachable", "coverable", "persists-via") or "Charter" in module or "Distinction" in module:
        return "S1 legit-large (charter/shadow)"
    if s.endswith("Context") or s in ("Poly", "Markov", "MarkovCategory", "UPCategory", "MarkovCategory") or s.endswith("Category"):
        return "M1 object-carrier (or category record)"
    if s == "constructor" or s.endswith(".constructor"):
        return "· constructor (goes with its parent record/data)"
    if re.search(r'(Presheaf|Sheaf|Sieve|Cover|Topos|Yoneda|Omega|Coverage)', s + module):
        return "S1 legit-large (topos)"
    return "?? unclassified"


def main():
    cores = sorted(glob.glob(os.path.join(BUILD, "**", "*.agdai"), recursive=True))
    cls_ct = Counter()
    cls_mods = defaultdict(Counter)
    cls_ex = defaultdict(list)
    total = 0
    for c in cores:
        rel = os.path.relpath(c, AGDA)
        try:
            p = subprocess.run([SHIM, rel], cwd=AGDA, env=env, capture_output=True, text=True, timeout=180)
        except Exception:
            continue
        if "decode Nothing" in p.stderr:
            continue
        mod = rel[:-len(".agdai")].replace(os.sep, ".").replace("2.8.0.agda.", "")
        for l in p.stdout.splitlines():
            if not l.startswith('{"unit"'):
                continue
            try:
                d = json.loads(l)
            except Exception:
                continue
            if isinstance(d.get("level"), int) and d["level"] >= 1:
                total += 1
                short = d.get("unit", "?").rsplit(".", 1)[-1]
                k = classify(short, mod)
                cls_ct[k] += 1
                cls_mods[k][mod] += 1
                if len(cls_ex[k]) < 6:
                    cls_ex[k].append(f"{mod.split('.')[-1]}.{short}")
    print(f"# ⟡held-family-sweep — {total} Set₁ held-family defs by CLASS\n")
    for k, n in cls_ct.most_common():
        topmods = ", ".join(f"{m.split('.')[-2] if '.' in m else m}:{c}" for m, c in cls_mods[k].most_common(5))
        print(f"{n:4}  {k}")
        print(f"        top modules: {topmods}")
        print(f"        e.g.: {cls_ex[k][:5]}\n")


if __name__ == "__main__":
    main()
