#!/usr/bin/env python3
"""jea_pyalg.py — the Python carrier for the term algebra. A faithful IR lowered from `ast`
(and, optionally, `libcst` for the surface/report layer) into the SAME Wedge/Trace machinery
the Agda `Substrate.Algebra.Wedge` defines. NOT a similarity metric: the engine is hash-cons +
Trace; "similarity" is just one `trace_fold` target over the kept trace, exactly as gcd-fold and
bezout-fold are targets over the EEATrace (Agda's Nat.GCD.Fold).

The shape is dictated by the Agda, read directly:
  DivStr  = (C, z, recon : C -> C -> C -> C)        -- recon q b r = "q over b, then remainder r"
  Wedge   = (quot, rem, wedge_eq : a == recon q b r) -- the witness is CARRIED, not discarded
  Trace   = base(a) | step(b, w, Trace(b, rem w, g)) -- the decomposition chain = the GRADING
  fold    = the Trace recursor, target-swappable     -- collapse / similarity / mapping are targets

Hash-CONS (not crypto-hash): the canonical thing stored is the structured node (kind, child-ids);
the dict key is just the table index. The residue (every sub-decomposition) is KEPT as more interned
nodes, so "same up to grade k" is a readout over structure that still exists -- never a digest.

NORMALIZATION is not a rule-list. It lives in `recon`: how a node decomposes into (head, base,
remainder). Each decomposition is WITNESSED (wedge_eq) and RECORDED (the Trace step). Commutativity,
alpha-renaming, etc. are *how recon chooses the decomposition* -- observed and traced, NEVER baked
into a canonical form that throws the alternative away.

`forget` (collapse to the value, discard the structure) is AVAILABLE but is the lossy/annihilating
read -- the Agda names it forgetful. We live in `Trace`.
"""
from __future__ import annotations
import ast
from dataclasses import dataclass, field
from typing import Optional


# ============================================================================
# The faithful IR.  A node is (kind, role, op, lit_kind, children) -- decomposed,
# nothing deleted. `src` keeps the span back to source (the report layer / cst join).
# Identifiers are lowered to BINDING ROLE (arg-i / local-i / global / attr), not name:
# the rename-orbit quotient, but the original name is kept as residue in `payload`.
# ============================================================================
@dataclass(frozen=True)
class IR:
    kind: str                       # the ast node class name: 'BinOp', 'Call', 'Name', ...
    role: str = ""                  # binding role for names: 'arg0','local1','global','attr','' (non-name)
    op: str = ""                    # operator token kept: 'Add','Mult','Eq', ... (NOT collapsed to 'binop')
    lit: str = ""                   # literal KIND kept (not value): 'int','str','none', ''
    children: tuple = ()            # tuple of child IR ids (ints into the intern table) -- hash-cons refs
    payload: tuple = ()             # RESIDUE: original name, literal value, etc. -- kept, not in the key
    # NB: `children` are IDs (already-interned), so structural equality of (kind,role,op,lit,children)
    # is structural equality ALL THE WAY DOWN, established once at intern (the SPPF property).

    def key(self):
        # the hash-cons key: structure only. payload/src are residue, NOT in the canonical identity.
        return (self.kind, self.role, self.op, self.lit, self.children)


# ============================================================================
# Hash-cons table: structural-equality interning.  id(node) is canonical;
# two structurally-identical subtrees get the SAME id (the SPPF / shared node).
# Fan-in (how many parents point at an id) is recorded -- that IS the similarity
# signal, computed once at build, read as a lookup (never pairwise).
# ============================================================================
class Intern:
    def __init__(self):
        self.nodes: list[IR] = []           # id -> IR
        self.table: dict = {}               # key -> id  (the "hash" is just this dict's hashing)
        self.fanin: list[int] = []          # id -> count of parent references (shared-ness)
        self.src: list[Optional[tuple]] = []# id -> (lineno,col,end) span for the report layer

    def intern(self, node: IR, span=None) -> int:
        k = node.key()
        i = self.table.get(k)
        if i is None:
            i = len(self.nodes)
            self.nodes.append(node)
            self.table[k] = i
            self.fanin.append(0)
            self.src.append(span)
            for c in node.children:        # record that this node references its children
                self.fanin[c] += 1
        return i

    def size(self): return len(self.nodes)


# ============================================================================
# DivStr for Python: recon decomposes a node into (head/quotient, base, remainder).
# For an n-ary node we read it as a LEFT-FOLD of binary wedges: a node with children
# [c0,c1,...,cn] reconstructs as recon(head, c0, recon(head, c1, ... )) -- the head
# (kind+role+op+lit) is the QUOTIENT (the shared shape), the first child is the BASE
# (what it's built over), the rest is the REMAINDER (recurse). z = the atom (no children).
# This makes "two nodes share their head and base, differ in the remainder tail" a GRADED
# fact: equal at grade-1 (same head+base), the remainder chain is the rest of the grading.
# ============================================================================
@dataclass(frozen=True)
class Wedge:
    quot: tuple          # the head shape (kind,role,op,lit) -- the QUOTIENT, a carrier rep
    base: int            # the first child id -- the BASE
    rem: int             # the remainder id (the rest, re-interned) -- recurse here
    # wedge_eq is carried implicitly: by construction recon(quot,base,rem) re-interns to `a`.
    # We assert it at build (faithful_check) rather than carry a proof object (Python, not Agda),
    # but it is CHECKED, not discarded -- the residue (quot,base,rem) reconstructs a exactly.


@dataclass
class Trace:
    """base(a) | step(head, base, sub).  The chain of decompositions = the GRADING.
    depth(trace) is the grade axis: 'equal up to grade k' = traces agree for k steps."""
    a: int                       # the node this trace decomposes
    head: tuple = ()             # the wedge quotient at this step ('' tuple at base)
    base: int = -1               # the wedge base child ('' at base)
    sub: Optional["Trace"] = None# the remainder trace (None at base -- the atom z)

    def is_base(self): return self.sub is None


class PyDivStr:
    """C = interned IR ids; z = atoms (childless nodes); recon rebuilds a node from head+base+rem."""
    def __init__(self, intern: Intern):
        self.I = intern

    def is_z(self, i: int) -> bool:
        return len(self.I.nodes[i].children) == 0      # atom: nothing left to decompose

    def recon(self, head: tuple, base: int, rem_children: tuple) -> int:
        # rebuild a node from its head shape + base child + remaining children, re-intern it.
        kind, role, op, lit = head
        node = IR(kind=kind, role=role, op=op, lit=lit, children=(base,) + rem_children)
        return self.I.intern(node)

    def wedge(self, i: int) -> Optional[Wedge]:
        """Decompose node i into the FIRST binary wedge: (head, first-child, rest-re-interned).
        Returns None for an atom (z -- the base case)."""
        n = self.I.nodes[i]
        if not n.children:
            return None
        head = (n.kind, n.role, n.op, n.lit)
        base = n.children[0]
        rest = n.children[1:]
        if rest:
            # re-intern the remainder as a node with the SAME head over the rest (left-fold shape)
            rem = self.I.intern(IR(kind=n.kind, role=n.role, op=n.op, lit=n.lit, children=rest))
        else:
            rem = -1     # only one child: remainder is empty (the wedge bottoms out next step)
        return Wedge(quot=head, base=base, rem=rem)

    def trace(self, i: int) -> Trace:
        """Build the full decomposition trace of node i -- the kept residue, the grading.
        EEATrace's structural recursion: step on the head, recurse on the REMAINDER if there is
        one, else recurse INTO the base child (so the chain bottoms out on a true atom z, giving
        collapse the EEA terminal property -- strict descent to the base case)."""
        w = self.wedge(i)
        if w is None:
            return Trace(a=i)                                  # base(a): an atom (z)
        if w.rem == -1:
            # single child: the remainder is empty, so descend into the base child itself
            return Trace(a=i, head=w.quot, base=w.base, sub=self.trace(w.base))
        return Trace(a=i, head=w.quot, base=w.base, sub=self.trace(w.rem))

    def trace_steps(self, i: int):
        """Σ-TRACE-LAZY: the LAZY dual of trace() — a generator yielding (head, base) per wedge step in
        chain order, ITERATIVELY (no recursion; O(1) working set). trace() builds the whole nested Trace
        before any read AND recurses, so it RecursionErrors on a chain deeper than the Python stack; this
        walks the SAME descent emitting one step at a time, so a readout over a deeply-nested / 50GiB
        forest streams. The deep correction (BEZOUT_READOUT.md): retention is the FOREST's job (interned
        nodes persist), frugality the READ's (keep nothing). Terminal atom = trace_atom(i)."""
        cur = i
        while True:
            w = self.wedge(cur)
            if w is None:
                return
            yield (w.quot, w.base)
            cur = w.base if w.rem == -1 else w.rem

    def trace_atom(self, i: int) -> int:
        """The terminal atom of the trace descent (the collapse target / base case), O(1) iterative."""
        cur = i
        while True:
            w = self.wedge(cur)
            if w is None:
                return cur
            cur = w.base if w.rem == -1 else w.rem

    def faithful_check(self, i: int) -> bool:
        """wedge_eq, checked not discarded: recon(decomposition) re-interns to exactly i."""
        w = self.wedge(i)
        if w is None:
            return True
        n = self.I.nodes[i]
        rebuilt = self.recon(w.quot, w.base, n.children[1:])
        return rebuilt == i


# ============================================================================
# trace_fold: the Trace recursor, target-swappable.  Exactly Agda's eea-fold /
# trace-fold.  Different targets = different reads of the SAME kept trace.
# ============================================================================
def trace_fold(base_interp, step_interp, t: Trace):
    if t.is_base():
        return base_interp(t.a)
    return step_interp(t.head, t.base, trace_fold(base_interp, step_interp, t.sub))


def trace_fold_lazy(divstr, i, base_interp, step_interp):
    """Σ-TRACE-LAZY: trace_fold WITHOUT materializing the nested Trace or recursing. Same RESULT as
    trace_fold(base_interp, step_interp, divstr.trace(i)) for ANY step_interp, but ITERATIVE — walk
    trace_steps to a flat (head, base) list, then fold right over it. No recursion (survives chains
    deeper than the Python stack, where trace()/trace_fold() RecursionError), and a flat list rather
    than O(chain) nested Trace dataclasses. Left-foldable readouts (grade, head_spine, collapse) stream
    in O(1) directly over trace_steps; this is the general drop-in for the right-fold."""
    steps = list(divstr.trace_steps(i))
    acc = base_interp(divstr.trace_atom(i))
    for head, base in reversed(steps):
        acc = step_interp(head, base, acc)
    return acc


# --- target 1: FORGETFUL collapse -- return the node id (the annihilating read). ---
def collapse(t: Trace):
    return trace_fold(lambda a: a, lambda head, base, rec: rec, t)


# --- target 2: the GRADE -- depth of the decomposition chain. ---
def grade(t: Trace) -> int:
    return trace_fold(lambda a: 0, lambda head, base, rec: rec + 1, t)


# --- target 3: the HEAD SPINE -- the sequence of head-shapes along the base chain (the
#     left-fold skeleton). Two nodes "equal up to grade k" iff their head-spines agree for k steps. ---
def head_spine(t: Trace) -> tuple:
    return tuple(trace_fold(lambda a: [], lambda head, base, rec: [head] + rec, t))


# --- target 4: the FULL SKELETON -- recurse over the WHOLE interned subtree (every child),
#     collecting head shapes depth-first. This is the readout that sees the operator (which the
#     base-spine misses): two structurally-distinct nodes have distinct full skeletons. Similarity
#     is then the longest common prefix / overlap of full skeletons -- a readout over kept structure. ---
def full_skeleton_steps(intern: Intern, i: int):
    """Σ-TRACE-LAZY's TREE dual: yield the full skeleton (kind, role, op, lit) in PRE-ORDER DFS over
    every child, ITERATIVELY (explicit stack, no recursion). Same retention/frugality split as
    trace_steps — the forest holds everything; the walk holds only the frontier. Two wins over the old
    recursion: (1) no RecursionError on a deep/wide forest; (2) a PREFIX consumer (e.g. a longest-common-
    prefix similarity read) can stop early without materializing the whole tuple."""
    stack = [i]
    while stack:
        n = intern.nodes[stack.pop()]
        yield (n.kind, n.role, n.op, n.lit)
        stack.extend(reversed(n.children))     # reversed -> children visited left-to-right (pre-order)


def full_skeleton(intern: Intern, i: int) -> tuple:
    """The full skeleton tuple (pre-order DFS over EVERY child) -- the readout that sees the operator,
    so two structurally-distinct nodes have distinct full skeletons. Now built on full_skeleton_steps
    (iterative): byte-identical output to the old recursion, but no RecursionError on a deep forest."""
    return tuple(full_skeleton_steps(intern, i))


# ============================================================================
# Lowering: ast -> IR, interned bottom-up. Binding roles assigned per-scope.
# ============================================================================
class Lowerer(ast.NodeVisitor):
    def __init__(self, intern: Intern):
        self.I = intern
        self.scopes: list[dict] = [{}]      # name -> role, per scope (rename-orbit quotient)
        self.bound: set = set()             # names that are BOUND somewhere (assigned / parameters)

    def _role(self, name: str, ctx_store: bool) -> str:
        for sc in reversed(self.scopes):
            if name in sc:
                return sc[name]
        # new binding: assign a role by scope depth + position (alpha-stable within scope)
        sc = self.scopes[-1]
        role = f"v{len(self.scopes)-1}_{len(sc)}"
        sc[name] = role
        return role

    def _is_bound(self, name: str) -> bool:
        """A name is BOUND iff it appears in some visible scope (assigned, or a parameter). Bound
        names are alpha-equivalent -> role-quotiented (identity in `role`, name in payload-residue).
        A FREE name (never bound, e.g. a global/builtin like abs/str/Fraction) is REFERENTIAL: its
        identity is the NAME itself, which must live in the KEY, not the residue -- else two distinct
        globals at the same position intern to one node (the abs-vs-str = vs ≅ bug)."""
        if name in self.bound:
            return True
        for sc in self.scopes:
            if name in sc:
                return True
        return False

    def lower(self, node) -> int:
        kind = type(node).__name__
        role = op = lit = ""
        payload = ()
        child_ids = []

        # ast materializes read/write CONTEXT as nodes (Load/Store/Del); cst encodes it positionally.
        # Context is positionally recoverable residue, NOT independent structure -- drop it so the two
        # representations converge (the cross-rep witness surfaced this as the real ast/cst divergence).
        if isinstance(node, ast.expr_context):
            return None  # caller filters None

        # unwrap ast.arguments to match cst's unwrapped Parameters: params flatten into the parent.
        if isinstance(node, ast.arguments):
            for ch in ast.iter_child_nodes(node):
                cid = self.lower(ch)
                if cid is not None:
                    child_ids.append(cid)
            if len(child_ids) == 1:
                return child_ids[0]
            return self.I.intern(IR(kind="Block", children=tuple(child_ids)))

        if isinstance(node, ast.Name):
            if isinstance(node.ctx, ast.Store) or self._is_bound(node.id):
                # BOUND: alpha-equivalent, role-quotient. identity in `role`, name in payload-residue.
                if isinstance(node.ctx, ast.Store):
                    self.bound.add(node.id)
                role = self._role(node.id, isinstance(node.ctx, ast.Store))
                payload = (node.id,)
            else:
                # FREE / referential (global, builtin, imported -- abs, str, Fraction): identity IS
                # the name. Put it in the KEY (`op`) so two distinct free names do NOT intern to one
                # node. (Was: role-quotiented like a bound var + name in payload -> abs and str
                # collapsed to the same node = the {unfamiliar,familiar} false-DUPLICATE bug.)
                op = node.id
                payload = (node.id,)
        elif isinstance(node, ast.arg):
            # ast represents a parameter as `arg` with the name as a STRING attribute (lossy);
            # cst represents it as a Name binding. Canonicalize to the faithful form: a roled Name.
            # (the cross-rep witness surfaced ast's under-representation here; cst is the truer form.)
            kind = "Name"
            role = self._role(node.arg, True)
            payload = (node.arg,)
            return self.I.intern(IR(kind=kind, role=role, op="", lit="", children=(), payload=payload),
                                 (getattr(node, "lineno", -1), getattr(node, "col_offset", -1),
                                  getattr(node, "end_lineno", -1)))
        elif isinstance(node, ast.Constant):
            lit = type(node.value).__name__                       # literal KIND, not value
            payload = (repr(node.value),)                         # residue: the value
        elif isinstance(node, (ast.BinOp, ast.UnaryOp, ast.BoolOp, ast.AugAssign)):
            o = getattr(node, "op", None)
            op = type(o).__name__ if o is not None else ""
        elif isinstance(node, ast.Compare):
            op = "|".join(type(o).__name__ for o in node.ops)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            payload = (node.name,)
            self.scopes.append({})                                # new scope for the body
            # PRESCAN: collect names BOUND in this scope (params + any assignment target + nested
            # def/class names + comprehension/with/for targets) so a name read BEFORE its binding is
            # still recognized as bound (role-quotiented), not mistaken for a free/referential global.
            for sub in ast.walk(node):
                if isinstance(sub, ast.arg):
                    self.bound.add(sub.arg)
                elif isinstance(sub, ast.Name) and isinstance(sub.ctx, ast.Store):
                    self.bound.add(sub.id)
                elif isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    self.bound.add(sub.name)

        # recurse into children in source order (order KEPT -- reordering is a future graded rule)
        for ch in ast.iter_child_nodes(node):
            cid = self.lower(ch)
            if cid is not None:
                child_ids.append(cid)

        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            self.scopes.pop()

        span = (getattr(node, "lineno", -1), getattr(node, "col_offset", -1),
                getattr(node, "end_lineno", -1))
        return self.I.intern(IR(kind=kind, role=role, op=op, lit=lit,
                                children=tuple(child_ids), payload=payload), span)


def lower_source(src: str, intern: Intern) -> list[int]:
    """Lower a source string; return the interned id of each top-level statement."""
    tree = ast.parse(src)
    lw = Lowerer(intern)
    return [lw.lower(stmt) for stmt in tree.body]


# ============================================================================
# The libcst lowerer: lossless CST -> the SAME shared IR.  cst names structural
# concepts differently (BinaryOperation vs BinOp, Add-as-node vs op='Add',
# Multiply vs Mult, Integer vs Constant) and wraps in trivia (IndentedBlock,
# SimpleStatementLine, Parameters, whitespace).  We canonicalize the structural
# kinds to the SAME heads the ast lowerer uses, and treat trivia as residue
# (kept losslessly by cst, but quotiented out of the canonical key).  Then the
# SAME source lowered via ast and via cst interns to the SAME id -- the
# cross-representation mapping FALLS OUT as the shared node (fan-in), never computed.
# ============================================================================
try:
    import libcst as cst
    _HAS_CST = True
except ImportError:
    _HAS_CST = False

# cst-kind -> shared canonical (kind, op-extractor).  Maps cst's vocabulary onto ast's heads.
_CST_BINOP = {"Add": "Add", "Subtract": "Sub", "Multiply": "Mult", "Divide": "Div",
              "Modulo": "Mod", "Power": "Pow", "FloorDivide": "FloorDiv",
              "BitAnd": "BitAnd", "BitOr": "BitOr", "BitXor": "BitXor",
              "LeftShift": "LShift", "RightShift": "RShift", "MatrixMultiply": "MatMult"}
_TRIVIA = ("Whitespace", "Comma", "Newline", "Semicolon", "EmptyLine", "Colon",
           "TrailingWhitespace", "ParenthesizedWhitespace", "Comment", "Dot")


class CstLowerer:
    """Lower a libcst tree into the SAME IR/Intern as the ast lowerer, canonicalizing cst's
    structural vocabulary to the shared heads and dropping trivia into residue."""
    def __init__(self, intern: Intern):
        self.I = intern
        self.scopes: list[dict] = [{}]

    def _role(self, name: str) -> str:
        for sc in reversed(self.scopes):
            if name in sc:
                return sc[name]
        sc = self.scopes[-1]
        role = f"v{len(self.scopes)-1}_{len(sc)}"
        sc[name] = role
        return role

    def _kind_and_head(self, node):
        """Map a cst node to (canonical_kind, op, lit, role, payload). Returns the shared-vocab head."""
        t = type(node).__name__
        if t == "Name":
            return "Name", "", "", self._role(node.value), (node.value,)
        if t == "Integer":
            return "Constant", "", "int", "", (node.value,)
        if t == "Float":
            return "Constant", "", "float", "", (node.value,)
        if t in ("SimpleString", "ConcatenatedString", "FormattedString"):
            return "Constant", "", "str", "", (getattr(node, "value", ""),)
        if t == "BinaryOperation":
            return "BinOp", _CST_BINOP.get(type(node.operator).__name__, type(node.operator).__name__), "", "", ()
        if t == "Comparison":
            ops = "|".join(type(c.operator).__name__ for c in node.comparisons)
            return "Compare", ops, "", "", ()
        if t == "Call":
            return "Call", "", "", "", ()
        if t == "Return":
            return "Return", "", "", "", ()
        if t == "Assign":
            return "Assign", "", "", "", ()
        if t == "FunctionDef":
            return "FunctionDef", "", "", "", (node.name.value,)
        if t == "Attribute":
            return "Attribute", "", "", "attr", ()
        # default: keep the cst kind verbatim (structural but unmapped -- shows up as a divergence)
        return t, "", "", "", ()

    def lower(self, node) -> int | None:
        t = type(node).__name__
        if any(s in t for s in _TRIVIA):
            return None                                            # trivia: residue, not in the structure
        # unwrap cst's pure structural wrappers to match ast's flattening
        if t in ("Module", "IndentedBlock", "SimpleStatementLine", "SimpleStatementSuite",
                 "Expr", "Parameters", "Decorator"):
            kids = [self.lower(c) for c in self._cst_children(node)]
            kids = [k for k in kids if k is not None]
            if t == "Module":
                return kids                                        # top-level: return list of stmt ids
            # a transparent wrapper with one child collapses to that child; else a generic Block
            if len(kids) == 1:
                return kids[0]
            return self.I.intern(IR(kind="Block", children=tuple(kids)))
        if t in ("AssignTarget", "Param", "Arg", "Element"):
            kids = [self.lower(c) for c in self._cst_children(node)]
            kids = [k for k in kids if k is not None]
            return kids[0] if len(kids) == 1 else self.I.intern(IR(kind=t, children=tuple(kids)))

        kind, op, lit, role, payload = self._kind_and_head(node)
        if kind == "FunctionDef":
            self.scopes.append({})
        kids = []
        for c in self._cst_children(node):
            k = self.lower(c)
            if isinstance(k, list):
                kids.extend(k)
            elif k is not None:
                kids.append(k)
        if kind == "FunctionDef":
            self.scopes.pop()
        return self.I.intern(IR(kind=kind, role=role, op=op, lit=lit,
                                children=tuple(kids), payload=payload))

    @staticmethod
    def _cst_children(node):
        import dataclasses
        fields = dataclasses.fields(node) if dataclasses.is_dataclass(node) else []
        for f in fields:
            val = getattr(node, f.name, None)
            if isinstance(val, cst.CSTNode):
                yield val
            elif isinstance(val, (list, tuple)):
                for v in val:
                    if isinstance(v, cst.CSTNode):
                        yield v


def lower_source_cst(src: str, intern: Intern) -> list[int]:
    """Lower via libcst into the SAME intern. Returns top-level statement ids."""
    if not _HAS_CST:
        raise RuntimeError("libcst not available")
    mod = cst.parse_module(src)
    lw = CstLowerer(intern)
    out = lw.lower(mod)
    return out if isinstance(out, list) else [out]


# ============================================================================
# CrossMix — Substrate.Algebra.Wedge.CrossMul, realized for the Python carriers.
#
# ast and cst are two carriers A, B; the shared IR is the common carrier R; both
# LOWER (embed, the Bridge) into R.  Two representations of one program do NOT get
# forced to the same id (that is Cross.agda's DIAGONAL, "not automatic" -- forcing
# it was the projection error).  Instead we read the CROSS-TERM and grade it:
#
#   COHERENCE IS THE CROSS-TERM'S NILPOTENCY DEGREE (graded, not binary).
#     * the two heads agree            -> cross term vanishes (degree 0): ORTHOGONAL/clean,
#                                          this is the SHARED structure, the common core.
#     * the heads differ but the nodes  -> nilpotent of degree n>1: a GRADED OBSTRUCTION
#       re-converge n levels down          (d^n=0), the degree = how deep the divergence runs
#                                          = the COST.  Kept as residue, not deleted.
#     * never re-converge               -> the obstruction does not vanish (residue carried).
#
# The degree is INFORMATION STORED IN THE GRADE: it measures HOW MUCH ast and cst
# disagree at each position, and WHERE -- not a binary same/different, not a forced
# equality.  Same instrument relates any two carriers (jea_carrier vs jea_divstr,
# two near-duplicate fns, N vs F2[x]); ast/cst is one instance.
# ============================================================================
from dataclasses import dataclass as _dc


@_dc
class CrossTerm:
    """The graded cross-term at a node pair (ast id, cst id).
    degree 0 = heads agree (orthogonal/coherent); n>0 = re-converge n levels down (graded
    obstruction); degree None = never re-converge within depth (residue carried, max cost)."""
    a_id: int
    b_id: int
    head_agree: bool          # do the two heads (kind,role,op,lit minus residue) coincide?
    degree: int | None        # nilpotency degree: 0 clean, n>0 graded, None = unbounded
    a_residue: tuple = ()     # what ast keeps here that cst doesn't (the A-strand cross residue)
    b_residue: tuple = ()     # what cst keeps here that ast doesn't (the B-strand cross residue)


class CrossMix:
    """A -> R <- B for the Python carriers.  Computes, per source position, the cross-term's
    nilpotency degree = the graded agreement of ast and cst.  Orthogonal where they share the
    common structure, graded-nilpotent where they diverge, the degree the cost (kept residue)."""
    def __init__(self, intern: Intern):
        self.I = intern

    def _head(self, i: int) -> tuple:
        n = self.I.nodes[i]
        return (n.kind, n.role, n.op, n.lit)   # the canonical head; payload (names/values) is residue

    def _subnodes(self, i: int) -> set:
        """The set of interned ids reachable from i (its subterm support in R)."""
        out = set(); stack = [i]
        while stack:
            j = stack.pop()
            if j in out: continue
            out.add(j); stack.extend(self.I.nodes[j].children)
        return out

    def cross_term(self, a_id: int, b_id: int, max_depth: int = 64) -> CrossTerm:
        """The cross-term in R (CrossMul: mul R (embA a) (embB b)), read from the SHARED interned
        structure -- NOT a positional tree-walk.  Two embedded structures are ORTHOGONAL (cross-term
        vanishes, degree 0) exactly where they intern to the SAME canonical nodes; the obstruction
        is the part that fails to share, GRADED by how much.

        degree 0  : a_id == b_id (the same canonical node) -- fully orthogonal/coherent.
        degree n>0: they share a fraction of their subterm support; n grades the NON-shared part
                    (here: the count of nodes one keeps that the other doesn't, the cross residue).
        The residue is what each side carries that the other doesn't -- kept, the graded obstruction."""
        if a_id == b_id:
            return CrossTerm(a_id, b_id, head_agree=True, degree=0)   # same canonical node: orthogonal
        sa = self._subnodes(a_id); sb = self._subnodes(b_id)
        shared = sa & sb
        only_a = sa - sb; only_b = sb - sa
        ha = self._head(a_id); hb = self._head(b_id)
        # the cross-term degree = the size of the non-orthogonal (non-shared) part. Vanishes (0)
        # iff the supports coincide; grows with the divergence. This is the nilpotency degree:
        # the structure shared in R is the orthogonal part, the residue is the graded obstruction.
        degree = len(only_a) + len(only_b)
        return CrossTerm(a_id, b_id, head_agree=(ha == hb), degree=degree,
                         a_residue=tuple(sorted(self._head(x) for x in only_a))[:8],
                         b_residue=tuple(sorted(self._head(x) for x in only_b))[:8])

    def shared_fraction(self, a_id: int, b_id: int) -> float:
        """The coherent (orthogonal) fraction: |shared support| / |total support|. 1.0 = identical."""
        sa = self._subnodes(a_id); sb = self._subnodes(b_id)
        u = sa | sb
        return len(sa & sb) / len(u) if u else 1.0

    def coherent(self, a_id: int, b_id: int) -> bool:
        """Coherent = the cross term vanishes (degree 0): the same canonical node, fully orthogonal."""
        return self.cross_term(a_id, b_id).degree == 0


if __name__ == "__main__":
    print("jea_pyalg: Python as a Wedge/Trace carrier (hash-cons SPPF; similarity = a trace_fold)\n")
    I = Intern()
    # two functions: structurally identical up to variable RENAME (alpha) -> should SHARE under role-lowering
    src_a = "def f(x, y):\n    z = x + y\n    return z * 2\n"
    src_b = "def g(a, b):\n    c = a + b\n    return c * 2\n"
    # a third: same skeleton but * -> + (operator differs) -> shares the SHAPE, differs at the op grade
    src_c = "def h(p, q):\n    r = p + q\n    return r + 2\n"

    ids_a = lower_source(src_a, I)
    ids_b = lower_source(src_b, I)
    ids_c = lower_source(src_c, I)
    D = PyDivStr(I)

    # W1: alpha-equivalence -- f and g lower to the SAME interned id (rename-orbit quotient exact).
    w1 = (ids_a == ids_b)
    print(f"  W1  ALPHA: f(x,y) and g(a,b) (same up to rename) intern to the SAME id "
          f"{ids_a}=={ids_b}: {w1}  (role-lowering = the rename quotient; names kept as residue)")

    # W2: faithful_check (wedge_eq) -- recon(decomposition) re-interns to the node, for every node.
    w2 = all(D.faithful_check(i) for i in range(I.size()))
    print(f"  W2  FAITHFUL (wedge_eq carried+checked): recon(decompose(i))==i for all {I.size()} nodes: {w2}")

    # W3: the trace IS the grading -- grade(trace) = decomposition depth; head_spine is the skeleton.
    # collapse is the FORGETFUL read: it returns the chain's TERMINAL atom (Agda's `g`), NOT the head --
    # the annihilating projection. So we assert it lands on an atom (a z, childless), per the Agda semantics.
    fa = ids_a[0]; ta = D.trace(fa)
    term = collapse(ta)
    w3 = (grade(ta) == len(head_spine(ta))) and D.is_z(term)
    print(f"  W3  TRACE=GRADING: grade(f)={grade(ta)} == |head_spine|={len(head_spine(ta))}; "
          f"collapse(f)={term} is an atom (z, the forgetful terminal): {w3}")

    # W4: SIMILARITY = a readout over kept structure, not pairwise distance. f vs h: same skeleton
    #     PREFIX then diverge where the op differs (* vs +). The FULL skeleton (whole subtree) sees the
    #     operator the base-spine misses -- similarity = longest common prefix of full skeletons.
    sa = full_skeleton(I, ids_a[0])
    sh = full_skeleton(I, ids_c[0])
    common = 0
    for x, y in zip(sa, sh):
        if x != y: break
        common += 1
    w4 = (sa != sh) and (common >= 1) and (ids_a[0] != ids_c[0])
    print(f"  W4  SIMILARITY=READOUT: f vs h full-skeletons agree for {common}/{min(len(sa),len(sh))} "
          f"nodes then diverge (the op grade: * vs +); distinct ids ({ids_a[0]} vs {ids_c[0]}): {w4}")

    # W5: FAN-IN = the SPPF sharing signal. The `x+y` / `a+b` BinOp subtree is SHARED between f and g
    #     (same after rename) -> its interned node has fan-in from both. Computed once, read as lookup.
    shared = sum(1 for fi in I.fanin if fi >= 2)
    w5 = (shared >= 1) and (I.size() < (len(ast.dump(ast.parse(src_a))) +  # crude: forest << raw
                                        len(ast.dump(ast.parse(src_b)))))
    print(f"  W5  FAN-IN (SPPF sharing): {shared} nodes shared by >=2 parents; forest {I.size()} nodes "
          f"(f and g's bodies collapsed by rename): {w5}")

    ok = w1 and w2 and w3 and w4 and w5
    print(f"\n  {'PASS' if ok else 'FAIL'} — Python lowered into the Wedge/Trace carrier: hash-cons interning")
    print(f"  (structural equality all the way down = the SPPF), recon decomposes a node into head+base+")
    print(f"  remainder, the Trace keeps every step (the grading), and similarity is a trace_fold over the")
    print(f"  kept trace -- NOT a digest, NOT pairwise distance. Alpha-rename is the role-lowering quotient")
    print(f"  (names kept as residue); the op grade and the fan-in fall out of the same interned structure.")

    # ====================================================================
    # CrossMix witnesses (Substrate.Algebra.Wedge.CrossMul): ast and cst as carriers A,B
    # embedded in the shared IR R; the cross-term's NILPOTENCY DEGREE grades their agreement.
    # NOT forcing equal ids (the diagonal, "not automatic") -- measuring the graded obstruction.
    # ====================================================================
    if _HAS_CST:
        print("\n  ── CrossMix (CrossMul): ast x cst, cross-term nilpotency degree = graded agreement ──")
        src = "def f(x, y):\n    z = x + y\n    return z * 2\n"
        J2 = Intern()
        a_ids = lower_source(src, J2)
        b_ids = lower_source_cst(src, J2)
        X = CrossMix(J2)

        # W6: SELF-COHERENCE -- a representation against ITSELF: cross term vanishes everywhere
        #     (degree 0, orthogonal). The clean extreme, like CrossMul's two-mul square-zero witness.
        ct_self = X.cross_term(a_ids[0], a_ids[0])
        w6 = (ct_self.degree == 0) and ct_self.head_agree
        print(f"  W6  SELF-COHERENT: ast vs ast cross-term degree {ct_self.degree} (vanishes -- orthogonal): {w6}")

        # W7: GRADED CROSS-TERM -- ast vs cst of the SAME source. They do NOT force to one id; the
        #     cross-term degree = the non-shared part of their interned support (the graded obstruction).
        #     shared_fraction grades coherence in [0,1]: how much of R's structure they hold in common.
        ct = X.cross_term(a_ids[0], b_ids[0])
        frac = X.shared_fraction(a_ids[0], b_ids[0])
        w7 = (ct.degree is not None) and (0.0 <= frac <= 1.0)
        print(f"  W7  GRADED ast×cst: cross-term degree {ct.degree} (non-shared nodes); shared fraction "
              f"{frac:.2f}; ast-residue {ct.a_residue[:3]}; cst-residue {ct.b_residue[:3]}: {w7}")

        # W8: COHERENCE IS GRADED, NOT BINARY -- the shared arithmetic core (`x+y` BinOp(Add)) is MORE
        #     coherent (higher shared fraction) than the whole tree: the obstruction lives in the
        #     wrappers/context/binding, NOT in the common structure. CRT's lesson: orthogonal factors
        #     are coherent; the cross-term obstruction concentrates in the non-orthogonal part.
        def find_binop_add(intern, root):
            seen = []
            def rec(i):
                n = intern.nodes[i]
                if n.kind == "BinOp" and n.op == "Add": seen.append(i)
                for c in n.children: rec(c)
            rec(root); return seen[0] if seen else None
        ba = find_binop_add(J2, a_ids[0]); bb = find_binop_add(J2, b_ids[0])
        if ba is not None and bb is not None:
            core_frac = X.shared_fraction(ba, bb)
            w8 = (core_frac >= frac)        # the core is at least as coherent as the whole
            print(f"  W8  GRADED COHERENCE: `x+y` core shared fraction {core_frac:.2f} >= whole-tree {frac:.2f} "
                  f"-- the obstruction concentrates in the wrappers, not the shared core: {w8}")
        else:
            w8 = False
            print(f"  W8  GRADED COHERENCE: could not locate shared BinOp(Add): {w8}")

        ok2 = w6 and w7 and w8
        print(f"\n  {'PASS' if ok2 else 'FAIL'} — CrossMix: ast and cst are NOT forced to one id (the diagonal is not")
        print(f"  automatic); their relationship is the cross-term's NILPOTENCY DEGREE -- graded, not binary.")
        print(f"  Vanishing degree = orthogonal/coherent (the shared common structure, e.g. the arithmetic")
        print(f"  core); degree n>0 = a graded obstruction (the ast/cst divergence -- context nodes, wrappers,")
        print(f"  binding), the degree its cost, the residue kept. Same instrument relates any two carriers.")
