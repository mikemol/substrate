#!/usr/bin/env python3
"""check_import_shape.py — enforce shape-specialized imports of colliding names.

Names are vacuous; a name declared in >1 module with DIFFERENT shapes must be
specialized at import — `open import M using () renaming (Name to Name⟦shape⟧)`
or qualified — never brought in bare, so the reader sees which shape. This
flags modules that `using (Name)` a genuinely-ambiguous Name without renaming
it. Excludes level-polymorphic foundation dups (⊤/⊥ — same object, lifted).

Usage: check_import_shape.py [--quiet]   (exit 1 on violations.)
"""
import os, re, sys, collections, hashlib
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "agda", "Substrate"))
ALLOW = {"⊤","⊥","⊤₁"}   # level-poly foundation dups: the level is the spec, visible
def strip(s):
    s=re.sub(r"\{-.*?-\}"," ",s,flags=re.S); return re.sub(r"--[^\n]*"," ",s)

# genuine-ambiguity names: declared in >1 module with >1 distinct shape-hash
decls=collections.defaultdict(list)
declre=re.compile(r"^(data|record)\s+(\S+)(.*)$")
texts={}
for dp,_,fns in os.walk(ROOT):
    for fn in fns:
        if not fn.endswith(".agda"): continue
        p=os.path.join(dp,fn); t=strip(open(p,encoding="utf-8").read()); texts[p]=t
        lines=t.splitlines(); i=0
        while i<len(lines):
            m=declre.match(lines[i])
            if m:
                kind,name,rest=m.group(1),m.group(2),m.group(3); body=[rest]; j=i+1
                while j<len(lines) and (lines[j].strip()=="" or lines[j][:1] in " \t"):
                    if " : " in lines[j]: body.append(lines[j].split(" : ",1)[1])
                    j+=1
                sh=hashlib.sha1((kind+"|"+"|".join(sorted(" ".join(b.split()) for b in body))).encode()).hexdigest()[:8]
                decls[name].append(sh); i=j; continue
            i+=1
genuine={n for n,shs in decls.items() if len(set(shs))>1} - ALLOW

# scan imports: a `using (...)` naming a genuine name without `renaming (Name to`
imp=re.compile(r"open\s+import\s+\S+([^\n]*(?:\n\s+[^\n]*)*)")  # stmt + continuations
viol=collections.defaultdict(list)
for p,t in texts.items():
    for m in imp.finditer(t):
        clause=m.group(1)
        us=re.search(r"using\s*\(([^)]*)\)",clause,re.S)
        if not us: continue
        names=set(w for w in re.split(r"[\s;,]+", us.group(1)) if w)
        ren=set(re.findall(r"renaming\s*\([^)]*?(\S+)\s+to\s",clause))
        for n in names & genuine:
            if n not in ren:
                viol[n].append(os.path.relpath(p,ROOT))

# RATCHET: a large codebase can't retrofit 90 sites at once. Gate on NO NEW
# bare colliding imports (count may only go down). Lower BASELINE as they're
# fixed; the policy is enforced for new code today.
BASELINE = 25
n=sum(len(v) for v in viol.values())
over = n > BASELINE
if "--quiet" not in sys.argv or over:
    print(f"import-shape: {len(genuine)} genuinely-ambiguous names; "
          f"{n} bare imports (baseline {BASELINE}).", file=sys.stderr if over else sys.stdout)
    if "--quiet" not in sys.argv:
        for nm,files in sorted(viol.items(), key=lambda kv:-len(kv[1])):
            print(f"  {nm}: {len(files)}  ({', '.join(files[:4])}{' …' if len(files)>4 else ''})")
    if over:
        print(f"  GATE FAILED: {n} > {BASELINE} — a NEW bare colliding import. Specialize "
              f"by shape: `renaming (Name to Name⟦shape⟧)` (see scratch/sppf_collision_index.md).",
              file=sys.stderr)
    elif n < BASELINE:
        print(f"  (note: {n} < baseline {BASELINE} — lower BASELINE in check_import_shape.py.)")
sys.exit(1 if over else 0)
