#!/usr/bin/env python3
"""audit_import_reach.py — transitive load-bearing reach via the import graph.

The per-type counts in audit_type_load_bearing.py are DIRECT (degree-1): files
that literally name the type. This computes TRANSITIVE reach: for a type T in
home module H, the set of modules that transitively import a module which
DIRECTLY references T — i.e. everything whose build ultimately pulls in a real
user of T — plus the degrees-of-separation distribution (BFS depth from the
direct users out through the reverse-import graph).

Usage: audit_import_reach.py [NAME ...]   (default: a built-in spine list)
"""
import os, re, sys, collections

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "agda", "Substrate"))

def strip(s):
    s = re.sub(r"\{-.*?-\}", " ", s, flags=re.S)
    return re.sub(r"--[^\n]*", " ", s)

mod_of, file_of, text_of, toks_of = {}, {}, {}, {}
modre  = re.compile(r"^module\s+(\S+)\s+where", re.M)
impre  = re.compile(r"^\s*(?:open\s+import|import)\s+([A-Za-z0-9_.'-]+)", re.M)

for dp, _, fns in os.walk(ROOT):
    for fn in fns:
        if not fn.endswith(".agda"): continue
        p = os.path.join(dp, fn)
        raw = open(p, encoding="utf-8").read()
        t = strip(raw)
        m = modre.search(t)
        if not m: continue
        name = m.group(1)
        mod_of[p] = name; file_of[name] = p; text_of[name] = t
        toks_of[name] = set(re.split(r"[\s()\[\]{};,.\"]+", t))

# import graph: module -> set of imported modules (restricted to our set)
imports = {n: set() for n in file_of}
for n in file_of:
    for m in impre.finditer(text_of[n]):
        dep = m.group(1)
        if dep in file_of:
            imports[n].add(dep)
# reverse: module -> direct importers
importers = collections.defaultdict(set)
for n, deps in imports.items():
    for d in deps:
        importers[d].add(n)

def bfs_reach(seeds):
    """transitive importers of any module in `seeds`, with BFS depth."""
    depth = {s: 0 for s in seeds}
    q = collections.deque(seeds)
    while q:
        u = q.popleft()
        for v in importers[u]:
            if v not in depth:
                depth[v] = depth[u] + 1
                q.append(v)
    return depth

def direct_users(name):
    return {n for n in file_of if name in toks_of[n]}

SPINE = sys.argv[1:] or ["_≡_","ℕ","Fin","Vec","Word","Linear","Σ","Permutation",
                          "UPArrow","Canonical","List","Gen","CategoryOf","DivStr","Wedge"]

print(f"== transitive reach ({len(file_of)} modules in graph) ==")
print(f"{'type':14s} {'direct':>7s} {'transitive':>11s} {'max-sep':>8s}  depth-histogram")
for name in SPINE:
    if name not in (set().union(*[toks_of[n] for n in file_of])):
        print(f"{name:14s}   (not found)"); continue
    du = direct_users(name)
    depth = bfs_reach(du)                 # depth 0 = direct users themselves
    downstream = {m: d for m, d in depth.items() if d > 0}
    hist = collections.Counter(downstream.values())
    histstr = " ".join(f"{k}:{hist[k]}" for k in sorted(hist))
    maxsep = max(downstream.values()) if downstream else 0
    print(f"{name:14s} {len(du):7d} {len(downstream):11d} {maxsep:8d}  {histstr}")

# global graph shape
alldepth = []
for n in file_of:
    d = bfs_reach({n})
    if len(d) > 1: alldepth.append(max(d.values()))
print(f"\nimport graph: max dependency-cone depth across modules = {max(alldepth) if alldepth else 0}")
fanin = sorted(((len(importers[n]), n) for n in file_of), reverse=True)[:8]
print("highest direct fan-in (most direct importers):")
for c, n in fanin: print(f"    {c:4d}  {n}")
