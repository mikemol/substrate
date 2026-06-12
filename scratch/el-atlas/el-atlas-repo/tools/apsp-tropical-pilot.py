"""
apsp-tropical-pilot.py — S17: geodesics close the loop. APSP is the
tropical (min,+) member of the pinning family; the multiplicity the
tropical pinning discards is recoverable from the hbar-correction of
the dequantization.

1. APSP = TROPICAL MATRIX POWERS: min-plus powers of the weight matrix
   reproduce brute-force shortest distances for all pairs.
2. LAPLACE/MASLOV DEQUANTIZATION: F(h) = -h log Sigma_paths e^{-c/h}
   converges to the geodesic cost as h -> 0 (the positive-weight,
   numerically clean sibling of the oscillatory S16 pilot).
3. THE DISCARDED MASS LIVES IN THE SUBLEADING TERM: two graphs with the
   SAME geodesic distance but different shortest-path multiplicities
   (2 vs 1) are tropically INDISTINGUISHABLE, yet
   k_hat = exp(-(F(h)-min)/h) recovers the multiplicities exactly as
   h -> 0. The tropical pinning's blind spot (idempotent min forgets
   how many) is the leading term of an expansion whose next order IS
   the packed multiplicity.
"""
import math
INF = float('inf')

def tropical_apsp(W):
    n = len(W); D = [row[:] for row in W]
    for _ in range(n-2):
        D = [[min(D[i][k] + W[k][j] for k in range(n)) for j in range(n)] for i in range(n)]
    for i in range(n): D[i][i] = min(D[i][i], 0.0)
    return D

def simple_paths(adj, s, t):
    out = []
    def dfs(v, cost, seen):
        if v == t: out.append(cost); return
        for u, w in adj[v]:
            if u not in seen: dfs(u, cost+w, seen | {u})
    dfs(s, 0.0, {s}); return out

# 1. five-node digraph
edges = [(0,1,2),(0,2,5),(1,2,1),(1,3,4),(2,3,1),(2,4,6),(3,4,1),(0,3,9),(1,4,8)]
n = 5
W = [[0.0 if i==j else INF for j in range(n)] for i in range(n)]
adj = {i: [] for i in range(n)}
for a,b,w in edges: W[a][b] = float(w); adj[a].append((b,float(w)))
D = tropical_apsp(W)
ok1 = True
for i in range(n):
    for j in range(n):
        if i == j: continue
        ps = simple_paths(adj, i, j)
        ok1 &= (D[i][j] == (min(ps) if ps else INF))
print(f"1. tropical powers == brute geodesic distance, all pairs: {ok1}")

# 2-3. diamond graphs: same geodesic (2.0), multiplicities 2 vs 1
gA = {0:[(1,1.0),(2,1.0),(3,5.0)], 1:[(3,1.0)], 2:[(3,1.0)], 3:[]}
gB = {0:[(1,1.0),(2,1.5),(3,5.0)], 1:[(3,1.0)], 2:[(3,1.0)], 3:[]}
cA, cB = simple_paths(gA,0,3), simple_paths(gB,0,3)
mA, mB = min(cA), min(cB)
def F(costs, h): return -h*math.log(sum(math.exp(-c/h) for c in costs))
print(f"2. dequantization (graph A): geodesic = {mA}; F(h) = " +
      ", ".join(f"{h}:{F(cA,h):.4f}" for h in (1.0,0.3,0.1,0.03)) +
      f" -> converges: {abs(F(cA,0.03)-mA) < 0.03}")
kA = [math.exp(-(F(cA,h)-mA)/h) for h in (0.3,0.1,0.03)]
kB = [math.exp(-(F(cB,h)-mB)/h) for h in (0.3,0.1,0.03)]
print(f"3. tropical sees both graphs identically (geodesic {mA} == {mB}: {mA==mB});")
print(f"   k_hat(A) = {[f'{k:.4f}' for k in kA]} -> 2 (two geodesics);  k_hat(B) = {[f'{k:.4f}' for k in kB]} -> 1 (one geodesic)")
print(f"   multiplicity recovered from the hbar-correction: {abs(kA[-1]-2)<0.01 and abs(kB[-1]-1)<0.01}")
