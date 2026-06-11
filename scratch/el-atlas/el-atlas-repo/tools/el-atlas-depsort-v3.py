"""
el-atlas-depsort-v3.py — rigorized per external review (the four counter-breaks).

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

VERDICT-RELATIVITY CAVEAT (load-bearing): "exhaustive" means exhaustive over the
DECLARED knob space. v2's basis_def knob (singular crossbar) separated {CRS,NOE}
and is not in this space, so v3 reports them unseparated. Persistence claims are
forall-over-declared-bases: every verdict carries its space index.
"""
import numpy as np
from itertools import product

KNOBS = dict(pins=[1,2,3], adj=[True,False], ident=[True,False], neg=[True,False],
             ops=['diagonal','linear'],
             lock=['available','unavailable','wrong','clipped','affine','noisy','partial','forced'],
             norm=['free','pinned'], two_ops=[True,False])
SPACE = [dict(zip(KNOBS, vals)) for vals in product(*KNOBS.values())]
BASE = dict(pins=2, adj=True, ident=True, neg=True, ops='linear',
            lock='available', norm='free', two_ops=True)
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
    return 'P'
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
    if not m['two_ops']: return 'F'
    r=t_L26(m)
    return r if r in ('V','U') else ('P' if r=='P' else 'F')
def t_V4I(m):
    if m['pins'] < 2 or not m['neg']: return 'V'
    return 'P'
def t_D4C(m):
    if m['pins'] < 2 or not m['neg']: return 'V'
    if m['ops']=='diagonal': return 'V'
    return 'P'
def t_PHS(m):
    if t_D4C(m)!='P': return 'V'
    if m['lock'] in ('unavailable','forced'): return 'V'
    if m['lock']=='partial': return 'U'
    if m['lock']=='noisy':   return 'U'
    on=np.array(locus(0.7 if m['lock']=='clipped' else 2.0, m['lock']))
    S=np.array([[0,1],[1,0]]); mid=-np.eye(2); off=np.array([2.0,1.0])
    triv_on = np.allclose(mid@on, S@on)
    return 'P' if (triv_on and not np.allclose(mid@off, S@off)) else 'F'
def t_RLS(m):
    if m['pins'] < 2 or not m['neg']: return 'V'
    if m['lock']=='unavailable': return 'V'
    if m['lock'] in ('clipped','partial'): return 'V'   # no rails to state
    if m['lock']=='noisy': return 'U'                   # rail-scale tolerance undecided
    B=1e9
    F=np.array(locus(-B,m['lock'])); T=np.array(locus(B,m['lock']))
    return 'P' if (np.allclose(F[::-1],T) and (-F[0]>0 and F[1]>0)) else 'F'
def t_NOE(m):
    if m['pins'] < 2: return 'V'
    return 'P'

CLAIMS=dict(ADJ=t_ADJ,BAL=t_BAL,CDC=t_CDC,CRS=t_CRS,PUR=t_PUR,PRO=t_PRO,LOC=t_LOC,
            L26=t_L26,T53=t_T53,V4I=t_V4I,D4C=t_D4C,PHS=t_PHS,RLS=t_RLS,NOE=t_NOE)

def run():
    names=list(CLAIMS)
    res={i:{n:CLAIMS[n](m) for n in names} for i,m in enumerate(SPACE)}
    base={n:CLAIMS[n](BASE) for n in names}
    print(f"model space: {len(SPACE)} models (exhaustive). base all-P: {all(v=='P' for v in base.values())}\n")
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
    print("=== Breaks 1+4: exhaustive (adversarial-complete over this space) separator search ===")
    for X,Y in [('LOC','L26'),('PUR','PRO'),('BAL','CDC'),('CRS','NOE')]:
        st=sk=co=either=0
        for i in res:
            a,b=res[i][X],res[i][Y]
            ma,mb=(a!='P'),(b!='P')
            either += (ma or mb); co += (ma and mb)
            st += (a=='F' and b=='P') or (b=='F' and a=='P')
            sk += (ma != mb)
        print(f"  {{{X},{Y}}}: truth-separators={st}  any-kind-separators={sk}  "
              f"co-movement={co}/{either} = {co/either:.2f}")
    mN=dict(BASE,lock='noisy')
    print(f"\n  Break 3 exhibit (noisy lock): LOC={CLAIMS['LOC'](mN)}, L26={CLAIMS['L26'](mN)}")
    print("  — same-direction movement, DIFFERENT KINDS (U vs F): divergence the old")
    print("  P/F/V scheme merged. Co-movement now has internal kind-structure.")

if __name__ == "__main__":
    run()
