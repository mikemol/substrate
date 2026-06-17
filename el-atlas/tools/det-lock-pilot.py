"""
det-lock-pilot.py — S25 prelude: the radial lock schedule. One certificate,
det L_x, carried through the tower; at d <= 8 it is LOCKED to the norm
(det L_x = N(x)^(d/2): one invariant, two charts — a codec); at d = 16 the
lock breaks and det becomes an INDEPENDENT coordinate — the unlock is the
purchase of an axis, and the witness modes (norm-failure vs kernel) are the
two readings of the unlocked pair. The certificate never stops; it refines.
"""
import numpy as np, random
rng = random.Random(17)
def cdm(x,y):
    n=len(x)
    if n==1: return (x[0]*y[0],)
    k=n//2; a,b,c,d=x[:k],x[k:],y[:k],y[k:]
    cj=lambda w:(w[0],)+tuple(-t for t in w[1:])
    return tuple(i-j for i,j in zip(cdm(a,c),cdm(cj(d),b)))+tuple(i+j for i,j in zip(cdm(d,a),cdm(b,cj(c))))
def L(x,d): return np.array([cdm(x, tuple(1.0 if t==j else 0.0 for t in range(d))) for j in range(d)]).T
for d in (2,4,8,16):
    rats=[]
    for _ in range(30):
        x=tuple(rng.gauss(0,1) for _ in range(d)); N=sum(t*t for t in x)
        rats.append(np.linalg.det(L(x,d))/N**(d//2))
    locked = max(abs(r-1.0) for r in rats) < 1e-6
    print(f"  d={d:2d}: det L_x / N^{d//2} over 30 samples: spread [{min(rats):.6f}, {max(rats):.6f}] -> LOCKED: {locked}")
x=tuple((1.0 if i==1 else 0.0)+(1.0 if i==10 else 0.0) for i in range(16))
print(f"  d=16 unlock refines: ZD exhibit has N = {sum(t*t for t in x):.0f} != 0, det = {np.linalg.det(L(x,16)):.1e} (kernel mode);")
print(f"  generic samples above have det != 0 with VARYING ratio (independent coordinate) — the pair (N, det) is the purchased chart.")
