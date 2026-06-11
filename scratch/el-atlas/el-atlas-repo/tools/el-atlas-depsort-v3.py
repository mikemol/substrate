"""
el-atlas-depsort-v3.py (v3.3) — empirical constitutive analysis (reviewer's name, adopted).

FORMAL SEMANTICS (per the second review, adopted verbatim):
  Claim:        C : S -> {P, F, U, V}
  Separator:    exists s in S : C_i(s) = P xor C_j(s) = P   (one moved, one not)
  Intrinsic@S:  forall s in S : C_i, C_j co-move            (no separator in S)
  Dependence:   C_j(break(C_i)) in {F, V}                   (U creates no edges)
  Layer:        condensation depth of the dependence digraph
The criterion is NOT circularity; it is UNSEPARABILITY UNDER DECLARED PERTURBATION:
"resistance to separation as evidence of identity." The framework itself rejects
"circularity alone is sufficient" — {BAL,CDC}, {CRS,NOE}, RLS-vs-(LOC,L26) are the
in-house counterexamples: SCC-coincident, separated in-space.

Taxonomy adopted as code (reviewer's three-way split of "circularity"):
  1. jointly-inhabited (constitutive): mutual support with a base witness — fine.
  2. self-certifying (vicious): P under EVERY model = no intervention reaches
     ground = unconstrained. AUDITED FOR EXPLICITLY; none found.
  3. closure-under-break: the loop breaks coherently under external perturbation
     — measured as co-movement over the exhaustive model space.

Break 1 (randomized breaks): lock generalized to a family
     {available, unavailable, wrong, clipped, affine, noisy, partial, forced}.
Break 2 (orthogonal interventions): knob-sensitivity audit per claim; a claim is
     structurally localized iff only its own mechanism's knobs ever move it.
Break 3 (P/F/U/V): U = observable but undecided; V = not statable. U creates NO
     dependence edges (undecided is not destroyed). Two dependence semantics:
     TRUTH (F only) vs EXPRESSIBILITY (F or V).
Break 4 (meta/adversarial): exhaustive enumeration of all 1536 models; per
     circle, search for ANY separator (one member moved off P, the other P).
     Zero separators over the space = adversarial-complete persistence.

VERDICT-RELATIVITY (v3.1, structural): NO UNINDEXED VERDICTS. "Unseparated" is
a claim; the emitted form is "unseparated-in-S" with S reconstructible: every
run prints a SPACE MANIFEST (knobs + value sets) and a fingerprint (sha256 of
the manifest + claim-test sources). Known spaces where a verdict differs are
carried as a RESIDUE LEDGER alongside the verdict. v3.1 also unions v2's
basis_def knob into the declared space, so the {CRS,NOE} separation is now
in-space, with its witness mutation printed; the v3 (9-knob) verdict is
retained in the ledger under its own index.
"""
import numpy as np
import hashlib, json, inspect
from itertools import product

KNOBS = dict(pins=[1,2,3], adj=[True,False], ident=[True,False], neg=[True,False],
             ops=['diagonal','linear'],
             lock=['available','unavailable','wrong','clipped','affine','noisy','partial','forced'],
             norm=['free','pinned','pinned_l2'], two_ops=[True,False],
             basis_def=['ok','singular'], coeff=['real','gf2'], cdlevel=[2,4,8,16])
SPACE = [dict(zip(KNOBS, vals)) for vals in product(*KNOBS.values())]
BASE = dict(pins=2, adj=True, ident=True, neg=True, ops='linear',
            lock='available', norm='free', two_ops=True, basis_def='ok',
            coeff='real', cdlevel=2)
TOL = 1e-9

def locus(u, lk):
    if lk in ('available','forced'): return (u, -u)
    if lk == 'wrong':   return (u, -2*u)
    if lk == 'affine':  return (u, -u + 0.3)
    if lk == 'noisy':   return (u, -u + 0.05*np.sin(7*u))
    if lk in ('clipped','partial'): return (u, -u)   # domain handled by caller
    return None
def lock_dom(lk, u):
    if lk=='clipped': return abs(u) <= 1.0
    if lk=='partial': return u > 0
    return True

def t_ADJ(m): return 'P' if m['adj'] else 'F'
def t_BAL(m):
    s=-0.2; ids = 1.0 if m['ident'] else 0.0
    if np.sign(s) != np.sign(np.exp(s)-ids): return 'F'
    return 'P' if m['adj'] else 'F'
def t_CDC(m):
    if not m['ident']: return 'F'
    v=np.exp(-0.2)
    return 'P' if (v-1.0 < 0 and v-0.0 > 0) else 'F'
def t_CRS(m):
    if m['pins'] < 2: return 'V'
    return 'F' if m['basis_def']=='singular' else 'P'
def t_PUR(m):
    if m['pins'] < 2: return 'V'
    if m['ops']=='diagonal': return 'V'
    return 'F' if m['norm']=='pinned' else 'P'
def t_PRO(m):
    if m['pins'] < 2 or m['ops']=='diagonal': return 'V'
    if m['norm']=='pinned': return 'V'
    return 'P'   # the conflation under pinning is arithmetic: true wherever statable
def t_LOC(m):
    if m['pins'] < 2: return 'V'
    if m['lock']=='unavailable': return 'V'
    if m['lock']=='partial': return 'U'           # observable on half-domain, undecided globally
    if m['lock']=='noisy':   return 'U'           # within/without tolerance by sample point
    us=[u for u in (-2.0,0.5,1.0) if lock_dom(m['lock'],u)]
    return 'P' if all(abs(sum(locus(u,m['lock'])))<TOL for u in us) else 'F'
def t_L26(m):
    if m['pins'] < 2: return 'V'
    if m['lock']=='unavailable': return 'V'
    if m['lock']=='partial': return 'V'           # negation exits the domain: not statable
    u=0.7 if m['lock']=='clipped' else 1.7
    p=locus(u,m['lock']); q=locus(-u,m['lock'])
    return 'P' if (abs(p[1]-q[0])<TOL and abs(p[0]-q[1])<TOL) else 'F'
def t_T53(m):
    if not m['neg']: return 'V'
    if m.get('coeff')=='gf2': return 'V'   # the signed-chart NOT is unstatable in char 2
    if not m['two_ops']: return 'F'
    r=t_L26(m)
    return r if r in ('V','U') else ('P' if r=='P' else 'F')
def t_V4I(m):
    if m['pins'] < 2 or not m['neg']: return 'V'
    if m.get('coeff')=='gf2': return 'F'   # -1=+1: the four sign maps collapse; no V4
    return 'P'
def t_D4C(m):
    if m['pins'] < 2 or not m['neg']: return 'V'
    if m['ops']=='diagonal': return 'V'
    if m.get('coeff')=='gf2': return 'F'   # NS=SN in char 2: braid trivial
    return 'P'
def t_PHS(m):
    if t_D4C(m)!='P': return 'V'   # includes coeff=gf2: no braid, no phase
    if m['lock'] in ('unavailable','forced'): return 'V'
    if m['lock']=='partial': return 'U'
    if m['lock']=='noisy':   return 'U'
    on=np.array(locus(0.7 if m['lock']=='clipped' else 2.0, m['lock']))
    S=np.array([[0,1],[1,0]]); mid=-np.eye(2); off=np.array([2.0,1.0])
    triv_on = np.allclose(mid@on, S@on)
    return 'P' if (triv_on and not np.allclose(mid@off, S@off)) else 'F'
def t_RLS(m):
    if m['pins'] < 2 or not m['neg']: return 'V'
    if m.get('coeff')=='gf2': return 'F'   # negate=identity: F-rail does not land on B
    if m['lock']=='unavailable': return 'V'
    if m['lock'] in ('clipped','partial'): return 'V'   # no rails to state
    if m['lock']=='noisy': return 'U'                   # rail-scale tolerance undecided
    B=1e9
    F=np.array(locus(-B,m['lock'])); T=np.array(locus(B,m['lock']))
    return 'P' if (np.allclose(F[::-1],T) and (-F[0]>0 and F[1]>0)) else 'F'
def t_NOE(m):
    if m['pins'] < 2: return 'V'
    return 'P'

import functools as _ft

def _cd_mult_real(x, y):
    n=len(x)
    if n==1: return [x[0]*y[0]]
    h=n//2; a,b=x[:h],x[h:]; c,d=y[:h],y[h:]
    def conj(z):
        if len(z)==1: return z
        hh=len(z)//2
        return conj(z[:hh])+[-v for v in z[hh:]]
    ac=_cd_mult_real(a,c); db=_cd_mult_real(conj(d),b)
    da=_cd_mult_real(d,a); bc=_cd_mult_real(b,conj(c))
    return [p-q for p,q in zip(ac,db)]+[p+q for p,q in zip(da,bc)]

@_ft.lru_cache(None)
def _rad_mult_ok(dim):
    """norm multiplicativity N(xy)=N(x)N(y) over R at this CD level (sampled)."""
    rng=np.random.default_rng(dim)
    for _ in range(40):
        x=list(rng.standard_normal(dim)); y=list(rng.standard_normal(dim))
        z=_cd_mult_real(x,y)
        if abs(sum(v*v for v in z) - sum(v*v for v in x)*sum(v*v for v in y)) > 1e-6*max(1,sum(v*v for v in x)*sum(v*v for v in y)):
            return False
    return True

@_ft.lru_cache(None)
def _zd_exists_real(dim):
    """search basis combinations (e_i+e_j)(e_k-e_l)=0 for a real zero divisor."""
    if dim < 16: 
        # exact: composition algebras through dim 8 have no zero divisors
        return False
    basis=lambda i: [1.0 if k==i else 0.0 for k in range(dim)]
    import itertools as _it
    for i,j in _it.combinations(range(1,dim),2):
        x=[a+b for a,b in zip(basis(i),basis(j))]
        for k,l in _it.combinations(range(1,dim),2):
            if {k,l} & {i,j}: continue
            y=[a-b for a,b in zip(basis(k),basis(l))]
            z=_cd_mult_real(x,y)
            if max(abs(v) for v in z) < 1e-9:
                return True
    return False

@_ft.lru_cache(None)
def _zd_exists_gf2(dim):
    if dim < 2: return False
    # (1 + g)^2 = 0 in GF(2)[(Z/2)^n]: e0+e1 squares to zero
    x=[1,1]+[0]*(dim-2)
    out=[0]*dim
    for i in range(dim):
        if x[i]:
            for j in range(dim):
                if x[j]: out[i^j]^=1
    return max(out)==0

def t_TWN(m):  # the twist is a nontrivial central element of the level group
    if m['pins'] < 2 or not m['neg']: return 'V'
    if m['ops']=='diagonal': return 'V'     # the braid needs the cross-read
    return 'F' if m.get('coeff')=='gf2' else 'P'

def t_RAD(m):  # radial schedule: norm multiplicative iff cdlevel <= 8 (Hurwitz)
    if m.get('coeff')=='gf2': return 'V'    # norm degenerates: no radius to schedule
    ok=_rad_mult_ok(m['cdlevel'])
    return 'P' if (ok == (m['cdlevel'] <= 8)) else 'F'

def t_ZDG(m):  # zero-divisor schedule: ZDs exist iff cdlevel >= 16
    if m.get('coeff')=='gf2':
        return 'F'                           # char 2: ZDs at EVERY level >= 2 - schedule violated
    return 'P' if (_zd_exists_real(m['cdlevel']) == (m['cdlevel'] >= 16)) else 'F'

def t_PR2(m):  # the sphere is also a one-mode decode: r-pinning conflates radius
    if m['pins'] < 2: return 'V'
    if m['ops']=='diagonal': return 'V'
    if m['norm']!='free': return 'V'         # cannot witness from inside a pinned model
    import math
    nz=lambda p:(p[0]/math.hypot(*p), p[1]/math.hypot(*p))
    a,b=(3.0,4.0),(6.0,8.0)
    return 'P' if (np.allclose(nz(a),nz(b)) and math.hypot(*a)!=math.hypot(*b)) else 'F'

CLAIMS=dict(ADJ=t_ADJ,BAL=t_BAL,CDC=t_CDC,CRS=t_CRS,PUR=t_PUR,PRO=t_PRO,LOC=t_LOC,
            L26=t_L26,T53=t_T53,V4I=t_V4I,D4C=t_D4C,PHS=t_PHS,RLS=t_RLS,NOE=t_NOE,
            TWN=t_TWN,RAD=t_RAD,ZDG=t_ZDG,PR2=t_PR2)

def space_fingerprint():
    manifest = {k:[str(v) for v in vals] for k,vals in KNOBS.items()}
    src = "".join(inspect.getsource(f) for f in CLAIMS.values())
    h = hashlib.sha256((json.dumps(manifest, sort_keys=True)+src).encode()).hexdigest()[:12]
    return manifest, h

# WHY THIS SPACE: no knob is a-priori. Each was ADMITTED when a distinction proved
# load-bearing in the workstream; knobs are monotonic (never removed). S is the
# accumulated record of distinctions that mattered — its provenance IS the answer.
KNOB_PROVENANCE = {
 'pins':      ("pin-scenario catalog (spec 5.6, draft 14)", "statability of every pair-structure claim vs P1"),
 'adj':       ("codec pair, Lemma 2.5b",                    "BAL's chart-invariance from CDC (directional split)"),
 'ident':     ("codec contract, spec 5.7 (frame anchor)",   "the identity-anchor claims from everything else"),
 'neg':       ("involution/De Morgan requirements",         "statability of V4I, D4C, T53, RLS"),
 'ops':       ("reading-relation ladder, spec 5.6",         "independent-reading vs composed-reading claims"),
 'lock':      ("classical-section family; reviewer Break 1","locus-circle members (clipped isolates RLS; noisy reveals U-kinds)"),
 'norm':      ("prohibition/purchase, spec 5.8a",           "falsifies PUR while de-stating PRO"),
 'two_ops':   ("Theorem 5.3 single-op collapse",            "T53 from the locus circle"),
 'basis_def': ("v2 split of {CRS,NOE}; admitted at v3.1 (indexed-verdict episode)", "CRS from NOE"),
 'coeff':     ("char-2 collapse theorem (draft 17, [W])",                "sign-structure claims (TWN,V4I,D4C,PHS,RLS,T53) from the carrier-codec claims"),
 'cdlevel':   ("radial entailment (d17) + zero-divisor geography (d18)", "the Hurwitz/ZD schedules across doubling rungs"),
}
# SCRUTINY STRATA (where "why?" migrates as each level is indexed):
#   knob VALUES (enumerated: this space) -> knob SET (KNOB_PROVENANCE) ->
#   TEST SEMANTICS (already hashed: the fingerprint covers claim sources) ->
#   CLAIM FORMALIZATION (spec sections; the cotype's observed/asserted ledger).
# FRONTIER: for circles unseparated-in-S, what a separator WOULD require, and at
# which stratum the residual openness lives.
FRONTIER = {
 frozenset({'LOC','L26'}): ("a model with f != -id yet c == 0 on it, or f == -id with "
   "swap != constrained-negation — both excluded by the shared arithmetic of the current "
   "test semantics; residual openness lives at the TEST-FORMALIZATION stratum, not the knob-value stratum"),
 frozenset({'PUR','PRO'}): ("a pinning that fails to conflate equal-d states, or a model "
   "where PRO is statable yet false — excluded by arithmetic; residual openness at the "
   "TEST-FORMALIZATION stratum"),
}
PRIOR_LEDGER = {
  frozenset({'CRS','NOE'}): [("S_v3 (9 knobs, no basis_def)", "unseparated-in-S_v3"),
                              ("S_v2 (characteristic-break basis + basis_def probe)", "separated (basis_def='singular')")],
  frozenset({'BAL','CDC'}):  [("S_v2 (characteristic-break basis)", "separated (adj; identical-frames)")],
  frozenset({'LOC','L26'}):  [("S_666bf26b7779 (3072 models)", "unseparated, co-movement 1.00"),
                              ("S_v3 (9 knobs)", "unseparated")],
  frozenset({'PUR','PRO'}):  [("S_666bf26b7779 (3072 models)", "unseparated, co-movement 1.00; PRO never F (expressibility-intrinsic)")],
}

def run():
    names=list(CLAIMS)
    manifest, fp = space_fingerprint()
    print(f"SPACE MANIFEST  S_{fp}  ({len(SPACE)} models, exhaustive):")
    for k,v in manifest.items(): print(f"  {k}: {v}")
    print(f"  fingerprint sha256[:12] = {fp}  (manifest + claim-test sources; reconstructible)")
    print("  knob provenance (why this space — each knob admitted by a correction event):")
    for k,(origin,seps) in KNOB_PROVENANCE.items():
        print(f"    {k:10s} <- {origin}; separates: {seps}")
    print()
    res={i:{n:CLAIMS[n](m) for n in names} for i,m in enumerate(SPACE)}
    base={n:CLAIMS[n](BASE) for n in names}
    print(f"base all-P: {all(v=='P' for v in base.values())}\n")
    print("=== self-certification audit (P under EVERY model = unconstrained = vicious) ===")
    flagged=[n for n in names if {res[i][n] for i in res}=={'P'}]
    print("  flagged:", flagged if flagged else "none")
    print("  special case PRO:", sorted({res[i]['PRO'] for i in res}),
          "-> never F: a THEOREM (truth-stable), constrained only by statability.\n")
    print("=== Break 2: knob-sensitivity (which knobs ever move each claim off P) ===")
    for n in names:
        sens=set()
        for k,vals in KNOBS.items():
            for v in vals:
                m=dict(BASE); m[k]=v
                if CLAIMS[n](m)!='P': sens.add(k)
        print(f"  {n:4s}: {sorted(sens)}")
    print("  D4C under unrelated breaks (ident=F, adj=F, pins=3):",
          CLAIMS['D4C'](dict(BASE,ident=False)), CLAIMS['D4C'](dict(BASE,adj=False)),
          CLAIMS['D4C'](dict(BASE,pins=3)), "\n")
    print("=== Breaks 1+4: separator search — ALL VERDICTS INDEXED BY S_"+fp+" ===")
    for X,Y in [('LOC','L26'),('PUR','PRO'),('BAL','CDC'),('CRS','NOE'),
                ('RAD','ZDG'),('TWN','D4C'),('TWN','PHS'),('PRO','PR2'),('PUR','PR2')]:
        st=sk=co=either=0; wit=None
        for i in res:
            a,b=res[i][X],res[i][Y]
            ma,mb=(a!='P'),(b!='P')
            either += (ma or mb); co += (ma and mb)
            if (a=='F' and b=='P') or (b=='F' and a=='P'):
                st += 1
                d={k:v for k,v in SPACE[i].items() if BASE.get(k)!=v}
                if wit is None or len(d)<len(wit): wit=d   # minimal witness
            sk += (ma != mb)
        verdict = f"separated-in-S_{fp}" if st else f"unseparated-in-S_{fp}"
        print(f"  SEP({{{X},{Y}}} | S_{fp}) = {st} truth / {sk} any-kind ; "
              f"co-movement {co}/{either} = {co/either:.2f}  -> {verdict}")
        if wit: print(f"      witness mutation: {wit}")
        if st==0 and sk==0 and frozenset({X,Y}) in FRONTIER:
            print(f"      frontier: a separator would require {FRONTIER[frozenset({X,Y})]}")
        for space_id, prior in PRIOR_LEDGER.get(frozenset({X,Y}), []):
            print(f"      ledger: {prior}  @ {space_id}")
    mN=dict(BASE,lock='noisy')
    print(f"\n  Break 3 exhibit (noisy lock): LOC={CLAIMS['LOC'](mN)}, L26={CLAIMS['L26'](mN)}")
    print("  — same-direction movement, DIFFERENT KINDS (U vs F): divergence the old")
    print("  P/F/V scheme merged. Co-movement now has internal kind-structure.")

if __name__ == "__main__":
    run()
