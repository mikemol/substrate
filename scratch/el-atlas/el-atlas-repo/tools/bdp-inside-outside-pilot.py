"""
bdp-inside-outside-pilot.py — S12: bidirectionality witness (extends SWP).
Forward (inside) pass alone answers only the ROOT question; per-node
questions require the backward (outside) pass; the answer at a node is
the PRODUCT of both passes. Grammar S->SS|'a', input 'aaaa' (5 trees).

1. IDENTITY: for every span, inside*outside == brute-force count of
   derivations CONTAINING that span (exact, all spans).
2. FORWARD UNDER-DETERMINATION: spans (0,1) and (0,2) have EQUAL inside
   (=1) but different containment totals (5 vs 2) — the forward pass
   alone cannot rank per-node participation.
3. CARRIER VERSION + CONFLATION: on the pair semiring, I*O at each span
   equals the summed full-derivation pair over containing trees; the
   (2,1)/(4,2) lexicons give equal G-shadow at EVERY span with different
   masses — the quotient blindness is pointwise, not just at the root.
"""
N = 4
def enum(i, j):
    if j == i+1: return [frozenset([(i, j)])]
    return [L | R | frozenset([(i, j)]) for k in range(i+1, j)
            for L in enum(i, k) for R in enum(k, j)]
trees = enum(0, N); assert len(trees) == 5
spans = sorted({s for t in trees for s in t}, key=lambda s: (s[1]-s[0], s))
contain = {s: sum(s in t for t in trees) for s in spans}

def inside_outside(w_a, w_SS, plus, times, one):
    I = {}
    for i in range(N): I[(i, i+1)] = w_a
    for L in range(2, N+1):
        for i in range(N-L+1):
            j = i+L; acc = None
            for k in range(i+1, j):
                term = times(times(I[(i, k)], I[(k, j)]), w_SS)
                acc = term if acc is None else plus(acc, term)
            I[(i, j)] = acc
    O = {s: None for s in I}; O[(0, N)] = one
    for L in range(N, 1, -1):
        for i in range(N-L+1):
            j = i+L
            if O[(i, j)] is None: continue
            for k in range(i+1, j):
                cL = times(times(O[(i, j)], I[(k, j)]), w_SS)
                cR = times(times(O[(i, j)], I[(i, k)]), w_SS)
                O[(i, k)] = cL if O[(i, k)] is None else plus(O[(i, k)], cL)
                O[(k, j)] = cR if O[(k, j)] is None else plus(O[(k, j)], cR)
    return I, O

# counting semiring
I, O = inside_outside(1, 1, lambda a,b: a+b, lambda a,b: a*b, 1)
ok1 = all(I[s]*O[s] == contain[s] for s in spans)
print(f"1. inside*outside == containment count at every span: {ok1}")
print(f"2. forward under-determination: I(0,1)={I[(0,1)]} == I(0,2)={I[(0,2)]} but I*O = {I[(0,1)]*O[(0,1)]} vs {I[(0,2)]*O[(0,2)]}")

# carrier (pair product semiring)
padd = lambda a,b:(a[0]+b[0], a[1]+b[1]); pmul = lambda a,b:(a[0]*b[0], a[1]*b[1])
def per_span(w_a):
    Ip, Op = inside_outside(w_a, (1.0,1.0), padd, pmul, (1.0,1.0))
    return {s: pmul(Ip[s], Op[s]) for s in spans}
A, B = per_span((2.0,1.0)), per_span((4.0,2.0))
okG = all(abs(A[s][0]/A[s][1] - B[s][0]/B[s][1]) < 1e-9 for s in spans)
okM = all(sum(B[s]) > sum(A[s]) for s in spans)
# cross-check pair identity against brute force on lexicon A
def full(t, w):
    m = [1.0,1.0]
    for (i,j) in t:
        f = w if j==i+1 else (1.0,1.0)
        m = [m[0]*f[0], m[1]*f[1]]
    return m
okP = all(all(abs(A[s][r] - sum(full(t,(2.0,1.0))[r] for t in trees if s in t)) < 1e-9
              for r in (0,1)) for s in spans)
print(f"3. carrier: I*O == summed pair over containing trees: {okP}; equal G-shadow at EVERY span: {okG}; masses differ at every span: {okM}")
