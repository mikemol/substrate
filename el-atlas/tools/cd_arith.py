#!/usr/bin/env python3
"""cd_arith — Cayley-Dickson arithmetic over flat real tuples.

The Python instance of the *doubling generator* (the same construction that
``Substrate.Algebra.CayleyDickson`` realises in Agda): a multivector is a tuple of
length 2ⁿ of real coefficients; ``conj`` negates all but the scalar; ``cdmul``
recurses by halving — the Cayley-Dickson doubling
``(a,b)·(c,d) = (a·c − d̄·b,  d·a + b·c̄)``.

Folds the conj/cdmul/vadd/vsub/vneg kernel that the zero-divisor pilots
(hyperplane-ride, radzdg-witness, second-order-zd, witness-stratum) had each
reimplemented byte-for-byte with the *same* convention (verified identical, modulo
variable names and add/sub-as-lambda). Each pilot keeps its own argument — the
witness / ZD-separation lesson; only the shared substrate arithmetic lives here.
"""


def vadd(u, v):
    return tuple(p + q for p, q in zip(u, v))


def vsub(u, v):
    return tuple(p - q for p, q in zip(u, v))


def vneg(u):
    return tuple(-p for p in u)


def conj(w):
    return (w[0],) + tuple(-t for t in w[1:])


def cdmul(x, y):
    n = len(x)
    if n == 1:
        return (x[0] * y[0],)
    h = n // 2
    a, b, c, d = x[:h], x[h:], y[:h], y[h:]
    return vsub(cdmul(a, c), cdmul(conj(d), b)) + vadd(cdmul(d, a), cdmul(b, conj(c)))


def norm(v):
    return sum(t * t for t in v)
