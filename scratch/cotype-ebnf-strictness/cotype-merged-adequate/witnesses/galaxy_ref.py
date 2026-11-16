# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""GALAXY reference: Hierarchical Aggregation of Peer Counts (the corpus's actual recurrence).
The conformance checks f090_2_galaxy_* pin THIS. SOURCE-VERIFIED against echo/galaxy
(13DYcNMHxgWilHx5ZthcNVCEy6YNfH6nSVAbq6OTXLd4) -- the corpus mechanism is the BITSTREAM RECURRENCE,
not the Katz sum. (Katz/W_{v,k}=Sum alpha^{k-1}|N_k| is the report's EXTERNAL GROUNDING, a change-of-frame
reading gated separately in f090_2_galaxy_katz; both readings retained -- this ref is GALAXY-the-structure.)

HOW IT WORKS (decomposed, per source):
  Base (k=1): peer_count(v,1) = |neighbors(v)|  (number of immediate neighbors).
  Recursive (k>1): for node v,
    1. take the (k-1)-order peer counts of v's neighbors,
    2. SORT those neighbors by their bitstream representations (the binary reps of the lower-order counts),
    3. CONCATENATE the sorted bitstreams into a new bitstream,
    4. peer_count(v,k) = LENGTH of that new bitstream.
  The bitstream IS the multi-scale signature; its length is the aggregated order-k count.

This is the PIPELINE HEAD: it produces the per-node, per-order counts that the polar frame (weights),
CONSTELLATION (Bloom input), and HARMONY (comparison) consume.

CANON+RESIDUE (AI-CANON-RESIDUE, the per-ref obligation): the order-k COUNT (a length) is the canonical
form -- it aggregates the neighbor bitstreams and is LOSSY (many neighbor-arrangements give the same length).
The residue is the SORTED NEIGHBOR ORDER + their lower-order bitstreams -- exactly what the length discarded
-- enough to reconstruct the concatenated bitstream. count + residue is LOSSLESS. Conservation: aggregation
RELEASES the trivial 'each neighbor is identical/order-free' and the residue (which-neighbor-contributed-
which-bitstream, in sorted order) is the carried witness. triviality-out (neighbor identity) = witness-in.
"""

def _bits(n):
    """Binary representation of a nonneg count as a bitstring (the corpus's 'binary rep of peer count')."""
    return bin(n)[2:] if n > 0 else "0"

def peer_count(adj, v, k, _memo=None):
    """GALAXY order-k peer count for node v in adjacency dict adj. Returns the count (an int).
    Base (k=1): the count IS the number of neighbors (degree). Higher orders: the count is the LENGTH
    of the concatenated bitstream (per the source's recursive rule)."""
    if k == 1:
        return len(adj.get(v, []))          # order-1 count = degree (source: 'simply the number of neighbors')
    bs, _order = bitstream(adj, v, k, _memo)
    return len(bs)

def bitstream(adj, v, k, _memo=None):
    """Returns (bitstream, sorted_neighbor_order) for node v at order k.
    bitstream = the order-k signature; sorted_neighbor_order = the residue (which neighbors, in sort order)."""
    if _memo is None: _memo = {}
    if (v, k) in _memo: return _memo[(v, k)]
    if k == 1:
        # base: the order-1 count is the neighbor count; its bitstream is the binary rep of that count
        cnt = len(adj.get(v, []))
        result = (_bits(cnt), [])              # no neighbor-residue at the base
        _memo[(v, k)] = result; return result
    # recursive: gather neighbors' (k-1)-order bitstreams, sort neighbors by those bitstreams, concat
    neigh = adj.get(v, [])
    child = [(u, bitstream(adj, u, k-1, _memo)[0]) for u in neigh]
    child_sorted = sorted(child, key=lambda ub: (ub[1], ub[0]))   # sort by bitstream, then identity (total order)
    new_bs = "".join(bs for _u, bs in child_sorted)
    sorted_order = [u for u, _bs in child_sorted]                  # the residue
    result = (new_bs if new_bs else "0", sorted_order)
    _memo[(v, k)] = result; return result

def galaxy_signature(adj, v, kmax):
    """The full multi-scale signature: the list of order-1..kmax peer counts for node v.
    This is what the polar frame / CONSTELLATION / HARMONY consume."""
    memo = {}
    return [peer_count(adj, v, k, memo) for k in range(1, kmax+1)]

# ---- CANON + RESIDUE (lossless) ----
def canonicalize(adj, v, k):
    """canonical form = the order-k count (a length, lossy); residue = (sorted neighbor order, their
    (k-1)-bitstreams) -- enough to rebuild the concatenated bitstream and hence the count."""
    memo = {}
    bs, sorted_order = bitstream(adj, v, k, memo)
    count = len(bs)
    if k == 1:
        residue = ("base", len(adj.get(v, [])))     # base residue: the raw neighbor count
    else:
        child_bs = {u: bitstream(adj, u, k-1, memo)[0] for u in sorted_order}
        residue = ("rec", sorted_order, child_bs)    # which neighbors (sorted) + their lower-order bitstreams
    return count, residue

def recover_bitstream(residue):
    """Rebuild the order-k bitstream from the residue (proves count+residue is lossless: the bitstream,
    and hence the count = its length, is recovered)."""
    if residue[0] == "base":
        n = residue[1]; return _bits(n)
    _tag, sorted_order, child_bs = residue
    return "".join(child_bs[u] for u in sorted_order) or "0"
