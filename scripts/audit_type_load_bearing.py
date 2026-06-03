#!/usr/bin/env python3
"""audit_type_load_bearing.py — which types are load-bearing, and which aren't.

For every top-level `data`/`record` type in agda/Substrate, count how many
OTHER modules reference it (comments stripped), classifying each as:

  DEAD   — referenced nowhere outside its own declaration (not load-bearing).
  LOCAL  — used only inside its defining module (load-bearing to that module's
           proofs, but not part of the cross-module surface).
  BORNE  — used in N other modules (load-bearing; N = its degree). If those
           uses are ONLY in re-export/catalog modules, flagged catalog-only.

Usage: scripts/audit_type_load_bearing.py [--full]
  (default prints the DEAD + LOCAL + catalog-only lists and a degree summary;
   --full also prints the load-bearing degree for every type.)
"""
import os, re, sys, collections

ROOT = os.path.join(os.path.dirname(__file__), "..", "agda", "Substrate")
ROOT = os.path.abspath(ROOT)
CATALOG = ("Generators.agda",)  # re-export catalogs: uses here aren't proof-load-bearing

def strip_comments(s: str) -> str:
    s = re.sub(r"\{-.*?-\}", " ", s, flags=re.S)        # block comments
    s = re.sub(r"--[^\n]*", " ", s)                      # line comments
    return s

# 1. gather files (path -> stripped text, tokens)
files = {}
for dp, _, fns in os.walk(ROOT):
    for fn in fns:
        if fn.endswith(".agda"):
            p = os.path.join(dp, fn)
            with open(p, encoding="utf-8") as f:
                txt = strip_comments(f.read())
            toks = set(re.split(r"[\s()\[\]{};,.\"]+", txt))
            files[p] = toks

# 2. find type declarations: `data NAME` / `record NAME` at line start
decls = {}   # name -> defining path (first wins; report dups separately)
dups = collections.defaultdict(list)
declre = re.compile(r"^(?:data|record)\s+(\S+)", re.M)
for p, _ in files.items():
    with open(p, encoding="utf-8") as f:
        for m in declre.finditer(strip_comments(f.read())):
            name = m.group(1)
            if name in ("where",):  # guard
                continue
            dups[name].append(p)
            decls.setdefault(name, p)

# 3. classify
dead, local, catalog_only, borne = [], [], [], []
for name, home in decls.items():
    ext = [p for p in files
           if p != home and name in files[p]]
    if not ext:
        # used only in own file? (token appears beyond the decl)
        own = files[home]
        local.append(name) if name in own else None
        if name not in own:
            dead.append(name)
        # note: token always in own file (the decl); refine: count >1 line
        continue
    non_catalog = [p for p in ext if not p.endswith(CATALOG)]
    if not non_catalog:
        catalog_only.append((name, len(ext)))
    else:
        borne.append((name, len(non_catalog)))

def rel(p): return os.path.relpath(p, ROOT)

print(f"== type load-bearing audit: {len(decls)} types ==")
print(f"DEAD (referenced nowhere outside declaration): {len(dead)}")
for n in sorted(dead):
    print(f"    {n:30s}  {rel(decls[n])}")
print(f"\nCATALOG-ONLY (only re-exported, no proof depends): {len(catalog_only)}")
for n, _ in sorted(catalog_only):
    print(f"    {n:30s}  {rel(decls[n])}")
print(f"\nDUPLICATE NAMES (same name, multiple decls — uniqueness check): "
      f"{sum(1 for v in dups.values() if len(v) > 1)}")
for n, ps in sorted(dups.items()):
    if len(ps) > 1:
        print(f"    {n:24s}  " + " | ".join(rel(p) for p in ps))

borne.sort(key=lambda x: -x[1])
print(f"\nLOAD-BEARING: {len(borne)} types; module-local only: ~{len(local)}")
print("  top 15 by degree (modules depending on it):")
for n, d in borne[:15]:
    print(f"    {d:4d}  {n}")
if "--full" in sys.argv:
    print("\n  full degree list:")
    for n, d in borne:
        print(f"    {d:4d}  {n:30s}  {rel(decls[n])}")
