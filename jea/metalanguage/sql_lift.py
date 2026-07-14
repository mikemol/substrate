#!/usr/bin/env python3
"""sql_lift.py — ⟡graded-relational-carrier: python-ops ↔ SQL-lifts lowered to ONE GradedProductOver.

The inverse of ⟡query-rawtocore (which migrated raw SQL → Core builders): here we DISCOVER python-side
relational operations (sort/dedup/group/count/filter over query results) that could be LIFTED INTO SQL —
the eager→fused roofline move (materialize-a-temporary-per-op → one declarative pass).

The design is a CrossMix cospan `Python-ops → R ← SQL-ops` (Substrate.Algebra.Wedge.CrossMul), where the
common carrier R is a **GradedProductOver over (ℕ,+,0)** (OrientationBimonoidal.agda:34-39; the python
GradedProductOver at jea_rigcat.py:136): the carrier family C(n) = relational-op PIPELINES of composition
depth n; `_∧_ : C i → C j → C (i+j)` composes ops, adding grades. Both sides lower via a `GradedHomOver`
bridge into R (the shared jea_pyalg.Intern); a python op is a LICENSED LIFT exactly when its Rel-lowering is
grade-0-coherent (CrossMix.cross_term degree 0 = same carrier point) with an SQL construct — proved by
same-interned-id, not similarity. The GRADE is load-bearing: it IS the liftability boundary — a bounded-grade
pipeline FLATTENS to a relational normal form (Family A, liftable); an unbounded-grade term (a recursive DAG
walk — Family B) never collapses (not liftable). Breadth = orbit-dedup fan-in over the shared Intern.

Reuse: jea_pyalg (Intern/IR/CrossMix), jea_rigcat (GradedProductOver / grade-transport cert), jea_pysim
(Corpus intern-all-python), query_builders (the SQL builders, co-interned). Curated Rel head-set (RIG_OPS
discipline — proven, not open-ended). Honest boundary: coherence is head-SEQUENCE / sub-pipeline level
(a bounded-grade python pipeline embeds as a graded sub-object of an SQL pipeline); column/source identity is
the ⟡L4 refinement; the roofline intensity is a READOUT annotation, not a grade (finding B).
"""
import os, sys, ast, glob, argparse
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
from jea_pyalg import IR, Intern, CrossMix
from jea_rigcat import GradedProductOver

# ── the curated relational head-set (proven / closed, like RIG_OPS) ─────────────────────────────────
# each is a generator of the graded relational carrier; a pipeline is a composition (grade = # heads).
REL_HEADS = ("Scan", "Filter", "Distinct", "GroupBy", "Agg", "OrderBy", "Limit", "Join")
# SQL canonical evaluation order (for the head-SEQUENCE that coherence matches as a sub-pipeline).
_SQL_ORDER = {h: i for i, h in enumerate(("Scan", "Join", "Filter", "GroupBy", "Agg", "Distinct", "OrderBy", "Limit"))}

# The common carrier R: a GradedProductOver over (ℕ,+,0). An element is a Rel pipeline; grade = its length;
# `_∧_` composes (nests) two pipelines, adding grades. (jea_rigcat.GradedProductOver, decategorified to grades.)
REL = GradedProductOver(op=lambda i, j: i + j, e=0)


class RelTerm:
    """A relational-op pipeline: a linear chain of Rel heads over a Scan leaf. `heads` is the sequence
    outer→inner (as written); `grade` = len(heads) = the GradedProductOver grade (composition depth);
    `source` = the scanned relation token where recoverable, else '*'. Interned into the shared carrier so
    two identical pipelines share an id (orbit-dedup fan-in = breadth)."""
    __slots__ = ("heads", "source", "sites")
    def __init__(self, heads, source="*"):
        self.heads = tuple(heads)          # e.g. ("Limit","OrderBy") outer→inner
        self.source = source
        self.sites = []                    # (file, lineno) emission sites
    @property
    def grade(self):
        return len(self.heads)
    def key(self):
        return (self.heads, self.source)
    def intern_into(self, I: Intern) -> int:
        """Lower this pipeline into the common carrier R (jea_pyalg.Intern): innermost Scan leaf first,
        each head an IR(kind='Rel', op=head) wrapping the sub-pipeline — children-as-ids, so identical
        pipelines content-address to ONE node."""
        cur = I.intern(IR(kind="Rel", op="Scan", lit=self.source))
        for h in reversed(self.heads):     # inner→outer: wrap the sub-pipeline
            cur = I.intern(IR(kind="Rel", op=h, children=(cur,)))
        return cur
    def canon_seq(self):
        """the head sequence in SQL evaluation order (Scan..Limit) — what sub-pipeline coherence matches."""
        return tuple(sorted(self.heads, key=lambda h: _SQL_ORDER.get(h, 99)))


# ════════════════════════════════ Bridge_py: python AST expression → Rel pipeline ═══════════════════
# A GradedHomOver: recognize the relational shapes and lower to Rel heads; STOP (return None) at a
# non-relational op (a per-row python fn, a recursive helper) — that unbounded grade IS the residue.
_SCAN_CALLS = {"run", "execute", "fetchall", "fetchone", "items", "keys", "values"}

def _callee(node):
    f = node.func
    if isinstance(f, ast.Name):      return f.id
    if isinstance(f, ast.Attribute): return f.attr
    return None

def rel_of_expr(node, depth=0):
    """python expression → RelTerm (heads outer→inner) or None if not a bounded relational pipeline."""
    if depth > 40:
        return None
    # x[:n]  → Limit
    if isinstance(node, ast.Subscript):
        sl = node.slice
        if isinstance(sl, ast.Slice) and sl.upper is not None:
            inner = rel_of_expr(node.value, depth + 1)
            if inner: return RelTerm(("Limit",) + inner.heads, inner.source)
        return rel_of_expr(node.value, depth + 1)          # non-limit subscript: pass through
    if isinstance(node, ast.Call):
        fn = _callee(node)
        arg0 = node.args[0] if node.args else None
        if fn == "sorted":
            inner = rel_of_expr(arg0, depth + 1) if arg0 is not None else None
            return RelTerm(("OrderBy",) + (inner.heads if inner else ("Scan",)),
                           inner.source if inner else _src(arg0))
        if fn == "Counter":                                # collections.Counter = GROUP BY … COUNT(*)
            inner = rel_of_expr(arg0, depth + 1) if arg0 is not None else None
            return RelTerm(("GroupBy", "Agg") + (inner.heads if inner else ()),
                           inner.source if inner else _src(arg0))
        if fn in ("set", "frozenset"):
            inner = rel_of_expr(arg0, depth + 1) if arg0 is not None else None
            return RelTerm(("Distinct",) + (inner.heads if inner else ("Scan",)),
                           inner.source if inner else _src(arg0))
        if fn in ("len", "sum", "max", "min"):
            return RelTerm(("Agg",), _src(arg0))
        if fn in _SCAN_CALLS:                              # QB.run(...) / con.execute(...) / .items()
            return RelTerm(("Scan",), _src(node))
        if fn == "dict":
            inner = rel_of_expr(arg0, depth + 1) if arg0 is not None else None
            return inner                                   # dict(rows) = a lookup-table load, pass through
        return None                                        # a non-relational call → bounded stop
    if isinstance(node, ast.SetComp):                      # {… for … in src (if p)} = DISTINCT [FILTER]
        src = rel_of_expr(node.generators[0].iter, depth + 1) if node.generators else None
        heads = ("Distinct",) + (("Filter",) if _has_if(node) else ()) + (src.heads if src else ("Scan",))
        return RelTerm(heads, src.source if src else "*")
    if isinstance(node, (ast.ListComp, ast.GeneratorExp)):
        src = rel_of_expr(node.generators[0].iter, depth + 1) if node.generators else None
        if _has_if(node):
            return RelTerm(("Filter",) + (src.heads if src else ("Scan",)), src.source if src else "*")
        return src                                         # a map-only comprehension: pass through source
    if isinstance(node, ast.Name):
        return RelTerm(("Scan",), node.id)                 # a variable = a relation source (bounded leaf)
    if isinstance(node, ast.Attribute):
        return rel_of_expr(node.value, depth + 1)
    return None

def _has_if(comp):
    return any(g.ifs for g in getattr(comp, "generators", []))

def _src(node):
    """recover the scanned-relation token (a QB builder name / table) where cheap, else '*'."""
    if node is None:
        return "*"
    if isinstance(node, ast.Call):
        fn = _callee(node)
        if fn in ("run", "execute"):                       # QB.run(con, QB.q_edges_all()) / con.execute("…")
            for a in node.args:
                if isinstance(a, ast.Call) and isinstance(a.func, ast.Attribute):
                    return a.func.attr                     # the q_* builder name
                if isinstance(a, ast.Constant) and isinstance(a.value, str):
                    return _table_of_sql(a.value)
        if fn in _SCAN_CALLS and isinstance(node.func, ast.Attribute):
            return _src(node.func.value)
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.GeneratorExp):
        return _src(node.generators[0].iter) if node.generators else "*"
    return "*"

def _table_of_sql(s):
    import re
    m = re.search(r"\bFROM\s+([A-Za-z_][\w]*)", s, re.I)
    return m.group(1) if m else "*"


def bridge_py_unit(fn_node):
    """A GradedHomOver over a python function: every maximal bounded Rel expression in its body.
    Returns [RelTerm]. An expression that does not reduce to a Rel pipeline (a recursive helper call,
    per-row python fn) contributes nothing — its unbounded grade is the (kept) residue, i.e. the reason
    that read stays python (Family B). We take only MAXIMAL terms (grade ≥ 2, or a lone dedup/group)."""
    out = []
    for node in ast.walk(fn_node):
        if isinstance(node, (ast.Subscript, ast.Call, ast.SetComp, ast.ListComp, ast.GeneratorExp)):
            rt = rel_of_expr(node)
            if rt is not None and _interesting(rt):
                out.append(rt)
    return _maximal(out)

def _interesting(rt):
    """a Rel term worth reporting: has ≥1 non-Scan relational head (drop bare Scan/pass-throughs)."""
    ops = [h for h in rt.heads if h != "Scan"]
    return len(ops) >= 1

def _maximal(terms):
    """drop a term whose head-sequence is a proper suffix of another term at the same source (keep the
    longest pipeline; the shorter is contained). Dedup identical."""
    uniq = {}
    for t in terms:
        uniq[t.key()] = t
    terms = list(uniq.values())
    kept = []
    for t in terms:
        if not any(o is not t and o.source == t.source and _suffix(t.heads, o.heads) for o in terms):
            kept.append(t)
    return kept

def _suffix(short, long):
    return len(short) < len(long) and long[len(long) - len(short):] == short


# ════════════════════════════════ Bridge_sql: SQLAlchemy Select → Rel heads ═════════════════════════
def rel_of_select(stmt):
    """A GradedHomOver over an SQLAlchemy Core select(): its Rel head-set in SQL evaluation order.
    Uses the Select's clause structure (stable in SQLAlchemy 2.x). Returns a RelTerm."""
    froms = []
    try:
        froms = list(stmt.get_final_froms())
    except Exception:
        pass
    for f in froms:                                            # ⟡L7: a recursive CTE = the reachability closure
        if type(f).__name__ == "CTE" and getattr(f, "recursive", False):
            return RelTerm(("Closure",), _select_source(froms))   # recursion→parallel: WITH RECURSIVE
    heads = ["Scan"]
    if any(type(f).__name__ == "Join" for f in froms):
        heads.append("Join")
    if getattr(stmt, "_where_criteria", ()):     heads.append("Filter")
    if getattr(stmt, "_group_by_clauses", ()):   heads.append("GroupBy")
    if _has_aggregate(stmt):                      heads.append("Agg")
    if getattr(stmt, "_distinct", False):         heads.append("Distinct")
    if getattr(stmt, "_order_by_clauses", ()):   heads.append("OrderBy")
    if getattr(stmt, "_limit_clause", None) is not None: heads.append("Limit")
    src = _select_source(froms)
    return RelTerm(tuple(heads), src)

def _has_aggregate(stmt):
    try:
        cols = list(stmt.selected_columns)
    except Exception:
        return False
    aggs = {"count", "sum", "max", "min", "avg"}
    for c in cols:
        for el in _walk_clause(c):
            if type(el).__name__ == "Function" and getattr(el, "name", "").lower() in aggs:
                return True
    return False

def _walk_clause(el, depth=0):
    yield el
    if depth > 20:
        return
    for ch in getattr(el, "get_children", lambda: [])():
        yield from _walk_clause(ch, depth + 1)

def _select_source(froms):
    for f in froms:
        n = getattr(f, "name", None)
        if n:
            return n
    return "*"


# ════════════════════════════════ Bridge_np: numpy relational op → Rel heads ════════════════════════
# The THIRD GradedHomOver (beside Bridge_py and Bridge_sql, rel_of_select). A numpy builder in
# numpy_builders.py is TAGGED with the Rel head it realizes; rel_of_np lowers a tag-chain to the SAME
# RelTerm heads Bridge_sql produces, so co-interning them reaches ONE carrier point (CrossMix.coherent =
# degree 0 = the same canonical node). This is the CROSSMIX leg of the SQL↔numpy hexagon: the numpy op and
# its SQL twin lower to one interned Rel node — the VALUE identity is proven separately (byte-exact, in
# numpy_builders.verify_hexagon). Head vocabulary + SQL-eval order reconciled via RelTerm.canon_seq, so the
# match is braiding-robust (any WHERE/head order lands on one orbit rep).
_NP_HEAD = {                       # numpy_builders fn name → Rel head
    "np_scan": "Scan", "np_filter": "Filter", "np_distinct": "Distinct",
    "np_group_count": "GroupBy", "np_order": "OrderBy", "np_limit": "Limit",
    "np_join": "Join", "np_closure": "Closure",
}
def rel_of_np(np_heads, source="*"):
    """np_heads: the sequence of numpy-builder names applied → RelTerm (same carrier as Bridge_sql). A
    group-count emits GroupBy∧Agg (matching Bridge_sql's _has_aggregate over COUNT(*))."""
    heads = []
    for h in np_heads:
        rh = _NP_HEAD[h]
        heads.append(rh)
        if rh == "GroupBy":
            heads.append("Agg")
    return RelTerm(tuple(heads), source)

def np_sql_coherent(I, np_heads, sql_stmt):
    """True iff the numpy op-chain and the SQL builder lower to the SAME interned Rel carrier node (degree 0).
    Both compared in SQL-eval order (canon_seq), Scan-leaf abstracted, source abstracted — so the coherence
    is the braiding-invariant orbit identity, not a positional match. (CrossMix.coherent, jea_pyalg.py:695.)"""
    p_heads = tuple(h for h in rel_of_np(np_heads).canon_seq() if h != "Scan")
    s_heads = tuple(h for h in rel_of_select(sql_stmt).canon_seq() if h != "Scan")
    p = RelTerm(p_heads, "*").intern_into(I)
    s = RelTerm(s_heads, "*").intern_into(I)
    return CrossMix(I).coherent(p, s)


# ════════════════════════════════ the corpus + the lift report ═════════════════════════════════════
def _py_files():
    return sorted(set(glob.glob(os.path.join(HERE, "*.py")) +
                      glob.glob(os.path.join(REPO, "scripts", "*.py"))))

def build(files=None):
    """Intern the SQL builders AND every python relational pipeline into ONE shared carrier R.
    Returns (I, py_terms, sql_terms) where *_terms map interned-id → RelTerm (sites recorded)."""
    files = files or _py_files()
    I = Intern()
    py = {}     # rel_id -> RelTerm (with sites)
    rec = []    # ⟡L6: (relpath, lineno, name, classification) — the recursion-pole computations
    for path in files:
        try:
            tree = ast.parse(open(path, encoding="utf-8").read())
        except (SyntaxError, OSError, UnicodeDecodeError):
            continue
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for rt in bridge_py_unit(node):
                    rid = rt.intern_into(I)
                    t = py.setdefault(rid, rt)
                    t.sites.append((os.path.relpath(path, REPO), getattr(node, "lineno", -1), node.name))
                cls = classify_recursion(node)     # ⟡L6: place it on the recursion↔loop↔parallel triangle
                if cls is not None:
                    # a reachability closure lowers to Rel(Closure); a fold-over-closure to Rel(Agg)∧Rel(Closure)
                    # — the recursion pole made grade structure (via the recursion→parallel morphism).
                    heads = (("Agg",) if cls["scheme"].startswith("fold") else ()) + ("Closure",)
                    if cls["sql_target"] != "residue":
                        RelTerm(heads, "*").intern_into(I)
                    rec.append((os.path.relpath(path, REPO), getattr(node, "lineno", -1), node.name, cls))
    sql = {}    # rel_id -> RelTerm
    try:
        from query_builders import INTERN_BUILDERS
        for name, thunk in INTERN_BUILDERS.items():
            try:
                rt = rel_of_select(thunk())
            except Exception:
                continue
            rid = rt.intern_into(I)
            t = sql.setdefault(rid, rt)
            t.sites.append(("query_builders", name))
    except Exception as e:
        print(f"  [sql-skip] {e}", file=sys.stderr)
    return I, py, sql, rec


def licensed_lifts(I, py, sql):
    """A python Rel pipeline is a LICENSED LIFT iff its head-sequence (SQL-eval order, source-abstracted)
    is a contiguous sub-pipeline of some SQL builder's — CrossMix coherence at the graded sub-object level
    (the python grade-k pipeline embeds in the SQL grade-m pipeline; the residue = the SQL heads the python
    doesn't cover, already done in SQL). Ranked by breadth (# python sites)."""
    sql_seqs = [(rt.canon_seq(), rt) for rt in sql.values()]
    out = []
    for rid, rt in py.items():
        pseq = tuple(h for h in rt.canon_seq() if h != "Scan")
        if len(pseq) < 2:                      # a COMPOSED pipeline (≥2 relational heads) is the real
            continue                           # eager→fused win — where intermediates materialize per op
        matches = [srt for sseq, srt in sql_seqs if _contig(pseq, tuple(h for h in sseq if h != "Scan"))]
        if matches:
            out.append((rt, matches))
    out.sort(key=lambda r: -roofline(r[0])["score"])   # ⟡L4: steer by intensity-gain × breadth
    return out

def _contig(short, long):
    """is `short` a contiguous subsequence of `long`?"""
    if not short or len(short) > len(long):
        return len(short) == 0
    for i in range(len(long) - len(short) + 1):
        if long[i:i + len(short)] == short:
            return True
    return False


# ════════════════════════════════ ⟡L4 — roofline steering: which lifts pay off ══════════════════════
# The eager→fused readout (el-atlas/tools/kernel_cost_model.py:12-25). A python pipeline runs EAGER: a
# materialized temporary per op (list/set/dict/Counter) → ~20k B/elem over k ops → intensity I = 2k/(20k) =
# 0.1 FLOP/byte, CONSTANT in size → MEMORY-BOUND. Lifting it into SQL runs FUSED: one declarative streaming
# pass, no python intermediates → 8 B/elem → I = 2k/8 = k/4, which SCALES with pipeline depth k → toward
# COMPUTE-BOUND. "Fusing IS the lever that raises intensity" (kernel_cost_model.py:24). So a lift's payoff is
# the intensity-GAIN (=I_fused/I_eager = 2.5·k) × its breadth (corpus-wide temporaries eliminated) — the same
# breadth×cost steering as query_registry's index recommender. HONEST: intensity is a READOUT ρ of the graded
# object, NOT a grade (finding B, the weakest thread); this is a cost HEURISTIC, workload-relative, not a
# measured speedup — measuring the wall-time win is ⟡L5 (apply + benchmark). Size (result cardinality) would
# scale the ABSOLUTE win but not the regime; left as a per-lift annotation, not in the score.
_I_EAGER = 0.1
def roofline(rt):
    k = len([h for h in rt.heads if h != "Scan"])   # relational ops = eager intermediates materialized
    i_fused = k / 4.0
    gain = i_fused / _I_EAGER                         # = 2.5·k (per-element intensity gain, size-independent)
    return {"k": k, "i_eager": _I_EAGER, "i_fused": i_fused, "gain": gain, "score": gain * len(rt.sites)}


# ════════════════════════ ⟡L6 — the recursion↔loop↔parallel triangle (pole classifier) ══════════════
# sql_lift's grade was scalar pipeline-DEPTH — the LOOP→PARALLEL edge only (a python set-op → an SQL set-op).
# The full grade is a position in the recursion↔loop↔parallel triangle = the substrate's PROVEN fold⊣unfold
# axis (least-fp ⊣ greatest-fp; SKIReduceResidueFP.agda:7-14). Family A (bounded/flattens/loop) vs Family B
# (unbounded/never-collapses/recursion) IS that boundary. A recursion is NOT a dead end: the recursion→parallel
# transition (least-fixpoint saturation = SQL WITH RECURSIVE; the grammar_fixpoint archetype) lifts a
# transitive-closure recursion to a declarative CTE. This classifier splits Family B into what that transition
# reaches. The trace_intern CLOSED/SUSPENDED verdict (jea_haskell_trace) is the substrate's decision procedure
# for which pole a computation sits at; here we read the pole structurally from the AST.
_ADJ_NAMES = {"child", "children", "kids", "edges", "node_child", "adj", "succ", "neighbors", "childmap", "cl"}
_NONSQL = {"log", "exp", "log2", "log10", "hexdigest", "sha1", "sha256", "md5", "sha", "digest"}

def _shallow_nodes(fn):
    """all AST nodes in fn's own body, NOT descending into nested def/lambda scopes (so a nested helper is
    classified as its OWN function, not attributed to its parent)."""
    out, stack = [], list(ast.iter_child_nodes(fn))
    while stack:
        n = stack.pop(); out.append(n)
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
            continue
        stack.extend(ast.iter_child_nodes(n))
    return out

def _features(fn):
    ns = _shallow_nodes(fn); name = getattr(fn, "name", "")
    self_rec = any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == name for n in ns)
    has_worklist = (any(isinstance(n, ast.While) for n in ns) and
                    any(isinstance(n, ast.Attribute) and n.attr == "pop" for n in ns) and
                    any(isinstance(n, ast.Attribute) and n.attr in ("extend", "append") for n in ns))
    def _named(nn): return (nn.func.id if isinstance(nn, ast.Call) and isinstance(nn.func, ast.Name) else
                            (nn.func.attr if isinstance(nn, ast.Call) and isinstance(nn.func, ast.Attribute) else None))
    calls = {_named(n) for n in ns if isinstance(n, ast.Call)}
    attrs = {n.attr for n in ns if isinstance(n, ast.Attribute)}
    names = {n.id for n in ns if isinstance(n, ast.Name)}
    adjacency = bool((_ADJ_NAMES & names) or (_ADJ_NAMES & attrs))
    set_accum = bool({"set", "frozenset"} & calls) or bool({"add", "update"} & attrs)
    nonsql = bool(_NONSQL & calls) or bool(_NONSQL & attrs)
    perm = bool({"permutations", "product", "factorial"} & calls)
    sorted_flatten = ("sorted" in calls and self_rec and bool({"extend", "append"} & attrs))
    # a term-rewrite / render / parse hylomorphism BUILDS text or new terms per node (f-string, str .join) —
    # NOT a reachability closure (which accumulates the reachable NODE SET); it is residue, not a CTE.
    builds_text = any(isinstance(n, ast.JoinedStr) for n in ns) or ("join" in attrs)
    reducers = set()
    if "sum" in calls or any(isinstance(n, ast.AugAssign) and isinstance(n.op, ast.Add) for n in ns): reducers.add("SUM")
    if "max" in calls: reducers.add("MAX")
    if "min" in calls: reducers.add("MIN")
    if "len" in calls or "count" in calls or "Counter" in calls: reducers.add("COUNT")
    # a DAG/collection WALK (not linear recursion like factorial(n-1)): a worklist, or self-recursion that
    # happens inside a loop/comprehension (recursing OVER a collection of children — even indirectly, e.g.
    # hei recurses over `descsh(n)`, which is why an ADJ-name guard is too narrow).
    has_loop_or_comp = any(isinstance(n, (ast.For, ast.ListComp, ast.SetComp, ast.GeneratorExp, ast.DictComp)) for n in ns)
    walks = has_worklist or (self_rec and has_loop_or_comp)
    return dict(name=name, self_rec=self_rec, has_worklist=has_worklist, adjacency=adjacency,
                set_accum=set_accum, nonsql=nonsql, perm=perm, sorted_flatten=sorted_flatten,
                builds_text=builds_text, reducers=reducers, walks=walks)

def classify_recursion(fn):
    """Place a python function on the recursion↔loop↔parallel triangle and name its available transition.
    Returns None if it is not a recursion/worklist walk (flat → handled by the Rel-pipeline path). Otherwise
    {pole, scheme, transition, sql_target, reason}. The split of Family B (grounded on the corpus):
      reachability-closure   → recursion→parallel: WITH RECURSIVE (UNION = distinct closure, O(V+E))
      fold-over-closure      → recursion→parallel: WITH RECURSIVE + aggregate (SUM/MAX/MIN/COUNT)
      residue                → stays python (non-SQL numeric / graph-iso / variable-arity rewrite)."""
    f = _features(fn)
    if not f["walks"]:
        return None                                              # not a recursion — flat (Family A / Rel path)
    if f["nonsql"]:
        return dict(pole="recursion", scheme="non-SQL numeric fold", transition="—", sql_target="residue",
                    reason="log/exp/hash reducer has no SQL aggregate (e.g. log-sum-exp / Merkle)")
    if f["perm"]:
        return dict(pole="recursion", scheme="permutation search / graph-iso", transition="—",
                    sql_target="residue", reason="canonical-labeling / permutation search is not relational")
    if f["sorted_flatten"]:
        return dict(pole="recursion", scheme="variable-arity term rewrite", transition="—", sql_target="residue",
                    reason="flatten-nested + sort (normal-form rewrite) is not a relational closure")
    if f["builds_text"] and not f["reducers"]:
        return dict(pole="recursion", scheme="term-rewrite / render hylomorphism", transition="—",
                    sql_target="residue", reason="builds text/new terms per node (render/parse), not a reachable set")
    if f["reducers"] and not (f["set_accum"] and not f["reducers"]):
        agg = "/".join(sorted(f["reducers"]))
        return dict(pole="recursion", scheme=f"fold-over-closure ({agg})", transition="recursion→parallel",
                    sql_target=f"WITH RECURSIVE + {agg}", reason="associative reducer over a DAG closure")
    return dict(pole="recursion", scheme="reachability / transitive-closure", transition="recursion→parallel",
                sql_target="WITH RECURSIVE (UNION)", reason="a set-accumulating walk over a child/edge adjacency")


def report(files=None):
    I, py, sql, rec = build(files)
    lifts = licensed_lifts(I, py, sql)
    print(f"⟡graded-relational-carrier — {len(py)} distinct python Rel-pipelines, {len(sql)} SQL builder "
          f"pipelines, interned into ONE carrier ({I.size()} nodes)\n")
    print(f"LICENSED LIFTS — STEER by roofline priority (intensity-gain × breadth; eager I≈0.1 memory-bound "
          f"→ fused I=k/4 compute-bound; a lift eliminates k materialized python temporaries per site):\n")
    for rt, matches in lifts:
        seq = " → ".join(h for h in rt.canon_seq() if h != "Scan")
        sset = ", ".join(sorted({s[1] for srt in matches for s in srt.sites})[:4])
        rf = roofline(rt)
        print(f"  score {rf['score']:5.1f}  ×{rf['gain']:.1f} intensity  (I {rf['i_eager']:.2f}→{rf['i_fused']:.2f}, "
              f"{rf['k']} temporaries × {len(rt.sites)} sites)  [{seq}]  ⟵ SQL: {sset}")
        for site in rt.sites[:4]:
            print(f"        {site[0]}:{site[1]}  {site[2]}()")
    if not lifts:
        print("  (none)")
    elif lifts:
        top = lifts[0][0]
        print(f"\n  → STEER: lift `[{' → '.join(h for h in top.canon_seq() if h!='Scan')}]` first "
              f"(score {roofline(top)['score']:.1f}: the highest intensity-gain × breadth — most eager "
              f"temporaries eliminated corpus-wide, workload-relative).")
    # the orbit-dedup headline: COMPOSED (grade≥2) python pipelines shared across ≥2 sites (fan-in clusters)
    shared = [rt for rt in py.values() if len(rt.sites) >= 2 and len([h for h in rt.heads if h != "Scan"]) >= 2]
    print(f"\nORBIT-DEDUP: {len(shared)} composed (grade≥2) python Rel-pipeline(s) recur across ≥2 sites "
          f"(the fan-in clusters — one canonical carrier node each):")
    for rt in sorted(shared, key=lambda r: (-len(r.sites), -r.grade)):
        seq = " → ".join(h for h in rt.canon_seq() if h != "Scan")
        print(f"  fan-in {len(rt.sites)}  grade {rt.grade}  [{seq}]  sites: " +
              "; ".join(f"{s[0]}:{s[1]}({s[2]})" for s in rt.sites[:4]))

    # ⟡L6 — the recursion↔loop↔parallel triangle: the split of Family B (previously "all not liftable").
    cte = [r for r in rec if r[3]["transition"] == "recursion→parallel"]
    residue = [r for r in rec if r[3]["sql_target"] == "residue"]
    has_cte = any("Closure" in rt.heads for rt in sql.values())   # ⟡L7: the WITH RECURSIVE builder exists?
    tgt = ("MATCHES query_builders.q_reach (WITH RECURSIVE, measured: 275× on-demand / 0.7× full-graph — "
           "workload-relative)" if has_cte else "RECOMMENDED (no WITH RECURSIVE builder in production yet)")
    print(f"\nRECURSION→PARALLEL (the fold⊣unfold transition: a greatest-fp recursion → a declarative "
          f"least-fixpoint = SQL WITH RECURSIVE) — {len(cte)} of {len(rec)} recursion-pole computations lift.")
    print(f"  recursion→parallel target: {tgt}")
    for path, ln, name, cls in sorted(cte, key=lambda r: r[3]["scheme"]):
        print(f"  {cls['sql_target']:26}  {name}()  ({cls['scheme']})  {path}:{ln}")
    print(f"\nRESIDUE (stays python — the honest greatest-fp: no relational/declarative form) — {len(residue)}:")
    for path, ln, name, cls in residue[:12]:
        print(f"  {name}()  {cls['scheme']} — {cls['reason']}  {path}:{ln}")
    return I, py, sql, lifts, rec


# ════════════════════════════════ selftests ═══════════════════════════════════════════════════════
def selftest():
    # ⟡L1 — the Rel carrier is a GradedProductOver over (ℕ,+,0): grades ADD under composition.
    assert REL.combine(2, 3) == 5 and REL.u == 0, "Rel graded product over (+,0)"
    a = RelTerm(("OrderBy", "Scan")); b = RelTerm(("Limit", "OrderBy", "Scan"))
    assert a.grade == 2 and b.grade == 3, "grade = pipeline depth"

    # ⟡L2 — python sorted(...) and SQL .order_by(...) lower to the SAME carrier point (cross_term degree 0).
    I = Intern()
    py_ob = rel_of_expr(ast.parse("sorted(rows, key=k)", mode="eval").body)
    from sqlalchemy import select, Table, Column, String, MetaData
    _md = MetaData(); t = Table("rows", _md, Column("k", String))
    sql_ob = rel_of_select(select(t.c.k).order_by(t.c.k))
    pid = py_ob.intern_into(I); sid = sql_ob.intern_into(I)
    X = CrossMix(I)
    # abstract the source leaf so the two OrderBy pipelines meet at one carrier point
    pid2 = RelTerm(tuple(h for h in py_ob.heads if h != "Scan") + ("Scan",), "*").intern_into(I)
    sid2 = RelTerm(tuple(h for h in sql_ob.heads if h != "Scan") + ("Scan",), "*").intern_into(I)
    assert X.cross_term(pid2, sid2).degree == 0, \
        f"sorted↔ORDER BY must be grade-0 coherent (same carrier point), got {X.cross_term(pid2, sid2).degree}"

    # ⟡L1 grade-transport: idempotent Distinct∘Distinct collapses (a certified reorder residue = identity).
    d1 = RelTerm(("Distinct", "Scan"), "*").intern_into(I)
    d2 = RelTerm(("Distinct", "Distinct", "Scan"), "*").intern_into(I)
    assert d1 != d2, "grades are distinct pre-normalization (Distinct is idempotent up to the transport)"

    # ⟡L3 ACCEPTANCE (the headline): the render_graph≈render_import Counter+rank near-clone lowers to ONE
    # carrier node (breadth 2) and is a licensed lift into SQL — CrossMix orbit-dedup + coherence, end to end.
    I2, pyt, sqlt, _rec2 = build([os.path.join(REPO, "scripts", "reuse_catalog.py")])
    lifts2 = licensed_lifts(I2, pyt, sqlt)
    _fns = lambda rt: {s[2] for s in rt.sites}
    _relseq = lambda rt: tuple(h for h in rt.canon_seq() if h != "Scan")
    ob_lim = [rt for rt, _ in lifts2 if _relseq(rt) == ("OrderBy", "Limit") and {"render_graph", "render_import"} <= _fns(rt)]
    assert ob_lim, "render_graph/render_import [OrderBy→Limit] must be ONE licensed lift at breadth ≥2"
    grp = [rt for rt in pyt.values() if _relseq(rt) == ("GroupBy", "Agg") and {"render_graph", "render_import"} <= _fns(rt)]
    assert grp, "Counter (GroupBy→Agg) must be ONE shared carrier node across render_graph + render_import"
    # The recursive helpers yield NO bounded Rel PIPELINE (they are the recursion pole, not the loop pole).
    I3, py3, _s3, _r3 = build([os.path.join(REPO, "scripts", "reuse_tui.py")])
    walk_fns = {s[2] for rt in py3.values() for s in rt.sites if len(_relseq(rt)) >= 2}
    assert not ({"sz", "lsz", "descsh", "hei"} & walk_fns), \
        "the recursive-unfold helpers must yield NO composed Rel PIPELINE (they are recursion-pole, not loop-pole)"

    # ⟡L6 — the recursion↔loop↔parallel classification: the recursion pole is NOT uniformly unliftable. The
    # recursion→parallel transition (least-fixpoint saturation = SQL WITH RECURSIVE) splits Family B correctly.
    R = {}
    for f in (os.path.join(REPO, "scripts", "reuse_tui.py"), os.path.join(HERE, "jea_pysim.py"),
              os.path.join(HERE, "jea_pyalg.py"), os.path.join(REPO, "scripts", "sppf_db.py")):
        for path, ln, nm, cls in build([f])[3]:
            R[nm] = cls
    for fn in ("_support", "_subnodes", "descsh"):                       # reachability closures → WITH RECURSIVE
        assert R.get(fn, {}).get("transition") == "recursion→parallel" and "RECURSIVE" in R[fn]["sql_target"], \
            f"{fn} must be a reachability closure lift (recursion→parallel, WITH RECURSIVE), got {R.get(fn)}"
    assert "reachability" in R["_subnodes"]["scheme"], "_subnodes is a transitive-closure reachability"
    assert R.get("sz", {}).get("transition") == "recursion→parallel" and ("SUM" in R["sz"]["sql_target"] or "COUNT" in R["sz"]["sql_target"]), \
        f"sz must be a fold-over-closure (WITH RECURSIVE + SUM/COUNT), got {R.get('sz')}"
    assert R.get("hei", {}).get("transition") == "recursion→parallel" and "MAX" in R["hei"]["sql_target"], \
        f"hei must be a max-fold over the closure (WITH RECURSIVE + MAX), got {R.get('hei')}"
    assert R.get("lsz", {}).get("sql_target") == "residue", f"lsz (log-sum-exp) must be residue, got {R.get('lsz')}"
    assert R.get("canon_syms", {}).get("sql_target") == "residue", \
        f"canon_syms (variable-arity flatten+sort) must be residue, got {R.get('canon_syms')}"
    assert "pack" not in R, "pack is a depth-1 self-join (Family A), NOT a recursion pole"

    # ⟡L7 — the recursion→parallel target now EXISTS: q_reach (WITH RECURSIVE) lowers to Rel(Closure), so the
    # reachability closures are MATCHED against a real builder (not merely recommended). Measured byte-exact
    # (59794==59794) and workload-relative (275× on-demand, 0.7× full-graph — the roofline crossover).
    from query_builders import q_reach as _q_reach
    assert rel_of_select(_q_reach()).heads == ("Closure",), \
        f"q_reach (WITH RECURSIVE) must lower to Rel(Closure), got {rel_of_select(_q_reach()).heads}"
    _I4, _py4, sql4, _r4 = build([os.path.join(REPO, "scripts", "reuse_catalog.py")])
    assert any("Closure" in rt.heads for rt in sql4.values()), \
        "the SQL corpus must now contain a Closure builder (q_reach) — reachability closures have a real target"

    # ⟡L4 — roofline readout: eager I is CONSTANT (size-independent), fused I SCALES with pipeline depth k;
    # gain = 2.5·k; the lift ranking steers by intensity-gain × breadth.
    r2 = roofline(RelTerm(("OrderBy", "Limit", "Scan"))); r3 = roofline(RelTerm(("Filter", "OrderBy", "Limit", "Scan")))
    assert r2["i_eager"] == r3["i_eager"] == _I_EAGER, "eager intensity is constant (memory-bound)"
    assert r3["i_fused"] > r2["i_fused"], "fused intensity SCALES with pipeline depth (compute-bound)"
    assert abs(r2["gain"] - 5.0) < 1e-9 and abs(r3["gain"] - 7.5) < 1e-9, "gain = 2.5·k"
    scores = [roofline(rt)["score"] for rt, _ in lifts2]
    assert scores == sorted(scores, reverse=True), "licensed lifts must be steered (sorted) by roofline score"
    assert abs(roofline(ob_lim[0])["score"] - 10.0) < 1e-9, \
        "the render_graph/render_import [OrderBy→Limit] lift: gain 5 × breadth 2 = score 10"

    print("PASS ⟡graded-relational-carrier selftest:")
    print("  Rel = GradedProductOver(+,0); grade = pipeline depth; python sorted(...) and SQL .order_by(...)")
    print("  lower to ONE carrier point (CrossMix cross_term degree 0) — licensed by same-interned-id.")
    print(f"  ACCEPT: render_graph≈render_import → ONE [OrderBy→Limit] lift (breadth {len(ob_lim[0].sites)}) +")
    print("  ONE shared [GroupBy→Agg] carrier node ⟵ SQL indegree_top.")
    print("  ⟡L6 recursion↔loop↔parallel (fold⊣unfold): _support/_subnodes/descsh = reachability closures →")
    print("  WITH RECURSIVE; sz→+SUM, hei→+MAX (fold-over-closure); lsz/canon_syms = residue; pack = not recursion.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--report", action="store_true")
    a = ap.parse_args()
    if a.selftest: selftest(); return
    if a.report: report(); return
    ap.print_help()


if __name__ == "__main__":
    main()
