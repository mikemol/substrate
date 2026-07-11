#!/usr/bin/env python3
"""set1_census_cores.py — census Set₁ from ELABORATED cores, not source text.
Each defmark carries {"unit","kind","sort","level"}; `level` is the universe the
definition INHABITS (codomain sort, Πs peeled). A Set₁ definition has level >= 1."""
import subprocess, json, glob, sys, os, collections, re

# The Agda-2.8.0 .agdai decoder (emits per-definition defmarks with sort/level). The old
# `/tmp/agdai263s` was a stopgap for a pre-2.8.0 environment; the real tool is the committed
# `jea/metalanguage/agdai_shim` (same one set1_ratchet_cores.py uses via AGDAI_SHIM).
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHIM = os.environ.get("AGDAI_SHIM", os.path.join(_ROOT, "jea", "metalanguage", "agdai_shim"))
# The shim's decodeInterface resolves the interface's recorded include paths against
# CWD. Cores built with `-i .` from the agda root only decode when CWD is that root.
# Two invariants, both learned the hard way:
#  (a) CWD must be the agda include root — decodeInterface resolves the interface's
#      recorded include paths against CWD; elsewhere it reports "decode Nothing".
#  (b) LC_ALL must be UTF-8 — the shim prints qnames like `_≈_`; under C locale it
#      dies with "commitBuffer: cannot encode character", AFTER a successful decode.
# Neither failure means a stale core. The error text lies in both cases.
AGDA_ROOT = os.environ.get("AGDA_ROOT") or os.getcwd()

def cores(root):
    return sorted(glob.glob(os.path.join(root, "**", "*.agdai"), recursive=True))

def defmarks(core):
    env = dict(os.environ, LC_ALL="C.UTF-8", LANG="C.UTF-8")
    p = subprocess.run([SHIM, os.path.relpath(core, AGDA_ROOT)],
                       cwd=AGDA_ROOT, env=env, capture_output=True, text=True, timeout=120)
    if "decode Nothing" in p.stderr:
        return None                       # explicit: undecodable, NOT empty
    out = []
    for l in p.stdout.splitlines():
        if l.startswith('{"unit"'):
            try: out.append(json.loads(l))
            except json.JSONDecodeError: pass
    return out

def _default_core_root():
    # Agda-2.8.0 puts cores under _build/<ver>/agda/Substrate (was alongside source pre-2.8.0).
    base = os.path.join(AGDA_ROOT, "_build")
    if os.path.isdir(base):
        vers = sorted(d for d in os.listdir(base) if os.path.isdir(os.path.join(base, d, "agda")))
        if vers:
            return os.path.join(base, vers[-1], "agda", "Substrate")
    return os.path.join(AGDA_ROOT, "Substrate")

root = sys.argv[1] if len(sys.argv) > 1 else _default_core_root()
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
