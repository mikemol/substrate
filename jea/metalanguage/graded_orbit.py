#!/usr/bin/env python3
"""graded_orbit.py — ⟡graded-orbit-interner (Phase A): the telescope-permutation NORMALIZER.

The rig ⊕/⊗ orbit (jea_rigcat.canonical / sppf_db.canon_syms) quotients FLAT binder-free commutative ops
by sorting immediate children. Argument-permutation of a DEFINITION is strictly more: a whole-subtree
transform — permute the Pi telescope domains AND renumber every dbN de Bruijn role through the remaining
domains and the Clause body. This module is that transform (the "forget/normalizer" arm flagged unbuilt as
⟡pyrig-normalizer), over the per-core UNAMBIGUOUS tree rebuilt from the event tier (the global packing is
reentrant — distribʳ/distribˡ share one root_id — so we cannot walk from a shared root).

Phase A deliverable: for a def, a canonical structure KEY invariant under top-level binder permutation, the
RESIDUE (the permutation, as a LehmerPath), and the STABILIZER (symmetric binders) — so the residue is a
G/Stab COSET, not a raw permutation.

Canonical binder order = the PROVEN-UNIQUE lex-min over the binder relabelings (NOT first-occurrence):
`canonicalize` returns argmin over the Sₙ action of the serialized binder-graph — the unique canonical
representative, with the full set of min-achievers as the automorphism group (the Stab). For n≤7 this is an
exact brute-force over n!. For n>7 (n! too big) it is an individualization-refinement (nauty-style): color
refinement to an equitable partition, then an exhaustive within-cell lex-min (the cross-cell order fixed by
the iso-invariant color) — still exact, cost Π|cellᵢ|! not n!; the discrete case (distinct types/usages ⇒
trivial Stab, the common asymmetric def) is O(n log n) with no search. A residual cell so large that
Π|cellᵢ|! still exceeds the 7! bound falls back to positional AND logs (declared, never silent). The
GRADED body key is likewise canonical: among Stab-equivalent residues the one lex-minimizing the body bag
is chosen (see `orbit_key`), so the (type,proof)-orbit key has no arbitrary tie-break.
"""
import sys, os, argparse
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
CATALOG_DB = os.path.join(REPO, "catalog", "catalog.db")
FREE = {"Def", "Con", "Prim", "PrimSort", "Proj", "PCon", "PDef", "PProj"}   # referential (identity = qname)

sys.path.insert(0, HERE)
from jea_pyalg import Intern, IR          # the content-addressed hash-cons interner (children-as-IDS) — the
                                          # orbit fixpoint interns through THIS (a reference = a bounded id
                                          # handle, NOT the inlined key) so the graded key can't blow up.
BODY_REMIN_CAP = 24     # max Stab achievers over which the body-bag tie-break runs (|S₄|; declared cap)


# ─────────────────────────────── the per-core UNAMBIGUOUS tree (from the event tier) ───────────────
class Core:
    """One core's node tree, reconstructed from obs/edge/event. node = local_id; each carries
    (ctor, qname, idx, [ordered child local_ids]). role = 'db{idx}' for Var/PVar (bound), else the ctor."""
    def __init__(self, ctor, qname, kids):
        self.ctor, self.qname, self.kids = ctor, qname, kids   # dict lid->str, lid->str|None, lid->[lid]

    def role(self, lid):
        c = self.ctor.get(lid, "")
        return f"db{self.idx.get(lid)}" if c in ("Var", "PVar") else c

    def head(self, lid):
        """the node's head symbol: a bound var → its dbN role; a referential node → its qname; else ctor."""
        c = self.ctor.get(lid, "")
        if c in ("Var", "PVar"):
            return f"db{self.idx.get(lid, '?')}"
        return self.qname.get(lid) or c or "·"


def load_core(conn, core_id):
    ctor, qname, idx, kids = {}, {}, {}, defaultdict(list)
    for lid, ct, qn, ix in conn.execute(
            "SELECT o.local_id, ct.text, pt.text, e.idx FROM obs o JOIN event e ON e.ekey=o.ekey "
            "JOIN terms ct ON ct.term_id=e.ctor_id LEFT JOIN path_text pt ON pt.path_id=e.qname_pid "
            "WHERE o.core_id=?", (core_id,)):
        ctor[lid] = ct; qname[lid] = qn; idx[lid] = ix
    for plid, clid in conn.execute(
            "SELECT plid, clid FROM edge WHERE core_id=? ORDER BY plid, ord", (core_id,)):
        kids[plid].append(clid)
    c = Core(ctor, qname, dict(kids)); c.idx = idx
    return c


def unit_locus(conn, qname):
    r = conn.execute(
        "SELECT u.file_id, u.root_lid FROM _unit u JOIN path_text pt ON pt.path_id=u.name_pid "
        "WHERE pt.text=? AND u.copy=0", (qname,)).fetchone()
    return r  # (core_id, root_lid) or None


# ─────────────────────────────── telescope navigation (the cod() peel, sppf_db.py:185-194) ─────────
def telescope(core, root_lid):
    """A def root is Defn → [defType (a Pi chain), Clause]. Peel the Pi chain: each Pi's FIRST child is a
    binder domain, its LAST child is the tail. Returns (binder_domains: [lid], codomain: lid, clause: lid)."""
    ch = core.kids.get(root_lid, [])
    if core.ctor.get(root_lid) != "Defn" or len(ch) < 2:
        return None
    ty, clause = ch[0], ch[-1]
    doms = []
    cur = ty
    while core.ctor.get(cur) == "Pi":
        k = core.kids.get(cur, [])
        if len(k) < 2:
            break
        doms.append(k[0]); cur = k[-1]        # first child = domain, last = tail
    return doms, cur, clause                   # cur = the codomain proposition


# ─────────────────────────────── the binder-graph + its permutation orbit ─────────────────────────
def binder_graph(core, doms):
    """Resolve each telescope binder to (type_head, sorted[referenced binder ids]) — de Bruijn dbN at
    binder position k resolves to top-level binder (k-1-N) (db0 = the immediately-preceding binder).
    Domains here reference only earlier telescope binders (no inner binders), so this is exact."""
    graph = []
    for k, d in enumerate(doms):
        refs = []
        # walk the domain subtree; collect dbN references, resolve to binder ids
        stack = [d]
        thead = None
        while stack:
            n = stack.pop()
            c = core.ctor.get(n, "")
            if c in ("Var", "PVar"):
                N = core.idx.get(n)
                if N is not None and 0 <= k - 1 - N < k:
                    refs.append(k - 1 - N)
            else:
                if thead is None:
                    thead = core.head(n)                 # the domain's head symbol (ℕ / Polynomial / …)
            stack.extend(core.kids.get(n, []))
        graph.append((thead or core.head(d), tuple(sorted(set(refs)))))
    return graph


def _serialize(graph, p):
    """relabel binder i → p[i]; emit the graph ordered by new label (order-independent binder identity)."""
    inv = [0] * len(p)
    for i, j in enumerate(p): inv[j] = i          # inv[new]=old
    rows = []
    for j in range(len(p)):
        typ, refs = graph[inv[j]]
        rows.append((typ, tuple(sorted(p[r] for r in refs))))
    return tuple(rows)


def _refine(graph):
    """1-dim Weisfeiler–Leman / color refinement: an iso-INVARIANT color per binder (fixpoint of
    color[i] ← (color[i], sorted multiset of referenced binders' colors)). Binders in different cells are
    never exchanged by an automorphism, so the canonical search need only break ties WITHIN a cell."""
    n = len(graph)
    color = [graph[i][0] for i in range(n)]              # seed: the binder's own type label
    while True:
        sig = [(color[i], tuple(sorted(color[r] for r in graph[i][1]))) for i in range(n)]
        rank = {s: k for k, s in enumerate(sorted(set(sig)))}
        new = [rank[sig[i]] for i in range(n)]
        if new == color:
            return color
        color = new


def _lexmin_over(graph, orderings):
    """lex-min serialization over a set of binder orderings (each an old-binder sequence in canonical
    position order). Returns (best serialization, residue perm, min-achievers)."""
    best = None; residue = None; stab = []
    for order in orderings:
        p = [0] * len(order)
        for newpos, old in enumerate(order): p[old] = newpos
        p = tuple(p)
        s = _serialize(graph, p)
        if best is None or s < best:
            best = s; residue = p; stab = [p]
        elif s == best:
            stab.append(p)
    return best, residue, stab


def canonicalize(graph):
    """canonical labeling under the full Sₙ on the binders — the PROVEN-UNIQUE lex-min (NOT
    first-occurrence). Returns (canonical tuple, residue permutation = argmin, stabilizer = min-achievers).
    n≤7: exact brute-force over n!. n>7: individualization-refinement — exact within-cell lex-min with the
    cross-cell order fixed by the iso-invariant refinement color (cost Π|cellᵢ|!, discrete ⇒ no search)."""
    from itertools import permutations, product
    from math import factorial
    n = len(graph)
    if n <= 7:                                           # exact: n! is tractable
        return _lexmin_over(graph, permutations(range(n)))
    # n > 7: refine to cells, then exhaustive lex-min WITHIN cells (cross-cell order = color order)
    color = _refine(graph)
    cells = defaultdict(list)
    for i, c in enumerate(color): cells[c].append(i)
    cell_lists = [cells[c] for c in sorted(cells)]       # cells ordered by iso-invariant color
    cost = 1
    for cl in cell_lists: cost *= factorial(len(cl))
    if cost > 5040:                                      # residual symmetry too large — declared fallback
        ident = tuple(range(n))
        print(f"⚠ graded_orbit.canonicalize: n={n} refines to Π|cell|!={cost} > 5040; "
              f"positional fallback (canonical labeling NOT computed for this telescope).", file=sys.stderr)
        return _serialize(graph, ident), ident, [ident]
    orderings = ([old for cellperm in combo for old in cellperm]
                 for combo in product(*[permutations(cl) for cl in cell_lists]))
    return _lexmin_over(graph, orderings)


# ─────────────────────────────── Phase B: the graded orbit-key (fixpoint over the def-dep DAG) ─────
def clause_of(core, root_lid):
    ch = core.kids.get(root_lid, [])
    return ch[-1] if core.ctor.get(root_lid) == "Defn" and ch else None


def body_bag(core, clause_lid, nargs, resid, orbit_key_of):
    """A canonical BAG signature of the proof body over the per-core tree (finite; def-refs are LEAVES, so
    the recursive type never unfolds). Structural nodes → ctor; a Var dbN resolving to a top-level arg →
    its CANONICAL binder position (via the telescope residue) so binder-permuted bodies agree; a Def-ref →
    the referenced def's ORBIT-HANDLE (a bounded int id from the fixpoint, NOT its inlined key — the
    reference is a relative address, so companion twins share a handle and the key cannot blow up).
    Depth-tracked: db0 = innermost binder; args sit under the clause's `nargs` pattern binders. Returns a
    sorted bag mixing structural-token STRINGS and reference-handle INTS."""
    inv = [0] * len(resid)
    for i, j in enumerate(resid): inv[j] = i            # canonical position of old binder i = resid[i]
    bag = []
    # DFS with de Bruijn depth (extra binders entered below the clause args)
    stack = [(clause_lid, 0)]
    seen = set()
    while stack:
        n, extra = stack.pop()
        if n in seen: continue
        seen.add(n)
        c = core.ctor.get(n, "")
        if c in ("Var", "PVar"):
            N = core.idx.get(n, 0); a = N - extra          # arg index from innermost, minus inner binders
            if 0 <= a < nargs:
                bag.append(f"b{resid[nargs - 1 - a]}")     # a top-level arg → its canonical position
            else:
                bag.append("bi")                            # an inner/local binder (position-agnostic)
        elif c in FREE and core.qname.get(n):
            bag.append(orbit_key_of(core.qname[n]))         # a reference → its orbit-key (fixpoint)
        else:
            bag.append(c or "·")
        # Pi/Lam/Clause introduce binders for their subtrees; a clause's own leading PVars are the args
        add = 1 if c in ("Pi", "Lam") else 0
        for ch in core.kids.get(n, []):
            stack.append((ch, extra + add))
    return tuple(sorted(bag, key=repr))                     # bag mixes ctor strings + orbit-key tuples


def unit_index(conn):
    """qname → (core_id, root_lid) for every independent def, in ONE query (no per-qname round-trips)."""
    return {nm: (fid, rl) for nm, fid, rl in conn.execute(
        "SELECT pt.text, u.file_id, u.root_lid FROM _unit u JOIN path_text pt ON pt.path_id=u.name_pid "
        "WHERE u.copy=0")}


def _engine(db_path=None):
    from sqlalchemy import create_engine
    return create_engine(f"sqlite:///{os.path.abspath(db_path or CATALOG_DB)}")


def preload_cores(db_path=None):
    """FRONTLOAD every core's tree in a handful of BULK SQLAlchemy-Core scans (grouped by core_id) instead
    of one nested-loop query PER core — the internment that all readings share. Profiling showed per-core
    loads (213 × 3-way obs⋈event⋈terms⋈path_text nested-loop probes on cold pages) dominated the run
    (~46s/68s); this replaces them with: one scan of the path_text view → {pid:text}, one obs⋈event⋈terms
    scan → per-core (ctor,qname,idx), one edge scan → per-core kids. Returns {core_id: Core}."""
    from sqlalchemy import MetaData, Table, select
    eng = _engine(db_path); md = MetaData()
    obs   = Table("obs",       md, autoload_with=eng)
    event = Table("event",     md, autoload_with=eng)
    terms = Table("terms",     md, autoload_with=eng)
    ptv   = Table("path_text", md, autoload_with=eng)     # materialized+indexed table (sppf_db habitat fix)
    edge  = Table("edge",      md, autoload_with=eng)
    cores = {}
    def C(cid):
        c = cores.get(cid)
        if c is None:
            c = cores[cid] = Core({}, {}, defaultdict(list)); c.idx = {}
        return c
    with eng.connect() as cn:
        # honest declarative join — path_text is a PK-indexed table now, so joining it for every node is a
        # cheap hash/index join done ONCE in the DB (one bulk scan, grouped by core in the pass below).
        nodes = (select(obs.c.core_id, obs.c.local_id, terms.c.text, ptv.c.text, event.c.idx)
                 .select_from(obs.join(event, event.c.ekey == obs.c.ekey)
                                 .join(terms, terms.c.term_id == event.c.ctor_id)
                                 .outerjoin(ptv, ptv.c.path_id == event.c.qname_pid)))
        for cid, lid, ct, qn, ix in cn.execute(nodes):
            c = C(cid); c.ctor[lid] = ct; c.qname[lid] = qn; c.idx[lid] = ix
        for cid, plid, clid in cn.execute(
                select(edge.c.core_id, edge.c.plid, edge.c.clid).order_by(edge.c.core_id, edge.c.plid, edge.c.ord)):
            C(cid).kids[plid].append(clid)
    for c in cores.values():
        c.kids = dict(c.kids)
    return cores


class Ctx:
    """the fixpoint context: preloaded unit index + memo + ALL cores (frontloaded in bulk via
    `preload_cores`). `resid[qname]` = the def's telescope residue Lehmer code (the coset element = the
    wedge r). `preload=False` falls back to lazy per-core loads (for the tiny selftest/graded cases)."""
    def __init__(self, conn, db_path=None, preload=True, keep_bags=False):
        self.conn = conn; self.idx = unit_index(conn); self.memo = {}; self.resid = {}
        self.cores = preload_cores(db_path) if preload else {}
        self.I = Intern()          # content-addressed orbit interner: memo[q]=(tkey, gid) where gid is a
        self.bags = {}             # bounded int handle into self.I; bags[q] = the body bag (inspection only)
        self.keep_bags = keep_bags # keep per-def bags (graded_test needs them; the full run does not)
    def core(self, core_id):
        if core_id not in self.cores: self.cores[core_id] = load_core(self.conn, core_id)
        return self.cores[core_id]


def orbit_key(ctx, qname, depth=3, stack=None):
    """The GRADED orbit-key of a def: `(type-orbit key = the telescope canonical, graded HANDLE)` where the
    handle is a BOUNDED int id into `ctx.I` (the content-addressed interner). A cross-reference embeds the
    referent's HANDLE (a relative address), NEVER its inlined key — so the key is bounded by construction;
    arg-perm twins share a handle (same structure + same child handles → same interned id), genuine
    divergence gets distinct handles. Bottom-up over the def-dependency DAG, memoized + cycle-guarded.
    Bounded at DEPTH 3 = the rig's precomputed-coherence self-collapse: beyond it a reference keys as its own
    qname (its content-addressed SPPF identity) — the self-collapse, not a truncation."""
    if stack is None: stack = set()
    if qname in ctx.memo: return ctx.memo[qname]
    if qname in stack or depth <= 0 or qname not in ctx.idx:
        return (("leaf", qname), ctx.I.intern(IR(kind="leaf", op=qname)))   # cycle / depth floor / primitive
    core_id, root_lid = ctx.idx[qname]
    stack.add(qname)
    core = ctx.core(core_id); tel = telescope(core, root_lid)
    if not tel:
        key = (("leaf", qname), ctx.I.intern(IR(kind="leaf", op=qname)))
        ctx.memo[qname] = key; stack.discard(qname); return key
    tkey, resid, stab = canonicalize(binder_graph(core, tel[0]))
    cl = clause_of(core, root_lid); nargs = len(tel[0])
    resolve = lambda q: orbit_key(ctx, q, depth - 1, stack)[1]   # the referent's bounded HANDLE (int id)
    if cl and len(stab) == 1:
        # asymmetric telescope (the common case): one residue, no tie-break — skip the repr-min entirely.
        bkey = body_bag(core, cl, nargs, resid, resolve)
    elif cl:
        # body re-minimization: among Stab-equivalent residues (same telescope key), pick the one whose
        # body bag is lex-min — so the graded (type,proof) key has NO arbitrary tie-break. Each candidate
        # runs a full body DFS, so a pathologically symmetric telescope (|Stab| up to n!) is CAPPED at
        # BODY_REMIN_CAP achievers (declared, not silent) — the tie-break is a refinement, not correctness.
        cands = stab if len(stab) <= BODY_REMIN_CAP else stab[:BODY_REMIN_CAP]
        if len(stab) > BODY_REMIN_CAP:
            print(f"⚠ graded_orbit.orbit_key: {qname} has |Stab|={len(stab)} > {BODY_REMIN_CAP}; body "
                  f"re-minimization capped (canonical body tie-break over first {BODY_REMIN_CAP} only).",
                  file=sys.stderr)
        bkey, resid = min(((body_bag(core, cl, nargs, r, resolve), r) for r in cands),
                          key=lambda x: repr(x[0]))
    else:
        bkey = ()
    ctx.resid[qname] = (to_lehmer(resid), len(stab))         # the coset element (Lehmer) + |Stab|
    # content-address the graded node THROUGH the interner: children = the referenced HANDLES (bounded ints),
    # op = the bounded structural signature (telescope canonical ‖ the non-reference body tokens). The gid is
    # bounded and stable-within-build; twins (same signature + same child handles) share it (SPPF property).
    refs   = tuple(sorted(x for x in bkey if isinstance(x, int)))
    struct = tuple(x for x in bkey if not isinstance(x, int))
    gid = ctx.I.intern(IR(kind="orbit", op=repr((tkey, struct)), children=refs, payload=(qname,)))
    if ctx.keep_bags: ctx.bags[qname] = bkey
    key = (tkey, gid)
    ctx.memo[qname] = key; stack.discard(qname)
    return key


def to_lehmer(perm):
    """the Lehmer code (factoradic digits) of a permutation — the proven Sₙ-canonical residue: digit[i] =
    #{j > i : perm[j] < perm[i]}. This is the per-level residue the LehmerPath datatype carries."""
    n = len(perm)
    return tuple(sum(1 for j in range(i + 1, n) if perm[j] < perm[i]) for i in range(n))


def from_lehmer(code):
    """inverse of `to_lehmer`: reconstruct the permutation from its factoradic Lehmer code (digit[i] = the
    rank of perm[i] among the remaining values). Lets the coset residue stored as a Lehmer code render back
    to a perm (⇒ a Coxeter word). Round-trips with `to_lehmer` (checked in `--selftest`)."""
    avail = list(range(len(code)))
    return tuple(avail.pop(c) for c in code)


def apply_coxeter_word(word, n):
    """apply an adjacent-transposition word (list of positions k; generator sₖ swaps positions k,k+1) to
    the identity sequence, left-to-right. Inverse rendering of `to_coxeter_word`."""
    seq = list(range(n))
    for k in word:
        seq[k], seq[k + 1] = seq[k + 1], seq[k]
    return tuple(seq)


def to_coxeter_word(perm):
    """the adjacent-transposition (Coxeter / `sadj`) WORD realizing `perm` — NOW PROVEN total by
    OrientationRigCatPermCoxeterGeneral.Properties.coxeter-complete (commit 9dcdbb7): every Perm n IS a
    word in adjacent transpositions (`CoxGen`), via the bubble-run decode of its Lehmer path
    (`decode-CoxGen` / `idInsert-step`). Here we realize that word concretely: bubble the sequence to the
    identity, recording each adjacent swap sₖ (positions k,k+1); the REVERSED swap-list rebuilds `perm`
    from the identity. Generators use position (`sₖ`) indexing, matching `sadj n k`. Round-trips against
    `apply_coxeter_word` (checked in `--selftest`). This is the residue-as-braiding-word renderer the
    coset holes consume — no new math, the bijection + completeness are both proven."""
    a = list(perm)
    n = len(a)
    swaps = []
    for i in range(n):                                   # bubble sort perm → identity
        for j in range(n - 1 - i):
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
                swaps.append(j)
    swaps.reverse()                                      # reversed run builds perm from id
    return swaps


def orbit_of(conn, qname):
    """(canonical telescope key, residue perm, Lehmer residue, |Stab|) for a def — the Phase A normalizer."""
    loc = unit_locus(conn, qname)
    if not loc: return None
    core = load_core(conn, loc[0]); tel = telescope(core, loc[1])
    if not tel: return None
    canon, residue, stab = canonicalize(binder_graph(core, tel[0]))
    return canon, residue, to_lehmer(residue), len(stab)


def coxeter_word_str(word):
    """render an adjacent-transposition word (list of positions k) as `s₀·s₁·…`; `id` if empty."""
    sub = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
    return "·".join(f"s{str(k).translate(sub)}" for k in word) if word else "id"


def orbit_cosets(conn, unit_ids=None, qnames=None):
    """READ the coset residues from `_orbit_def` for a set of units (by unit_id and/or qname) → a dict
    unit_id → {qname, type_key, graded_key, lehmer, stab, coxeter}. This is the consolidation payload the
    autocorr/reuse-TUI holes renderer consumes: the residue rendered as the PROVEN adjacent-transposition
    (`sadj`) word (coxeter-complete, 9dcdbb7) — the wedge form `orbit-rep ∘ residue`, not opaque tokens.
    Requires `_orbit_def` (run `sppf_db.py --argperm`); returns {} if the table is absent."""
    import ast
    if conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='_orbit_def'").fetchone() is None:
        return {}
    where, params = [], []
    if unit_ids is not None:
        ids = list(unit_ids)
        where.append(f"od.unit_id IN ({','.join('?' * len(ids))})"); params += ids
    if qnames is not None:
        nm = list(qnames)
        where.append(f"pt.text IN ({','.join('?' * len(nm))})"); params += nm
    clause = (" WHERE " + " OR ".join(where)) if where else ""
    out = {}
    for uid, qn, tk, gk, res, stab in conn.execute(
            "SELECT od.unit_id, pt.text, od.type_key, od.graded_key, od.residue, od.stab "
            "FROM _orbit_def od JOIN _unit u ON u.unit_id=od.unit_id "
            "JOIN path_text pt ON pt.path_id=u.name_pid" + clause, params):
        try:
            leh = ast.literal_eval(res) if res else ()
            word = to_coxeter_word(from_lehmer(leh)) if leh else []
        except (ValueError, SyntaxError):
            leh, word = (), []
        out[uid] = {"qname": qn, "type_key": tk, "graded_key": gk, "lehmer": leh,
                    "stab": stab, "coxeter": coxeter_word_str(word)}
    return out


def selftest(conn):
    D = "Substrate.Algebra.F2.Polynomial.RingLaws.Distrib"
    r = orbit_of(conn, f"{D}.*P-distribʳ"); l = orbit_of(conn, f"{D}.*P-distribˡ")
    assert r and l, "distribʳ/ˡ must resolve"
    ck_r, res_r, leh_r, stab_r = r; ck_l, res_l, leh_l, stab_l = l
    assert ck_r == ck_l, "distribʳ/ˡ must share ONE canonical telescope key (same arg-perm orbit)"
    assert res_r != res_l, "…with DISTINCT residues (they are different coset points)"
    assert stab_r > 1 and stab_l > 1, "nontrivial Stab (symmetric binders) ⇒ residue is a G/Stab coset"
    # coxeter-completeness (proven, 9dcdbb7): the residue renders as an adjacent-transposition word that
    # round-trips. Exhaustively verify to_coxeter_word ∘ apply == identity over all Sₙ, n≤5.
    from itertools import permutations as _perms
    for nn in range(1, 6):
        for p in _perms(range(nn)):
            w = to_coxeter_word(p)
            assert apply_coxeter_word(w, nn) == tuple(p), f"coxeter word must rebuild {p}, got {apply_coxeter_word(w, nn)} via {w}"
            assert from_lehmer(to_lehmer(p)) == tuple(p), f"lehmer round-trip must rebuild {p}"
    # n>7 refinement path: verify it is EXACT against a brute-force lex-min oracle on synthetic n=8 graphs,
    # and that a pure relabeling of a graph canonicalizes to the SAME key (iso-invariance).
    def _brute(graph):
        best = None
        for p in _perms(range(len(graph))):
            s = _serialize(graph, p)
            if best is None or s < best: best = s
        return best
    def _relabel(graph, p):                              # apply binder relabeling old i → p[i]
        inv = [0] * len(p)
        for i, j in enumerate(p): inv[j] = i
        return [(graph[inv[j]][0], [p[r] for r in graph[inv[j]][1]]) for j in range(len(p))]
    G_disc = [(f"t{i}", [(i + 1) % 8]) for i in range(8)]                 # distinct types ⇒ discrete
    G_sym  = [("a", [1]), ("a", [0]), ("b", [3]), ("b", [2]),            # two symmetric a-pairs, b-pairs
              ("a", [5]), ("a", [4]), ("b", [7]), ("b", [6])]
    for G in (G_disc, G_sym):
        canon8, _, stab8 = canonicalize(G)                               # n=8 ⇒ refinement path
        assert canon8 == _brute(G), "n>7 refinement canonical must EQUAL the brute-force lex-min oracle"
        # iso-invariance: any relabeling gives the identical canonical key
        rel = _relabel(G, (3, 1, 4, 0, 5, 2, 7, 6))
        assert canonicalize(rel)[0] == canon8, "canonical key must be relabeling-invariant"
    assert canonicalize(G_disc)[2].__len__() == 1, "discrete refinement ⇒ trivial Stab"
    assert canonicalize(G_sym)[2].__len__() > 1, "symmetric graph ⇒ nontrivial Stab (coset)"
    print("PASS ⟡graded-orbit Phase A (telescope-permutation normalizer):")
    print(f"  distribʳ/ˡ → ONE canonical key; residues {res_r} vs {res_l} (Lehmer {leh_r} vs {leh_l}); "
          f"|Stab|={stab_r} (2 interchangeable Polynomials) ⇒ coset, not raw perm.")
    print(f"  coxeter-word round-trip verified ∀ Sₙ n≤5 (residue {res_r} → sadj word {to_coxeter_word(res_r)}).")
    print(f"  n>7 refinement EXACT vs brute-force oracle (n=8, discrete + symmetric); relabeling-invariant.")


def graded_test(conn):
    D = "Substrate.Algebra.F2.Polynomial.RingLaws.Distrib"
    ctx = Ctx(conn, preload=False, keep_bags=True)        # 4-def case: lazy load; keep bags to localize
    def K(nm): return orbit_key(ctx, f"{D}.{nm}", depth=3)
    dr, dl = K("*P-distribʳ"), K("*P-distribˡ")
    cr, cl = K("convCoeff-distrib"), K("convCoeff-distribˡ")
    bag = lambda nm: ctx.bags[f"{D}.{nm}"]                 # the bounded body bag (strings + ref-handle ints)
    br, bl = bag("*P-distribʳ"), bag("*P-distribˡ")
    print("⟡graded-orbit Phase B — the GRADED key (type-orbit, proof-orbit; refs = bounded handles):")
    print(f"  convCoeff-distrib vs ˡ : type-orbit {'SAME' if cr[0]==cl[0] else 'diff'}, "
          f"proof-orbit {'same' if cr[1]==cl[1] else 'DIFFERENT'} "
          f"({len(bag('convCoeff-distrib'))} vs {len(bag('convCoeff-distribˡ'))} body-bag items)")
    print(f"  *P-distribʳ  vs ˡ      : type-orbit {'SAME' if dr[0]==dl[0] else 'diff'}, "
          f"proof-orbit {'same' if dr[1]==dl[1] else 'DIFFERENT'}  (graded handles {dr[1]} vs {dl[1]})")
    # localize the divergence over the (now bounded) body bags: the differing item(s) are the companion
    # reference HANDLES (ints) — convCoeff-distrib vs ˡ interned to distinct ids.
    from collections import Counter
    diff = (Counter(br) - Counter(bl)) + (Counter(bl) - Counter(br))
    companions = [x for x in diff if isinstance(x, int)]
    print(f"  distribʳ/ˡ proof-bag symmetric difference: {sum(diff.values())} items; the differing "
          f"reference HANDLE(s) {companions} = the companion divergence (convCoeff-distrib vs ˡ).")
    assert dr[0] == dl[0], "distribʳ/ˡ must share the TYPE orbit (arg-perm twins at the telescope)"
    assert dr[1] != dl[1], "…and DIFFER at the PROOF orbit (their proofs genuinely diverge)"
    assert cr[0] == cl[0] and cr[1] != cl[1], "convCoeff companions: same type-orbit, distinct proof-orbit"
    assert companions, "the divergence must localize to the differing companion reference handle(s)"
    print("PASS — the graded key correctly MERGES the type-abstraction and DISTINGUISHES the proofs.")


def cosets_view(conn, filt=None, min_members=2):
    """Read _orbit_def as the mechanical consolidation: each TYPE-orbit (defs sharing a telescope
    abstraction) → its members + their coset residues + the graded split. g graded-orbits among n members:
    g<n ⇒ some are FULL arg-perm twins (mergeable); g=n ⇒ each proof is distinct (the diagonalization —
    parameterize the shared type/skeleton, keep the proofs). The residue is the wedge r: instance = rep∘r."""
    from collections import defaultdict
    rows = conn.execute(
        "SELECT pt.text, od.type_key, od.graded_key, od.residue, od.stab FROM _orbit_def od "
        "JOIN _unit u ON u.unit_id=od.unit_id JOIN path_text pt ON pt.path_id=u.name_pid").fetchall()
    if not rows:
        print("_orbit_def is empty — run: python3 scripts/sppf_db.py \"<filter>\" --argperm"); return
    by_t = defaultdict(list)
    for name, tk, gk, res, stab in rows:
        if not filt or filt in name: by_t[tk].append((name, gk, res, stab))
    orbits = sorted((m for m in by_t.values() if len(m) >= min_members), key=lambda m: -len(m))
    print(f"⟡graded-orbit cosets: {len(orbits)} type-orbits with ≥{min_members} members "
          f"({sum(len(m) for m in orbits)} defs share a telescope-abstraction)\n")
    for m in orbits[:30]:
        ng = len({g for _, g, _, _ in m})
        rep = min(m, key=lambda x: x[2])                     # orbit rep = lex-min residue
        kind = "FULL twins → MERGE" if ng < len(m) else "type-twins, distinct proofs (diagonalization)"
        print(f"  ×{len(m)}  {ng} graded-orbit(s)  [{kind}]  rep={rep[0].split('.')[-1]}")
        for name, g, res, stab in sorted(m, key=lambda x: x[2]):
            print(f"      {name.split('.')[-1]:26s} residue(coset)={res}  |Stab|={stab}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", metavar="QNAME", help="print a def's telescope + body structure")
    ap.add_argument("--canon", metavar="QNAME", help="canonical telescope key + residue + Stab")
    ap.add_argument("--graded", action="store_true", help="Phase B: the graded (type, proof) orbit-key test")
    ap.add_argument("--cosets", nargs="?", const="", metavar="FILTER",
                    help="Phase D: read _orbit_def as type-orbit → (rep, coset residues); optional qname filter")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    import sqlite3
    conn = sqlite3.connect(CATALOG_DB)
    if args.selftest:
        selftest(conn); return
    if args.graded:
        graded_test(conn); return
    if args.cosets is not None:
        cosets_view(conn, args.cosets or None); return
    if args.probe:
        loc = unit_locus(conn, args.probe)
        if not loc:
            sys.exit(f"no unit {args.probe!r}")
        core_id, root_lid = loc
        core = load_core(conn, core_id)
        tel = telescope(core, root_lid)
        if not tel:
            sys.exit(f"{args.probe} root {root_lid} is not a Defn telescope")
        doms, cod, clause = tel
        print(f"# {args.probe.split('.')[-1]}  root={root_lid}  {len(doms)} telescope binders")
        for i, d in enumerate(doms):
            # the domain's head + any dbN it references (first child chain)
            dk = core.kids.get(d, [])
            refs = [core.head(x) for x in dk]
            print(f"  binder[{i}] domain: {core.head(d)}  children: {refs}")
        print(f"  codomain head: {core.head(cod)}")
        cl = core.kids.get(clause, [])
        print(f"  clause: {core.ctor.get(clause)}  leading binders: "
              f"{[core.head(x) for x in cl if core.ctor.get(x) in ('Var','PVar')]}")
        print(f"  clause body heads (first 12): {[core.head(x) for x in cl][:12]}")
        return
    if args.canon:
        loc = unit_locus(conn, args.canon)
        if not loc: sys.exit(f"no unit {args.canon!r}")
        core = load_core(conn, loc[0]); tel = telescope(core, loc[1])
        if not tel: sys.exit("not a Defn telescope")
        g = binder_graph(core, tel[0])
        canon, residue, stab = canonicalize(g)
        print(f"# {args.canon.split('.')[-1]}")
        print(f"  binder-graph : {g}")
        print(f"  CANONICAL    : {canon}")
        print(f"  residue perm : {residue}   |Stab| = {len(stab)}  (symmetric binders ⇒ the coset ≠ raw perm)")
        return
    print("use --probe QNAME | --canon QNAME (Phase A wip)")


if __name__ == "__main__":
    main()
