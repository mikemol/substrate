"""
pit-zipper-pilot.py — S13: the "product" pun is precise (Pi/Sigma layer
under inside-outside).

1. ZIPPER BIJECTION (categorified S12 check 1): for every span v, the
   pairing tree -> (context, filling) is a bijection onto the FULL
   cartesian product Context(v) x Filling(v) — independence witnessed,
   not just the count identity. This is WHY inside x outside is exact:
   context-freeness = the filling family is constant over contexts.
2. DEPENDENCE BREAKS THE PRODUCT: impose an agreement condition (the
   filling's lean must match the attachment side of v in its context) —
   a context-SENSITIVE constraint. Naive product over-counts (4); the
   dependent sum  Sigma_c |Filling(c)|  gives the true count (2),
   matching brute force. Sigma degenerates to x only when the family is
   constant.
3. PI AS EVOLUTION OF STATE: trajectories of a state-dependent
   transition family Next(s) are counted by the iterated dependent sum
   = the transfer-matrix product (brute-force equality); when Next is
   state-INdependent (constant family), the count degenerates to the
   plain product |Next|^T. The matrix product is the Sigma-bookkeeping;
   the scalar power is its context-free shadow.
"""
def trees(i, j):
    if j == i+1: return [(i, j, None, None)]
    return [(i, j, L, R) for k in range(i+1, j)
            for L in trees(i, k) for R in trees(k, j)]

def spans(t):
    yield (t[0], t[1])
    if t[2]: yield from spans(t[2]); yield from spans(t[3])

def subtree(t, v):
    if (t[0], t[1]) == v: return t
    if t[2] is None: return None
    return subtree(t[2], v) or subtree(t[3], v)

def context(t, v):  # tree with HOLE at v
    if (t[0], t[1]) == v: return 'HOLE'
    if t[2] is None: return t
    return (t[0], t[1], context(t[2], v), context(t[3], v))

ok1 = True
for n in (4, 5):
    T = trees(0, n)
    allspans = sorted({s for t in T for s in spans(t) if s[1]-s[0] >= 2})
    for v in allspans:
        cont = [t for t in T if v in set(spans(t))]
        pairs = {(context(t, v), subtree(t, v)) for t in cont}
        Cs = {p[0] for p in pairs}; Fs = {p[1] for p in pairs}
        ok1 &= (len(pairs) == len(cont)) and (pairs == {(c, f) for c in Cs for f in Fs})
print(f"1. zipper bijection onto the FULL product, every span, n=4 and n=5: {ok1}")

# 2. context-sensitive agreement at v=(1,4), n=5
v = (1, 4); T5 = trees(0, 5)
cont = [t for t in T5 if v in set(spans(t))]
def lean(f): return 'left' if (f[2][1]-f[2][0]) > (f[3][1]-f[3][0]) else 'right'
def side(t, v):
    if t[2] is None: return None
    if (t[2][0], t[2][1]) == v: return 'left'
    if (t[3][0], t[3][1]) == v: return 'right'
    return side(t[2], v) or side(t[3], v)
brute = sum(1 for t in cont if lean(subtree(t, v)) == side(t, v))
Cs = {context(t, v) for t in cont}; Fs = {subtree(t, v) for t in cont}
def attach_side(c, v):  # side of HOLE in context
    if c == 'HOLE' or c[2] is None: return None
    if c[2] == 'HOLE': return 'left'
    if c[3] == 'HOLE': return 'right'
    return attach_side(c[2], v) or attach_side(c[3], v)
dep_sum = sum(sum(1 for f in Fs if lean(f) == attach_side(c, v)) for c in Cs)
naive = len(Cs)*len(Fs)
print(f"2. agreement condition at {v}: naive product = {naive}; dependent sum = {dep_sum}; brute force = {brute}; product over-counts: {naive != brute and dep_sum == brute}")

# 3. evolution of state
M = [[1,1,0],[0,1,1],[1,0,1]]; S = range(3); Tlen = 7
def brute_paths(M, Tlen):
    tot = 0; stack = [(s, 0) for s in S]
    while stack:
        s, d = stack.pop()
        if d == Tlen: tot += 1; continue
        for s2 in S:
            if M[s][s2]: stack.append((s2, d+1))
    return tot
def matpow_total(M, Tlen):
    import copy; A = [[1 if i==j else 0 for j in S] for i in S]
    for _ in range(Tlen):
        A = [[sum(A[i][k]*M[k][j] for k in S) for j in S] for i in S]
    return sum(sum(r) for r in A)
b, m = brute_paths(M, Tlen), matpow_total(M, Tlen)
K = [[1]*3 for _ in S]
const = brute_paths(K, Tlen)
print(f"3. state-dependent: brute {b} == matrix product {m}: {b == m}; constant family: brute {const} == plain product 3*3^T = {3*3**Tlen}: {const == 3*3**Tlen}")
