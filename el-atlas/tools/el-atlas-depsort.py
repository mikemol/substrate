"""
el-atlas-depsort.py — empirical dependency sort over the EL-Atlas claims.

Each claim is an executable (sympy/numeric) test against a mutable model:
  test(model) -> 'P' (pass) | 'F' (fail) | 'V' (vacuous: not statable there)
Each claim has a characteristic BREAK (the minimal mutation disabling its
structure). Then:
  dep(B <- A) := test_B(base)=='P' and test_B(break(A)) in {'F','V'}
  circles     := SCCs of the dep digraph; COHERENT iff all members 'P' in the
                 base model (the base jointly inhabits the cycle — mutual
                 constitution, not vicious regress; vicious = a cycle witnessed
                 only vacuously; none occur here)
  layers      := condensation depth (0 = foundations)
Known artifact: T53 maps an inner 'V' to 'F' under pins=1 (conservative).
"""
import numpy as np, sympy as sp
import functools

BASE = dict(pins=2, adj_ok=True, identity_ok=True, neg_ok=True,
            ops='linear', lock='available', norm='free', two_ops=True)
def M(**kw):
    m = dict(BASE); m.update(kw); return m
BIG = 1e9
def locus_pair(u, lock): return (u, -u) if lock != 'wrong' else (u, -2*u)

def t_ADJ(m):
    u = sp.symbols('u', real=True); y = sp.symbols('y', positive=True)
    if not m['adj_ok']: return 'F'
    return 'P' if (sp.simplify(sp.log(sp.exp(u))-u)==0 and
                   sp.simplify(sp.exp(-sp.log(y))-1/y)==0) else 'F'

def t_BAL(m):
    s = -0.2
    id_semi = 1.0 if m['identity_ok'] else 0.0
    if np.sign(s) != np.sign(np.exp(s)-id_semi): return 'F'
    if not m['adj_ok']: return 'F'
    return 'P'

def t_CDC(m):
    if not m['identity_ok']: return 'F'
    v = np.exp(-0.2)
    return 'P' if (np.sign(v-1.0) < 0 and np.sign(v-0.0) > 0) else 'F'

def t_CRS(m):
    if m['pins'] < 2: return 'V'
    E = np.array([3.0,5.0]); A = np.array([[1,1],[1,-1]])
    return 'P' if np.allclose(np.linalg.solve(A, A@E), E) else 'F'

def t_PUR(m):
    if m['pins'] < 2: return 'V'
    if m['ops'] == 'diagonal': return 'V'
    if m['norm'] == 'pinned': return 'F'
    a, b = (7.0,7.0), (0.1,0.1)
    return 'P' if (a[0]-a[1] == b[0]-b[1] and a[0]+a[1] != b[0]+b[1]) else 'F'

def t_PRO(m):
    if m['pins'] < 2 or m['ops'] == 'diagonal': return 'V'
    if m['norm'] == 'pinned': return 'V'
    nz = lambda p: (p[0]/(p[0]+p[1]), p[1]/(p[0]+p[1]))
    a, b = (7.0,7.0), (0.1,0.1)
    return 'P' if (np.allclose(nz(a), nz(b)) and a[0]+a[1] != b[0]+b[1]) else 'F'

def t_LOC(m):
    if m['pins'] < 2: return 'V'
    if m['lock'] == 'unavailable': return 'V'
    return 'P' if all(abs(p+q) < 1e-12 for p,q in
                      (locus_pair(u, m['lock']) for u in (-2.0,0.5,3.0))) else 'F'

def t_L26(m):
    if m['pins'] < 2: return 'V'
    if m['lock'] == 'unavailable': return 'V'
    u = 1.7; p = locus_pair(u, m['lock'])
    return 'P' if np.allclose((p[1],p[0]), locus_pair(-u, m['lock'])) else 'F'

def t_T53(m):
    if not m['neg_ok']: return 'V'
    a, b = sp.symbols('a b', positive=True)
    collapses = sp.simplify(1/((1/a)*(1/b)) - a*b) == 0
    if not m['two_ops']: return 'F' if collapses else 'P'
    if t_L26(m) != 'P': return 'F'
    return 'P' if collapses else 'F'

def t_V4I(m):
    if m['pins'] < 2 or not m['neg_ok']: return 'V'
    G = [np.diag([a,b]) for a in (1,-1) for b in (1,-1)]
    return 'P' if (all(np.allclose(g@g, np.eye(2)) for g in G) and
                   all(np.allclose(x@y, y@x) for x in G for y in G) and
                   all(any(np.allclose(x@y, z) for z in G) for x in G for y in G)) else 'F'

def t_D4C(m):
    if m['pins'] < 2 or not m['neg_ok']: return 'V'
    if m['ops'] == 'diagonal': return 'V'
    N = np.diag([-1,1]); S = np.array([[0,1],[1,0]])
    comm = N@S@np.linalg.inv(N)@np.linalg.inv(S)
    els = {tuple(np.eye(2).astype(int).ravel())}; fr=[np.eye(2)]
    while fr:
        X = fr.pop()
        for g in (N,S):
            for Pp in (X@g, g@X):
                tt = tuple(Pp.astype(int).ravel())
                if tt not in els: els.add(tt); fr.append(Pp)
    return 'P' if (len(els)==8 and np.allclose(comm, -np.eye(2))) else 'F'

def t_PHS(m):
    if t_D4C(m) != 'P': return 'V'
    if m['lock'] in ('unavailable','forced'): return 'V'
    S = np.array([[0,1],[1,0]]); mid = -np.eye(2)
    on = np.array(locus_pair(2.0, m['lock'])); off = np.array([2.0,1.0])
    return 'P' if (np.allclose(mid@on, S@on) and not np.allclose(mid@off, S@off)) else 'F'

def t_RLS(m):
    if m['pins'] < 2 or not m['neg_ok']: return 'V'
    if m['lock'] == 'unavailable': return 'V'
    F = np.array(locus_pair(-BIG, m['lock'])); T = np.array(locus_pair(BIG, m['lock']))
    return 'P' if (np.allclose(F[::-1], T) and (-F[0] > 0 and F[1] > 0)) else 'F'

def t_NOE(m):
    if m['pins'] < 2: return 'V'
    u = np.array([1.3,0.4]); t = 0.7
    return 'P' if (np.isclose((u+[t,-t]).sum(), u.sum()) and
                   np.isclose((u+[t,t])[0]-(u+[t,t])[1], u[0]-u[1])) else 'F'

CLAIMS = dict(ADJ=t_ADJ, BAL=t_BAL, CDC=t_CDC, CRS=t_CRS, PUR=t_PUR, PRO=t_PRO,
              LOC=t_LOC, L26=t_L26, T53=t_T53, V4I=t_V4I, D4C=t_D4C, PHS=t_PHS,
              RLS=t_RLS, NOE=t_NOE)
BREAKS = dict(ADJ=M(adj_ok=False), BAL=M(identity_ok=False), CDC=M(identity_ok=False),
              CRS=M(pins=1), PUR=M(norm='pinned'), PRO=M(norm='pinned'),
              LOC=M(lock='wrong'), L26=M(lock='wrong'), T53=M(two_ops=False),
              V4I=M(neg_ok=False), D4C=M(ops='diagonal'), PHS=M(lock='forced'),
              RLS=M(lock='wrong'), NOE=M(pins=1))

def run():
    names = list(CLAIMS)
    base = {n: CLAIMS[n](BASE) for n in names}
    print("base:", base, " all P:", all(v=='P' for v in base.values()), "\n")
    dep = {}
    print("matrix (rows B under test; cols A broken; entry = B in break(A)):")
    print("       " + " ".join(f"{a:>4s}" for a in names))
    for b in names:
        row = [CLAIMS[b](BREAKS[a]) for a in names]
        for a, r in zip(names, row): dep[(b,a)] = (base[b]=='P' and r in ('F','V'))
        print(f"  {b:4s} " + " ".join(f"{r:>4s}" for r in row))
    edges = {b:{a for a in names if a!=b and dep[(b,a)]} for b in names}
    def reach(x):
        seen=set(); st=[x]
        while st:
            n=st.pop()
            for nn in edges[n]:
                if nn not in seen: seen.add(nn); st.append(nn)
        return seen
    R = {n: reach(n) for n in names}
    sccs=[]; done=set()
    for n in names:
        if n in done: continue
        c = sorted({n} | {x for x in names if x in R[n] and n in R[x]})
        sccs.append(c); done |= set(c)
    print("\ncircles (coherent iff jointly witnessed in base):")
    for c in sccs:
        if len(c)>1:
            print(f"  {c} -> {'COHERENT' if all(base[x]=='P' for x in c) else 'VICIOUS?'}")
    comp_of = {x:i for i,c in enumerate(sccs) for x in c}
    ce = {i:set() for i in range(len(sccs))}
    for b in names:
        for a in edges[b]:
            if comp_of[b]!=comp_of[a]: ce[comp_of[b]].add(comp_of[a])
    @functools.lru_cache(None)
    def depth(i): return 0 if not ce[i] else 1+max(depth(j) for j in ce[i])
    layers={}
    for i,c in enumerate(sccs): layers.setdefault(depth(i),[]).append(c)
    print("\nlayers (0 = foundations):")
    for d in sorted(layers):
        print(f"  layer {d}: " + "  ".join("{"+",".join(c)+"}" for c in layers[d]))
    indep=[(a,b) for i,a in enumerate(names) for b in names[i+1:]
           if not dep[(a,b)] and not dep[(b,a)]]
    print(f"\nindependent pairs: {len(indep)} of {len(names)*(len(names)-1)//2}")

if __name__ == "__main__":
    run()


# =====================================================================
# BASIS REFINEMENT (v2). An SCC under probe basis B is correct AT B — never
# "fake." The well-posed question is stability under refinement:
#   SPLITS   -> basis-coarseness: a projection coincidence of the coarse probe
#               (members fused only because they ride the same shared structure)
#   PERSISTS -> candidate-INTRINSIC: mutual constitution. A forall-over-bases
#               claim — refutable by the next finer basis, never provable.
#               Intrinsic circles are open-by-design objects (cf. OB-1).
# The probe basis itself composes: a coarse break is the composed meaning of
# finer breaks — the instrument obeys the spec's own differential encoding.
# Verdicts at the current finest basis (see session draft-16+):
#   {CRS, NOE}        SPLITS   (basis_def='singular' moves CRS alone)
#   {LOC, L26, RLS}   SPLITS   (lock='clipped' vacuates RLS alone: the rails are
#                              a compactification fact, detachable from the section)
#   {LOC, L26}        PERSISTS (every locus deformation tried breaks both:
#                              the section and its involution-coincidence are
#                              facets of f = -id)
#   {BAL, CDC}        SPLITS   (adj-break moves BAL alone; identical-frames
#                              vacuates CDC alone)
#   {PUR, PRO}        PERSISTS (co-break under pinning, alt-pinning, and
#                              read-restriction: purchase and prohibition are
#                              one structure)
# =====================================================================
