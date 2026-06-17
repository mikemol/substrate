"""
act-stationary-pilot.py — S16: the act-pun adjudication. "Apparent
choice" is the stationary-phase shadow of a held ensemble of histories.

Ensemble: all paths of T=8 steps from {-2..2}, endpoints 0 -> 0 (fixed),
kinetic action S = sum(step^2)/2. The stationary (here minimal) path is
x == 0. Weights:
  - complex semiring e^{iS/hbar} (the path-integral weighting)
  - flat positive weights (the plain counting semiring)

1. CONCENTRATION: under complex weights, the 5% of paths nearest the
   stationary action carries far more than 5% of the total magnitude —
   the remaining 95% net-cancels by interference. Under flat positive
   weights the same 5% carries exactly 5%: no concentration is possible
   in a positive semiring; "the chosen path" cannot even be defined
   there.
2. SHARPENING: shrinking hbar increases the concentration — the
   classical limit is the pinning tightening.
Reading: the single "chosen" trajectory is a QUOTIENT SHADOW of the
full path ensemble (classical path : path integral :: Viterbi : packed
forest :: probability : carrier). Teleological language ("the path
chooses", "forces act") is the act-1 reading of an act-2 ensemble —
precise once indexed.
"""
import itertools, cmath

T = 8; steps = (-2, -1, 0, 1, 2)
S_list = [sum(v*v for v in s)/2.0
          for s in itertools.product(steps, repeat=T) if sum(s) == 0]
N = len(S_list)
thr = sorted(S_list)[int(0.05*N)]
near = [S for S in S_list if S <= thr]
frac = len(near)/N

def conc(hbar):
    Z  = sum(cmath.exp(1j*S/hbar) for S in S_list)
    Zn = sum(cmath.exp(1j*S/hbar) for S in near)
    return abs(Zn)/abs(Z)

c10, c04 = conc(1.0), conc(0.4)
print(f"ensemble: {N} paths, near-stationary subset = {len(near)} ({100*frac:.1f}% of paths, S <= {thr})")
print(f"1. flat positive weights: subset carries exactly {100*frac:.1f}% of the total — no concentration definable")
print(f"   complex weights, hbar=1.0: subset carries {100*c10:.1f}% of |Z| — concentration: {c10 > 4*frac}")
print(f"2. hbar=0.4: subset carries {100*c04:.1f}% of |Z| — sharpening toward the classical pinning: {c04 > c10}")
print(f"VERDICT: 'the chosen path' is the stationary-phase shadow of the held ensemble; choice-language is the act-1 reading of act-2 dynamics, valid once indexed: {c10 > 4*frac and c04 > c10}")

# --- v2 addendum: check 2 RETAINED AS FAILED above (fixed 5-10% window,
# hbar=0.4 -> 36.1%): a FIXED window decoheres internally as hbar shrinks,
# because the stationary-phase support narrows. The corrected claim:
# sharpening holds in HBAR-SCALED windows W(hbar) = {S <= pi*hbar} — a
# SHRINKING fraction of paths maintains/grows its capture, so the
# concentration FACTOR (capture / path-fraction) grows as hbar -> 0.
# The classical pinning tightens in WIDTH; it does not fatten in place.
print()
print("2'. corrected sharpening (hbar-scaled windows, W = {S <= pi*hbar}):")
factors = []
for hbar in (1.0, 0.4, 0.2):
    W = [S for S in S_list if S <= 3.14159265*hbar]
    Z  = sum(cmath.exp(1j*S/hbar) for S in S_list)
    Zw = sum(cmath.exp(1j*S/hbar) for S in W)
    cap, fr = abs(Zw)/abs(Z), len(W)/N
    factors.append(cap/fr)
    print(f"    hbar={hbar}: window = {len(W)} paths ({100*fr:.2f}%), capture = {100*cap:.1f}% of |Z|, concentration factor = {cap/fr:.1f}")
print(f"    factor grows as hbar shrinks (support narrows, pinning tightens): {factors[-1] > factors[0]}")
