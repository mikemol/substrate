#!/usr/bin/env python3
"""set1_census_cores.py — census Set₁ from ELABORATED cores, not source text.
Each defmark carries {"unit","kind","sort","level"}; `level` is the universe the
definition INHABITS (codomain sort, Πs peeled). A Set₁ definition has level >= 1."""
import glob, sys, os, collections, re

# ⟡lift-shared-core-machinery — the shim-decode + core-root path logic (which this file and
# set1_locate_census + reuse_catalog each re-rolled, the dogfood's structural dup and the typehole-
# confirmed shim-decode shell) now live ONCE in jea_agdai; imported here. The shim-invocation
# invariants (cwd = core dir, LC_ALL UTF-8, decode-Nothing = undecodable) live in `decode_core`.
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "jea", "metalanguage"))
from jea_agdai import decode_core, substrate_core_root
SHIM = os.environ.get("AGDAI_SHIM")   # None ⇒ decode_core's default (the committed agdai_shim)
AGDA_ROOT = os.environ.get("AGDA_ROOT") or os.getcwd()

def cores(root):
    return sorted(glob.glob(os.path.join(root, "**", "*.agdai"), recursive=True))

def defmarks(core):
    d = decode_core(core, shim_bin=SHIM)
    return None if d is None else d["defmarks"]   # explicit None = undecodable, NOT empty

root = sys.argv[1] if len(sys.argv) > 1 else substrate_core_root(AGDA_ROOT)
cs = cores(root)
ok = undec = 0
by_level = collections.Counter(); by_kind = collections.Counter()
set1_defs = []
for c in cs:
    dm = defmarks(c)
    if dm is None:
        undec += 1; continue
    ok += 1
    for d in dm:
        lv = d.get("level")
        by_level[lv] += 1
        if isinstance(lv, int) and lv >= 1:
            set1_defs.append(d); by_kind[d["kind"]] += 1

print(f"  cores: {len(cs)}   decoded: {ok}   UNDECODABLE: {undec}")
if undec:
    print(f"  !! {undec} cores could not be decoded — the census is INCOMPLETE, not zero.")
print(f"  definitions seen: {sum(by_level.values())}")
print(f"  level distribution: {dict(sorted((k,v) for k,v in by_level.items() if k is not None))}"
      f"  (level=null: {by_level[None]})")
print(f"  Set₁-inhabiting (level>=1): {len(set1_defs)}")
print(f"  by kind: {dict(by_kind)}")
