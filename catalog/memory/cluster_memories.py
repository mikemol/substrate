#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""cluster_memories.py — the MECHANIZER: derive the corpus's core ideas by comparing
CONTENT (not the pressure-written links/types). Refine the mechanism, not a taxonomy.

Refinement log (each a self-similar step under pressure):
  v1 max-df → generic words.   v2 min-df → random-rare.   v3 IDF connected-components
  → over-merged (190/196, no resolution control).   v4 (eliza's pointer: geometrically-
  ORTHOGONAL conceptual directions): LSA — SVD the IDF memory×term matrix; the top-k
  RIGHT singular vectors are k ORTHOGONAL concept axes (the core ideas), memories are
  their projections, k sets resolution. Orthogonality replaces transitive merge.
"""

import os, re, glob
import numpy as np
from collections import Counter

HERE = os.path.dirname(os.path.realpath(__file__))
SKIP = {"MEMORY.md", "ARCHIVE.md", "MEMORY.candidate.md"}
STOP = set(
    "the a an of to in is it as be by or and not for on with that this these those we i so its are was can has had via per no also when then than only into out up down over under most more less each both new one".split()
)


def claim(p):
    s = open(p).read()
    m = re.match(r"^---\n(.*?)\n---", s, re.S)
    d = re.search(r"^description:\s*(.+)$", m.group(1), re.M) if m else None
    return d.group(1).strip().strip('"') if d else ""


def terms(t):
    caps = {w.lower() for w in re.findall(r"\b[A-Z][A-Z-]{2,}\b", t)}
    lows = {w for w in re.findall(r"\b[a-z]{5,}\b", t.lower()) if w not in STOP}
    return caps | lows


files = sorted(
    f for f in glob.glob(HERE + "/**/*.md", recursive=True) if os.path.basename(f) not in SKIP
)
names = [os.path.basename(f)[:-3] for f in files]
T = [terms(claim(f)) for f in files]
df = Counter(w for ts in T for w in ts)
vocab = sorted(w for w, n in df.items() if 3 <= n <= 60)  # distinctive, shared, not boilerplate
vix = {w: j for j, w in enumerate(vocab)}
N, V = len(names), len(vocab)

# IDF-weighted memory×term matrix (rows L2-normalized so a long claim isn't louder)
M = np.zeros((N, V))
for i, ts in enumerate(T):
    for w in ts & set(vocab):
        M[i, vix[w]] = np.log(N / df[w])
M /= np.linalg.norm(M, axis=1, keepdims=True) + 1e-9

K = 16
U, sv, Vt = np.linalg.svd(M, full_matrices=False)
# v5 = CONFORM TO ELIZA (scratch/eliza/11.py), not reimplement a thinner SVD:
#  (1) START AT FIEDLER — drop mode 0, the trivial constant / centroid "all-memories"
#      direction (eliza: fiedler = eigenvectors[:,1], dropping eigvec 0). modes 1..K.
modes = list(range(1, K + 1))
Vk = Vt[modes]  # K × V : the orthogonal Fiedler-onward concept axes
loadM = U[:, modes] * sv[modes]  # N × K : each memory's loading on them
print(f"items: {N}  vocab: {V}  modes: Fiedler..{K} (mode 0 / centroid dropped, eliza convention)")

#  (2) FRAGMENT-GATE (the one genuinely-new fix): a term joins an axis only if that axis
#      DOMINATES it (top loading ≥ MARGIN × 2nd). A term spread across axes is a BRIDGE
#      (cross-cutting, e.g. 'residue'), kept as such — NOT shattered into one axis.
MARGIN = 1.4
axis_vocab = {k: [] for k in range(K)}
bridges = []
for j in range(V):
    col = np.abs(Vk[:, j])
    o = np.argsort(-col)
    if col[o[0]] >= MARGIN * (col[o[1]] if K > 1 else 0):
        axis_vocab[int(o[0])].append((col[o[0]], vocab[j]))
    else:
        bridges.append((col[o[0]], vocab[j]))
for k in axis_vocab:
    axis_vocab[k].sort(reverse=True)
bridges.sort(reverse=True)


def axis_label(k, n):
    return " · ".join(w for _, w in axis_vocab[k][:n]) or "·"


#  (3) SOFT DUAL-MODE membership (eliza's Fiedler+turbulence, banded — not hard argmax):
#      a memory belongs to its top axis, and to its 2nd if comparably loaded (banded).
mem_axes = {k: [] for k in range(K)}
for i in range(N):
    col = np.abs(loadM[i])
    o = np.argsort(-col)
    mem_axes[int(o[0])].append((col[o[0]], names[i], True))
    if col[o[1]] >= 0.6 * col[o[0]]:
        mem_axes[int(o[1])].append((col[o[1]], names[i], False))
for k in mem_axes:
    mem_axes[k].sort(reverse=True)

print("=== Fiedler-onward orthogonal concept axes (label = de-overlapped vocabulary) ===")
for k in range(K):
    ms = mem_axes[k]
    tag = lambda nm, p: nm if p else nm + "˖"
    print(f"\n  axis {k:2} [{len(ms):2}]  {axis_label(k, 8)}")
    print("      " + ", ".join(tag(nm, p) for _, nm, p in ms)[:160])
print(
    f"\n  bridges (cross-cutting, gated out of any single axis, {len(bridges)}): "
    + ", ".join(w for _, w in bridges[:18])
)

# --- project the compact core-idea index ------------------------------------
hooks = {}
for f in files:
    raw = open(f).read()
    mm = re.match(r"^---\n(.*?)\n---", raw, re.S)
    d = re.search(r"^description:\s*(.+)$", mm.group(1), re.M) if mm else None
    h = d.group(1).strip().strip('"') if d else ""
    cut = min([i for i in (h.find(". "), h.find("; ")) if i > 0] + [len(h)])
    hooks[os.path.basename(f)[:-3]] = h[:cut].strip()
lines = [
    f"# MEMORY.md — {K} orthogonal core-idea axes (Fiedler-onward; mechanized cluster_memories.py; full claims in warrants.bib)\n"
]
for k in range(K):
    ms = mem_axes[k]
    if not ms:
        continue
    lines.append(f"\n## axis {k} — {axis_label(k, 10)}")
    lines.append(f"seed: [{ms[0][1]}]({ms[0][1]}.md) — {hooks.get(ms[0][1], '')[:110]}")
    lines.append("members: " + ", ".join(nm + ("" if p else "˖") for _, nm, p in ms))
lines.append(
    f"\n## bridges (cross-cutting, in no single axis): " + ", ".join(w for _, w in bridges)
)
txt = "\n".join(lines) + "\n"
open(os.path.join(HERE, "MEMORY.candidate.md"), "w").write(txt)
print(
    f"\nMEMORY.candidate.md: {len(txt) / 1024:.1f}KB  (˖ = soft 2nd-mode member)  (limit 24.4KB; target 17.1KB)"
)
