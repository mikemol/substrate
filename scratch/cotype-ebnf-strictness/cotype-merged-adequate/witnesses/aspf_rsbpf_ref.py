# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""ASPF = parse forests. The REAL ASPF reference (batch [AI-CORPUS-ASPF]), grounded from Drive:
  - RSBPF "Ranked Symmetric Binary Path Forest - A Unified Formalization" (1DzSPa1) -- the ALGEBRAIC face.
  - "ASPF Payload Alternation Ambiguity Example" (1c5_PD) -- the PARSING face (ASPF = Ambiguous Shared
    Parse Forest = SPPF; sharing + packing + payload-alternation).

This is the THIRD distinct ASPF-named object, and the CORRECT one:
  - aspf_ref.py            = prime-fingerprint MULTISET / Godel reading  (NOT parse forest -- misnamed)
  - aspf_segment_ref.py    = single-shared-vertex segment monoid          (this is APSP material -- misnamed)
  - aspf_rsbpf_ref.py      = THIS: binary path forests, the real parse-forest ASPF  (RSBPF)
The relabel of the misnamed nine is [AI-ASPF-RELABEL] (separate, gated). This module ADDS the real thing.

ALGEBRAIC STRUCTURE (RSBPF doc, implemented faithfully):
  - binary path: a tuple in {L,R}*; the free monoid under concatenation, |epsilon|=0.
  - binary tree skeleton: a finite PREFIX-CLOSED set of {L,R}* paths (epsilon in T; p.d in T => p in T).
  - address sort of a node p in T: Addr0 (leaf: no children), Addr1 (unary: exactly one of p.L,p.R),
    Addr2 (binary: both). Exhaustive + exclusive partition.
  - rank(T) = max path length (depth); rank({epsilon})=0.
  - binary path FOREST F = finite multiset of skeletons; rank(F)=max rank; rank(empty)=0.
  - object (F, r, sigma): sigma : Addr2(F) -> GF(2) the swap-parity decoration.
  - monoidal product (X) = disjoint forest union; unit = empty forest; rank via max; braiding beta^2 = id.
  - rank functor R : RSBPF -> (N, max, 0), STRICT monoidal: R(A (X) B) = max(R A, R B), R(I)=0.
  - involution group Inv(F) = GF(2)^|Addr2(F)|, elementary abelian 2-group, FREE+TRANSITIVE on decorations.
  - swap_p flips sigma at exactly p; self-inverse; rank- and sort-preserving.

PARSING READING (payload doc): a binary node (Addr2) is a PACKED / branching point; sigma(p) in GF(2)
records which derivation orientation is active (the L/R child order = the packed-alternative selector).
rank = parse-tree depth. address = the {L,R}* path to a node. PACKING = one vertex, alternative hyperedges;
the GF(2) swap toggles between the two children's order = the alternation selector.

CONSERVATION (the ASPF witness): the GF(2) decoration RELEASES the trivial law "child order is fixed /
canonical" (a binary node has a definite left-then-right reading); the carried witness is sigma(p), the
swap-parity per binary node. triviality-out (fixed child order) = witness-in (the GF(2) decoration). The
involution group is the full reservoir of these witnesses; it is free+transitive, so every orientation is
reachable from every other by a unique swap sequence (the decoration is a torsor for Swap(F)).

CANON+RESIDUE (per-ref obligation; ASPF releases CHILD-ORDER): the UNDECORATED forest (F, r) is the canonical
form -- it is LOSSY (it forgets sigma, i.e. which alternative is active at each binary node). The residue is
sigma : Addr2(F) -> GF(2). forest + sigma is lossless. This is the 7th carrier (cf. ASPF-order, polar-
orientation, CONSTELLATION-injectivity, GALAXY-neighbor, Nedge-bivalence, APSP-locality).
"""
from itertools import product as _product

# ─────────────────────────────────────────────────────────────────────────────
# binary paths and tree skeletons
# ─────────────────────────────────────────────────────────────────────────────
EPS = ()                      # the empty path epsilon (the root)

def is_prefix_closed(T):
    """T (a set of {L,R}* tuples) is prefix-closed: epsilon in T and every prefix of every path is in T."""
    S = set(T)
    if EPS not in S:
        return False
    for p in S:
        for k in range(len(p)):
            if p[:k] not in S:
                return False
    return True

def skeleton(paths):
    """Build a binary tree skeleton from paths, closing under prefixes (epsilon always included)."""
    S = set()
    for p in paths:
        p = tuple(p)
        for k in range(len(p) + 1):
            S.add(p[:k])
    S.add(EPS)
    assert is_prefix_closed(S)
    return frozenset(S)

def addr_sort(T, p):
    """Address sort of node p in skeleton T: 0 (leaf), 1 (unary), 2 (binary). Exhaustive + exclusive."""
    assert p in T, "p must be a node of T"
    has_L = (p + ('L',)) in T
    has_R = (p + ('R',)) in T
    return (1 if has_L else 0) + (1 if has_R else 0)   # 0/1/2 = exactly the arity

def addr2_nodes(T):
    """The binary (Addr2) nodes of T -- the sites that carry a GF(2) swap parity."""
    return frozenset(p for p in T if addr_sort(T, p) == 2)

def rank_tree(T):
    """rank(T) = max path length (depth). rank({epsilon}) = 0."""
    return max((len(p) for p in T), default=0)

# ─────────────────────────────────────────────────────────────────────────────
# forests and decorated objects (F, r, sigma)
# ─────────────────────────────────────────────────────────────────────────────
class RSBPF:
    """A decorated ranked binary path forest. forest = tuple of skeletons (multiset; order irrelevant for
    semantics but kept as a tuple). sigma = dict mapping (tree_index, addr2_path) -> GF(2) bit."""
    def __init__(self, forest, sigma=None):
        self.forest = tuple(forest)                       # multiset of skeletons
        # default decoration: 0 everywhere
        keys = self._addr2_keys()
        self.sigma = {k: 0 for k in keys}
        if sigma:
            for k, v in sigma.items():
                assert k in keys, f"sigma key {k} is not an Addr2 node"
                self.sigma[k] = v & 1
    def _addr2_keys(self):
        return frozenset((i, p) for i, T in enumerate(self.forest) for p in addr2_nodes(T))
    def rank(self):
        return max((rank_tree(T) for T in self.forest), default=0)
    def addr2(self):
        return self._addr2_keys()
    def __eq__(self, o):
        return isinstance(o, RSBPF) and self.forest == o.forest and self.sigma == o.sigma
    def __repr__(self):
        return f"RSBPF(rank={self.rank()}, |Addr2|={len(self.addr2())}, sigma={dict(self.sigma)})"

I = RSBPF(())                 # the monoidal unit: empty forest, rank 0, empty decoration

# ─────────────────────────────────────────────────────────────────────────────
# rank functor R : RSBPF -> (N, max, 0)
# ─────────────────────────────────────────────────────────────────────────────
def R(obj):
    """The rank functor on objects."""
    return obj.rank()

def rank_monoid_op(a, b):
    """(N, max, 0): the rank monoid operation."""
    return max(a, b)

RANK_UNIT = 0

# ─────────────────────────────────────────────────────────────────────────────
# monoidal product (X) = disjoint forest union; unit = I
# ─────────────────────────────────────────────────────────────────────────────
def tensor(A, B):
    """A (X) B = disjoint forest union; rank = max; sigma = union (reindexed). STRICT monoidal."""
    forest = A.forest + B.forest
    sigma = {}
    for (i, p), v in A.sigma.items():
        sigma[(i, p)] = v
    off = len(A.forest)
    for (i, p), v in B.sigma.items():
        sigma[(i + off, p)] = v
    return RSBPF(forest, sigma)

def braiding(A, B):
    """beta_{A,B}: A (X) B -> B (X) A, the swap of disjoint components. A symmetry: beta(B,A) o beta(A,B) = id."""
    return tensor(B, A)

# ─────────────────────────────────────────────────────────────────────────────
# GF(2) involutions: swap_p flips sigma at one binary node; Inv(F) = GF(2)^|Addr2(F)|
# ─────────────────────────────────────────────────────────────────────────────
def swap(obj, key):
    """swap_p: flip the parity at exactly the Addr2 node `key`=(tree_index, path). Self-inverse; rank- and
    sort-preserving (the tree shape is unchanged)."""
    assert key in obj.sigma, f"{key} is not an Addr2 node"
    s = dict(obj.sigma)
    s[key] ^= 1
    return RSBPF(obj.forest, s)

def involution_group_size(obj):
    """|Inv(F)| = 2^|Addr2(F)| -- the elementary abelian 2-group of decorations."""
    return 2 ** len(obj.addr2())

def apply_inv(obj, subset):
    """Apply the involution that flips exactly the Addr2 nodes in `subset` (a set of keys)."""
    o = obj
    for key in subset:
        o = swap(o, key)
    return o

# ─────────────────────────────────────────────────────────────────────────────
# canon + residue: the undecorated forest is canonical (lossy); sigma is the residue (lossless together)
# ─────────────────────────────────────────────────────────────────────────────
def canonicalize(obj):
    """Canonical form = the undecorated forest (sigma zeroed); residue = the original sigma. Lossy alone
    (forgets which alternative is active at each binary node); canonical + residue is lossless."""
    canon = RSBPF(obj.forest)                 # sigma defaults to 0 everywhere
    residue = dict(obj.sigma)
    return canon, residue

def recover(canon, residue):
    """Reattach the decoration: forest + sigma reproduces the original object."""
    return RSBPF(canon.forest, residue)
