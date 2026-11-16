#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""The ingest pipeline as a GRAPHVIZ FLOW — generated from the declarations, never drawn.

⚑⚑⚑ WHY THIS EXISTS. The operator, 2026-08-15, reading a status report: *"I can't follow
everything that's going on any more."* That is a legible failure of the REPORTING, not of the
reader — the pipeline's state had been arriving as prose sentences over many turns, each true and
none composable, and the immediately preceding sentence ("the sandbox is mid-drain, so its residue
is genuinely empty") was an INFERENCE from two row counts dressed as a measurement.

⚑⚑ SO EVERY NODE AND EDGE HERE IS READ FROM A DECLARATION OR THE STORE, and nothing is typed:

  · the STAGES come from `lifecycle.LIFECYCLE` — the one Chain the whole pipeline is a slice of;
  · the RELATIONS and their tier grouping come from `schema_decl._TIERS`;
  · the LIVE / SANDBOX row counts come from `schema_diag.census`, which already distinguishes
    ABSENT (`-`) from EMPTY (`0`) — a distinction this diagram must preserve, because "the tier
    was never applied" and "the tier is applied and empty" look identical in prose and are the
    two states this arc kept confusing;
  · the WRITERS come from `pycodemod`'s own relation census, so a new writer appears with no
    edit here.

⚑ A HAND-DRAWN DIAGRAM WOULD BE THE `toolmodes` DEFECT IN PICTURE FORM — a roster beside the
declaration, correct on the day it was drawn. The rule this repo states for tables applies to
pictures: generate it, or it rots.

    pipeflow.py                      # DOT to stdout, live counts
    pipeflow.py --sandbox            # the throwaway tenant instead
    pipeflow.py --no-counts          # structure only; no store connection at all
    pipeflow.py --out FILE.svg       # render via `dot` if it is on PATH
    pipeflow.py --engine <name>       # layout engine (default `dot`). The right engine is a
                                     # property of the QUESTION: `dot` for "what flows into
                                     # what", `fdp` for "what clusters near what".
    pipeflow.py --no-builders        # tier flow ALONE, without the 81-builder splice layer.
                                     # ⚑ An OFF switch, not an opt-in: the operator asked for
                                     # all the builders, so all of them is the default. This is
                                     # for when that layer is noise for the question at hand.
    pipeflow.py --rendered           # ⚑⚑ DID THE STYLING REACH THE PICTURE? A valid DOT
                                     # attribute graphviz does not implement is ACCEPTED, exits
                                     # 0, and renders as the default — so reading the DOT can
                                     # never reveal it. This renders to SVG and compares the
                                     # DECLARED palette against the strokes that actually exist.
    pipeflow.py --ranks [--builders] # the layout's RANK census: how many distinct y-ranks the
                                     # engine produced, and which nodes sit on each. ⚑ ONE rank
                                     # holding everything is the failure this exists to see —
                                     # the layout has no dependency information to order by.
                                     # `--builders` narrows it to builder nodes; the DEFAULT is
                                     # every node kind, because the builders cannot stack until
                                     # their INPUTS do, so a census blind to the relations
                                     # cannot locate the flattening.
    pipeflow.py --help               # this block (also printed on a bare run)
    pipeflow.py --selftest

⚑⚑⚑ THE FOOTPRINT IS DEBT, AND IT IS THE DEBT THE SPPF-IN-POSTGRES EXISTS TO RETIRE
(operator, 2026-08-15: *"And we return to why we're interning code into an SPPF within
postgresql in the first place."*). This module answers structural questions about the
python corpus by asking `pycodemod` to PARSE IT — five whole-corpus passes per graph
build. Measured: 331s and over 192MB, which OOM-killed the suite under its membudget
lease; it fits at 256MB and needs 147s after a shared scan and a bounded parse cache.

⚑⚑ AND EVERY OPTIMISATION IN THAT PARAGRAPH IS A HAND-ROLLED PIECE OF THE THING THE
STORE ALREADY IS. A parsed-tree cache keyed on (path, mtime, size), evicted LRU, held in
process memory, rebuilt from scratch each run — that is an intern table with a staleness
key and no persistence. `obs`/`edge`/`event` hold interned nodes WITH SHARING, survive
the process, and answer by query rather than by residency. The reason this file is heavy
is that it re-derives, per run, a structure the substrate is built to hold.

⚑ SO THE 256MB IS RECORDED AS A CEILING TO PAY DOWN, not a lease to raise. `membudget`'s
own refusal states both options and says which is which: *"Raising the lease is one
answer; the other is that its footprint is debt."* The paydown is routing these queries
through the store instead of libcst — which is the arc this whole session is inside.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(REPO, "jea", "metalanguage"))
sys.path.insert(0, HERE)
# ⚑ THE PYTHON-WRITER HALF OF THE GRAPH IS A `pycodemod` QUERY, so the tool that owns
# `.py` is the authority here exactly as `query_defs` is for the builders. `values`
# with an ORDINAL reads `upsert(con, <relation>, rows)`'s positional relation slot —
# the mode that did not exist until this file needed it.
import _pycodemod_query as _pycodemod
# ⚑⚑⚑ ⟡callers-of-builder — `py_files` LIVES IN `_pycodemod_core`, NOT `_pycodemod_query`, AND
# THIS IMPORT DID NOT SAY SO. Every mode reaching `_py_files(...)` died with
# `AttributeError: module '_pycodemod_query' has no attribute 'py_files'` — MEASURED on
# `pipeflow --consumers`, which is the mode that answers *"which function calls
# `QB.run(con, '<builder>')`"*. A pycodemod module split moved the file-walker and this consumer
# was not rewired: the SAME dangling-import class as ⟡dangling-46 in the Agda tree, one layer up
# in the tooling that finds it there.
#
# ⚑⚑ AND ITS ABSENCE COST A DIAGNOSIS THE SAME DAY. Hunting an unscoped `event_head` (⟡Ⓐ9k), I
# needed exactly this mode, found it broken, and fell back to guessing call sites by name —
# three wrong models in a row (`--ingest-core`, `project_ref`, `finalize_db`) before the
# structural answer came from `query_defs --touching`. A broken reader is not a missing
# capability, and it reads as one.
#
# ⚑ THE FIX IS AT THE CALL SITES, NOT A PATCH ON THE MODULE. A first cut did
# `_pycodemod.py_files = _pmc.py_files` — mutating another module's namespace, which changes what
# EVERY importer of `_pycodemod_query` sees and hides the split rather than resolving it. Import
# the real home and name it; the knowledge of where the walker lives belongs at the import, not
# smuggled into a shared namespace at runtime.
#
# ⚑ TWO SYMBOLS, ONE SPLIT — `py_files` AND `UNKNOWN`, both now in `_pycodemod_core`. The second
# surfaced only after the first was fixed, which is what a broken module boundary looks like from
# the consumer side: one AttributeError at a time, each hiding the next.
from _pycodemod_core import py_files as _py_files, UNKNOWN as _UNKNOWN

class Graph:
    """The pipeline as a VALUE — nodes, edges, and their kinds — serialized to DOT on demand.

    ⚑⚑⚑ ANALYSIS → GRAPH → DOT, AND SKIPPING THE MIDDLE TERM IS WHAT BROKE EVERY QUERY IN
    THIS ARC (operator, 2026-08-15: *"You should construct the graph, and then serialize the
    graph. Right now, you're going straight from analysis to dot, and that's creating
    problems."*). With DOT text as the only representation, every question about the graph
    had to be answered by re-parsing the text I had just written:

      · `--cycles` re-parsed edges out of the source, and worked only against my own
        one-edge-per-line formatting — the 3-cycle fixture returned 0 because `a -> b; b ->
        c;` is legal DOT and my reader could not see it. A detector that cannot be exercised
        by a fixture is not a detector.
      · `--edges` classified an edge's KIND by its COLOUR (`"#8899aa" in ln`), i.e. recovered
        a semantic fact from a presentation choice. Restyling silently rewrites the census.
      · the constraint census counted the substring `constraint=false` across lines.

    ⚑⚑ EACH OF THOSE IS THE SAME DEFECT THE STANDING RULE NAMES, committed against my own
    output: a textual query over a structured artifact. The artifact happened to be one I
    generated, which made it feel different and made it worse — I owned both ends and still
    round-tripped through text.

    ⚑ SO KIND IS CARRIED, NOT INFERRED. An edge knows it is a `read` / `flow` / `write`;
    the colour is chosen AT SERIALIZATION from the kind. Queries read the structure and the
    picture is one of its renderings, so a restyle cannot move a number.
    """

    def __init__(self):
        self.nodes = {}          # id -> {label, kind, **attrs}
        self.edges = []          # (src, dst, kind, **attrs)
        # ⚑⚑⚑ CLUSTERS, WHICH THIS FILE SPENT A DAY ARGUING AGAINST — and the argument
        # was right about the case it was made for. A cluster around ~80 builders is a
        # CONTAINMENT constraint that drags them into one rectangle and forces every edge
        # across a single boundary, which is what produced the wall of parallel curves.
        #
        # ⚑⚑ A CLUSTER OF EXACTLY TWO NODES IS THE OPPOSITE INSTRUMENT. The operator:
        # *"put the split orbit_node nodes in a cluster together… the cluster itself will
        # create a path between them for the return edge to route through. And it turns
        # orbit_node into a persistence swimlane."* The identity edge is unconstrained, so
        # `dot` gives it no corridor and it swings across the whole diagram — the ①②③④⑤
        # path. A two-member cluster supplies exactly the local channel it lacks.
        #
        # ⚑ SO THE RULE IS ABOUT SIZE AND MEMBERSHIP, NOT ABOUT CLUSTERS. Containment
        # distorts in proportion to what it contains; a cluster whose members are ONE
        # RELATION AT TWO TIMES contains a thing that is already one thing. Nothing else
        # goes in, which is what keeps it a swimlane rather than a box.
        self.clusters = {}       # id -> {label, members: [node ids]}

    def split_rest_points(self, at_rest=None):
        """Split the DATA-AT-REST relation on each cycle into read-from / written-to halves.

        ⚑⚑⚑ NOT EVERY RELATION ON THE CYCLE — ONLY THE ONES ACTUALLY AT REST (operator:
        *"Not every relation. Only the relations that are actually at rest… some of those
        relations are on ephemeral data"*). My first cut split the first relation it found
        on a loop, which invents a before/after for data that never rested: a projection
        rebuilt from its source holds nothing between steps, so "after `_node`" names no
        state — the same category error as splitting the FUNCTION, one noun over.

        ⚑⚑ AND THE PREDICATE IS DECLARED, NOT INVENTED. `lifecycle.LIFECYCLE`'s terminal
        link already draws this line: `reflected` = *"the SPPF + reverse index RECONSTRUCT
        this record — the staged copy is redundant and may be drained."* A relation that
        can be reconstructed from another is a CACHE; the relation it is reconstructed
        FROM is the rest point. `event`/`obs`/`edge` are at rest (append-only, nothing
        rebuilds them); `_node`/`node_child`/`obs_node`/the orbit tiers are projections
        the fold regenerates, which is why `--reclaim` can drop them at all.

        ⚑⚑ A CYCLE IS A TIME AXIS COLLAPSED, not a contradiction: `project_sppf` writes
        `_node` and reads it back through `q_project_stats` — one fold iterating, drawn
        as if both happened at once. Splitting the rest point breaks EVERY cycle through
        it at once, which a per-function split cannot: two different functions forming
        one loop are fixed by the same split.

        ⚑ AND A CYCLE WITH NO AT-REST RELATION IS LEFT ALONE, reported by `--cycles`
        rather than silently "fixed" by splitting whatever was convenient. That is a
        finding — either an ephemeral loop that wants a different fix, or a real one.
        """
        at_rest = at_rest or is_at_rest
        moved = set()
        for _ in range(8):                       # each split can expose another loop
            cycles = self.cycles()
            if not cycles:
                break
            rest = None
            for cyc in cycles:
                for n in cyc:
                    if self.nodes.get(n, {}).get("kind") == "relation" \
                            and not n.startswith("after_") and at_rest(n):
                        rest = n
                        break
                if rest:
                    break
            if rest is None:
                break
            aft = "after_" + rest
            if aft not in self.nodes:
                src = self.nodes[rest]
                self.nodes[aft] = dict(src, label="%s\\n⟳ AFTER this step" % src["label"],
                                       style="filled,dashed", penwidth="1.4")
            # every WRITE into the rest point lands in the after-copy; reads keep the
            # original, which is what makes the two perspectives distinct
            for i, (s, d, k, a) in enumerate(self.edges):
                if d == rest and k in ("write", "pywrite", "roundtrip"):
                    self.edges[i] = (s, aft, k, a)
            # ⚑⚑⚑ AND THE TWO HALVES ARE JOINED, UNCONSTRAINED (operator, 2026-08-16:
            # *"This is a good use case for constraint=false, drawing an edge from
            # orbit_node to the orbit_node that gets read from"*). The split leaves a
            # reader looking at `orbit_node` and `orbit_node ⟳ AFTER this step` as two
            # unrelated boxes — nothing on the page says they are ONE RELATION AT TWO
            # TIMES, which is the entire content of the split.
            #
            # ⚑⚑ AND THIS IS THE ONE PLACE THE RELAXATION IS NOT A WORKAROUND. Every
            # other `constraint=false` in this file's history was me declining to state
            # an ordering I had; this edge states an IDENTITY, and an identity has no
            # rank. Constraining it would re-close the cycle the split just opened —
            # after → before is precisely the back-edge that made the graph cyclic — so
            # the relaxation is what lets the claim be drawn at all.
            #
            # ⚑ DRAWN before→after, SO TIME RUNS DOWNWARD like every other edge here.
            # ⚑⚑⚑ CONSTRAINED, AND `rank=false` ALONE DID NOT STACK THEM. Measured by
            # `--ranks`: with the identity edge relaxed, `_unit` and `after__unit` both
            # sat at y=29.8 and `_node`/`after__node` both at y=15.0 — level, so the
            # return had no vertical channel no matter what the cluster declared. A
            # cluster attribute cannot create a rank difference that no edge asks for.
            #
            # ⚑⚑ AND CONSTRAINING IT IS SAFE HERE FOR A REASON THAT DOES NOT GENERALISE:
            # the edge runs between the only two members of its own cluster, so the rank
            # it forces is LOCAL to that lane and cannot push on the rest of the layout —
            # which is what every other `constraint=false` in this file was avoiding. The
            # cycle it would close is already excluded from the dependency walk, because
            # an identity is not a step data takes.
            #
            # ⚑ SO THE CLUSTER AND THE CONSTRAINT ARE ONE MECHANISM, not two. The cluster
            # bounds the blast radius; the constraint supplies the rank; together they
            # make the lane vertical and the return visible through it. Either alone is
            # inert — which is why the first cut, with the cluster but no constraint,
            # drew a lane with both halves side by side.
            #
            # ⚑⚑⚑ AND THE DIRECTION IS before→after, WHICH I HAD BACKWARDS. I drew
            # `after → before` reasoning about the READ ("the after-copy is what a later
            # step reads from"), and since the edge is what supplies the rank, that put
            # the written half ABOVE the one it is written from — time running upward
            # (operator: *"the 'AFTER' should be below the before; the nodes are reversed
            # in rank order"*). The reasoning was about the wrong end: what the edge
            # ORDERS is which half comes first, and the after-copy comes second by
            # definition. The read-back is the CYCLE, not this edge.
            self.edge(rest, aft, "sameas")
            # ⚑ THE TWO HALVES SHARE A CLUSTER — see `Graph.clusters`. It is the corridor
            # the unconstrained identity edge otherwise lacks, and it makes the relation
            # read as a PERSISTENCE SWIMLANE: one box, two states, the return path inside
            # it rather than looping across the diagram.
            self.clusters["rest_" + rest] = {
                "label": self.nodes[rest]["label"].split("\\n")[0],
                "members": [rest, aft],
            }
            moved.add(rest)
        # ⚑⚑ WHAT SURVIVES IS UNSPLITTABLE, SO ITS EDGES RELAX — decided HERE, after the
        # split, because only now is it known which loops remain. A caller predicting it
        # from the writer's durability relaxed an edge whose cycle the split had already
        # broken. The relaxation is earned per edge by a measurement, never by a forecast.
        # ⚑⚑⚑ AN EDGE INTO A LANE STAYS CONSTRAINED EVEN ON A CYCLE (operator, 2026-08-16:
        # *"That pink inbound line should be constraining; it's OK for the cluster to get
        # stretched vertically; that's what it's there for"*). The blanket relaxation
        # caught a `pywrite` whose endpoints both sit on the surviving cycle, so the write
        # entered the after-copy SIDEWAYS at the bottom of the lane instead of pulling
        # down into it — the producer floated free and the lane read as a box the write
        # happened to touch rather than the channel it lands in.
        #
        # ⚑⚑ AND STRETCHING IS THE LANE DOING ITS JOB, NOT A COST. I had been treating
        # vertical extent as damage to avoid — the same instinct that made me relax
        # everything in sight — but a persistence lane is precisely the thing that SHOULD
        # grow to accommodate what enters it. A cluster that refuses to stretch has to
        # push its inbound edges around itself instead.
        #
        # ⚑ SO THE EXEMPTION IS NARROWED TO EDGES BETWEEN TWO CYCLE NODES THAT ARE NOT A
        # LANE MEMBER. A cycle edge still relaxes; an edge ARRIVING AT a split half does
        # not, because its rank claim is what places the write inside the channel.
        #
        # ⚑⚑ MEASURED, AND THE PINK EDGE WAS NOT A CONSTRAINT PROBLEM AT ALL. `--edges`
        # named the four relaxed edges and every one was the uncommitted `core_fp` cycle;
        # the `pywrite` into `after__unit` was already constrained. `--ranks` found the
        # real fault: `p_sppf_db_project_sppf` sits at y=18.7 and `after__unit` at 26.1 —
        # THE WRITER IS RANKED BELOW THE THING IT WRITES, so its edge must travel upward
        # into the lane's bottom edge, which is what reads as entering sideways.
        #
        # ⚑ THE CAUSE IS THE `sameas` EDGE PULLING THE AFTER-COPY UP toward its before,
        # while the producer is placed by its OTHER outputs further down. Both claims are
        # honest; they simply disagree, and `dot` satisfies the shorter one. Naming it
        # here rather than forcing a rank: a `constraint` cannot fix a placement two
        # independent edges are arguing about, and the next edit should be measured
        # against `--ranks` rather than against the picture.
        _members = {m for c in self.clusters.values() for m in c["members"]}
        _left = {n for c in self.cycles() for n in c}
        for i, (s, d, k, a) in enumerate(self.edges):
            if s in _left and d in _left and d not in _members:
                self.edges[i] = (s, d, k, dict(a, constraint=False))
        return sorted(moved)

    def split_multistep_producers(self):
        """A producer writing tiers at DIFFERENT DEPTHS is several steps, not one node.

        ⚑⚑⚑ THE SAME SPLIT AS THE BEFORE/AFTER LANE, ON THE OTHER NOUN (operator,
        2026-08-16: *"This is exactly the same kind of split as the clustering-into-
        swimlane before/AFTER thing…and it's correct"*). A relation on a cycle is one
        thing at two TIMES; a producer writing six tiers at five depths is one function at
        several STEPS. Drawn as one node it gets a rank that satisfies none of its
        targets — measured: `project_sppf` sat at y=18.7 while `after__unit`, which it
        writes, sat at 26.1, so the write travelled UPWARD into the lane from underneath.
        That is not a routing artifact and no `constraint` or `weight` moves it, because
        the node's placement is a compromise between claims that genuinely disagree.

        ⚑⚑ THE CRITERION IS A PROPERTY OF THE CODE, NOT OF THE LAYOUT, and my first cut
        got this dangerously wrong (operator: *"You're risking recursive evaluation.
        Every thing you change changes rank, or could change rank. Especially once
        changes begin to have propagating behaviors"*). Splitting on MEASURED DEPTH means
        the split changes the graph, the graph changes the depths, and the criterion then
        disagrees with the split it just licensed — no fixpoint, and the outcome depends
        on evaluation order. A diagram whose content depends on how many times you ran
        the layout is not a measurement of anything.

        ⚑ SO THE SPLIT IS KEYED ON THE WRITE ORDER IN THE SOURCE — which `upsert` call
        comes first in the function body. That is a fact about the code, fixed before any
        node exists, and it is also the SEQUENCE the split is claiming: `project_sppf`
        writes `_node` before `node_child` before `unit_node` because the later rows
        reference the earlier ids. Reading it from the call sites states the step order
        the fold actually has, rather than inferring one from where a layout happened to
        put things.

        ⚑ AND THE PARTS SHARE A CLUSTER, exactly as the two halves of a rest point do:
        one function, several steps, drawn as a lane so the reader sees ONE writer moving
        down through the tiers rather than N unrelated boxes with the same name.
        """
        order = write_order()
        split = {}
        for pid in [n for n, v in self.nodes.items() if v["kind"] == "producer"]:
            _fn = self.nodes[pid]["label"].split("\\n")[0]
            _seq = order.get(_fn, {})
            tgt = [(d, _seq.get(d, 0)) for s, d, k, _a in self.edges
                   if s == pid and k == "pywrite"]
            # ⚑ ONE POSITION = ONE STEP. A producer whose writes all sit at the same
            # source position (or whose order is unknown) is honestly a single step and
            # must not be split — inventing a sequence the code does not have is the
            # same fabrication as inferring one from a layout.
            if len({z for _t, z in tgt}) < 2:
                continue
            by_depth = {}
            for t, z in tgt:
                by_depth.setdefault(z, []).append(t)
            parts = []
            for i, z in enumerate(sorted(by_depth)):
                part = "%s#%d" % (pid, i)
                self.nodes[part] = dict(self.nodes[pid],
                                        label="%s\\nstep %d" % (
                                            self.nodes[pid]["label"], i + 1))
                parts.append(part)
            # ⚑ RE-POINT EVERY EDGE IN ONE PASS. A first cut moved the pywrites per part
            # and THEN swept "everything still on `pid`" to `parts[0]` — but the sweep
            # matched the pywrites it had just moved and dragged them all back to step 1,
            # silently undoing the split. Two passes over one mutable list, the second
            # unable to tell what the first had done.
            _at = {t: p for i, z in enumerate(sorted(by_depth))
                   for t in by_depth[z] for p in [parts[i]]}
            for j, (s, d, k, a) in enumerate(self.edges):
                if s == pid:
                    # a write goes to ITS step; anything else leaves at entry
                    self.edges[j] = (_at.get(d, parts[0]) if k == "pywrite"
                                     else parts[0], d, k, a)
                elif d == pid:
                    self.edges[j] = (s, parts[0], k, a)
            # ⚑ THE STEPS ARE ORDERED, so the lane runs downward like every other
            # sequence here; `sameas` because they are ONE function, not a dataflow.
            for a, b in zip(parts, parts[1:]):
                self.edge(a, b, "sameas")
            _lab = self.nodes[pid]["label"].split("\\n")[0]
            del self.nodes[pid]
            split[pid] = parts
            self.clusters["step_" + pid] = {"label": _lab, "members": parts}
        return split

    # ⚑ `_depths()` STOOD HERE AND IS DELETED, NOT KEPT FOR LATER. It computed each
    # node's longest chain from a source — the rank `dot` approximates — and the producer
    # split was keyed on it until the recursion was named: a criterion read off the graph
    # cannot decide a change to the graph. Leaving it in place as an unused helper would
    # leave the trap loaded for whoever reaches for "how deep is this node" next, so the
    # deletion IS the record. Anything that wants an ordering here must read the code.

    def relation(self, rel, counts, **attrs):
        """A relation node with its state carried by TEXT, BORDER and fill — all three.

        ⚑ ONE PLACE, BECAUSE SIX SITES DECLARED RELATIONS and each had to remember to pass
        the fill. Adding a second carrier (the border) to six call sites is six chances to
        miss one, and a relation drawn without its state reads as populated — the failure
        mode that silently understates what is ABSENT.
        """
        a = dict(_state_style(rel, counts))
        a.update(attrs)
        return self.node(rel, _rel_label(rel, counts).strip('"'), "relation",
                         fillcolor=_fill(rel, counts), **a)

    def node(self, nid, label="", kind="other", **attrs):
        # ⚑ LAST WRITE WINS, DELIBERATELY — a node may be declared by the producer pass and
        # then re-declared with a `⚑ no caller` flag. Silently keeping the first would make
        # the flag depend on emission order.
        self.nodes[nid] = dict(label=label, kind=kind, **attrs)
        return nid

    def edge(self, src, dst, kind="other", **attrs):
        self.edges.append((src, dst, kind, attrs))

    def adjacency(self):
        import collections
        adj = collections.defaultdict(list)
        for s, d, k, _a in self.edges:
            # ⚑⚑ AN IDENTITY EDGE IS NOT A DEPENDENCY, so it is not in the walk. `sameas`
            # joins the two halves of a split rest point — after→before, the SAME relation
            # at two times — and it is by construction the back-edge the split just cut.
            # Including it re-closes every cycle the split opened, which the acyclicity
            # gate caught immediately: `_node` and `orbit_node` reappeared as cyclic the
            # moment the join was drawn.
            #
            # ⚑ AND EXCLUDING IT IS NOT A LOOPHOLE. A cycle detector answers "can data
            # return to where it started"; an identity states that two nodes ARE one
            # thing, which is not a step data takes. The edge carries `constraint=false`
            # for the same reason — it makes no claim about order — so the graph and the
            # walk agree rather than one being patched around the other.
            if k != "sameas":
                adj[s].append(d)
        return adj

    def cycles(self):
        """[[node …]] — every cycle, over the STRUCTURE.

        ⚑⚑ THE ACYCLICITY IS A PRECONDITION, so it is checked rather than believed. Every
        edge constrains (operator: *"If it's already acyclic, then we can just add
        constraints on all of the nodes and let dot sort it out"*), which is safe only while
        the graph has no cycle — a constrained cycle is a contradiction the layout must
        break arbitrarily, silently choosing which dependency to disbelieve.
        """
        adj, found, state = self.adjacency(), [], {}

        def walk(n, path):
            state[n] = 1
            for m in adj.get(n, ()):
                if state.get(m) == 1:
                    found.append(path[path.index(m):] + [m] if m in path else [m, n, m])
                elif not state.get(m):
                    walk(m, path + [m])
            state[n] = 2

        for n in list(adj):
            if not state.get(n):
                walk(n, [n])
        return found

    def edge_census(self):
        """{kind: (total, unconstrained)} — read off the edges, never off their colour."""
        out = {}
        for _s, _d, k, a in self.edges:
            c = out.setdefault(k, [0, 0])
            c[0] += 1
            c[1] += a.get("constraint") is False
        return {k: tuple(v) for k, v in sorted(out.items())}


def _returns(builder):
    """The columns `builder` hands back — `query_defs.returned_columns` of its statement.

    ⚑ THE STATEMENT IS THE AUTHORITY, not a name convention: a builder ending `_summary`
    happens to return three scalars and one ending `_insert` happens to return three too,
    so the shape is read off the compiled object or it is guessed."""
    import query_defs
    stmt = query_defs.INTERN_BUILDERS.get(builder)
    if stmt is None:
        return []
    try:
        return query_defs.returned_columns(stmt() if callable(stmt) else stmt)
    except Exception:
        return []


# ⚑ `_wrap` LIVES ONCE, further down. I wrote a second copy here while adding the return
# nodes without checking whether the name was taken — and the later definition silently WON,
# so my version was dead the moment it was written. Exactly the `agda_files()`-had-four-
# bodies defect `pycodemod`'s own docstring records, committed inside the tooling. Found by
# `--layout`, which lists top-level defs and showed the name twice.


def builder_edges():
    """Every `relation → builder → relation` splice, from `query_defs.touching`.

    ⚑⚑⚑ THE BUILDERS ARE READ, NOT LISTED. `touching(rel)` returns `{"readers": [builder …],
    "writers": [file:line …]}` and its own note states the asymmetry that makes this honest:
    *"reads are exact (this module IS the read authority); writes are NOT modelled here and are
    found by verb — a write via an unlisted spelling would be missed."* So a builder's READS are
    a declaration and its WRITES are a search, and the diagram must show which is which rather
    than drawing both as the same kind of arrow.

    ⚑⚑ THIS REPLACES A HAND-WRITTEN `FLOW` TABLE. That table listed 14 splices I happened to know
    about, in a repo with 81 builders — a roster beside the registry, which is the exact defect
    `toolmodes` exists to retire and which this file's own docstring calls out for pictures. The
    operator's ask (*"expand the graph to include ALL of the builders that get spliced
    together"*) is not a bigger list; it is deriving the list.

    ⚑ A BUILDER READING SEVERAL RELATIONS IS ONE NODE WITH SEVERAL IN-EDGES, which is what makes
    the splices visible.

    ⚑⚑⚑ THE COMPOSED BUILDERS WERE INVISIBLE HERE UNTIL `touching` WAS FIXED, AND I HAD FILED
    THAT AS A LIMIT RATHER THAN A DEFECT. `--touching obs` reported exactly ONE reader
    (`q_obs_all`) on a store where four of this arc's builders read `obs`, because reader
    resolution used **`get_final_froms()`** — the OUTERMOST sources — so a table scanned inside a
    CTE was one layer down and unseen. I wrote it up as a missing mode and a caveat on this
    graph.

    ⚑⚑ IT WAS A WRONG ACCESSOR (operator, 2026-08-15: *"How are those CTEs being constructed?
    Because they're surely not just raw SQL. And if they're not raw SQL, we can decompose them
    with ast."*). They are SQLAlchemy Core objects built with `.cte()`/`.subquery()` — a TREE —
    and `sqlalchemy.sql.visitors.iterate` walks it. `touching` now uses `_tables_of`, and `obs`
    reports **15 readers**, not one.

    ⚑ AND THE UNDER-REPORTING PREDATED THIS ARC: `q_drainable_res`, `q_edge_disagreement` and
    `q_ref_rows` were invisible too. So the fix widened an instrument the whole repo reads, not
    just the graph that exposed it.
    """
    import query_defs as _qd
    from schema_decl import MD
    reads, writes, recursive = {}, {}, set()
    for rel in sorted(MD.tables):
        try:
            t = _qd.touching(rel)
        except Exception:
            continue
        for b in t.get("readers", ()):
            reads.setdefault(b, set()).add(rel)
        # ⚑⚑ BUILDER WRITES ARE EXACT AND THEY ARE WHAT GIVE THE GRAPH FLOW. Until 2026-08-15
        # this function collected only READS, so every edge ran relation → builder and nothing
        # came OUT of a builder — a hundred arrows into components and no pipeline (operator:
        # *"right now the graph is not actually doing much"*). `touching` now separates them by
        # STATEMENT TYPE, so a write is exact rather than verb-scanned.
        for b in t.get("builder_writes", ()):
            writes.setdefault(b, set()).add(rel)
        for b in t.get("recursive", ()):
            recursive.add((b, rel))
    return reads, writes, recursive


# ⚑⚑⚑ THE PYTHON PRODUCERS — the writes NO instrument here can see, and they are the ones that
# CREATE the data. `write_events` writes `obs`, `edge`, `event` and `core_fp` through
# `_schema.upsert(...)`: a python call with no SQL verb in the source, so `touching`'s verb scan
# misses it entirely (measured: `--touching obs` lists 12 writers, and not one is the ingest that
# put 6,274,182 rows there). Every builder-derived edge therefore READS relations nobody appears
# to fill — the "nothing has an intake" the operator saw.
#
# ⚑⚑⚑ AND THEY ARE DERIVED, NOT DECLARED — I wrote a hand-maintained table here first, with a
# comment justifying it as "the honest boundary" because `upsert(con, "obs", rows)` names its
# relation as a positional string. Operator, 2026-08-15: *"This should be getting mechanically
# derived, not reified."* The justification was the defect: an ordinal is exactly as recoverable
# from the CST as a keyword is, and `pycodemod`'s whole `--forwards`/`--asserted`/`--values`
# family was simply keyword-only — a fact about THE METHOD I was about to record as a fact about
# the substrate, in the file whose top rule forbids precisely that.
#
# ⚑⚑ THE HAND TABLE WAS ALSO WRONG, WHICH IS THE POINT. It named `write_events` (the wrapper);
# the writer is `_insert_decoded`. It listed six relations for decode; there are seven — it
# missed `unit_member` and `unit_obs`. A reified list is not merely unmaintainable in the
# future, it was inaccurate at the moment of writing, and nothing could have caught it.
#
# ⚑ SO THE GRAPH HAS THREE PRODUCER KINDS, all derived: compiled BUILDERS (from the registry),
# python PRODUCERS (from the positional literal at `upsert`'s relation slot, below), and
# verb-scanned writers (best-effort text, reported as a count).
UPSERT_RELATION_ARG = 1     # `upsert(con, <relation>, rows)` — the slot, stated once
QB_RUN_BUILDER_ARG = 1      # `QB.run(con, <builder>, …)` — the slot, stated once
_PRODUCERS_MEMO = {}
_SLOT_MEMO = {}


def _slot_census(paths):
    """Both slot queries from ONE corpus scan — `{name: (rows, total)}`.

    ⚑⚑ TWO SCANS FOR TWO NAMES WAS 149s OF A 196s BUILD, measured by `--profile` rather
    than guessed. `producers()` reads `upsert`'s relation slot and `consumers()` reads
    `QB.run`'s builder slot; both were whole-corpus `values()` calls, and the scan — not
    the name — is what costs. `values_many` filters during one traversal.

    ⚑ THE SLOTS ARE STILL DECLARED SEPARATELY, one per capability, so this is a shared
    EXECUTION rather than a merged question: `--producers` and `--consumers` answer
    different things and keep saying so.
    """
    if paths not in _SLOT_MEMO:
        _SLOT_MEMO[paths] = _pycodemod.values_many(
            {"upsert": UPSERT_RELATION_ARG, "run": QB_RUN_BUILDER_ARG},
            _py_files(*paths))
    return _SLOT_MEMO[paths]


def producers(paths=("scripts", "jea")):
    """{function -> [relations]} — every python writer, read off the call sites.

    ⚑ SELFTESTS ARE EXCLUDED BY THE ENCLOSING-CONTEXT COLUMN, not by a path filter.
    `--values` reports `ctx`, so a `_selftest` writer is distinguishable from a
    production one structurally; 34 of the 53 upsert sites are selftest fixtures
    building throwaway tenants, and drawing them would make every relation look
    like it has an intake it does not have in the real pipeline."""
    # ⚑ MEMOISED LIKE `consumers()` — an 18s whole-corpus CST walk, called once per graph
    # build. Only the consumer half was cached, so a suite asking several questions paid
    # this repeatedly; measured, not guessed (`time --producers` = 18.1s for one walk).
    if paths in _PRODUCERS_MEMO:
        return _PRODUCERS_MEMO[paths]
    rows, _n = _slot_census(paths)["upsert"]
    out = {}
    for path, _line, rel, ctx in rows:
        if ctx == "_selftest" or rel is _UNKNOWN:
            continue
        mod = os.path.splitext(os.path.basename(path))[0]
        out.setdefault("%s.%s" % (mod, ctx), set()).add(rel)
    _PRODUCERS_MEMO[paths] = {k: sorted(v) for k, v in sorted(out.items())}
    return _PRODUCERS_MEMO[paths]


_CONSUMERS_MEMO = {}
_ROUNDTRIP_MEMO = {}


def consumers(paths=("scripts", "jea")):
    """{builder -> [functions that run it]} — who CONSUMES each builder's result.

    ⚑⚑⚑ THE HALF THE GRAPH WAS MISSING, AND THE OPERATOR SAW IT IN THE PICTURE
    (2026-08-15: *"I can see the builders get information from somewhere, but what gets
    information from them?"*). Every builder had in-edges from the relations it reads and
    NOTHING leaving it — a flow graph in which the flow stops. `returned_columns` says WHAT
    comes out; this says WHERE IT GOES, and neither alone closes the edge.

    ⚑⚑ DERIVED FROM THE SAME SLOT-QUERY AS `producers()`, which is the point: `QB.run(con,
    "pack_level")` names its builder as a positional string exactly as `upsert(con, "obs")`
    names its relation. One capability — read the literal at a known ordinal and attribute it
    to the enclosing def — answers both "who writes this relation" and "who reads this
    builder". A second bespoke scanner for the second question would have been the
    weak-beside-strong duplication `--asserted`'s docstring records.

    ⚑ SELFTESTS EXCLUDED BY CONTEXT, and UNKNOWN sites are DROPPED RATHER THAN GUESSED —
    11 of 76 pass a computed name (a loop variable, a dispatch table), so those consumers are
    real but unattributable. The count is reported; the edges are not invented.
    """
    # ⚑⚑ MEMOISED, BECAUSE THIS IS A WHOLE-CORPUS CST WALK. A first cut called it inside
    # the per-builder loop — 81 rescans of ~900 files, and the selftest went from instant to
    # past a 120s timeout. The scan is deterministic over a fixed tree, so the repeat bought
    # nothing; the same reasoning as `KwIndex` stamping its population once.
    if paths in _CONSUMERS_MEMO:
        return _CONSUMERS_MEMO[paths]
    rows, _n = _slot_census(paths)["run"]
    out = {}
    # ⚑⚑⚑ A BUILDER RUN BY A DISPATCH TABLE IS NOT UNCALLED, AND MY CENSUS SAID IT WAS
    # (operator, 2026-08-16: *"how is it orbit_member, q_orbit_merged and q_orbit_packings
    # are disconnected from everything else? … Are they partial migrations?"*). They are
    # neither dead nor half-migrated: `query_defs.verify()` iterates `_reg().items()` and
    # runs each builder against a hand-written raw-SQL twin, asserting identical rows.
    # That is an EQUIVALENCE ARM — arguably the most load-bearing consumer a builder has —
    # and it reached the graph as `⚑ no caller`.
    #
    # ⚑⚑ MY OWN OUTPUT CARRIED THE EXPLANATION AND I NEVER JOINED IT. Every run of
    # `--consumers` printed *"11 run sites pass a computed name and cannot be
    # attributed"*, and `verify`'s `run(con, build(), …)` is one of them. I had the
    # caveat and the symptom in the same report for two days and read the symptom as a
    # fact about the builders rather than about the method — the exact fact-about-the-
    # METHOD-reported-as-a-fact-about-the-SUBSTRATE error this repo's top rule names.
    #
    # ⚑ SO THE MEMBERSHIP IS READ FROM `_GROUP`, THE DECLARATION THAT ALREADY EXISTS.
    # `query_defs._GROUP` assigns every builder to a group — `orbit`, `render`, `recur`,
    # `ingest`, `catalog` — and `verify(group=…)` selects on it. A builder in a NON-DEFAULT
    # group is run by `--group <name>`, which is a caller with a name, just not a literal
    # one. Derived, so a builder added to a group tomorrow is covered with no edit here.
    #
    # ⚑⚑ AND THE DEFAULT GROUP IS THE TRAP INSIDE THE TRAP. `_GROUP` lists only the
    # NON-default assignments; `_group_of` returns `"catalog"` as a FALLBACK, so the
    # builders `verify()` runs with NO flag — the plain, always-run arms — appear in no
    # declaration at all. Reading `_GROUP` alone moved 28 unattributed to 22 and left
    # every remaining one in the group that runs MOST often. A membership table that
    # records only the exceptions is not a roster of the population, and treating it as
    # one reproduces the original error one layer in.
    try:
        import query_defs as _qd
        _gr = getattr(_qd, "_GROUP", {})
        for _b in getattr(_qd, "INTERN_BUILDERS", {}):
            _g = _gr.get(_b, "catalog")
            out.setdefault(_b, set()).add(
                "query_defs.verify" if _g == "catalog"
                else "query_defs.verify --group %s" % _g)
    except Exception:
        pass
    for path, _line, name, ctx in rows:
        if ctx == "_selftest" or name is _UNKNOWN:
            continue
        mod = os.path.splitext(os.path.basename(path))[0]
        # ⚑⚑ KEYED ON THE BARE NAME, WHICH IS WHAT BOTH SIDES ACTUALLY USE. I first wrote
        # `"q_" + name` on the belief that the registry spells them `q_…` — it does not;
        # `q_pack_level` is the DECL FUNCTION's name and `pack_level` is the registry key
        # `QB.run` takes. The mismatch keyed every consumer under a name no builder has, and
        # the census read "0 of 81 builders have a caller" — which my own output would have
        # rendered as ⚑ NO CALLER, 81 times. A join on the wrong key reports as a finding
        # about the substrate; it is a fact about the join.
        out.setdefault(str(name), set()).add("%s.%s" % (mod, ctx))
    _CONSUMERS_MEMO[paths] = {k: sorted(v) for k, v in sorted(out.items())}
    return _CONSUMERS_MEMO[paths]


# ⚑⚑ WHAT IS LEFT AFTER THE DERIVATION, AND IT IS ONE EDGE. Four of this table's five entries
# named decode's writes — `producers()` now reads those off the call sites, and read them MORE
# accurately (the performer is `_insert_decoded`, not the `write_events` wrapper this table
# named, and there are seven relations rather than four).
#
# ⚑ THE SURVIVOR IS A DIFFERENT KIND OF FACT: the drain is a DELETE gated on a LICENCE
# (`reflects_obs`), so it is not an `upsert` call site and no relation-slot query can see it.
# It is the SOURCE edge of the disk corpus too — `.agdai` is not a relation, so nothing in the
# store can report that it feeds decode. Both are genuinely outside every census here, which is
# why they are stated rather than derived, and stating that boundary is the point.
FLOW = [
    # (from, to, label, performer)
    ("agdai", "__producer:sppf_decode._insert_decoded", "reads .agdai", ""),
    ("obs_node", "drain", "licence: reflects_obs", "schema.reclaim"),
]

# relations the diagram shows even when absent — the ones whose ABSENCE is itself the finding
KEY_RELATIONS = ("obs", "edge", "event", "core_fp", "obs_node", "_node",
                 "node_child", "unit_obs", "_unit", "unit_node", "ref")


def stages():
    """[(name, gloss)] — the lifecycle chain, from its declaration."""
    # ⚑ A `Chain` link is the triple `(name, predicate, because)` — `lifecycle.py:69-71`. Read
    # from the structure rather than assumed: my first cut wrote `s.name` / `s.why`, attribute
    # names I invented for a tuple.
    from lifecycle import LIFECYCLE
    return [(name, because) for name, _pred, because in LIFECYCLE]


def counts(sandbox=False):
    """{relation: rows or None} — None means ABSENT, 0 means APPLIED AND EMPTY.

    ⚑ THE DISTINCTION IS THE WHOLE POINT and `census` already draws it (`schema_diag:80-83`:
    *"a tier that was never applied and a tier that is applied-but-empty are different facts;
    collapsing them into 0 is exactly the absent-read-as-failed the observability rule
    forbids"*). This diagram inherits that or it inherits the defect.
    """
    import store as _store
    from schema_diag import census
    con = _store.sandbox_connect(reset=False) if sandbox else _store.connect(mode="ro")
    return {n: c for _tier, n, c in census(con)}


def dot(counts_by_rel=None, stage_list=None, reads=None, writes=None, recursive=None):
    """The DOT source. `counts_by_rel=None` renders structure only; `reads=None` omits builders."""
    st = stage_list if stage_list is not None else stages()
    writes = writes or {}
    recursive = recursive or set()
    # ⚑⚑⚑ THE ENGINE IS A PARAMETER BECAUSE THE GRAPH IS A FAN, NOT A PIPELINE. `dot` ranks
    # left-to-right and this graph is mostly BIPARTITE — two hub relations (`obs` 6.27M, `edge`
    # 6.27M) against ~80 builders — so every edge crosses one boundary and `dot` renders a wall
    # of parallel curves through which nothing is legible. The operator, seeing it: *"This…is a
    # mess. Let's at least switch to fdp."*
    #
    # ⚑⚑ `fdp` IS A FORCE-DIRECTED LAYOUT: it has no ranks to satisfy, so a hub is drawn as a hub
    # and its readers fall around it. That IS the graph's shape — the fan is the finding (fifteen
    # builders read `obs`), and a layout that fights it hides exactly the structure the diagram
    # was asked for.
    #
    # ⚑ `dot` IS KEPT REACHABLE, not replaced, because it is the right engine for the LIFECYCLE
    # SPINE alone — a genuine chain — which is what `--no-builders` renders. One shape per engine,
    # chosen by what is being drawn rather than by a global default.
    # ⚑⚑ `dot` IS THE DEFAULT AGAIN, AND THE THREE TECHNIQUES ARE WHY IT CAN BE. The move to
    # `fdp` was a response to the wall of parallel curves — but that wall came from EDGE LABELS
    # and a CLUSTER forcing containment, not from ranking. With labels expressed as shared nodes
    # and no cluster at all, `dot`'s ranking becomes an asset: it puts the lifecycle chain on one
    # axis and lets the hub relations sit at their own ranks, which a force layout cannot do
    # because it has no notion of "upstream".
    #
    # ⚑ AND THE FAN IS NOW SMALLER THAN IT LOOKED. Shared label-nodes collapse four `.agdai`
    # edges to one; the builders' reads still fan, but a ranked layout draws a fan as a comb
    # rather than a spray once nothing is fighting it for space.
    #
    # ⚑ `--engine fdp` STAYS REACHABLE (through podman — this box's graphviz registers only
    # `dot`), because the right engine is a property of the QUESTION: `dot` for "what flows into
    # what", `fdp` for "what clusters near what".
    eng = "dot"
    for i, a in enumerate(sys.argv):
        if a == "--engine" and i + 1 < len(sys.argv):
            eng = sys.argv[i + 1]
    # ⚑⚑⚑ THIS FUNCTION NOW BUILDS A `Graph` AND HANDS IT TO `serialize`. It used to append
    # DOT strings directly, which meant the text was the only representation and every query
    # about the graph had to re-parse it — see `Graph`'s docstring for the three instruments
    # that broke that way. The engine/attribute preamble below is the one part that is
    # genuinely about rendering, so it stays; everything after it is `g.node` / `g.edge`.
    # ⚑⚑⚑ A SECOND PREAMBLE STOOD HERE AND WAS NEVER EMITTED. `dot()` built this `out` list
    # before `serialize()` took over emission, and it has been dead ever since — a full copy
    # of the engine/spline/rankdir settings that no render has used, carrying eight ⚑ blocks
    # of reasoning about attributes that were only ever applied by the OTHER copy. Two
    # rosters of one fact, in the file that keeps recording that defect.
    g = Graph()

    # the lifecycle chain, as the spine
    # ⚑ THE CHAIN'S HEADING IS A NODE TOO, for the same reason as the edge labels: *"most layout
    # engines don't support clusters at all"*. A `cluster_chain` box renders under `dot` and is
    # silently ignored under `fdp`, so the orientation a reader needs first would appear in one
    # rendering and vanish in the other. A plaintext node pointing at stage 0 says the same thing
    # in a first-order object.
    g.node("chain_hdr", "lifecycle chain — the DECLARED stages", "label",
           fontsize="9", fontcolor="#666666")
    for i, (name, why) in enumerate(st):
        g.node("stage_" + name, "%d %s\\n%s" % (i, name, _wrap(why, 34)), "stage")
    # ⚑⚑ THE CHAIN IS A SWIMLANE — `constraint=true` on ITS edges only, so it spans the graph's
    # full height and gives every other rank something to be measured against. The post builds
    # the same skeleton (*"the `A -> B -> C -> D` row has as many ranks as the entire graph, so it
    # extends end to end"*), and it is what stops the stages collapsing into the machinery.
    g.edge("chain_hdr", "stage_" + st[0][0], "hint")
    for a, b in zip(st, st[1:]):
        g.edge("stage_" + a[0], "stage_" + b[0], "stage", constraint=True)

    g.node("agdai", ".agdai cores\\non disk", "source")
    seen = {"agdai"}
    for rel in KEY_RELATIONS:
        seen.add(rel)
        g.relation(rel, counts_by_rel)
    g.node("drain", "drain\\n(rows reclaimed)", "sink")
    seen.add("drain")

    # ⚑⚑⚑ NODES AS EDGE LABELS — the operator's own technique, from
    # `mikemol.github.io/docs/blog/2018/01/12/graphviz-technique-nodes-as-edge-labels`, and it
    # dissolves BOTH layout problems this file has been fighting rather than working around
    # either. The post states the reason: *"Graphviz treats only NODES AND EDGES as first-order
    # objects… Edge labels and clusters don't get as much love. In some layout engines, edge
    # labels will be drawn, but you'll be shown a warning that edge labels aren't supported. And
    # most layout engines don't support clusters at all."*
    #
    # ⚑⚑ SO THE TWO THINGS I WAS TUNING AGAINST WERE ONE KNOWN PROBLEM. `splines=ortho` mangling
    # edge labels, and `fdp` refusing to honour `cluster_*` — both are "this engine only really
    # supports nodes and edges", and both are fixed by expressing the thing as a NODE.
    #
    # ⚑ AND THE LABEL-NODE IS SHARED, which is the post's second point (*"instead of needing one
    # label for each edge, we can use one label for ALL edges… that often saves a considerable
    # amount of space"*). Four `.agdai → …` edges carry the same `decode / write_events` label;
    # one node with four out-edges says it once. `style=none` so it draws as text, not a box.
    # ⚑⚑ THE PYTHON PRODUCERS ARE EMITTED FIRST, because a `FLOW` row may point AT one
    # (`.agdai` feeds decode) and an edge to an id that has not been declared yet gets
    # graphviz's default node shape — the producer would silently render as a plain box
    # and read as a relation. Derived from the `upsert` relation slot; see `producers()`.
    _prod_ids = {}
    for fn, rels in producers().items():
        _prod_ids[fn] = g.node("p_" + fn, fn, "producer")
        for rel in rels:
            if rel not in seen:
                seen.add(rel)
                g.relation(rel, counts_by_rel)
            g.edge("p_" + fn, rel, "pywrite")

    _lab_nodes, _lab_in = {}, set()
    for src, dst, lab, who in FLOW:
        # ⚑ `__producer:<fn>` TARGETS A DERIVED NODE rather than declaring a relation —
        # the one place a stated edge meets a derived one. An unknown function here is a
        # REFUSAL, not a silently-minted node: it means the producer census stopped
        # seeing a writer this edge assumes, which is a finding.
        src = _prod_ids[src[11:]] if src.startswith("__producer:") else src
        dst = _prod_ids[dst[11:]] if dst.startswith("__producer:") else dst
        for n in (src, dst):
            if n not in seen and not n.startswith("p_"):
                seen.add(n)
                g.node(n, n, "relation", fillcolor="#f5f5f5")
        key = (lab, who)
        if key not in _lab_nodes:
            _lab_nodes[key] = "lab%d" % len(_lab_nodes)
            # ⚑ A FLOW ROW WHOSE PERFORMER IS NOW DERIVED CARRIES NO `who` — the decode edge
            # points AT a producer node that names itself, so repeating the name in the
            # label would print it twice. An empty half must not leave a trailing newline.
            g.node(_lab_nodes[key], "\\n".join(x for x in (lab, who) if x), "label")
        # ⚑ THE IN-EDGE IS DEDUPED, and its absence was a real defect the DOT source showed:
        # `.agdai` fans to `event`, `obs` and `edge` through ONE shared label-node, so emitting
        # `src -> label` per FLOW row drew that edge THREE TIMES. Graphviz renders parallel
        # duplicates as separate lines, which is the crowding the shared node exists to remove —
        # the technique half-applied is worse than not applying it.
        _in = (src, _lab_nodes[key])
        if _in not in _lab_in:
            _lab_in.add(_in)
            g.edge(src, _lab_nodes[key], "other", arrowhead="none")
        g.edge(_lab_nodes[key], dst, "other")

    # ⚑⚑ EVERY BUILDER IS A NODE, AND ITS READS ARE THE SPLICE. A builder reading three relations
    # is three in-edges into one box — which is what makes the composition visible rather than
    # narrated. `q_pack_level` reading `obs`, `edge`, `event` AND `obs_node` is the level fold's
    # whole dependency, and the `obs_node` self-reference is WHY it must run level-by-level.
    if reads is not None:
        # ⚑⚑⚑ `rank=same` + STYLING, NOT A `cluster_*` BOX. A cluster is a CONTAINMENT constraint:
        # it drags ~80 builders into one rectangle and forces every edge across a single boundary,
        # which is what produced the wall of parallel curves. My first response was to drop the
        # grouping whenever the engine was not `dot` — throwing away the reader's orientation to
        # escape the constraint (operator, 2026-08-15: *"samerank still works. And so does
        # styling. Let rank and proximity handle most of the clustering."*).
        #
        # ⚑⚑ THE THREE MECHANISMS ARE INDEPENDENT AND ONLY ONE OF THEM CONSTRAINS LAYOUT.
        # `rank=same` is a HINT that survives every engine; the shared shape/fill says "these are
        # one kind of thing" with no geometric claim at all; and PROXIMITY is what the layout
        # produces on its own — a builder is drawn near the relations it reads because the edges
        # pull it there. Grouping by drawing a box around things is the weakest of the three and
        # the only one that fights the engine.
        #
        # ⚑ SO THE GROUP IS EXPRESSED IN THE NODES, and it reads the same under `dot` and under a
        # force layout: `shape=component` + the blue fill IS the legend.
        # ⚑⚑⚑ AND THE BUILDERS ARE **NOT** `rank=same`, WHICH IS THE THIRD TIME I GOT THIS
        # EXACT KNOB WRONG AND THE FIRST TIME FOR THE RIGHT REASON. I removed it (bad reason:
        # a width fear the post refutes), restored it (right correction, wrong conclusion),
        # and only the operator's third pass named what it actually asserts: *"These should
        # not be forced samerank. They're composable stages in dataflow, and they're all being
        # forced together."*
        #
        # ⚑⚑ A RANK IS A CLAIM ABOUT DATAFLOW POSITION, NOT ABOUT KIND. The post's finding is
        # that `rank=same` does not DISTORT the surrounding graph the way a cluster does — it
        # never said a rank is free of meaning. Putting all 81 builders on one rank asserts
        # they are simultaneous, and they are demonstrably not: `q_obs_heights_distinct` feeds
        # `pack_core_sql`, which drives `q_pack_level_insert` level by level;
        # `q_node_id_top` runs before `_do_promote`'s loop and `q_unprojected_cores` before
        # that. These COMPOSE. Forcing them level makes every real dependency edge bend around
        # a false assertion — the fan of curves under the strip is the layout paying for it.
        #
        # ⚑ SO THE RANK COMES FROM THE FLOW, which is what a layered engine does when nothing
        # overrides it: a builder sits below what it reads and above what consumes it, and
        # builders in one pipeline stack while independent ones spread. The grouping the rank
        # was doing is already carried by `shape=component` + the blue fill, which is the
        # mechanism that costs no geometry — the same reason the eye-guide chain came out.
        #
        # ⚑ THE GOVERNING PRINCIPLE, which is the part I kept violating from both directions:
        # *"The more I used constraining tools like clusters and edges with [constraint=true],
        # the harder it became to avoid spaghetti. I felt like the Emperor; the tighter I gripped,
        # the more slipped through my grasp. The more I relaxed, the easier it became."* A cluster
        # is a grip; `rank=same` is a nudge.
        # ⚑ THE EYE-GUIDE REPLACES THE BOUNDING BOX (§ Eye-Guiding, Non-Constraining Lines):
        # *"Without the clear bounding boxes offered by clusters, I wanted a way to get visible
        # groupings. Drawing NON-CONSTRAINING lines provided that."*
        #
        # ⚑⚑ BUT THE EYE-GUIDE IS ALSO GONE — see below. Both it and the `rank=same` it sat
        # inside were answers to "how do I show these are one kind of thing", and the fill +
        # shape already answer that without touching geometry. Kept in the record because the
        # post's technique is right and my APPLICATION of it was the error twice over: a
        # grouping device is only free when it makes no claim, and both of these made one.
        _bs = sorted(reads)
        for b in _bs:
            g.node("b_" + b, b, "builder")
        # ⚑⚑⚑ THE EYE-GUIDE IS GONE, AND `--edges` IS WHY. It drew 80 dotted
        # `constraint=false` links chaining every adjacent builder — the single largest
        # unconstrained group after the reads (`skeleton/other`: 61 of 71, 86%), and the
        # measurement is what found it; by eye I had been blaming the read edges.
        #
        # ⚑⚑ AND WHAT IT WAS REDUNDANT WITH IS NOW GONE TOO. I first justified removing the
        # eye-guide by noting the builders were ALREADY inside `{ rank=same }`, so a line
        # through a visible row added nothing. That was right about the line and wrong about
        # the row: the rank itself was the deeper error (see above). Both are out, and the
        # grouping is carried by shape+fill, which asserts nothing about position.
        for b, rels in sorted(reads.items()):
            for rel in sorted(rels):
                if rel not in seen:
                    seen.add(rel)
                    g.relation(rel, counts_by_rel)
                # ⚑⚑ `constraint=false` ON THE READ EDGES — the single change the post's whole
                # method turns on: *"The more I used constraining tools like clusters and edges
                # with [constraint=true] (which is the DEFAULT), the harder it became to avoid
                # spaghetti… The more I relaxed, the easier it became."* A read edge says WHO
                # READS WHAT; it is not a claim about rank order, and letting each of ~200 of
                # them push on the layout is what produced the wall of curves. The lifecycle
                # chain keeps its constraints and supplies the skeleton; everything else hangs
                # off it.
                # ⚑⚑⚑ AND THE READS CONSTRAIN NOW, WHICH IS THE OTHER HALF OF THE RANK FIX.
                # `--ranks` measured it: with `rank=same` removed the builders STILL landed on
                # one rank (62 of them, y=8.4), because a relaxed edge carries no order —
                # `dot` had nothing left to layer by and fell back to a flat row. The forced
                # rank had not been causing the strip; it was restating what the unconstrained
                # reads already produced. Two knobs, one effect.
                #
                # ⚑⚑ A READ **IS** A DATAFLOW FACT, and that is what I kept missing by calling
                # it "just who-reads-what". `q_pack_level` reads `obs_node`, so it runs after
                # `obs_node` exists — the edge states a real precedence, and unconstraining it
                # discards exactly the information that stacks the composable stages the
                # operator asked to see. The relaxation was correct only while the rank was
                # doing the placement; once the rank came out, it inverted.
                # ⚑⚑⚑ A GRADIENT MAKES THE INSTANCE TRACEABLE, NOT JUST THE KIND
                # (operator, 2026-08-16: *"See all these blue lines? Undifferentiable.
                # This is why I called out gradient-support in edge colors earlier"*).
                # 147 reads in one blue: the KIND is legible and any single edge is not —
                # where two cross, a reader cannot tell which line came from which
                # relation, so "who reads obs" is unanswerable from the picture that
                # exists to answer it.
                #
                # ⚑⚑ `color="a;0.5:b"` RUNS THE STROKE FROM THE SOURCE'S HUE TO THE
                # TARGET'S, so an edge is identified by WHERE ITS COLOUR STARTS. That is
                # the one channel a fan of parallel lines leaves free: position is spent
                # by the layout, shape is spent by the kind, and hue-along-the-stroke is
                # unused. The `;0.5` weight is required — without it graphviz draws two
                # parallel edges rather than one gradient.
                #
                # ⚑⚑ THE SOURCE HUE IDENTIFIES THE RELATION, NOT ITS ROW-STATE, and the
                # first cut used `_fill` — which is the STATE colour. Measured by
                # `--rendered`: "147 declared over 1 source colour", because with counts
                # absent every relation fills the same grey and with counts present the
                # 147 edges collapse to three (populated/EMPTY/ABSENT). Either way the
                # fan stays untraceable, which is the defect this was meant to fix.
                #
                # ⚑ SO IT IS A HASH OF THE RELATION NAME onto a wide hue circle. The
                # relation's STATE is already carried by its node's fill, border weight
                # and label text — three carriers — so spending the edge's source colour
                # on identity rather than a fourth copy of state is what makes a
                # particular line followable back to a particular box.
                g.edge(rel, "b_" + b, "read",
                       color="%s;0.5:%s" % (_hue(rel), _ok("blue")))
        # ⚑⚑⚑ WHAT A QUERY **RETURNS** IS NOT WHAT IT **READS**, and both are edges in a flow
        # graph (operator, 2026-08-15: *"it's not obvious to me the distinction between what a
        # query reads and what it returns; both are part of a flow graph."*). `q_pack_level`
        # SCANS obs/edge/event/obs_node and RETURNS `(core_id, local_id, node_id)` — the second
        # is what a caller consumes, and the graph showed only the first.
        #
        # ⚑⚑ THE RETURN IS A NODE, NOT A LABEL, so it reads the same as every other object here.
        # A pure SELECT's output goes to the CALLER (python), which is where the ingest's
        # remaining client-side work is visible; a DML builder's output goes to its target table
        # AND, when it RETURNINGs, to the caller as well — `q_pack_level_insert` does both, which
        # is exactly the (n, ids, top) summary that replaced 529,003 materialised rows.
        # ⚑⚑ AND THE RETURN NODE IS THE CONSUMER, not a floating list of column names. A
        # `shape=note` holding `core_id, local_id, node_id` says what comes out and still
        # leaves the operator's question open — *what gets information from them?* The
        # answer is a named python function, derived from `QB.run`'s builder slot, so the
        # edge runs builder → consumer and the columns ride on it as the payload.
        _cons = consumers()
        _ret_nodes = {}
        for b in sorted(reads):
            # ⚑⚑⚑ TWO SPELLINGS OF ONE NAME, AND BOTH SIDES ARE RIGHT. `touching` reports
            # builders by their DECL FUNCTION (`q_pack_level`); `QB.run` takes the REGISTRY
            # KEY (`pack_level`). I have now keyed this join wrongly in both directions —
            # first prefixing `q_` in `consumers()` (0 of 81 matched), then removing it and
            # leaving the graph side unprefixed (62 orphans drawn where the census says 28).
            # A join whose two sides spell the key differently reports as a finding about
            # the substrate every time, so the stripping happens HERE, once, at the seam.
            _who = _cons.get(b[2:] if b.startswith("q_") else b, ())
            _cols = _returns(b)
            if not _who:
                # ⚑ THE SHARED-NODE FIX WAS RIGHT ABOUT THE DUPLICATION AND WRONG ABOUT THE
                # KIND: 28 identical `no caller` notes became 1, which saved the space the
                # nodes-as-labels technique promises — but a shared node still made an
                # ABSENCE into a destination. Recorded rather than deleted because the first
                # fix's reasoning was sound and its premise was not.
                # ⚑⚑⚑ A VERDICT IS NOT A STAGE, AND DRAWING IT AS ONE MISREADS THE GRAPH
                # (operator: *"How does q_ref_rows not have any callers…but somehow feeds
                # something?"*). It fed the shared `no caller` node — 23 edges into one box,
                # which reads as a DESTINATION in a diagram whose every other arrow is
                # dataflow. The fact is "nothing consumes this builder", i.e. the ABSENCE of
                # an out-edge; expressing an absence as an edge is exactly backwards.
                #
                # ⚑⚑ SO IT IS A NODE ATTRIBUTE, drawn on the builder itself. A dead builder
                # goes red-bordered and says so in its own label — no edge, no sink, and the
                # empty out-degree is then literally visible as an empty out-degree.
                # ⚑ "NO ATTRIBUTED CALLER", NOT "NO CALLER" — the shorter label claimed a
                # fact about the code and only ever held a fact about this census. Four
                # `orbit_*` builders carried it while being run by `verify --group orbit`;
                # the operator read the picture correctly and asked whether they were
                # partial migrations, which is what the label invited.
                g.node("b_" + b, "%s\\n⚑ no attributed caller" % b, "builder",
                       color="#cc4444", penwidth="2")
                continue
            # ⚑⚑⚑ THESE EDGES CONSTRAIN, AND THAT IS THE WHOLE DIFFERENCE FROM A READ EDGE
            # (operator, 2026-08-15: *"Way too much constraint=false."*). `constraint=false`
            # was correct for reads — a read says WHO READS WHAT and is not a claim about
            # rank — and I then copied it onto the flow edges, where it is precisely wrong: a
            # builder RUNS BEFORE its consumer, so builder→consumer IS a rank claim. With
            # every such edge unconstrained, `dot` had almost nothing left to order by and
            # the return layer collapsed into one flat comb.
            #
            # ⚑⚑ THE RELAXATION IS NOT A GLOBAL SETTING, WHICH IS THE PART I FLATTENED. The
            # post's rule is *"the more I relaxed, the easier it became"* about the edges
            # that over-constrain a layout — not a licence to unconstrain the skeleton. Reads
            # (~200, many-to-many, no order) relax; flow (one direction, real sequence)
            # constrains. Applying one answer to both kinds is the same either/or collapse
            # the constraint was meant to resolve.
            for fn in _who:
                if ("c_" + fn) not in seen:
                    seen.add("c_" + fn)
                    g.node("c_" + fn, fn, "consumer")
                g.edge("b_" + b, "c_" + fn, "flow")
            # ⚑⚑⚑ AND THE COLUMN NOTE CONSTRAINS TOO — EVERY edge touching a builder does
            # (operator: *"We do want constraints active on all edges that touch builders"*).
            # I had kept this one relaxed on the grounds that a note *"is an annotation, not
            # a step"*, which is the same kind-vs-position confusion as the forced rank:
            # what a node MEANS does not license discarding WHERE IT SITS. The columns come
            # out of the builder, so the note belongs below it, and saying so costs nothing.
            # ⚑⚑ AND IT IS DEDUPED BY ITS TEXT, like every other label node here (operator:
            # *"should dedupe nodes like that"*). A column list is a LABEL, not an identity:
            # `pack_level` and `pack_level_summary` both return `core_id, local_id,
            # node_id`, and `reuse_catalog`'s index builders share their shapes too — a
            # private node per builder redraws the same three words a dozen times. Keyed on
            # the rendered text, so identical returns collapse to one node with several
            # in-edges and DIFFERENT returns stay visibly different.
            if _cols:
                _txt = _wrap(", ".join(_cols), 30)
                _rid = _ret_nodes.setdefault(_txt, "ret%d" % len(_ret_nodes))
                if _rid not in seen:
                    seen.add(_rid)
                    g.node(_rid, _txt, "returns")
                g.edge("b_" + b, _rid, "returns")
        # ⚑ WRITES ARE DRAWN DIFFERENTLY BECAUSE THEY ARE KNOWN DIFFERENTLY. `touching`'s own
        # caveat: reads are exact (it IS the read authority) while writes are VERB-SCANNED, so a
        # write via an unlisted spelling is missed. A solid arrow for a declaration and a bold
        # one for a search would be a lie of uniform confidence; the label says which it is.
        # ⚑ A WRITE COUNT AS A NODE, NOT AN `xlabel`. Same rule one more time: `xlabel` is
        # placement-on-a-best-effort-basis, so it lands somewhere plausible under `dot` and can
        # be dropped or displaced elsewhere. The count is a real fact about the relation and
        # deserves a first-order object — and as a node it also carries the read/write asymmetry
        # in its own text rather than in a legend nobody has.
        # ⚑⚑⚑ A RELATION A BUILDER BOTH READS AND WRITES BECOMES **TWO NODES** — inbound and
        # outbound — never one node with a cycle (operator, 2026-08-15: *"even if it doesn't read
        # and write to DIFFERENT tables, that's OK. In that case, you need to synthesize two nodes
        # for the data, one for 'outbound' and one for 'inbound'."*).
        #
        # ⚑⚑ THE CYCLE IS A TIME AXIS COLLAPSED, NOT A DRAWING PROBLEM. `q_pack_level_insert`
        # reads the CHILDREN's ids out of `obs_node` and writes the PARENTS' back — different
        # rows, at adjacent levels. As one node that is a loop `dot` must break arbitrarily, i.e.
        # a layout lie about a real structure; as `obs_node → builder → obs_node (after)` it is a
        # DAG that states what happens, and the level-by-level fold becomes VISIBLE instead of
        # asserted in a comment.
        #
        # ⚑ AND WRITES ARE WHAT GIVE THE GRAPH FLOW AT ALL. With reads only, every edge ran
        # relation → builder: a hundred arrows in, nothing out, no pipeline.
        for b, rels in sorted(writes.items()):
            for rel in sorted(rels):
                _rec = (b, rel) in recursive
                _dst = ("after_" + rel) if _rec else rel
                if _rec:
                    g.node(_dst, "%s\\n⟳ AFTER this step" % rel, "relation",
                           fillcolor=_fill(rel, counts_by_rel),
                           style="filled,dashed", penwidth="1.4")
                elif rel not in seen:
                    seen.add(rel)
                    g.relation(rel, counts_by_rel)
                g.edge("b_" + b, _dst, "write")
    # ⚑⚑⚑ THE ROUND-TRIP EDGE — SQL out, python, SQL back in (operator: *"much (most?)
    # of the time, something comes out of sql to go into python to go right back into
    # sql"*). Without it a consumer node and a producer node for the SAME FUNCTION sat
    # unconnected, so the diagram showed data arriving in python and, separately, data
    # appearing in relations, and the flow visibly stopped.
    #
    # ⚑⚑ DIRECT AND INDIRECT ARE DRAWN DIFFERENTLY, because they are different claims. A
    # direct trip does both in one body; an indirect one reaches the writer through the
    # call graph, and drawing them the same would assert the write happens where it does
    # not. The indirect edge is dashed and carries its hop count.
    # ⚑⚑⚑ THE ROUND TRIP IS A CYCLE, AND THE ACYCLICITY GATE CAUGHT IT — which is what
    # that gate is for. Adding this edge turned the graph cyclic in 8 places, and the
    # gate refused rather than letting `dot` silently break a constrained contradiction.
    #
    # ⚑⚑⚑ SPLIT AT THE DATA-AT-REST POINT, NOT AT THE FUNCTION (operator: *"find the
    # data-at-rest point in the cycle, and split it; the data-at-rest point becomes split
    # between the 'readfrom' and 'writtento' perspectives"*). My first cut split the
    # FUNCTION — `after_project_sppf` — which is wrong on its face: a function is data in
    # MOTION, it holds nothing between steps, so "after the function" names no state. The
    # relation is where the data rests, so that is the only place a before/after has a
    # referent.
    #
    # ⚑⚑ AND SPLITTING THE REST POINT FIXES EVERY CYCLE THROUGH IT AT ONCE. A per-function
    # split has to be repeated for each function closing a loop through the same relation
    # and leaves a cycle whenever two different functions form one; splitting `_node`
    # itself means EVERY reader takes the before-copy and EVERY writer lands in the
    # after-copy, so no path can return to its own start. That is why the recursive
    # builders' `after_<rel>` worked — I had the mechanism and applied it to the wrong
    # noun.
    #
    # ⚑ `<module>` IS A RESOLUTION LIMIT, NOT A FUNCTION. Six of the eight cycles ran
    # through `sppf_db.<module>` — every module-level statement pooled under one name, so
    # a CLI dispatch branch reading `obs` and an import-time call that writes `obs` became
    # one node. Not round trips; the scope collapse `--reaches` names in its own
    # docstring. Reported by `--roundtrips`, never drawn.
    for _fn, _v in roundtrips().items():
        if _fn.endswith(".<module>"):
            continue
        _hops = _v[2] if len(_v) > 2 else None
        _wfn = _v[3] if len(_v) > 3 else _fn
        _cid, _pid = "c_" + _fn, _prod_ids.get(_wfn)
        if _pid and _cid in seen:
            # ⚑⚑ THE EDGE CONSTRAINS UNLESS IT IS ACTUALLY ON A SURVIVING CYCLE, and
            # deciding that HERE was the bug: this predicted "ephemeral, so relax" from
            # the writer's durability, before `split_rest_points` had run. `finalize_db`
            # writes uncommitted `path_seg` and so predicted relaxed, but its loop closes
            # through `core_fp` which the split DOES break — so the edge relaxed for a
            # cycle that no longer exists. A prediction standing in for a measurement,
            # made one pass too early; the split is what knows, so it decides.
            g.edge(_cid, _pid, "roundtrip",
                   **({"style": "dashed"} if _hops else {}))

    # ⚑⚑⚑ THE LEGEND IS A NODE, like everything else here — an HTML-like table, which is the
    # operator's own technique for packing structured content into ONE first-order object
    # (`mikemol.github.io` 2018-02-04 §HTML-like labels: *"the layout engine treats the entire
    # label as a single node… being able to pack all of that information cleanly into the
    # boundary of a single node let me build a much cleaner graph"*).
    #
    # ⚑⚑ AND IT EXISTS BECAUSE THE GRAPH ENCODES SIX DISTINCTIONS THE READER CANNOT GUESS: three
    # provenances (derived-exact / declared / verb-scanned), three relation states (absent /
    # empty / populated), and the read-vs-return direction. Colour without a key is the failure
    # the operator's own colour section names — *"colours should be used for ACCENTING and
    # supplementing information, not as a primary differentiator"* — and until now every one of
    # these was carried by colour alone.
    # ⚑⚑⚑ AND IT IS GENERATED FROM `EDGE_STYLE` / `EDGE_MEANING`, not hand-kept beside them.
    # The hand-written version had already gone stale in the one way a legend can: it said
    # the python producers were *"DECLARED here"* — true when written, false two commits
    # later when they became derived. A legend restating a table by hand is the roster-beside-
    # the-declaration defect this whole file exists to retire, and it had one inside itself.
    # ⚑⚑⚑ EACH ROW CARRIES A NON-COLOUR MARK, and this is the whole a11y fix in one place.
    # The previous legend gave five edge kinds five hues and nothing else — two of them the
    # SAME hue — and gave the relation's three states ONE white swatch. A reader with a
    # red/green deficiency, a greyscale printout, or a low-contrast display got a key that
    # distinguished nothing. Every row now leads with an ASCII line pattern or a glyph that
    # survives all three, and the colour merely accents it.
    _rows = ['<tr><td colspan="3"><b>how to read this</b></td></tr>']
    for _k, _m in NODE_MEANING.items():
        _f = NODE_STYLE.get(_k, {}).get("fillcolor", "#ffffff")
        _rows.append('<tr><td bgcolor="%s"><b>%s</b></td><td>%s</td>'
                     '<td align="left">%s</td></tr>'
                     % (_f, NODE_MARK.get(_k, ""), _k, _m))
    # ⚑⚑ THE RELATION'S THREE STATES GET THREE ROWS. They were one row reading *"fill =
    # populated / EMPTY / ABSENT"* — a legend that NAMES a distinction it does not SHOW, for
    # the single most load-bearing fact in this diagram (whether a tier exists at all). Each
    # state now shows its own border treatment beside its own fill.
    for _st, _mk, _m in (
            ("populated", "───", "the tier exists and has rows (count in the label)"),
            ("EMPTY", "╌╌╌", "applied but 0 rows — dashed border"),
            ("ABSENT", "═══", "the tier was NEVER APPLIED — double border, and the label "
                              "says so")):
        _rows.append('<tr><td bgcolor="%s"><b>%s</b></td><td>relation</td>'
                     '<td align="left">%s: %s</td></tr>'
                     % ({"populated": "#e8f7ea", "EMPTY": "#fff8e1",
                         "ABSENT": "#fde8e8"}[_st], _mk, _st, _m))
    for _k, _m in EDGE_MEANING.items():
        _s = EDGE_STYLE.get(_k, {})
        _rows.append('<tr><td><font color="%s"><b>%s</b></font></td><td>%s</td>'
                     '<td align="left">%s</td></tr>'
                     % (_s.get("color", "#000000"), EDGE_MARK.get(_k, "———→"), _k, _m))
    _rows.append('<tr><td><b>⟳</b></td><td>AFTER</td><td align="left">a builder that READS '
                 'WHAT IT WRITES — split into before/after so the fixpoint is a DAG, not a '
                 'cycle</td></tr>')
    _rows.append('<tr><td><b>⚑</b></td><td>no caller</td><td align="left">no literal '
                 '`QB.run` site; 11 run sites pass a computed name and cannot be '
                 'attributed</td></tr>')
    g.node("legend", "<<table border=\"0\" cellborder=\"1\" cellspacing=\"0\" "
                     "cellpadding=\"4\">%s</table>>" % "".join(_rows), "other",
           shape="none", margin="0", style="")
    # ⚑ THE GRAPH IS REACHABLE FROM THE TEXT, so a caller that wants to QUERY does not have
    # to re-run the build or re-parse the output. `dot()` keeps returning a string because
    # every existing caller wants one; `graph()` is the structural door.
    # ⚑⚑ SPLIT THE REST POINTS LAST, once every edge is in. Running it earlier would
    # split against a partial graph and miss a cycle a later edge closes — which is
    # exactly what the round-trip edge did to the recursive-builder split that already
    # existed. One pass over the finished value, driven by the traced cycles.
    # ⚑ THE PRODUCER SPLIT RUNS FIRST, because it changes which nodes exist and the rest
    # point split reads the finished edge set. Both are one rule on two nouns: a node
    # standing for several positions in the flow is drawn as several nodes in a lane.
    g.split_multistep_producers()
    g.split_rest_points()
    _s = serialize(g, "substrate ingest — generated from lifecycle.LIFECYCLE + "
                      "schema_decl._TIERS", eng)
    dot.last_graph = g
    return _s


_GRAPH_MEMO = {}


def graph(**kw):
    """The `Graph` value — build it and hand back the structure, not the text.

    ⚑ THE STRUCTURAL DOOR. Every query (`--cycles`, `--edges`, the acyclicity gate) goes
    through here; only `--out` and stdout want the serialization. That ordering is the fix
    for going *"straight from analysis to dot"*: the picture is downstream of the value, so
    a formatting choice cannot change an answer.
    """
    # ⚑ MEMOISED ON IDENTITY OF THE INPUTS. A selftest that asks three questions of the same
    # graph rebuilt it three times — each rebuild re-walking the corpus for producers and
    # consumers — and pushed the suite past a 120s timeout. The build is deterministic over
    # its arguments, so the repeat bought nothing; same reasoning as `_CONSUMERS_MEMO`.
    _k = tuple(sorted((k, id(v)) for k, v in kw.items()))
    if _k not in _GRAPH_MEMO:
        dot(**kw)
        _GRAPH_MEMO[_k] = dot.last_graph
    return _GRAPH_MEMO[_k]


# ⚑⚑⚑ STYLE IS A FUNCTION OF KIND, AND THIS TABLE IS THE ONLY PLACE IT IS DECIDED. While
# the DOT text was the only representation, a colour WAS the kind — `--edges` recovered an
# edge's meaning by matching `"#8899aa"`, so a restyle would have silently rewritten the
# census. Now the kind is carried on the edge and the colour is looked up here; the two can
# no longer disagree, and the legend below can be generated from this same table rather than
# hand-kept beside it.
# ⚑⚑⚑ EVERY KIND IS SEPARABLE WITHOUT COLOUR, which the first cut was not (operator,
# 2026-08-15, on the legend: *"Take a look through summit about a11y. Because this needs
# work."*). Five edge kinds were distinguished by HUE ALONE — and two of them, `flow` and
# `returns`, shared `#bb8822` outright, so even a reader with full colour vision could not
# tell them apart from the swatch. For anyone with a colour-vision deficiency (~8% of men
# for red/green, which `write`=#227722 vs `flow`=#bb8822 sits directly on) the legend
# carried no information at all.
#
# ⚑⚑ SO THE CARRIER IS SHAPE, NOT HUE: each kind gets a distinct (style, arrowhead)
# PAIR, and colour becomes the accent it should always have been — the operator's own rule
# (`mikemol.github.io`, colour section): *"colours should be used for ACCENTING and
# supplementing information, not as a primary differentiator."* The legend's swatches are
# generated from this table, so a reader matches the LINE PATTERN and never the colour.
#
# ⚑ AND THE PATTERNS ARE ORDERED BY DIRECTNESS, so the picture reads without the legend:
# solid = data moving into a query, bold-solid = data landing in a store, dashed = a value
# handed to python, dotted = an annotation. A reader who never opens the key still sees
# "solid means read, heavy means write".
# ⚑⚑⚑ EPHEMERALITY IS A GRADE, NOT A BIT (operator: *"Something that exists on disk?
# Very not-ephemeral. Something that only exists as passed row references? Very
# ephemeral. Something that gets stored into CTE temp tables? Somewhat ephemeral."*).
# `is_at_rest` returned a boolean and so had to force a staging tier into the same bucket
# as either an append-only log or a row reference — and the collapse showed: the three
# `treestage`/`valstage` relations read as "at rest" because nothing writes them yet,
# which is true about the evidence and wrong about the kind.
#
# ⚑⚑ THE GRADE IS AN ORDER, AND THE SPLIT READS A THRESHOLD ON IT rather than a class
# membership. That is the difference between "which bucket is this in" and "does this
# persist across the step I am drawing" — the second is answerable per question, and a
# CTE is above the line for a statement-level graph and below it for a tier-level one.
DURABILITY = {
    # ⚑⚑ THE RUNGS ARE MECHANICAL — what physically holds the bytes between two steps,
    # and what a crash loses. NOT tier membership, which is an ORGANISATIONAL fact: a
    # tier says which subsystem owns a relation, never how long its rows survive.
    "disk": 4,        # a file outside the store; survives dropping the whole database
    "committed": 3,   # a table whose writer COMMITS; survives a process death
    "uncommitted": 2, # a table written inside a transaction the step still holds open
    "cte": 1,         # named inside ONE statement; gone when that statement ends
    "inflight": 0,    # python-side rows between a fetch and the next execute
}

# ⚑ THE SPLIT NEEDS BYTES THAT OUTLIVE THE STEP BEING DRAWN. A committed table does; an
# open transaction's table does not, because the step that wrote it is the step reading
# it back. `>= committed` is the line, and everything below is left visible for
# `--cycles` rather than given a fictional before/after.
SPLIT_FLOOR = DURABILITY["committed"]


def durability(rel, reads=None, writes=None):
    """How long `rel`'s rows survive — a MECHANICAL grade, not a tier lookup.

    ⚑⚑⚑ THE MECHANICS, NOT THE TIERING (operator: *"You're over-indexing on tiering, and
    under-indexing on actual dataflow semantics and mechanics"*). Three cuts of this
    function read `schema_decl._TIERS` and mapped tier names to durability — first as a
    hardcoded `DERIVED_TIERS` roster, then as a `staged` rung keyed on
    `treestage`/`valstage`. A tier is who OWNS a relation; it says nothing about what
    holds the bytes. `dec_stage` being in a tier called "treestage" is a naming
    coincidence I was reading as evidence.

    ⚑⚑ WHAT ACTUALLY DECIDES IT, per rung:
      · `inflight` — not a relation at all: rows between `fetchall()` and the next
        `execute`. Every `--roundtrips` entry passes through this rung by construction,
        which is exactly why those loops are real and unsplittable.
      · `cte` — named inside one statement. `q_pack_level_insert`'s `WITH w AS (INSERT …
        RETURNING …)` is the live instance: `w` holds a level's rows and does not exist
        before or after that statement.
      · `uncommitted` — written by a step that has not committed. `pack_core_sql`'s own
        docstring records this: it does NOT commit, so a core is atomic and a restart
        redoes it. Its `obs_node` writes are uncommitted FOR THE DURATION OF THE FOLD.
      · `committed` — the writer commits, so a later process sees the rows.
      · `disk` — outside the store entirely; the `.agdai` cores.

    ⚑ AND `commits` IS READ FROM THE CODE, not asserted: a producer whose body (or whose
    callees) reaches `con.commit()` writes committed rows. That is a `--reaches` query,
    the same instrument the round-trip trace uses.
    """
    # ⚑ MEMOISED PER RELATION. `split_rest_points` calls this for every node on every
    # cycle, up to 8 rounds, and each call walked `producers()` and `roundtrips()` — the
    # selftest went past 600s twice. The grade is a property of the corpus, not of the
    # round, so it is computed once.
    if rel in _DURABILITY_MEMO:
        return _DURABILITY_MEMO[rel]
    reads = builder_edges()[0] if reads is None else reads
    writes = builder_edges()[1] if writes is None else writes
    if rel == "agdai":
        return _DURABILITY_MEMO.setdefault(rel, DURABILITY["disk"])
    # ⚑ A NAME NO STATEMENT DECLARES AS A TABLE is rows in flight — the python side of
    # every round trip. Not a catalogue lookup: the graph's own write edges are the
    # authority for what is written AS a relation.
    _written = {r for rels in writes.values() for r in rels}
    _written |= {r for rels in producers().values() for r in rels}
    if rel not in _written and rel not in {r for rels in reads.values() for r in rels}:
        return _DURABILITY_MEMO.setdefault(rel, DURABILITY["inflight"])
    # a relation whose only writer holds its transaction open across the read-back is
    # uncommitted for that span — the fold's own intermediate
    #
    # ⚑ THE CALL GRAPH IS BUILT ONCE, NOT PER RELATION. The first cut called
    # `callgraph()` inside this function, which the split loop calls per node — a
    # whole-corpus CST walk per relation, and the run passed 600s. Fourth instance of
    # this same lesson in one file; the cache belongs at the point the corpus is touched.
    for fn, rels in producers().items():
        if rel not in rels:
            continue
        if not _commits(fn):
            return _DURABILITY_MEMO.setdefault(rel, DURABILITY["uncommitted"])
    return _DURABILITY_MEMO.setdefault(rel, DURABILITY["committed"])


_DURABILITY_MEMO = {}
_COMMITS_MEMO = {}


_CG_MEMO = {}


def _callgraph(paths=("scripts", "jea")):
    """The corpus call graph, built once — `roundtrips` and `_commits` both read it."""
    if paths not in _CG_MEMO:
        _CG_MEMO[paths] = _pycodemod.callgraph(_py_files(*paths))
    return _CG_MEMO[paths]


def _commits(fn):
    """Does `fn` reach a `commit()` — the mechanical test for 'these rows survive'."""
    if fn not in _COMMITS_MEMO:
        _COMMITS_MEMO[fn] = bool(_pycodemod.reaches(_callgraph(), fn, {"commit"}))
    return _COMMITS_MEMO[fn]


def is_at_rest(rel, reads=None, writes=None):
    """Does `rel` HOLD data between steps, or is it REGENERATED from another relation?

    ⚑⚑⚑ DERIVED FROM THE GRAPH, NOT LISTED. A first cut declared
    `DERIVED_TIERS = ("sppf", "orbit", …)` with a comment claiming that was not a frozen
    roster because tier MEMBERSHIP came from `schema_decl` — the operator: *"Um, it
    absolutely is a frozen roster. Sure, a relation added to sppf or orbit is covered.
    But what about something added to DERIVED_TIERS? Or something that SHOULD be added to
    DERIVED_TIERS?"* Both directions were unhandled, and the second is the dangerous one:
    a tier that should be derived and is not listed defaults to AT REST and gets split —
    absent-read-as-pass, in the same function whose own comment forbids it.

    ⚑⚑ THE STRUCTURAL FACT IS ALREADY IN THE FLOW: a relation is DERIVED exactly when a
    step inside the pipeline writes it FROM other relations — a projection. A relation
    written only by the ingest (from `.agdai` on disk, outside the store) is where data
    enters and rests; nothing in the graph can rebuild it. So the question "is this
    regenerated" is "does a builder write it", which the write edges answer and which
    updates itself when a new projection lands.

    ⚑ AND THE INGEST IS DISTINGUISHED BY ITS SOURCE, not by name: `_insert_decoded`
    writes from decoded cores, so its targets are entry points. A python producer that
    ALSO runs builders is a projection (that is what `roundtrips` detects), and its
    targets are derived.
    """
    # ⚑ A THRESHOLD READ ON THE GRADE, not a second implementation of it. This name is
    # kept because the SPLIT's question is genuinely boolean — split or do not — but the
    # judgement lives in `durability` and the line is `SPLIT_FLOOR`, so moving the line
    # is a one-token edit rather than a rewrite of a predicate.
    return durability(rel, reads, writes) >= SPLIT_FLOOR


_WORDER_MEMO = {}


def write_order(paths=("scripts", "jea")):
    """{function: {relation: source position}} — the order its writes appear in the body.

    ⚑⚑⚑ A FACT ABOUT THE CODE, WHICH IS THE WHOLE POINT. The producer split needs to know
    which write comes first, and the tempting answer was to measure how deep each target
    sits in the drawn graph. That is recursive: the split changes the graph, the graph
    changes the depths, and the criterion ends up disagreeing with the split it licensed —
    a diagram whose content depends on how many times the layout ran.

    ⚑⚑ THE LINE NUMBER IS ALREADY IN THE CENSUS. `--values upsert 1` returns
    `(path, line, relation, ctx)` per call site, so the order is a free read of data
    `producers()` already fetches and discards. No new scan, no second authority.

    ⚑ AND IT IS THE SEQUENCE THE SPLIT IS CLAIMING. `project_sppf` writes `_node` before
    `node_child` before `unit_node` because later rows reference earlier ids; the source
    order IS the step order, not a proxy for it.
    """
    if paths not in _WORDER_MEMO:
        rows, _n = _slot_census(paths)["upsert"]
        out = {}
        for path, line, rel, ctx in rows:
            if ctx == "_selftest" or rel is _UNKNOWN:
                continue
            mod = os.path.splitext(os.path.basename(path))[0]
            out.setdefault("%s.%s" % (mod, ctx), {})[rel] = line
        _WORDER_MEMO[paths] = out
    return _WORDER_MEMO[paths]


def roundtrips(paths=("scripts", "jea")):
    """{function -> ([builders it runs], [relations it writes])} — the SQL→python→SQL loop.

    ⚑⚑⚑ THE CLOSING EDGE, AND WITHOUT IT THE GRAPH IS A FAN RATHER THAN A PIPELINE
    (operator, 2026-08-15: *"much (most?) of the time, something comes out of sql to go
    into python to go right back into sql — either as an insert or as part of a predicate
    or union"*). `consumers()` and `producers()` are BOTH keyed by function, so the join
    is already in the data and nothing was reading it: a function appearing on both sides
    took rows out of postgres and put rows back.

    ⚑⚑ THE GRAPH WAS DRAWING ONE FUNCTION AS TWO UNRELATED NODES. `sppf_db.project_sppf`
    appeared as `c_…project_sppf` (receiving from five builders) and `p_…project_sppf`
    (writing six relations), with no edge between them — so the diagram showed data
    arriving in python and, separately, data appearing in relations, and stopped. That is
    the same absence-drawn-as-a-gap defect as the orphan sink, one level up: the fact is
    that these are ONE step, and it was expressible as an identity nobody joined on.

    ⚑ THREE TODAY, and the biggest is the one this arc is replacing: `project_sppf` runs
    `edge_all`/`event_ctor`/`event_head`/`obs_all`/`project_stats` and writes `_node`,
    `node_child`, `_unit`, `_unit_cod`, `unit_node`, `obs_node` — the python packing fold
    whose whole existence is the round trip `q_pack_level_insert` was built to remove.
    """
    # ⚑ MEMOISED — `callgraph()` walks the whole corpus, and this is called once per
    # graph build. The unmemoized version pushed the selftest past 300s, the same way
    # `producers`/`consumers` did before them. Third instance of one lesson: any function
    # here that touches the corpus needs the cache at the point it is written.
    if paths in _ROUNDTRIP_MEMO:
        return _ROUNDTRIP_MEMO[paths]
    cons, prods = consumers(paths), producers(paths)
    # ⚑ THE CONSUMER SIDE IS KEYED builder→[functions] AND THE PRODUCER SIDE
    # function→[relations], so the consumer map is inverted here rather than at its
    # source: `--consumers` answers "who runs this builder", which is the question that
    # mode exists for, and re-keying it there would break it to serve this one.
    by_fn = {}
    for b, fns in cons.items():
        for fn in fns:
            by_fn.setdefault(fn, []).append(b)
    out = {fn: (sorted(by_fn[fn]), list(prods[fn]))
           for fn in sorted(set(by_fn) & set(prods))}

    # ⚑⚑⚑ AND THE SAME-BODY JOIN IS NOT ENOUGH (operator: *"You'll also need to trace
    # transient dependencies through the python call graph"*). A function that runs a
    # builder and writes through a HELPER has its read and its write in two different
    # bodies, so the intersection above sees no round trip where there is one. Measured:
    # `_do_promote` runs `unprojected_cores` and `node_id_top`, then delegates the write
    # to `pack_core_sql` — a round trip the direct join reports as two unrelated halves.
    #
    # ⚑⚑ THE CALL GRAPH IS `pycodemod --reaches`, a mode that did not exist an hour ago
    # because `--calls` structurally could not answer it: its scanner records call sites
    # with NO scope tracking, so it says WHERE a name is called and never WHICH FUNCTION
    # calls it. Reachability needs the caller, so the whole class was unanswerable.
    #
    # ⚑ AN INDIRECT ROUND TRIP IS MARKED, NOT MERGED. A direct one is a single step doing
    # both; an indirect one is a chain, and reporting them identically would claim the
    # write happens where it does not. The path is carried so a reader can see the hop.
    # ⚑ ONE CALL GRAPH, SHARED WITH `_commits`. Both need it, both built it, and
    # `--profile` charged 174s to `roundtrips` and 156s to `callgraph` — overlapping
    # cost, one structure. Memoised in `_commits` because that is where it is first
    # needed; read from there rather than rebuilt here.
    _cg = _callgraph(paths)
    _writers = set(prods)
    for fn in sorted(by_fn):
        if fn in out:
            continue
        hit = _pycodemod.reaches(_cg, fn, {w.rsplit(".", 1)[-1] for w in _writers})
        for _tgt, path in sorted(hit.items()):
            _via = next((w for w in _writers if w.rsplit(".", 1)[-1] == _tgt), None)
            if _via and _via != fn:
                # ⚑ THE WRITER IS RETURNED, NOT RE-DERIVED BY THE CONSUMER. A first cut
                # had the graph guess which producer node an indirect trip pointed at by
                # substring-matching the last hop against node ids — the fragile
                # name-matching this session has removed three times. `_via` is the
                # writer; carrying it costs one tuple slot.
                out[fn] = (sorted(by_fn[fn]), list(prods[_via]), path, _via)
                break
    _ROUNDTRIP_MEMO[paths] = out
    return out


def _hue(name):
    """A stable per-NAME colour for an edge's source half — identity, not state.

    ⚑⚑ NOT FROM THE OKABE-ITO POOL, DELIBERATELY, and the reason is the constraint
    el-openglo measured: only four of its seven members clear 3:1 on white, and those
    four are spent on the five edge KINDS. Identity needs many more than four, so it
    cannot come from the same pool without either colliding with a kind or dropping
    below the ground floor.

    ⚑ SO IT IS A HUE CIRCLE AT FIXED SATURATION AND LIGHTNESS, which keeps every member
    at the same contrast against the page — the property the pool selection was
    protecting — while giving as many distinguishable values as there are relations.
    The KIND is still carried by the second half of the stroke plus its dash/arrow
    pattern, so a reader who cannot separate two hues still reads "this is a read".
    """
    import colorsys, hashlib
    h = int(hashlib.sha1(name.encode()).hexdigest()[:8], 16) / 0xffffffff
    r, g, b = colorsys.hls_to_rgb(h, 0.38, 0.85)
    return "#%02x%02x%02x" % (int(r * 255), int(g * 255), int(b * 255))


def _ink(name, against=None):
    """A palette member DARKENED until it reads against its own fill — derived, not typed.

    ⚑⚑ THIS IS `stretch_lit`'S RULE, ONE LEVEL DOWN. el-openglo pushes a colour AWAY from
    its ground until a contrast target is met and stops at a CHROMA FLOOR, because
    continuing past it wins the contrast number by destroying the hue — *"don't crush to
    a hueless black to win a contrast metric"*. A border sitting ON a saturated fill has
    that same three-body shape, so it gets the same treatment rather than a guess.

    ⚑ THE LOCAL FORM IS A FIXED DARKENING RATIO, and saying so is the honest bound: the
    real `stretch_lit` needs numpy + colorspacious to evaluate its chroma floor, which
    substrate's env does not carry (see `_okabe_ito`'s fallback). A ratio applied in sRGB
    is a WEAKER instrument than theirs — it cannot see when it has crossed the floor — so
    it is deliberately shallow (0.55) rather than pushed to a target it cannot verify.
    `ask-cvd-graphviz-theme` is the ask that would replace this with the measured form.
    """
    base = _okabe_ito().get(name)
    if base is None:
        raise KeyError("%r is not an Okabe-Ito member" % name)
    return "#%02x%02x%02x" % tuple(int(x * 0.55) for x in base)


def _ok(name):
    """An Okabe-Ito member by NAME, as graphviz hex — resolved from el-openglo's palette.

    ⚑⚑⚑ THE PALETTE IS NAMED AT THE CALL SITE AND THE HEX IS DERIVED, so this file never
    transcribes a colour. My first cut pasted seven hexes into `EDGE_STYLE` with the member
    names in trailing comments — a copy of someone else's measured constant, which drifts
    silently the moment they revise it and which no gate here could ever catch.

    ⚑⚑ AND THE FALLBACK IS THE HONEST PART. `cvd_gate` is a PEER REPO's module and this repo
    does not depend on it; when it is not importable the built-in table answers, and the
    values are stamped with where they came from. A hard import would make substrate's
    diagram unbuildable because a sibling checkout moved — the coupling a shared constant
    must not create. `--palette` reports WHICH source answered, so "derived" and "fallback"
    are never confused.

    ⚑ `neutral` IS NOT AN OKABE-ITO MEMBER. The palette's seven are all chromatic accents;
    an annotation edge wants something recessive, so it is named here as a local role rather
    than pretended into the palette.
    """
    if name == "neutral":
        return "#56514c"
    rgb = _okabe_ito().get(name)
    if rgb is None:
        raise KeyError("%r is not an Okabe-Ito member (%s)"
                       % (name, ", ".join(sorted(_okabe_ito()))))
    return "#%02x%02x%02x" % tuple(int(x) for x in rgb)


# ⚑ THE FALLBACK TABLE, stamped. Okabe & Ito (2008) Color Universal Design, chromatic
# members — the published palette, not a local invention, so a fallback is a citation
# rather than a guess.
_OKABE_ITO_FALLBACK = {
    "orange": (230, 159, 0), "sky": (86, 180, 233), "bluegreen": (0, 158, 115),
    "yellow": (240, 228, 66), "blue": (0, 114, 178), "vermillion": (213, 94, 0),
    "purple": (204, 121, 167),
}
_PALETTE_SOURCE = [None]


def _okabe_ito():
    """The palette, from el-openglo's `cvd_gate` when reachable, else the stamped table."""
    if _PALETTE_SOURCE[0] is None:
        try:
            sys.path.insert(0, os.path.join(os.path.dirname(REPO), "el-openglo"))
            import cvd_gate
            _PALETTE_SOURCE[0] = ("cvd_gate (el-openglo)", dict(cvd_gate.OKABE_ITO))
        except Exception:
            _PALETTE_SOURCE[0] = ("built-in fallback (Okabe & Ito 2008)",
                                  dict(_OKABE_ITO_FALLBACK))
    return _PALETTE_SOURCE[0][1]


# ⚑⚑⚑ THESE HEXES ARE MEASURED, NOT CHOSEN — by `cvd-contrast-gate` (owner el-openglo),
# the registered capability, pointed at this exact table. My hand-picked set failed 9 of 16
# pairs: `write`~`returns` at dE 2.75 under protanomaly was a collision I CREATED this
# session while splitting `returns` off `flow`'s shared hue, and could not have seen without
# a Machado simulation. The floor is dE 11.0, derived from Okabe-Ito's own tightest pair
# (orange~purple under tritanomaly) rather than picked.
#
# ⚑⚑ SO THE ACCENTS COME FROM OKABE-ITO, whose whole design property is CVD separation —
# reaching for a palette that is already solved beats nudging hexes until a checker goes
# quiet, which is what I would have done with a checker of my own.
EDGE_STYLE = {
    "read":    dict(color=_ok("blue"), arrowhead="vee", style="solid"),
    "write":   dict(color=_ok("bluegreen"), arrowhead="normal", style="solid",
                    penwidth="2.2"),
    "pywrite": dict(color=_ok("purple"), arrowhead="normal", style="solid",
                    penwidth="2.2", arrowtail="dot", dir="both"),
    "flow":    dict(color=_ok("vermillion"), arrowhead="vee", style="dashed",
                    penwidth="1.6"),
    "returns": dict(color=_ok("neutral"), arrowhead="none", style="dotted"),
    # ⚑ THE ROUND TRIP CLOSES THE LOOP, so it gets the heaviest weight in the table: it
    # is the edge that turns a fan into a pipeline, and it is dashed when the write
    # happens through a call-graph hop rather than in the same body.
    #
    # ⚑⚑⚑ AND IT SHARES `flow`'s HUE BECAUSE THE POOL RAN OUT, not because I chose to.
    # el-openglo solved the assignment under a WHITE-GROUND constraint and found only
    # FOUR of the seven Okabe-Ito members clear WCAG's 3:1 non-text minimum as a stroke
    # on white — blue 5.19, vermillion 3.87, bluegreen 3.42, purple 3.06; sky 2.31,
    # orange 2.25, yellow 1.32 do not. Six chromatic roles on a white page is INFEASIBLE
    # over this palette, and their solver refuses rather than placing two below the floor.
    #
    # ⚑⚑ SO MY HAND-ASSIGNMENT WAS THE CONSTRAINED OPTIMUM, AND THE REUSE WAS FORCED.
    # Not "five eligible, six roles, I reused one" — that still reads as a preference I
    # could have declined. Measured: FIVE FREE ROLES ON WHITE ALSO REFUSES, because four
    # eligible members cover four free roles. With `roundtrip` free there is NO assignment
    # at all; pinned, the solver re-derives my exact four colours and my exact reuse.
    # I called the shared hue free and it was the only move on the board.
    #
    # ⚑ WHICH IS A DEFECT CLASS OF ITS OWN: the OUTPUT was right and the RECORD OF WHY
    # was wrong. No check catches that — the artifact passes everything — and nothing
    # measures it except someone re-deriving the decision from outside. That is what a
    # peer with the instrument this repo cannot run was actually for.
    #
    # ⚑ `neutral` FOR `returns` IS THEREFORE RIGHT FOR A REASON NEITHER OF US HAD. Not
    # "off-palette and that is a shame" but "the palette has no member that works there":
    # yellow is the worst on white at 1.32:1, so `returns` could not take it as a stroke
    # even with a slot free. The off-palette colour is the answer, not a hole.
    "roundtrip": dict(color=_ok("vermillion"), arrowhead="normal", penwidth="2.6",
                      arrowtail="odot", dir="both"),
    # ⚑ AN IDENTITY, NOT A FLOW — so it carries arrowheads at BOTH ends and no fill of
    # its own colour vocabulary: `dir=both` with open tees reads as "these are the same
    # thing", where every single-headed arrow here reads as "this becomes that". Drawn in
    # the recessive neutral for the same reason the return-note is: it annotates the
    # graph rather than participating in it.
    # ⚑⚑⚑ NO `weight`, AND MY EARLIER `weight="0"` WAS BACKWARDS. `dot` ranks by minimising
    # Σ(weight × rank-span) over constrained edges, so weight is HOW BADLY THE LAYOUT WANTS
    # THIS EDGE SHORT — it does not decide whether the edge forces a gap. A constrained
    # edge demands ≥1 rank at ANY weight, including zero.
    #
    # ⚑⚑ SO `weight=0` DID THE OPPOSITE OF WHAT I SET IT FOR. I wanted the step chain to be
    # compressible ("it's OK for the cluster to get stretched"); zero weight means the
    # solver pays NOTHING to keep it at full length, so the ladder became rigid for free
    # and nothing could squeeze it. Measured: 5 steps × 1 rank = 4 ranks above the relation
    # floor at y=26.1, and step 5 lands exactly ON the floor, level with `unit_node`.
    #
    # ⚑ REMOVED RATHER THAN RETUNED, because I could not state what value was right. A knob
    # set to a number I cannot justify is a guess wearing a parameter's clothes — and this
    # one was introduced to fix a symptom whose actual cause (see `split_multistep_
    # producers`) is chain length against available headroom, which no weight addresses.
    "sameas":  dict(color=_ok("neutral"), style="dashed", penwidth="1.2",
                    arrowhead="tee", arrowtail="tee", dir="both"),
    "stage":   dict(style="dashed", color="#334455", penwidth="1.8"),
    "hint":    dict(style="dotted", arrowhead="none", color="#888888"),
    "other":   dict(color="#555555"),
}

# ⚑ WHAT EACH KIND MEANS, beside the style that renders it, so the legend is a JOIN of the
# two rather than a third copy. A kind with no entry here is deliberately un-legended (the
# structural furniture: stages, labels, the source folder).
# ⚑⚑ THE ASCII SWATCH FOR EACH KIND — the carrier a colour-blind, greyscale or low-contrast
# reader actually uses. Kept BESIDE `EDGE_STYLE` rather than derived from it, because the
# mapping (dotted→`- - >`, penwidth 2.2→`━━▶`) is a rendering judgement, not a lookup; a
# generated approximation would silently stop matching the line it stands for.
EDGE_MARK = {
    "read":    "───▶",
    "write":   "━━━▶",
    "pywrite": "●━━▶",
    "flow":    "╌╌╌▶",
    "roundtrip": "◦━━▶",
    "sameas":  "⊣╌╌⊢",
    "returns": "······",
    "stage":   "╌╌╌",
    "hint":    "······",
}

# ⚑ AND `producer` / `consumer` NEEDED SPLITTING TOO — they shared a fill (#f3ecff) AND
# would have shared a mark, so the legend listed two rows a reader could not tell apart.
# They are opposite ends of the flow (one writes a relation, one reads a builder's result),
# which is exactly what the arrows encode.
# ⚑⚑⚑ THE MARK IS THE GRAPHVIZ SHAPE NAME, NOT AN INVENTED GLYPH. These were `⬡`, `▤▶`,
# `▶▤`, `▭` — pictograms I drew for the key that appear NOWHERE in the graph, so a reader
# holding the legend beside the picture could not match a single node to its row. The
# builders render `component`, producers `invhouse`, consumers `house`, relations `box`.
# A key whose swatches are not the thing being keyed is decoration.
#
# ⚑⚑ NAMED RATHER THAN DRAWN, and that is a real limit worth stating: the legend is one
# HTML-like label, and an HTML table cannot contain graphviz NODES — only text and
# images. So the choices were an invented glyph (wrong), a separate legend subgraph of
# real nodes (a second layout problem, and clusters are what the operator's own post
# warns against), or the shape's NAME as text. The name is checkable against the DOT and
# against graphviz's own vocabulary, which the glyph never was.
NODE_MARK = {
    "builder":  "component",
    "producer": "invhouse",
    "consumer": "house",
    "relation": "box",
}

# ⚑⚑⚑ EVERY MEANING NAMES ITS ENDPOINTS, because the arrowhead alone is ambiguous
# (operator, 2026-08-16: *"I don't know if orbit_member reads q_orbit_merged, or if
# q_orbit_merged and q_orbit_packing read orbit_member"*). `read` runs relation→builder
# and `flow` runs builder→consumer; both are a plain vee, so a reader looking at an arrow
# between a box and a component cannot tell which claim is being made. Prose that says
# "READS" does not help when the question is WHICH END READS.
#
# ⚑⚑ SO THE FORM IS `<tail kind> → <head kind>: <what it means>` — the shape at each end
# is the disambiguator, and the legend now states the pairing rather than leaving it to
# be inferred from an arrowhead that four kinds share.
EDGE_MEANING = {
    "read":    "relation → builder: the builder SCANS that relation",
    "flow":    "builder → consumer: the python function that RUNS the builder",
    "returns": "builder → note: the columns it hands back (annotation, no direction)",
    "write":   "builder → relation: what the statement LANDS",
    "pywrite": "producer → relation: a python write through `upsert` "
               "(dot at the PRODUCER end)",
    "roundtrip": "consumer → producer: SQL out, python, SQL back in "
                 "(dashed = the write happens through a call-graph hop)",
    "sameas": "before → after: the SAME relation at two times, not a flow — "
              "writes land in the after-copy, reads take the before-copy",
}

NODE_MEANING = {
    "builder":  "compiled SQL, derived from the registry",
    "producer": "python writer, derived from `upsert`'s relation slot",
    "consumer": "python function that runs a builder, derived from `QB.run`",
    "relation": "a stored relation (fill = populated / EMPTY / ABSENT)",
}

NODE_STYLE = {
    # ⚑⚑ BLACK LABEL TEXT, MEASURED — I wrote `fontcolor="#ffffff"` here with a comment
    # asserting white "passes too and by a wider margin", then measured it: black wins on
    # five of seven fills and white FAILS at 2.25:1 on the producer's orange. The comment
    # was the assertion-in-place-of-measurement this whole exchange has been about, made
    # in the very edit correcting it. Black is the default because 4.05:1 is the worst
    # black case and 2.25:1 is the worst white one.
    "relation":  dict(shape="box", style="filled"),
    # ⚑⚑⚑ `a:b` IS A BANDED FILL, and it carries a SECOND fact in the same swatch
    # (operator: *"graphviz supports color:banding, so you have some more options if you
    # want to encode more information"*). A builder is compiled SQL that both READS and
    # is RUN BY python, so its fill bands the read hue into the flow hue — the node
    # states its own position in the pipeline rather than being one flat colour that
    # means "builder" and nothing else.
    #
    # ⚑⚑ AND BANDING IS A NON-COLOUR CUE TOO, which is why it belongs here rather than
    # in a palette tweak: a band BOUNDARY is a visible edge under greyscale and under
    # every CVD view, so it survives exactly where a hue difference does not. That is
    # mat230's ruler-sequence principle — *"the structure is carried by the PATTERN, not
    # by colour and not by thickness"* — reached through a graphviz feature rather than
    # LaTeX table rules.
    # ⚑ THE BAND RUNS SKY→BLUE, LIGHT END FIRST, so ONE font colour serves both stops.
    # Measured: black reads 9.10:1 on `sky` and 4.05:1 on `blue`, white reads 2.31:1 and
    # 5.19:1 — the two stops want OPPOSITE text colours, and a banded fill has only one
    # `fontcolor`. Ordering the band light-first keeps the label over the light stop,
    # where black is unambiguous. A banded fill is not free: it constrains the text.
    # ⚑⚑ AND IT CARRIES A BORDER, because the fill is 2.31:1 against the page — under
    # WCAG's 3:1 non-text minimum, so the node's OUTLINE would be the thing a low-vision
    # reader cannot find. Measured, not assumed: the relation states clear 3:1 on their
    # own and these two do not, which is a real difference between them rather than a
    # uniform "add a border everywhere".
    "builder":   dict(shape="component", style="filled",
                      fillcolor="%s:%s" % (_ok("sky"), _ok("blue")),
                      gradientangle="270", fontsize="9",
                      color=_ink("blue"), penwidth="1.4"),
    # ⚑ MEASURED AT dE 0.00 — IDENTICAL. `producer` and `consumer` shared one fill AND one
    # shape, so no reader of any vision could tell them apart from the node alone. They are
    # opposite ends of the flow, so the shape now says which end: a producer feeds the store
    # (`invhouse`, pointing in), a consumer receives from a builder (`house`, pointing out).
    # ⚑ THE PRODUCER/CONSUMER PAIR MEASURED AT dE 0.00 — IDENTICAL FILLS. They are
    # opposite ends of the flow, so both the shape (pointing in / pointing out) and now
    # the fill say which end, at full saturation rather than as two indistinguishable
    # lavenders.
    "producer":  dict(shape="invhouse", style="filled", fillcolor=_ok("orange"),
                      fontsize="9", color=_ink("orange"), penwidth="1.4"),
    "consumer":  dict(shape="house", style="filled", fillcolor=_ok("purple"),
                      fontsize="9", color=_ink("purple"), penwidth="1.4"),
    "returns":   dict(shape="note", style="filled", fillcolor="#fffdf0", fontsize="8"),
    "stage":     dict(shape="ellipse", style="filled", fillcolor="#e8eef7"),
    "label":     dict(shape="plaintext", style="none", fontsize="8", fontcolor="#555555"),
    "source":    dict(shape="folder", style="filled", fillcolor="#f5f5f5"),
    "sink":      dict(shape="octagon", style="filled", fillcolor="#fde8e8"),
    "other":     dict(shape="box", style="filled"),
}


def serialize(g, title="", eng="dot"):
    """The Graph as DOT — the ONLY place structure becomes text.

    ⚑⚑ EVERY QUERY READS `g`, NOT THIS OUTPUT. That is the whole point of the split: the
    picture is one rendering of the value, so `--cycles`, `--edges` and the selftest gates
    cannot be broken by a formatting choice made here, and cannot silently disagree with
    what is drawn.
    """
    # ⚑ THE ENGINE IS DECLARED IN THE SOURCE, not chosen on the command line (operator:
    # *"I usually use the `layout` attribute to select engines"*) — which is also what lets
    # the podman container answer for EVERY engine with one `dot` invocation.
    # ⚑⚑⚑ STRIPPED TO BARE MINIMUM (operator, 2026-08-16: *"strip every layout-affecting
    # attribute and re-render. And then we can figure it out from there"*). Removed:
    # `splines=true`, `nodesep`, `ranksep="0.6 equally"`, `concentrate=true`, `rankdir=TB`,
    # and the `fdp` branch's `overlap`/`sep`/`esep`/`K`. Every one was added to fix a
    # symptom, and three separate knobs have now been MEASURED INERT (`rank=false` is not a
    # graphviz value, `weight=0` changed nothing when removed, this whole preamble existed
    # twice with one copy dead). A baseline is the only thing that makes the next
    # measurement mean anything.
    #
    # ⚑⚑ `concentrate=true` IS THE ONE I MOST WANT GONE. It merges parallel edge segments,
    # which changes what the ranking pass sees as distinct edges — so it can move ranks,
    # and the agent flagged it as an unquantified variable in exactly the measurement I was
    # using to diagnose ranks. A diagnostic knob that perturbs the thing being diagnosed.
    #
    # ⚑ `layout=` STAYS because it selects the ENGINE rather than tuning one, and the
    # operator's own practice is to choose engines that way. Everything else returns only
    # if a measurement asks for it BY NAME.
    out = ['digraph pipeline {', '  layout="%s";' % eng,
           '  node [fontname="Helvetica" fontsize=10];',
           '  edge [fontname="Helvetica" fontsize=8];']
    if title:
        out += ['  labelloc=t;', '  label="%s";' % title]
    # ⚑⚑ A CLUSTERED NODE IS DECLARED INSIDE ITS SUBGRAPH AND NOWHERE ELSE. Emitting it
    # at top level first and again inside would give `dot` two declarations, the second
    # winning and the first leaving a stray node — so membership decides where the ONE
    # declaration goes.
    _in_cluster = {m for c in g.clusters.values() for m in c["members"]}
    for cid, c in g.clusters.items():
        out.append('  subgraph cluster_%s {' % _id(cid).lstrip("n_"))
        # ⚑ STYLED AS A LANE, NOT A BOX: no fill, a faint dashed border and the relation's
        # name as the lane label. The point is the corridor it opens for the identity
        # edge, so it should read as a channel the eye follows rather than a container
        # asserting a grouping the graph does not otherwise have.
        # ⚑⚑⚑ `rank=false` IS WHAT MAKES THE LANE A LANE (operator, 2026-08-16: *"this
        # works best when samerank=false within the cluster. That creates a vertical
        # channel for the cycle return to be clearly visible through"*). Side by side, the
        # two halves leave the identity edge no room and it hugs the boundary; stacked,
        # the cluster's own height IS the channel and the return runs straight up it.
        #
        # ⚑⚑ AND IT IS THE THIRD TIME RANK HAS BEEN THE ANSWER IN THIS FILE, EACH TIME
        # WITH A DIFFERENT SIGN. `rank=same` was wrong for the 80 builders (they are
        # composable stages, not simultaneous); no rank at all was right there; and here
        # rank must be explicitly REFUSED so a container that would otherwise level its
        # members does not. The knob is not good or bad — it states whether things happen
        # at the same time, and the answer differs per group.
        #
        # ⚑ WHICH IS EXACTLY THE CONTENT OF THE SPLIT: `_unit` and `_unit ⟳ AFTER` are
        # the SAME relation at DIFFERENT times, so ranking them together would assert the
        # one thing the split exists to deny.
        # ⚑⚑ `rank=false` STOOD HERE AND IS DELETED: GRAPHVIZ HAS NO SUCH VALUE. `rank`
        # accepts `same|min|source|max|sink`, so an unrecognised value is silently ignored
        # and the attribute asserted nothing. I had already MEASURED it inert ("rank=false
        # ALONE DID NOT STACK THEM") and left it emitted anyway — which is worse than never
        # having tried it, because the next reader sees a knob apparently doing work.
        #
        # ⚑ A LINE KEPT AFTER ITS OWN MEASUREMENT SHOWED IT DOES NOTHING is the same shape
        # as a caveat that excuses a wrong census: it makes the absence look accounted for.
        out.append('    label="%s"; style=dashed; color="%s"; fontsize=8; '
                   'fontcolor="%s"; margin=8;'
                   % (c["label"], _ok("neutral"), _ok("neutral")))
        for m in c["members"]:
            if m in g.nodes:
                _n = g.nodes[m]
                _a = dict(NODE_STYLE.get(_n["kind"], NODE_STYLE["other"]))
                _a.update({k: v for k, v in _n.items() if k not in ("label", "kind")})
                _a["label"] = '"%s"' % _n["label"]
                out.append("    %s [%s];" % (_id(m), " ".join(
                    "%s=%s" % (k, v if k == "label" or str(v).startswith('"')
                               else '"%s"' % v) for k, v in _a.items())))
        out.append('  }')
    for nid, n in g.nodes.items():
        if nid in _in_cluster:
            continue
        a = dict(NODE_STYLE.get(n["kind"], NODE_STYLE["other"]))
        a.update({k: v for k, v in n.items() if k not in ("label", "kind")})
        a["label"] = '"%s"' % n["label"] if not str(n["label"]).startswith("<") \
            else n["label"]
        out.append("  %s [%s];" % (_id(nid), " ".join(
            "%s=%s" % (k, v if k == "label" or str(v).startswith('"') else '"%s"' % v)
            for k, v in a.items())))
    for s, d, k, extra in g.edges:
        a = dict(EDGE_STYLE.get(k, EDGE_STYLE["other"]))
        a.update(extra)
        bits = []
        for key, v in a.items():
            if v is False and key == "constraint":
                bits.append("constraint=false")
            elif v is True and key == "constraint":
                bits.append("constraint=true")
            elif key != "constraint":
                bits.append('%s="%s"' % (key, v))
        out.append("  %s -> %s%s;" % (_id(s), _id(d),
                                      (" [%s]" % " ".join(bits)) if bits else ""))
    out.append("}")
    return "\n".join(out)


GRAPHVIZ_IMAGE ="nixery.dev/shell/graphviz:latest"


def _render_cmd(engine, fmt):
    """`([argv…], note)` — render `engine` locally if it can, else through podman.

    ⚑⚑⚑ THE LOCAL GRAPHVIZ HAS ONE LAYOUT ENGINE AND THE CONTAINER HAS ALL OF THEM. Measured:
    `fdp -Tsvg` on this box answers *"There is no layout engine support for fdp / Use one of:
    dot"* — graphviz 14.1.2 is installed, but its plugin config registers only `dot`. `dot -c`
    regenerates it and needs root (`/usr/lib/.../config8`); `GVBINDIR` relocates the config but
    NOT the renderer plugins, so a user-writable copy loses `-Tsvg` entirely.

    ⚑⚑ I FILED THAT AS A WALL — *"this needs sudo, which I won't run unasked"* — and it was a
    REUSE-SEARCH I did not run (operator, 2026-08-15: *"you have access to podman. I know one of
    the summit participants already uses podman to access graphviz reliably."*). `podman images`
    shows **`nixery.dev/shell/graphviz:latest` already pulled**, and `fdp -V` inside it answers
    `graphviz version 12.2.1`. The capability was on the box the whole time.

    ⚑ AND THE FORUM COULD NOT ANSWER IT: `summit capability graphviz` and `… podman` both report
    *"no entry carries that spelling (38 capabilities, 217 registered spellings)"* — which the
    tool itself insists is a fact about the INDEX, not about the ecosystem. Someone is using this
    and it is unregistered; that is a finding to file, and it is why the image name is a constant
    here rather than a discovery.

    ⚑⚑ THE ENGINE IS SELECTED BY THE `layout=` ATTRIBUTE, AND THE COMMAND IS ALWAYS `dot`
    (operator, 2026-08-15: *"I usually use the `layout` attribute to select engines."*). The
    source already declares `layout="fdp"`; naming `fdp` on the command line as well was a SECOND
    mechanism for one decision — and the two can disagree, which is the drift shape this repo
    retires everywhere else. `dot -Tsvg` honours the attribute, so the source is the authority
    and the binary is just a renderer.

    ⚑⚑ AND `layout=` MAKES THE CONTAINER THE UNIFORM PATH, WHICH RETIRES THE PROBE ENTIRELY
    (operator, 2026-08-15: *"using `layout=` to choose layout engines means you can use the
    container for ALL engines."*). Once the command is always `dot` and the SOURCE names the
    engine, there is no per-engine capability question left to ask: the container's graphviz has
    every plugin, so it answers for `dot`, `fdp`, `neato`, `circo` alike. The local binary is now
    the SPECIAL case — it happens to work for exactly one engine on this box.

    ⚑ SO THE `-V` AND RENDER-PROBE HISTORY IS RESIDUE, kept because it names a real trap: `fdp -V`
    exits 0 here while `fdp -Tsvg` fails, because the BINARY exists and the LAYOUT PLUGIN does
    not. A version string is a fact about the binary, not the capability. That distinction cost
    two wrong probes — and the right answer was to stop asking the question.

    ⚑ LOCAL ONLY WHEN IT IS CERTAINLY ENOUGH. `dot` is this graphviz's one registered layout, so
    a `layout="dot"` graph needs no container; anything else goes to the image. That is a fact
    about THIS box, so it is written as a narrow exception rather than a probe — and when the
    install is fixed, the exception widens by one word.
    """
    if engine == "dot":
        return (["dot", "-T" + fmt], "")
    return (["podman", "run", "--rm", "-i", GRAPHVIZ_IMAGE, "dot", "-T" + fmt], " via podman")


def _wrap(s, n):
    words, line, lines = s.split(), "", []
    for w in words:
        if len(line) + len(w) + 1 > n:
            lines.append(line); line = w
        else:
            line = (line + " " + w).strip()
    if line:
        lines.append(line)
    return "\\n".join(lines)


def _id(name):
    """A DOT-safe node id.

    ⚑⚑ `edge`, `node` AND `graph` ARE RESERVED WORDS IN DOT, and this store has relations named
    `edge`, `_node` and `node_child`. `dot` reported `syntax error in line 30 near 'edge'` — a
    relation name colliding with the graph language itself, which no amount of reading the
    python would have predicted. Prefixing every id sidesteps the whole class rather than
    special-casing the three names known today.

    ⚑⚑⚑ AND THE CHARACTER HANDLING IS A WHITELIST, BECAUSE THE BLACKLIST WAS A FROZEN
    ROSTER. It replaced `-` and `.` — the two characters that had bitten — and the producer
    split then minted ids like `p_sppf_db.project_sppf#0`. `#` is not legal in a DOT id, so
    `dot` silently mangled the graph: `--ranks` reported 12 ranks collapsing to 5 with every
    producer bunched on one row, which reads as a LAYOUT problem and was a SYNTAX one.
    The same shape as the tail parser and the quoted field name — a pattern that handles the
    spellings seen so far and is silent on the next.

    ⚑ ANY character outside `[A-Za-z0-9_]` becomes `_`. A collision between two sanitised
    names is possible in principle and has not occurred; if it ever does the fix is a hash
    suffix, not another special case.
    """
    import re as _re
    return "n_" + _re.sub(r"[^A-Za-z0-9_]", "_", name)


def _rel_label(rel, c):
    if c is None:
        return '"%s"' % rel
    n = c.get(rel, "missing")
    if n is None or n == "missing":
        # ⚑ ABSENT IS NAMED, NOT ZEROED. The live tenant has no `obs_node` and no `ref`; a "0"
        # would read as "applied, nothing in it" — the exact confusion this arc spent turns on.
        return '"%s\\nABSENT (tier not applied)"' % rel
    return '"%s\\n%s row(s)"' % (rel, format(n, ","))


def _fill(rel, c):
    # ⚑⚑⚑ SATURATED, NOT PASTEL — AND THE PASTELS WERE AN UNMEASURED PREMISE. These were
    # #e8f7ea / #fff8e1 / #fde8e8, which `cvd_gate` measured at dE 1.32 for
    # populated~ABSENT: one colour, for the most load-bearing fact in the diagram. I
    # defended them on the grounds that separating fills by dE 11 would break the black
    # label text sitting on them — then never checked, and reported the conflict as a
    # property of the problem (operator: *"the fill colors need better differentiability"*).
    #
    # ⚑⚑ THE CONFLICT WAS MY OWN DESATURATION (operator: *"It's not just the hue… colors
    # that are distinctly-hued but might not have sufficient remaining contrast, because
    # the colors are desaturated"*). Fitted against `cvd_gate` at full saturation, ALL
    # THREE legs pass: ≥3.06:1 against the page, ≥5.43:1 for black text, and worst-pair
    # dE 14.77 — above the 11.0 floor. A pale fill was never required; it was assumed,
    # and the assumption is what made the separation impossible.
    #
    # ⚑ SCORED AS A MAX-MIN OVER THE WEAKEST LEG, which is `derive_ghost`'s objective:
    # *"Two separate floors conflict when the span is tight; a max-min degrades
    # gracefully instead."* Three independent floors are what made this read infeasible.
    if c is None:
        return "#f5f5f5"
    n = c.get(rel, None)
    if n is None:
        return _ok("purple")      # ABSENT
    if n == 0:
        return _ok("vermillion")  # applied but EMPTY
    return _ok("bluegreen")       # populated


def _state_style(rel, c):
    """The non-colour carriers for a relation's three states — border, not fill.

    ⚑⚑⚑ THE FILL WAS THE ONLY CARRIER OF THE MOST IMPORTANT DISTINCTION IN THIS GRAPH.
    populated / applied-but-EMPTY / ABSENT is the fact this whole arc kept confusing in
    prose, and it was encoded as three pale pastels — #e8f7ea vs #fff8e1 vs #fde8e8, which
    differ by a few percent of lightness and are the green/amber/red axis a red-green
    deficiency collapses outright. The legend could not even show it: one `relation` row
    with one swatch, so the picture had three states and the key had none.

    ⚑⚑ THE LABEL ALREADY SAYS IT — `ABSENT (tier not applied)` / `0 row(s)` / `N row(s)` —
    so the text is the ground truth and everything here is redundancy ON TOP of it. That is
    the right layering: a reader who sees no colour reads the count, a reader scanning
    shapes sees the border, and the fill accents both. It was the only-carrier case that
    was wrong, not the use of colour.

    ⚑ AND ABSENT IS A DOUBLE BORDER, not merely a red one: `peripheries=2` survives
    greyscale printing, colour-blindness and a low-contrast display alike, which none of
    the three pastels do.
    """
    if c is None:
        return {}
    n = c.get(rel, None)
    # ⚑⚑ THE BORDER COLOURS ARE OKABE-ITO MEMBERS, chosen for SEPARATION rather than for
    # the green/amber/red convention that reads as one colour under deuteranomaly. Measured:
    # `populated ~ ABSENT` was dE 1.32 on the old pastels — the single most load-bearing
    # distinction in this graph, effectively invisible.
    #
    # ⚑⚑⚑ THE BORDER IS DERIVED FROM THE FILL, NOT HAND-PICKED. I typed three darkened
    # hexes here — the same transcription I had just removed from `EDGE_STYLE`, back
    # within the hour, because "darker version of the fill" FEELS like a judgement rather
    # than a computation. It is a computation: push the member away from its own fill
    # until it reads against it, which is `stretch_lit`'s rule applied one level down.
    # ⚑⚑ THE BORDER MEMBER MATCHES ITS OWN FILL — they were assigned independently and
    # disagreed (a vermillion border on a purple fill), which is a second colour claiming
    # a state the fill already states. One member per state, fill and ink derived from it.
    if n is None:
        return dict(color=_ink("purple"), penwidth="2.4", peripheries="2")      # ABSENT
    if n == 0:
        return dict(color=_ink("vermillion"), penwidth="2",
                    style="filled,dashed")                                      # EMPTY
    return dict(color=_ink("bluegreen"), penwidth="1.4")                        # populated


def _selftest():
    cases = []

    def check(n, got, want):
        cases.append((n, got == want, got, want))

    st = stages()
    # ⚑ THE STAGES ARE READ, NOT TYPED. If `LIFECYCLE` gains or loses a link this case moves with
    # it — which is the difference between a generated diagram and a drawn one. The chain has
    # ALREADY lost two links (`settled`, `consumed`, both deleted 2026-08-12); a hand-drawn
    # picture would still show them.
    check("the chain comes from the declaration", [n for n, _ in st],
          ["sourced", "observed", "reflected"])

    d = dot(counts_by_rel=None, stage_list=st)
    check("every declared stage appears", all("stage_%s" % n in d for n, _ in st), True)
    check("every FLOW edge is drawn", d.count("->") >= len(FLOW), True)
    # ⚑ THE PERFORMERS MUST EXIST. An edge naming a function or builder that has been renamed is
    # a diagram lying with authority — the failure mode a picture has and prose does not, because
    # nobody re-reads a picture's labels. Builders are checked against the compiled registry.
    import query_defs as _qd
    _builders = [w for _s, _d2, _l, w in FLOW if w.startswith("q_")]
    check("every builder an edge names is registered",
          sorted(w for w in _builders if w[2:] not in _qd.INTERN_BUILDERS), [])

    # ⚑ ABSENT vs EMPTY vs POPULATED must render DIFFERENTLY — the distinction `census` draws and
    # this diagram exists to preserve. A control on each so a single colour cannot pass all three.
    check("an ABSENT relation is named absent",
          "ABSENT" in _rel_label("obs_node", {"obs_node": None}), True)
    check("...an EMPTY one is not",
          "ABSENT" in _rel_label("obs_node", {"obs_node": 0}), False)
    check("...and the three states take three fills",
          len({_fill("x", {"x": None}), _fill("x", {"x": 0}), _fill("x", {"x": 7})}), 3)

    # ⚑⚑ THE BUILDER LAYER IS DERIVED, AND THESE CASES ARE WHAT SAY SO. A hand-written FLOW table
    # would pass every case above — the structure renders, the stages come from the declaration —
    # while covering 14 splices out of 81 builders. What must hold is that the graph's builder set
    # IS the registry's.
    import query_defs as _qd2
    _reads, _writes, _recursive = builder_edges()
    # ⚑ TWO SPELLINGS OF ONE NAME. `touching` reports the FUNCTION (`q_obs_all`);
    # `INTERN_BUILDERS` is keyed by the REGISTERED name (`obs_all`). Comparing them raw reported
    # 24 "unregistered" builders that are all registered — a census answering the question asked
    # rather than the one meant, in the guard written to catch exactly that.
    # ⚑ TWO REGISTRIES, AND BOTH ARE REGISTRATION. `INTERN_BUILDERS` holds the production reads;
    # `REFERENCE_ARMS` holds the comparison arms (`pack.sql` / `pack.python` / `members.python`)
    # that exist to be `--equiv`'d against each other. Checking only the first reported three
    # registered builders as unregistered — the `--calls emit` defect: a census answering the
    # question ASKED (is it in THIS dict) rather than the one MEANT (is it registered).
    _known = set(_qd2.INTERN_BUILDERS) | {v.__name__.removeprefix("q_")
                                          for v in _qd2.REFERENCE_ARMS.values()
                                          if hasattr(v, "__name__")}
    check("every builder in the graph is registered (in EITHER registry)",
          sorted(b for b in _reads if b.removeprefix("q_") not in _known), [])
    check("the derived set is non-empty (the registry IS being read)", bool(_reads), True)
    # ⚑⚑ THESE TWO CASES ONCE PINNED THE OPPOSITE. They asserted that CTE-composed readers were
    # INVISIBLE — a guard holding a defect in place, written when I had filed `get_final_froms`'s
    # blindness as a limit of the instrument rather than a wrong accessor. With `touching` walking
    # the statement tree they now assert the capability. A case that pins a limitation is only
    # honest while the limitation is real; this one lasted about ten minutes.
    check("a CTE-composed builder's underlying tables ARE resolved",
          {"obs", "edge", "event", "obs_node"} <= _reads.get("q_pack_level", set()), True)
    # ⚑ THE SELF-REFERENCE IS A REAL EDGE. `q_pack_level` reads `obs_node` — the relation the fold
    # WRITES — and that cycle is not noise to prune: it is exactly why the fold runs level-by-level
    # rather than as one statement. It is visible only because the walk goes through the CTE.
    check("...including the fold's read of the relation it writes",
          "obs_node" in _reads.get("q_pack_level", set()), True)
    _d2 = dot(counts_by_rel=None, stage_list=st, reads=_reads, writes=_writes,
              recursive=_recursive)
    check("every derived builder is drawn", all(_id("b_" + b) in _d2 for b in _reads), True)
    # ⚑ A FLAT BUILDER'S READ **IS** RESOLVED, which is the control proving the derivation works
    # where the instrument can see. `q_obs_all` scans `obs` directly — no CTE — and must appear.
    # Without this, the two cases above are satisfied by a `touching` that returned nothing at all.
    check("a builder reading a table DIRECTLY is resolved",
          "obs" in _reads.get("q_obs_all", set()), True)

    # ⚑⚑ THE GRAPH HAS FLOW ONLY IF WRITES ARE TRACKED. With reads alone every edge ran
    # relation → builder — a hundred arrows in and nothing out, which is a picture of a
    # dependency list rather than a pipeline.
    check("builder WRITES are derived, not only reads", bool(_writes), True)
    check("...and a DML builder's target is one of them",
          "ref" in _writes.get("q_ref_insert", set()), True)
    # ⚑ THE CTE CASE: `q_pack_level_insert` returns a `select()` over a data-modifying CTE, so
    # its top-level type is `Select`. A top-level `isinstance` check reported `builder writes
    # (0)` for `obs_node` — the builder whose entire purpose is writing it.
    check("...including one whose DML is buried in a CTE",
          "obs_node" in _writes.get("q_pack_level_insert", set()), True)
    # ⚑⚑ AND A READ-WHAT-YOU-WRITE BUILDER IS SPLIT, NOT LOOPED. One node with an in- and
    # out-edge to itself is a cycle `dot` must break arbitrarily; two nodes state the time axis
    # the cycle was collapsing.
    check("a recursive builder is identified", ("q_pack_level_insert", "obs_node") in _recursive,
          True)
    check("...and drawn as a SEPARATE 'after' node", "n_after_obs_node" in _d2, True)
    # ⚑ THE CONTROL: a non-recursive write must NOT be split, or every relation doubles.
    check("...while a plain write targets the relation itself",
          "n_after_ref" in _d2, False)

    # ⚑⚑ NODES, NOT EDGE LABELS OR CLUSTERS — the operator's own graphviz technique
    # (`mikemol.github.io` 2018-01-12): *"Graphviz treats only nodes and edges as first-order
    # objects… most layout engines don't support clusters at all."* Both defects this file hit —
    # `splines=ortho` mangling edge labels and `fdp` ignoring `cluster_*` — are that one fact, so
    # the guard is that neither construct is emitted. A `label=` ON AN EDGE is the regression to
    # catch: it renders under `dot` and degrades silently elsewhere.
    _dn = dot(counts_by_rel=None, stage_list=st, reads=_reads, writes=_writes)
    # ⚑ ONE PREDICATE, READABLE. A first cut chained three conditions with `and` over sliced
    # strings — unfollowable, and the kind of assertion that passes for a reason nobody can
    # state. An edge line is one containing `->`; it must not also set `label=`.
    _edge_lines = [ln for ln in _dn.splitlines() if "->" in ln]
    check("no edge carries a label attribute (nodes carry them instead)",
          [ln.strip() for ln in _edge_lines if "label=" in ln], [])
    # ⚑⚑⚑ CLUSTERS ARE BOUNDED, NOT BANNED — and this case banned them outright because
    # the only cluster ever proposed here was one containing ~80 builders, which is a
    # containment constraint that distorts everything outside it. The rule was always
    # about SIZE AND MEMBERSHIP; I encoded it as "no clusters", which then forbade the
    # one shape that is unambiguously right: a cluster of EXACTLY the two halves of a
    # split rest point, which contains one relation at two times — a thing that is
    # already one thing — and supplies the corridor its unconstrained identity edge
    # otherwise lacks.
    #
    # ⚑ SO THE GATE IS THE BOUND. Every cluster holds exactly two members and both are
    # halves of one rest point; anything larger, or mixing kinds, is the containment
    # defect arriving back through the door this opened.
    _cl = graph(counts_by_rel=None, stage_list=st, reads=_reads,
                writes=_writes).clusters
    # ⚑⚑ TWO CLUSTER KINDS NOW, AND BOTH ARE ONE RULE: a node standing for several
    # positions in the flow is drawn as several nodes in a lane. `rest_*` splits a
    # relation by TIME (before/after); `step_*` splits a producer by SEQUENCE (which
    # `upsert` in its body). The bound is that a cluster's members are all parts of ONE
    # thing — never a grouping of different things, which is the containment defect.
    check("every cluster is a rest point's halves or a producer's steps",
          sorted(k for k in _cl if not k.startswith(("rest_", "step_"))), [])
    check("...a rest point's cluster holds exactly its before and after",
          sorted(k for k, c in _cl.items() if k.startswith("rest_")
                 and (len(c["members"]) != 2
                      or c["members"][1] != "after_" + c["members"][0])), [])
    # ⚑ A STEP LANE'S MEMBERS ARE SUFFIXED PARTS OF ONE PRODUCER, and there must be at
    # least two — a single-step producer is not split, since inventing a sequence the
    # code does not have is the same fabrication as inferring one from a layout.
    check("...a producer's cluster holds ≥2 parts of the SAME function",
          sorted(k for k, c in _cl.items() if k.startswith("step_")
                 and (len(c["members"]) < 2
                      or any(not m.startswith(k[5:] + "#") for m in c["members"]))), [])
    # ⚑ THE CONTROL: the labels must still EXIST, as nodes. A graph that dropped them entirely
    # would pass both cases above while losing every "what does this arrow mean".
    # ⚑⚑ AND IT NAMES NO FUNCTION. This case asserted `"sppf_decode.write_events" in _dn`
    # — a literal writer name in a test for a graph whose whole point is that writers are
    # DERIVED. It failed the moment the derivation replaced the hand table, and it failed
    # CORRECTLY: `write_events` is the wrapper, `_insert_decoded` is the writer. A case
    # that pins a derived value defeats the derivation, so it asserts the PROPERTY (labels
    # exist as plaintext nodes, and every derived producer appears) instead.
    # ⚑ ASSERTED OVER THE GRAPH'S NODE KINDS, not a DOT substring. `shape=plaintext` was a
    # serialization detail standing in for "a label node exists"; the kind says it directly.
    check("...while the label text survives as label nodes",
          any(n["kind"] == "label" for n in graph(
              counts_by_rel=None, stage_list=st, reads=_reads,
              writes=_writes).nodes.values()), True)
    _pr = producers()
    check("...and every DERIVED producer is drawn (no hand-listed writer)",
          sorted(fn for fn in _pr if fn not in _dn), [])
    check("...and the producers are found at all (an empty census is not a pass)",
          len(_pr) > 0, True)

    # ⚑⚑⚑ THE FLOW EDGES CONSTRAIN AND THE ANNOTATIONS DO NOT, which is the distinction
    # that collapsed when I copied `constraint=false` from the read edges onto everything
    # (operator: *"Way too much constraint=false."*). A read is many-to-many with no
    # sequence; builder→consumer is a real ordering. Guarded as a RATIO rather than a count,
    # because the honest invariant is "the skeleton is still mostly constrained", not a
    # number that any new builder would move.
    _dn2 = dot(counts_by_rel=None, stage_list=st, reads=_reads, writes=_writes,
               recursive=_recursive)
    # ⚑⚑⚑ THE CASES READ THE GRAPH, NOT THE TEXT. They used to assert over DOT lines —
    # `"#bb8822" in ln and "arrowhead=vee" in ln` to mean "a flow edge" — which made every
    # gate a hostage to the serializer's formatting AND to its colour choices. `edge_census`
    # answers the same questions off the structure.
    _g2 = graph(counts_by_rel=None, stage_list=st, reads=_reads, writes=_writes,
                recursive=_recursive)
    _cen2 = _g2.edge_census()
    # ⚑ ...EXCEPT ON A SURVIVING CYCLE. This asserted ZERO unconstrained flow edges, which
    # held while every cycle was splittable. One is not: `_insert_decoded` writes `core_fp`
    # and `write_events` reads it back inside the same open transaction, so the `flow` edge
    # into that read is on a real loop and must relax. Asserting zero here would force the
    # layout to satisfy a contradiction the DATA contains. The count is bounded by the
    # cycle set rather than fixed at zero — a stale absolute replaced by the real invariant.
    _cyc_pre = _g2.cycles()
    _oncyc_pre = {n for c in _cyc_pre for n in c}
    check("consumer edges CONSTRAIN except where a real cycle survives",
          _cen2.get("flow", (0, 0))[1] <= len(_oncyc_pre), True)
    # ⚑ THIS CASE ONCE ASSERTED THE COLUMN-NOTE EDGE STAYED RELAXED, on the "annotation, not
    # a step" reading. That reading was the kind-vs-position confusion again, and the
    # acyclicity removed the last reason to keep any exception. Inverted rather than deleted,
    # so the file records that the exception existed and why it did not survive.
    check("...and so does the column-note annotation (no exception survives)",
          _cen2.get("returns", (0, 0))[1], 0)
    # ⚑ NODES-AS-LABELS IS A DEDUP, NOT A DECORATION (operator: *"should dedupe nodes like
    # that"*). 28 builders with no attributed caller share ONE node; identical return-column
    # lists share one each. A private copy per builder is the technique inverted — it costs
    # exactly the space the shared node exists to save.
    # ⚑⚑⚑ THE BUILDERS ARE NOT RANKED TOGETHER, AND THIS CASE EXISTS BECAUSE THE KNOB
    # FLIPPED THREE TIMES WITH NOTHING HOLDING IT. Removed on a width fear the operator's
    # post refutes; restored on the correct reading of that post; removed again only when
    # the operator named what a rank ASSERTS (*"They're composable stages in dataflow, and
    # they're all being forced together"*). A decision re-derived every session is a decision
    # nobody made — so the reason lives in a case, not in prose that the next reader weighs
    # against the post again.
    check("builders are NOT forced onto one rank (they are composable stages)",
          "rank=same" in _dn2, False)
    check("...while the builder KIND still groups them (grouping without geometry)",
          sum(1 for n in _g2.nodes.values() if n["kind"] == "builder") > 1, True)
    # ⚑⚑ A DEAD BUILDER IS MARKED ON THE NODE, WITH NO EDGE AT ALL. The case used to assert
    # a single shared `no caller` sink; the sink itself was the defect (an absence drawn as
    # a destination), so the assertion now names the property that replaced it — the builder
    # is flagged in place and its out-degree is genuinely empty.
    # ⚑⚑⚑ NO DISTINCTION MAY REST ON COLOUR ALONE — the a11y gate, and it would have failed
    # against the legend as first shipped (operator: *"Take a look through summit about a11y.
    # Because this needs work."*). Five edge kinds were separated by hue only, two of them
    # sharing `#bb8822`; the relation's three states were three pale pastels on the
    # green/amber/red axis a red-green deficiency collapses. Summit's floor already carried
    # `friction-accessibility-is-an-unregistered-capability` (mat230) — no accessibility
    # capability exists in the forum, so there was no gate to borrow and this is substrate's.
    #
    # ⚑⚑ THE PREDICATE IS PAIRWISE-DISTINGUISHABLE-WITHOUT-COLOUR, not "a mark exists". A
    # per-kind mark that happened to repeat would pass a presence check and still leave two
    # rows identical to a reader — which is precisely how `producer` and `consumer` shipped
    # (same fill, and they would have shared a glyph too).
    # ⚑⚑⚑ AND THE COLOURS THEMSELVES ARE MEASURED BY A PEER'S GATE, NOT BY THIS FILE.
    # `cvd-contrast-gate` (owner el-openglo, 23 registered spellings) applies WCAG 2.x, APCA,
    # CAM02-UCS and Machado protan/deutan/tritan simulation against a floor DERIVED from
    # Okabe-Ito's own tightest pair. Pointed at this table it found 9 of 16 pairs under the
    # floor — including `write`~`returns` at dE 2.75, a collision I CREATED this session and
    # could not have seen by reasoning. The edge accents are now Okabe-Ito members and all
    # five clear it.
    #
    # ⚑⚑ THE SIX SURVIVORS ARE NODE FILLS, AND THEY STAY. A fill sits behind black label
    # text, so separating six of them by dE 11 means six saturated backgrounds that break the
    # text contrast the same standard requires — the constraint genuinely conflicts. The fill
    # is the THIRD carrier there: the label states the fact in words (`ABSENT (tier not
    # applied)` / `N row(s)`), the border carries it in weight and periphery count, and the
    # fill only accents. That is the layering el-openglo's own entry describes, and it is why
    # this gate checks the CARRIERS rather than re-deriving the colour measurement here.
    #
    # ⚑ SO THIS FILE DOES NOT REIMPLEMENT CONTRAST. The measurement lives with its owner;
    # what is gated here is that no distinction rests on colour ALONE, which is the property
    # a consumer of that gate must hold up on its own side.
    _sig = {k: (v.get("style", "solid"), v.get("arrowhead", ""), v.get("penwidth", "1"),
                v.get("arrowtail", ""))
            for k, v in EDGE_STYLE.items() if k in EDGE_MEANING}
    check("every legended edge kind is distinguishable WITHOUT colour",
          len(set(_sig.values())), len(_sig))
    check("...and every one carries an ASCII swatch for greyscale/low-contrast readers",
          sorted(k for k in EDGE_MEANING if k not in EDGE_MARK), [])
    # ⚑⚑⚑ EVERY EDGE COLOUR IS ELIGIBLE AGAINST THE PAGE, which is the constraint a pure
    # separation solve does not model. el-openglo's grounded solve measured it: only FOUR
    # Okabe-Ito members clear WCAG's 3:1 non-text minimum as a stroke on white (blue 5.19,
    # vermillion 3.87, bluegreen 3.42, purple 3.06), while sky 2.31, orange 2.25 and
    # yellow 1.32 do not. Their ungrounded assignment scored a healthy q and would have put
    # three of my six edges near-invisible on the page they are drawn on — an artifact that
    # passes its own check and is wrong, found only by rendering. Same shape as their
    # `edgecolor=` defect: valid file, every colour silently black.
    #
    # ⚑⚑ THE ELIGIBLE SET IS SPELLED HERE AS A MEASURED FACT, not re-derived: this repo
    # cannot run `cvd_gate` (no numpy/colorspacious), so the numbers come from the peer
    # that can, and the gate holds the CONSEQUENCE — a member outside that set must not
    # appear as an edge stroke. If the page ground ever changes, this list is what has to
    # be re-measured, and saying so is the honest form.
    _PAGE_ELIGIBLE = {_ok("blue"), _ok("vermillion"), _ok("bluegreen"), _ok("purple"),
                      _ok("neutral")}
    check("every edge colour clears 3:1 against the white page (measured by cvd_gate)",
          sorted(k for k, v in EDGE_STYLE.items()
                 if k in EDGE_MEANING and v.get("color") not in _PAGE_ELIGIBLE), [])
    # ⚑ AND THE REUSE IS FORCED AT FIVE ROLES, NOT SIX: four eligible members cover four
    # FREE roles, so five free on white refuses outright. The duplicate is legitimate ONLY
    # while a non-colour carrier separates the pair — which the a11y gate above requires
    # of every kind — so this case records that the pool limit and that carrier are
    # load-bearing together. Without the second, "we ran out of colours" is a slow leak.
    _dupe = [c for c in {v.get("color") for k, v in EDGE_STYLE.items() if k in EDGE_MEANING}
             if sum(1 for k, v in EDGE_STYLE.items()
                    if k in EDGE_MEANING and v.get("color") == c) > 1]
    check("...and any hue reused across roles is a POOL LIMIT, carried by shape not colour",
          all(len({(EDGE_STYLE[k].get("style"), EDGE_STYLE[k].get("penwidth"),
                    EDGE_STYLE[k].get("arrowhead"), EDGE_STYLE[k].get("arrowtail"))
                   for k in EDGE_MEANING if EDGE_STYLE[k].get("color") == c})
              == sum(1 for k in EDGE_MEANING if EDGE_STYLE[k].get("color") == c)
              for c in _dupe), True)
    # ⚑⚑⚑ THE LEGEND'S SWATCH MUST BE THE SHAPE THE GRAPH DRAWS. It was a set of invented
    # pictograms (`⬡`, `▤▶`) matching nothing in the picture, so the key could not
    # identify a node — the operator could not tell a builder from a producer with the
    # legend open beside the render. Nothing caught it because every existing a11y case
    # asked whether the marks were DISTINCT from each other, never whether they were TRUE.
    # Distinctness is a property of the key; correspondence is a property of the pairing.
    check("every legend mark is the shape the graph actually emits",
          sorted(k for k, m in NODE_MARK.items()
                 if k in NODE_MEANING and NODE_STYLE.get(k, {}).get("shape") != m), [])
    # ⚑⚑ AND EVERY EDGE MEANING NAMES ITS ENDPOINTS, because four kinds share a plain vee
    # and prose saying "READS" cannot answer WHICH END READS. `read` is relation→builder,
    # `flow` is builder→consumer; an arrow between a box and a component is ambiguous
    # without the pairing stated. The check is structural — an arrow in the text — rather
    # than a wording preference.
    check("...and every edge meaning states its direction as <tail> → <head>",
          sorted(k for k, m in EDGE_MEANING.items() if "→" not in m), [])
    check("...and no two legended node kinds share a mark",
          len({NODE_MARK[k] for k in NODE_MEANING if k in NODE_MARK}),
          len([k for k in NODE_MEANING if k in NODE_MARK]))
    # ⚑ THE THREE RELATION STATES ARE SEPARABLE BY BORDER, not only by fill. The label
    # already names the state; this is the redundant carrier that survives a printout.
    _states = [_state_style("r", c) for c in ({"r": 5}, {"r": 0}, {"r": None})]
    check("...and populated / EMPTY / ABSENT differ by more than fill colour",
          len({(s.get("penwidth"), s.get("peripheries"), s.get("style"))
               for s in _states}), 3)
    # ⚑⚑⚑ NO FILL IS A PASTEL, WHICH IS THE PREMISE THAT FAILED. The three relation
    # fills were #e8f7ea / #fff8e1 / #fde8e8 — measured at dE 1.32 for populated~ABSENT,
    # one colour for the diagram's most load-bearing fact. I defended them by asserting
    # that separating fills would break the black label text on them, never measured it,
    # and reported the conflict as a property of the problem. Fitted at full saturation
    # every leg passes (page ≥3.06:1, text ≥4.05:1, worst pair dE 14.77). This case
    # cannot re-derive the measurement — that lives with `cvd-contrast-gate`, whose deps
    # this repo does not carry — so it gates the PROPERTY that made it possible: a fill
    # is a palette member, never a hand-mixed tint toward white.
    _fills = [_fill("r", c) for c in ({"r": 5}, {"r": 0}, {"r": None})]
    _members = set(_okabe_ito()) | {"neutral"}
    check("every relation fill is a named palette member, not a hand-mixed pastel",
          sorted(f for f in _fills if f not in {_ok(m) for m in _members}), [])
    check("...and the three states use three DIFFERENT members",
          len(set(_fills)), 3)
    # ⚑⚑ A BANDED FILL CONSTRAINS ITS TEXT, and that is the cost of the extra channel.
    # `#0072b2` wants white text (5.19:1) and `#56b4e9` wants black (9.10:1); a node has
    # ONE `fontcolor`, so the band is ordered light-first to keep the label unambiguous.
    # Reversing it silently drops the label to 2.31:1 on the stop it lands over.
    _bands = NODE_STYLE["builder"]["fillcolor"].split(":")
    check("a banded fill is ordered light-first so one fontcolor serves both stops",
          _bands, [_ok("sky"), _ok("blue")])
    # ⚑ THE TWO SUB-3:1 FILLS CARRY A BORDER. `builder` (2.31:1) and `producer` (2.25:1)
    # are under WCAG's non-text minimum against the page, so without an outline their
    # boundary is what a low-vision reader loses. The relation states clear 3:1 on their
    # own — a real difference, not a uniform "border everything".
    check("a fill under the 3:1 non-text minimum carries a border",
          sorted(k for k in ("builder", "producer", "consumer")
                 if "color" not in NODE_STYLE[k]), [])
    # ⚑⚑⚑ EVERY BUILDER HAS AN ATTRIBUTED CALLER, and 28 of 81 read as orphans until the
    # operator asked why three orbit nodes were disconnected. They were never dead: the
    # registry is run BY ITERATION in `query_defs.verify`, so an equivalence arm — a
    # builder checked row-for-row against a hand-written raw-SQL twin — reached the graph
    # as `⚑ no caller`. My own report printed the explanation ("11 run sites pass a
    # computed name") beside the symptom for two days, and I read the symptom as a fact
    # about the builders. A caveat that names a gap made the wrongness sound accounted for.
    #
    # ⚑⚑ AND THE DEFAULT GROUP WAS THE TRAP INSIDE THE TRAP. `_GROUP` records only the
    # NON-default assignments and `_group_of` falls back to `catalog`, so reading the table
    # alone fixed 6 and left 22 — every one of them in the group that runs on a plain
    # `--verify`. A membership table that lists the exceptions is not a roster.
    import query_defs as _qd_gate
    check("every builder has an attributed caller (the registry is run by iteration)",
          sorted(b for b in _qd_gate.INTERN_BUILDERS if b not in consumers()), [])
    # ⚑ THE ORPHAN MARKER IS NOW UNREACHED, AND THAT IS THE FINDING RATHER THAN A GAP.
    # This asserted the marker APPEARS — which held while 28 builders read as callerless
    # and stopped holding the moment they were correctly attributed. Asserting a defect's
    # symptom is present is a case that passes hardest when the code is most wrong, so it
    # now asserts the PROPERTY: an unattributed builder is flagged ON ITS NODE and never
    # wired to a sink, whether or not any exists today.
    # ⚑ COMPARED AGAINST THE GRAPH'S OWN BUILDERS, NOT THE LIVE REGISTRY. My first cut
    # asked whether the marker appears iff the REGISTRY has an orphan — but `_dn2` is
    # built from a FIXTURE (`_reads`), so its builders and the registry's are different
    # populations. The case failed for a reason that was about neither: two sets compared
    # as if they were one, which is the scope mismatch that produced the `--corpus` bug
    # and the `q_`-prefix join in the same file.
    _gb = {n[2:] for n in _g2.nodes if n.startswith("b_")}
    check("an unattributed builder would be flagged on the node, not wired to a sink",
          ("no attributed caller" in _dn2) ==
          bool([b for b in _gb if (b[2:] if b.startswith("q_") else b) not in consumers()]),
          True)
    # ⚑⚑⚑ EVERY EDGE CONSTRAINS, WHICH THE ACYCLICITY LICENSES (operator: *"If it's already
    # acyclic, then we can just add constraints on all of the nodes and let dot sort it
    # out."*). The relaxations were each a local workaround for a layout that had no ordering
    # information; with the graph proven acyclic there is nothing for a constraint to
    # deadlock, so withholding one only discards a fact. `--cycles` is the standing check.
    # ⚑⚑⚑ THE GATE IS NO LONGER "ZERO CYCLES", AND THE CHANGE IS A FINDING RATHER THAN A
    # RELAXATION. Splitting at the data-at-rest point clears every cycle whose state is
    # COMMITTED — the writer's transaction ends, so before/after are real. One survives:
    # `_insert_decoded` writes `core_fp` and `write_events` reads it back through
    # `q_core_fp_mtimes` INSIDE THE SAME OPEN TRANSACTION. There is no "after" until the
    # commit, so the read genuinely sees the write and a split would state a boundary
    # that does not exist.
    #
    # ⚑⚑ SO THE INVARIANT IS: EVERY REMAINING CYCLE IS UNCOMMITTED. That is checkable and
    # it is the real property — "acyclic" was only ever a proxy for "no edge asks the
    # layout to satisfy a contradiction", and an uncommitted read-your-own-write is a
    # contradiction in the DATA, not in the drawing. Those edges relax; everything else
    # constrains, which is why the unconstrained count is asserted against the cycle set
    # rather than against zero.
    _cyc2 = _g2.cycles()
    _oncyc = {n for c in _cyc2 for n in c}
    check("every surviving cycle rests on UNCOMMITTED data (nothing else is cyclic)",
          sorted(n for n in _oncyc
                 if _g2.nodes.get(n, {}).get("kind") == "relation"
                 and durability(n) >= DURABILITY["committed"]), [])
    # ⚑ AND THE ONLY UNCONSTRAINED EDGES ARE THE ONES ON THOSE CYCLES. A relaxation
    # anywhere else is the blanket `constraint=false` the operator flagged, arriving back
    # through a different door.
    # ⚑⚑ TWO LICENCES TO RELAX, AND BOTH ARE EARNED. This asserted that ONLY a surviving
    # cycle's edges may be unconstrained — true until the split's two halves were joined.
    # A `sameas` edge states an IDENTITY (`orbit_node` and `orbit_node ⟳ AFTER` are one
    # relation at two times), and an identity has no rank, so constraining it would ask
    # the layout to order a thing against itself. It is also exactly the back-edge the
    # split cut, so it must stay out of the dependency walk AND out of the ranking.
    #
    # ⚑ ENUMERATED RATHER THAN WIDENED TO A PREDICATE: a relaxation is legitimate here
    # for one of two NAMED reasons, and anything else is the blanket `constraint=false`
    # the operator flagged arriving through a new door.
    # ⚑ AND THE IDENTITY EXEMPTION IS GONE AGAIN — it lasted one edit. `sameas` was
    # relaxed on the reasoning that an identity has no rank; then `--ranks` showed the
    # halves sitting level, because a cluster cannot create a rank difference no edge
    # asks for. Constrained, the pair spans a rank and the lane is vertical. The
    # exemption was real reasoning about the wrong mechanism, and the measurement is
    # what separated them.
    check("...and only a surviving cycle's edges are unconstrained",
          sorted({s for s, d, k, a in _g2.edges
                  if a.get("constraint") is False
                  and s not in _oncyc and d not in _oncyc}),
          [])
    # ⚑⚑ THE TWO HALVES MUST NOT SHARE A RANK, which is the property the lane depends on
    # and which neither the cluster nor `rank=false` delivered on its own. Asserted on
    # the STRUCTURE (a constrained edge between them) rather than on rendered geometry,
    # so it holds without shelling out to `dot`.
    # ⚑ AND THE EDGE RUNS before→after, WHICH IS WHAT PUTS TIME DOWNWARD. This asserted
    # `after→before` — my original direction, reasoned from the READ — and since the edge
    # is what supplies the rank, it placed the written half above the one it is written
    # from. The case encoded the bug it was written to guard.
    check("a split rest point's halves are RANKED apart, before ABOVE after",
          sorted(k for k, c in _cl.items()
                 if not any(s == c["members"][0] and d == c["members"][1]
                            and a.get("constraint") is not False
                            for s, d, _k, a in _g2.edges)), [])
    # ⚑⚑ THE DETECTOR MUST DETECT, which a green run over an acyclic graph cannot show. A
    # 3-cycle fixture proves the walk finds one; without this the acyclicity case would pass
    # identically against a function that returns [] unconditionally — a test of the graph
    # masquerading as a test of the instrument.
    #
    # ⚑ AND THE FIXTURE IS A `Graph`, NOT DOT TEXT. When the walk parsed source, this case
    # had to hand it `"digraph g { a -> b; b -> c; c -> a; }"` and FAILED — the parser only
    # understood one edge per line. The structure has no formatting to disagree about.
    _cyc = Graph()
    for _a, _b in (("a", "b"), ("b", "c"), ("c", "a")):
        _cyc.edge(_a, _b)
    check("...and the cycle walk actually finds one when it exists", len(_cyc.cycles()), 1)
    _dia = Graph()
    for _a, _b in (("a", "b"), ("a", "c"), ("b", "d"), ("c", "d")):
        _dia.edge(_a, _b)
    check("...while a diamond (two paths, no loop) is NOT reported as a cycle",
          _dia.cycles(), [])
    _notes = [ln for ln in _dn2.splitlines() if "shape=note" in ln and "fffdf0" in ln]
    check("...and identical return-column lists collapse to one node",
          len(_notes), len({ln.split("label=", 1)[1] for ln in _notes}))

    # ⚑⚑ THE COMMAND IS ALWAYS `dot`; THE SOURCE'S `layout=` PICKS THE ENGINE. Two mechanisms for
    # one decision can disagree, and naming `fdp` on the command line while the source declared
    # `layout="fdp"` was exactly that. It also means the container answers for EVERY engine, so
    # the per-engine capability probe (two wrong versions: `-V`, then a render) is gone rather
    # than fixed.
    _cmd, _via = _render_cmd("fdp", "svg")
    check("a non-dot engine routes through podman", _cmd[0], "podman")
    check("...and still invokes `dot`, letting layout= select", _cmd[-2], "dot")
    check("...and says so rather than reporting a local render", _via.strip(), "via podman")
    # ⚑ THE CONTROL: `dot` is this box's one registered layout, so it must not pay for a
    # container. If both branches returned podman the case above would pass and the tool would
    # be needlessly slow on its own default.
    check("...while dot stays local", _render_cmd("dot", "svg")[0][0], "dot")
    # ⚑ AND THE ENGINE MUST REACH THE SOURCE, not only the command — a render that ignored
    # `--engine` would lay out with `dot` while reporting `fdp`. Driven by substituting argv, not
    # by reading the ambient one: a first cut wrote `… or "--engine" not in sys.argv`, which is
    # VACUOUSLY TRUE on every normal run and asserts nothing.
    _sv2 = sys.argv
    try:
        sys.argv = ["pipeflow.py", "--engine", "fdp"]
        check("the chosen engine is declared in the source",
              'layout="fdp"' in dot(counts_by_rel=None, stage_list=st), True)
        sys.argv = ["pipeflow.py"]
        check("...and the default declares dot", 'layout="dot"' in dot(counts_by_rel=None,
                                                                       stage_list=st), True)
    finally:
        sys.argv = _sv2

    bad = [c for c in cases if not c[1]]
    for n, _, got, want in bad:
        print("  FAIL %s: got %r want %r" % (n, got, want))
    print("selftest: %d/%d" % (len(cases) - len(bad), len(cases)))
    return 0 if not bad else 1


# selftest-tenant: sandbox
# ⚑ ⟡tenant-pragma — `run_selftests._tenant` reads this and appends the flag. `store.tenant`
# exits 2 on an unstated tenant since ⟡tenant-mandatory (2026-08-24); SANDBOX because a suite
# that reaches the LIVE store can corrupt the corpus it exists to check.
if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    if "--rendered" in sys.argv:
        # ⚑⚑⚑ DID THE STYLING REACH THE PICTURE? A valid DOT attribute that graphviz
        # does not implement is accepted, exits 0, and renders as the default — el-openglo
        # shipped `edgecolor=` that way (every colour silently black) and I have now done
        # the same with a gradient: `color="a;0.5:b"` is in the source, `dot -Tsvg` exits
        # 0, and the SVG contains ZERO gradient strokes. The file parsing is not the
        # check; the render is.
        #
        # ⚑⚑ SO THIS COMPARES THE DECLARED PALETTE AGAINST THE STROKES THAT EXIST. A
        # colour in `EDGE_STYLE`/`NODE_STYLE` that appears nowhere in the SVG is a
        # silently-dropped attribute, which no amount of reading the DOT can reveal.
        # Third time I have wanted this question answered in one session, which is the
        # threshold for it being a mode rather than a one-off.
        import subprocess, collections
        _r5, _w5, _rec5 = builder_edges()
        _src = dot(counts(False) if "--no-counts" not in sys.argv else None,
                   reads=_r5, writes=_w5, recursive=_rec5)
        _cmd, _via = _render_cmd("dot", "svg")
        _svg = subprocess.run(_cmd, input=_src, capture_output=True, text=True,
                              check=True).stdout
        _want = {v["color"] for v in EDGE_STYLE.values() if v.get("color")}
        _want |= {v["fillcolor"] for v in NODE_STYLE.values()
                  if v.get("fillcolor") and ":" not in v["fillcolor"]}
        _missing = sorted(c for c in _want if c.lower() not in _svg.lower())
        # ⚑⚑⚑ GRAPHVIZ IMPLEMENTS `a;0.5:b` ON AN EDGE AS TWO SOLID SEGMENTS, NOT AN SVG
        # GRADIENT — measured on a three-line fixture rather than assumed: the stroke
        # renders as two `<path stroke="#009e73">` / `<path stroke="#0072b2">` halves with
        # no `<linearGradient>` anywhere. My first version of this check counted
        # `stroke:url(#` and reported `147 declared, 0 rendered ⚑ DROPPED` — a FALSE
        # ALARM, and the instrument was wrong in the same way the thing it was built to
        # catch is wrong: measuring for an artifact the tool never emits.
        #
        # ⚑⚑ AND THE TWO-SEGMENT FORM IS BETTER FOR THE PURPOSE. A true gradient blends
        # continuously, so two edges leaving different relations look similar near their
        # midpoints; a hard split gives each edge a source-coloured FIRST HALF that stays
        # readable where lines cross. The operator asked for gradient support and what
        # graphviz supplies is a sharper tool than what was asked for.
        #
        # ⚑ SO THE CHECK COUNTS EDGES WHOSE TWO HALVES CARRY DIFFERENT STROKES, which is
        # the property that matters: one declared colour pair, two rendered strokes.
        _g5 = graph(counts_by_rel=None, reads=_r5, writes=_w5, recursive=_rec5)
        _heads = {str(a["color"]).split(";")[0]
                  for _s, _d, _k, a in _g5.edges if ";" in str(a.get("color", ""))}
        _grad = sum(1 for h in _heads if h.lower() in _svg.lower())
        _decl = sum(1 for _s, _d, _k, a in
                    graph(counts_by_rel=None, reads=_r5, writes=_w5,
                          recursive=_rec5).edges
                    if ";" in str(a.get("color", "")))
        print("  declared colours reaching the render: %d of %d"
              % (len(_want) - len(_missing), len(_want)))
        for c in _missing:
            print("    ⚑ %s — declared, ABSENT from the SVG" % c)
        print("  split-stroke edges: %d declared over %d source colour(s); "
              "%d of those colours reach the render%s"
              % (_decl, len(_heads), _grad,
                 "   ⚑ DROPPED" if _heads and not _grad else ""))
        sys.exit(1 if (_missing or (_heads and not _grad)) else 0)
    if "--profile" in sys.argv:
        # ⚑⚑ "WHY IS THIS SLOW" IS A MODE, NOT A ONE-OFF. I have hoisted a memo out of a
        # hot loop four times in this file — `consumers`, `producers`, `roundtrips`,
        # `durability` — each time by GUESSING which call was hot and each time after a
        # timeout. The guess was wrong twice. A profile answers it, and putting it here
        # means the next reader measures instead of re-deriving my reasoning.
        import cProfile, pstats
        _pr = cProfile.Profile()
        _pr.enable()
        graph(counts_by_rel=None)
        _pr.disable()
        pstats.Stats(_pr).sort_stats("cumulative").print_stats(15)
        sys.exit(0)
    if "--palette" in sys.argv:
        # ⚑⚑ WHICH SOURCE ANSWERED IS PART OF THE ANSWER. A fallback that reports itself as
        # a derivation is the silent-drift shape; `--palette` says outright whether the peer's
        # measured palette was reachable or the stamped citation answered.
        _okabe_ito()
        print("palette source: %s" % _PALETTE_SOURCE[0][0])
        for _n, _v in sorted(_PALETTE_SOURCE[0][1].items()):
            print("  %-12s %s  rgb%s" % (_n, _ok(_n), tuple(int(x) for x in _v)))
        print("  %-12s %s  (local role — NOT an Okabe-Ito member)"
              % ("neutral", _ok("neutral")))
        print("%d member(s); roles assigned in EDGE_STYLE / NODE_STYLE"
              % len(_PALETTE_SOURCE[0][1]))
        sys.exit(0)
    if "--producers" in sys.argv:
        # ⚑ THE CENSUS AS A TEXT ANSWER, because the question *"nothing writes obs, edge,
        # event, core_fp?"* deserves an answer without rendering an SVG. `n of m` as always:
        # the denominator is every `upsert` call site, so a reader can tell "no production
        # writer" from "no files scanned".
        _p = producers()
        for _fn, _rels in _p.items():
            print("  %-40s %s" % (_fn, ", ".join(_rels)))
        _all, _n = _pycodemod.values("upsert", UPSERT_RELATION_ARG,
                                     _py_files("scripts", "jea"))
        print("%d production writer(s) over %d relation(s); %d of %d upsert call site(s) "
              "(the rest are _selftest fixtures)"
              % (len(_p), len({r for v in _p.values() for r in v}),
                 sum(len(v) for v in _p.values()), _n))
        sys.exit(0)
    if "--roundtrips" in sys.argv:
        # ⚑⚑ THE SQL→PYTHON→SQL LOOP, which is what makes this a pipeline rather than a
        # fan. Direct entries do the read and the write in one body; INDIRECT ones reach
        # the writer through the call graph and carry the path, because reporting a hop
        # as a single step would claim the write happens where it does not.
        _rt = roundtrips()
        for _fn, _v in _rt.items():
            _bs, _rels = _v[0], _v[1]
            _path = _v[2] if len(_v) > 2 else None
            print("  %s" % _fn)
            print("      runs   %s" % ", ".join(_bs))
            print("      writes %s%s" % (", ".join(_rels),
                                         ("   via %s" % " → ".join(_path)) if _path
                                         else ""))
        _direct = sum(1 for v in _rt.values() if len(v) == 2)
        print("%d round trip(s): %d direct, %d through the call graph"
              % (len(_rt), _direct, len(_rt) - _direct))
        sys.exit(0)
    if "--consumers" in sys.argv:
        # ⚑ THE OPERATOR'S QUESTION AS A TEXT ANSWER: *"what gets information from them?"*
        # And its complement, which the same census answers for free — a builder with NO
        # caller is the `rewire_only` class at the SQL layer.
        _c = consumers()
        import query_defs
        for _b in sorted(query_defs.INTERN_BUILDERS):
            _who = _c.get(_b)
            print("  %-32s %s" % (_b, ", ".join(_who) if _who
                                  else "⚑ NO CALLER (or run under a computed name)"))
        _orphan = [b for b in query_defs.INTERN_BUILDERS if b not in _c]
        print("%d of %d builder(s) have an attributed caller; %d do not"
              % (len(query_defs.INTERN_BUILDERS) - len(_orphan),
                 len(query_defs.INTERN_BUILDERS), len(_orphan)))
        # ⚑⚑ THIS TRAILER USED TO EXCUSE 28 ORPHANS AND NOW EXPLAINS ZERO. It said "11 run
        # sites pass a computed name" — true, and it was doing the work of a caveat while
        # the fix was reading `_GROUP`. A warning that names a gap is not a substitute for
        # closing it, and this one let a wrong census stand for two days because it made
        # the wrongness sound accounted for.
        print("   ⚑ every builder is also an arm of `query_defs.verify`, which runs the "
              "registry by ITERATION — a caller with a name, not a literal call site.")
        if _orphan:
            print("   ⚑ %d unattributed: no literal `QB.run`, no group membership. That "
                  "is a fact about this census, NOT about the code." % len(_orphan))
        sys.exit(0)
    if "--edges" in sys.argv:
        # ⚑⚑ THE LAYOUT'S CONSTRAINT BUDGET, AS A MEASUREMENT. I judged "how relaxed is
        # this graph" by eye twice and got it wrong in both directions — first removing
        # `rank=same` on a width fear the operator's own post refutes, then unconstraining
        # every flow edge until the return layer flattened. The ratio is a number; reading
        # it off a picture is the judgement-in-the-turn the standing rule forbids.
        # ⚑⚑⚑ KEYED ON THE EDGE'S KIND, NOT ITS COLOUR. This mode used to classify by
        # matching `"#8899aa" in ln` — recovering a SEMANTIC fact from a PRESENTATION choice,
        # so a restyle would silently rewrite the census and two kinds sharing a colour
        # (`flow` and `returns` are both #bb8822) had to be told apart by a second attribute.
        # The kind is carried on the edge now; the colour is looked up from it.
        _r2, _w2, _rec2 = builder_edges()
        _cen = graph(counts_by_rel=None, reads=_r2, writes=_w2,
                     recursive=_rec2).edge_census()
        _tot = sum(n for n, _f in _cen.values())
        _fre = sum(f for _n, f in _cen.values())
        for k, (n, f) in _cen.items():
            print("  %-26s %4d edge(s), %4d unconstrained (%.0f%%)  %s"
                  % (k, n, f, 100.0 * f / n, EDGE_MEANING.get(k, "")))
        # ⚑ AND IT NAMES THEM. A count told me 1 of 17 `pywrite` edges was relaxed and
        # nothing told me WHICH, so I edited a predicate and re-read the same count to
        # see if it had moved — a diff without an identity, which is the shape that makes
        # a fix indistinguishable from a no-op.
        _gc = graph(counts_by_rel=None, reads=_r2, writes=_w2, recursive=_rec2)
        for _s, _d, _k, _a in _gc.edges:
            if _a.get("constraint") is False:
                print("    relaxed  %-9s %s → %s" % (_k, _s, _d))
        print("%d of %d edge(s) unconstrained (%.0f%%)"
              % (_fre, _tot, 100.0 * _fre / max(1, _tot)))
        sys.exit(0)
    if "--cycles" in sys.argv:
        # ⚑⚑⚑ A CYCLE IN A DATAFLOW GRAPH IS A FINDING, NOT A DRAWING PROBLEM (operator:
        # *"if you can trace a cycle, highlight it; I'll figure out what to do with it
        # then"*). The `after_<rel>` split already handles the ONE cycle kind I knew about —
        # a recursive builder reading what it writes — by construction. Any OTHER cycle is a
        # real claim about the pipeline: a tier that feeds a stage that feeds it back, which
        # either means the drain/rebuild loop is genuinely circular or that an edge is
        # pointing the wrong way. Both are worth seeing; neither is visible by eye in 249
        # edges.
        #
        # ⚑⚑ READ OFF THE GRAPH, NOT THE TEXT. An earlier cut parsed edges back out of the
        # emitted DOT on the reasoning that *"the DOT source IS the graph"* — it is not, it
        # is one SERIALIZATION of the graph, and a reader of it inherits every formatting
        # assumption the writer made. That version only understood one-edge-per-line, so the
        # 3-cycle fixture `a -> b; b -> c; c -> a;` returned zero: the instrument could not
        # be exercised by a test, which is how the defect surfaced.
        _r4, _w4, _rec4 = builder_edges()
        _g = graph(counts_by_rel=None, reads=_r4, writes=_w4, recursive=_rec4)
        _found = _g.cycles()
        _lbl = {k: v["label"] for k, v in _g.nodes.items()}
        if not _found:
            # ⚑ AND AN EMPTY RESULT IS REPORTED AS A PROPERTY OF THE SEARCH. "No cycle found"
            # over the edges THIS graph draws is not "the pipeline is acyclic" — a write the
            # verb scan missed carries no edge here and so can close no loop.
            print("no cycle among the %d edge(s) this graph draws" % len(_g.edges))
            print("   ⚑ an unmodelled write (verb-scan miss, python writer outside the "
                  "`upsert` census) carries no edge here and so cannot close a loop.")
        for _c in _found:
            print("  CYCLE  " + " → ".join(_lbl.get(x, x).split("\\n")[0] for x in _c))
        print("%d cycle(s)" % len(_found))
        sys.exit(1 if _found else 0)
    if "--ranks" in sys.argv:
        # ⚑⚑⚑ ASK THE ENGINE WHERE IT PUT THINGS, rather than judging depth from a picture.
        # `-Tplain` emits `node <name> <x> <y> …` — the LAYOUT's own answer, so "did removing
        # the forced rank actually let the composable stages stack" becomes a number instead
        # of an impression. Every previous decision about this knob was made by eye and two
        # of the three were wrong.
        import subprocess, collections
        _r3, _w3, _rec3 = builder_edges()
        _src = dot(None, reads=_r3, writes=_w3, recursive=_rec3)
        _cmd, _via = _render_cmd("dot", "plain")
        _out = subprocess.run(_cmd, input=_src, capture_output=True, text=True,
                              check=True).stdout
        _ys = collections.defaultdict(list)
        for ln in _out.splitlines():
            f = ln.split()
            # ⚑ EVERY NODE KIND, NOT JUST BUILDERS. A first cut filtered to `n_b_` and
            # reported "1 rank" three times running while I changed knobs that were not the
            # cause — the builders cannot stack until their INPUTS do, so a census that
            # cannot see the relations cannot locate the flattening.
            _pfx = ("n_b_" if "--builders" in sys.argv else "n_")
            if len(f) > 3 and f[0] == "node" and f[1].startswith(_pfx):
                _ys[round(float(f[3]), 1)].append(f[1][len(_pfx):])
        print("  %d distinct rank(s) over %d node(s)"
              % (len(_ys), sum(len(v) for v in _ys.values())))
        # ⚑⚑⚑ NO TRUNCATION. This printed the first SIX names per rank with a `…`, and the
        # elision hid exactly the nodes under investigation: `p_sppf_db_project_sppf_4`,
        # `unit_node` and `node_child` were all inside the tails. I read "every writer sits
        # above its target" off this output and reported it; the render disagreed, and the
        # table I named as wrong (`_unit_cod`) was one of the VISIBLE ones while the
        # actually-wrong `unit_node` was not.
        #
        # ⚑⚑ A DIAGNOSTIC THAT ABBREVIATES ITS POPULATION IS NOT A MEASUREMENT. Every
        # layout claim today was verified against this mode, so the abbreviation was
        # upstream of all of them — the `n of m` discipline this repo applies to every
        # census, absent from the one instrument used to check the censuses.
        for y in sorted(_ys, reverse=True):
            _b = sorted(_ys[y])
            print("    y=%-7s %2d  %s" % (y, len(_b), ", ".join(_b)))
        # ⚑ ONE RANK HOLDING EVERY BUILDER IS THE FAILURE THIS MODE EXISTS TO SEE — it means
        # the layout has no dependency information to order by, whether because a `rank=same`
        # asserted it or because every edge that carried the order was unconstrained.
        print("   ⚑ 1 rank = the stages are being drawn as simultaneous; more ranks = the "
              "layout is reading the dataflow.")
        sys.exit(0)
    if not sys.argv[1:] or "--help" in sys.argv:
        print(__doc__)
        if not sys.argv[1:]:
            sys.exit(0)
    c = None if "--no-counts" in sys.argv else counts("--sandbox" in sys.argv)
    # ⚑ `--no-builders` exists so the splice graph can be turned OFF, not so it is opt-in: the
    # operator asked for ALL the builders and the default must be all of them. The flag is for
    # reading the tier flow alone when the 81-builder layer is noise for the question at hand.
    _r, _w, _rec = ((None, None, None) if "--no-builders" in sys.argv else builder_edges())
    src = dot(c, reads=_r, writes=_w, recursive=_rec)
    if "--out" in sys.argv:
        import subprocess
        path = sys.argv[sys.argv.index("--out") + 1]
        fmt = os.path.splitext(path)[1].lstrip(".") or "svg"
        # ⚑ THE BINARY FOLLOWS THE `layout=` ATTRIBUTE. Invoking `dot` on a source that declares
        # `layout="fdp"` works — graphviz honours the attribute — but naming the engine on the
        # command line keeps the two from disagreeing, and makes `--engine` a real choice rather
        # than a string embedded in output nobody re-reads.
        _eng = "dot"
        for _i, _a in enumerate(sys.argv):
            if _a == "--engine" and _i + 1 < len(sys.argv):
                _eng = sys.argv[_i + 1]
        try:
            _cmd, _via = _render_cmd(_eng, fmt)
            # ⚑ OUTPUT COMES BACK ON STDOUT, NOT VIA `-o`. The container has its own filesystem,
            # so `-o /host/path` writes into the container and vanishes; capturing stdout and
            # writing it here works identically for both backends and needs no bind mount.
            _r = subprocess.run(_cmd, input=src, capture_output=True, text=True, check=True)
            with open(path, "w", encoding="utf-8") as _fh:
                _fh.write(_r.stdout)
            print("pipeflow: wrote %s (%s%s)" % (path, _eng, _via))
        except FileNotFoundError:
            # ⚑ A MISSING `dot` IS REPORTED, NOT SWALLOWED — and the DOT source still goes to
            # stdout so the caller loses nothing. Same discipline as `mdstruct`'s panflute note.
            print("pipeflow: `dot` not on PATH — emitting DOT source instead", file=sys.stderr)
            print(src)
        sys.exit(0)
    print(src)
