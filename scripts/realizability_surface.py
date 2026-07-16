#!/usr/bin/env python3
"""realizability_surface.py — rank every type by the Charter gate-chain,
read off its reactions, plotted over dependency depth: a topological surface.

Charter chain  ε ▷ recipe ▷ manifest ▷ measure ▷ bounded  (con ⊑ rea ⊑ obs ⊑ cov,
ordering forced). Empirically, per type T:
  1 recipe   — declared (always).             rank 1 if neither produced nor consumed.
  2 manifest — an instance is constructed:     T appears as a result type (produced).
  3 measure  — it is observed:                 T appears in an argument position
               (consumed) OR its record fields are projected.
  4 bounded  — covered: wide transitive reach (proxy for a finite cover / saturation).
Rank-1 = the realizability holes (recipe but never manifest — implementation owed).
The surface = rank (height) over dep-depth (base): low cells are the holes.

Caveat: arg-position consume-scan misses infix/projection, so rank is a LOWER
bound; the rank-1 set (neither produced nor consumed) is the reliable floor.
"""
import os, re, collections
from _agdatext import split_arrows, strip
sa = split_arrows
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "agda", "Substrate"))
from _shred_graph import ShredGraph
_G = ShredGraph(ROOT)                       # rung-1: the shared Agda decl graph + reach/rank/toks
text, kind, home, modof, fileof, known, produced, consumed, importers = (
    _G.text, _G.kind, _G.home, _G.modof, _G.fileof, _G.known, _G.produced, _G.consumed, _G.importers)
toks, reach, rank = _G.toks, _G.reach, _G.rank
impre=re.compile(r"^\s*(?:open\s+import|import)\s+([A-Za-z0-9_.'-]+)",re.M)
depth={}
def md(m,st=()):
    if m in depth: return depth[m]
    if m in st: return 0
    depth[m]=1+max([md(d,st+(m,)) for d in []] or [-1])  # placeholder; set below
    return depth[m]
# proper depth via imports
imports=collections.defaultdict(set)
for p,t in text.items():
    if p not in modof: continue
    for m in impre.finditer(t):
        if m.group(1) in fileof: imports[modof[p]].add(m.group(1))
depth={}
def dep(m,st=()):
    if m in depth: return depth[m]
    if m in st: return 0
    depth[m]=1+max([dep(d,st+(m,)) for d in imports[m]] or [-1]); return depth[m]
for m in fileof: dep(m)

ranks={T:rank(T) for T in known}           # rank = _G.rank (routed above)
dist=collections.Counter(ranks.values())
NAMES={1:"recipe-only (HOLE)",2:"manifest, unmeasured",3:"measured (observed)",4:"bounded (covered)"}
print(f"== realizability surface: {len(known)} types by Charter gate-rank ==")
for r in (1,2,3,4):
    print(f"  rank {r} {NAMES[r]:24s}: {dist[r]}")
rel=lambda T: os.path.relpath(home[T],ROOT)
# exclude mixfix (consumed infix — the scan can't see it; rank is a lower bound)
holes=sorted((T for T in known if ranks[T]==1 and "_" not in T),
             key=lambda T: depth.get(modof.get(home[T],""),0))
mixfix_h=[T for T in known if ranks[T]==1 and "_" in T]
print(f"\n-- rank-1 HOLES ({len(holes)} non-mixfix; {len(mixfix_h)} mixfix excluded as "
      f"infix-consumed) — recipe but never manifest, by dep-depth (surface floor) --")
for T in holes:
    d=depth.get(modof.get(home[T],""),0)
    print(f"   depth {d:2d}  {T:28s} {kind[T]:6s} {rel(T)}")

peak=sorted((T for T in known if ranks[T]==4), key=lambda T: -reach(modof.get(home[T],"")))
print(f"\n-- rank-4 PEAK ({len(peak)}) — covered/bounded, by transitive reach (the summits) --")
for T in peak:
    print(f"   reach {reach(modof.get(home[T],'')):4d}  {T:24s} {kind[T]:6s} {rel(T)}")
