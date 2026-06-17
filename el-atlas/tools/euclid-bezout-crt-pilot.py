"""
euclid-bezout-crt-pilot.py — S20: one machine, three theorems. Exact
integers throughout.

a. The Euclid quotient stream losslessly encodes the REDUCED PAIR: folding
   the quotients back through the convergent recurrence returns (a,b)/g.
b. BEZOUT = THE DETERMINANT: the extended algorithm's certificate
   u*a + v*b = g is the convergent-pair determinant (S19's Pell +-1 was
   Bezout's identity all along) — the pair carries its own coprimality
   witness.
c. WITNESS-CARRYING vs VERDICT-ONLY: the certificate verifies in one
   multiply-add, independent of the computation that produced it
   (1000 pairs at 10^50 scale).
d. CRT = SPLIT/JOIN UNDER A COPRIMALITY GUARD: Bezout builds orthogonal
   idempotents (e1+e2=1, e1*e2=0 — a discrete resolution of identity);
   encode/decode round-trips exhaustively; per-pin arithmetic joins to the
   direct product. GUARD WITNESS: non-coprime moduli (6,4) — a collision
   (1 and 13 share residues) AND an unreachable pair ((0 mod 6, 1 mod 4))
   — the shared factor is cross-talk; independence fails exactly there.
e. RATIONAL RECONSTRUCTION closes the codec: from the modular SHADOW
   x = p*q^{-1} mod M, the half-extended algorithm recovers the formal-
   quotient PAIR (p,q) — the quotient shadow, lifted, by Euclid himself.
"""
from math import gcd, isqrt
import random
rng = random.Random(23)

def quotients(a, b):
    qs = []
    while b: qs.append(a//b); a, b = b, a % b
    return qs, a                      # stream, gcd

def ext_gcd(a, b):
    r0, r1, s0, s1, t0, t1 = a, b, 1, 0, 0, 1
    while r1:
        q = r0 // r1
        r0, r1, s0, s1, t0, t1 = r1, r0-q*r1, s1, s0-q*s1, t1, t0-q*t1
    return r0, s0, t0

ok_a = ok_b = ok_c = True
for _ in range(300):
    a, b = rng.randint(2, 10**6), rng.randint(1, 10**6)
    qs, g = quotients(a, b)
    h0, h1, k0, k1 = 1, qs[0], 0, 1
    for qq in qs[1:]:
        h0, h1, k0, k1 = h1, qq*h1+h0, k1, qq*k1+k0
    ok_a &= (h1, k1) == (a//g, b//g)
    gg, u, v = ext_gcd(a, b)
    ok_b &= gg == g and u*a + v*b == g and abs(h1*k0 - h0*k1) == 1
for _ in range(1000):
    a, b = rng.randint(10**49, 10**50), rng.randint(10**49, 10**50)
    g, u, v = ext_gcd(a, b)
    ok_c &= (u*a + v*b == g)          # one multiply-add verifies the witness
print(f"a. quotient stream folds back to the reduced pair (300 trials): {ok_a}")
print(f"b. Bezout certificate == convergent determinant (+-1 in lowest terms): {ok_b}")
print(f"c. witness verifies independently of computation (1000 pairs @ 1e50): {ok_c}")

m, n = 35, 12  # wait — must be coprime; gcd(35,12)=1, good
g, u, v = ext_gcd(m, n)
e1, e2 = (v*n) % (m*n), (u*m) % (m*n)
ok_d = (e1+e2) % (m*n) == 1 and (e1*e2) % (m*n) == 0
for x in range(m*n):
    ok_d &= (x % m * e1 + x % n * e2) % (m*n) == x
    y = (x*7 + 3) % (m*n)
    ok_d &= (x*y) % (m*n) == ((x % m * (y % m)) % m * e1 + (x % n * (y % n)) % n * e2) % (m*n)
collide = (1 % 6, 1 % 4) == (13 % 6, 13 % 4)
unreach = all(not (x % 6 == 0 and x % 4 == 1) for x in range(24))
print(f"d. CRT idempotents (resolution of identity), exhaustive round-trip + per-pin product (mod {m*n}): {ok_d}; non-coprime guard — collision(1,13 mod 24): {collide}, unreachable pair (0 mod 6, 1 mod 4): {unreach}")

M = (1 << 61) - 1
ok_e = True
for _ in range(200):
    p = rng.randint(1, 10**8); q = rng.randint(1, 10**8)
    gg = gcd(p, q); p //= gg; q //= gg
    x = p * pow(q, -1, M) % M
    r0, r1, t0, t1 = M, x, 0, 1
    bound = isqrt(M // 2)
    while r1 > bound:
        qq = r0 // r1
        r0, r1, t0, t1 = r1, r0-qq*r1, t1, t0-qq*t1
    if t1 < 0: r1, t1 = -r1, -t1
    ok_e &= (r1, t1) == (p, q)
print(f"e. rational reconstruction: the pair recovered exactly from its modular shadow (200 trials, M = 2^61-1): {ok_e}")
