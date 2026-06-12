"""
swp-carrier-parsing-pilot.py — T-series pilot: the carrier as a parse-weight
semiring (candidate claim SWP).

Setup: CKY over the maximally ambiguous CNF grammar S -> S S | 'a', input
'aaaa' (5 binary derivations = Catalan(3)). One chart computation, pluggable
semiring — Goodman's semiring-parsing frame. Checks:

1. COUNTING SHADOW: carrier weights w_a=(1,0), w_SS=(1,1) elementwise
   product-semiring => root E+ = 5 = derivation count. The mass axis
   carries the multiplicity the SPPF packs.
2. PROBABILITY = the no-conflict section: normalized rule weights on the
   positive rail only (E- = 0) => root E+ = inside probability exactly
   (5 p^3 q^4). Probabilistic parsing is a SECTION of carrier parsing.
3. VITERBI = an idempotent pinning: (max, x) at the root = best single
   derivation; the multiplicity 5 is unrecoverable from the Viterbi value
   — argmax is pruning, the forced disambiguation.
4. CONFLATION WITNESS: two lexicon weightings with equal G-shadow
   (E+/E-) at the root but different masses — the ratio-quotient cannot
   see evidence volume at the parse level either.
"""
from functools import lru_cache
import math

N = 4  # 'aaaa'; derivations = Catalan(3) = 5

def cky(w_a, w_SS, plus, times):
    ch = {}
    for i in range(N): ch[(i, i+1)] = w_a
    for span in range(2, N+1):
        for i in range(0, N-span+1):
            j = i+span; acc = None
            for k in range(i+1, j):
                term = times(times(ch[(i,k)], ch[(k,j)]), w_SS)
                acc = term if acc is None else plus(acc, term)
            ch[(i,j)] = acc
    return ch[(0,N)]

# carrier: product semiring on pairs
padd = lambda a,b:(a[0]+b[0], a[1]+b[1]); pmul = lambda a,b:(a[0]*b[0], a[1]*b[1])

root_count = cky((1.0,0.0),(1.0,1.0),padd,pmul)
print(f"1. counting shadow: root = {root_count}; E+ == Catalan(3) == 5: {abs(root_count[0]-5)<1e-9}")

p, q = 0.4, 0.6  # P(S->SS), P(S->a): locally normalized
root_prob = cky((q,0.0),(p,0.0),padd,pmul)
inside = 5 * p**3 * q**4
print(f"2. probability section: root E+ = {root_prob[0]:.10f}; inside = 5 p^3 q^4 = {inside:.10f}; equal: {abs(root_prob[0]-inside)<1e-12}; E- = {root_prob[1]} (no-conflict rail)")

vit = cky(q, p, max, lambda a,b: a*b)
print(f"3. Viterbi pinning: root = {vit:.10f} = p^3 q^4 = {p**3*q**4:.10f}: {abs(vit-p**3*q**4)<1e-12}; multiplicity 5 UNRECOVERABLE from it (idempotent plus)")

rA = cky((2.0,1.0),(1.0,1.0),padd,pmul)
rB = cky((4.0,2.0),(1.0,1.0),padd,pmul)
GA, GB = rA[0]/rA[1], rB[0]/rB[1]
print(f"4. conflation witness: lexicon (2,1) -> root {rA}, G = {GA}; lexicon (4,2) -> root {rB}, G = {GB};")
print(f"   equal G-shadow: {abs(GA-GB)<1e-9}; masses differ: {abs(sum(rA)-sum(rB))>1}  => the ratio-quotient cannot see evidence volume at the parse level")
