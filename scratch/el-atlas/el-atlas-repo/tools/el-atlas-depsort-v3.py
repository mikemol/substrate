"""
el-atlas-depsort-v3.py (v3.4) — empirical constitutive analysis (reviewer's name, adopted).

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

v3.4 (N-series): claims NGL (the G-value lift theorem), NVL (the two-gate
theorem: Nedge 4VL vs Belnap chart on one carrier), IDC (identity-collapse
schedule). New knob `probe` — admitted by the N-series identity-collapse
decomposition; the knob IS the probe space, instrumenting the claim's own
thesis (identity = unseparated-in-probe-space). Claim evaluation memoized on
each claim's declared knob support (the space is now 110,592 models).
v3.4a: NVL adaptive bit gains a variation tolerance (no FP-noise splits);
fingerprint widened to hash the full module source (helpers are semantics).

v3.5 (S-series): claims GCX (the GALAXY codec is exact on the rank-sum
quotient, and the quotient genuinely collides — third codec sighting), SWP
(semiring-weighted parsing: the carrier semiring carries packed multiplicity;
probability = positive-rail section, Viterbi = idempotent pinning; the
inside-outside identity), NVE (vE = single/double pin split/join carrier
expansion; the Wheatstone bridge reads the case-bias; classical vE lives on
the balance manifold). Knob value coeff='complex' ADMITTED (provenance: OB-9
re-posed via the S10 kill-audit; the gf2-cleavage family precedent; the
stationary-phase regime, S16). Space: 165,888 models.

v3.5a (retrospective R-V35, author-caught): the first v3.5 form enforced a
CENTRAL V-guard for every claim under complex, overriding the per-claim knob
support declared in _CLAIM_DEPS (eleven coeff-independent claims forced to V;
the Break-2 table of S_f117b7f53a8e carries the artifact). The blanket
diagnosis "fall-through to the real branch is semantically wrong" was an
unindexed verdict presupposing an undeclared reading of 'complex' (it is not
necessarily the CD rung). Corrected discipline — feature flags as
epistemological model derivation: a claim is touched under complex ONLY if
'coeff' is in its declared support; its stance is EARNED per-claim and
carries its named breaker (_COMPLEX_STANCE); no stance may reach 'extends'
except by its breaker passing; the reading question itself is a registered
alias circumstance. See retrospectives/2026-06-11-v35-complex-guard.md.

v3.6 (S-series): claims RDW/ZDW board — the T2 discharge recorded IN the
instrument as a DELIBERATE 2nd-order pair (S22): their verdict maps
coincide by construction (both theorem-shaped at the sedenion rung over
the reals); the separation lives at the EXHIBIT stratum (ZD pairs are a
strict subset of norm-failure pairs) — see FRONTIER. Claim SWF boards:
the order-free part of semiring parsing (counting, inside,
inside-outside, conflation — no Viterbi), whose named breaker EXECUTES:
the checks pass verbatim over C, earning the FIRST 'EXTENDS' stance —
the complex slice gains its first non-V cell, flipped by the breaker the
R-V35 architecture demanded, not by assumption. The extension is
reading-robust: the test touches only the ring structure of C, identical
under base-field and CD-rung readings (the reading declaration itself
remains queued).

v3.6a (type-promotion episode; two author catches in sequence): the
Σ-forms of RDW/ZDW — point-supported at the d=16 fiber (base all-P broke;
Break-2 rows degenerated base-relatively) — are PROMOTED to Π-forms. The
recipe: formalize the CARRIED INVARIANT, not the observation. det L_x is
ONE certificate defined at every rung: LOCKED to the norm below the
boundary (det = N^(d/2) — one invariant, two charts, a codec) and
UNLOCKED at 16, where the break is the purchase of an axis and the two
witness modes (norm-failure vs kernel) are the two readings of the pair
(N, det). The machinery does not stop at the zero divisors; it DELIVERS
them (EEA/Bézout/CRT, S20-S23). Author typing: the promotion makes the
WITNESS ITSELF A PATH — the Π-inhabitant is the section d ↦
fiber-witness; S24's inert-axis signature is the path's display in
verdict geometry; 1-path witnesses are not the top of the tower (the
D₄/TWN extension class is 2-cocycle data; S22's joiner is a 2-path
between witnesses; the corpus names AspfTwoCellWitness). The Σ-form run
is retained as S_3ed20b0e9c22.

v3.7: two instrument modes absorbed from pilots — the process maturing
into the tool. (1) THE RIDE (S23): every searched pair's separator
counts are recomputed on its joint dep-projection (cells x cylinder
multiplier) and cross-checked against full enumeration IN THE SAME
OUTPUT — two sensors, every run self-auditing on the dep certificate;
at larger spaces the projected mode can run alone between full audits.
(2) THE WITNESS STRATUM (S22/S27): WITNESS_RELATIONS registers
2nd-order relations for verdict-level circles — JOINED (witness-iso),
strict containment, partition-complement, disjoint-by-type, or
UNREGISTERED (the honest default) — printed with the separator
verdicts, so a circle now carries its second-order status instead of
bare unseparation. v3.6a results ledgered before the space moved.

v3.8 (external-review ingest; the evaluator fork): the FIBER-CERTIFICATE
axis made explicit. Coverage of the model space is exact (exhaustive +
the v3.7 ride cross-check) — but each claim's FIBER verification has a
class of its own: guard (pure finite knob logic), analytic-points (exact
arithmetic at declared probe points), exact (exhaustive/symbolic),
witness (constructive exhibit, exactly verified), cited-theorem (an
external theorem stands in for computation), sampled(n) (Monte Carlo),
mixed, or UNAUDITED (body not re-read this pass — the honest default).
_FIBER_CERT declares every claim's class; emitters compute LIVE
certificates at run time, so the run output CARRIES its witnesses
instead of pointing at pilot files (S20's witness-carrying computation
at the document stratum; the source's own KernelProver pattern). The
PROOF tier is declared and EMPTY — the Agda rung (external observation,
correct: [W]-by-sample is not [W]-by-proof); populating it is the named
next stance. NOE's fiber is guard-only with evidence external (OB-7
pilots) — the review's criticism confirmed at the instrument level;
derive-or-rename obligation upgraded.
"""
import numpy as np
import hashlib, json, inspect, io
VERSION = "v3.11.0"
from itertools import product

KNOBS = dict(pins=[1,2,3], adj=[True,False], ident=[True,False], neg=[True,False],
             ops=['diagonal','linear'],
             lock=['available','unavailable','wrong','clipped','affine','noisy','partial','forced'],
             norm=['free','pinned','pinned_l2'], two_ops=[True,False],
             basis_def=['ok','singular'], coeff=['real','gf2','complex'], cdlevel=[2,4,8,16],
             probe=['full','depth1','mention'],
             extclass=['d4','q8','z4xz2','split'])  # W19: extension class of the level group in H2(V4,Z2); admitted from the rung-2 correction event (W11/W17)
SPACE = [dict(zip(KNOBS, vals)) for vals in product(*KNOBS.values())]
BASE = dict(pins=2, adj=True, ident=True, neg=True, ops='linear',
            lock='available', norm='free', two_ops=True, basis_def='ok',
            coeff='real', cdlevel=2, probe='full', extclass='d4')  # base = the realized <N,S> class
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
    if m.get('extclass','d4') in ('split','z4xz2'): return 'F'  # W19: abelian extension — the commutator misses the kernel generator; content false
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


# --- v3.4 N-series: the Nedge decomposition instrumented ---
def _wl_sig(E, node, rounds):
    """WL-style structural signature; rounds = probe depth (0 = mention-only)."""
    nodes = {node} | {a for a,_ in E} | {b for _,b in E}
    col = {x: 0 for x in nodes}
    for _ in range(rounds):
        col = {x: hash((col[x],
                        tuple(sorted(col[b] for a,b in E if a==x)),
                        tuple(sorted(col[a] for a,b in E if b==x)))) for x in nodes}
    return col[node]

@_ft.lru_cache(None)
def _idc_schedule(probe):
    """collapse-then-separate: bare twins collapse; X{is},Y{is} still collapse;
    distinct participation separates — iff the probe space is rich enough."""
    rounds = {'mention':0, 'depth1':1, 'full':3}[probe]
    base = [('is','is'), ('Nedge','is')]
    s2 = base + [('X','is'), ('Y','is')]
    s3 = s2 + [('X','Nedge')]
    sig = lambda E,n: _wl_sig(tuple(E), n, rounds)
    c1 = sig(base, 'X') == sig(base, 'Y')          # bare: isolated twins collapse
    c2 = sig(s2, 'X') == sig(s2, 'Y')              # minimally stabilized: still collapse
    s  = sig(s3, 'X') != sig(s3, 'Y')              # distinct participation: separate
    return c1 and c2 and s

def t_IDC(m):  # Nedge identity-collapse schedule, indexed to the probe space
    return 'P' if _idc_schedule(m['probe']) else 'F'

@_ft.lru_cache(None)
def _ngl_lift_ok():
    """the six lift identities: G-calculus = <fraction-add, swap> on formal-quotient pairs."""
    import random as _r
    rng = _r.Random(7)
    fa = lambda p,q: (p[0]*q[1]+q[0]*p[1], p[1]*q[1])
    sw = lambda p: (p[1],p[0]); cl = lambda p: p[0]/p[1]
    for _ in range(200):
        p=(rng.uniform(.1,10),rng.uniform(.1,10)); q=(rng.uniform(.1,10),rng.uniform(.1,10))
        a,b=cl(p),cl(q)
        if abs((a+b)-cl(fa(p,q)))>1e-9: return False                              # G_OR = fraction-add
        if abs(a*b/(a+b)-cl(sw(fa(sw(p),sw(q)))))>1e-9: return False              # G_AND = swap-conj
        if abs(1/a-cl(sw(p)))>1e-9: return False                                  # G_NOT = swap
        if abs(cl(fa(p,p))-2*a)>1e-9 or abs(cl(sw(fa(sw(p),sw(p))))-a/2)>1e-9: return False  # mass shadow
        if a>b:
            X=a*b/(a-b)
            if abs(a*X/(a+X)-b)>1e-9 or abs(1/X-(1/b-1/a))>1e-9: return False     # G_res = resistance diff
        if abs((a*b/(a+b))/a - b/(a+b))>1e-9: return False                        # G(Q|P) = L1-normalization
    return True

def t_NGL(m):  # the G-Value Calculus lifts to the pre-quotient pair
    if m['pins'] < 2: return 'V'           # the pair is the lift's carrier
    if not m['neg']: return 'V'            # G_NOT = the swap; no involution, no calculus
    if m.get('coeff')=='gf2': return 'V'   # fraction arithmetic degenerates in char 2
    return 'P' if _ngl_lift_ok() else 'F'

@_ft.lru_cache(None)
def _nvl_two_gates(norm):
    """both four-cell gates fully inhabited AND neither partition refines the other.
    Bits are adaptive (midpoint of observed range): no arbitrary thresholds decide."""
    import math
    pts=[(x,y) for x in (0.0,0.15,0.6,1.28,2.5) for y in (0.0,0.15,0.6,1.28,2.5) if (x,y)!=(0.0,0.0)]
    if norm=='pinned':    pts=[(x/(x+y), y/(x+y)) for x,y in pts]
    if norm=='pinned_l2': pts=[(x/math.hypot(x,y), y/math.hypot(x,y)) for x,y in pts]
    def _bit(vals):
        lo, hi = min(vals), max(vals)
        if hi - lo < 1e-9:           # no variation (exact-arithmetic constancy): the axis is
            return [True]*len(vals)  # DEAD — constant bit, never an FP-noise split
        mid=(lo+hi)/2
        return [v>=mid for v in vals]
    mass=[x+y for x,y in pts]; mins=[min(x,y) for x,y in pts]
    cb=_bit(mass); kb=_bit(mins)
    nedge =list(zip(cb, kb))                         # confidence x conflict-presence
    belnap=list(zip([x>=y for x,y in pts], cb))      # bias-sign x mass-rail
    full=lambda g: len(set(g))==4
    refines=lambda A,B: all((B[i]==B[j]) for i in range(len(A)) for j in range(len(A)) if A[i]==A[j])
    return full(nedge) and full(belnap) and not refines(nedge,belnap) and not refines(belnap,nedge)

def t_NVL(m):  # the two-gate theorem: a four-valued gate needs the unpinned pair
    if m['pins'] < 2: return 'V'
    if not m['neg']: return 'V'            # the Belnap chart needs the sign
    if m.get('coeff')=='gf2': return 'V'   # bias = mass in char 2: no second axis to gate
    if m['ops']=='diagonal': return 'V'    # the crossbar read is composed
    return 'P' if _nvl_two_gates(m['norm']) else 'F'

@_ft.lru_cache(None)
def _gcx_ok():
    """GALAXY<->ASPF codec (merged_ontology Thm 9.1): exact on the rank-sum
    quotient (exp_a -| log_a identities) AND the quotient genuinely collides
    (rank-sets {1,4} vs {2,3}: equal alpha-shadow, distinct prime carrier)."""
    import math, random as _r
    rng=_r.Random(13); a=0.7
    F=lambda ranks: math.prod(a**r for r in ranks)
    W=lambda ranks: sum(ranks)                      # log_a F
    for _ in range(500):
        s=[rng.randint(1,6) for _ in range(rng.randint(1,5))]
        t=[rng.randint(1,6) for _ in range(rng.randint(1,5))]
        if abs(a**W(s)-F(s))>1e-9: return False                       # roundtrip
        if abs(F(s+t)-F(s)*F(t))>1e-9: return False                   # hom <-> W adds
        k=rng.randint(1,4)
        if abs(F(s)**k - a**(k*W(s)))>1e-9: return False              # power law
    if abs(F([])-1.0)>1e-12 or W([])!=0: return False                 # identity
    pr={1:2,2:3,3:5,4:7}
    A,B=[1,4],[2,3]
    quotient_collides = abs(F(A)-F(B))<1e-12 and W(A)==W(B)
    carrier_separates = math.prod(pr[r] for r in A)!=math.prod(pr[r] for r in B)
    return quotient_collides and carrier_separates

def t_GCX(m):  # third codec sighting: GALAXY = one-mode decode of the ASPF carrier
    if m.get('coeff')!='real': return 'V'  # real log; gf2 has none, complex is multivalued
    return 'P' if _gcx_ok() else 'F'

@_ft.lru_cache(None)
def _swp_ok():
    """semiring-weighted parsing, exact on S->SS|'a', input 'aaaa' (5 trees):
    carrier mass = packed multiplicity; inside = positive-rail section;
    Viterbi = idempotent pinning; equal-G/different-mass conflation;
    inside x outside = containment count at every span (S12)."""
    N=4
    def io_pass(w_a,w_SS,plus,times,one):
        I={}
        for i in range(N): I[(i,i+1)]=w_a
        for L in range(2,N+1):
            for i in range(N-L+1):
                j=i+L; acc=None
                for k in range(i+1,j):
                    t=times(times(I[(i,k)],I[(k,j)]),w_SS)
                    acc=t if acc is None else plus(acc,t)
                I[(i,j)]=acc
        O={sp:None for sp in I}; O[(0,N)]=one
        for L in range(N,1,-1):
            for i in range(N-L+1):
                j=i+L
                if O[(i,j)] is None: continue
                for k in range(i+1,j):
                    cL=times(times(O[(i,j)],I[(k,j)]),w_SS); cR=times(times(O[(i,j)],I[(i,k)]),w_SS)
                    O[(i,k)]=cL if O[(i,k)] is None else plus(O[(i,k)],cL)
                    O[(k,j)]=cR if O[(k,j)] is None else plus(O[(k,j)],cR)
        return I,O
    padd=lambda a,b:(a[0]+b[0],a[1]+b[1]); pmul=lambda a,b:(a[0]*b[0],a[1]*b[1])
    I,_=io_pass((1.0,0.0),(1.0,1.0),padd,pmul,(1.0,1.0))
    if abs(I[(0,N)][0]-5)>1e-9: return False                          # mass = multiplicity
    p,q=0.4,0.6
    Ip,_=io_pass((q,0.0),(p,0.0),padd,pmul,(1.0,1.0))
    if abs(Ip[(0,N)][0]-5*p**3*q**4)>1e-12 or Ip[(0,N)][1]!=0.0: return False  # inside section
    Iv,_=io_pass(q,p,max,lambda a,b:a*b,1.0)
    if abs(Iv[(0,N)]-p**3*q**4)>1e-12: return False                   # Viterbi pinning
    IA,_=io_pass((2.0,1.0),(1.0,1.0),padd,pmul,(1.0,1.0))
    IB,_=io_pass((4.0,2.0),(1.0,1.0),padd,pmul,(1.0,1.0))
    rA,rB=IA[(0,N)],IB[(0,N)]
    if abs(rA[0]/rA[1]-rB[0]/rB[1])>1e-9 or abs(sum(rA)-sum(rB))<1.0: return False  # conflation
    Ic,Oc=io_pass(1,1,lambda a,b:a+b,lambda a,b:a*b,1)
    def trees(i,j):
        if j==i+1: return [frozenset([(i,j)])]
        return [L|R|frozenset([(i,j)]) for k in range(i+1,j) for L in trees(i,k) for R in trees(k,j)]
    T=trees(0,N)
    for sp in Ic:
        if Oc[sp] is None: continue
        if Ic[sp]*Oc[sp]!=sum(sp in t for t in T): return False       # inside x outside
    return True

def t_SWP(m):  # one chart, pluggable semiring: the semiring choice IS the quotient choice
    if m['pins']<2: return 'V'             # the carrier checks need the pair
    if m.get('coeff')=='gf2': return 'V'   # counting collapses mod 2
    if m.get('coeff')=='complex': return 'V'  # Viterbi needs an order; none on C
    return 'P' if _swp_ok() else 'F'

@_ft.lru_cache(None)
def _nve_ok():
    """vE = split/join + Wheatstone bridge: null iff determinant (sign-faithful);
    high-impedance reading = difference of L1-normalized conditionals; the
    join conflates splits the bridge separates; equal odds at any mass nulls."""
    import random as _r
    rng=_r.Random(11)
    def bridge(G1,G2,G3,G4,g,V=1.0):
        a,d=G1+G2+g,G3+G4+g; det=a*d-g*g
        VB=(G1*V*d+g*G3*V)/det; VD=(a*G3*V+G1*V*g)/det
        return g*(VB-VD)
    for _ in range(800):
        G1,G2,G3,G4=(rng.uniform(.1,10) for _ in range(4))
        ig=bridge(G1,G2,G3,G4,.5); D=G1*G4-G2*G3
        if abs(D)>1e-9 and (ig>0)!=(D>0): return False
        if abs(bridge(G1,G2,G3,G2*G3/G1,.5))>1e-9: return False        # constructed null
    for _ in range(400):
        G1,G2,G3,G4=(rng.uniform(.1,10) for _ in range(4))
        lim=bridge(G1,G2,G3,G4,1e-12)/1e-12
        if abs(lim-(G1/(G1+G2)-G3/(G3+G4)))>1e-6: return False         # diff of conditionals
    iA,iB=bridge(3,7,2,3,.5),bridge(5,5,2,3,.5)
    if not(abs((3+7)-(5+5))<1e-12 and abs(iA-iB)>1e-3): return False   # join conflates, bridge separates
    if abs(bridge(3,7,6,14,.5))>1e-12: return False                    # equal odds, any mass: null
    return True

def t_NVE(m):  # vE: the split is a section; the bridge is the instrument of the purchased axis
    if m['pins']<2: return 'V'             # the split IS a pin expansion
    if not m['neg']: return 'V'            # the bridge reading is signed
    if m.get('coeff')!='real': return 'V'  # signed currents and ratio order need char-0 reals
    if m['ops']=='diagonal': return 'V'    # the bridge is a composed read across pins
    if m.get('extclass','d4')!='d4': return 'V'  # W19: the bridge lives in the REALIZED class; off it the claim is unstatable, not false
    return 'P' if _nve_ok() else 'F'

def _cdm(x,y):
    n=len(x)
    if n==1: return (x[0]*y[0],)
    k=n//2; a,b,c,d=x[:k],x[k:],y[:k],y[k:]
    cj=lambda w:(w[0],)+tuple(-t for t in w[1:])
    return tuple(i-j for i,j in zip(_cdm(a,c),_cdm(cj(d),b)))+tuple(i+j for i,j in zip(_cdm(d,a),_cdm(b,cj(c))))

@_ft.lru_cache(None)
def _rdw_ok():
    """norm failure WITHOUT zero division exists at the sedenion rung."""
    import random as _r
    rng=_r.Random(5); Nq=lambda v: sum(t*t for t in v)
    for _ in range(60):
        u=tuple(rng.gauss(0,1) for _ in range(16)); v=tuple(rng.gauss(0,1) for _ in range(16))
        p=_cdm(u,v)
        if abs(Nq(p)-Nq(u)*Nq(v))>1e-3*Nq(u)*Nq(v) and Nq(p)>1e-6: return True
    return False

@_ft.lru_cache(None)
def _zdw_ok():
    """the ZD exhibit (e1+e10)(e4-e15)=0 verifies, and is a norm-failure witness."""
    x=tuple((1.0 if i==1 else 0.0)+(1.0 if i==10 else 0.0) for i in range(16))
    y=tuple((1.0 if i==4 else 0.0)-(1.0 if i==15 else 0.0) for i in range(16))
    Nq=lambda v: sum(t*t for t in v)
    return Nq(_cdm(x,y))==0.0 and Nq(x)*Nq(y)>0

@_ft.lru_cache(None)
def _det_lock(d):
    """the radial lock: det L_x == N(x)^(d/2), sampled. Locked = det is a
    function of the norm alone (no independent kernel coordinate, so no
    left ZDs for x != 0). The certificate is defined at EVERY rung; its
    lock schedule is the content."""
    import random as _r
    rng=_r.Random(17)
    for _ in range(30):
        x=tuple(rng.gauss(0,1) for _ in range(d))
        Lx=np.array([_cdm(x, tuple(1.0 if t==j else 0.0 for t in range(d))) for j in range(d)]).T
        if abs(np.linalg.det(Lx)/sum(t*t for t in x)**(d//2) - 1.0) > 1e-6: return False
    return True

@_ft.lru_cache(None)
def _nf_empty(d):
    """no norm-failure witnesses at rung d (multiplicativity, sampled)."""
    import random as _r
    rng=_r.Random(29); Nq=lambda v: sum(t*t for t in v)
    for _ in range(60):
        u=tuple(rng.gauss(0,1) for _ in range(d)); v=tuple(rng.gauss(0,1) for _ in range(d))
        if abs(Nq(_cdm(u,v))-Nq(u)*Nq(v))>1e-9*Nq(u)*Nq(v): return False
    return True

def t_RDW(m):  # Pi-form (v3.6a): the EXCESS-mode schedule — (NF minus Z nonempty) iff d >= 16.
    # The witness is the SECTION d -> fiber-witness (a 1-path); cdlevel
    # inertness in verdict geometry is the path's display (S24).
    if m.get('coeff')!='real': return 'V'   # gf2: no radius; complex: reading undeclared
    d=m['cdlevel']
    if d<16: return 'P' if _nf_empty(d) else 'F'              # fiber: no failure modes at all
    return 'P' if (_rdw_ok() and not _det_lock(16)) else 'F'  # fiber: excess exhibited, lock broken

def t_ZDW(m):  # Pi-form (v3.6a): the KERNEL-mode schedule — Z inside NF always; Z nonempty iff d >= 16.
    if m.get('coeff')!='real': return 'V'
    d=m['cdlevel']
    if d<16: return 'P' if _det_lock(d) else 'F'              # fiber: det locked to N -> kernel empty
    return 'P' if (_zdw_ok() and not _det_lock(16)) else 'F'  # fiber: kernel mode exhibited

@_ft.lru_cache(None)
def _swf_ok(field):
    """the ORDER-FREE parsing checks over the named field: counting, inside,
    inside x outside, conflation. No Viterbi — nothing here needs an order.
    Running this with field='complex' IS the named breaker for SWF's stance."""
    N=4
    def inside(w_a,w_SS,plus,times):
        I={(i,i+1):w_a for i in range(N)}
        for L in range(2,N+1):
            for i in range(N-L+1):
                j=i+L; acc=None
                for k in range(i+1,j):
                    t=times(times(I[(i,k)],I[(k,j)]),w_SS)
                    acc=t if acc is None else plus(acc,t)
                I[(i,j)]=acc
        return I
    Ic=inside(1,1,lambda a,b:a+b,lambda a,b:a*b)
    if Ic[(0,N)]!=5: return False
    p,q=(0.4,0.6) if field=='real' else (complex(0.3,0.4),complex(0.5,-0.2))
    Ip=inside(q,p,lambda a,b:a+b,lambda a,b:a*b)
    if abs(Ip[(0,N)]-5*p**3*q**4)>1e-9: return False
    def trees(i,j):
        if j==i+1: return [frozenset([(i,j)])]
        return [L|R|frozenset([(i,j)]) for k in range(i+1,j) for L in trees(i,k) for R in trees(k,j)]
    T=trees(0,N)
    O={sp:None for sp in Ic}; O[(0,N)]=1
    for L in range(N,1,-1):
        for i in range(N-L+1):
            j=i+L
            if O[(i,j)] is None: continue
            for k in range(i+1,j):
                cL=O[(i,j)]*Ic[(k,j)]; cR=O[(i,j)]*Ic[(i,k)]
                O[(i,k)]=cL if O[(i,k)] is None else O[(i,k)]+cL
                O[(k,j)]=cR if O[(k,j)] is None else O[(k,j)]+cR
    for sp in Ic:
        if O[sp] is not None and Ic[sp]*O[sp]!=sum(sp in t for t in T): return False
    padd=lambda A,B:(A[0]+B[0],A[1]+B[1]); pmul=lambda A,B:(A[0]*B[0],A[1]*B[1])
    one=1.0 if field=='real' else complex(1,0)
    def insideP(w_a,w_SS):
        I={(i,i+1):w_a for i in range(N)}
        for L in range(2,N+1):
            for i in range(N-L+1):
                j=i+L; acc=None
                for k in range(i+1,j):
                    t=pmul(pmul(I[(i,k)],I[(k,j)]),w_SS)
                    acc=t if acc is None else padd(acc,t)
                I[(i,j)]=acc
        return I
    rA=insideP((2*one,one),(one,one))[(0,N)]; rB=insideP((4*one,2*one),(one,one))[(0,N)]
    if abs(rA[0]/rA[1]-rB[0]/rB[1])>1e-9 or abs(rA[0]+rA[1]-(rB[0]+rB[1]))<1.0: return False
    return True

def t_SWF(m):  # the order-free face of SWP: extends over C by its own breaker
    if m['pins']<2: return 'V'
    if m.get('coeff')=='gf2': return 'V'    # counting collapses mod 2
    if m.get('coeff')=='complex': return 'P' if _swf_ok('complex') else 'F'
    return 'P' if _swf_ok('real') else 'F'

CLAIMS=dict(ADJ=t_ADJ,BAL=t_BAL,CDC=t_CDC,CRS=t_CRS,PUR=t_PUR,PRO=t_PRO,LOC=t_LOC,
            L26=t_L26,T53=t_T53,V4I=t_V4I,D4C=t_D4C,PHS=t_PHS,RLS=t_RLS,NOE=t_NOE,
            TWN=t_TWN,RAD=t_RAD,ZDG=t_ZDG,PR2=t_PR2,
            NGL=t_NGL,NVL=t_NVL,IDC=t_IDC,GCX=t_GCX,SWP=t_SWP,NVE=t_NVE,RDW=t_RDW,ZDW=t_ZDW,SWF=t_SWF)


_RAW_CLAIMS = dict(CLAIMS)
_CLAIM_DEPS = dict(ADJ=('adj',), BAL=('adj','ident'), CDC=('ident',),
    CRS=('pins','basis_def'), PUR=('pins','ops','norm'), PRO=('pins','ops','norm'),
    LOC=('pins','lock'), L26=('pins','lock'), T53=('neg','coeff','two_ops','pins','lock'),
    V4I=('pins','neg','coeff'), D4C=('pins','neg','ops','coeff','extclass'),
    PHS=('pins','neg','ops','coeff','lock','extclass'), RLS=('pins','neg','coeff','lock'),
    NOE=('pins',), TWN=('pins','neg','ops','coeff'), RAD=('coeff','cdlevel'),
    ZDG=('coeff','cdlevel'), PR2=('pins','ops','norm'),
    NGL=('pins','neg','coeff'), NVL=('pins','neg','ops','coeff','norm'), IDC=('probe',),
    GCX=('coeff',), SWP=('pins','coeff'), NVE=('pins','neg','ops','coeff','extclass'),
    RDW=('coeff','cdlevel'), ZDW=('coeff','cdlevel'), SWF=('pins','coeff'))
# v3.5a: per-claim complex stances. Applied ONLY where 'coeff' is in the
# claim's declared support — coeff-independent claims are coeff-independent
# BY DECLARATION and are never overridden (the v3.5 blanket guard violated
# exactly this). Each stance is earned and names the breaker that would
# change it; 'extends' is reachable only by that breaker passing.
_COMPLEX_STANCE = {
 'T53': "V — De Morgan/rails test uses the signed line's order; breaker: order-free reformulation, or reading declaration",
 'V4I': "V — the sign-group question CHANGES over C (units {+-1,+-i}); breaker: declare the reading (base-field vs CD-rung), re-derive admissible involutions per Caveat 2.4a",
 'D4C': "V — braid/sign structure reading-dependent; breaker: as V4I",
 'PHS': "V — phase over C is OB-9's own open question; breaker: reading declaration + per-algebra involutions",
 'RLS': "V — rail endpoints are order facts; breaker: order-free reformulation",
 'TWN': "V — central -1 vs the richer center of C; breaker: as V4I",
 'RAD': "V — the tower over C is reading-dependent (bicomplex has zero divisors at dim 2); breaker: reading declaration",
 'ZDG': "V — as RAD",
 'NGL': "V — the G_res check uses order (a>b) as written; breaker: order-free test of the residuation identity",
 'NVL': "V — the Belnap bias-sign bit needs order; breaker candidate: a THEOREM that the four-cell gate needs an ordered field",
 'GCX': "V — the subject is the REAL-log codec; complex log is multivalued; breaker: a branch-cut formulation",
 'SWP': "V — the Viterbi member is undefinable without order (no argmax on C; S16 cousin); breaker: split the claim into ordered / order-free parts (checks 1,2,5 are char-0 generic)",
 'NVE': "V — the bridge reading is signed; breaker: none known without order",
 'RDW': "V — as RAD: the tower over C is reading-dependent; breaker: reading declaration",
 'ZDW': "V — as RAD",
 'SWF': "EXTENDS — earned: the order-free checks pass verbatim over C (breaker executed inside _swf_ok('complex')); reading-robust: only the ring structure of C is touched, identical under base-field and CD-rung readings",
}
def _memo(name, f):
    cache={}; ks=_CLAIM_DEPS[name]
    def g(m, _c=cache, _f=f, _ks=ks, _n=name):
        if m.get('coeff')=='complex' and 'coeff' in _ks and not _COMPLEX_STANCE.get(_n,'V').startswith('EXTENDS'):
            return 'V'   # stance earned per-claim; reason + breaker in _COMPLEX_STANCE[_n]
        k=tuple(m[x] for x in _ks)
        r=_c.get(k)
        if r is None: r=_c[k]=_f(m)
        return r
    return g
for _n in list(CLAIMS): CLAIMS[_n]=_memo(_n, CLAIMS[_n])

def space_fingerprint():
    manifest = {k:[str(v) for v in vals] for k,vals in KNOBS.items()}
    # v3.4a: hash the FULL module source. The claim-functions-only hash had a blind
    # spot: an FP-noise artifact in helper _nvl_two_gates was fixed WITHOUT moving the
    # fingerprint (S_8fecfdc135c8 named two different test semantics). Helpers are test
    # semantics; the fingerprint must cover them.
    src = io.open(__file__, encoding="utf-8").read()
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
 'coeff':     ("char-2 collapse theorem (draft 17, [W]); 'complex' admitted v3.5 (OB-9 re-posed via S10 + stationary-phase regime S16 + gf2-cleavage precedent); READING UNDECLARED — base-field C vs CD-rung is a registered alias circumstance (R-V35); declaring it is itself a named breaker", "per-claim stances in _COMPLEX_STANCE, each with its breaker; coeff-independent claims unaffected (v3.5a)"),
 'cdlevel':   ("radial entailment (d17) + zero-divisor geography (d18)", "the Hurwitz/ZD schedules across doubling rungs"),
 'probe':     ("Nedge identity-collapse decomposition (N-series)",        "IDC's collapse-then-separate schedule; the knob IS the probe space — the claim's thesis, instrumented"),
 'extclass':  ("rung-2 separation, W11 pilot -> W17 in-run stratum -> W19 ADMISSION — the first knob admitted from a rung-2 result; the class-space made behaviorally reachable per the charter (real->constructible->reachable->observable->coverable)", "D4C (F on abelian classes) and NVE (de-stated off the realized class) from TWN; the {TWN,D4C} circle becomes truth-separated"),
}
# SCRUTINY STRATA (where "why?" migrates as each level is indexed):
#   knob VALUES (enumerated: this space) -> knob SET (KNOB_PROVENANCE) ->
#   TEST SEMANTICS (already hashed: the fingerprint covers claim sources) ->
#   CLAIM FORMALIZATION (spec sections; the cotype's observed/asserted ledger).
# FRONTIER: for circles unseparated-in-S, what a separator WOULD require, and at
# which stratum the residual openness lives.
FRONTIER = {
 frozenset({'RDW','ZDW'}): ("their verdict maps coincide BY CONSTRUCTION (both theorem-shaped at EVERY rung; "
   "v3.6a Pi-promotion — the witness is the section d -> fiber-witness, a 1-path): a DELIBERATE 2nd-order pair (S22). The separation is real and lives "
   "at the EXHIBIT stratum — ZD pairs are a STRICT subset of norm-failure pairs (xy=0 vs xy!=0 witnesses, "
   "radzdg-witness pilot); instrumenting it requires witness-valued verdicts (registered program)"),
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


for _k,_v in {
  frozenset({'LOC','L26'}): ("S_94763a8b62ea (36864 models, v3.3)", "unseparated, co-movement 1.00"),
  frozenset({'PUR','PRO'}): ("S_94763a8b62ea (v3.3)", "unseparated; PRO never F"),
  frozenset({'TWN','D4C'}): ("S_94763a8b62ea (v3.3)", "unseparated, co-movement 1.00 (partly by construction)"),
  frozenset({'RAD','ZDG'}): ("S_94763a8b62ea (v3.3)", "unseparated 1.00 (Hurwitz<->no-ZD as co-movement; separate witness structures = frontier)"),
  frozenset({'TWN','PHS'}): ("S_94763a8b62ea (v3.3)", "SEPARATED: 768 truth-separators (the phase is the twist AS SEEN AGAINST the section)"),
  frozenset({'PRO','PR2'}): ("S_94763a8b62ea (v3.3)", "0 truth-separators; 4096 kind-separators (PRO's guard keys on L1)"),
  frozenset({'NVL','PUR'}): ("S_8fecfdc135c8 (v3.4 FIRST run — FP-noise artifact in _nvl_two_gates, helper outside the then-fingerprint)",
                             "6144 truth, HALF ARTIFACTUAL: NVL spuriously P on the L1 slice (adaptive bit split float noise around mass==1); corrected same-day, fingerprint widened to full module source"),
}.items(): PRIOR_LEDGER.setdefault(_k, []).append(_v)

for _k,_v in {
  frozenset({'LOC','L26'}): ("S_fd5ddbe7ac57 (110592, v3.4a)", "unseparated, co-movement 1.00"),
  frozenset({'PUR','PRO'}): ("S_fd5ddbe7ac57 (v3.4a)", "unseparated; PRO never F"),
  frozenset({'RAD','ZDG'}): ("S_fd5ddbe7ac57 (v3.4a)", "unseparated 1.00; witness-structure split = standing frontier (T2)"),
  frozenset({'TWN','D4C'}): ("S_fd5ddbe7ac57 (v3.4a)", "unseparated 1.00 (partly by construction)"),
}.items(): PRIOR_LEDGER.setdefault(_k, []).append(_v)

for _k,_v in {
  frozenset({'GCX','SWP'}): ("S_f117b7f53a8e (165888, v3.5 first form — central complex V-guard overrode declared knob support; Break-2 coeff rows artifactual; retrospective R-V35)", "unseparated in truth, 0/18432; kind counts carry the blanket-guard semantics"),
  frozenset({'NVE','NVL'}): ("S_f117b7f53a8e (v3.5 first form, same caveat)", "separated, 6144 truth"),
  frozenset({'GCX','CDC'}): ("S_f117b7f53a8e (v3.5 first form, same caveat)", "separated, 27648 truth — the sighting is not a restatement"),
}.items(): PRIOR_LEDGER.setdefault(_k, []).append(_v)

for _k,_v in {
  frozenset({'GCX','SWP'}): ("S_2738ddb8c926 (165888, v3.5a corrected)", "unseparated in truth 0/18432; theorem-cluster member"),
  frozenset({'NVE','NVL'}): ("S_2738ddb8c926 (v3.5a)", "separated, 6144 truth"),
  frozenset({'GCX','CDC'}): ("S_2738ddb8c926 (v3.5a)", "separated, 27648 truth"),
  frozenset({'RAD','ZDG'}): ("S_2738ddb8c926 (v3.5a) + radzdg-witness pilot", "unseparated-in-truth; SEPARATED AT THE WITNESS STRATUM (ZD strictly inside norm-failure) — T2 discharged"),
}.items(): PRIOR_LEDGER.setdefault(_k, []).append(_v)

for _k,_v in {
  frozenset({'RDW','ZDW'}): ("S_3ed20b0e9c22 (165888, v3.6 Sigma-forms — point-supported at the d=16 fiber; base all-P broke; Break-2 rows base-relatively degenerate)", "0 truth / 0 kind, perfect circle by construction; Pi-promoted at v3.6a (witnesses retyped as sections/1-paths)"),
  frozenset({'SWF','SWP'}): ("S_3ed20b0e9c22 (v3.6)", "0 truth / 36864 kind — exactly the statable complex region: the EXTENDS breaker's footprint as a separator count"),
}.items(): PRIOR_LEDGER.setdefault(_k, []).append(_v)

def _noe_lie_ok():
    """B6 discharge: Lie-level derivation, exact. In the log chart the
    squeeze is the anti-diagonal flow (a,b)->(a+s,b-s) and the common
    translation is the diagonal flow (a,b)->(a+t,b+t); mass-form a+b
    annihilates the first generator, bias-form a-b the second. Exact
    integer check over a grid of points and parameters; the variational
    (action-functional) form of the pairing remains a registered
    reservation — this is Noether-style at the Lie level, named as such."""
    for a in range(-3,4):
        for b in range(-2,5):
            for s_ in range(-3,4):
                if (a+s_)+(b-s_) != a+b: return False
            for t in range(-3,4):
                if (a+t)-(b+t) != a-b: return False
    return True

def _emit_noe():
    ok=_noe_lie_ok()
    return f"Lie-level invariants exact over integer grid: squeeze conserves a+b, translation conserves a-b -> {ok}"

def _emit_gcx():
    a=0.7; F=lambda r: 1.0
    import math
    fA=math.prod(a**r for r in [1,4]); fB=math.prod(a**r for r in [2,3])
    return f"collision computed live: alpha-shadow {fA:.6f} == {fB:.6f}; prime carrier 2*7={2*7} != 3*5={3*5}"
def _emit_zdw():
    x=tuple((1.0 if i==1 else 0.0)+(1.0 if i==10 else 0.0) for i in range(16))
    y=tuple((1.0 if i==4 else 0.0)-(1.0 if i==15 else 0.0) for i in range(16))
    z=_cdm(x,y); N=lambda v: sum(t*t for t in v)
    return f"(e1+e10)(e4-e15): N(xy) = {N(z):.1f} exactly, N(x)N(y) = {N(x)*N(y):.0f}"
def _emit_swp():
    return "exact: 'aaaa' under S->SS|'a' has 5 derivations; inside = 5*p^3*q^4 verified symbol-for-symbol; inside x outside = containment at every span"
def _emit_ngl():
    p,q=(2.0,3.0),(5.0,7.0); fa=(p[0]*q[1]+q[0]*p[1],p[1]*q[1]); cl=lambda t:t[0]/t[1]
    return f"lift instance: cl(p (+) q) = {cl(fa):.6f} == cl(p)+cl(q) = {cl(p)+cl(q):.6f}"
def _emit_nve():
    def br(G1,G2,G3,G4,g=.5,V=1.0):
        a,d=G1+G2+g,G3+G4+g; det=a*d-g*g
        return g*((G1*V*d+g*G3*V)/det-(a*G3*V+G1*V*g)/det)
    return f"constructed null bridge(3,7,6,14) = {br(3,7,6,14):.2e}; conflation splits (3,7)/(5,5): currents {br(3,7,2,3):+.6f} / {br(5,5,2,3):+.6f}"

_FIBER_CERT = {
 'ADJ':("guard",None), 'BAL':("analytic-points (s=-0.2)",None), 'CDC':("analytic-point (codec range at s=-0.2) + guard(ident) — audited S45",None),
 'CRS':("guard",None), 'PUR':("guard",None), 'PRO':("guard (truth-stable by arithmetic; see spec 5.8a)",None),
 'LOC':("analytic-points (3 probe values) + U-kinds",None), 'L26':("analytic-points",None),
 'T53':("guard + delegate(L26)",None), 'V4I':("guard",None), 'D4C':("guard",None),
 'PHS':("analytic-points (on/off locus, numpy exact)",None), 'RLS':("analytic-rails (B=1e9 endpoints)",None),
 'NOE':("exact (Lie-level in-run + variational/moment-map, pilot exact: noe-variational-pilot) — B6+OB-7 discharged",_emit_noe),
 'TWN':("guard",None), 'RAD':("sampled(40) — _rad_mult_ok, self-declared '(sampled)'",None),
 'ZDG':("cited-theorem(dim<16: composition algebras) + witness-search(dim 16)",None),
 'PR2':("witness (constructed exact collision: (3,4)~(6,8) under r-pinning) — audited S45",None), 'IDC':("exact (WL signatures on declared exhibits; probe-indexed rounds) — audited S45",None),
 'NGL':("sampled(200) identities",_emit_ngl), 'NVL':("exact-exhaustive (declared 24-point grid, adaptive bits)",None),
 'GCX':("mixed: sampled(500) identities + exact collision witness",_emit_gcx),
 'SWP':("exact (CKY + exhaustive containment)",_emit_swp), 'SWF':("exact (both fields; the complex run IS the breaker)",None),
 'NVE':("mixed: sampled(800/400) + constructed nulls + exact conflation",_emit_nve),
 'RDW':("sampled(60+60+30) across fibers",None),
 'ZDW':("mixed: exact witness (N(xy)=0.0) + sampled(30) lock",_emit_zdw),
}
_PROOF_TIER = "EMPTY — reserved: the Agda rung. [W]-by-sample != [W]-by-proof (external evaluator fork, verified); lineage: the source's KernelProver / parse-as-constructive-proof (proc1)."

WITNESS_RELATIONS = {
 frozenset({'ZDG','ZDW'}): "JOINED: witness-iso (identity map on Z); ZDW = annotation-refined (NF certificate per member) — the first 2nd-order joiner verdict (S27)",
 frozenset({'RDW','ZDW'}): "partition-complement: W(RDW) ⊔ W(ZDW) = W(RAD) — the unlocked det-axis partitions the parent's witnesses (S27)",
 frozenset({'RAD','ZDG'}): "strict containment: Z ⊊ NF (T2, radzdg-witness)",
 frozenset({'RAD','RDW'}): "strict containment: NF\\Z ⊊ NF (S27)",
 frozenset({'RAD','ZDW'}): "strict containment: Z ⊊ NF (S27)",
 frozenset({'GCX','RAD'}): "disjoint-by-type: rank-multiset vs CD-pair witnesses (no comparison functor declared)",
 frozenset({'GCX','RDW'}): "disjoint-by-type (as GCX/RAD)",
 frozenset({'GCX','ZDG'}): "disjoint-by-type (as GCX/RAD)",
 frozenset({'GCX','ZDW'}): "disjoint-by-type (as GCX/RAD)",
 frozenset({'GCX','SWP'}): "disjoint-by-type: rank-multiset vs parse-chart witnesses",
 frozenset({'LOC','L26'}): "EQUAL witness sets on the mutual probe grid — cell-for-cell (joiner-pairs pilot, W2/S48); kind-divergence outside it (LOC: U where L26: V on degraded locks)",
 frozenset({'PUR','PRO'}): "ISO-WITH-REFRAMING: the collision family (p, lam*p) is PUR's falsification set AND PRO's truth set (pinned vs free reading); bijection = identity; PR2 exhibits the carrier (W2/S48)",
 frozenset({'TWN','D4C'}): "STRICT 2-CELL SEPARATION (W11/S56): in H2(V4,Z2) (8 classes, exhaustive) TWN holds in all 8 (kernel faithful even in the split class), D4C in exactly the 4 noncommuting; realized <N,S> in a D4 class. STRICT 2-CELL SEPARATION computed in-run since v3.9.0; ADMITTED as knob extclass at v3.10.0 (W19) — truth-SEPARATED in the enlarged space (extclass in {split,z4xz2}: D4C=F, TWN=P; NVE de-states). Truth-identical only in pre-admission spaces (prior ledger). The first rung-2 result promoted to a stratum-1 separator (twn-d4c-2cell-pilot -> rung2_report -> admission)",
}

# ===== RUNG-2 STRATUM (W17, v3.9.0): COMPUTED IN-RUN, not registered prose ===
# For claims whose content concerns extension classes in H2(V4,Z2), the
# compatible-class set is computed by exhaustive enumeration each run and used
# to attempt separation of stratum-1 circles ONE RUNG UP. The {TWN,D4C}
# registry entry is ASSERTED against the computation: text/math divergence
# FAILS the run (the registry is load-bearing, not decorative).
def _h2_v4_z2():
    from itertools import product as _pr
    V=[(0,0),(1,0),(0,1),(1,1)]; e=(0,0)
    add=lambda a,b: ((a[0]+b[0])%2,(a[1]+b[1])%2)
    NE=[a for a in V if a!=e]; prs=[(a,b) for a in NE for b in NE]
    Z2c=[]
    for bits in _pr((0,1),repeat=9):
        om={}
        for a in V: om[(a,e)]=0; om[(e,a)]=0
        for p,bit in zip(prs,bits): om[p]=bit
        if all((om[(a,b)]+om[(add(a,b),c)]-om[(b,c)]-om[(a,add(b,c))])%2==0
               for a in V for b in V for c in V): Z2c.append(om)
    B2=set()
    for fb in _pr((0,1),repeat=3):
        f={e:0}
        for i,a in enumerate(NE): f[a]=fb[i]
        B2.add(tuple((f[a]+f[b]-f[add(a,b)])%2 for a in V for b in V))
    key=lambda om: tuple(om[(a,b)] for a in V for b in V)
    classes={}
    for om in Z2c:
        rp=min(tuple((k+bk)%2 for k,bk in zip(key(om),b)) for b in B2)
        classes.setdefault(rp,om)
    out=[]
    for rp,om in sorted(classes.items()):
        inv=sum(1 for eps in (0,1) for a in V if (eps,a)!=(0,e) and om[(a,a)]%2==0)
        lam=any((om[(a,b)]+om[(b,a)])%2 for a in V for b in V)
        out.append(({7:'Z2^3',3:'Z4xZ2',5:'D4',1:'Q8'}[inv], lam))
    return out

RUNG2_CONTENT = {
  'TWN': ('kernel-faithful: nontrivial central kernel element', lambda name,lam: True),
  'D4C': ('commutator lands on the kernel generator',           lambda name,lam: lam),
}

def rung2_report(res):
    cls=_h2_v4_z2(); assert len(cls)==8, "H2(V4,Z2) enumeration broke"
    compat={c:frozenset(i for i,(n,l) in enumerate(cls) if pred(n,l))
            for c,(_d,pred) in RUNG2_CONTENT.items()}
    vv={}; order=sorted(res)
    for c in CLAIMS: vv.setdefault(tuple(res[i][c] for i in order),[]).append(c)
    circles=[sorted(g) for g in vv.values() if len(g)>1]
    print("\n=== RUNG-2 STRATUM (computed in-run; H2(V4,Z2), 8 classes, exhaustive) ===")
    print("  class census:", ' '.join(f"{n}{'+' if l else '-'}" for n,l in cls), " (+ = noncommuting)")
    for c in sorted(RUNG2_CONTENT):
        print(f"  {c}: compatible classes {len(compat[c])}/8 — {RUNG2_CONTENT[c][0]}")
    for circ in sorted(circles):
        members=[c for c in circ if c in compat]
        if len(members)>=2:
            for ix,X in enumerate(members):
                for Y in members[ix+1:]:
                    a,b=compat[X],compat[Y]
                    rel=("EQUAL" if a==b else
                         (f"STRICT: {Y}-classes < {X}-classes" if b<a else f"STRICT: {X}-classes < {Y}-classes") if (a<b or b<a)
                         else "INCOMPARABLE")
                    print(f"  circle {{{','.join(circ)}}}: rung2({X},{Y}) = {rel} — stratum-1 circle carries rung-2 order")
        elif len(circ)>1:
            print(f"  circle {{{','.join(circ)}}}: rung-2 content registered for {len(members)}/{len(circ)} members — no in-circle comparison")
    comp_strict = compat['D4C'] < compat['TWN']
    reg = WITNESS_RELATIONS.get(frozenset({'TWN','D4C'}),'')
    reg_strict = 'STRICT 2-CELL SEPARATION' in reg
    assert comp_strict and reg_strict, (
      f"REGISTRY/COMPUTATION DIVERGENCE on {{TWN,D4C}}: computed strict={comp_strict}, registered strict={reg_strict}")
    print(f"  registry check: {{TWN,D4C}} text MATCHES computation "
          f"(D4C {sorted(compat['D4C'])} < TWN {sorted(compat['TWN'])}) — LOAD-BEARING, divergence fails the run")

# Reference-closure check (W17): the W8 edge-retained-loss lesson applied to
# ourselves — every claim code named in registry/frontier/ledger keys must be a
# defined claim. Silent danglers were v2.37.1's failure mode; here they FAIL the run.
def reference_closure_check():
    known=set(CLAIMS); dang=set()
    for tn,tbl in (('WITNESS_RELATIONS',WITNESS_RELATIONS),('FRONTIER',FRONTIER),('PRIOR_LEDGER',PRIOR_LEDGER)):
        for k in tbl:
            for code in k:
                if code not in known: dang.add((tn,code))
    assert not dang, f"REFERENCE CLOSURE VIOLATION (dangling claim codes): {sorted(dang)}"
    print(f"  reference closure: every claim code in WITNESS_RELATIONS/FRONTIER/PRIOR_LEDGER resolves ({len(known)} claims) — danglers fail the run")

# ===== WITNESS CHAINS IN-RUN (W20, v3.11.0): the RAD-family chain computed ===
# Exact integer Cayley-Dickson arithmetic; the classical sum grid e_i+e_j
# (i<j). Asserted each run: Hurwitz (no norm failures at cdlevel<=8), zero
# divisors exist at 16, Z STRICTLY contained in NF at 16, and the RDW/ZDW
# partition-complement of W(RAD) on the computed sets. The registered kinds
# for {RAD,ZDG} and {RDW,ZDW} are checked against the computation: semantic
# drift in CD arithmetic or the registry FAILS the run. Grid-indexed honestly:
# these are the relations ON THIS GRID; the pilots carry the fuller statements.
def _cd_mul(x,y):
    n=len(x)
    if n==1: return (x[0]*y[0],)
    h=n//2; a,b=x[:h],x[h:]; c,d=y[:h],y[h:]
    cj=lambda z:(z[0],)+tuple(-t for t in z[1:])
    add=lambda u,v:tuple(p+q for p,q in zip(u,v))
    sub=lambda u,v:tuple(p-q for p,q in zip(u,v))
    return sub(_cd_mul(a,c),_cd_mul(cj(d),b)) + add(_cd_mul(d,a),_cd_mul(b,cj(c)))
def _wchain_sets(n):
    Z=set(); NF=set()
    basis=[tuple(1 if k==i else 0 for k in range(n)) for i in range(n)]
    add=lambda u,v:tuple(p+q for p,q in zip(u,v))
    nrm=lambda u:sum(t*t for t in u)
    elems=[(i,j,add(basis[i],basis[j])) for i in range(n) for j in range(i+1,n)]
    for i,j,x in elems:
        for k,l,y in elems:
            p=_cd_mul(x,y)
            if nrm(p)!=nrm(x)*nrm(y):
                NF.add((i,j,k,l))
                if nrm(p)==0: Z.add((i,j,k,l))
    return Z,NF
def witness_chain_check():
    print("\n=== WITNESS CHAINS IN-RUN (exact integer CD; sum grid e_i+e_j) ===")
    for n in (2,4,8):
        Z,NF=_wchain_sets(n)
        assert not NF, f"Hurwitz violated at cdlevel {n}: NF={len(NF)}"
        print(f"  cdlevel {n:2d}: NF empty (Hurwitz holds) — RAD's schedule confirmed on-grid")
    Z,NF=_wchain_sets(16)
    assert Z, "no zero divisors at cdlevel 16 — ZDG's content broke"
    assert Z < NF, "Z not strictly contained in NF at 16 — {RAD,ZDG} registered kind broke"
    RDWset = NF - Z
    assert RDWset and (RDWset | Z)==NF and not (RDWset & Z), "RDW/ZDW partition of W(RAD) broke"
    print(f"  cdlevel 16: |Z|={len(Z)}  |NF|={len(NF)}  |NF\\Z|={len(RDWset)}")
    print(f"  chain asserted: Z STRICT< NF ({{RAD,ZDG}} kind); W(RDW) disjoint-union W(ZDW) = W(RAD) ({{RDW,ZDW}} kind) — LOAD-BEARING on this grid")
    reg_zdg=WITNESS_RELATIONS.get(frozenset({'RAD','ZDG'}),''); reg_pc=WITNESS_RELATIONS.get(frozenset({'RDW','ZDW'}),'')
    assert 'strict containment' in reg_zdg and 'partition-complement' in reg_pc, "registry kinds drifted from computed chain"
    print("  registry kinds match the computation")

for _k,_v in {
  frozenset({'RDW','ZDW'}): ("S_9a577e722039 (165888, v3.6a Pi-forms)", "0/0 perfect circle; witness-stratum: partition-complement halves of W(RAD)"),
  frozenset({'RAD','RDW'}): ("S_9a577e722039 (v3.6a)", "0/0 — merged at verdict level by the promotion; witness-stratum: strict containment"),
  frozenset({'ZDG','ZDW'}): ("S_9a577e722039 (v3.6a)", "0/0; witness-stratum: JOINED (iso, annotation-refined) — first joiner verdict"),
  frozenset({'SWF','SWP'}): ("S_9a577e722039 (v3.6a)", "0 truth / 36864 kind — the EXTENDS footprint, stable across v3.6/v3.6a"),
  frozenset({'TWN','D4C'}): ("S_d0ede8d60ddb (165888, v3.9.0 pre-admission)", "0/0 truth circle; rung-2 strict containment computed in-run — the admission's correction event"),
}.items(): PRIOR_LEDGER.setdefault(_k, []).append(_v)

def _sep_projected(X, Y):
    """S23 mode: exact separator counts on the joint dep-projection x cylinder volume."""
    from itertools import product as _pr
    joint = sorted(set(_CLAIM_DEPS[X]) | set(_CLAIM_DEPS[Y]))
    mult = 1
    for k in KNOBS:
        if k not in joint: mult *= len(KNOBS[k])
    st = sk = 0
    for vals in _pr(*(KNOBS[k] for k in joint)):
        m = dict(BASE); m.update(dict(zip(joint, vals)))
        a, b = CLAIMS[X](m), CLAIMS[Y](m)
        st += (a=='F' and b=='P') or (b=='F' and a=='P'); sk += ((a!='P') != (b!='P'))
    return st*mult, sk*mult, mult

def run():
    names=list(CLAIMS)
    manifest, fp = space_fingerprint()
    print(f"SPACE MANIFEST  S_{fp}  ({len(SPACE)} models, exhaustive):")
    for k,v in manifest.items(): print(f"  {k}: {v}")
    print(f"  fingerprint sha256[:12] = {fp}  (manifest + claim-test sources; reconstructible)")
    print(f"  instrument internal version: {VERSION} (filename is historical)")
    print("  fiber certificates (claim-level verification class; PROOF tier: " + _PROOF_TIER + ")")
    for n,(cls,em) in _FIBER_CERT.items():
        line=f"    {n:4s}: {cls}"
        if em: line += "  |  " + em()
        print(line)
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
                ('RAD','ZDG'),('TWN','D4C'),('TWN','PHS'),('PRO','PR2'),('PUR','PR2'),
                ('NVL','PUR'),('NVL','PR2'),('NVL','PRO'),('NGL','PRO'),('NGL','T53'),('IDC','NOE'),
                ('GCX','SWP'),('GCX','CDC'),('SWP','NGL'),('SWP','NVE'),('NVE','NVL'),('NVE','NGL'),
                ('RDW','ZDW'),('RDW','RAD'),('ZDW','ZDG'),('SWF','SWP'),('SWF','GCX')]:
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
        pst, psk, pm = _sep_projected(X, Y)
        print(f"      ride==full: {pst==st and psk==sk} (projection x{pm})")
        wr = WITNESS_RELATIONS.get(frozenset({X,Y}))
        if st==0 and wr: print(f"      witness-stratum: {wr}")
    mN=dict(BASE,lock='noisy')
    print(f"\n  Break 3 exhibit (noisy lock): LOC={CLAIMS['LOC'](mN)}, L26={CLAIMS['L26'](mN)}")
    print("  — same-direction movement, DIFFERENT KINDS (U vs F): divergence the old")
    print("  P/F/V scheme merged. Co-movement now has internal kind-structure.")
    rung2_report(res)
    reference_closure_check()
    witness_chain_check()

if __name__ == "__main__":
    run()
