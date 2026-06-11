"""
nve-bridge-pilot.py — the author's answer to Nedge's open vE (proof by
cases): single/double pin SPLIT/JOIN carrier expansion + the Wheatstone
bridge. Candidate claim NVE.

Circuit: source V across A-C; left divider A-(G1)-B-(G2)-C = the case
pair; right divider A-(G3)-D-(G4)-C = the reference; galvanometer
conductance g across B-D. Checks:

1. NULL = DETERMINANT: i_g = 0 iff G1*G4 = G2*G3 (sign of i_g = sign of
   the determinant) — the bridge reads the bias of the
   comparison-of-comparisons.
2. BRIDGE = DIFFERENCE OF CONDITIONALS: in the high-impedance limit,
   i_g/g -> V*( G1/(G1+G2) - G3/(G3+G4) ) — each divider midpoint is the
   L1-normalization (sec. 5.7e identification 5); the bridge compares two
   conditionals and nulls on equal odds.
3. SPLIT IS A SECTION, THE JOIN FORGETS IT: distinct case splits (3,7)
   and (5,5) of the same joined G = 10 — the scalar join conflates them;
   the bridge against a fixed reference DISTINGUISHES them. The purchased
   axis is measurable.
4. THE CLASSICAL SECTION OF vE: a reference with the SAME ODDS (any
   mass!) nulls the bridge — (3,7) vs (6,14) -> i_g = 0. The null
   detects ratio equality only (the bridge is a G-comparator: a
   shadow-level instrument); case identity is invisible exactly on the
   balance manifold, which is why classical logic does vE for free and
   the scalar calculus cannot do it off the manifold.
"""
import random
random.seed(11)

def bridge(G1,G2,G3,G4,g,V=1.0):
    a, d = G1+G2+g, G3+G4+g
    det = a*d - g*g
    VB = (G1*V*d + g*G3*V)/det
    VD = (a*G3*V + G1*V*g)/det
    return g*(VB-VD)

ok_null = ok_sign = True
for _ in range(3000):
    G1,G2,G3 = (random.uniform(.1,10) for _ in range(3))
    G4 = random.uniform(.1,10)
    ig = bridge(G1,G2,G3,G4, .5)
    D  = G1*G4 - G2*G3
    ok_sign &= (ig > 0) == (D > 0) or abs(D) < 1e-9
    G4b = G2*G3/G1                      # constructed balance
    ok_null &= abs(bridge(G1,G2,G3,G4b,.5)) < 1e-9
print(f"1. null<=>det and sign match over 3000 samples: null={ok_null}, sign={ok_sign}")

ok_cond = True
for _ in range(2000):
    G1,G2,G3,G4 = (random.uniform(.1,10) for _ in range(4))
    lim = bridge(G1,G2,G3,G4,1e-12)/1e-12
    formula = G1/(G1+G2) - G3/(G3+G4)
    ok_cond &= abs(lim-formula) < 1e-6
print(f"2. high-impedance bridge = difference of L1-normalized conditionals: {ok_cond}")

ref = (2.0,3.0)
iA = bridge(3,7,*ref,.5); iB = bridge(5,5,*ref,.5)
print(f"3. splits (3,7) and (5,5) of joined G=10: scalar join equal ({3+7}=={5+5}); bridge readings {iA:+.6f} vs {iB:+.6f} differ: {abs(iA-iB)>1e-3}")

i_same_odds = bridge(3,7,6,14,.5)
print(f"4. classical section: (3,7) vs (6,14) (equal odds, double mass) -> i_g = {i_same_odds:.2e} (null: {abs(i_same_odds)<1e-12}) — the bridge is a shadow-level (ratio) instrument; the case-pair retains the mass it cannot see")
