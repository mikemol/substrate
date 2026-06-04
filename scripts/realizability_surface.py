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
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "agda", "Substrate"))
def strip(s):
    s=re.sub(r"\{-.*?-\}"," ",s,flags=re.S); return re.sub(r"--[^\n]*"," ",s)

text={}; kind={}; home={}; modof={}; fileof={}
modre=re.compile(r"^module\s+(\S+)\s+where",re.M)
for dp,_,fns in os.walk(ROOT):
    for fn in fns:
        if fn.endswith(".agda"):
            p=os.path.join(dp,fn); t=strip(open(p,encoding="utf-8").read()); text[p]=t
            for m in re.finditer(r"^(data|record)\s+(\S+)",t,re.M):
                kind.setdefault(m.group(2),m.group(1)); home.setdefault(m.group(2),p)
            mm=modre.search(t)
            if mm: modof[p]=mm.group(1); fileof[mm.group(1)]=p
known=set(kind)
def sa(s):
    out=[];d=0;cur=""
    for ch in s:
        if ch in "([{":d+=1
        elif ch in ")]}":d-=1
        if ch=="→" and d==0: out.append(cur);cur=""
        else: cur+=ch
    out.append(cur);return out
def toks(s): return [t for t in re.split(r"[\s()\[\]{};,.]+",s) if t in known]

produced=set(); consumed=set()
sig=re.compile(r"^\s*[^\s:]+\s*:\s*(.+)$")
for t in text.values():
    for line in t.splitlines():
        m=sig.match(line)
        if not m or "→" not in m.group(1):
            if m: produced|=set(toks(m.group(1)))
            continue
        parts=sa(m.group(1))
        for a in parts[:-1]: consumed|=set(toks(a))
        produced|=set(toks(parts[-1]))

# transitive reach (for the bounded proxy)
impre=re.compile(r"^\s*(?:open\s+import|import)\s+([A-Za-z0-9_.'-]+)",re.M)
importers=collections.defaultdict(set)
for p,t in text.items():
    if p not in modof: continue
    for m in impre.finditer(t):
        if m.group(1) in fileof: importers[m.group(1)].add(modof[p])
def reach(mod):
    seen={mod}; q=collections.deque([mod])
    while q:
        u=q.popleft()
        for v in importers[u]:
            if v not in seen: seen.add(v); q.append(v)
    return len(seen)-1
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

def rank(T):
    mod=modof.get(home[T],"")
    if T in consumed:
        return 4 if reach(mod)>=40 else 3
    if T in produced: return 2
    return 1
ranks={T:rank(T) for T in known}
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
