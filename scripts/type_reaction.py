#!/usr/bin/env python3
"""type_reaction.py — invert the SPPF: catalogue types by what REACTS to them.

POSIWID / meaning-is-use: a type's identity is not its constructors but the
shape of its eliminators — the functions that take it as input and what they
turn it into. For each top-level signature `f : … T … → R`, T in an argument
position is CONSUMED; R is the reaction. reaction(T) = multiset of result-type
tokens across all consumers. Then enums that look identical by introduction
should DIFFER by reaction (different reactors = different meaning), and types
that look different by introduction may SHARE a reaction profile.
"""
import os, re, collections
from _agdatext import split_arrows, strip
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "agda", "Substrate"))
from _shred_graph import ShredGraph
_G = ShredGraph(ROOT)                       # rung-1: the shared Agda decl graph (known + toks)
known, text, toks = _G.known, _G.text, _G.toks

reaction=collections.defaultdict(collections.Counter)   # T -> Counter(result-type)
consumers=collections.defaultdict(set)                   # T -> set(consuming def names)
sigre=re.compile(r"^([^\s:{}()]+)\s*:\s*(.+)$")
for p,t in text.items():
    # join continuation lines into logical sigs (cheap: per physical line)
    for line in t.splitlines():
        m=sigre.match(line)
        if not m: continue
        nm,sig=m.group(1),m.group(2)
        if "→" not in sig: continue
        parts=split_arrows(sig); args,res=parts[:-1],parts[-1]
        argset=set();
        for a in args: argset|=set(toks(a))
        for T in argset:
            for r in toks(res): reaction[T][r]+=1
            consumers[T].add(nm)

ENUMS=["Distinction-Name","Selector","SylowPrime","Axis","Chirality","Gen",
       "Line","Point","Mode","LockState","TenseMarker"]
print("== enum class: reaction profiles (what reacts to each) ==")
for T in ENUMS:
    if T in reaction:
        top=", ".join(f"{k}:{v}" for k,v in reaction[T].most_common(5))
        print(f"  {T:18s} consumers={len(consumers[T]):3d}  reacts→ {top or '(none)'}")
    else:
        print(f"  {T:18s} (no arrow-consumers found)")

# reaction-iso: types with the SAME dominant reaction signature
print("\n== reaction-iso: types sharing a reaction signature (top-3 result types) ==")
sigof={T:tuple(sorted(k for k,_ in c.most_common(3))) for T,c in reaction.items() if c}
groups=collections.defaultdict(list)
for T,s in sigof.items():
    if s: groups[s].append(T)
for s,ts in sorted(groups.items(), key=lambda kv:-len(kv[1]))[:12]:
    if len(ts)>1:
        print(f"  reacts→{{{', '.join(s)}}} : " + ", ".join(sorted(ts)[:8]) + (" …" if len(ts)>8 else ""))
