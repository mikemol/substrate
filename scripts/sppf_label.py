#!/usr/bin/env python3
"""sppf_label.py — label the SEMANTIC SPPF nodes: group constructions by the
OBJECT they build (not by shape). A node = an object; its members = alternate
constructions; its edges = ≃ bridges. Membership signals:
  * same canonical name across modules (subscripts normalised) — the same
    object presented in different files;
  * an explicit `X≃Y` / `X≃Y`-style equivalence witness linking two types.
Multi-member nodes are the ATLASES (objects with alternate constructions); the
missing within-node ≃ pairs are the bridge TODO. Shape-iso is deliberately NOT
used for membership (different objects can share a shape).
"""
import os, re, collections
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "agda", "Substrate"))
def strip(s):
    s=re.sub(r"\{-.*?-\}"," ",s,flags=re.S); return re.sub(r"--[^\n]*"," ",s)
SUB=str.maketrans("₀₁₂₃₄₅₆₇₈₉ₐ","0123456789a")
def norm(n): return n.translate(SUB).lower().replace("-","").replace("_","")

decls=collections.defaultdict(list)        # type name -> [module]
modof={}
eqs=[]                                      # (A,B) equivalence-witness links
declre=re.compile(r"^(?:data|record)\s+(\S+)")
eqre=re.compile(r"^(?:data|record)\s+(\S+?)≃(\S+)")   # records named A≃B
modre=re.compile(r"^module\s+(\S+)\s+where",re.M)
for dp,_,fns in os.walk(ROOT):
    for fn in fns:
        if not fn.endswith(".agda"): continue
        p=os.path.join(dp,fn); t=strip(open(p,encoding="utf-8").read())
        mm=modre.search(t); mod=mm.group(1) if mm else os.path.relpath(p,ROOT)
        for line in t.splitlines():
            m=declre.match(line)
            if m: decls[m.group(1)].append(mod)
            e=eqre.match(line)
            if e: eqs.append((e.group(1),e.group(2)))

# name-classes: normalised name -> set of (rawname, module)
nameclass=collections.defaultdict(set)
for n,mods in decls.items():
    for mod in mods: nameclass[norm(n)].add((n,mod))

# union-find over presentations to fold ≃-links into name-classes
parent={}
def find(x):
    parent.setdefault(x,x)
    while parent[x]!=x: parent[x]=parent[parent[x]]; x=parent[x]
    return x
def union(a,b): parent[find(a)]=find(b)
# seed components by normalised name
for nn,members in nameclass.items():
    reps=list(members)
    for m in reps[1:]: union(reps[0],m)
# add ≃ links (by normalised name, joining whatever components)
allmembers={m for ms in nameclass.values() for m in ms}
byname=collections.defaultdict(list)
for (n,mod) in allmembers: byname[norm(n)].append((n,mod))
for A,B in eqs:
    a=byname.get(norm(A)); b=byname.get(norm(B))
    if a and b: union(a[0],b[0])

comp=collections.defaultdict(set)
for m in allmembers: comp[find(m)].add(m)
atlases=[c for c in comp.values() if len({n for n,_ in c})>1 or len(c)>1]

# show the multi-presentation nodes (the atlases), richest first
atlases=[c for c in comp.values() if len(c)>1]
atlases.sort(key=lambda c:-len(c))
print(f"== labeled semantic SPPF nodes with ALTERNATE constructions: {len(atlases)} ==")
print(f"   ({len(eqs)} ≃-witnesses found; {len(allmembers)} type-presentations total)\n")
for c in atlases[:30]:
    names=sorted({n for n,_ in c})
    label=max(names, key=len)   # canonical label = the most explicit name
    print(f"  ⟦{label}⟧  ({len(c)} presentations)")
    for n,mod in sorted(c):
        print(f"        {n:24s} {mod}")