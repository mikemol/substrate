#!/usr/bin/env python3
"""jea_oneforest.py — Σ-FOREST (Δ-Π-oneforest): the verification gate as a CrossMix readout.

Intern source + core + kernel into ONE forest, then the project's REASON falls out as a readout, not
a new mechanism (the recursive law: tiling and the cross-term are two FOLDS of one forest):
  * source↔core↔kernel CROSS-TERM = `CrossMix.cross_term` across the three arms' units = the
    VERIFICATION GATE (`gate`). Where a kernel/source unit and the proof-core unit are ORTHOGONAL
    (degree 0, same canonical node) the kernel REALIZES the proof; where they diverge, the graded
    obstruction + residue say BY HOW MUCH and WHERE -- exactly the "does this artifact faithfully
    realize the proven algorithm" question, answered structurally, not asserted. This is FIDELITY
    (precision): is each matched pair faithful.
  * the COMPLETENESS companion closes the recall side the bare gate can't see. The correspondence is
    DISCOVERED, never declared -- nothing is *supposed* to mirror anything; two units correspond because
    they share canonical structure under the symmetry the interner already quotients by (α/role, the
    gauge). `correspondence` is the SYMMETRIC (mutual-best/reciprocal) matching -- a↔b iff each is the
    other's most-shared partner; ORPHANS = the units the symmetry leaves unpaired; `symmetric` = a total
    structural bijection of the unit-sets up to the gauge. EXACT = cross-term degree 0. (`coverage` is the
    weaker per-side floored existence view; its optional `manifest` is NOT a table of intentions but a
    regression PIN -- assert a once-discovered structural symmetry still holds.) Together: complete ∧ faithful.
  * tiling / metalanguage = the cohomology fold on a single arm (jea_pysim) -- a separate readout of
    the same forest (not built here; this module is the cross-arm gate).

ARCHITECTURE (the language-agnostic core, the part that runs ANYWHERE):
  a forest = one `Intern` + a set of named UNITS `(arm, qname, root)` from ANY front-ends that wrote
  into that Intern. The front-ends are environment-bound (libclang here, the Agda shim in the
  integrating session's env); the cross-term READOUT is NOT -- it is pure `CrossMix` over interned
  ids. So this module is verifiable on whichever arms' toolchains are present. In THIS repo that is Python
  (jea_pyalg) AND the AGDA-CORE arm via its REAL landed interface (`jea_agdai.core_intern_agdai`, Φ4):
  both RUN here (ghc+Agda present), no faked output. The CUDA arm (jea_cuda/libclang) is env-bound and
  ABSENT here; it composes by construction where that front-end exists -- NO rework, NO faked Agda output.

WHY no faked Agda arm: inventing shim output would be the invent-attributions error. The Agda arm is
ATTACHED by interface (add_arm consumes the documented {units:[(qname,root)]} shape that
core_intern_agdai returns) and EXERCISED by whoever has the toolchain. Here we prove the gate on the
two arms we can run, and the third composes by construction (same Intern, same unit shape)."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "metalanguage"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jea_pyalg import Intern, CrossMix, lower_source, IR


class OneForest:
    """One Intern, units from multiple arms, the cross-term readout over them."""
    def __init__(self):
        self.I = Intern()
        self.arms: dict[str, list[tuple[str, int]]] = {}    # arm -> [(qname, interned_root), ...]
        self.cross = CrossMix(self.I)
        self._shape_memo: dict[int, tuple] = {}

    # ── front-end arms (each writes into the ONE shared Intern) ──────────────
    def add_python(self, arm: str, src: str, qname: str):
        root = lower_source(src, self.I)[0]
        self.arms.setdefault(arm, []).append((qname, root))
        return root

    def add_cuda(self, arm: str, src: str, qname: str):
        import jea_cuda
        # jea_cuda.lower_cuda interns into ITS own call; rebind it to ours by passing our Intern
        root = jea_cuda.lower_cuda(src, self.I)[0]
        self.arms.setdefault(arm, []).append((qname, root))
        return root

    def add_agda_core(self, arm: str, agdai_path: str, shim_bin: str | None = None):
        """The AGDA-CORE arm via the LANDED shim (jea_agdai.core_intern_agdai). Requires the compiled
        agdai_shim (ghc -package Agda) -- present in the integrating session's env, not necessarily here.
        Consumes the documented {units:[(qname,root)]} shape; drops in unchanged."""
        import jea_agdai
        res = jea_agdai.core_intern_agdai(agdai_path, self.I, shim_bin=shim_bin)
        self.arms.setdefault(arm, []).extend(res["units"])
        return res["units"]

    def add_units(self, arm: str, units: list[tuple[str, int]]):
        """Attach pre-interned units (e.g. a test double for an arm whose toolchain is absent). The
        roots MUST be ids in THIS forest's Intern."""
        self.arms.setdefault(arm, []).extend(units)

    def _vocab(self, arm: str) -> set:
        """The set of node-KINDS an arm's units intern to — its canonical vocabulary. Two arms can only
        share interned ids (hence have a non-vacuous correspondence) where their vocabularies OVERLAP."""
        ks = set()
        for _, r in self.arms.get(arm, []):
            stack, seen = [r], set()
            while stack:
                j = stack.pop()
                if j in seen:
                    continue
                seen.add(j); n = self.I.nodes[j]; ks.add(n.kind); stack.extend(n.children)
        return ks

    # ── the readout: the cross-arm verification gate ─────────────────────────
    def gate(self, arm_a: str, arm_b: str) -> list[dict]:
        """The VERIFICATION GATE: for each (unit_a, unit_b) pairing across two arms (matched by qname
        when names coincide, else best by shared support), the cross-term. degree 0 = arm_b REALIZES
        arm_a (orthogonal, same canonical structure); degree>0 = graded obstruction (residue = what
        each carries the other doesn't); the shared_fraction = how coherent."""
        ua = {q: r for q, r in self.arms.get(arm_a, [])}
        ub = {q: r for q, r in self.arms.get(arm_b, [])}
        out = []
        for q, ra in ua.items():
            # match by qname if present in b, else take b's best-sharing unit
            if q in ub:
                rb, how = ub[q], "by-name"
            else:
                cand = [(self.cross.shared_fraction(ra, r), r) for r in ub.values()]
                if not cand:
                    continue
                frac, rb = max(cand); how = "by-support"
            ct = self.cross.cross_term(ra, rb)
            out.append({"unit": q, "match": how,
                        "realizes": ct.degree == 0,
                        "degree": ct.degree,
                        "shared_fraction": round(self.cross.shared_fraction(ra, rb), 3),
                        "a_residue": ct.a_residue, "b_residue": ct.b_residue})
        return out

    # ── the COMPLETENESS readout: does every unit have a mirror at all? ───────
    def coverage(self, arm_a: str, arm_b: str, floor: float = 0.5,
                 manifest: dict[str, str] | None = None) -> dict:
        """The completeness/recall companion to `gate`. `gate` answers PRECISION ("is each *matched*
        pair faithful?"); `coverage` answers RECALL ("does every unit have a mirror at all?"). The bare
        gate cannot see recall — it iterates arm_a only and, for an arm_a unit with no real partner,
        still takes arm_b's *best* match, so a MISSING mirror is silently reported as a (low-coherence)
        match and an arm_b unit absent from arm_a is never visited.

        coverage walks BOTH sides: for each unit it finds its best partner across the other arm by
        `shared_fraction`; a unit whose best < `floor` is an ORPHAN (no structural mirror). It returns
        the orphan lists for both arms + per-side coverage fractions. `complete` is True iff neither
        side has an orphan. Coverage is the EXISTENCE question (≥ floor), kept distinct from the gate's
        FIDELITY question (degree 0) — together: complete ∧ faithful.

        For the SYMMETRIC structural correspondence (a↔b mutual-best, the gauge-free matching), use
        `correspondence` — that, not this per-side view, is the discovered mirroring. The optional
        `manifest` here is NOT a table of intentions (nothing is *supposed* to mirror anything); it is a
        regression PIN — assert a once-discovered structural symmetry {a_qname: b_qname} still holds
        (present on both sides AND faithful, degree 0), so a later edit can't silently break it."""
        au = self.arms.get(arm_a, [])
        bu = self.arms.get(arm_b, [])

        def best(r, others):
            cand = [(self.cross.shared_fraction(r, ro), qo) for qo, ro in others]
            return max(cand) if cand else (0.0, None)

        a_orphans, b_orphans, a_ok, b_ok = [], [], 0, 0
        for q, r in au:
            frac, partner = best(r, bu)
            if frac >= floor:
                a_ok += 1
            else:
                a_orphans.append({"unit": q, "best": partner, "shared_fraction": round(frac, 3)})
        for q, r in bu:
            frac, partner = best(r, au)
            if frac >= floor:
                b_ok += 1
            else:
                b_orphans.append({"unit": q, "best": partner, "shared_fraction": round(frac, 3)})

        shared_vocab = sorted(self._vocab(arm_a) & self._vocab(arm_b))
        result = {
            "arm_a": arm_a, "arm_b": arm_b, "floor": floor,
            "n_a": len(au), "n_b": len(bu),
            "coverage_a": round(a_ok / len(au), 3) if au else 1.0,
            "coverage_b": round(b_ok / len(bu), 3) if bu else 1.0,
            "a_orphans": a_orphans, "b_orphans": b_orphans,
            "shared_vocab": shared_vocab, "comparable": bool(shared_vocab),
        }
        if manifest is not None:
            ad, bd, misses = dict(au), dict(bu), []
            for qa, qb in manifest.items():
                if qa not in ad:
                    misses.append({"expected": f"{qa}→{qb}", "reason": f"{arm_a}:{qa} absent"})
                elif qb not in bd:
                    misses.append({"expected": f"{qa}→{qb}", "reason": f"{arm_b}:{qb} absent"})
                else:
                    ct = self.cross.cross_term(ad[qa], bd[qb])
                    if ct.degree != 0:
                        misses.append({"expected": f"{qa}→{qb}",
                                       "reason": f"present but unfaithful (degree {ct.degree})",
                                       "shared_fraction": round(self.cross.shared_fraction(ad[qa], bd[qb]), 3)})
            result["manifest_misses"] = misses
            result["manifest_complete"] = not misses

        result["complete"] = (not a_orphans and not b_orphans
                              and (manifest is None or result["manifest_complete"]))
        return result

    # ── the SYMMETRIC structural correspondence: discovered, not declared ─────
    def correspondence(self, arm_a: str, arm_b: str, floor: float = 0.5) -> dict:
        """The structural correspondence between two arms — DISCOVERED by the shared forest, never
        declared. Nothing is *supposed* to mirror anything: two units correspond because they share
        canonical structure under the symmetry the interner already quotients by (α/role-equivalence,
        the gauge). The correspondence is therefore the SYMMETRIC (mutual-best) matching — a ↔ b iff
        each is the other's most-shared partner (reciprocity = the symmetry; it removes `coverage`'s
        asymmetry, where a's best-b need not have a as its best). EXACT correspondence = cross-term
        degree 0 (same canonical structure up to the gauge); graded below. Orphans = the units the
        symmetry leaves unpaired. `symmetric` = a TOTAL mutual correspondence (a structural bijection
        of the unit-sets up to the gauge) — completeness as symmetry, with no manifest of intentions."""
        au, bu = self.arms.get(arm_a, []), self.arms.get(arm_b, [])

        def argbest(r, others):  # (best shared_fraction, index) of r's most-shared partner in others
            cand = [(self.cross.shared_fraction(r, ro), j) for j, (_, ro) in enumerate(others)]
            return max(cand) if cand else (0.0, None)

        a_best = [argbest(r, bu) for _, r in au]
        b_best = [argbest(r, au) for _, r in bu]
        pairs, a_matched, b_matched = [], set(), set()
        for i, (qa, ra) in enumerate(au):
            fa, j = a_best[i]
            if j is None or fa < floor:
                continue
            fb, i2 = b_best[j]
            if i2 == i:                      # reciprocal mutual-best ⇒ the symmetric correspondent
                ct = self.cross.cross_term(ra, bu[j][1])
                pairs.append({"a": qa, "b": bu[j][0], "shared_fraction": round(fa, 3),
                              "degree": ct.degree, "exact": ct.degree == 0})
                a_matched.add(i); b_matched.add(j)
        a_orphans = [qa for i, (qa, _) in enumerate(au) if i not in a_matched]
        b_orphans = [qb for j, (qb, _) in enumerate(bu) if j not in b_matched]
        # COMPARABILITY is QUOTIENT-RELATIVE. This `comparable` is at the FINEST (label-full) rung: two
        # arms share interned ids only where their `kind` vocabularies overlap, so Python AST vs Agda
        # 'AgdaCore' is comparable=False HERE. That does NOT mean "nothing corresponds" — it means the
        # label rung is the wrong one for this pair. Quotient further (drop the labels) and `shared_structure`
        # finds the generic concepts that DO correspond (the leaf, the generic pair, …). The label rung is
        # for within-language operator identity; cross-language structure lives at the coarse shape rung;
        # cross-language *semantic* unit-identity is the finer frontier (a behaviour-discovered alignment,
        # generalizing jea_seam_provenance). `comparable` flags the rung, it is not a verdict of non-mirroring.
        va, vb = self._vocab(arm_a), self._vocab(arm_b)
        shared_vocab = sorted(va & vb)
        return {"arm_a": arm_a, "arm_b": arm_b, "floor": floor,
                "n_a": len(au), "n_b": len(bu), "pairs": pairs,
                "a_orphans": a_orphans, "b_orphans": b_orphans,
                "n_pairs": len(pairs), "exact_pairs": sum(p["exact"] for p in pairs),
                "symmetric": not a_orphans and not b_orphans,
                "shared_vocab": shared_vocab, "comparable": bool(shared_vocab)}

    # ── the COARSE rung: label-free structural shape (where generic concepts live) ──
    def shape(self, i: int) -> tuple:
        """The LABEL-FREE structural shape of a subtree: its arity + the (unordered) shapes of its
        children, recursively. Quotients away kind/role/op/lit/value AND child order — the bare recursion
        structure, language-AGNOSTIC. This is the COARSE rung of the quotient ladder, where GENERIC
        structural concepts live and correspond ACROSS languages even when the label vocabularies are
        disjoint: (0,()) = a leaf/atom; (2,((0,()),(0,()))) = the generic PAIR — a binary combinator of two
        atoms, which a Python tuple, an Agda Σ/binary-constructor, a Cayley-Dickson doubling, and a BinOp
        ALL are at once. `full_skeleton` (jea_pyalg) is the label-FULL dual — the finest rung (keeps the
        operator, so it distinguishes within a language but goes disjoint across)."""
        memo = self._shape_memo
        if i in memo:
            return memo[i]
        kids = self.I.nodes[i].children
        s = (len(kids), tuple(sorted(self.shape(c) for c in kids)))
        memo[i] = s
        return s

    def _shapes(self, arm: str) -> set:
        out, seen = set(), set()
        for _, r in self.arms.get(arm, []):
            stack = [r]
            while stack:
                j = stack.pop()
                if j in seen:
                    continue
                seen.add(j); out.add(self.shape(j)); stack.extend(self.I.nodes[j].children)
        return out

    def shared_structure(self, arm_a: str, arm_b: str) -> dict:
        """Cross-language structural correspondence at the COARSE (label-free shape) quotient — the rung
        where structure corresponds even when the label vocabularies are disjoint (so `correspondence`'s
        label-level `comparable=False` is NOT 'nothing corresponds'; quotient further). Returns the shared
        structural vocabulary, its coverage of each arm, and named landmarks (leaf, generic pair). The
        generic pair coming up across Python and Agda is the proof the coarse rung is non-vacuous."""
        sa, sb = self._shapes(arm_a), self._shapes(arm_b)
        shared = sa & sb
        LEAF = (0, ()); PAIR = (2, (LEAF, LEAF))
        return {"arm_a": arm_a, "arm_b": arm_b,
                "n_shapes_a": len(sa), "n_shapes_b": len(sb), "n_shared": len(shared),
                "shared_fraction_a": round(len(shared) / len(sa), 3) if sa else 1.0,
                "shared_fraction_b": round(len(shared) / len(sb), 3) if sb else 1.0,
                "leaf_shared": LEAF in shared, "generic_pair_shared": PAIR in shared,
                "shared_shapes": sorted(shared, key=lambda s: len(str(s)))[:12]}

    # ── apply CrossMul AGAIN: quotient to shape, then the cross-term re-applies cross-language ──
    def quotient_to_shape(self) -> "OneForest":
        """Re-intern the whole forest by LABEL-FREE shape and return a NEW OneForest over it, then the
        SAME readouts (gate/correspondence/coverage = CrossMul) re-apply AT THE SHAPE RUNG. This is the
        recursion the project runs everywhere (homology→cohomology, level-1→level-2): CrossMul at level 1
        is over labels (within-language, cross-language ≡ 0 — disjoint vocab); quotient away the labels so
        a generic pair (Python tuple, Agda Σ/binary-ctor, Cayley-Dickson doubling, BinOp) is ONE shared
        node, then CrossMul at level 2 is over shapes — now NON-vacuous across languages, the shared
        shape-support is the orthogonal (corresponding) part and the shape residue is the graded
        obstruction. Proper cross-language correspondences fall out of the same machine, one rung up.

        The shape node interns kind=arity, no op/lit/role, children = the (sorted, unordered) shape-ids of
        the children — so structurally-identical subtrees across arms hash-cons to the SAME id."""
        G = OneForest()
        memo: dict[int, int] = {}

        def reintern(i: int) -> int:
            if i in memo:
                return memo[i]
            kids = self.I.nodes[i].children
            sid = G.I.intern(IR(kind=str(len(kids)),
                                children=tuple(sorted(reintern(c) for c in kids))))
            memo[i] = sid
            return sid

        for arm, units in self.arms.items():
            G.arms[arm] = [(q, reintern(r)) for q, r in units]
        return G

    # ── the TRUNCATABLE graded correspondence: S(g), never a scalar ──────────
    def _size(self, sid: int) -> int:
        """Number of nodes in an interned subtree (its shape SIZE) — the grade axis for the profile."""
        return 1 + sum(self._size(c) for c in self.I.nodes[sid].children)

    def profile(self, root_a: int, root_b: int, gmax: int = 10) -> list:
        """The TRUNCATABLE graded correspondence S(g) between two (shape-forest) roots — NOT a scalar.
        Grade g = shape SIZE: at g the shared structure is restricted to sub-shapes of size <= g. Small g
        = the universal vocabulary (a leaf, the generic pair) that ~everything shares; large g = the
        distinctive structure. Read it at any g (truncate); the SHAPE of the curve classifies and the
        CLIFF — the g where sharing falls to the universal floor — localizes the correspondence DEPTH.
        A flat-high curve = real correspondence (shares distinctive structure too); an early cliff =
        'shares only the universals' (the trim~valStr non-correspondence collapsing a scalar hid as 0.25).
        This is jea_pysim's S(g) (truncation, not collapse) carried one forgetting-rung further: down to
        the label-free arity shape, so it reads ACROSS languages. Never collapse it to one number."""
        sa = self.cross._subnodes(root_a)
        sb = self.cross._subnodes(root_b)
        out = []
        for g in range(1, gmax + 1):
            ag = {i for i in sa if self._size(i) <= g}
            bg = {i for i in sb if self._size(i) <= g}
            u = ag | bg
            out.append((g, round(len(ag & bg) / len(u), 3) if u else 1.0))
        return out

    @staticmethod
    def cliff(profile: list, floor: float = 0.5) -> int:
        """The correspondence DEPTH: the largest shape-size grade g for which the profile is still >= floor
        (sharing distinctive structure up to size g). A GRADE, not a magnitude — itself a truncation level,
        so it stays truncatable. Universals-only pairs cliff at a tiny g; real correspondences cliff deep."""
        last = 0
        for g, frac in profile:
            if frac >= floor:
                last = g
            else:
                break
        return last


if __name__ == "__main__":
    print("=== Σ-FOREST: the cross-arm verification gate (CrossMix over one forest) ===\n")
    F = OneForest()

    # ARM 'spec' = source intent; 'impl' = a faithful realization; 'broken' = a divergent one (same
    # qname, different body). The gate asks, structurally: does the other arm REALIZE spec? (stand-in
    # for source↔core↔kernel; the Agda-core and CUDA arms attach identically below.)
    F.add_python("spec",   "def axpy(x, y):\n    return x + y\n", "axpy")
    F.add_python("impl",   "def axpy(x, y):\n    return x + y\n", "axpy")   # faithful
    F.add_python("broken", "def axpy(x, y):\n    return x * y\n", "axpy")   # same name, divergent body

    def show(a, b):
        print(f"--- gate({a}, {b}): does {b} realize {a}? ---")
        for row in F.gate(a, b):
            verdict = "REALIZES (orthogonal, degree 0)" if row["realizes"] else \
                      f"DIVERGES (degree {row['degree']}, shared {row['shared_fraction']})"
            print(f"  {row['unit']:12} [{row['match']}]  {verdict}")
            if not row["realizes"]:
                print(f"       a_residue={row['a_residue']}  b_residue={row['b_residue']}")

    show("spec", "impl")            # REALIZES (orthogonal)
    print()
    show("spec", "broken")          # DIVERGES -- the gate localizes the obstruction (the residues)
    print()

    # ── COMPLETENESS readout: the gate above is blind to a MISSING mirror. Give 'spec' a 2nd algorithm
    #    with no realization, and 'impl' an extra unit with no spec -> coverage flags both as orphans.
    print("--- coverage(spec, impl): does EVERY unit have a mirror? (recall, not just precision) ---")
    F.add_python("spec", "def dot(u, v):\n    return sum(a * b for a, b in zip(u, v))\n", "dot")   # no impl
    F.add_python("impl", "def scale(x, k):\n    return x * k\n", "scale")                            # no spec
    cov = F.coverage("spec", "impl", floor=0.6)
    print(f"  coverage_a(spec→impl)={cov['coverage_a']}  coverage_b(impl→spec)={cov['coverage_b']}  "
          f"complete={cov['complete']}")
    print(f"  spec orphans (no impl mirror): {[o['unit'] for o in cov['a_orphans']]}")
    print(f"  impl orphans (no spec mirror): {[o['unit'] for o in cov['b_orphans']]}")
    print()
    print("--- correspondence(spec, impl): the SYMMETRIC structural matching (discovered, not declared) ---")
    corr = F.correspondence("spec", "impl", floor=0.6)
    for p in corr["pairs"]:
        verdict = "EXACT (degree 0)" if p["exact"] else f"graded (degree {p['degree']})"
        print(f"  {p['a']} ↔ {p['b']}   shared {p['shared_fraction']}  {verdict}")
    print(f"  orphans: spec={corr['a_orphans']}  impl={corr['b_orphans']}   symmetric={corr['symmetric']}")
    print(f"  comparable={corr['comparable']} at the LABEL rung (shared vocab: {corr['shared_vocab'][:5]}...)")
    print()

    # ── the QUOTIENT LADDER: a foreign arm with a DIFFERENT label vocabulary still shares STRUCTURE.
    #    Mint a binary node of two atoms under foreign kinds (the Python-vs-Agda situation in miniature):
    #    label-incomparable, yet the GENERIC PAIR corresponds at the coarse shape rung.
    import jea_pyalg
    leaf1 = F.I.intern(jea_pyalg.IR(kind="Foreign", op="a"))
    leaf2 = F.I.intern(jea_pyalg.IR(kind="Foreign", op="b"))
    F.add_units("foreign", [("pair", F.I.intern(jea_pyalg.IR(kind="Foreign", children=(leaf1, leaf2))))])
    print("--- the data the right way: shared_structure(spec, foreign) at the LABEL-FREE shape rung ---")
    lab = F.correspondence("spec", "foreign", floor=0.6)
    ss = F.shared_structure("spec", "foreign")
    print(f"  label rung:  comparable={lab['comparable']}  (disjoint kinds -> 'nothing' at this rung)")
    print(f"  shape rung:  generic_pair_shared={ss['generic_pair_shared']}  leaf_shared={ss['leaf_shared']}  "
          f"n_shared={ss['n_shared']}")
    print("  => quotient far enough and the GENERIC PAIR (2,(leaf,leaf)) corresponds across the vocabulary gap.")
    print()
    print("--- apply CrossMul AGAIN: re-intern by shape, the cross-term re-applies (now non-vacuous) ---")
    lab = max(F.cross.shared_fraction(r, fr) for _, r in F.arms["spec"] for _, fr in F.arms["foreign"])
    G = F.quotient_to_shape()
    shp = max(G.cross.shared_fraction(r, fr) for _, r in G.arms["spec"] for _, fr in G.arms["foreign"])
    print(f"  spec~foreign cross-term: label rung shared_fraction={lab:.3f} (vacuous) -> shape rung {shp:.3f} (real)")
    print("  CrossMul level-1 = labels (within-language); level-2 = shapes (cross-language). Same machine, one rung up.")
    print()
    print("--- but a scalar is crud: the TRUNCATABLE profile S(g) by shape-size (read the CURVE, not a number) ---")
    raxpy = dict(G.arms["spec"])["axpy"]
    for label, rb in (("axpy ~ axpy (identical)", dict(G.arms["spec"])["axpy"]),
                      ("axpy ~ dot   (different)", dict(G.arms["spec"])["dot"])):
        p = G.profile(raxpy, rb, gmax=7)
        print(f"  {label:26} S(g)=[{' '.join(f'{f:.2f}' for _, f in p)}]  cliff@{G.cliff(p, 0.9)}")
    print("  flat 1.0 = correspondence at every grade; a decay = shares the universal vocabulary, sheds content.")
    print()

    # The other arms compose into the SAME forest+gate with NO new mechanism. They are ENVIRONMENT-BOUND
    # front-ends (the gate READOUT is not); each runs where its toolchain exists, skipping gracefully
    # otherwise -- never faking arm output.
    # AGDA-CORE arm via the LANDED shim (jea_agdai.core_intern_agdai, Φ4): runs where ghc+Agda + a CURRENT
    # .agdai exist (a stale/absent interface -> graceful skip; rebuild with `agda --safe`).
    print("--- agda-core arm (REAL, via the landed Φ4 shim) ---")
    try:
        units = F.add_agda_core("core", os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                     "agda-emit", "Emit.agdai"))
        print(f"  {len(units)} Agda definitions interned into the SAME forest; gate(spec, core) computes the "
              f"cross-term across a real cross-LANGUAGE pair (Python spec ↔ Agda core):")
        for row in F.gate("spec", "core")[:3]:
            print(f"    {row['unit']:20} [{row['match']}]  degree {row['degree']}  shared {row['shared_fraction']}")
    except Exception as e:
        print(f"  skipped (env-bound): {type(e).__name__}: {str(e).splitlines()[0]}")
        print("  (runs where ghc+Agda + a fresh interface exist -- the arm composes by construction)")

    # CUDA kernel arm via libclang: env-bound; composes by construction when the jea_cuda front-end is present.
    print("\n--- cuda kernel arm (env-bound front-end) ---")
    try:
        F.add_cuda("kernel", "__global__ void axpy(float* x, float* y, float* z){ z[0]=x[0]+y[0]; }", "axpy")
        print(f"  kernel arm units: {[q for q,_ in F.arms['kernel']]}; gate(spec, kernel) runs identically.")
    except ModuleNotFoundError:
        print("  jea_cuda front-end not present in this env; the arm composes by construction (same Intern,")
        print("  same {(qname,root)} unit shape) -- no new mechanism, exercised where libclang exists.")
