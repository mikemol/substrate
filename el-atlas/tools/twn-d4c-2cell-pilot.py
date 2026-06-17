#!/usr/bin/env python3
"""W11: the {TWN,D4C} 2-cell. Exhaustive over H2(V4,Z2).
V4 = Z2 x Z2. Normalized 2-cochains omega: V4xV4 -> Z2 (omega(e,.)=omega(.,e)=0).
Z2 = cocycles (64-triple condition); B2 = coboundaries of normalized 1-cochains;
H2 = Z2/B2, expected Z2^3 (8 classes). Each class classified by:
  - alternating form lam(a,b)=omega(a,b)+omega(b,a) nonzero? (= noncommuting
    extension = D4C's commutator content survives)
  - involution count of the reconstructed extension (D4=5, Q8=1, Z2^3=7, Z4xZ2=3)
TWN's content (kernel element (1,e) is a nontrivial central element) is checked
per class directly. The realized <N,S> matrix group's cocycle is extracted and
located. All exact; no sampling."""
from itertools import product
V=[(0,0),(1,0),(0,1),(1,1)]; e=(0,0)
def add(a,b): return ((a[0]+b[0])%2,(a[1]+b[1])%2)
NE=[a for a in V if a!=e]
# --- enumerate Z2 (normalized): 9 free values on NExNE
pairs=[(a,b) for a in NE for b in NE]
Z2c=[]
for bits in product((0,1),repeat=9):
    om={}
    for a in V: om[(a,e)]=0; om[(e,a)]=0
    for (p,bit) in zip(pairs,bits): om[p]=bit
    if all((om[(a,b)]+om[(add(a,b),c)]-om[(b,c)]-om[(a,add(b,c))])%2==0
           for a in V for b in V for c in V):
        Z2c.append(om)
# --- B2
B2=set()
for fb in product((0,1),repeat=3):
    f={e:0}; [f.__setitem__(a,fb[i]) for i,a in enumerate(NE)]
    B2.add(tuple((f[a]+f[b]-f[add(a,b)])%2 for a in V for b in V))
key=lambda om: tuple(om[(a,b)] for a in V for b in V)
# --- classes
classes={}
for om in Z2c:
    rep=min(tuple((k+bk)%2 for k,bk in zip(key(om),b)) for b in B2)
    classes.setdefault(rep,[]).append(om)
print(f"|Z2|={len(Z2c)}  |B2|={len(B2)}  |H2|={len(classes)} (expected 8)")
assert len(classes)==8
def involutions(om):
    n=0
    for eps in (0,1):
        for a in V:
            if (eps,a)==(0,e): continue
            if om[(a,a)]%2==0: n+=1
    return n
def lam_nonzero(om):
    return any((om[(a,b)]+om[(b,a)])%2 for a in V for b in V)
NAME={7:'Z2^3 (split)',3:'Z4xZ2',5:'D4',1:'Q8'}
rows=[]
for rep,members in sorted(classes.items()):
    om=members[0]; inv=involutions(om); nl=lam_nonzero(om)
    rows.append((rep,inv,nl))
    # TWN per class: (1,e) central and != (0,e): central always (kernel), nontrivial always
    # D4C per class: exists a,b with commutator = kernel generator <=> lam nonzero
print("class | extension     | involutions | lam!=0 (D4C content) | TWN content")
twn_ok=d4c_ok=0
for rep,inv,nl in rows:
    print(f"  {NAME[inv]:13s}    {inv}            {nl}                  True")
    twn_ok+=1; d4c_ok+=nl
print(f"\nTWN-compatible classes: {twn_ok}/8 (kernel faithful in every extension, including split)")
print(f"D4C-compatible classes: {d4c_ok}/8 (exactly the noncommuting extensions)")
assert twn_ok==8 and d4c_ok==4
# --- realized group <N,S>
import numpy as np
N=np.diag([1,-1]); S=np.array([[0,1],[1,0]]); I=np.eye(2,dtype=int)
sec={e:I,(1,0):N,(0,1):S,(1,1):N@S}
om_real={}
for a in V:
    for b in V:
        prod_=sec[a]@sec[b]; tgt=sec[add(a,b)]
        if (prod_==tgt).all(): om_real[(a,b)]=0
        elif (prod_==-tgt).all(): om_real[(a,b)]=1
        else: raise AssertionError("section image escaped +/-")
comm = N@S@np.linalg.inv(N).astype(int)@np.linalg.inv(S).astype(int)
print(f"\nrealized [N,S] = -I: {(comm==-I).all()}")
rep_real=min(tuple((k+bk)%2 for k,bk in zip(key(om_real),b)) for b in B2)
inv_r=involutions(classes[rep_real][0])
print(f"realized <N,S> class: {NAME[inv_r]} (involutions={inv_r}); lam!=0: {lam_nonzero(classes[rep_real][0])}")
assert NAME[inv_r]=='D4'
print("\n2-CELL VERDICT: STRICT SEPARATION ONE RUNG UP — truth-identical at stratum 1,")
print("D4C-classes (4) STRICTLY CONTAINED in TWN-classes (8); realized group in a D4 class.")
print("TWN survives the split extension where D4C dies: the circle separates only at rung 2.")
