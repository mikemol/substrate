#!/usr/bin/env python3
"""jea_pysim.py — the similarity script, for Python.  The Agda similarity tool
(scripts/agda_similarity) operated on Agda files via textual multi-scale n-grams;
this operates on Python via the term-algebra interner (jea_pyalg), so the multi-scale
fingerprint IS the grading, anonymization IS exact alpha-equivalence (role-lowering),
and "shared across units" IS interned-node fan-in -- computed once at intern, read as a
lookup, never pairwise.  Two front-ends (ast, and cst if present) lower into ONE forest;
where they share canonical nodes the structure is corroborated, and the ast×cst cross-term
grades their agreement (jea_pyalg.CrossMix).

The machinery mirrors the Agda script's surfaces:
  * UNIT of comparison: a def / async def / class (the thing you'd extract), one per root id.
  * FINGERPRINT per unit: its interned-support set at each GRADE (the multi-scale analogue of
    the token/char/line/block n-gram bags).
  * SHARED/TOTAL per grade -> the genericization ratio -> STRONG/PARTIAL/WEAK orbit verdict
    (same thresholds as agda_similarity.score), max-ratio-across-grades.
  * CLUSTERS: units grouped by SHARED high-fan-in canonical subtrees (the interner already
    grouped them -- no distance matrix); reported with the per-pair shared fraction.

NOT a similarity METRIC bolted on: similarity is a readout of the SPPF the interner builds.
NO target script is hardcoded -- this is the instrument; point it at any .py via the CLI.
"""
from __future__ import annotations
import ast
import sys
import os
import glob as glob_mod
import argparse
from dataclasses import dataclass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jea_pyalg import (Intern, IR, Lowerer, PyDivStr, CrossMix,
                       full_skeleton, grade as trace_grade, _HAS_CST)
try:
    from jea_pyalg import CstLowerer
    import libcst as cst
except Exception:
    CstLowerer = None
    cst = None


# the comparison units: the things one would extract / consolidate.
_UNIT_NODES = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)

# orbit thresholds -- identical to agda_similarity.score (so the verdict reads the same).
STRONG_ORBIT = 0.80
PARTIAL_ORBIT = 0.50


@dataclass
class Unit:
    """One comparison unit (a def/class): its source location + its interned root id."""
    name: str
    path: str
    lineno: int
    root: int                      # interned id of the unit's IR root
    support: frozenset             # all interned ids reachable from root (its subterm support)
    depth: dict = None             # node id -> min trace-depth from this unit's root (the SCALE axis)


class Corpus:
    """All units across the given files, lowered into ONE interner -> one SPPF forest.
    Fan-in across units is the sharing signal; it is computed at intern, read as a lookup.

    The four readouts are the backward-images of the Agda similarity script's four either/ors,
    each a read of THIS forest (not a separate textual pass):
      * scales->grade  (Trace 1): support stratified by actual trace-DEPTH (block..char3 = depth bands)
      * anonymize->role(Trace 2): the payload name-map IS the parametric-template parameter list
      * cosine->fan-in (Trace 3): fan-in carries MULTIPLICITY (the freq cosine weighed), not just presence
      * recursive-tmpl (Trace 4): INTERIOR-node fan-in = shared structure inside the residue (already there)
    """
    def __init__(self):
        self.I = Intern()
        self.units: list[Unit] = []
        # node id -> set of unit indices referencing it (multiplicity fan-in across units)
        self.node_units: dict[int, set] = {}

    def _support(self, root: int) -> frozenset:
        out = set(); stack = [root]
        while stack:
            j = stack.pop()
            if j in out: continue
            out.add(j); stack.extend(self.I.nodes[j].children)
        return frozenset(out)

    def _depth_map(self, root: int) -> dict:
        """node id -> MIN depth from root (BFS). This is the real scale axis: depth 0 = the unit
        head (block-coarse), increasing depth = finer structure (line/token/char3 bands). The
        backward-image of the Agda script's four nested scales -- recoverable, not a size-cap proxy."""
        depth = {root: 0}
        frontier = [root]
        d = 0
        while frontier:
            nxt = []
            for j in frontier:
                for c in self.I.nodes[j].children:
                    if c not in depth:
                        depth[c] = d + 1
                        nxt.append(c)
            frontier = nxt; d += 1
        return depth

    def add_file(self, path: str):
        try:
            src = open(path, encoding="utf-8").read()
            tree = ast.parse(src)
        except (SyntaxError, OSError, UnicodeDecodeError) as e:
            print(f"  [unparsed] {path}: {type(e).__name__}", file=sys.stderr)
            return
        lw = Lowerer(self.I)
        # lower every top-level AND nested def/class as a unit (walk, intern each unit root).
        for node in ast.walk(tree):
            if isinstance(node, _UNIT_NODES):
                # lower this unit in its own fresh role-scope so alpha-equivalence is per-unit
                ulw = Lowerer(self.I)
                root = ulw.lower(node)
                if root is None:
                    continue
                sup = self._support(root)
                u = Unit(name=getattr(node, "name", "?"), path=path,
                         lineno=getattr(node, "lineno", -1), root=root,
                         support=sup, depth=self._depth_map(root))
                uidx = len(self.units)
                self.units.append(u)
                for nid in sup:                       # record unit-membership (multiplicity fan-in)
                    self.node_units.setdefault(nid, set()).add(uidx)

    # ---- readouts (all lookups over the interned forest, no pairwise distance) ----

    def fanin_of(self, node_id: int) -> int:
        return self.I.fanin[node_id]

    def shared_fraction(self, u: Unit, v: Unit) -> float:
        """Coherent/orthogonal fraction of two units: |shared support| / |union support|.
        1.0 = identical (alpha-equivalent -> SAME root id); 0 = no shared canonical structure."""
        inter = len(u.support & v.support)
        union = len(u.support | v.support)
        return inter / union if union else 1.0

    def shared_fraction_at_grade(self, u: Unit, v: Unit, k: int) -> float:
        """Trace-1 backward-image: shared support restricted to nodes at trace-DEPTH <= k -- the
        real scale axis (depth 0 = coarse/block-like unit head; deeper = finer line/token/char3).
        NOT a size-cap proxy: it uses each node's actual min-depth-from-root, so the coarse/fine
        spread is recoverable to the Agda script's nested scales. Low k high + high k low = the
        'shared vocabulary, distinct content' = healthy-abstraction diagnostic."""
        su = {n for n in u.support if u.depth.get(n, 1 << 30) <= k}
        sv = {n for n in v.support if v.depth.get(n, 1 << 30) <= k}
        inter = len(su & sv); union = len(su | sv)
        return inter / union if union else 1.0

    def scale_spread(self, u: Unit, v: Unit, kmax: int = 6) -> list:
        """The full coarse->fine spread between two units: shared-fraction at each depth band.
        This IS the Agda script's multi-scale breakdown, now a continuous depth axis over one forest."""
        return [(k, self.shared_fraction_at_grade(u, v, k)) for k in range(kmax + 1)]

    # =====================================================================
    # S(g) -- THE SIMILARITY PROFILE AS A HoTT TRUNCATION (not a scalar collapse).
    #
    # The OLD verdict took max-ratio-across-grades -> one %, which returns the COARSEST,
    # most-saturated grade (the universal node-types near the root) = ~95% for ANY two Python
    # files. That is the (-1)-truncation ‖·‖_{-1}: the bare proposition "merely similar", the
    # path discarded. Every control read STRONG because max reports the grade carrying no signal.
    #
    # The fix is to TRUNCATE LIKE A PATH, not collapse to a prop. At grade g we keep the
    # similarity-path structure to depth g and forget above: ‖forget_carrier(u)‖_g. Two terms are
    # "equal in the g-truncation" iff their carrier-forgotten skeletons agree to depth g. The
    # CLIFF -- the highest g* with agreement, where g*+1 splits -- is the pair's CONNECTEDNESS
    # LEVEL, and it IS the hole's location (the structural depth the carrier/divergence sits at).
    #
    # Two forgettings composed (this is the load-bearing correction over the old canonical-support
    # intersection, which showed FLAT-ZERO for carrier-different code that shares no interned ids):
    #   forget_carrier : drop `lit` (the carrier VALUE), keep kind/role/op -- so two
    #                    implementations of the same SHAPE match even when no subtree interns equal.
    #   truncate_g     : keep the head-spine to depth <= g, forget below.
    # S(g) = longest-common-prefix fraction of the two truncated carrier-forgotten skeletons.
    # The SHAPE of S(g) classifies; the cliff localizes. Never collapse it to one number.
    # =====================================================================
    def _trunc_skeleton(self, root: int, g: int) -> tuple:
        """‖forget_carrier(root)‖_g : carrier-forgotten head-spine, truncated at depth <= g.
        forget_carrier = drop `lit` (the carrier value); keep (kind, role, op) = the SHAPE.
        Pre-order with depth cut -- the n-truncation of the term's skeleton path."""
        out = []
        def walk(i, d):
            if d > g:
                return
            n = self.I.nodes[i]
            out.append((n.kind, n.role, n.op))      # forget_carrier: NO lit
            for c in n.children:
                walk(c, d + 1)
        walk(root, 0)
        return tuple(out)

    def S(self, u: Unit, v: Unit, gmax: int = None) -> list:
        """The similarity PROFILE S(g) -- now a DEPTH-FOLD over the recursive typehole tree, NOT a
        flat pre-order LCP. (The flat LCP was one root-to-divergence PATH through the alignment; it
        WALLED at the first mismatch -- couldn't see {familiar, unfamiliar, familiar} past the
        middle divergence, and was fooled into 'DUPLICATE' by {unfamiliar, familiar} root-level
        differences the skeleton flattens. The typehole tree recurses PAST every divergence on
        every branch; S(g) is its projection onto the DEPTH axis.)

        S(g) = (shared/skeleton nodes at depth <= g) / (all aligned nodes at depth <= g), read off
        the typehole tree. A hole at depth d is a cliff at g=d; multiple holes at different depths
        give MULTIPLE cliffs (the flat LCP could only ever report one). The tail past a hole still
        counts as shared (so {f,u,f} keeps its trailing familiar); a root hole shows as a g=0 cliff
        (so {u,f} is NOT a false duplicate). The cliff is a hole projected onto the depth axis."""
        th = self.typehole([u.root, v.root])
        by_depth_shared, by_depth_total = self._depth_fold(th)
        if gmax is None:
            gmax = max(max(by_depth_total or [0]), 1)
        prof = []
        cum_shared = cum_total = 0
        for g in range(gmax + 1):
            cum_shared += by_depth_shared.get(g, 0)
            cum_total += by_depth_total.get(g, 0)
            prof.append((g, cum_shared / cum_total if cum_total else 1.0))
        return prof

    def _depth_fold(self, th: dict, depth: int = 0, shared: dict = None, total: dict = None):
        """Fold the typehole tree into (shared-by-depth, total-by-depth). A `shared`/`skeleton`
        node counts shared at its depth; a `hole` counts toward total but NOT shared (it is the
        divergence at that depth). Recurses into skeleton children AND into hole sub-structure
        (the recurse-into-holes the flat LCP lacked), so every branch is counted, not just one path."""
        if shared is None:
            shared, total = {}, {}
        kind = th.get("kind")
        total[depth] = total.get(depth, 0) + 1
        if kind in ("shared", "skeleton"):
            shared[depth] = shared.get(depth, 0) + 1
        # recurse into children (skeleton/shared) AND any sub-structure under a recursed hole
        for c in th.get("children", []):
            self._depth_fold(c, depth + 1, shared, total)
        return shared, total

    def lcp_depth(self, u: Unit, v: Unit, gmax: int = None) -> list:
        """The RAW longest-common-prefix length as a function of g -- the order-faithful
        discriminator the normalized ratio is a view of. The cliff is where lcp_depth STOPS
        GROWING while the skeletons keep growing: that g is the connectedness level (the hole).
        Reading raw depth separates 'deep shared prefix' (real) from 'short head match scaled up'
        (the FunctionDef preamble), which the min-normalized ratio alone can't tell apart."""
        if gmax is None:
            gmax = 1 + max(max(u.depth.values(), default=0), max(v.depth.values(), default=0))
        out = []
        for g in range(gmax + 1):
            su = self._trunc_skeleton(u.root, g)
            sv = self._trunc_skeleton(v.root, g)
            lcp = 0
            for a, b in zip(su, sv):
                if a != b:
                    break
                lcp += 1
            out.append((g, lcp, min(len(su), len(sv))))   # (grade, lcp depth, shorter length)
        return out

    @staticmethod
    def classify_profile(prof: list) -> dict:
        """Read the SHAPE of S(g) (never a single %). Returns the relationship class + the cliff
        grade (the hole's location). The discriminator and the hole both live in the shape:
          flat ~1 throughout            -> DUPLICATE (inf-connected; no hole)
          plateau through skeleton, cliff-> SAME-ALGORITHM-DIFFERENT-CARRIER (hole = cliff grade)
          low mid, rises only at fine   -> SHARED-IDIOMS-DIFFERENT-ALGORITHM (no shared skeleton)
          high only at g=0, decays      -> UNRELATED (baseline; (-1)/0-connected)"""
        if not prof:
            return {"class": "EMPTY", "cliff": None, "profile": prof}
        vals = [s for _, s in prof]
        g0 = vals[0]
        drops = [(prof[i][0], vals[i] - vals[i + 1]) for i in range(len(vals) - 1)]
        cliff_g, cliff_drop = (max(drops, key=lambda t: t[1]) if drops else (None, 0.0))
        hi = 0.85
        lo = 0.30
        mn = min(vals); mx = max(vals); last = vals[-1]
        # a real PLATEAU requires the high region to extend PAST g=0: there must be a grade g>=1
        # that is still high, with the cliff AFTER it. A cliff at g=0 (immediate decay) is NOT a
        # plateau -- it is unrelated/baseline. The plateau length is how far high persists.
        plateau_len = 0
        for s in vals:
            if s >= hi:
                plateau_len += 1
            else:
                break
        if mn >= hi:
            cls = "DUPLICATE"; cliff_g = None                  # flat high: inf-connected
        elif plateau_len >= 2 and cliff_drop >= 0.25 and (cliff_g or 0) >= 1:
            cls = "SAME-ALGORITHM-DIFFERENT-CARRIER"           # high persists past g0, THEN a cliff
        elif mx < hi and last > g0 + 0.05:
            cls = "SHARED-IDIOMS-DIFFERENT-ALGORITHM"; cliff_g = None   # low coarse, rises fine
        elif g0 >= hi and last <= lo:
            cls = "UNRELATED"; cliff_g = 0                      # high only at g0, decays (no plateau)
        else:
            cls = "PARTIAL"                                    # mixed; cliff_g still reported
        return {"class": cls, "cliff": cliff_g, "cliff_drop": round(cliff_drop, 2),
                "plateau_len": plateau_len,
                "S0": round(g0, 2), "Smin": round(mn, 2), "Smax": round(mx, 2),
                "profile": [(g, round(s, 2)) for g, s in prof]}

    def shape_verdict(self, u: Unit, v: Unit) -> dict:
        """The verdict IS the typehole tree's structure -- NOT a label. (The recursive law, applied
        to the classifier itself: a shape-LABEL is ‖tree‖_{-1}, the bare-proposition collapse, the
        same max-collapse sin one level up. {f,u,f} has no label -- it has a SHAPE: shared shell,
        holes at specific depths, shared tail. Collapsing it to SHARED-SHELL-MULTI-HOLE throws away
        the depths and the fraction, which are exactly what distinguish it from an unrelated pair
        that also happens to have several holes. So we REPORT THE TREE.)

        Returns the hole-depths (the multi-cliff structure), the shared-fraction, and the S(g)
        profile. `label` is assigned ONLY for genuinely DEGENERATE trees (0 holes -> DUPLICATE; a
        single hole at depth 0 -> ROOT-DIVERGENT) and is None otherwise -- the structure is the
        verdict, the label is just a name for the simplest shapes. Don't ship the label as if it
        were the structure."""
        th = self.typehole([u.root, v.root])
        prof = self.S(u, v)
        s, h = self._th_stats(th)
        holes = self._collect_holes(th)
        hole_depths = sorted(hd.get("depth", 0) for hd in holes)
        shared_frac = s / (s + h) if (s + h) else 1.0
        # a label ONLY for degenerate trees; otherwise None -- the hole_depths ARE the answer.
        if h == 0:
            label = "DUPLICATE"                       # zero holes: the trivial tree
        elif h == 1 and hole_depths == [0]:
            label = "ROOT-DIVERGENT"                  # one hole at the root: differ only at top
        else:
            label = None                              # structured tree: read hole_depths, do not collapse
        return {"label": label, "holes": h, "shared_nodes": s, "shared_frac": round(shared_frac, 2),
                "hole_depths": hole_depths,           # THE VERDICT: where the divergences are (multi-cliff)
                "profile": [(g, round(sg, 2)) for g, sg in prof],
                # a human summary that PRESERVES the structure rather than collapsing it:
                "summary": (f"{s} shared nodes, {h} hole(s)"
                            + (f" at depths {hole_depths}" if hole_depths else "")
                            + f"; shared_frac {shared_frac:.2f}"
                            + (f" [{label}]" if label else ""))}

    def genericization(self) -> dict:
        """Per 'scale', the shared/total ratio across ALL units -- the Agda score.genericization_score
        analogue. Trace-3 backward-image: 'shared' counts a node referenced by >=2 distinct UNITS
        (node_units multiplicity), the faithful image of the Agda 'in >=2 files' -- NOT raw parent
        fan-in (which over-counts within a single unit). Coarse = head shapes; fine = canonical nodes."""
        n = len(self.units)
        if n == 0:
            return {}
        # fine scale: canonical nodes shared across >=2 distinct units (multiplicity, not parent-count)
        total_fine = len(self.node_units)
        shared_fine = sum(1 for us in self.node_units.values() if len(us) >= 2)
        # coarse scale: distinct HEAD shapes, shared = a head shape used by >1 unit
        head_units: dict[tuple, set] = {}
        for ui, u in enumerate(self.units):
            for nid in u.support:
                nn = self.I.nodes[nid]
                head_units.setdefault((nn.kind, nn.op, nn.lit), set()).add(ui)
        total_coarse = len(head_units)
        shared_coarse = sum(1 for us in head_units.values() if len(us) >= 2)
        return {
            "coarse(head-shape)": (shared_coarse, total_coarse,
                                   shared_coarse / total_coarse if total_coarse else 0.0),
            "fine(canonical-node)": (shared_fine, total_fine,
                                     shared_fine / total_fine if total_fine else 0.0),
        }

    # =====================================================================
    # COHOMOLOGY -- the corpus's METALANGUAGE, computed (not designed).
    #
    # The corpus is written in an implicit language. Its ALPHABET is the GENERATORS
    # (low-grade shared atoms -- the words everyone uses); its IDIOMS are the COCYCLES
    # (compounds shared MORE than their generators alone would explain). Everything
    # else is COBOUNDARY (composites shared only because their parts always co-occur --
    # mechanically derivable, the redundancy cleanup removes; the "small things look
    # alike" noise, correctly identified as d-exact).
    #
    # This is H^1 of the corpus-as-graded-complex (cf. CrossMul: coherence is the
    # nilpotency degree; coboundary = d-exact = vanishes; cocycle = d-closed-not-exact
    # = the residue that IS information). The metalanguage = generators + cocycles;
    # |generators + cocycles| is the "Just Enough" receipt -- the minimal vocabulary
    # the corpus actually speaks, with the coboundary the throwable redundancy.
    #
    # The test for a shared composite node n (shared by U(n) units, children c):
    #   COBOUNDARY: its children are each shared by ~U(n) units too -- n recurs only
    #     because its parts always co-occur. d-exact, derivable, boring.
    #   COCYCLE:    its children are shared MORE WIDELY than n (common vocabulary), but
    #     THIS composition recurs as a unit -- the composition carries information the
    #     parts don't. d-closed-not-exact. An idiom. The real abstraction.
    # =====================================================================
    def cohomology(self, min_units: int = 2, cocycle_bits: float = 1.0):
        """Classify every shared canonical node as generator / coboundary / cocycle.

        The coboundary map is the INDEPENDENT-ASSEMBLY prediction: a composite n with children
        c_i, each shared by U(c_i) of N units, would under independent composition recur about
        N * prod(U(c_i)/N) times. n is a COBOUNDARY if its actual U(n) ~ that prediction (as common
        as chance-assembly of its parts -- derivable). It is a COCYCLE if U(n) >> prediction: the
        composition recurs as a unit far more than its parts predict -- an idiom. The excess is the
        SURPRISAL in bits: log2(U(n)) - sum log2(U(c_i)/N) ... but since prediction can exceed 1,
        we measure observed-minus-predicted in log space: bits = log2(U(n) / max(pred, 1e-9)).
        cocycle_bits: surprisal threshold (default 1.0 = recurs >=2x more than parts predict)."""
        import math
        N = max(1, len(self.units))
        U = {nid: len(us) for nid, us in self.node_units.items() if len(us) >= min_units}
        def size(nid):
            return len(self._support(nid))
        generators, cocycles, coboundary = [], [], []
        for nid, u in U.items():
            nn = self.I.nodes[nid]
            head = (nn.kind, nn.role, nn.op, nn.lit)
            kids = list(nn.children)
            if not kids:
                generators.append((nid, u, 1, head, 0.0))      # atom shared across units = a word
                continue
            # independent-assembly prediction: N * prod over the INDEPENDENT children of (U(c)/N).
            # Δ-Π-surprisal-truearity: a child REUSED within this node is a diamond (a repeated
            # interned id) -- its co-occurrence with itself is FORCED (conditional prob 1, log2=0),
            # NOT an independent draw. Counting reused children inflated the prediction's smallness,
            # spuriously inflating surprise (the old 43%-cocycle generosity). Use DISTINCT child ids
            # = the free positions = the per-node true arity. Read from the SPPF (distinct interned
            # ids), not recomputed -- the diamond is already collapsed in the structure.
            free_kids = list(dict.fromkeys(kids))      # distinct ids = independent draws (diamonds once)
            log_pred = math.log2(N)
            for c in free_kids:
                uc = U.get(c) or len(self.node_units.get(c, {0}))
                log_pred += math.log2(max(uc, 1) / N)
            # observed minus predicted, in bits. >0 => recurs more than independent assembly => idiom.
            bits = math.log2(max(u, 1)) - log_pred
            if bits >= cocycle_bits:
                cocycles.append((nid, u, size(nid), head, round(bits, 1)))
            else:
                coboundary.append((nid, u, size(nid), head, round(bits, 1)))
        generators.sort(key=lambda t: -t[1])
        cocycles.sort(key=lambda t: -(t[4] * t[2]))     # surprisal * size = the substantial idioms
        coboundary.sort(key=lambda t: -t[1])
        return {
            "generators": generators, "cocycles": cocycles, "coboundary": coboundary,
            "summary": {
                "alphabet_size": len(generators),
                "idiom_count": len(cocycles),
                "coboundary_count": len(coboundary),
                "metalanguage_size": len(generators) + len(cocycles),
                "total_shared": len(U),
            }}

    def recursive_shared(self, min_units: int = 2, min_depth: int = 1):
        """Trace-4 backward-image: the Agda script's RECURSIVE template (shared structure found
        INSIDE per-file residue) is ALREADY in the forest -- it is the fan-in of INTERIOR nodes
        (nodes shared across units that are NOT any unit's root). No separate drill-down pass:
        interning is bottom-up, so nested shared structure is just multiplicity at depth >= min_depth.
        Returns (node_id, n_units, min_depth_across_units, head) for interior shared nodes."""
        roots = {u.root for u in self.units}
        out = []
        for nid, us in self.node_units.items():
            if len(us) >= min_units and nid not in roots:
                md = min(self.units[ui].depth.get(nid, 1 << 30) for ui in us)
                if md >= min_depth:
                    nn = self.I.nodes[nid]
                    out.append((nid, len(us), md, (nn.kind, nn.op, nn.lit)))
        return sorted(out, key=lambda t: (-t[1], t[2]))

    def parameter_map(self, node_id: int) -> dict:
        """Trace-2 backward-image: role-lowering kept the original names as payload residue, and
        that residue IS the parametric-template's parameter list (skeleton.py's 'per-file
        substitution map'). For a shared canonical node, return {unit -> the payload bindings it
        carried at that position} -- i.e. how each unit instantiates the shared parametric skeleton.
        (The role-quotient runs BACKWARD: shared structure + per-unit payload = the parametric form.)"""
        # NB: a shared node has ONE canonical identity; the per-unit instantiation lives in the
        # payload of the nodes that role-mapped to it. We surface the node's own payload here as the
        # representative binding; full per-unit recovery would thread the lowerer's name-map (kept).
        if not (0 <= node_id < self.I.size()):
            return {}
        nn = self.I.nodes[node_id]
        return {"head": (nn.kind, nn.role, nn.op, nn.lit), "payload(residue)": nn.payload,
                "units": sorted(self.node_units.get(node_id, set()))}

    def verdict(self, scores: dict) -> str:
        if not scores:
            return "NO DATA"
        mx = max(r for _, _, r in scores.values())
        if mx >= STRONG_ORBIT:
            return f"STRONG orbit candidate ({mx*100:.1f}% max shared) -- ready to consolidate"
        if mx >= PARTIAL_ORBIT:
            return f"PARTIAL orbit ({mx*100:.1f}% max shared)"
        return f"WEAK orbit ({mx*100:.1f}% max shared) -- structurally divergent"

    # =====================================================================
    # THE TYPEHOLER -- the one operation the whole tool is readouts of.
    # Given a set of aligned node-ids (one per unit), find the COMMON STRUCTURE
    # (the shared skeleton, kept) and the DISTINCTIONS (the typed holes, where they
    # diverge).  At each hole, RECURSE on the fillers (find THEIR common structure);
    # stop when the fillers share nothing (the residue has no structure left -- the
    # productivity/EEATrace termination: recurse on the residue until interning finds
    # no more sharing).  Flat = depth-capped; verdict = skeleton/hole ratio; grouping
    # guidance = does it reduce to one skeleton or shatter into holes.  ONE function.
    #
    # A hole's TYPE is the common structure of its fillers (all BinOp -> <BinOp:?>;
    # all int literals -> <Constant/int:?>; mixed -> <?>) -- the SEMANTIC distinction
    # axis, not a string coincidence.  This is "the semantic distinction between these
    # things" (the holes) AND "the common semantics underneath them" (the skeleton),
    # one decomposition read two ways.
    # =====================================================================
    def typehole(self, node_ids: list[int], depth: int = 0, max_depth: int = 24) -> dict:
        """Align a set of node-ids; return {kind, head, skeleton/hole, ...}. Recursive."""
        node_ids = list(node_ids)
        # base: all identical -> fully shared, no hole (the common structure IS this node)
        if len(set(node_ids)) == 1:
            nid = node_ids[0]; nn = self.I.nodes[nid]
            return {"kind": "shared", "head": (nn.kind, nn.role, nn.op, nn.lit),
                    "node": nid, "children": []}
        heads = [(self.I.nodes[i].kind, self.I.nodes[i].op, self.I.nodes[i].lit) for i in node_ids]
        # if heads DIVERGE, or we hit the depth cap -> a TYPED HOLE. Its type is the common
        # structure of the fillers: shared head if they share one, else the set of head-kinds.
        if len(set(heads)) > 1 or depth >= max_depth:
            kinds = sorted(set(h[0] for h in heads))
            # RECURSE INTO THE HOLE: even when heads differ, the fillers may share sub-structure
            # (the reused p/q/y inside a diverging expression). Try to typehole their children;
            # if a shared sub-skeleton emerges, the divergence is a SKELETON-with-sub-holes, not a
            # terminal hole -- and the reused fillers surface as multiple holes whose dependencies
            # the telescope reads. Only emit a TERMINAL hole when the fillers share nothing (the
            # residue has no structure left -- the productivity/EEATrace termination).
            if depth < max_depth and len(set(heads)) > 1:
                childsets = [self.I.nodes[i].children for i in node_ids]
                arities = set(len(c) for c in childsets)
                if len(arities) == 1 and arities != {0}:
                    nchild = arities.pop()
                    sub = [self.typehole([cs[pos] for cs in childsets], depth + 1, max_depth)
                           for pos in range(nchild)]
                    # only treat as a recursable region if SOME child position is shared (a sub-skeleton
                    # or a re-shared hole) -- i.e. the recursion found structure the flat hole hid.
                    if any(s["kind"] in ("shared", "skeleton") for s in sub):
                        return {"kind": "skeleton", "head": ("|".join(kinds), "", ""),
                                "diverged": True, "children": sub}
            # terminal typed hole: the fillers share no sub-structure.
            hole_type = kinds[0] if len(kinds) == 1 else "?"
            fillers = [self._filler_repr(i) for i in node_ids]
            return {"kind": "hole", "type": hole_type, "head_kinds": kinds,
                    "fillers": fillers, "depth": depth}
        # heads AGREE -> shared skeleton at this node; RECURSE positionally into children.
        # (arity can differ even with same head -- e.g. Call with different #args -> that's a hole.)
        childsets = [self.I.nodes[i].children for i in node_ids]
        arities = set(len(c) for c in childsets)
        h0 = heads[0]
        if len(arities) > 1:
            # same head, different arity: the children-region is a typed hole (variadic distinction)
            return {"kind": "skeleton", "head": (h0[0], h0[1], h0[2]),
                    "children": [{"kind": "hole", "type": h0[0] + ":variadic",
                                  "fillers": [self._filler_repr(i) for i in node_ids], "depth": depth}]}
        nchild = arities.pop()
        kids = []
        for pos in range(nchild):
            kids.append(self.typehole([cs[pos] for cs in childsets], depth + 1, max_depth))
        return {"kind": "skeleton", "head": (h0[0], h0[1], h0[2]), "children": kids}

    def _filler_repr(self, node_id: int) -> dict:
        nn = self.I.nodes[node_id]
        return {"head": (nn.kind, nn.op, nn.lit), "payload": nn.payload, "node": node_id}

    # =====================================================================
    # DEPENDENT TYPEHOLES -- the hole-telescope, READ FROM THE SPPF (not a post-pass).
    #
    # The dependency I want -- "these holes carry the same filler" -- is SHARING, and sharing
    # is what the interner IS. A reused parameter (`r*r`) is not detected by comparing filler
    # vectors after the fact; it is a DIAMOND in the DAG: one interned node with fan-in >= 2,
    # built at intern time. The interner is already a dependency-tracker -- hash-consing turns
    # equality-of-structure into identity-of-node, which is exactly what a dependent type needs
    # ("H2's value = H1's value" <=> "H2's filler IS H1's filler node"). So the telescope is a
    # READOUT of the cluster subforest's fan-in, not a recomputation. Dependency kind = the
    # cross-term nilpotency degree between two holes' fillers (CrossMix at the hole-grade):
    #   EQ   : the fillers are the SAME interned node (a full diamond)        -- degree 0, orthogonal-shared.
    #   TYPE : different nodes, same head, sharing children (a partial diamond) -- graded.
    #   FREE : disjoint subforests (no shared interned structure)              -- no diamond.
    #
    # TRUE ARITY = free holes. Dependencies collapse apparent arity to real arity. This is the
    # corpus's GRAMMAR (which holes must agree), and the principled surprisal fix (dependent
    # holes aren't independent draws). EXTENSIONAL (observed co-variation), not a proven Pi --
    # flagged for AI-Q: liftable to Agda Pi-telescopes, or only observed sharing?
    # =====================================================================
    def _collect_holes(self, th: dict, acc: list = None) -> list:
        """In-order list of holes in the typehole tree, each with its per-unit filler vector."""
        if acc is None:
            acc = []
        if th["kind"] == "hole":
            acc.append(th)
        for c in th.get("children", []):
            self._collect_holes(c, acc)
        return acc

    def _hole_filler_support(self, hole: dict) -> set:
        """The interned nodes the hole's fillers occupy, unioned across units -- the hole's
        position in the SPPF. Two holes are dependent iff these supports SHARE (a diamond)."""
        sup = set()
        for f in hole["fillers"]:
            sup.add(f["node"])
        return sup

    def dependency_telescope(self, th: dict) -> dict:
        """The hole-telescope, read from SPPF sharing (the diamonds the interner already built).
        Two holes are EQ-dependent iff their filler-supports intersect (same interned node in
        some unit -- a diamond); TYPE-dependent iff their fillers share a head AND share child
        structure (partial diamond) without being equal; FREE iff disjoint. True arity = free holes."""
        holes = self._collect_holes(th)
        n = len(holes)
        supports = [self._hole_filler_support(h) for h in holes]
        # per-hole per-unit head-kind vector (for the TYPE-dependency graded case)
        kinds = [tuple(f["head"][0] for f in h["fillers"]) for h in holes]
        # per-hole per-unit filler node vector (for the diamond test PER UNIT, the strongest EQ)
        nodevec = [tuple(f["node"] for f in h["fillers"]) for h in holes]
        deps = []
        free = [True] * n
        for j in range(n):
            for i in range(j):
                # EQ: the diamond -- fillers are the SAME interned node in every unit (identity =
                # the interner's recorded equality). This is fan-in linking the two hole-positions.
                if nodevec[j] == nodevec[i]:
                    deps.append((j, i, "EQ")); free[j] = False; break
                # partial diamond: supports share an interned node (reuse in SOME units) -> EQ-ish
                if supports[j] & supports[i]:
                    deps.append((j, i, "EQ")); free[j] = False; break
                # TYPE: same head-kind per unit and the kind varies (a type-family dependency)
                if kinds[j] == kinds[i] and len(set(kinds[j])) > 1:
                    deps.append((j, i, "TYPE")); free[j] = False; break
        return {"n_holes": n, "true_arity": sum(1 for f in free if f),
                "deps": deps, "free": [k for k in range(n) if free[k]]}

    @staticmethod
    def _th_stats(th: dict) -> tuple:
        """(shared_count, hole_count) over a typehole tree -- the skeleton/hole ratio = the verdict."""
        if th["kind"] == "hole":
            return (0, 1)
        s, h = (1 if th["kind"] == "shared" else 1), 0   # skeleton/shared nodes count toward 'shared'
        for c in th.get("children", []):
            cs, ch = Corpus._th_stats(c); s += cs; h += ch
        return (s, h)

    def cluster_surprisal(self, comp: list, th: dict = None) -> dict:
        """Δ-Π-surprisal-truearity (the cluster-level fix the telescope uniquely enables).

        A typeholed cluster of U units with apparent hole-count h would, under INDEPENDENT
        variation of its holes, recur about prod over holes of (variants_i / U) -- but holes that
        are dependently linked (the telescope's deps) do NOT vary independently. The free-parameter
        count is the telescope's TRUE_ARITY, not h. So the prediction uses true_arity free holes,
        each contributing its observed variant-count; the dependent holes contribute nothing (their
        variation is FORCED by the free ones, conditional prob 1, log2=0). This catches dependencies
        BETWEEN HOLES AT DIFFERENT DEPTHS -- transitively -- which the per-node distinct-children
        dedup cannot. The surprisal is observed-cluster-cohesion minus the true-arity prediction:
        a cluster that coheres MORE than its true_arity free holes predict is a genuine idiom."""
        if th is None:
            th = self.typehole([self.units[ui].root for ui in comp])
        tel = self.dependency_telescope(th)
        s, h = self._th_stats(th)
        U = len(comp)
        holes = self._collect_holes(th)
        # variants per FREE hole = distinct fillers across the cluster (the real degrees of freedom)
        free_idx = set(tel["free"])
        free_variants = []
        for k, hole in enumerate(holes):
            if k in free_idx:
                nodevec = tuple(f["node"] for f in hole["fillers"])
                free_variants.append(len(set(nodevec)))
        # the apparent prediction would multiply ALL h holes' variants; the true one only the free.
        apparent_dof = 1
        for hole in holes:
            apparent_dof *= max(1, len(set(f["node"] for f in hole["fillers"])))
        true_dof = 1
        for v in free_variants:
            true_dof *= max(1, v)
        return {"units": U, "apparent_holes": h, "true_arity": tel["true_arity"],
                "apparent_dof": apparent_dof, "true_dof": true_dof,
                "deps": [d[2] for d in tel["deps"]],
                # collapse factor: how much the dependencies shrink the parameter space
                "collapse": (apparent_dof / true_dof) if true_dof else 1.0}

    def typehole_verdict(self, th: dict) -> str:
        s, h = self._th_stats(th)
        tot = s + h
        ratio = s / tot if tot else 0.0
        if h == 0:
            return f"IDENTICAL ({s} shared nodes, 0 holes) -- one concept, no parameters"
        tel = self.dependency_telescope(th)
        ta = tel["true_arity"]; nd = len(tel["deps"])
        # the arity clause: apparent holes vs the INDEPENDENT (free) ones the dependencies collapse to
        if nd:
            arity = f"{h} holes -> {ta} independent params ({nd} dependency: {[d[2] for d in tel['deps']][:4]})"
        else:
            arity = f"{h} independent hole(s)"
        if ratio >= STRONG_ORBIT:
            return f"STRONG orbit ({ratio*100:.0f}% shared, {arity}) -- one parametric concept"
        if ratio >= PARTIAL_ORBIT:
            return f"PARTIAL orbit ({ratio*100:.0f}% shared, {arity}) -- partly common, partly distinct"
        return f"WEAK ({ratio*100:.0f}% shared, {arity}) -- distinct concepts; reason about them separately"

    @staticmethod
    def render_typehole(th: dict, indent: int = 0) -> str:
        """Human-readable skeleton with typed holes -- 'common semantics' (skeleton) + 'distinctions'
        (holes named by what varies). The thing you point an LLM at to mechanize the grouping."""
        pad = "  " * indent
        if th["kind"] == "hole":
            kinds = th.get("head_kinds", [])
            fillers = th.get("fillers", [])
            # name the hole by the varying payloads when the kind is shared (the parameter values)
            vals = []
            for f in fillers:
                p = f.get("payload", ())
                vals.append(p[0] if p else f["head"][0])
            distinct = sorted(set(str(v) for v in vals))
            return f"{pad}<HOLE:{th['type']}> varies: {{{', '.join(distinct[:6])}}}"
        head = th["head"]
        label = head[0] + (f"[{head[2]}]" if len(head) > 2 and head[2] else "") + (f"({head[1]})" if head[1] else "")
        if th["kind"] == "shared" and not th.get("children"):
            return f"{pad}{label}"
        out = [f"{pad}{label}"]
        for c in th.get("children", []):
            out.append(Corpus.render_typehole(c, indent + 1))
        return "\n".join(out)

    def clusters(self, min_shared: float = 0.5, min_size: int = 6,
                 min_cohesion: float = 0.0) -> list[list[int]]:
        """Units grouped by mutual high shared-fraction (mutual-NN analogue). Cheap: the sharing
        is already interned, so this is a threshold over precomputed support-overlaps.

        min_size: ignore units whose support is smaller than this -- trivial accessors / 3-line
          __init__s share a high FRACTION of their tiny support with anything, smearing into one
          blob. The Agda tool's lesson: small things look similar because they're small. Gate them.
        min_cohesion: after union-find, drop clusters whose MEDIAN intra-pair shared-fraction is
          below this -- defends against weak-chain smearing (a chain of marginal pairs is not a
          clique). The Agda cluster.py cohesion floor, ported."""
        idx = [i for i, u in enumerate(self.units) if len(u.support) >= min_size]
        parent = {i: i for i in idx}
        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]; x = parent[x]
            return x
        def union(a, b):
            ra, rb = find(a), find(b)
            if ra != rb: parent[ra] = rb
        for ii in range(len(idx)):
            for jj in range(ii + 1, len(idx)):
                i, j = idx[ii], idx[jj]
                if self.shared_fraction(self.units[i], self.units[j]) >= min_shared:
                    union(i, j)
        comp: dict[int, list] = {}
        for i in idx:
            comp.setdefault(find(i), []).append(i)
        out = []
        for c in comp.values():
            if len(c) <= 1:
                continue
            if min_cohesion > 0.0:
                pairs = [self.shared_fraction(self.units[a], self.units[b])
                         for x, a in enumerate(c) for b in c[x+1:]]
                med = sorted(pairs)[len(pairs)//2] if pairs else 0.0
                if med < min_cohesion:
                    continue
            out.append(c)
        return sorted(out, key=lambda c: -len(c))

    def extract_candidates(self, min_fanin: int = 3, min_size: int = 3) -> list[tuple]:
        """Canonical subtrees referenced by many units = parametric-helper candidates (the apex
        signal: >= min_fanin instances of a non-trivial motif -> a parametric apex should exist).
        Returns (node_id, fanin, size, head) sorted by fanin*size (impact)."""
        out = []
        for nid in range(self.I.size()):
            fi = self.I.fanin[nid]
            sz = len(self._support(nid))
            if fi >= min_fanin and sz >= min_size:
                nn = self.I.nodes[nid]
                out.append((nid, fi, sz, (nn.kind, nn.op, nn.lit)))
        return sorted(out, key=lambda t: -(t[1] * t[2]))


def expand(paths_or_globs: list[str]) -> list[str]:
    out = []
    for p in paths_or_globs:
        if any(ch in p for ch in "*?["):
            out.extend(glob_mod.glob(p, recursive=True))
        else:
            out.append(p)
    return sorted(set(out))


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Multi-scale structural similarity over Python via the term-algebra interner "
                    "(the Agda similarity script, for Python). Units = def/class; sharing = SPPF fan-in.")
    ap.add_argument("files", nargs="*", help="Python files or globs")
    ap.add_argument("--min-shared", type=float, default=0.6,
                    help="cluster threshold: min shared-support fraction (default 0.6)")
    ap.add_argument("--min-size", type=int, default=6,
                    help="ignore units with support smaller than this (trivial-accessor gate, default 6)")
    ap.add_argument("--min-cohesion", type=float, default=0.5,
                    help="drop clusters whose median intra-pair share is below this (weak-chain floor, default 0.5)")
    ap.add_argument("--min-fanin", type=int, default=3,
                    help="extract-candidate threshold: min units sharing a subtree (default 3)")
    ap.add_argument("--clusters", action="store_true", help="report unit clusters")
    ap.add_argument("--extract", action="store_true", help="report extract (parametric-helper) candidates")
    ap.add_argument("--recursive", action="store_true",
                    help="report shared structure INSIDE residue (interior-node fan-in = recursive template)")
    ap.add_argument("--skeleton", action="store_true",
                    help="typehole each cluster: shared skeleton + typed holes (the common semantics + the distinctions)")
    ap.add_argument("--metalanguage", action="store_true",
                    help="compute the corpus's implicit metalanguage: generators (alphabet) + cocycles (idioms) vs coboundary (derivable redundancy)")
    ap.add_argument("--json", action="store_true",
                    help="machine-readable output (the LLM accelerator: run once, parse, don't re-derive)")
    args = ap.parse_args(argv)

    files = expand(args.files)
    if not files:
        ap.error("no input files")

    C = Corpus()
    for f in files:
        C.add_file(f)

    cls = C.clusters(args.min_shared, args.min_size, args.min_cohesion)
    scores = C.genericization()

    if args.json:
        import json
        out = {"corpus": {"units": len(C.units), "files": len(files), "nodes": C.I.size()},
               "genericization": {k: {"shared": s, "total": t, "ratio": r} for k, (s, t, r) in scores.items()},
               "verdict": C.verdict(scores), "clusters": []}
        for comp in cls:
            roots = [C.units[ui].root for ui in comp]
            th = C.typehole(roots)
            out["clusters"].append({
                "units": [f"{C.units[ui].path}::{C.units[ui].name}:{C.units[ui].lineno}" for ui in comp],
                "verdict": C.typehole_verdict(th),
                "skeleton": th})                                   # the full typehole tree, machine-readable
        print(json.dumps(out, indent=2))
        return 0

    print(f"corpus: {len(C.units)} units across {len(files)} file(s); forest {C.I.size()} interned nodes")
    print("\ngenericization (shared / total per scale):")
    for scale, (sh, tot, r) in scores.items():
        print(f"  {scale:<22} {sh:>6} / {tot:<6}  {r*100:5.1f}% shared")
    print(f"verdict: {C.verdict(scores)}")

    # the PRIMARY readout: typehole each cluster -> shared skeleton + typed holes + verdict.
    # (the common semantics underneath them = the skeleton; the distinctions = the typed holes.)
    if args.clusters or args.skeleton or not (args.extract or args.recursive or args.metalanguage):
        print(f"\nclusters (units sharing >= {args.min_shared:.0%} support) -- typeholed:")
        if not cls:
            print("  (none -- no units share enough structure; healthy if these are distinct routines)")
        for ci, comp in enumerate(cls):
            roots = [C.units[ui].root for ui in comp]
            th = C.typehole(roots)
            # durable handles: path::name:line, stable across runs
            print(f"\n  cluster {ci} ({len(comp)} units) -- {C.typehole_verdict(th)}")
            for ui in comp:
                u = C.units[ui]
                print(f"    {u.path}::{u.name}:{u.lineno}")
            print("    -- common semantics (skeleton) + distinctions (typed holes):")
            for line in C.render_typehole(th).splitlines():
                print(f"      {line}")

    if args.extract:
        cand = C.extract_candidates(args.min_fanin)
        print(f"\nextract candidates (subtrees in >= {args.min_fanin} places, the apex signal):")
        if not cand:
            print("  (none -- no motif is repeated enough to warrant a parametric helper)")
        for nid, fi, sz, head in cand[:20]:
            print(f"  node {nid:<5} fanin {fi:<3} size {sz:<3} head {head}")

    if args.recursive:
        rec = C.recursive_shared(min_units=2, min_depth=1)
        print(f"\nrecursive shared structure (interior nodes shared across units = the recursive template):")
        if not rec:
            print("  (none -- no shared structure hides inside unit residue)")
        for nid, nu, md, head in rec[:20]:
            print(f"  node {nid:<5} in {nu:<3} units  depth {md:<3} head {head}")

    if args.metalanguage:
        ch = C.cohomology(min_units=2)
        s = ch["summary"]
        def hdr(h):
            return h[0] + (f"[{h[3]}]" if h[3] else "") + (f"({h[2]})" if h[2] else "")
        print(f"\n=== the corpus's implicit METALANGUAGE (computed cohomology) ===")
        print(f"  alphabet (generators): {s['alphabet_size']}   idioms (cocycles): {s['idiom_count']}"
              f"   derivable (coboundary): {s['coboundary_count']}")
        print(f"  metalanguage size = {s['metalanguage_size']} of {s['total_shared']} shared "
              f"({100*s['metalanguage_size']/max(1,s['total_shared']):.0f}%); "
              f"the rest is coboundary redundancy (cleanup removes it)")
        print(f"\n  ALPHABET -- the words the corpus is written in (top generators by use):")
        for nid, u, sz, head, ex in ch["generators"][:15]:
            print(f"    {hdr(head):<28} used by {u:>4} units")
        print(f"\n  IDIOMS -- cocycles: compositions shared MORE than their parts explain (the real abstractions):")
        for nid, u, sz, head, ex in ch["cocycles"][:20]:
            print(f"    {hdr(head):<28} in {u:>3} units, size {sz:<3}, excess {ex:>3}  (node {nid})")
        if not ch["cocycles"]:
            print("    (none -- all shared composites are coboundary; the corpus speaks only in generators)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
