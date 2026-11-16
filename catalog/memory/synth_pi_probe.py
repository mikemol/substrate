#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""synth_pi_probe.py — PROBE: the apex as a QUOTIENTED Π, not a Σ.

My projection was a SUM (⊕ phrases — enumerate alternatives). This expands the
meet back OUT into the cluster's grammar phrases and extracts TYPED-HOLE TEMPLATES:
phrases identical except in one slot collapse to a skeleton (the Π, shared by ≥2
members) with a HOLE (the Σ of fillers = the quotiented residue). E.g.
`eea trace` + `algebra trace` ⟹ `⟨eea|algebra⟩ trace`. The skeleton is the
universal structure; the hole's fillers are the retained per-member variation.
(This is jea_pysim.typehole specialized to the cluster's phrase grammar-subset.)

  python3 synth_pi_probe.py "never discard residue"
"""

import os, re, sys, glob
from collections import defaultdict

HERE = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, HERE)
import grammar_phrase_lattice as G
from eliza.sequitur import Sequitur

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
df = __import__("collections").Counter(w for t in toks for w in set(t))
vocab = set(w for w, n in df.items() if 3 <= n <= 60)
members = [i for i in range(len(files)) if (" " + PHRASE + " ") in text[i]]
memtext = [text[i] for i in members]

# expand the meet back out: the cluster's recurring grammar phrases (≥2 members, 2–5 words)
gram = Sequitur()
for i in members:
    for w in toks[i]:
        gram.observe(w)
    gram.observe("∎")
rules = gram.all_rules()
phrases = set()
for rid in rules:
    if rid == 0:
        continue
    p = tuple(w for w in G.expand(rules[rid], rules) if w != "∎")
    if 2 <= len(p) <= 5 and any(w in vocab for w in p):
        if sum(1 for t in memtext if (" " + " ".join(p) + " ") in t) >= 2:
            phrases.add(p)

# QUOTIENTED Π: collapse phrases identical but for one slot → skeleton + typed hole
holes = defaultdict(set)
for p in phrases:
    for i in range(len(p)):
        holes[p[:i] + ("⟨⟩",) + p[i + 1 :]].add(p[i])
templates = [
    (len(f), skel, f) for skel, f in holes.items() if len(f) >= 2
]  # ≥2 fillers = real quotient
templates.sort(reverse=True)

print(
    f"=== quotiented-Π apex of «{PHRASE}» ({len(members)} members, {len(phrases)} recurring phrases) ==="
)
print("templates (Π skeleton · ⟨Σ hole = quotiented residue⟩):")
for nf, skel, f in templates[:18]:
    sk = " ".join("⟨" + "|".join(sorted(f)) + "⟩" if w == "⟨⟩" else w for w in skel)
    print(f"  {sk}")
if not templates:
    print("  (no phrase shares a skeleton-with-one-hole — the cluster's commonality is lexical,")
    print(
        "   not sequential: the apex is genuinely a Σ at the phrase level, a Π only at the token level)"
    )
print(
    f"\nfor contrast, the Σ (flat phrase enumeration): {', '.join(' '.join(p) for p in list(phrases)[:12])}"
)
