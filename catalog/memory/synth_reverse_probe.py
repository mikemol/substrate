#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""synth_reverse_probe.py — PROTOTYPE: synthesize a cluster's apex by REVERSE
GROUP ACTION on the mesh-derived gauge.

Forward (Forgetful, lossy): route a memory's distinctive terms through eliza's
S₄ action → it lands in an orbit (its structural class). GAUGE = mesh-derived:
term → its dominant SVD content-mode (modes 1–3 of the IDF memory×term matrix,
the corpus's own orthogonal content axes) → generator s1/s2/s3.

Reverse (Free): the cluster's members CONCENTRATE in an orbit; that orbit's
shortlex-canonical WORD is the section s(orbit) — the apex skeleton. Decode it
through the INVERSE gauge (generator k → mode-k's top terms = what it "means")
→ the concept-axis recipe the members share. That is the computed apex; a thin
render (not done here) would turn the skeleton into prose, witnessed by members.
"""

import os, re, sys
import numpy as np
from collections import Counter

HERE = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, HERE)
import grammar_phrase_lattice as G  # full(), words(), SKIP, sys.path→eliza
from eliza.engine import Engine
from eliza.alphabets import Gen
import glob

GENS = (Gen.s1, Gen.s2, Gen.s3)
CLUSTER_PHRASE = sys.argv[1] if len(sys.argv) > 1 else "never discard residue"

# --- corpus ---------------------------------------------------------------
files = sorted(
    f
    for f in glob.glob(HERE + "/**/*.md", recursive=True)
    if os.path.basename(f) not in G.SKIP and (os.sep + "index" + os.sep) not in f
)
names = [os.path.basename(f)[:-3] for f in files]
toks = [G.words(G.full(f)) for f in files]
text = [" " + " ".join(t) + " " for t in toks]

# --- mesh-derived gauge: term → dominant SVD content-mode → generator -----
from collections import Counter as C

df = C(w for t in toks for w in set(t))
vocab = sorted(w for w, n in df.items() if 3 <= n <= 60)
vix = {w: j for j, w in enumerate(vocab)}
N, V = len(files), len(vocab)
M = np.zeros((N, V))
for i, t in enumerate(toks):
    for w in set(t) & set(vocab):
        M[i, vix[w]] = np.log(N / df[w])
M /= np.linalg.norm(M, axis=1, keepdims=True) + 1e-9
_, _, Vt = np.linalg.svd(M, full_matrices=False)
Vk = Vt[1:4]  # 3 content axes (Fiedler-onward)
gauge = {w: int(np.argmax(np.abs(Vk[:, vix[w]]))) for w in vocab}  # term → mode 0/1/2


def inverse_axis(k, n=8):  # mode k → its top terms (what gen-k means)
    order = np.argsort(-np.abs(Vk[k]))
    return [vocab[j] for j in order[:n]]


def router(ch):  # the mesh-derived gauge
    return GENS[gauge.get(ch, 0)]


# --- the cluster ----------------------------------------------------------
needle = " " + CLUSTER_PHRASE + " "
members = [i for i in range(N) if needle in text[i]]
print(f"=== cluster «{CLUSTER_PHRASE}» — {len(members)} members ===")

# --- FORWARD: route each member's distinctive terms; orbit histogram ------
dom = []
for i in members:
    e = Engine(router=router, vocab_size=V + 64)
    hist = Counter()
    for w in toks[i]:
        if w in gauge:  # walk over DISTINCTIVE terms only
            r = e.step(w)
            hist[r.orbit_to] += 1
    if hist:
        dom.append(hist.most_common(1)[0][0])
conc = Counter(dom)
canon_orbit, hits = conc.most_common(1)[0]
print(
    f"forward routing → members concentrate in orbit: {canon_orbit}  "
    f"({hits}/{len(dom)} = {100 * hits // max(1, len(dom))}%)  full spread: {dict(conc)}"
)

# --- REVERSE: orbit's canonical word → decode against the cluster MEET ------
# eliza-conformant: read the group-invariant ADDRESS (orbit, already computed),
# then decode CONTENT against the cluster's MEET — its shared distinctive vocab,
# which is boilerplate-free BY CONSTRUCTION (the vocab cap df≤60 drops the
# corpus-wide structural words; the meet is the intersection, not a data-mode).
from collections import Counter as C2

cdf = C2(w for i in members for w in set(toks[i]) if w in gauge)  # within-cluster df, vocab only
meet = {w: cdf[w] for w in cdf if cdf[w] >= len(members) * 0.4}  # shared by ≥40% of members
by_gen = {0: [], 1: [], 2: []}
for w in sorted(meet, key=lambda w: -meet[w]):
    by_gen[gauge[w]].append(f"{w}·{meet[w]}")

gen_idx = {"s1": 0, "s2": 1, "s3": 2}
word = canon_orbit.split("·") if canon_orbit != "e" else []
print(f"\n=== reverse group action: ADDRESS = orbit «{canon_orbit}»;  CONTENT = meet ∩ axis ===")
print("apex SKELETON (the shared meet, organized by the canonical word's axes):")
if not word:
    print(f"  e (central): the apex IS the bare shared core → {', '.join(list(meet)[:10])}")
for g in word:
    k = gen_idx[g]
    print(f"  {g} = axis {k}: {', '.join(by_gen[k][:8]) or '(no meet terms on this axis)'}")
print(
    f"\nfull meet (the overclaim ceiling — apex may not exceed): "
    + ", ".join(f"{w}" for w in sorted(meet, key=lambda w: -meet[w]))
)
print("witnesses: " + ", ".join(names[i] for i in members))
