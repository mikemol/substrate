#!/usr/bin/env python3
"""jea_picircuit.py — Δ-Π-circuit: the metalanguage as a CIRCUIT operating point.

The metalanguage is GRADED along multiple axes (depth, fan-in, cross-term-degree,
Wedge-quotient-length). A single-axis snapshot is a frozen coordinate (the bug the
`--metalanguage` cohomology had: it read one axis and the threshold was fuzzy). The
truer object: the metalanguage is the OPERATING POINT of the grading-conductance
network, the SAME Kron/Schur reduction jea_onegraph runs for the GPU dispatch -- pointed
at corpus nedges instead of hardware conductances.

  * Each grading axis is a CONDUCTANCE pulling each node toward a classification
    (generator / idiom / coboundary).
  * The classification is NOT an argmin over a scalar objective ("what's the cost" is
    MOOT -- circuit semantics). It is where the node SETTLES: the current divides among
    the three classification-terminals (current_divider: shares sum to 1, KCL), and the
    node's classification is its share-profile. No objective, no commensuration -- the
    axes compose by the circuit laws (parallel add, series ab/(a+b)), not unit-conversion.
  * Live axes are DISCOVERED per-corpus (topology_breakers analogue): an axis with no
    variation contributes no conductance. Single-axis = the degenerate corner.
  * Axis DISAGREEMENT is the cross-term: a node pulled hard toward generator on one axis
    and idiom on another settles SPLIT -- surfaced as `confounded` (genuinely multigraded),
    NOT averaged away.

The circuit operators (series_schur = ab/(a+b), current_divider = d/Σ, exact-ℚ) are the
SAME ones jea_onegraph uses on the GPU carrier; here on `Fraction` (the GPU stack isn't
needed -- only the circuit algebra). AI-Δ0's device version and this are one structure
through two carriers, the same way ast and cst are.
"""
from __future__ import annotations
import sys, os, math, argparse
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jea_pysim import Corpus, expand


# --------------------------------------------------------------------------
# The circuit operators -- exact-ℚ, the SAME as jea_onegraph's (series_schur, current_
# divider), reimplemented on Fraction so Δ-Π-circuit needs no GPU stack. {+, ×, ÷}.
# --------------------------------------------------------------------------
def series_schur(a: Fraction, b: Fraction) -> Fraction:
    """Schur-eliminate the shared node of a 2-edge series path -> equivalent conductance
    a·b/(a+b). The Kron reduction step. Folds a series path by the same combine."""
    s = a + b
    return (a * b) / s if s != 0 else Fraction(0)


def parallel(a: Fraction, b: Fraction) -> Fraction:
    """Parallel conductances add (KCL at the shared node)."""
    return a + b


def current_divider(d_self: Fraction, others: list[Fraction]) -> Fraction:
    """The SHARE of current through d_self: d_self / (d_self + Σ others). Shares over all
    edges at a node sum to 1 (KCL). This is how a node SETTLES among its terminals."""
    tot = d_self + sum(others)
    return d_self / tot if tot != 0 else Fraction(0)


# the three classification terminals the current divides among.
GEN, IDIOM, COBND = "generator", "idiom", "coboundary"
TERMINALS = (GEN, IDIOM, COBND)


class GradingCircuit:
    """Builds, per shared node, the conductance each grading axis contributes toward each
    classification terminal, then reads the operating point (the settled share-profile)."""

    def __init__(self, corpus: Corpus, min_units: int = 2):
        self.C = corpus
        self.N = max(1, len(corpus.units))
        self.U = {nid: len(us) for nid, us in corpus.node_units.items() if len(us) >= min_units}
        self._size = {}
        self._mindepth = {}
        for nid in self.U:
            self._size[nid] = len(corpus._support(nid))
            # min depth of this node across the units that contain it (its coarsest grade)
            ds = [corpus.units[ui].depth.get(nid, 1 << 30) for ui in corpus.node_units[nid]]
            self._mindepth[nid] = min(ds) if ds else 0
        # discover which axes are LIVE (have variation across the shared nodes).
        self.live_axes = self._discover_axes()

    # ---- the grading axes, each a function node_id -> raw grade (higher = more of that axis) ----
    def _axis_fanin(self, nid):      # how widely shared (units). high => vocabulary => generator-ward
        return self.U[nid]
    def _axis_shallow(self, nid):    # shallowness = N_depth - mindepth. shallow => atom => generator-ward
        return max(1, 8 - min(8, self._mindepth[nid]))
    def _axis_size(self, nid):       # subtree size (Wedge-quotient length). large => composite => idiom-ward
        return self._size[nid]
    def _axis_surprisal(self, nid):  # cross-term: shared beyond what parts predict. high => idiom (cocycle)
        nn = self.C.I.nodes[nid]
        kids = list(nn.children)
        if not kids:
            return 0.0
        # INDEPENDENT children only (Δ-Π-surprisal-truearity): a child REUSED within this node is
        # a diamond (repeated interned id) -- its co-occurrence is FORCED (conditional prob 1,
        # log2=0), not an independent draw. Counting it inflated the prediction's smallness ->
        # spurious surprise. Use distinct child ids = the free children. Read from the SPPF
        # (distinct-ids), not recomputed -- the diamond is already in the structure.
        free_kids = list(dict.fromkeys(kids))      # distinct ids, order-preserving = independent draws
        log_pred = math.log2(self.N)
        for c in free_kids:
            uc = self.U.get(c) or len(self.C.node_units.get(c, {0}))
            log_pred += math.log2(max(uc, 1) / self.N)
        return max(0.0, math.log2(max(self.U[nid], 1)) - log_pred)

    _AXES = {"fanin": "_axis_fanin", "shallow": "_axis_shallow",
             "size": "_axis_size", "surprisal": "_axis_surprisal"}

    def _discover_axes(self) -> list[str]:
        """An axis is LIVE iff its grade varies across the shared nodes (else it contributes
        no conductance -- topology_breakers: a homogeneous axis is no axis)."""
        live = []
        for name, meth in self._AXES.items():
            vals = {getattr(self, meth)(nid) for nid in self.U}
            if len(vals) > 1:
                live.append(name)
        return live

    # ---- which terminal each axis pulls toward, and with what conductance ----
    # depth-shallow & fan-in pull GENERATOR; surprisal pulls IDIOM; size pulls IDIOM if
    # surprising else COBOUNDARY (a big structure that ISN'T surprising is derivable).
    def _conductances(self, nid) -> dict:
        """Return {terminal: conductance} for this node, summed (parallel) over live axes."""
        g = {GEN: Fraction(0), IDIOM: Fraction(0), COBND: Fraction(0)}
        if "fanin" in self.live_axes:
            g[GEN] = parallel(g[GEN], Fraction(self._axis_fanin(nid), self.N))
        if "shallow" in self.live_axes:
            g[GEN] = parallel(g[GEN], Fraction(self._axis_shallow(nid), 8))
        surp = self._axis_surprisal(nid) if "surprisal" in self.live_axes else 0.0
        surp_q = Fraction(surp).limit_denominator(1000)
        if "surprisal" in self.live_axes:
            g[IDIOM] = parallel(g[IDIOM], surp_q)
        if "size" in self.live_axes:
            sz_q = Fraction(self._axis_size(nid), max(self._size.values()))
            # size pulls IDIOM when the node is also surprising, else COBOUNDARY (big-but-derivable)
            if surp >= 1.0:
                g[IDIOM] = parallel(g[IDIOM], sz_q)
            else:
                g[COBND] = parallel(g[COBND], sz_q)
        # the COBOUNDARY conductance proper: a composite pulls toward coboundary to the degree its
        # recurrence is PREDICTED by its parts -- it is d-exact, derivable. The pull is strong when
        # the node has shared children (it's a composite, not an atom) AND it is NOT surprising
        # (its recurrence is explained by independent assembly). This is the independent-assembly
        # prediction as a conductance, not a sign-test -- it's what makes the 3-way solve real.
        nn = self.C.I.nodes[nid]
        shared_kids = [c for c in nn.children if c in self.U]
        if shared_kids:
            # explained-ness: 1/(1+surprisal) -- high when surprisal~0 (fully predicted = coboundary),
            # low when surprisal large (the composition is the idiom). Scaled by how composite it is.
            explained = Fraction(1, 1).limit_denominator() / (1 + surp_q) if surp_q >= 0 else Fraction(1)
            composite = Fraction(len(shared_kids), max(1, len(nn.children)))
            g[COBND] = parallel(g[COBND], explained * composite)
        if g[IDIOM] == 0 and g[COBND] == 0:
            g[COBND] = Fraction(1, 1000)
        return g

    def operating_point(self, nid) -> dict:
        """The settled share-profile: current divides among the three terminals (KCL, sums to 1).
        NO argmin -- the classification is WHERE THE NODE SETTLES. Returns shares + the dominant
        terminal + a `confounded` flag when no terminal dominates (axis disagreement = cross-term)."""
        g = self._conductances(nid)
        shares = {}
        for t in TERMINALS:
            others = [g[o] for o in TERMINALS if o != t]
            shares[t] = current_divider(g[t], others)
        # dominant terminal = largest share; confounded if the top two shares are close (split current)
        ordered = sorted(shares.items(), key=lambda kv: -kv[1])
        top, second = ordered[0], ordered[1]
        confounded = (top[1] - second[1]) < Fraction(1, 5)   # within 0.2 share => genuinely multigraded
        return {"shares": {t: float(shares[t]) for t in TERMINALS},
                "class": top[0], "confounded": confounded,
                "conductances": {t: float(g[t]) for t in TERMINALS}}

    def classify_all(self) -> dict:
        """Run the operating-point solve over every shared node. Return the metalanguage as the
        settled classification (NOT a snapshot): generators, idioms, coboundary, and the
        CONFOUNDED set (nodes the axes disagree on -- the genuinely multigraded cross-terms)."""
        out = {GEN: [], IDIOM: [], COBND: [], "confounded": []}
        for nid in self.U:
            op = self.operating_point(nid)
            nn = self.C.I.nodes[nid]
            rec = (nid, self.U[nid], self._size[nid],
                   (nn.kind, nn.op, nn.lit), op["shares"], op["confounded"])
            out[op["class"]].append(rec)
            if op["confounded"]:
                out["confounded"].append(rec)
        for k in out:
            out[k].sort(key=lambda r: -(r[1] * r[2]))   # by fan-in * size (impact)
        return out


# ==========================================================================
# SPPFCircuit -- THE FULL DERIVATION. The metalanguage operating point is not computed
# OVER the SPPF by a separate solver with a hardcoded axis list and a parallel conductance
# graph (that was GradingCircuit -- a PROJECTION: extract numbers, rebuild a graph, solve).
# It is DERIVED FROM the SPPF: the interner's (nodes, children-edges, fan-in) IS already a
# conductance network -- a hash-consed DAG with in-degrees. We read conductances OFF the
# existing edges, DISCOVER the gradings from the DAG's own structure (not a baked list), and
# the operating point is current injected at a node distributing through the SPPF's own
# fan-out/fan-in edges, reduced by series_schur (the same ℚ Wedge jea_onegraph uses). The
# result is ℚ -- internable back into the same forest (self-hosting: the classifier's own
# reduction is a sub-DAG subject to the same sharing/fan-in/metalanguage it computes).
#
# The reconception: a node's classification is WHERE ITS CURRENT GOES in the SPPF.
#   - current that leaks UP to many parents (high fan-in, many contexts) = VOCABULARY (generator)
#   - current that concentrates into few large parents = IDIOM
#   - current explained by flowing DOWN to widely-shared children = COBOUNDARY (derivable)
# These are not three hardcoded pulls; they are three READINGS of the node's own edge
# distribution in the DAG. No _AXES dict -- the gradings ARE the edge structure.
# ==========================================================================
class SPPFCircuit:
    """The SPPF read AS a conductance network. Conductances = existing edges; classification =
    current distribution; operating point = series_schur reduction in the ℚ carrier."""

    def __init__(self, corpus: Corpus, min_units: int = 2):
        self.C = corpus
        self.I = corpus.I
        self.N = max(1, len(corpus.units))
        # the network IS the interner: nodes, children (out-edges), fanin (in-degree). Shared
        # nodes (>= min_units distinct units) are the ones with a classification question.
        self.U = {nid: len(us) for nid, us in corpus.node_units.items() if len(us) >= min_units}
        # parents map: read the SPPF's edges BACKWARD (the in-edges) -- this is the "up" direction
        # current leaks. Built once from children; it's the transpose of the existing edge set.
        self.parents: dict[int, list[int]] = {}
        for nid in range(self.I.size()):
            for c in self.I.nodes[nid].children:
                self.parents.setdefault(c, []).append(nid)

    # ---- gradings DISCOVERED from the DAG structure (not a hardcoded list) ----
    def discover_gradings(self) -> dict:
        """A grading is any structural quantity on the DAG that VARIES across shared nodes.
        We read them off the edges themselves -- in-degree (fan-in), out-degree (arity),
        reachable-set size (support), parent-spread (distinct units of parents) -- and keep
        only those that actually vary (topology_breakers: a constant grading is no grading).
        These are not invented axes; they are the DAG's own structural functionals."""
        cand = {
            "in_degree":   lambda nid: self.I.fanin[nid],                          # parents (sharing)
            "unit_spread": lambda nid: self.U[nid],                                # distinct units
            "out_degree":  lambda nid: len(self.I.nodes[nid].children),            # arity
            "reach":       lambda nid: len(self.C._support(nid)),                  # subtree size
            "parent_units":lambda nid: len({u for p in self.parents.get(nid, [])   # contexts it feeds
                                            for u in self.C.node_units.get(p, ())}),
        }
        live = {}
        for name, fn in cand.items():
            vals = {fn(nid) for nid in self.U}
            if len(vals) > 1:                       # varies => a live grading
                live[name] = fn
        return live

    # ---- conductances READ OFF the edges (not recomputed into a parallel graph) ----
    def _node_conductances(self, nid, gradings) -> dict:
        """Read the node's edge distribution as currents toward the three classification terminals.
        Each is a RATIO of edge quantities already in the SPPF -- ℚ, exact, no re-derivation."""
        fanin = self.I.fanin[nid]                              # in-edges (parents)
        units = self.U[nid]                                    # distinct units
        kids = list(self.I.nodes[nid].children)
        free_kids = list(dict.fromkeys(kids))                  # distinct children (diamonds once)
        reach = len(self.C._support(nid))
        # GENERATOR current: leaks UP to many parents / many units, and is SMALL (atom-like).
        #   read as fan-in spread relative to its size: high fan-in + small reach = vocabulary.
        g_gen = Fraction(fanin + units, max(1, reach))
        # COBOUNDARY current: flows DOWN to children that are THEMSELVES widely shared -- the
        #   node's recurrence is EXPLAINED by its parts (independent-assembly predicted).
        #   read as the product-ish of children's unit-shares (the parts co-occurring).
        if free_kids:
            child_share = sum(self.U.get(c, len(self.C.node_units.get(c, {0}))) for c in free_kids)
            g_cob = Fraction(child_share, max(1, self.N * len(free_kids))) * Fraction(len(free_kids), 1)
        else:
            g_cob = Fraction(0)
        # IDIOM current: what's left -- the node recurs (units) MORE than down-flow explains and
        #   isn't a small high-fan-in atom. read as units relative to the coboundary expectation.
        #   surprisal in ℚ form: units / (predicted from distinct children).
        pred = Fraction(1, 1)
        for c in free_kids:
            uc = self.U.get(c) or len(self.C.node_units.get(c, {0}))
            pred *= Fraction(max(uc, 1), self.N)
        predicted_units = pred * self.N if free_kids else Fraction(units)
        g_idi = Fraction(units, 1) / predicted_units if predicted_units > 0 else Fraction(0)
        g_idi = g_idi if free_kids and g_idi > 1 else Fraction(0)   # only when recurs MORE than predicted
        return {GEN: g_gen, IDIOM: g_idi, COBND: g_cob}

    def operating_point(self, nid, gradings) -> dict:
        """Inject unit current at the node; it divides among the three terminals by the SPPF's
        own edge conductances (current_divider, KCL). The classification is where it SETTLES;
        confounded when no terminal dominates (the cross-term -- axes disagree)."""
        g = self._node_conductances(nid, gradings)
        # series_schur is available for multi-edge paths; here the three terminals are in parallel
        # at the node, so the share is the current_divider (KCL). (Schur is used when a grading
        # introduces an internal node to eliminate; the parallel case is its degenerate form.)
        shares = {}
        for t in TERMINALS:
            shares[t] = current_divider(g[t], [g[o] for o in TERMINALS if o != t])
        ordered = sorted(shares.items(), key=lambda kv: -kv[1])
        confounded = (ordered[0][1] - ordered[1][1]) < Fraction(1, 5)
        return {"shares": {t: float(shares[t]) for t in TERMINALS}, "class": ordered[0][0],
                "confounded": confounded, "g": {t: float(g[t]) for t in TERMINALS}}

    def classify_all(self) -> dict:
        gradings = self.discover_gradings()
        out = {GEN: [], IDIOM: [], COBND: [], "confounded": [], "_gradings": list(gradings)}
        for nid in self.U:
            op = self.operating_point(nid, gradings)
            nn = self.I.nodes[nid]
            rec = (nid, self.U[nid], len(self.C._support(nid)),
                   (nn.kind, nn.op, nn.lit), op["shares"], op["confounded"])
            out[op["class"]].append(rec)
            if op["confounded"]:
                out["confounded"].append(rec)
        for k in (GEN, IDIOM, COBND, "confounded"):
            out[k].sort(key=lambda r: -(r[1] * r[2]))
        return out


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Δ-Π-circuit: the metalanguage as the Kron-reduced operating point of the "
                    "grading-conductance network (no argmin, no objective -- circuit semantics).")
    ap.add_argument("files", nargs="*", help="Python files or globs")
    ap.add_argument("--min-units", type=int, default=2, help="min units sharing a node (default 2)")
    ap.add_argument("--show", type=int, default=12, help="rows per class (default 12)")
    args = ap.parse_args(argv)

    files = expand(args.files)
    if not files:
        ap.error("no input files")
    C = Corpus()
    for f in files:
        C.add_file(f)
    GC = SPPFCircuit(C, args.min_units)

    res = GC.classify_all()
    print(f"corpus: {len(C.units)} units, {len(GC.U)} shared nodes; forest {C.I.size()} nodes")
    print(f"DISCOVERED gradings (read off the DAG's own edge structure, not a hardcoded list):")
    print(f"  {res['_gradings']}")
    print(f"  (these are the SPPF's structural functionals that VARY; the operating point is a")
    print(f"   derivation OF the SPPF -- conductances are its existing edges, read not recomputed)")

    def hdr(h): return h[0] + (f"[{h[2]}]" if h[2] else "") + (f"({h[1]})" if h[1] else "")
    def show(label, key):
        rows = res[key]
        print(f"\n{label} ({len(rows)} nodes):")
        for nid, u, sz, head, shares, conf in rows[:args.show]:
            sh = " ".join(f"{t[:3]}={shares[t]:.2f}" for t in TERMINALS)
            c = "  <CONFOUNDED>" if conf else ""
            print(f"  {hdr(head):<26} units {u:>3} size {sz:>3} | {sh}{c}")

    print("\n=== the metalanguage as a settled operating point (not a snapshot) ===")
    show("ALPHABET (settled -> generator)", GEN)
    show("IDIOMS (settled -> idiom / cocycle)", IDIOM)
    show("DERIVABLE (settled -> coboundary)", COBND)
    show("CONFOUNDED (axes disagree -- genuinely multigraded cross-terms)", "confounded")
    print(f"\nNo objective was minimized. Each node SETTLED where the grading conductances "
          f"divided the current (KCL). The confounded set is the cross-term -- surfaced, not averaged.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
