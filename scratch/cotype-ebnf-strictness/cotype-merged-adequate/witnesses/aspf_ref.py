# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""ASPF reference implementation (the spec-as-code the conformance checks pin).
An implementer in a fresh session reconstructs THIS by making the f090_2_aspf_* checks pass.
ASPF = Algebraic Structural Prime Fingerprint = Godel numbering of a type/token multiset."""
from math import gcd as _gcd
from functools import reduce

# Operation 1: prime assignment. Tokens -> primes by rank (first-seen order over a stable registry).
#   The corpus invariant: p(t) = the rank-th prime (rank 0-indexed: int->2, str->3, bool->5, ...).
_PRIMES = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47]
def prime_of(token, registry):
    """Stable prime for a token; registry maps token->rank, mutated on first sight."""
    if token not in registry:
        registry[token] = len(registry)
    return _PRIMES[registry[token]]

# Operation 2: fingerprint. A multiset of tokens -> the product of their primes (Godel number).
#   Order-independent by commutativity of multiplication; multiplicity = prime power.
def _canonical_registry(tokens):
    # ONE canonicalizer (sorted token identity) -- any stable canonical order works; what matters is that
    # the SAME token always gets the SAME prime, so fingerprint is order-independent. Not the only choice.
    return {t:i for i,t in enumerate(sorted(set(tokens)))}

def fingerprint(tokens, registry=None):
    # CANONICAL FORM: the prime product, order-independent (a true multiset invariant). For dedup/equality.
    registry = _canonical_registry(tokens) if registry is None else registry
    return reduce(lambda acc,t: acc * _PRIMES[registry[t]], tokens, 1)

def canonicalize(tokens, registry=None):
    # canonicalization + RESIDUE RETAINMENT: returns (canonical_fingerprint, residue) where the residue is
    # exactly what the canonical form discarded -- enough to RECOVER the original token sequence. Here the
    # residue is the original order as indices into the multiset's canonical (sorted) listing. The fingerprint
    # alone is lossy (12 <- both [int,int,str] and [str,int,int]); fingerprint + residue is LOSSLESS.
    registry = _canonical_registry(tokens) if registry is None else registry
    fp = fingerprint(tokens, registry)
    canonical_seq = sorted(tokens)                      # the canonical listing of this multiset
    # residue = the permutation taking canonical_seq -> the original tokens (recovers order)
    used = list(canonical_seq)
    residue = []
    for t in tokens:
        j = used.index(t); residue.append(j); used[j] = None  # mark consumed (handles duplicates)
    return fp, (tuple(canonical_seq), tuple(residue))

def recover(canonical_seq, residue):
    # invert canonicalize: residue + canonical listing -> the original token sequence (proves residue lossless)
    return [canonical_seq[i] for i in residue]

# Operation 3: structural arithmetic on fingerprints (the (N, gcd, lcm, |) lattice).
def common_substructure(f1, f2):   # GCD = shared tokens with min multiplicity
    return _gcd(f1, f2)
def union_structure(f1, f2):        # LCM = all tokens with max multiplicity
    return f1 * f2 // _gcd(f1, f2)
def is_subtype(sub, sup):           # divisibility: sub <: sup iff sup | sub (sub has >= the tokens)
    return sub % sup == 0

# Operation 4: intern (hash-cons). Same fingerprint -> same canonical id; idempotent normal form.
class Interner:
    def __init__(self): self._t = {}
    def intern(self, fp):
        return self._t.setdefault(fp, fp)   # canonical: equal fp -> identical stored object
