#!/usr/bin/env python3
"""rank4_shred.py — shred the rank-4 peak in terms of itself.

For each rank-4 (covered) type, read its definition's referenced types and
split them into:
  * BRIDGES  — other rank-4 types it is built from (peak ↔ peak: the fluidity
               graph; mutual/cyclic edges = mutually expressible);
  * RESIDUES — lower-rank types in its definition (the leftover that "belongs at
               a lower level" — a connector exposed by the shred).
Reveals which summit objects compose from which, and the lower-rank residues
that bridge them.
"""
import os, re, collections
from _agdatext import split_arrows, strip
sa = split_arrows
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "agda", "Substrate"))
text={}; kind={}; home={}; modof={}; fileof={}; body=collections.defaultdict(list)
modre=re.compile(r"^module\s+(\S+)\s+where",re.M)
declre=re.compile(r"^(data|record)\s+(\S+)(.*)$")
for dp,_,fns in os.walk(ROOT):
    for fn in fns:
        if not fn.endswith(".agda"): continue
        p=os.path.join(dp,fn); t=strip(open(p,encoding="utf-8").read()); text[p]=t
        mm=modre.search(t)
        if mm: modof[p]=mm.group(1); fileof[mm.group(1)]=p
        lines=t.splitlines(); i=0
        while i<len(lines):
            m=declre.match(lines[i])
            if m:
                k,name,rest=m.group(1),m.group(2),m.group(3); body[name].append(rest); j=i+1
                kind.setdefault(name,k); home.setdefault(name,p)
                while j<len(lines) and (lines[j].strip()=="" or lines[j][:1] in " \t"):
                    if " : " in lines[j]: body[name].append(lines[j].split(" : ",1)[1])
                    j+=1
                i=j; continue
            i+=1
known=set(kind)
def toks(s): return [t for t in re.split(r"[\s()\[\]{};,.]+",s) if t in known]

produced=set(); consumed=set()
sig=re.compile(r"^\s*[^\s:]+\s*:\s*(.+)$")
for t in text.values():
    for line in t.splitlines():
        m=sig.match(line)
        if not m: continue
        if "→" in m.group(1):
            parts=sa(m.group(1))
            for a in parts[:-1]: consumed|=set(toks(a))
            produced|=set(toks(parts[-1]))
        else: produced|=set(toks(m.group(1)))
imports=collections.defaultdict(set); impre=re.compile(r"^\s*(?:open\s+import|import)\s+([A-Za-z0-9_.'-]+)",re.M)
for p,t in text.items():
    if p not in modof: continue
    for m in impre.finditer(t):
        if m.group(1) in fileof: imports[modof[p]].add(m.group(1))
importers=collections.defaultdict(set)
for m,ds in imports.items():
    for d in ds: importers[d].add(m)
def reach(mod):
    seen={mod}; q=collections.deque([mod])
    while q:
        u=q.popleft()
        for v in importers[u]:
            if v not in seen: seen.add(v); q.append(v)
    return len(seen)-1
def rank(T):
    mod=modof.get(home[T],"")
    if T in consumed: return 4 if reach(mod)>=40 else 3
    if T in produced: return 2
    return 1
ranks={T:rank(T) for T in known}
peak=[T for T in known if ranks[T]==4]

def refs(T):
    r=set()
    for b in body[T]: r|=set(toks(b))
    r.discard(T)
    return r

print(f"== shredding the rank-4 peak ({len(peak)} objects) ==\n")
edges=collections.defaultdict(set)
for T in sorted(peak):
    rs=refs(T)
    bridges=sorted(r for r in rs if ranks.get(r)==4)
    residues=sorted((ranks.get(r,0),r) for r in rs if ranks.get(r,9)<4)
    for b in bridges: edges[T].add(b)
    if bridges or residues:
        print(f"  {T}")
        if bridges:  print(f"      ⇄ peak: {', '.join(bridges)}")
        if residues: print(f"      ↓ residue: " + ", ".join(f"{r}(r{k})" for k,r in residues))

# mutual edges = fluid pairs (A built from B AND B from A)
mutual=sorted({tuple(sorted((a,b))) for a in edges for b in edges[a] if a in edges.get(b,())})
print(f"\n== MUTUAL (fluid) peak pairs — each built from the other ==")
for a,b in mutual: print(f"   {a} ⇄ {b}")
