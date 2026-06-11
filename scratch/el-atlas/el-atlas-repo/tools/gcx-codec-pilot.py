"""
gcx-codec-pilot.py — S4 pilot for candidate GCX (the GALAXY codex):
merged_ontology Theorem 9.1, W_{v,k} <-> log_alpha(F(s)^k), tested as stated.

What the theorem IS, verified exactly (the third codec sighting):
  the substitution is the exp_alpha -| log_alpha adjunction — a
  multiplicative magnitude carrier linked formula-for-formula to an
  additive weight carrier (Lemma 2.5b in gauge alpha):
    (1) roundtrip identity, (2) product <-> sum (hom),
    (3) power <-> scalar action, (4) F=1 <-> W=0 (identity images),
    (5) base change log_alpha F = ln F / ln alpha (gauge, not structure).

What the theorem MISSES, demonstrated: the doc's "canonical prime
assignment" p(t) = alpha^rank(t) is not a prime assignment — alpha-powers
collide on equal rank-sums, so reversibility (the ASPF normative rule
"prime products remain authoritative") is sacrificed. The W-side is the
RANK-SUM QUOTIENT of the genuine prime-product carrier: GALAXY is a
one-mode decode / lossy projection of ASPF, and Thm 9.1's "isomorphism"
is exact precisely on that quotient.
"""
import math, random
random.seed(42)
ALPHA = 0.7
ok = dict(roundtrip=True, hom=True, power=True, ident=True, gauge=True)
for _ in range(2000):
    ranks1 = [random.randint(0, 9) for _ in range(random.randint(1, 6))]
    ranks2 = [random.randint(0, 9) for _ in range(random.randint(1, 6))]
    k = random.randint(1, 5)
    F1 = math.prod(ALPHA ** r for r in ranks1)           # F(s) = prod p(t), p(t)=alpha^rank
    F2 = math.prod(ALPHA ** r for r in ranks2)
    W1, W2 = sum(ranks1), sum(ranks2)                    # additive carrier (rank-sums)
    ok['roundtrip'] &= abs(math.log(F1, ALPHA) - W1) < 1e-9
    ok['hom']       &= abs(math.log(F1 * F2, ALPHA) - (W1 + W2)) < 1e-9
    ok['power']     &= abs(math.log(F1 ** k, ALPHA) - k * W1) < 1e-9
    ok['gauge']     &= abs(math.log(F1) / math.log(ALPHA) - W1) < 1e-9
ok['ident'] = abs(math.log(1.0, ALPHA) - 0.0) < 1e-9     # empty multiset: F=1 <-> W=0
print("CODEC LAYER (Thm 9.1 substitution = exp_a -| log_a, exact):", ok)

# The quotient demonstration: equal rank-sum, distinct structure.
PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]            # genuine ASPF assignment by rank
m1, m2 = [1, 4], [2, 3]                                   # rank multisets, both sum to 5
F_true1 = math.prod(PRIMES[r] for r in m1)                # 3*23  = 69? no: PRIMES[1]*PRIMES[4]=3*11=33
F_true2 = math.prod(PRIMES[r] for r in m2)                # 5*7   = 35
W_shadow1, W_shadow2 = sum(m1), sum(m2)
F_alpha1 = math.prod(ALPHA ** r for r in m1)
F_alpha2 = math.prod(ALPHA ** r for r in m2)
print(f"QUOTIENT: rank-multisets {m1} vs {m2}: W-side {W_shadow1} == {W_shadow2} (collides);",
      f"alpha-side {F_alpha1:.6f} == {F_alpha2:.6f} (collides);",
      f"genuine prime products {F_true1} != {F_true2} (carrier distinguishes)")
print("=> GALAXY W is the rank-sum quotient of the prime-product carrier:",
      W_shadow1 == W_shadow2 and abs(F_alpha1-F_alpha2) < 1e-12 and F_true1 != F_true2)
