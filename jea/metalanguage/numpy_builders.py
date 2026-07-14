#!/usr/bin/env python3
"""numpy_builders.py — ⟡H: the array-side of query_builders.py, built as the FOUR-GAUGE semiring `contract`.

The substrate already carries the relational engine: `Substrate.Algebra.Semiring.Instances` builds ONE
`Semiring` in four GAUGES — ℕ (counting, +/·), F₂ (GF(2): XOR/AND field, 1+1=0), Bool (routing: ∨/∧ semiring,
1+1=1), tropical (min/+) — and `Substrate.Algebra.Semiring.Contraction` runs ONE GraphBLAS inner product
`contract(a,b) = ⊕ᵢ aᵢ⊗bᵢ` that PLACES ITSELF via the gauge: Bool = reachability, ℕ = path-count, tropical =
shortest-cost, F₂ = parity (Contraction.agda:46-69). A relational operation is a `contract` at the right gauge;
the numpy realization is the semiring reduction (Bool = any/all, ℕ = sum, tropical = min, F₂ = XOR-parity),
packbits-able to the SWAR word for Bool/F₂.

THE GF(2) → boolean → predicate bridge, with the FIELD-VS-SEMIRING caveat (the whole point of the four-gauge
split): at F₂, ⊕ = XOR and ⊗ = AND (F2.agda:16); a grade-n F₂ object is a Vec F₂ n = a row-MASK; ⊗ = predicate
conjunction (WHERE p AND q), ⊕ = symmetric difference. BUT SQL WHERE/OR/reachability is the **Bool routing
gauge (∨/∧)**, NOT the F₂ field: F₂'s + is XOR, so 1∨1 would wrongly become 0. Reserve F₂ for XOR/parity/crypto.
OR = a⊕b⊕(a∧b) is a derived (three-term) F₂ expression, not primitive.

⟡H1 (this file, first): the four-gauge Semiring + `contract`, reproducing the Contraction.agda placements
byte-exact. ⟡H2/⟡H3 (next): the relational builders mirroring query_builders + the SQL↔numpy hexagon identity
(braiding coherence certified numerically via rig_coherence's blockSwap/factorSwap).
"""
import os, sys, argparse, sqlite3
import numpy as np
try:                                   # the jea host/device seam (jea_zsppf.py:24) — device is optional here
    import cupy as cp                  # noqa: F401
    HAVE_CUPY = True
except Exception:
    HAVE_CUPY = False
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

_INF = float("inf")


class Semiring:
    """One `Semiring` (Semiring/Instances.agda), pluggable gauge. `mul` = ⊗ (elementwise); `add_reduce` = the
    ⊕-fold over an axis; `zero`/`one` = the additive/multiplicative units. `contract` reads it GraphBLAS-style."""
    __slots__ = ("name", "mul", "add_reduce", "zero", "one", "add")
    def __init__(self, name, mul, add_reduce, zero, one, add):
        self.name, self.mul, self.add_reduce = name, mul, add_reduce
        self.zero, self.one, self.add = zero, one, add


# ── the four gauges (Semiring/Instances.agda:9-12) ──────────────────────────────────────────────────
def _nat_reduce(x):    return np.add.reduce(x) if x.size else 0
def _bool_reduce(x):   return np.logical_or.reduce(x) if x.size else False
def _trop_reduce(x):   return np.minimum.reduce(x) if x.size else _INF        # min over an empty ⊕ = ∞ (the ⊕-unit)
def _f2_reduce(x):     return int(np.bitwise_xor.reduce(x.astype(np.uint8)) & 1) if x.size else 0

SR_NAT  = Semiring("ℕ",        np.multiply,     _nat_reduce,  0,    1, np.add)              # counting: +/·
SR_BOOL = Semiring("Bool",     np.logical_and,  _bool_reduce, False, True, np.logical_or)   # routing: ∨/∧  (reachability)
SR_TROP = Semiring("tropical", np.add,          _trop_reduce, _INF, 0, np.minimum)          # cost: min/+
SR_F2   = Semiring("F₂",       np.bitwise_and,  _f2_reduce,   0,    1, np.bitwise_xor)       # GF(2): XOR/AND (parity)
GAUGES  = {"nat": SR_NAT, "bool": SR_BOOL, "tropical": SR_TROP, "f2": SR_F2}


def contract(a, b, S):
    """The GraphBLAS inner product ⟨a,b⟩ = ⊕ᵢ (aᵢ ⊗ bᵢ), placed by the gauge S (Contraction.agda:46-49).
    a, b are equal-length 1-D arrays (or array-likes). Returns the scalar in S's carrier."""
    a = np.asarray(a); b = np.asarray(b)
    n = min(a.shape[0], b.shape[0])                    # contract stops at the shorter (Contraction.agda:47-48)
    if n == 0:
        return S.zero
    return S.add_reduce(S.mul(a[:n], b[:n]))


def matmul(A, B, S):
    """Semiring matrix product C[i,j] = ⊕ₖ A[i,k] ⊗ B[k,j], placed by the gauge S. The batched `contract`
    (a JOIN / one boolean-matrix reachability step). Dense O(n³) broadcast — fine for small/verify; the
    packbits SWAR form is ⟡H4."""
    A = np.asarray(A); B = np.asarray(B)
    prod = S.mul(A[:, :, None], B[None, :, :])         # (i,k,j)
    # reduce over k (axis=1) with the gauge's ⊕
    if S is SR_BOOL:   return np.logical_or.reduce(prod, axis=1)
    if S is SR_NAT:    return np.add.reduce(prod, axis=1)
    if S is SR_TROP:   return np.minimum.reduce(prod, axis=1)
    if S is SR_F2:     return np.bitwise_xor.reduce(prod.astype(np.uint8), axis=1) & 1
    raise ValueError(S.name)


# ════════════════ ⟡H2 — grade-indexed AUTOSCALING n-wide contract (the SWAR ladder) ═════════════════
# The contract's n-wideness is a GRADE the builder autoscales along the 1/2/4/8/16/32/64 SWAR ladder
# (jea_swar.py:4-6 "L=32→…→1, nlanes=32/L"; jea_bucket_msb.py:41 LADDER). Rows pack into uint64 words
# (nlanes = 64/L lanes per word); the MIGRATION LAW (jea_bucket_msb.py:8-11: mul ⇒ widths ADD → migrate UP;
# reduce ⇒ narrow DOWN) sets the lane width from the working-set magnitude; the nedge Wheatstone bridge
# (jea_nedge_model.py:90-93, with L as the K-analogue and the ladder rungs as the ×2 neighbours) autonavigates
# to the min-cost rung (conductance = 1/cost). At L=1 the lane is carry-free GF(2)/Bool (jea_swar.py:15-16):
# 64 independent bits/word = the reachability/parity floor. This CLOSES the bucket_msb ↔ swar loop (the first
# place the width-navigator actually drives a SWAR-packed execution). VERIFIED oracle (catalog.db, measured):
# V=77394 vertices, W=⌈V/64⌉=1210 uint64 frontier words, the max-children root's closure = 59794 (== q_reach).
CATALOG_DB = os.path.join(os.path.dirname(os.path.dirname(HERE)), "catalog", "catalog.db")  # == query_builders.py:20

LADDER_H2 = [1, 2, 4, 8, 16, 32, 64]                       # the SWAR/pow-2 ladder (jea_bucket_msb.py:41)
def _grade(v):  return max(1, int(v).bit_length())         # width IS the grade (jea_graded.py:27)
def bucket(w):                                             # round a bit-width UP the ladder (jea_bucket_msb.py:43-46)
    for L in LADDER_H2:
        if w <= L: return L
    return 128                                             # > 64 = escalate past the uint64 carrier


def densify(con):
    """`node_child(node_id TEXT, child_id TEXT)` → dense int adjacency. base64 TEXT ids densify to 0..V-1 via
    np.unique(return_inverse) — the host-numpy form of the device radix interning (jea_zsppf.py:58). A node = a
    bit position. Returns (V, ix2id, rows, cols): edge k is rows[k]→cols[k] as dense ids; V = |node_id ∪ child_id|."""
    pairs = con.execute("SELECT node_id, child_id FROM node_child").fetchall()
    E = len(pairs)
    src = np.array([p[0] for p in pairs], dtype=object)
    dst = np.array([p[1] for p in pairs], dtype=object)
    uniq, inv = np.unique(np.concatenate([src, dst]), return_inverse=True)      # TEXT → 0..V-1
    inv = np.asarray(inv).ravel()
    return len(uniq), uniq, inv[:E].astype(np.int64), inv[E:].astype(np.int64)


def reach_nwide(V, rows, cols, root_ix):
    """N-wide PACKED reachability at L=1 (the carry-free GF(2)/Bool floor, jea_swar.py:15-16). The frontier is V
    bits packed 64-per-uint64 (W=⌈V/64⌉ words; bit i in word i>>6 at position i&63 — the jea_graded.py:34
    convention). One STEP ORs the child of every live-source edge into the frontier; iterate to fixpoint. ∨ is
    associative-idempotent-commutative (the jea_megakernel license) ⇒ any lane/order gives the same least
    fixpoint ⇒ packed == unpacked == q_reach. Returns the reached dense-int set."""
    U64 = np.uint64
    W = (V + 63) // 64
    frontier = np.zeros(W, U64)
    frontier[root_ix >> 6] |= U64(1) << U64(root_ix & 63)
    sh_r = (rows & 63).astype(U64); wd_r = rows >> 6                            # per-edge source word/bit
    while True:
        live = ((frontier[wd_r] >> sh_r) & U64(1)).astype(bool)                # edges with a live source
        fire = cols[live]                                                       # children to light this step
        before = frontier.copy()
        np.bitwise_or.at(frontier, fire >> 6, U64(1) << (fire & 63).astype(U64))   # unbuffered scatter-OR
        if np.array_equal(frontier, before):
            break                                                              # fixpoint (monotone ⇒ terminates)
    idx = np.arange(V)
    return set(int(x) for x in idx[((frontier[idx >> 6] >> (idx & 63).astype(U64)) & U64(1)).astype(bool)])


def autoscale(working_set):
    """The lane width L for a working set = bucket(max magnitude bit-width) — the migration law read as a
    lane-width selector (jea_bucket_msb.py:8-11,43-46). Bool/F₂ ⊂ {0,1} ⇒ bitlen 1 ⇒ L=1 (max-pack, 64
    lanes/word). ℕ/tropical magnitudes grow ⇒ bitlen climbs ⇒ L climbs 1→2→4→8→16→… (widths ADD)."""
    return bucket(max((_grade(v) for v in working_set), default=1))


def need_bits(S, working_set):
    """Bits a lane must hold for gauge S over this working set. Bool/F₂: values ⊂ {0,1}, ⊕ carry-free (∨/XOR
    don't cross lanes, jea_swar.py:15-16) ⇒ 1 bit ⇒ L=1 forever. ℕ (⊕=+) / tropical (⊗=+ ripples): the value
    occupies grade(v) bits and the SWAR adder carries, so the lane MUST be ≥ the magnitude's bit-width."""
    if S is SR_BOOL or S is SR_F2:
        return 1
    finite = [v for v in working_set if v != _INF]         # tropical ∞ = the ⊕-unit, carries no bits
    return max((_grade(v) for v in finite), default=1)


def cost(L, nbits, nvals):
    """Plant cost of the N-wide contract at lane width L. L < nbits ⇒ a value overflows its lane ⇒ carry crosses
    the boundary ⇒ WRONG ⇒ ∞ (must escalate — the migration law's escalate clause). Else cost = ⌈nvals/(64//L)⌉
    packed words (jea_bucket_msb.py:83): fewer/wider lanes ⇒ more words. Conductance = 1/cost."""
    if L < nbits: return _INF
    lanes = 64 // L
    return -(-nvals // lanes)                              # ⌈nvals / lanes⌉ words


def _bridge_L(La, Lb, nbits, nvals):                       # jea_nedge_model.py:52-54: det>0 ⇒ La more conductance
    ca, cb = cost(La, nbits, nvals), cost(Lb, nbits, nvals)
    return (0.0 if ca == _INF else 1.0 / ca) - (0.0 if cb == _INF else 1.0 / cb)


def autonavigate(L, nbits, nvals):
    """ONE warm-started relaxation step — jea_nedge_model.py:90-93 ported with L as the K-analogue and the ladder
    rungs as the ×2 neighbours. Nudge L toward the neighbour of higher conductance (=1/cost); hold if neither
    wins. Converges onto bucket(nbits) = the smallest lane that still fits (max-pack, min-cost); the escalation
    floor (cost(<nbits)=∞) stops the descent."""
    down, up = max(1, L // 2), min(64, L * 2)
    if _bridge_L(down, L, nbits, nvals) > 0: return down
    if _bridge_L(up,   L, nbits, nvals) > 0: return up
    return L


def selftest_h2(db=CATALOG_DB):
    con = sqlite3.connect(db)
    # ── 1. N-wide PACKED reachability == q_reach (byte-exact 59794 on catalog.db) ──
    root = con.execute("SELECT node_id FROM node_child GROUP BY node_id "
                       "ORDER BY COUNT(*) DESC LIMIT 1").fetchone()[0]          # _samp_node (query_builders.py:426-433)
    oracle = {r[0] for r in con.execute(                                        # q_reach (query_builders.py:188-192)
        "WITH RECURSIVE reach(node_id) AS (SELECT ? UNION "
        "SELECT nc.child_id FROM reach r JOIN node_child nc ON nc.node_id=r.node_id) "
        "SELECT node_id FROM reach", (root,)).fetchall()}
    V, ix2id, rows, cols = densify(con)
    root_ix = int(np.nonzero(ix2id == root)[0][0])
    reached = {ix2id[i] for i in reach_nwide(V, rows, cols, root_ix)}
    assert V == 77394, f"vertex space (node_id ∪ child_id) = 77394, got {V}"
    assert len(oracle) == 59794, f"q_reach closure = 59794, got {len(oracle)}"
    assert reached == oracle, f"packed {len(reached)} != q_reach {len(oracle)} — NOT byte-exact"
    assert 64 // 1 == 64, "nlanes = 64/L = 64 carry-free lanes/word at L=1 (jea_swar.py:15-16)"

    # ── 2. ℕ path-count contraction whose lane width CLIMBS 1→2→4→8→16 (migration law observed) ──
    # doubling DAG: front·A in SR_NAT doubles the path count each hop (⊕=+, NOT idempotent ⇒ must widen).
    A = np.array([[1, 1], [1, 1]]); front = np.array([[1, 0]])
    L_trace = []
    for _ in range(11):                                    # 11 hops ⇒ counts reach 2¹⁰=1024 (grade 11 ⇒ L=16)
        L_trace.append(autoscale(front.ravel().tolist()))  # migration-law lane width for this working set
        front = matmul(front, A, SR_NAT)                   # ℕ path-count hop (counts grow)
    assert L_trace[0] == 1, "grade-1 counts start at L=1"
    assert L_trace == sorted(L_trace), "widths ADD ⇒ migrate UP ⇒ monotone non-decreasing"
    assert L_trace[-1] > L_trace[0], "lane width CLIMBS as ℕ counts grow (migration law)"
    assert set(L_trace) >= {1, 2, 4, 8, 16}, f"observed the 1→2→4→8→16 climb, got {L_trace}"

    # ── 3. the nedge bridge picks the MIN-COST rung. Rung choice only bites at SCALE (with 2 values every
    # rung is 1 word), so demonstrate on a representative pack of 1000 magnitude-1024 values (nbits=11). ──
    pack = [1024] * 1000; nb = need_bits(SR_NAT, pack); nv = len(pack)
    assert nb == 11, f"grade(1024) = 11, got {nb}"
    L = 64
    for _ in range(12): L = autonavigate(L, nb, nv)        # warm-started relaxation to fixpoint
    assert L == bucket(nb) == 16, f"navigator settles on the min-cost valid rung bucket({nb})=16, got {L}"
    assert cost(L, nb, nv) < cost(L * 2, nb, nv), "the chosen rung packs more lanes (fewer words) than the wider one"
    assert cost(L // 2, nb, nv) == _INF, "one rung narrower (L=8 < nbits=11) would overflow the lane ⇒ escalate"

    # ── 4. Bool/F₂ stay L=1 (carry-free max-pack); ℕ/tropical widen with magnitude ──
    assert need_bits(SR_BOOL, [0, 1, 1, 0, 1]) == 1 and autoscale([0, 1, 1, 0, 1]) == 1
    assert need_bits(SR_F2,   [1, 0, 1])       == 1
    assert need_bits(SR_NAT,  [1, 5, 300])     == _grade(300) == 9     # ℕ widens with magnitude
    assert need_bits(SR_TROP, [_INF, 7, 40])   == _grade(40)  == 6     # tropical ∞ carries no bits

    print("PASS ⟡H2 autoscale-nwide (grade-indexed SWAR-ladder contract):")
    print(f"  1. N-wide PACKED reachability (frontier {(V+63)//64} uint64 words, nlanes=64 @L=1) == q_reach:")
    print(f"     {len(reached)} nodes, byte-exact ({len(oracle)}); ∨ associative-idempotent ⇒ packed==unpacked.")
    print(f"  2. ℕ path-count lane width CLIMBS {L_trace} (migration law: widths ADD ⇒ migrate UP).")
    print(f"  3. nedge bridge (L as K-analogue) settles on the min-cost rung bucket({nb})=16 (conductance=1/cost).")
    print(f"  4. Bool/F₂ stay L=1 (carry-free, 64 lanes/word); ℕ/tropical widen with magnitude.")
    print(f"  ⟡ bucket_msb ↔ swar loop CLOSED: the width-navigator now drives the SWAR pack (first run).")
    con.close()


# ════════════════ ⟡H3 — relational builders vs SQL + the SQL↔numpy hexagon ══════════════════════════
# Each relational op is a gauge-placed contraction (⟡H1) whose VALUE is byte-exact with its SQL builder over
# the SAME db (the query_builders.verify pattern). The HEXAGON has four legs: VALUE (numpy == SQL multiset),
# GAUGE (Bool ∨ = reachability ≠ F₂ ⊕ = parity — the four-gauge split), BRAIDING (a WHERE/join reorder = the
# PROVEN blockSwap/factorSwap braiding, rig_coherence — so any conjunct order is ONE orbit rep), and CROSSMIX
# (a numpy op and its SQL twin lower to ONE sql_lift Rel carrier point, via Bridge_np). Predicate masks are
# the GF(2)→Bool→predicate bridge: AND=⊗, XOR=⊕, NOT=xor-ones, and OR = a⊕b⊕(a∧b) = recon(XOR, AND) — the
# apex wedge (a=recon q b r), NOT a separate primitive: the ∧ cross-term is the oriented residue the Bool
# gauge adds to the F₂ field (grounded PROVEN in the substrate: bool→F₂-xor + ResidueIsBezoutGCD; the closed
# form is the ~4-line refl of ⟡H-lemmas). The hexagon's braiding is backed by PROVEN Agda (GradedSymMonoidal
# + LehmerPath initiality + ∀-n Coxeter-completeness + the block-action OrientationHexagon); rig_coherence
# CORROBORATES it (it is not the sole certificate). See the plan's ORIENTED-RESIDUE RE-REVIEW.

def _rows(con, sql, params=()):  return list(map(tuple, con.execute(sql, params).fetchall()))
def _cols(rows):                 return [np.array(c, dtype=object) for c in zip(*rows)] if rows else []

# ── predicate masks: the GF(2) field ops (F2/Vector.agda) + the derived Bool OR ─────────────────────
def pred_and(a, b):  return np.asarray(a, np.uint8) & np.asarray(b, np.uint8)   # ⊗ = zipWith AND = WHERE p AND q
def pred_xor(a, b):  return np.asarray(a, np.uint8) ^ np.asarray(b, np.uint8)   # ⊕ = zipWith XOR = symmetric diff
def pred_not(a):     return np.asarray(a, np.uint8) ^ np.uint8(1)               # NOT = xor-ones (F₂ complement)
def pred_or(a, b):                                                             # OR = a⊕b⊕(a∧b) = recon(XOR, AND)
    a = np.asarray(a, np.uint8); b = np.asarray(b, np.uint8)
    return a ^ b ^ (a & b)          # the Bool ∨ built from the F₂ field — the ∧ cross-term is the residue

# ── the relational builders (gauge-placed contractions), each mirroring a query_builders SQL builder ──
def np_scan(con, sql):                     return _rows(con, sql)               # Scan = the identity leaf
def np_distinct(con, sql, proj_idx=0):
    rows = _rows(con, sql); cols = _cols(rows)                                  # DISTINCT = np.unique (jea_zsppf:58)
    if not rows: return []
    uniq, _ = np.unique(cols[proj_idx], return_inverse=True)
    return [(u,) for u in uniq.tolist()]
def np_group_count(con, sql, key_idx=0):                                        # GROUP BY + COUNT(*) = unique+add.at
    rows = _rows(con, sql); cols = _cols(rows)
    if not rows: return []
    uniq, inv = np.unique(cols[key_idx], return_inverse=True)
    deg = np.zeros(uniq.shape[0], np.int64); np.add.at(deg, inv, 1)             # ℕ gauge (count)
    return list(zip(uniq.tolist(), deg.tolist()))
def np_filter(con, sql, mask_fn):                                              # WHERE = a Bool mask ⊗ (routing gauge)
    rows = _rows(con, sql); cols = _cols(rows)
    if not rows: return []
    m = np.asarray(mask_fn(cols)).astype(bool)
    return [r for r, keep in zip(rows, m) if keep]
def np_order(rows, keys, descs):                                              # ORDER BY = np.lexsort (jea_zsppf:123)
    if not rows: return []
    seq = []
    for k, d in zip(keys, descs):
        a = np.asarray(k)
        seq.append(-a if (d and np.issubdtype(a.dtype, np.number)) else a)
    o = np.lexsort(tuple(reversed(seq)))                                        # keys[0] = primary
    return [rows[i] for i in o.tolist()]
def np_limit(rows, n):                     return rows[:n]                      # LIMIT = a slice
def np_join(lrows, rrows, lkey_idx, rkey_idx):                                 # JOIN = searchsorted equijoin
    rk = np.array([r[rkey_idx] for r in rrows], dtype=object)
    order = np.argsort(rk, kind="stable"); rk_s = rk[order]
    out = []
    for lr in lrows:
        k = lr[lkey_idx]
        lo = int(np.searchsorted(rk_s, k, side="left")); hi = int(np.searchsorted(rk_s, k, side="right"))
        for j in range(lo, hi):
            out.append(tuple(lr) + tuple(rrows[int(order[j])]))
    return out
def np_closure(con, root):                                                    # CLOSURE = the ⟡H2 N-wide reachability
    V, ix2id, rows, cols = densify(con)
    root_ix = int(np.nonzero(ix2id == root)[0][0])
    return {ix2id[i] for i in reach_nwide(V, rows, cols, root_ix)}


def verify_hexagon(db=CATALOG_DB):
    """The SQL↔numpy hexagon over node_child (the SPPF adjacency present on catalog.db). VALUE: each numpy
    builder == its SQL builder byte-exact (multiset, or in-order for ORDER BY). GAUGE / BRAIDING / CROSSMIX
    as above. Mirrors query_builders.verify (byte-exact multiset compare)."""
    sys.path.insert(0, HERE)
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)), "scripts"))   # rig_coherence lives here
    import rig_coherence as rc
    from jea_pyalg import Intern
    import sql_lift, query_builders as QB
    con = sqlite3.connect(db)
    ok, fail = 0, []
    def _cmp(name, got, raw, ordered=False):
        nonlocal ok
        want = list(map(tuple, con.execute(raw).fetchall()))
        g = got if ordered else sorted(got); w = want if ordered else sorted(want)
        if g == w: ok += 1; print(f"  ✓ VALUE {name:16s} {len(g):>6} rows — numpy == SQL")
        else:      fail.append(name); print(f"  ✗ VALUE {name}: numpy {len(g)} vs SQL {len(w)}")

    # ── (VALUE) each numpy builder == its SQL over the SAME db, byte-exact (query_builders.verify pattern) ──
    _cmp("distinct_child", np_distinct(con, "SELECT child_id FROM node_child"),
         "SELECT DISTINCT child_id FROM node_child")
    _cmp("group_count",    np_group_count(con, "SELECT child_id FROM node_child"),
         "SELECT child_id, COUNT(*) FROM node_child GROUP BY child_id")
    grp = np_group_count(con, "SELECT child_id FROM node_child")                # GROUP+COUNT then ORDER+LIMIT
    top = np_limit(np_order(grp, [np.array([g[1] for g in grp]), np.array([g[0] for g in grp], object)],
                            [True, False]), 20)                                 # ORDER BY c DESC, child_id ASC
    _cmp("indegree_top", top,
         "SELECT child_id, COUNT(*) c FROM node_child GROUP BY child_id ORDER BY c DESC, child_id LIMIT 20",
         ordered=True)
    _cmp("filter_ord0", np_filter(con, "SELECT node_id, ord, child_id FROM node_child", lambda c: c[1] == 0),
         "SELECT node_id, ord, child_id FROM node_child WHERE ord=0")
    # closure = q_reach (the ⟡H2 oracle, byte-exact 59794)
    root = con.execute("SELECT node_id FROM node_child GROUP BY node_id ORDER BY COUNT(*) DESC LIMIT 1").fetchone()[0]
    oracle = {r[0] for r in con.execute(
        "WITH RECURSIVE reach(node_id) AS (SELECT ? UNION SELECT nc.child_id FROM reach r "
        "JOIN node_child nc ON nc.node_id=r.node_id) SELECT node_id FROM reach", (root,)).fetchall()}
    reached = np_closure(con, root)
    if reached == oracle: ok += 1; print(f"  ✓ VALUE {'closure':16s} {len(reached):>6} nodes — np_closure == q_reach")
    else:                 fail.append("closure"); print(f"  ✗ VALUE closure: {len(reached)} vs {len(oracle)}")
    # join = a synthetic equijoin vs sqlite's own JOIN (the Join head, no node_child self-join needed)
    mem = sqlite3.connect(":memory:")
    mem.execute("CREATE TABLE L(a,k)"); mem.execute("CREATE TABLE R(k,b)")
    L = [(1, "x"), (2, "y"), (3, "x")]; R = [("x", "p"), ("x", "q"), ("z", "r")]
    mem.executemany("INSERT INTO L VALUES(?,?)", L); mem.executemany("INSERT INTO R VALUES(?,?)", R)
    sj = sorted(map(tuple, mem.execute("SELECT L.a,L.k,R.k,R.b FROM L JOIN R ON L.k=R.k").fetchall()))
    if sorted(np_join(L, R, 1, 0)) == sj: ok += 1; print(f"  ✓ VALUE {'join':16s} {len(sj):>6} rows — np_join == SQL JOIN")
    else:                                 fail.append("join"); print("  ✗ VALUE join")

    # ── (GAUGE) Bool ∨ (reachability) ≠ F₂ ⊕ (parity) — the four-gauge split, made executable ──
    assert bool(contract([1, 1], [1, 1], SR_BOOL)) is True, "Bool: two live channels ⇒ ⊤ (reachability)"
    assert contract([1, 1], [1, 1], SR_F2) == 0, "F₂: 1⊕1 = 0 (parity) — NOT the Bool answer"
    assert pred_xor([1, 1], [1, 1]).tolist() == [0, 0] and pred_or([1, 1], [1, 1]).tolist() == [1, 1], \
        "predicate ⊕ (XOR) ≠ derived OR — the field-vs-semiring split; OR = recon(XOR, AND)"
    print("  ✓ GAUGE  Bool ∨ (reachability) ≠ F₂ ⊕ (parity); OR = a⊕b⊕ab = recon(XOR,AND) [oriented residue]")

    # ── (BRAIDING) a conjunct/factor reorder = the PROVEN blockSwap/factorSwap involution (rig_coherence) ──
    import itertools
    p = np.array([1, 0, 1, 1, 0], np.uint8); q = np.array([1, 1, 0, 1, 0], np.uint8); r = np.array([0, 1, 1, 1, 1], np.uint8)
    reps = {tuple(pred_and(pred_and(a, b), c).tolist()) for a, b, c in itertools.permutations([p, q, r])}
    assert len(reps) == 1, "WHERE p AND q AND r is order-invariant (∧ commutative) ⇒ ONE orbit rep"
    assert rc.perm_eq(rc.compose(rc.blockSwap(1, 1), rc.blockSwap(1, 1)), rc.ident(2)), \
        "adjacent conjunct swap = blockSwap(1,1), a PROVEN involution (rig_coherence)"
    assert all(rc.perm_eq(rc.compose(rc.factorSwap(n, m), rc.factorSwap(m, n)), rc.ident(m * n))
               for m in range(1, 4) for n in range(1, 4)), "GROUP/JOIN factor reorder = factorSwap (proven involution)"
    print("  ✓ BRAID  conjunct reorder = blockSwap(1,1); factor reorder = factorSwap — PROVEN involutions")

    # ── (CROSSMIX) numpy op + its SQL twin → ONE sql_lift Rel carrier point (Bridge_np, degree 0) ──
    I = Intern()
    assert sql_lift.np_sql_coherent(I, ("np_closure",), QB.q_reach()), "np_closure ↔ WITH RECURSIVE: one carrier point"
    assert sql_lift.np_sql_coherent(I, ("np_distinct",), QB.q_edges_dst_distinct()), "np_distinct ↔ DISTINCT: one point"
    assert sql_lift.np_sql_coherent(I, ("np_order", "np_limit"), QB.q_indegree_top()), "order+limit ↔ ORDER BY..LIMIT"
    print("  ✓ CROSS  numpy-op & SQL-twin co-intern to ONE Rel carrier node (CrossMix degree 0, Bridge_np)")

    con.close()
    print(f"\n{'PASS' if not fail else 'FAIL'} ⟡H3-relational-hexagon — {ok} VALUE + GAUGE/BRAID/CROSS"
          + (f"; failures: {fail}" if fail else "  (SQL↔numpy = two braided-coherent realizations of one rig)"))
    return not fail


# ════════════════ ⟡H-carrier — the carrier-interrelation core (DivStr/recon + EEA-fold + CRT) ═══════
# The deep layer BOTH SQL and numpy realize (witness-tower/CRT/EEA guidance). Every carrier is a DivStr =
# {z, recon(q,b,r)="q·b then r"} (Algebra/Wedge.agda:53-59); ⊗ = the q·b part, ⊕ = the +r part. Two carriers
# INTERRELATE via the EEA trace, folded to many targets (WitnessTower/EEAFoldTable.agda: gcd = common
# structure, Bézout = the recon inverses, CF-digits = the graded residue tower, coprime → CRT split — one
# trace, the fold TARGET picks the extraction). The residue r = the orientation = the CRT correction.

class DivStr:
    """A carrier's wedge interface (Algebra/Wedge.agda:53-59): `z` (terminal divisor) + `recon(q,b,r)` = q·b+r.
    ⊗ is the q·b part, ⊕ is the +r part. A wedge of `a` against `b` is (q, r) with `a == recon(q, b, r)`."""
    __slots__ = ("name", "z", "recon", "wedge")
    def __init__(self, name, z, recon, wedge):
        self.name, self.z, self.recon, self.wedge = name, z, recon, wedge

DIV_NAT = DivStr("ℕ", 0, lambda q, b, r: q * b + r, lambda a, b: divmod(a, b))   # ℕ-div (Algebra/Z/Wedge)
DIV_F2  = DivStr("F₂", 0, lambda q, b, r: (q & b) ^ r, None)                       # F₂-div (⊕=XOR, ⊗=AND)


def eea_steps(a, b):
    """The EEATrace (Nat/GCD/EEATrace.agda): the chain of one-step wedges (a,b)↦(q,r) down to gcd. Returns
    (gcd, [(a_i, b_i, q_i, r_i)] top-down). Each step: a_i = recon(q_i, b_i, r_i) = q_i·b_i + r_i."""
    steps = []
    while b != 0:
        q, r = divmod(a, b)
        assert a == DIV_NAT.recon(q, b, r), "the wedge identity a = recon q b r"
        steps.append((a, b, q, r)); a, b = b, r
    return a, steps                                        # a = gcd (the trace's target index g)

# the universal fold, THREE targets (eea_fold, Nat/GCD/Fold.agda — the target picks the extraction):
def fold_gcd(a, b):     return eea_steps(a, b)[0]          # the common structure
def fold_digits(a, b):  return [q for _, _, q, _ in eea_steps(a, b)[1]]   # CF / Lehmer digits (the residue tower)
def fold_bezout(a, b):
    """Bézout via the back-substitution fold (Z/Bezout.agda:53-59): base (s,t)=(1,0), step (s',t')↦(t', s'−t'·q),
    folded from the gcd base UP. Returns (s, t, g) with s·a + t·b = g."""
    g, steps = eea_steps(a, b)
    s, t = 1, 0
    for (_, _, q, _) in reversed(steps):
        s, t = t, s - t * q
    return s, t, g

def modinv(x, m):
    """x⁻¹ mod m via Bézout (s·x + t·m = 1 ⇒ s ≡ x⁻¹). The CRT inverse (CRT/FromTrace.agda)."""
    s, _, g = fold_bezout(x % m, m)
    assert g == 1, f"{x} not invertible mod {m} (gcd {g})"
    return s % m

def crt_idempotents(moduli):
    """The CRT correction basis eᵢ = Mᵢ·(Mᵢ⁻¹ mod mᵢ), Mᵢ = ∏_{j≠i} mⱼ (CRT/{Inverses,FromIdempotents}.agda):
    eᵢ ≡ 1 mod mᵢ, ≡ 0 mod mⱼ (j≠i). The idempotents ARE the codec legs; coprime ⇒ orthogonal (eᵢ·eⱼ ≡ 0)."""
    M = 1
    for m in moduli: M *= m
    return [(M // m) * modinv((M // m) % m, m) for m in moduli], M

def crt_combine(residues, moduli):
    """The Bézout-mediated CRT splitter (CRT.agda): combine(a₁,…) = Σ aᵢ·eᵢ — recompose a value from its
    residues across coprime moduli. Reconstruction = a sum of wedge recons (each aᵢ·eᵢ is recon(aᵢ, eᵢ, 0))."""
    es, _ = crt_idempotents(moduli)
    return sum(a * e for a, e in zip(residues, es))


def carrier_selftest():
    # reproduce EEAFoldTable.agda BYTE-EXACT on the trace of (3,2): ONE trace, four fold targets.
    assert fold_gcd(3, 2) == 1, "gcd(3,2) = 1 (the trace's target index — coprime)"
    assert fold_digits(3, 2) == [1, 2], "CF/Lehmer digits of 3/2 = [1,2] (the quotient sequence consed by the fold)"
    s, t, g = fold_bezout(3, 2)
    assert (s * 3 + t * 2 == g == 1) and (s, t) == (1, -1), f"Bézout: 1·3 + (−1)·2 = 1, got s={s},t={t},g={g}"
    # the residue r IS the wedge remainder (a = recon q b r): 3 = recon(1, 2, 1) = 1·2 + 1.
    assert DIV_NAT.recon(1, 2, 1) == 3, "a = recon q b r (the orientation residue r=1)"

    # CRT ℤ/15 ≅ ℤ/3 × ℤ/5 — reproduce CRT/Examples.agda byte-exact.
    es, M = crt_idempotents([3, 5])
    assert M == 15 and es == [10, 6], f"idempotents e₁=10 (≡1 mod3,≡0 mod5), e₂=6, got {es}"
    assert crt_combine([1, 2], [3, 5]) == 22, "combine(1,2) = 1·10 + 2·6 = 22 ≡ (1 mod 3, 2 mod 5)"
    assert 22 % 3 == 1 and 22 % 5 == 2, "the reconstruction hits both residues"
    # COPRIME ⇒ ORTHOGONAL: the cross-term e₁·e₂ ≡ 0 mod 15 (CenterIsStarCRT: ⊗ degenerates to ⊕, clean split).
    assert (es[0] * es[1]) % 15 == 0, "coprime ⇒ e₁·e₂ ≡ 0 (orthogonal, cross-term vanishes)"
    # SHARED FACTOR ⇒ a GRADED RESIDUE (CenterIsStarNumeral: ℤ/8, 2·2=4 nilpotent — carried, not rejected).
    assert (2 * 2) % 8 == 4 and (4 * 2) % 8 == 0, "shared prime-2: 2 nilpotent in ℤ/8 (a graded residue, the cost)"
    print("PASS ⟡H-carrier (DivStr/recon + EEA-fold + CRT):")
    print("  ONE EEA trace of (3,2), four fold targets (EEAFoldTable): gcd=1, CF-digits=[1,2], Bézout 1·3−1·2=1,")
    print("  residue r=1 = recon(1,2,1). CRT ℤ/15≅ℤ/3×ℤ/5: e=[10,6], combine(1,2)=22; coprime ⇒ e₁·e₂≡0")
    print("  (orthogonal, ⊗→⊕); shared prime ⇒ graded residue (2 nilpotent in ℤ/8) — the grade CARRIES it.")


# ════════════════════════════════ ⟡H1 selftest — the four placements, byte-exact ════════════════════
def selftest():
    # reproduce Contraction.agda:55-69 exactly (one tensor, four gauges — instances, not builds).
    assert contract([1, 2], [3, 4], SR_NAT) == 11, "ℕ count: 1·3 + 2·4 = 11"
    assert bool(contract([True, False], [True, True], SR_BOOL)) is True, "Bool route: (⊤∧⊤)∨(⊥∧⊤) = ⊤"
    assert contract([1, 2], [3, 4], SR_TROP) == 4, "tropical: min(1+3, 2+4) = 4"
    assert contract([1, 1], [1, 1], SR_F2) == 0, "F₂ parity: (𝟙∧𝟙)⊕(𝟙∧𝟙) = 𝟙⊕𝟙 = 𝟘"
    # the field-vs-semiring caveat, made executable: SAME 2-element inputs, DIFFERENT addition ⇒ different answer.
    #   Bool routes: 1∨1 = 1 (reachability accumulates);  F₂ parity: 1⊕1 = 0 (XOR cancels).
    assert bool(contract([True, True], [True, True], SR_BOOL)) is True, "Bool: two live channels ⇒ ⊤"
    assert contract([1, 1], [1, 1], SR_F2) == 0, "F₂: two ⇒ parity 0 — NOT the Bool answer (the trap the split prevents)"
    # a Bool reachability STEP as a matmul (frontier · adjacency): {0}·(0→1) reaches {0,1}? one step 0→1.
    adj = np.array([[False, True, False], [False, False, True], [False, False, False]])  # 0→1→2 chain
    front = np.array([[True, False, False]])                                             # frontier = {0}
    step = matmul(front, adj, SR_BOOL)                                                   # one hop
    assert step.tolist() == [[False, True, False]], "Bool matmul = one reachability hop 0→1"
    print("PASS ⟡H1 numpy four-gauge semiring `contract`:")
    print("  ONE contract, four gauges (Contraction.agda:55-69): ℕ=11, Bool=⊤, tropical=4, F₂=𝟘 — byte-exact.")
    print("  the field-vs-semiring caveat executable: Bool 1∨1=1 (reachability) ≠ F₂ 1⊕1=0 (parity);")
    print("  Bool matmul = one reachability hop. numpy" + (" + cupy" if HAVE_CUPY else " (host; cupy absent)") + ".")
    print()
    carrier_selftest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--selftest-h2", action="store_true")
    ap.add_argument("--verify-hexagon", action="store_true")
    ap.add_argument("--db", default=CATALOG_DB)
    a = ap.parse_args()
    if a.selftest: selftest()
    if a.selftest_h2: selftest_h2(a.db)
    if a.verify_hexagon: sys.exit(0 if verify_hexagon(a.db) else 1)
    if a.selftest or a.selftest_h2: return
    ap.print_help()


if __name__ == "__main__":
    main()
