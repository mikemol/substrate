"""
cf-grace-pilot.py — S19: continued fractions over epistemological quotient
space. Exact integer arithmetic throughout (target sqrt(2), convergents via
the pair recurrence p_n = 2p_{n-1}+p_{n-2}, q_n likewise).

1. THE OSCILLATION IS THE INVARIANT: p^2 - 2q^2 = +-1, strictly
   alternating (Pell) — the convergents provably alternate sides of the
   limit. The oscillation is not a defect of the approximation; it IS the
   approximation working. (And the +-1 is the SL2 determinant: an
   invariant the quotient p/q cannot see — the pair is the carrier.)
2. SELF-CANONICALIZATION: gcd(p,q) = 1 automatically, forced by the
   determinant — the pre-quotient pair arrives in lowest terms without a
   reduction step.
3. NEVER BETTER NOW THAN TOMORROW: each convergent strictly improves on
   the last, AND is optimal at its complexity budget — no rational with a
   smaller denominator comes closer (brute-forced, exact).
4. TODAY'S ERROR IS BOUNDED BY TOMORROW'S RESOURCES:
   |x - p_n/q_n| < 1/(q_n * q_{n+1}) — the bound on the current stage is
   expressed in the NEXT stage's denominator. The Goedelian clause, as an
   inequality.
"""
from math import gcd, isqrt
from fractions import Fraction

ps, qs = [1, 3], [1, 2]
for _ in range(18):
    ps.append(2*ps[-1] + ps[-2]); qs.append(2*qs[-1] + qs[-2])

pell = [p*p - 2*q*q for p, q in zip(ps, qs)]
ok1 = all(abs(v) == 1 for v in pell) and all(pell[i] == -pell[i+1] for i in range(len(pell)-1))
print(f"1. Pell alternation (first eight): {pell[:8]} — strict +-1 alternation: {ok1}")

ok2 = all(gcd(p, q) == 1 for p, q in zip(ps, qs))
print(f"2. self-canonicalization (gcd = 1 at every stage, forced by det): {ok2}")

X = Fraction(isqrt(2*10**60), 10**30)        # sqrt(2) to ~1e-30, exact rational
err = lambda p, q: abs(Fraction(p, q) - X)
ok3 = True
for n in range(2, 8):
    p, q = ps[n], qs[n]; e = err(p, q)
    ok3 &= e < err(ps[n-1], qs[n-1])                       # strictly better tomorrow
    for b in range(1, q):                                   # optimal at today's budget
        a = round(X*b)
        ok3 &= err(a, b) > e
print(f"3. never better now than tomorrow (strict improvement + best-at-budget, q up to {qs[7]}): {ok3}")

ok4 = all(err(ps[n], qs[n]) < Fraction(1, qs[n]*qs[n+1]) for n in range(10))
print(f"4. today's error < 1/(q_n * q_n+1) — bounded by tomorrow's denominator: {ok4}")
