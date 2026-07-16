#!/usr/bin/env python3
"""type_sppf_crosslayer.py — rank SPPF isomorphism classes by the dep-depth
span they cross. A class whose members live at both a low (foundation) and a
high (applied) dependency depth, across different silos, with NON-TRIVIAL
shared structure, is an unconstructed cross-silo correspondence — found
structurally. Trivial shapes (enums, ⊤) are kept but flagged by low weight.
"""
import os, re, collections, hashlib
from _agdatext import strip

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "agda", "Substrate"))
STRUCT = {"→","×","Σ","⊎","≡","⊤","⊥","Set","Set₁","Set₂","∀","List","Vec","Fin","ℕ"}
blocks, home = {}, {}            # name -> (kind,[exprs]) ; name -> file
modof, fileof = {}, {}           # file -> module ; module -> file
imports = collections.defaultdict(set)
declre = re.compile(r"^(data|record)\s+(\S+)(.*)$")
modre  = re.compile(r"^module\s+(\S+)\s+where", re.M)
impre  = re.compile(r"^\s*(?:open\s+import|import)\s+([A-Za-z0-9_.'-]+)", re.M)

for dp,_,fns in os.walk(ROOT):
    for fn in fns:
        if not fn.endswith(".agda"): continue
        p=os.path.join(dp,fn); txt=strip(open(p,encoding="utf-8").read())
        mm=modre.search(txt)
        if mm: modof[p]=mm.group(1); fileof[mm.group(1)]=p
        lines=txt.splitlines(); i=0
        while i<len(lines):
            m=declre.match(lines[i])
            if m:
                kind,name,rest=m.group(1),m.group(2),m.group(3); exprs=[rest]; j=i+1
                while j<len(lines) and (lines[j].strip()=="" or lines[j][:1] in " \t"):
                    if " : " in lines[j]: exprs.append(lines[j].split(" : ",1)[1])
                    elif "→" in lines[j] or "×" in lines[j]: exprs.append(lines[j])
                    j+=1
                if name not in blocks: blocks[name]=(kind,exprs); home[name]=p
                i=j; continue
            i+=1
for p in list(modof):
    for m in impre.finditer(strip(open(p,encoding="utf-8").read())):
        if m.group(1) in fileof: imports[modof[p]].add(m.group(1))

known=set(blocks)
def fshape(expr,stack):
    out=[]
    for t in re.split(r"[\s()\[\]{};,.]+",expr):
        if t in STRUCT: out.append(t)
        elif t in known: out.append("⟲" if t in stack else "T"+hashes.get(t,"?")[:6])
    return tuple(out)
hashes={}
def nh(name,stack=()):
    if name in hashes: return hashes[name]
    kind,exprs=blocks[name]; stack=stack+(name,)
    for e in exprs:
        for t in re.split(r"[\s()\[\]{};,.]+",e):
            if t in known and t not in stack and t not in hashes: nh(t,stack)
    shapes=sorted(fshape(e,stack) for e in exprs if e.strip())
    hashes[name]=hashlib.sha1((kind+"|"+repr(shapes)).encode()).hexdigest(); return hashes[name]
for n in list(blocks): nh(n)

# module depth (longest import chain from a root)
depth={}
def md(m,seen=()):
    if m in depth: return depth[m]
    if m in seen: return 0
    ds=[md(d,seen+(m,)) for d in imports[m]] or [-1]
    depth[m]=1+max(ds); return depth[m]
for m in fileof: md(m)
def silo(mod):
    parts=mod.split("."); return parts[1] if len(parts)>1 else parts[0]
def tdepth(n): return depth.get(modof.get(home[n],""),0)
def tsilo(n):  return silo(modof.get(home[n],"?"))
def weight(n):                       # structural richness of the shared shape
    return sum(len(fshape(e,(n,))) for e in blocks[n][1] if e.strip())

byhash=collections.defaultdict(list)
for n,h in hashes.items(): byhash[h].append(n)
classes=[v for v in byhash.values() if len(v)>1]

rows=[]
for cls in classes:
    ds=[tdepth(n) for n in cls]; silos={tsilo(n) for n in cls}
    rows.append((max(ds)-min(ds), len(silos), weight(cls[0]), min(ds),max(ds),silos,cls))
rows.sort(key=lambda r:(-r[0],-r[1],-r[2]))

print("== isomorphism classes ranked by dep-depth span ==")
print(f"{'span':>4} {'silos':>5} {'wt':>3}  depth   members")
for span,nsil,wt,lo,hi,silos,cls in rows[:25]:
    tag = "  <-- RICH+WIDE (bridge candidate)" if span>=4 and wt>=4 else (
          "  (trivial shape)" if wt<=2 else "")
    print(f"{span:4d} {nsil:5d} {wt:3d}  {lo:>2}..{hi:<2}  "
          + ", ".join(sorted(cls)[:6]) + (" …" if len(cls)>6 else "") + tag)
