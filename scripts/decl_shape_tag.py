#!/usr/bin/env python3
"""decl_shape_tag.py — make a colliding type's SHAPE visible at its declaration.

Names are vacuous; for a genuinely-ambiguous name (declared in >1 module with
DIFFERENT shapes) the reader can't tell which node a `data/record Name` line is
without inference. This appends a visible tag comment to that line:

    record Section : Set where      -- ⟦shape:053a2000 lift,drop,drop-lift⟧

(a line comment, compile-safe). --check verifies every such decl is tagged;
--fix appends missing tags. Tags match scripts/sppf_node_index.py's hashes.
"""
import os, re, sys, collections, hashlib
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "agda", "Substrate"))
ALLOW = {"⊤","⊥","⊤₁"}
def strip(s):
    s=re.sub(r"\{-.*?-\}"," ",s,flags=re.S); return re.sub(r"--[^\n]*"," ",s)

# collect decls with shape-hash + a short head-list; find genuinely-ambiguous names
info=collections.defaultdict(list)   # name -> [(path, kind, hash, heads)]
declre=re.compile(r"^(data|record)\s+(\S+)(.*)$")
for dp,_,fns in os.walk(ROOT):
    for fn in fns:
        if not fn.endswith(".agda"): continue
        p=os.path.join(dp,fn); lines=strip(open(p,encoding="utf-8").read()).splitlines(); i=0
        while i<len(lines):
            m=declre.match(lines[i])
            if m:
                kind,name,rest=m.group(1),m.group(2),m.group(3); body=[rest]; heads=[]; j=i+1
                while j<len(lines) and (lines[j].strip()=="" or lines[j][:1] in " \t"):
                    if " : " in lines[j]:
                        heads.append(lines[j].split(" : ",1)[0].strip()); body.append(lines[j].split(" : ",1)[1])
                    j+=1
                sh=hashlib.sha1((kind+"|"+"|".join(sorted(" ".join(b.split()) for b in body))).encode()).hexdigest()[:8]
                info[name].append((p,kind,sh,",".join(h for h in heads[:3] if h))); i=j; continue
            i+=1
genuine={n for n,v in info.items() if len({x[2] for x in v})>1} - ALLOW

fix = "--fix" in sys.argv
missing=[]
for name in genuine:
    for (p,kind,sh,heads) in info[name]:
        tag=f"⟦shape:{sh}" + (f" {heads}" if heads else "") + "⟧"
        lines=open(p,encoding="utf-8").read().splitlines()
        dl=re.compile(r"^(data|record)\s+"+re.escape(name)+r"(\s|$|\()")
        changed=False
        for k,line in enumerate(lines):
            if dl.match(line):
                base=re.sub(r"\s*--\s*⟦shape:[^⟧]*⟧\s*$","",line).rstrip()
                want=base+f"      -- {tag}"
                if line.rstrip()==want: break        # correct tag already present
                if fix:
                    lines[k]=want; changed=True
                else:
                    missing.append((name,os.path.relpath(p,ROOT)))
                break
        if changed:
            open(p,"w",encoding="utf-8").write("\n".join(lines)+"\n")

if fix:
    print(f"decl-shape-tag: tagged genuinely-ambiguous declarations "
          f"({len(genuine)} names).")
else:
    print(f"decl-shape-tag: {len(missing)} untagged genuinely-ambiguous declarations.")
    for n,p in sorted(missing): print(f"    {n:28s} {p}")
    sys.exit(1 if missing else 0)
