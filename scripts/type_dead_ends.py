#!/usr/bin/env python3
"""type_dead_ends.py — POSIWID dead ends: types with no eliminator.

A type's purpose is what reacts to it. A type that never appears in an
ARGUMENT/input position of any signature has no signature-level eliminator —
nothing consumes it. Split:
  ISOLATED  — never consumed AND never produced (the introduction-dead).
  DEAD-END  — produced (returned / constructed / held as a field) but never
              consumed: write-only, inert.
Caveat: RECORD types can be consumed via field PROJECTION (not an arg
position), so flagged records need a projection check; DATA types are reliable
(eliminated only by being passed to case/fold = an arg position).
"""
import os, re, collections
from _agdatext import split_arrows, strip
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "agda", "Substrate"))
from _shred_graph import ShredGraph
_G = ShredGraph(ROOT)                       # rung-1: the shared Agda decl graph (kind/home/known + toks)
kind, home, text, known, toks = _G.kind, _G.home, _G.text, _G.known, _G.toks

consumed=set(); produced=set()
sigre=re.compile(r"^([^\s:{}()]+)\s*:\s*(.+)$")
for p,t in text.items():
    for line in t.splitlines():
        m=sigre.match(line)
        if not m: continue
        sig=m.group(2)
        parts=split_arrows(sig)
        if len(parts)>1:
            for a in parts[:-1]: consumed|=set(toks(a))
        produced|=set(toks(parts[-1]))
# field types (held) and constructor returns count as produced
for nm in known:
    produced.add(nm)  # every type is at least its own constructor's result
    blk=text[home[nm]]
    for line in blk.splitlines():
        if " : " in line:
            produced|=set(toks(line.split(" : ",1)[1]))

no_elim=sorted(known-consumed)
isolated=[n for n in no_elim if n not in produced]
deadend =[n for n in no_elim if n in produced]
dd_data=[n for n in deadend if kind[n]=="data"]
dd_rec =[n for n in deadend if kind[n]=="record"]

rel=lambda n: os.path.relpath(home[n],ROOT)
print(f"== POSIWID dead ends: {len(no_elim)}/{len(known)} types have no signature-level eliminator ==")
print(f"\nDATA dead-ends (reliable — data is eliminated only by being consumed): {len(dd_data)}")
for n in dd_data: print(f"    {n:30s} {rel(n)}")
print(f"\nRECORD dead-ends (verify: may be consumed via field projection): {len(dd_rec)}")
for n in dd_rec[:40]: print(f"    {n:30s} {rel(n)}")
if len(dd_rec)>40: print(f"    … (+{len(dd_rec)-40} more)")
print(f"\nISOLATED (never consumed, never produced — the introduction-dead): {len(isolated)}")
for n in isolated: print(f"    {n:30s} {rel(n)}")
