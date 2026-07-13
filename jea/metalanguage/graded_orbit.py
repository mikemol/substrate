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
G/Stab COSET, not a raw permutation. Canonical binder order = first-occurrence (a deterministic
representative; the proven-unique automorphism-aware labeling is a follow-up).
"""
import sys, os, argparse
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
CATALOG_DB = os.path.join(REPO, "catalog", "catalog.db")
FREE = {"Def", "Con", "Prim", "PrimSort", "Proj", "PCon", "PDef", "PProj"}   # referential (identity = qname)


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


def canonicalize(graph):
    """canonical labeling under the full Sₙ on the binders (brute-force lex-min — exact for small
    telescopes). Returns (canonical tuple, residue permutation = argmin, stabilizer = automorphisms)."""
    from itertools import permutations
    n = len(graph)
    if n > 7:                                            # n! blows up; large telescopes stay positional
        ident = tuple(range(n))
        return _serialize(graph, ident), ident, [ident]
    best = None; residue = None; stab = []
    for p in permutations(range(n)):
        s = _serialize(graph, p)
        if best is None or s < best:
            best = s; residue = p; stab = [p]
        elif s == best:
            stab.append(p)
    # Stab as permutations fixing the canonical form (compose residue⁻¹ with each min-achiever)
    return best, residue, stab


# ─────────────────────────────── Phase B: the graded orbit-key (fixpoint over the def-dep DAG) ─────
def clause_of(core, root_lid):
    ch = core.kids.get(root_lid, [])
    return ch[-1] if core.ctor.get(root_lid) == "Defn" and ch else None


def body_bag(core, clause_lid, nargs, resid, orbit_key_of):
    """A canonical BAG signature of the proof body over the per-core tree (finite; def-refs are LEAVES, so
    the recursive type never unfolds). Structural nodes → ctor; a Var dbN resolving to a top-level arg →
    its CANONICAL binder position (via the telescope residue) so binder-permuted bodies agree; a Def-ref →
    the referenced def's ORBIT-KEY (the fixpoint — so companion twins collapse, genuine divergence stays).
    Depth-tracked: db0 = innermost binder; args sit under the clause's `nargs` pattern binders."""
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


class Ctx:
    """the fixpoint context: preloaded unit index + memo + a per-core cache (load each core once).
    `resid[qname]` = the def's telescope residue Lehmer code (the coset element = the wedge r)."""
    def __init__(self, conn):
        self.conn = conn; self.idx = unit_index(conn); self.memo = {}; self.cores = {}; self.resid = {}
    def core(self, core_id):
        if core_id not in self.cores: self.cores[core_id] = load_core(self.conn, core_id)
        return self.cores[core_id]


def orbit_key(ctx, qname, depth=3, stack=None):
    """The GRADED orbit-key of a def: (type-orbit key = the telescope canonical, proof-orbit key = the
    fixpoint body bag). Bottom-up over the def-dependency DAG, memoized + cycle-guarded. Bounded at
    DEPTH 3 = the rig's precomputed-coherence depth: beyond it a reference COLLAPSES BACK INTO THE SPPF
    (keys as its own qname, the content-addressed identity) — the self-collapse, not a truncation."""
    if stack is None: stack = set()
    if qname in ctx.memo: return ctx.memo[qname]
    if qname in stack or depth <= 0 or qname not in ctx.idx:
        return ("leaf", qname)                              # cycle / coherence-depth reached / primitive
    core_id, root_lid = ctx.idx[qname]
    stack.add(qname)
    core = ctx.core(core_id); tel = telescope(core, root_lid)
    if not tel:
        ctx.memo[qname] = ("leaf", qname); stack.discard(qname); return ctx.memo[qname]
    tkey, resid, stab = canonicalize(binder_graph(core, tel[0]))
    ctx.resid[qname] = (to_lehmer(resid), len(stab))         # the coset element (Lehmer) + |Stab|
    cl = clause_of(core, root_lid); nargs = len(tel[0])
    bkey = body_bag(core, cl, nargs, resid,
                    lambda q: orbit_key(ctx, q, depth - 1, stack)) if cl else ()
    key = (tkey, bkey)
    ctx.memo[qname] = key; stack.discard(qname)
    return key


def to_lehmer(perm):
    """the Lehmer code (factoradic digits) of a permutation — the proven Sₙ-canonical residue: digit[i] =
    #{j > i : perm[j] < perm[i]}. This is the per-level residue the LehmerPath datatype carries."""
    n = len(perm)
    return tuple(sum(1 for j in range(i + 1, n) if perm[j] < perm[i]) for i in range(n))


def orbit_of(conn, qname):
    """(canonical telescope key, residue perm, Lehmer residue, |Stab|) for a def — the Phase A normalizer."""
    loc = unit_locus(conn, qname)
    if not loc: return None
    core = load_core(conn, loc[0]); tel = telescope(core, loc[1])
    if not tel: return None
    canon, residue, stab = canonicalize(binder_graph(core, tel[0]))
    return canon, residue, to_lehmer(residue), len(stab)


def selftest(conn):
    D = "Substrate.Algebra.F2.Polynomial.RingLaws.Distrib"
    r = orbit_of(conn, f"{D}.*P-distribʳ"); l = orbit_of(conn, f"{D}.*P-distribˡ")
    assert r and l, "distribʳ/ˡ must resolve"
    ck_r, res_r, leh_r, stab_r = r; ck_l, res_l, leh_l, stab_l = l
    assert ck_r == ck_l, "distribʳ/ˡ must share ONE canonical telescope key (same arg-perm orbit)"
    assert res_r != res_l, "…with DISTINCT residues (they are different coset points)"
    assert stab_r > 1 and stab_l > 1, "nontrivial Stab (symmetric binders) ⇒ residue is a G/Stab coset"
    print("PASS ⟡graded-orbit Phase A (telescope-permutation normalizer):")
    print(f"  distribʳ/ˡ → ONE canonical key; residues {res_r} vs {res_l} (Lehmer {leh_r} vs {leh_l}); "
          f"|Stab|={stab_r} (2 interchangeable Polynomials) ⇒ coset, not raw perm.")


def graded_test(conn):
    D = "Substrate.Algebra.F2.Polynomial.RingLaws.Distrib"
    ctx = Ctx(conn)
    def K(nm): return orbit_key(ctx, f"{D}.{nm}", depth=3)
    dr, dl = K("*P-distribʳ"), K("*P-distribˡ")
    cr, cl = K("convCoeff-distrib"), K("convCoeff-distribˡ")
    print("⟡graded-orbit Phase B — the GRADED key (type-orbit, proof-orbit):")
    print(f"  convCoeff-distrib vs ˡ : type-orbit {'SAME' if cr[0]==cl[0] else 'diff'}, "
          f"proof-orbit {'same' if cr[1]==cl[1] else 'DIFFERENT'} ({len(cr[1])} vs {len(cl[1])} body nodes)")
    print(f"  *P-distribʳ  vs ˡ      : type-orbit {'SAME' if dr[0]==dl[0] else 'diff'}, "
          f"proof-orbit {'same' if dr[1]==dl[1] else 'DIFFERENT'}")
    # localize the divergence: the ONLY body-bag difference is the companion orbit-key
    from collections import Counter
    diff = (Counter(dr[1]) - Counter(dl[1])) + (Counter(dl[1]) - Counter(dr[1]))
    companions = [x for x in diff if isinstance(x, tuple)]
    print(f"  distribʳ/ˡ proof-bag symmetric difference: {sum(diff.values())} items; the reference-orbit(s) "
          f"among them = the companion divergence (convCoeff-distrib vs ˡ, themselves type-twins/proof-distinct).")
    assert dr[0] == dl[0], "distribʳ/ˡ must share the TYPE orbit (arg-perm twins at the telescope)"
    assert dr[1] != dl[1], "…and DIFFER at the PROOF orbit (their proofs genuinely diverge)"
    assert cr[0] == cl[0] and cr[1] != cl[1], "convCoeff companions: same type-orbit, distinct proof-orbit"
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
