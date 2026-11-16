#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""synth_typehole_probe.py — PROBE (2): the REAL jea_pysim.typehole on interned
cluster structures, for HIERARCHICAL (nested) holes vs my one-slot version.

Bridge: intern each cluster phrase as its Sequitur RULE-TREE (rules nest → depth;
identical sub-phrases hash-cons to one node → shared subtrees = fan-in). Group by
arity so they align, then C.typehole() recurses positionally — a position whose
fillers share sub-structure becomes a SKELETON-with-sub-holes (nested), only a
TERMINAL hole when the fillers share nothing. render_typehole prints it.
"""

import os, sys, glob
from collections import defaultdict

HERE = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, "/home/mikemol/github/substrate/jea/metalanguage")
sys.path.insert(0, "/home/mikemol/github/substrate/jea")
import grammar_phrase_lattice as G
from eliza.sequitur import Sequitur, NT
from jea_pysim import Corpus
from jea_pyalg import IR

PHRASE = sys.argv[1] if len(sys.argv) > 1 else "never discard residue"
files = sorted(
    f
    for f in glob.glob(HERE + "/**/*.md", recursive=True)
    if os.path.basename(f) not in G.SKIP
    and (os.sep + "index" + os.sep) not in f
    and (os.sep + "synth" + os.sep) not in f
)
toks = [G.words(G.full(f)) for f in files]
text = [" " + " ".join(t) + " " for t in toks]
members = [i for i in range(len(files)) if (" " + PHRASE + " ") in text[i]]
memtext = [text[i] for i in members]

gram = Sequitur()
for i in members:
    for w in toks[i]:
        gram.observe(w)
    gram.observe("∎")
rules = gram.all_rules()

C = Corpus()
memo = {}


def intern_rule(rid):
    if rid in memo:
        return memo[rid]
    kids = []
    for sym in rules[rid]:
        if isinstance(sym, NT):
            kids.append(intern_rule(sym.rule_id))
        elif sym != "∎":
            kids.append(C.I.intern(IR(kind="tok", op=sym)))
    nid = C.I.intern(IR(kind="seq", children=tuple(kids)))
    memo[rid] = nid
    return nid


trees = []
for rid in rules:
    if rid == 0:
        continue
    p = tuple(w for w in G.expand(rules[rid], rules) if w != "∎")
    if not (2 <= len(p) <= 6):
        continue
    if sum(1 for t in memtext if (" " + " ".join(p) + " ") in t) < 2:  # ≥2 members
        continue
    nid = intern_rule(rid)
    trees.append((nid, len(C.I.nodes[nid].children), " ".join(p)))


def depth(th):
    return 1 + max([depth(c) for c in th.get("children", [])] + [0]) if th.get("children") else 0


print(
    f"=== cluster «{PHRASE}»: {len(members)} members, {len(set(t[0] for t in trees))} distinct phrase-trees, "
    f"interned forest size {C.I.size()} ==="
)
shared = sum(1 for fi in C.I.fanin if fi >= 2)
print(f"shared subtrees (fan-in ≥2, the hash-consed quotient): {shared}")


# typehole needs COMPARABLE inputs — group by (head child, arity), then align within.
def headtok(nid):
    c = C.I.nodes[nid].children
    return C.I.nodes[c[0]].op or f"seq{C.I.nodes[c[0]].kind}" if c else "?"


byhead = defaultdict(set)
for nid, ar, phr in trees:
    c = C.I.nodes[nid].children
    head = c[0] if c else -1
    byhead[(head, ar)].add(nid)
groups = []
for (head, ar), ids in byhead.items():
    if len(ids) < 3:
        continue
    th = C.typehole(list(ids))
    groups.append((depth(th), len(ids), headtok(next(iter(ids))), th))
groups.sort(key=lambda g: (g[0], g[1]), reverse=True)
dd = [d for d, *_ in groups]
print(
    f"head-groups (≥3 trees): {len(groups)}; nesting depths {sorted(set(dd), reverse=True)} "
    f"(max {max(dd) if dd else 0}); depth≥2 groups (genuine hierarchy): {sum(1 for d in dd if d >= 2)}\n"
)
for d, n, h, th in groups[:6]:
    print(f"=== head «{h}»: {n} trees → typehole depth {d} ===")
    print(C.render_typehole(th))
    print()
