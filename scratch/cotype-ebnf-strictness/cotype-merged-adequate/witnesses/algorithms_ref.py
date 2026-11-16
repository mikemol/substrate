# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Reference impls of the remaining algorithmic name-drops in the groundings: Katz centrality (GALAXY),
Bloom filter (CONSTELLATION), EMD-on-S^1 (AURORA/HARMONY), color-refinement/1-WL (the ceiling)."""

# ---------- Katz centrality / von Neumann series (GALAXY) ----------
# HOW IT WORKS: C = sum_{k>=1} alpha^k A^k 1 = ((I-alpha A)^{-1} - I) 1. Each term counts alpha-attenuated
# walks of length k. Converges for alpha < 1/spectral_radius(A). GALAXY's decay-weighted peer count IS this.
def katz(A, alpha, kmax=None):
    n=len(A)
    # iterative (Neumann) form: x_{t+1} = alpha * A x_t + 1, fixed point = (I-alpha A)^{-1} 1
    x=[0.0]*n
    iters = kmax or 200
    for _ in range(iters):
        x=[alpha*sum(A[i][j]*x[j] for j in range(n)) + 1.0 for i in range(n)]
    return x
def katz_series(A, alpha, K):
    # explicit partial sum sum_{k=1..K} alpha^k (A^k 1) -- shows the walk-counting decomposition
    n=len(A); ones=[1.0]*n; Ak=[row[:] for row in A]; total=[0.0]*n; vec=ones
    for k in range(1,K+1):
        vec=[sum(A[i][j]*vec[j] for j in range(n)) for i in range(n)]   # A^k 1
        for i in range(n): total[i]+=alpha**k * vec[i]
    return total

# ---------- Bloom filter (CONSTELLATION) ----------
# HOW IT WORKS: m-bit array, k hash functions; insert sets k bits; query tests them. No false negatives;
# false positives at rate ~ (1 - e^{-kn/m})^k. The "identity hash, m=|vocab|, k=1" degeneration = exact bitmask.
class Bloom:
    def __init__(self, m, k, seeds=None):
        self.m=m; self.k=k; self.bits=[0]*m
        self.seeds=seeds or list(range(k))
    def _h(self, x, seed):
        return (hash((seed,x)) % self.m)
    def add(self, x):
        for s in self.seeds: self.bits[self._h(x,s)]=1
    def __contains__(self, x):
        return all(self.bits[self._h(x,s)] for s in self.seeds)
def bitmask_exact(items, vocab):
    # the degenerate Bloom: m=|vocab|, k=1, identity hash -> exact membership (no false positives)
    idx={t:i for i,t in enumerate(vocab)}; bits=[0]*len(vocab)
    for it in items: bits[idx[it]]=1
    return bits

# ---------- EMD on S^1 (AURORA / HARMONY) ----------
# HOW IT WORKS: for two circular histograms of equal mass, the 1-Wasserstein distance = min over rotations
# of the sum of absolute CDF differences (Werman). The minimizing rotation is AURORA's registration (the
# radius); the minimum value is HARMONY's distance. Decomposed: cumulative diff, then minimize over offset.
def emd_circular(p, q):
    n=len(p); sp=sum(p); sq=sum(q)
    p=[x/sp for x in p]; q=[x/sq for x in q]
    best=None; best_shift=0
    for shift in range(n):
        qs=q[shift:]+q[:shift]
        # 1D EMD on the line = sum of |prefix-sum differences|
        c=0.0; acc=0.0
        for i in range(n):
            acc += p[i]-qs[i]; c += abs(acc)
        if best is None or c<best: best=c; best_shift=shift
    return best, best_shift   # (HARMONY distance, AURORA registration rotation)

# ---------- color refinement / 1-WL (the expressiveness ceiling) ----------
# HOW IT WORKS: start every node same color; repeatedly recolor each node by hashing (its color, sorted
# multiset of neighbor colors); stop at a fixed point. Two graphs 1-WL-equivalent iff same color histogram.
# This is the ceiling GALAXY/ASPF cannot exceed (Yoneda-truncation). ECLIPSE's sort is the multiset canonicalization.
def wl_refine(adj, rounds=None):
    n=len(adj); color=[0]*n
    rounds = rounds or n
    for _ in range(rounds):
        sig=[(color[v], tuple(sorted(color[u] for u in adj[v]))) for v in range(n)]
        # canonicalize signatures -> new colors
        order={s:i for i,s in enumerate(sorted(set(sig)))}
        newc=[order[sig[v]] for v in range(n)]
        if newc==color: break
        color=newc
    return color
def wl_histogram(adj):
    from collections import Counter
    return Counter(wl_refine(adj))
