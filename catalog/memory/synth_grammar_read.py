#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""synth_grammar_read.py — read Sequitur's grammar HIERARCHY directly (it is lossless,
so the structure is present; depth-1 was a reading error, not the data). Measure rule
depth / fan-in / member-support, and render the deepest most-shared rules WITH nesting.
"""

import os, sys, glob
from collections import Counter

HERE = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, HERE)
import grammar_phrase_lattice as G
from eliza.sequitur import Sequitur, NT

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

_dep = {}


def rdepth(rid):
    if rid in _dep:
        return _dep[rid]
    _dep[rid] = 1 + max([rdepth(s.rule_id) for s in rules[rid] if isinstance(s, NT)] + [0])
    return _dep[rid]


info = {}
for rid in rules:
    if rid == 0:
        continue
    exp = tuple(w for w in G.expand(rules[rid], rules) if w != "∎")
    if not exp:
        continue
    ms = sum(1 for t in memtext if (" " + " ".join(exp) + " ") in t)
    info[rid] = (exp, ms, gram.rule_uses(rid), rdepth(rid))

depths = Counter(d for _, _, _, d in info.values())
shared_depths = Counter(d for _, ms, _, d in info.values() if ms >= 2)
print(f"=== «{PHRASE}» grammar: {len(info)} rules, top-rule len {len(rules[0])} ===")
print(f"rule-depth distribution (ALL):    {dict(sorted(depths.items()))}  max {max(depths)}")
print(
    f"rule-depth distribution (≥2-mem): {dict(sorted(shared_depths.items()))}  "
    f"max {max(shared_depths) if shared_depths else 0}"
)


def show(rid, ind=0, cap=8):
    e, ms, fi, d = info[rid]
    mark = "·".join(e)[:48]
    print("  " * ind + f"«{mark}»  ms{ms} fan{fi} depth{d}")
    if ind < cap:
        for s in rules[rid]:
            if isinstance(s, NT) and s.rule_id in info:
                show(s.rule_id, ind + 1, cap)


# the deepest ≥2-member rules — the genuine cross-member hierarchical motifs
deep = sorted((rid for rid in info if info[rid][1] >= 2), key=lambda r: (-info[r][3], -info[r][1]))
print(f"\n=== deepest ≥2-member rules (the cross-member hierarchy, read off the grammar) ===")
for rid in deep[:5]:
    show(rid)
    print()
