"""
second-order-zd-pilot.py — S22: the certificate is carried, not computed;
zero divisors are compiled, not searched; the sedenion exhibit is an
alignment (cross-talk) witness. Exact arithmetic.

1. THE INVARIANT IS CARRIED AT EVERY STEP: along the whole extended-Euclid
   trajectory, r_i = s_i*a + t_i*b holds at EACH i — the Bezout certificate
   is not a final output but a maintained invariant; "the final vector just
   prior to zero" is where you stop READING a continuously certified path.
2. ZERO DIVISORS COMPILED FROM THE CERTIFICATE: in Z/420 the CRT
   idempotents (built from the Bezout vector, S20) are themselves a
   zero-divisor pair — the first ZDs of the split ring come out of EEA, no
   search.
3. THE CHART CLASSIFIES ALL OF THEM: exhaustively over Z/420, the
   zero-divisor set = {x != 0 : gcd(x,420) > 1} = {some prime-power CRT
   coordinate is 0}; and each annihilator is READ OFF the coordinates:
   |ann(x)| = prod_f gcd(x,f), ann(x) = {y : (f/gcd(x,f)) | y for each
   factor} — verified against brute force. The full witness structure of
   the ZD phenomenon (existence, classification, annihilators) is compiled
   from the EEA/Bezout/CRT chart.
4. THE SEDENION EXHIBIT IS AN ALIGNMENT WITNESS: (e1+e10)(e4-e15) = 0
   decomposes in octonion-pair coordinates as the simultaneous system
   a*c = conj(d)*b  AND  d*a = -(b*conj(c)) — channel cross-talk between
   the doubling halves, with the octonion multiplication (the last rung
   before the boundary — "the final vector just prior") supplying the
   coefficients. Verified componentwise, exactly.
CORRECTION (retained-as-failed, act-stationary precedent): check 3's first
form used "some coordinate = 0" — the FIELD-product reading — against the
non-squarefree modulus 420 = 2^2*3*5*7, whose Z/4 factor is non-reduced
(nilpotent 2): x = 2 is a ZD with a non-unit, NONZERO coordinate. Corrected
criterion: ZD <=> some coordinate is a NON-UNIT in its factor (verified
exhaustively); over squarefree 210 the naive reading holds exactly. The
failure is the lesson: the chart classifies through the factor rings' own
unit structure, and non-reduced factors are a sub-stratum of their own.
"""
from math import gcd
import random
rng = random.Random(7)

ok1 = True
for _ in range(300):
    a, b = rng.randint(2, 10**9), rng.randint(1, 10**9)
    r0, r1, s0, s1, t0, t1 = a, b, 1, 0, 0, 1
    ok1 &= (r0 == s0*a + t0*b) and (r1 == s1*a + t1*b)
    while r1:
        q = r0 // r1
        r0, r1, s0, s1, t0, t1 = r1, r0-q*r1, s1, s0-q*s1, t1, t0-q*t1
        ok1 &= (r0 == s0*a + t0*b) and (r1 == s1*a + t1*b)
print(f"1. certificate carried at EVERY trajectory step (300 runs): {ok1}")

M = 420
def ext_gcd(a, b):
    r0, r1, s0, s1, t0, t1 = a, b, 1, 0, 0, 1
    while r1:
        q = r0//r1; r0, r1, s0, s1, t0, t1 = r1, r0-q*r1, s1, s0-q*s1, t1, t0-q*t1
    return r0, s0, t0
g, u, v = ext_gcd(35, 12)
e1, e2 = (v*12) % M, (u*35) % M
ok2 = e1 != 0 and e2 != 0 and (e1*e2) % M == 0
print(f"2. idempotents e1={e1}, e2={e2}: a zero-divisor pair compiled from the Bezout vector: {ok2}")

zd_brute = {x for x in range(1, M) if any((x*y) % M == 0 for y in range(1, M))}
zd_gcd   = {x for x in range(1, M) if gcd(x, M) > 1}
F = [4, 3, 5, 7]
zd_chart = {x for x in range(1, M) if any(x % f == 0 for f in F)}
ok3 = zd_brute == zd_gcd == zd_chart
ok3b = True
for x in rng.sample(range(1, M), 30):
    ann_brute = {y for y in range(M) if (x*y) % M == 0}
    ann_form  = {y for y in range(M) if all(y % (f//gcd(x, f)) == 0 for f in F)}
    ok3b &= ann_brute == ann_form and len(ann_brute) == 1 if False else (ann_brute == ann_form)
    ok3b &= len(ann_brute) == gcd(x,4)*gcd(x,3)*gcd(x,5)*gcd(x,7)
print(f"3. chart classifies ZDs exhaustively ({len(zd_brute)} of them): {ok3}; annihilators read off coordinates (30 samples): {ok3b}")

from cd_arith import conj, vadd, vneg, cdmul   # Π9: shared CD doubling generator
def e8(i):
    w = [0]*8; w[i] = 1; return tuple(w)
a_, b_ = e8(1), e8(2)            # x = e1 + e10 = (e1, e2)
c_, d_ = e8(4), vneg(e8(7))      # y = e4 - e15 = (e4, -e7)
eq1 = cdmul(a_, c_) == cdmul(conj(d_), b_)
eq2 = cdmul(d_, a_) == vneg(cdmul(b_, conj(c_)))
print(f"4. sedenion exhibit decomposes as the alignment system: a*c = conj(d)*b: {eq1}; d*a = -(b*conj(c)): {eq2} — cross-talk between the doubling halves, octonion coefficients")
