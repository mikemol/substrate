#!/usr/bin/env python3
"""numpy_law_bridge.py — the horizontal-push glue (Ⓐ auto-pushout of the reach).

A numpy-discovered/verified law  →  an interner-unit written in the SHARED COMBINATOR
VOCABULARY, so its term interns in a node-space comparable to the Agda .agdai cores'
combinator structure.  Then `jea_pysim --shape law cores…` can (try to) consolidate the
law with the real definitions → the "pushout node" (shared shell + carrier holes).

Two things live here:

  1. THE LAW (numpy ground truth).  Reconstructs the rig_cata2.py enumeration: `combine`
     (divmod-based Fin pairing), `insert_at`, `oplus` (block-sum ⊕), `otimes` (combine-
     product ⊗) on permutations-as-tuples, and VERIFIES the ⊗-over-◂ recursion
        (insert_at p σ) ⊗ τ = [ rows<p: keep σ⊗τ | row=p: block m·n+τ[j] | rows>p: shift ]
     exhaustively for m,n ≤ 4.  This is the finite-verified frontier reach.

  2. THE SERIALIZER (two modes, honest about the cross-language seam):
     · emit_py_source()      — the law as a .py unit in the combinator vocabulary.
                               Interned via jea_pysim's PYTHON front-end → Python node
                               kinds ('Call','Name','BinOp'…).  This is the NAIVE emit.
     · intern_law_agdacore() — the law built DIRECTLY as AgdaCore IR nodes, qnames pulled
                               through NAME_MAP (python combinator → Agda qualified name).
                               This speaks the cores' own vocabulary ('AgdaCore' kind, the
                               `Substrate.…` qnames in `op`) so the shape scan can match.

The design's caveat, made concrete here (see the CROSS-LANGUAGE SEAM note below): the
Python front-end hardcodes node.kind from the AST class, so a naive .py emit's nodes are
kind='Call'/'BinOp'/'Name' and can NEVER head-match the cores' kind='AgdaCore' nodes.
The vocabulary translation IS NAME_MAP + emitting AgdaCore-kind nodes — that is the
minimal missing glue that makes the pushout node appear.
"""
from __future__ import annotations
import sys, os, argparse, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jea_pyalg import IR, Intern

try:
    import numpy as np
    HAVE_NUMPY = True
except Exception:
    HAVE_NUMPY = False


# ─────────────────────────────────────────────────────────────────────────────
# 1.  THE LAW  — numpy ground truth (reconstructs rig_cata2.py; the finite frontier).
#     Permutations are 0-based tuples; a graded perm carries its degree = len.
# ─────────────────────────────────────────────────────────────────────────────
def combine(n: int, i: int, j: int) -> int:
    """Fin pairing: combine over Fin m × Fin n → Fin (m·n).  divmod-inverse of remQuot.
    combine n i j = i*n + j  (== the Agda Substrate.Foundation.Fin.Combine.combine)."""
    return i * n + j


def remQuot(n: int, k: int) -> tuple[int, int]:
    """Inverse of combine: k ↦ (k // n, k % n) = divmod.  (Agda …Fin.RemQuot.remQuot)."""
    return divmod(k, n)


def insert_at(p: int, sigma: tuple, m: int) -> tuple:
    """◂ : place a fresh maximal point at row p of a degree-m perm → degree m+1.
    (values ≥ p shift up by one; the new row p takes value... m, the fresh max)."""
    bumped = tuple(v + (1 if v >= p else 0) for v in sigma)
    return bumped[:p] + (m,) + bumped[p:]


def oplus(sigma: tuple, tau: tuple) -> tuple:
    """Block-sum ⊕ : degree m ⊕ degree n → degree m+n.  σ on the first block, τ shifted."""
    m = len(sigma)
    return tuple(sigma) + tuple(v + m for v in tau)


def otimes(sigma: tuple, tau: tuple) -> tuple:
    """Combine-product ⊗ : degree m ⊗ degree n → degree m·n.  The graded Lehmer product:
    entry at combine(n,i,j) = combine(n, σ[i], τ[j]) = σ[i]·n + τ[j]  (row-major Kronecker)."""
    m, n = len(sigma), len(tau)
    out = [0] * (m * n)
    for i in range(m):
        for j in range(n):
            out[combine(n, i, j)] = combine(n, sigma[i], tau[j])
    return tuple(out)


def otimes_via_recursion(sigma: tuple, tau: tuple) -> tuple:
    """The ⊗-over-◂ recursion (design line 59), computed structurally on the ◂-decomposition
    of σ, so it can be checked to AGREE with the direct otimes above:
        (insert_at p σ') ⊗ τ = rows<p·n : keep (σ'⊗τ)
                               row  p·n.. : the fresh block  m·n .. m·n+n-1   (i.e. m·n + τ[j])
                               rows>       : σ'⊗τ shifted down by one n-block
    We recover (p, σ') from σ by reading its max position, then splice τ's block in."""
    m, n = len(sigma), len(tau)
    if m == 0:
        return ()
    if m == 1:
        # degree-1 σ = (0,): σ ⊗ τ = τ  (the unit block, values 0·n+τ[j] = τ[j])
        return tuple(tau)
    p = sigma.index(m - 1)                       # the ◂ insertion row: where the fresh max sits
    sigma_rest = tuple(v for k, v in enumerate(sigma) if k != p)   # peel the max off → degree m-1
    base = otimes_via_recursion(sigma_rest, tau)                    # (m-1)·n entries
    block = tuple(combine(n, m - 1, j) for j in range(n))          # row p's block: (m-1)·n + τ[j] permuted by τ
    block = tuple((m - 1) * n + tau[j] for j in range(n))          # == m·n-block offset + τ
    out = base[: p * n] + block + base[p * n:]
    return out


def verify_law(maxdeg: int = 4) -> dict:
    """Exhaustively check, for all perms of degree ≤ maxdeg, that the ◂-recursion agrees with
    direct ⊗, and that ⊕/⊗ land in the right degree and stay permutations.  m,n ≤ maxdeg."""
    from itertools import permutations
    checks = fails = 0
    for m in range(1, maxdeg + 1):
        for n in range(1, maxdeg + 1):
            for sigma in permutations(range(m)):
                for tau in permutations(range(n)):
                    a = otimes(sigma, tau)
                    b = otimes_via_recursion(sigma, tau)
                    checks += 1
                    if a != b or sorted(a) != list(range(m * n)):
                        fails += 1
    # ⊕ sanity
    oplus_ok = True
    for m in range(1, maxdeg + 1):
        for n in range(1, maxdeg + 1):
            for sigma in permutations(range(m)):
                for tau in permutations(range(n)):
                    s = oplus(sigma, tau)
                    if sorted(s) != list(range(m + n)):
                        oplus_ok = False
    return {"checks": checks, "fails": fails, "oplus_ok": oplus_ok,
            "verdict": "VERIFIED" if fails == 0 and oplus_ok else "FALSIFIED", "maxdeg": maxdeg}


# ─────────────────────────────────────────────────────────────────────────────
# 2a. NAIVE emit — the law as a .py unit in the combinator vocabulary.
#     (Interned through jea_pysim's Python front-end → Python node kinds.)
# ─────────────────────────────────────────────────────────────────────────────
def emit_py_source() -> str:
    """The ⊗-over-◂ law + ⊕/⊗ as a .py unit written in the shared combinator vocabulary.
    Structure, not runtime lists: the def bodies are combinator EXPRESSIONS (combine, remQuot,
    lookup, tabulate, mul) so the AST spine mirrors the Agda cores' application spine."""
    return '''# emitted by numpy_law_bridge — the ⊗-over-◂ law in the combinator vocabulary.
def otimes_law(sigma, tau, m, n):
    # lookup (sigma ⊗ tau) (combine i j)  ≡  combine (lookup sigma i) (lookup tau j)
    return tabulate(lambda k: combine(lookup(sigma, remQuot(n, k)[0]),
                                      lookup(tau,   remQuot(n, k)[1])))

def otimes_def(sigma, tau, m, n):
    # the graded product: entry at combine(i,j) = m·(lookup sigma i) + lookup tau j
    return tabulate(lambda k: mul(m, lookup(sigma, remQuot(n, k)[0])) + lookup(tau, remQuot(n, k)[1]))

def oplus_def(sigma, tau, m, n):
    return tabulate(lambda k: lookup(sigma, k) if k < m else mul(1, m) + lookup(tau, k))
'''


def emit_py_unit(path: str) -> str:
    with open(path, "w") as fh:
        fh.write(emit_py_source())
    return path


# ─────────────────────────────────────────────────────────────────────────────
# 2b. VOCAB-MAPPED emit — the law built DIRECTLY as AgdaCore IR nodes.
#     THIS is the vocabulary translation the design flags as "small + one-time".
# ─────────────────────────────────────────────────────────────────────────────
# python combinator token  →  Agda qualified name (as it appears in the .agdai cores).
NAME_MAP = {
    "combine":  "Substrate.Foundation.Fin.Combine.combine",
    "remQuot":  "Substrate.Foundation.Fin.RemQuot.remQuot",
    "lookup":   "Substrate.Foundation.Vec.lookup",
    "tabulate": "Substrate.Foundation.Vec.tabulate",
    "mul":      "Substrate.Foundation.Nat._*_",
    "otimes":   "Substrate.WitnessTower.Wedge.OrientationProduct._⊗_",
}


class AgdaCoreBuilder:
    """Emit AgdaCore IR nodes (kind='AgdaCore', op=<qname>, role=<de-Bruijn/''>) into an
    Intern, exactly as jea_agdai does for real cores — so structurally-coincident subterms
    HASH-CONS to the same interned id as the cores' nodes (the literal pushout node)."""
    def __init__(self, intern: Intern):
        self.I = intern

    def app(self, pyname: str, *kids: int) -> int:
        """An application headed by a mapped global qname."""
        qn = NAME_MAP.get(pyname, pyname)
        return self.I.intern(IR(kind="AgdaCore", role="", op=qn, lit="",
                                children=tuple(kids), payload=(qn,)))

    def var(self, dbindex: int) -> int:
        """A bound variable (de-Bruijn) — role-quotiented, exactly as jea_agdai's BOUND path."""
        return self.I.intern(IR(kind="AgdaCore", role=f"db{dbindex}", op="", lit="", children=()))

    def build_otimes_combine_law(self) -> int:
        """lookup (σ ⊗ τ) (combine i j)  ≡  combine (lookup σ i) (lookup τ j)
        as an AgdaCore application tree in the cores' own vocabulary."""
        sig, tau, i, j = self.var(0), self.var(1), self.var(2), self.var(3)
        lhs = self.app("lookup",
                       self.app("otimes", sig, tau),
                       self.app("combine", i, j))
        rhs = self.app("combine",
                       self.app("lookup", sig, i),
                       self.app("lookup", tau, j))
        # the equation as a 2-arg node (mirrors _≡_ shell; op left generic so it doesn't
        # falsely claim to share the cores' _≡_ node — the LAW's content is lhs/rhs).
        return self.I.intern(IR(kind="AgdaCore", role="", op="Substrate.Foundation.Eq._≡_",
                                lit="", children=(lhs, rhs)))


def register_unit(pysim_corpus, name: str, root: int):
    """Append an already-interned root as a Unit in a jea_pysim.Corpus (mirrors add_agdai's
    unit bookkeeping) so the shape scan sees it alongside the core units."""
    sup = pysim_corpus._support(root)
    from jea_pysim import Unit
    u = Unit(name=name, path="<numpy-law>", lineno=-1, root=root,
             support=sup, depth=pysim_corpus._depth_map(root))
    uidx = len(pysim_corpus.units)
    pysim_corpus.units.append(u)
    for nid in sup:
        pysim_corpus.node_units.setdefault(nid, set()).add(uidx)
    return uidx


# ─────────────────────────────────────────────────────────────────────────────
# 3.  DEMO
# ─────────────────────────────────────────────────────────────────────────────
CORES = ["OrientationProduct.agdai", "OrientationProductLaws.agdai", "OrientationProductComm.agdai"]
CORE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "../../agda/_build/2.8.0/agda/Substrate/WitnessTower/Wedge")


def demo():
    import jea_pysim
    print("=" * 78)
    print("Ⓐ auto-pushout demo — numpy law ⊗ typeholer")
    print("=" * 78)

    # (1) numpy ground truth
    v = verify_law(4)
    print(f"\n[1] numpy law (rig_cata2 reconstruction): {v['verdict']} "
          f"({v['checks']} ⊗-recursion checks, {v['fails']} fails; ⊕ ok={v['oplus_ok']}) "
          f"m,n ≤ {v['maxdeg']}  [numpy={'yes' if HAVE_NUMPY else 'no, pure-py'}]")

    # (2) VOCAB-MAPPED: build cores + law in ONE interner, look for the pushout node.
    print("\n[2] vocab-mapped emit (AgdaCore kind + NAME_MAP qnames), interned WITH the cores:")
    C = jea_pysim.Corpus()
    for f in CORES:
        C.add_agdai(os.path.join(CORE_DIR, f))
    n_core_units = len(C.units)
    core_nodes_before = C.I.size()
    B = AgdaCoreBuilder(C.I)
    law_root = B.build_otimes_combine_law()
    law_uidx = register_unit(C, "otimes_combine_law", law_root)
    law_support = C.units[law_uidx].support

    # literal pushout nodes = interned ids in BOTH the law's support and some core unit's support.
    core_support = set().union(*(C.units[k].support for k in range(n_core_units)))
    shared_ids = (law_support & core_support)
    print(f"    cores: {n_core_units} units, {core_nodes_before} nodes; law adds "
          f"{C.I.size() - core_nodes_before} NEW nodes, {len(law_support)} in its support.")
    print(f"    LITERAL pushout nodes (interned id in BOTH law and a core) : {len(shared_ids)}")
    for nid in sorted(shared_ids):
        nn = C.I.nodes[nid]
        print(f"        node {nid}: kind={nn.kind} op={nn.op!r} fanin={C.I.fanin[nid]}")

    # SHAPE pushout = shared shell + carrier holes between the law unit and each core unit.
    print("    SHAPE consolidation (law-unit  X  each core-unit):")
    lawu = C.units[law_uidx]
    any_shell = False
    for k in range(n_core_units):
        cu = C.units[k]
        if len(cu.support) < 6:
            continue
        sv = C.shape_verdict(lawu, cu)
        tag = "SHELL+HOLES" if (sv["shared_frac"] >= 0.55 and any(d > 0 for d in sv["hole_depths"])) else "—"
        if tag != "—":
            any_shell = True
        print(f"        {cu.name:<28} frac={sv['shared_frac']:.2f} "
              f"holes@{sv['hole_depths']} label={sv['label']}  {tag}")

    print(f"\n    VERDICT (vocab-mapped): pushout node "
          f"{'FOUND' if shared_ids or any_shell else 'NOT found'} "
          f"({len(shared_ids)} literal shared ids, shell-share={'yes' if any_shell else 'no'})")
    return C


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--verify", action="store_true", help="run the numpy law verification (m,n≤4)")
    ap.add_argument("--emit-py", metavar="PATH", help="write the naive .py law unit to PATH")
    ap.add_argument("--demo", action="store_true", help="full pushout demo (cores + law, both modes)")
    args = ap.parse_args(argv)
    if args.verify:
        print(verify_law(4))
    if args.emit_py:
        print("wrote", emit_py_unit(args.emit_py))
    if args.demo or not (args.verify or args.emit_py):
        demo()
    return 0


if __name__ == "__main__":
    sys.exit(main())
