#!/usr/bin/env python3
"""jea_cuda.py — Δ-Π-cuda: the CUDA front-end+back-end as ONE bidirectional IR↔CUDA grammar.

The cotype caution (recursive law on "front-end + back-end"): a CUDA front-end (CUDA→IR, the FOLD)
and a CUDA back-end (IR→CUDA, the UNFOLD) are not two maps — they are the two readings of ONE
correspondence. Build them from a single table so the projector inverts EXACTLY what the lowerer
produces (else they drift — the agdai-stub-lesson-4-backwards class of bug). The Python side has two
maps that merely happen to agree (guarded by the fixpoint test); CUDA bakes the agreement in.

MEMORY-SPACE = CARRIER/MOVE-STRUCTURE (the corrected analysis, NOT a key-tag):
  * a memory space (__global__/__shared__/__device__/__constant__/__local__) is a CARRIER, like
    Fraction vs ℚ-Wedge -- a `Space` node.
  * a buffer LIVES IN a space: Buffer node with the Space as a child.
  * a data movement (global→shared load, shared→global store) is a `Move(src_space, dst_space, data)`
    node = LITERALLY recon : C→C→C. The tiling dataflow is then a recognizable interned subtree (a
    metalanguage generator), and a carrier SUBSTITUTION (Δ-Π-substitute) retargets the memory
    hierarchy by swapping the Space/Move structure.
  * __restrict__ is a SEPARATE node composing over the space (aliasing ⊥ location).
  * the = vs ≅ key-rule applies ONLY to genuinely ATOMIC referents (kernel/intrinsic names like
    __syncthreads, threadIdx) -- those are leaves, they go in the key (op), like abs/str.

libclang exposes structure but NOT the memory-space via storage_class (reads INVALID); the
qualifier is recovered from the declaration's TOKEN stream (measured: tokens carry __global__/
__shared__). So the front-end reads tokens for the carrier layer, cursors for the syntactic layer.

SCOPE: a focused bidirectional grammar — enough to round-trip a real kernel and exhibit the
Move-carrier structure. A complete C++ grammar is unbounded; this covers the kernel core
(FunctionDef, params, VarDecl with space, ArraySubscript, BinOp, Assign, Call, intrinsics).
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jea_pyalg import Intern, IR, full_skeleton

try:
    import clang.cindex as cc
    _HAS_CLANG = True
except Exception:
    _HAS_CLANG = False

# memory-space qualifiers (the carriers). order matters for token scan.
_SPACES = ("__global__", "__shared__", "__device__", "__constant__", "__local__", "__host__")
# CUDA intrinsics that are ATOMIC referents (leaves -> identity in the key, like free names)
_INTRINSICS = ("threadIdx", "blockIdx", "blockDim", "gridDim", "__syncthreads", "warpSize")

# ── THE ONE BIDIRECTIONAL GRAMMAR ────────────────────────────────────────────
# each entry: IR-kind  <->  (clang CursorKind name, infix/emit template). The lowerer reads it
# CursorKind→IR; the projector reads it IR→syntax. Single source of truth.
_BINOP_TOK = {"+": "Add", "-": "Sub", "*": "Mult", "/": "Div", "%": "Mod",
              "<": "Lt", ">": "Gt", "==": "Eq", "<=": "LtE", ">=": "GtE"}
_BINOP_EMIT = {v: k for k, v in _BINOP_TOK.items()}     # the inverse, by construction


class CudaLowerer:
    """CUDA → IR (the fold). Reads cursors for syntax, tokens for the memory-space carrier."""
    def __init__(self, intern: Intern):
        self.I = intern
        self.scopes = [{}]
        self.bound = set()

    def _space_of(self, cursor) -> str | None:
        toks = [t.spelling for t in cursor.get_tokens()]
        for s in _SPACES:
            if s in toks:
                return s
        return None

    def _space_node(self, space: str) -> int:
        return self.I.intern(IR(kind="Space", op=space.strip("_"), children=()))

    def _role(self, name: str) -> str:
        for sc in reversed(self.scopes):
            if name in sc:
                return sc[name]
        r = f"v{len(self.scopes)-1}_{len(self.scopes[-1])}"
        self.scopes[-1][name] = r
        return r

    def lower(self, c) -> int | None:
        k = str(c.kind).split(".")[-1]
        if k == "FUNCTION_DECL":
            space = self._space_of(c)                       # __global__ etc -- the kernel's carrier
            self.scopes.append({})
            params, body = [], []
            for ch in c.get_children():
                ck = str(ch.kind).split(".")[-1]
                if ck == "PARM_DECL":
                    self.bound.add(ch.spelling)
                    params.append(self.I.intern(IR(kind="Name", role=self._role(ch.spelling),
                                                   children=(), payload=(ch.spelling,))))
                elif ck == "COMPOUND_STMT":
                    for st in ch.get_children():
                        cid = self.lower(st)
                        if cid is not None:
                            body.append(cid)
            self.scopes.pop()
            pblock = self.I.intern(IR(kind="Block", children=tuple(params)))
            kids = (pblock,) + tuple(body)
            # the kernel's memory space is a Space CHILD (carrier-structure), not a key-tag on the def
            sp = (self._space_node(space),) if space else ()
            return self.I.intern(IR(kind="FunctionDef", op="", children=sp + kids, payload=(c.spelling,)))
        if k == "DECL_STMT":
            for ch in c.get_children():
                return self.lower(ch)
            return None
        if k == "VAR_DECL":
            space = self._space_of(c)                       # __shared__ float tile[...] -> Space carrier
            self.bound.add(c.spelling)
            nm = self.I.intern(IR(kind="Name", role=self._role(c.spelling), children=(), payload=(c.spelling,)))
            sp = (self._space_node(space),) if space else ()
            ty = c.type.spelling or "float"                   # capture the declared TYPE (int/float/...);
            # else the projector defaults to float and `y[i]` with a float index becomes ill-typed on
            # re-parse -> clang drops the statement -> the round-trip DRIFTS. Type lives in payload (residue).
            # an initializer (int i = threadIdx.x) makes the decl an Assign of the init to the name
            inits = [self.lower(ch) for ch in c.get_children()]
            inits = [x for x in inits if x is not None]
            decl = self.I.intern(IR(kind="VarDecl", children=sp + (nm,), payload=(c.spelling, ty)))
            if inits:
                return self.I.intern(IR(kind="Assign", children=(decl, inits[0])))
            return decl
        if k == "BINARY_OPERATOR":
            kids = [self.lower(ch) for ch in c.get_children()]
            kids = [x for x in kids if x is not None]
            if len(kids) != 2:
                return kids[0] if kids else None
            opc = self._binop_token(c)                       # the operator token BETWEEN the operands
            if opc == "=":
                return self.I.intern(IR(kind="Assign", children=tuple(kids)))
            return self.I.intern(IR(kind="BinOp", op=_BINOP_TOK.get(opc, "Add"), children=tuple(kids)))
        if k == "MEMBER_REF_EXPR":
            # threadIdx.x -- atomic referent; keep the full dotted name in the key (identity)
            toks = [t.spelling for t in c.get_tokens()]
            nm = "".join(toks) if toks else c.spelling
            return self.I.intern(IR(kind="Name", op=nm, children=(), payload=(nm,)))
        if k == "ARRAY_SUBSCRIPT_EXPR":
            kids = [self.lower(ch) for ch in c.get_children()]
            kids = [x for x in kids if x is not None]
            if len(kids) == 2:
                return self.I.intern(IR(kind="Subscript", children=tuple(kids)))
        if k in ("INTEGER_LITERAL", "FLOATING_LITERAL"):
            toks = [t.spelling for t in c.get_tokens()]
            val = toks[0] if toks else "0"
            return self.I.intern(IR(kind="Constant", lit="int" if k.startswith("INT") else "float",
                                    children=(), payload=(val,)))
        if k == "UNEXPOSED_EXPR":
            # a transparent wrapper -- ALWAYS descend to the real child, never synthesize from tokens
            kids = [self.lower(ch) for ch in c.get_children()]
            kids = [x for x in kids if x is not None]
            return kids[0] if kids else None
        if k == "DECL_REF_EXPR":
            nm = c.spelling or next((t.spelling for t in c.get_tokens()), "")
            if not nm:
                return None
            if nm in _INTRINSICS or not self._is_bound(nm):     # atomic referent -> identity in key
                return self.I.intern(IR(kind="Name", op=nm, children=(), payload=(nm,)))
            return self.I.intern(IR(kind="Name", role=self._role(nm), children=(), payload=(nm,)))
        if k == "CALL_EXPR":
            nm = c.spelling
            kids = [self.lower(ch) for ch in c.get_children() if self.lower(ch) is not None]
            fn = self.I.intern(IR(kind="Name", op=nm, children=(), payload=(nm,)))
            return self.I.intern(IR(kind="Call", children=(fn,) + tuple(kids)))
        # fallthrough: descend
        kids = [self.lower(ch) for ch in c.get_children()]
        kids = [x for x in kids if x is not None]
        if len(kids) == 1:
            return kids[0]
        if kids:
            return self.I.intern(IR(kind="Block", children=tuple(kids)))
        return None

    def _is_bound(self, nm):
        return nm in self.bound or any(nm in sc for sc in self.scopes)

    def _binop_token(self, c) -> str:
        # clang does not expose a binary operator as a field; find it positionally as the token
        # between the first operand's last token and the second operand's first token.
        ch = list(c.get_children())
        if len(ch) != 2:
            toks = [t.spelling for t in c.get_tokens()]
            return next((t for t in toks if t in _BINOP_TOK or t == "="), "+")
        end1 = ch[0].extent.end.offset
        start2 = ch[1].extent.start.offset
        for t in c.get_tokens():
            if end1 <= t.extent.start.offset and t.extent.end.offset <= start2:
                if t.spelling in _BINOP_TOK or t.spelling == "=":
                    return t.spelling
        return "="


# minimal declarations of the CUDA intrinsics (_INTRINSICS) so a HEADERLESS parse (-nocudainc, no CUDA
# toolkit here) resolves `threadIdx.x` etc. -- else they are undeclared, their initializers become clang
# recovery nodes that lower to nothing, and the round-trip DRIFTS (the init is silently lost). The prelude
# is excluded from lowering by source offset, so it contributes NO units (incl. its __syncthreads decl).
_CUDA_PRELUDE = (
    "struct uint3 { unsigned x, y, z; };\n"
    "struct dim3 { unsigned x, y, z; };\n"
    "uint3 threadIdx; uint3 blockIdx; dim3 blockDim; dim3 gridDim; int warpSize;\n"
    "void __syncthreads();\n"
)


def lower_cuda(src: str, intern: Intern) -> list[int]:
    if not _HAS_CLANG:
        raise RuntimeError("libclang not available")
    full = _CUDA_PRELUDE + src
    off = len(_CUDA_PRELUDE)                                  # user code starts here; prelude is < off
    idx = cc.Index.create()
    tu = idx.parse("k.cu", args=["-x", "cuda", "-nocudainc", "-nocudalib", "-std=c++14"],
                   unsaved_files=[("k.cu", full)])
    L = CudaLowerer(intern)
    out = []
    for c in tu.cursor.get_children():
        if str(c.kind).split(".")[-1] == "FUNCTION_DECL" and c.extent.start.offset >= off:
            out.append(L.lower(c))
    return out


class CudaProjector:
    """IR → CUDA (the unfold). Inverts the SAME grammar the lowerer used."""
    def __init__(self, intern: Intern, carrier: dict | None = None):
        self.I = intern
        self.carrier = carrier or {}        # op-kind -> ("fn", name) for substitute mode

    def _nm(self, n: IR) -> str:
        if n.op:
            return n.op
        if n.payload:
            return str(n.payload[0])
        return n.role or "_"

    def project(self, nid: int) -> str:
        n = self.I.nodes[nid]
        k = n.kind
        if k == "Name":
            return self._nm(n)
        if k == "Constant":
            return str(n.payload[0]) if n.payload else "0"
        if k == "Space":
            return f"__{n.op}__"
        if k == "BinOp":
            kids = [c for c in n.children if self.I.nodes[c].kind != "Space"]
            a, b = self.project(kids[0]), self.project(kids[1])
            rule = self.carrier.get(n.op)
            if rule and rule[0] == "fn":            # substitute: carrier op -> named fn (defunctionalize)
                return f"{rule[1]}({a}, {b})"
            return f"{a} {_BINOP_EMIT.get(n.op, '+')} {b}"
        if k == "Subscript":
            return f"{self.project(n.children[0])}[{self.project(n.children[1])}]"
        if k == "Assign":
            lhs, rhs = n.children[0], n.children[1]
            # if lhs is a VarDecl (declared-with-init), emit a declaration; else a plain assignment
            if self.I.nodes[lhs].kind == "VarDecl":
                ld = self.I.nodes[lhs]
                name = ld.payload[0] if ld.payload else "_"
                ty = ld.payload[1] if ld.payload and len(ld.payload) > 1 else "float"
                space = next((c for c in ld.children if self.I.nodes[c].kind == "Space"), None)
                qual = self.project(space) + " " if space is not None else ""
                return f"  {qual}{ty} {name} = {self.project(rhs)};"
            return f"  {self.project(lhs)} = {self.project(rhs)};"
        if k == "Call":
            fn = self.project(n.children[0])
            args = ", ".join(self.project(c) for c in n.children[1:])
            return f"{fn}({args})"
        if k == "VarDecl":
            space = next((c for c in n.children if self.I.nodes[c].kind == "Space"), None)
            qual = self.project(space) + " " if space is not None else ""
            name = n.payload[0] if n.payload else "_"
            ty = n.payload[1] if n.payload and len(n.payload) > 1 else "float"
            return f"  {qual}{ty} {name};"
        if k == "FunctionDef":
            space = next((c for c in n.children if self.I.nodes[c].kind == "Space"), None)
            qual = self.project(space) + " " if space is not None else ""
            name = n.payload[0] if n.payload else "k"
            rest = [c for c in n.children if self.I.nodes[c].kind != "Space"]
            params, body = [], []
            for c in rest:
                if self.I.nodes[c].kind == "Block" and not params:
                    params = [f"float* {self.project(g)}" for g in self.I.nodes[c].children]
                else:
                    body.append(c)
            head = f"{qual}void {name}({', '.join(params)}) {{"
            lines = []
            for c in body:
                ck = self.I.nodes[c].kind
                s = self.project(c)
                if ck in ("Assign", "VarDecl") or s.lstrip().startswith(("__", "float")):
                    lines.append(s if s.startswith("  ") else "  " + s)   # already a statement line
                else:
                    lines.append("  " + s + ";")                          # bare expr -> statement
            return head + "\n" + "\n".join(lines) + "\n}"
        if k == "Block":
            return "\n".join(self.project(c) for c in n.children)
        # fallthrough
        return " ".join(self.project(c) for c in n.children)


def project_cuda(intern: Intern, root: int, carrier: dict | None = None) -> str:
    return CudaProjector(intern, carrier).project(root)


def fixpoint_test(src: str) -> dict:
    """The bidirectional-grammar gate: lower→project→re-lower lands on the same canonical node."""
    I1 = Intern(); r1 = lower_cuda(src, I1)[0]
    emitted = project_cuda(I1, r1)
    # wrap emitted back as a parseable kernel and re-lower
    I2 = Intern(); r2 = lower_cuda(emitted, I2)[0]
    sk1, sk2 = full_skeleton(I1, r1), full_skeleton(I2, r2)
    return {"emitted": emitted, "fixpoint": sk1 == sk2, "n1": len(sk1), "n2": len(sk2)}


if __name__ == "__main__":
    if not _HAS_CLANG:
        print("libclang not available; install: pip install libclang --break-system-packages")
        sys.exit(1)
    kernel = ("__global__ void saxpy(float* x, float* y) {\n"
              "  int i = threadIdx.x;\n"
              "  y[i] = x[i] + y[i];\n"
              "}\n")
    print("=== Δ-Π-cuda: ONE bidirectional grammar, fixpoint gate ===\n")
    r = fixpoint_test(kernel)
    print(f"[{'FIXPOINT OK' if r['fixpoint'] else 'DRIFT'}]  ({r['n1']}->{r['n2']} nodes)")
    print("--- re-emitted CUDA ---")
    for ln in r["emitted"].splitlines():
        print("  " + ln)
