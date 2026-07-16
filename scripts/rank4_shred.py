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
from _shred_graph import ShredGraph
_G = ShredGraph(ROOT)                       # rung-1: the shared Agda decl graph + reach/rank/refs/toks
text, kind, home, modof, fileof, body, known, produced, consumed, importers = (
    _G.text, _G.kind, _G.home, _G.modof, _G.fileof, _G.body, _G.known, _G.produced, _G.consumed, _G.importers)
toks, reach, rank, refs = _G.toks, _G.reach, _G.rank, _G.refs
ranks={T:rank(T) for T in known}
peak=[T for T in known if ranks[T]==4]

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
