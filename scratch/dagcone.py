#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""THE cone authority: reachability, and the part a set blocks EXCLUSIVELY.

⚑ WHY THIS EXISTS — TWO `leverage` DEFINITIONS UNDER ONE NAME (user, 2026-08-02:
*"that needs lifting to support dedup"*).  `split_pipeline.leverage` answered it
over the Agda import DAG; `worklist_gate.leverage` answered it over the warrant
graph.  Neither was a copy of the other and both were correct, which is exactly
the shape that hides: a shared NAME is not a shared authority, and the same
relation with two implementations grows two answers.  `agda_files()` was four
bodies under one name; this is the same class over a graph relation.

⚑ AND THE DEFECT THEY SHARED IS WHY IT HAD TO BE LIFTED, NOT MERELY DEDUPED
(user: *"does it FREE all the elements in that cone, or do some remain blocked
by other things?  This applies to ALL DAG ordering, not just agda work"*).  Both
called their result "what clearing this would free".  A cone is REACHABILITY:
every node transitively depending on the seeds.  A node in it can sit behind
several blocking sets at once, so clearing one frees only the nodes whose
remaining blockers are all inside it.

MEASURED on the three ban-directive buckets: cones of 538 / 417 / 298, exclusive
205 / 97 / 82 -- 60-75% shared.  The naive reading was wrong by ~4x, and the
figures never summed (538+298+417 over a ~3400-module tree is one subtree counted
three times).  Fixing that in one consumer and leaving the other is how a
correction becomes a divergence.

⚑ AND `rests-on` / `enables` ARE NOT TWO EDGE KINDS -- THEY ARE ONE ARROW READ
FROM BOTH ENDS (user, 2026-08-02: *"one is the reverse arrow of the other;
injective vs surjective dependency"*).  I had carried them as a genuine
distinction the graph would need to model, and named it as the part that "remains
ours" after delegating the walk to networkx.  It is `G` and `G.reverse()`.  The
bib stores both spellings so each entry can state its own relations without
editing its neighbours; that is an AUTHORING convenience, not two relations.

The substantive half is which FOLD each reading wants:
  * GROUNDING is many-to-one -- an item rests on several premises and needs them
    all, a conjunction, so LAYERING follows this direction;
  * SEQUENCING is one-to-many -- clearing this makes several things cheaper, a
    fan-out, so WEIGHT follows this one.
Same arrows, different question, which is exactly why the bib insists `enables`
counts toward leverage and never toward layer.  Two functions over one graph, not
two graphs.

THE GRAPH IS SUPPLIED, NEVER DISCOVERED HERE.  Callers own their edges -- the
import DAG comes from `gen_build_makefiles.parse_tree()`, the warrant graph from
the bib -- and this module owns only the walk.  Inventing an edge source here
would make it a second authority for whatever it guessed at.

⚑ AND THE WALK ITSELF IS networkx (user, 2026-08-02: *"how much of this is us
reinventing networkx?"*).  My first cut hand-wrote the BFS -- which is exactly
`nx.descendants`, and `pycodemod --available networkx` reports **3.6.1 in the
venv**.  The reuse-search should have fired on the words "reachability closure"
before a line was written; instead it fired on the user's question, which is the
same miss this repo has recorded against `conduit_resolve`, `_rename_pairs` and
`euclid`.  ⚑ THE INSTRUMENT WAS BUILT IN THE SAME BREATH: "is this library
importable here" had no command, so it was being answered with `python3 -c`.

What is NOT networkx, and is why this module still exists: **the exclusivity
subtraction and the refusal to call a cone a liberation**.  `nx.descendants`
answers reachability; nothing in it says that two blocking sets overlap by 60-75%
and that reporting either as "frees N" is wrong by ~4x.  That is the domain
finding, and it is what gets a home here.
"""

try:
    import networkx as nx
except Exception:                        # pragma: no cover - environment probe
    nx = None


def reach(seeds, successors):
    """Every node transitively reachable from `seeds`, EXCLUDING the seeds.

    `successors(node) -> iterable` is the caller's edge relation: importers for
    an import DAG, dependents for a claim graph.

    ⚑ `nx.descendants` IS THE WALK.  The graph is built lazily from the
    caller's successor function -- callers hold their edges in dicts, adjacency
    lists and closures, so demanding an `nx.DiGraph` at every call site would
    push graph construction into five modules to save it in one.

    ⚑ NO DEPTH BOUND, and that is load-bearing rather than incidental: a bound
    here silently truncates (the `_conduit_set` `range(3)` class, where 1506 of
    2964 modules reached past it).  `descendants` is unbounded and cycle-safe
    by construction, which is one fewer invariant to re-establish by hand.

    The fallback is a plain BFS so a bare environment (a hook with no venv)
    degrades to a slower answer rather than to NO answer -- but it is a
    FALLBACK, deliberately not the primary, so the two cannot drift unnoticed:
    a selftest case asserts they agree."""
    seeds = list(seeds)
    if nx is not None:
        g = nx.DiGraph()
        g.add_nodes_from(seeds)
        seen, stack = set(seeds), list(seeds)
        while stack:                     # materialise only the reachable part
            cur = stack.pop()
            for nxt in successors(cur):
                g.add_edge(cur, nxt)
                if nxt not in seen:
                    seen.add(nxt)
                    stack.append(nxt)
        out = set()
        for s in seeds:
            out |= nx.descendants(g, s)
        return out - set(seeds)
    return _reach_bfs(seeds, successors)


def _reach_bfs(seeds, successors):
    """The dependency-free fallback — kept honest by a selftest agreement case."""
    out, stack = set(), list(seeds)
    while stack:
        cur = stack.pop()
        for nxt in successors(cur):
            if nxt not in out:
                out.add(nxt)
                stack.append(nxt)
    return out - set(seeds)


def rank(seeds, successors):
    """[(n_reached, seed)] descending — which seed reaches most, ALL of them.

    ⚑ THIS WAS THE "DOMAIN LAYER" AND IT IS NOT DOMAIN (user, 2026-08-02: *"I
    question whether the concrete difference is legitimate ... much of what's
    presumed to be domain-specific is stale, calcified judgement-as-code"*).  I
    defended `split_pipeline.leverage` as differing by "top-seed ranking".
    Reading it: it computes each seed's cone, sorts descending, truncates.
    Ranking nodes by reach is the same generic operation as reach itself --
    there is nothing about Agda imports in it.

    ⚑ AND THE TRUNCATION WAS JUDGEMENT FROZEN INTO THE COMPUTATION.  It
    returned `top[:5]`: a DISPLAY decision made once, baked in where no caller
    could ask for more, and silently dropping the 6th-largest seed from every
    consumer.  That is the `[:6]` class this repo already recorded against
    `resolve_notinscope` (64 names have more than 6 homes).  The cap belongs at
    the print, so it is returned WHOLE.

    ⚑ AND THE ROWS OVERLAP -- same caveat as `cone`.  Two seeds under one
    subtree both report it, so this ORDERS seeds and must never be SUMMED."""
    return sorted(((len(reach([s], successors)), s) for s in seeds),
                  reverse=True)


# ⚑ THERE IS NO `reach_where` HERE, AND ITS ABSENCE IS THE FINDING.  Told that
# `worklist_gate.leverage`'s "composition" is just a tree merge (user,
# 2026-08-02: *"that's just a tree merge, though.  That doesn't feel distinct
# from what we're doing"*), I agreed -- correctly -- and then LIFTED A FILTERED
# REACH to prove it.  `pycodemod --calls reach_where` answered:
#
#     reach_where: 1 def(s), 0 call(s)
#        ⚑ DEAD CAPABILITY — defined and never called (the rewire_only class)
#
# The caller already holds a `cone` closure that delegates here, so
# `[c for c in cone(key) if open(c)]` composes with it in one line and needs no
# API.  I built machinery to win an argument, which is the same reflex as
# `rewire_only` (written, documented, zero callers) that this repo filed R13
# for.  **Agreeing with a critique is not a licence to add code**; the merge is
# real and it is already expressible.  Deleted, and recorded so the next reader
# does not re-add it as an obvious convenience.


def orient_hyper(hyperedges):
    """{"rank": {item: int}, "oriented": [...], "free": [...], "conflict": [...]}

    Each hyperedge is `(file, [items...])` — ONE relation over k items, never
    k*(k-1)/2 pairwise constraints.

    ⚑ THE PAIRWISE MODEL WAS PROVABLY UNSATISFIABLE ON THIS DATA, AND ITS FIRST
    RUN MEASURED MY OWN FRAMING.  `orient` shattered each co-read file into every
    pair of its readers, then 2-coloured.  But a file read by k>=3 items becomes a
    k-CLIQUE, and a clique on 3+ nodes is never bipartite -- so the two reported
    "conflicts" were the 6-clique on `pycodemod.py` and the 3-clique on
    `bibstruct.py`, i.e. artifacts of the shattering rather than findings about
    the worklist.  `0 oriented, 0 free, 2 in conflict` was the tell: an instrument
    that classifies NOTHING is reporting on itself.

    ⚑ AND THE SHATTERING DESTROYED THE QUESTION.  "Which of these 6 items touches
    `pycodemod.py` first" is a k-ary question; splitting it into 15 yes/no pair
    questions asks something the data cannot answer and then reports the
    contradiction as structure.  The hyperedge IS the unit -- the shared file is
    one fact about six items, not fifteen facts about two.

    ⚑ SO THE ROLE IS A RANK, NOT A COLOUR.  The torsor reading survives intact and
    generalises: roles are per-item, an edge is their DIFFERENCE, and no item
    carries an absolute rank (adding a constant to a component changes nothing --
    the same torsor action, now over Z instead of Z/2).  What changes is the
    codomain.  A 2-colouring can only say "differs"; a rank says WHICH SIDE, which
    is what an `enables` edge needs and what a colour could never supply.

    ⚑ COHERENCE IS ACYCLICITY, NOT BIPARTITENESS.  Constraints come only from
    edges already ORDERED by evidence; a hyperedge with no such evidence
    constrains nothing and its members are mutually FREE.  A genuine conflict is
    then a directed cycle -- reported, never resolved by picking -- and it cannot
    be manufactured by the encoding the way an odd cycle could."""
    items = sorted({i for _e in hyperedges for i in _e[1]})
    if nx is None:
        return {"rank": {}, "oriented": [], "free": [],
                "conflict": [], "unmeasured": "networkx absent"}

    # ⚑ THE CONSTRAINT SET IS THE EVIDENCE, AND HERE IT IS EMPTY BY MEASUREMENT.
    # A co-read is a COUPLING, not a precedence: six items reading one file says
    # they are entangled, and says NOTHING about which precedes which.  Inventing
    # a direction from membership is exactly the coordinate a torsor forbids.
    g = nx.DiGraph()
    g.add_nodes_from(items)
    for _f, ms, *rest in hyperedges:
        prec = rest[0] if rest else ()
        for a, b in prec:
            g.add_edge(a, b)

    conflict = []
    try:
        order = list(nx.topological_sort(g))
        rank = {n: i for i, n in enumerate(order)}
    except nx.NetworkXUnfeasible:
        for cyc in nx.simple_cycles(g):
            conflict.append(cyc)
        rank = {}

    # ⚑ THE RANK OF AN UNCONSTRAINED ITEM IS A SORT ARTIFACT, NOT A MEASUREMENT,
    # and reading it as one made the FREE branch unreachable on the live data.
    # `topological_sort` numbers an edgeless graph 0..k-1, so six mutually
    # unordered items came back with six DISTINCT ranks and a naive
    # `len(set(ranks)) == len(ms)` test called that an orientation -- inventing
    # precisely the arbitrary coordinate the torsor reading forbids.  A hyperedge
    # is oriented only where the CONSTRAINT GRAPH relates its members, so the
    # test is reachability in `g`, never adjacency of their rank integers.
    oriented, free = [], []
    for _f, ms, *rest in hyperedges:
        if conflict or any(rank.get(m) is None for m in ms):
            continue
        ordered = all(nx.has_path(g, a, b) or nx.has_path(g, b, a)
                      for i, a in enumerate(ms) for b in ms[i + 1:])
        if ordered and len(ms) > 1:
            oriented.append((_f, sorted(ms, key=lambda m: rank[m])))
        else:
            free.append((_f, sorted(ms)))
    return {"rank": rank, "oriented": oriented, "free": free,
            "conflict": conflict}


def orient(pairs):
    """{"roles": {item: 0|1}, "oriented": [...], "free": [...], "conflict": [...]}

    ⚑ SUPERSEDED BY `orient_hyper` — THIS MODEL IS WRONG ON k>=3 CO-READS.  Kept
    only because its torsor reasoning below is correct and generalises; the
    2-colouring it implements is not.  A caller shattering a shared file into
    pairs before arriving here gets odd cycles BY CONSTRUCTION.  Use
    `orient_hyper`, which takes the file and its readers as one relation.

    ⚑ AN EDGE IS A TORSOR, THE MULTIGRAPH A LATTICE (user, 2026-08-02: *"it
    doesn't matter. The edge is a torsor, the multigraph a lattice. Allow the
    edges to adopt the roles required to achieve coherence."*).

    I spent three passes hunting an INTRINSIC direction for each co-read pair --
    in the witness AST, then the claim prose, then the remedy parts -- and came up
    empty each time, because a torsor has NO DISTINGUISHED POINT.  There is no
    absolute orientation to recover; there is only relative displacement, and the
    roles are fixed by requiring the WHOLE STRUCTURE to cohere rather than by
    reading any edge alone.  Asking "which way does this one edge point" is
    choosing a coordinate in a space that has only differences.

    ⚑ SO THE ROLE IS PER-ITEM AND THE ORIENTATION IS THEIR DIFFERENCE.  Flipping
    an item flips every edge it touches, which is exactly the torsor action -- so
    an assignment is a 2-colouring, an edge is ORIENTED when its endpoints differ,
    and WEDGE-ZERO (`a ∧ a = 0`) when they match.  Coherence is bipartiteness; an
    odd cycle is a genuine conflict and is REPORTED, never resolved by picking.

    ⚑ AND THE ASSIGNMENT IS DETERMINED ONLY UP TO THE ACTION.  Every component's
    colouring may be flipped wholesale with no loss, so the RELATIVE structure is
    rigid while no item carries an absolute role.  Reporting a role as though it
    were intrinsic would re-introduce the arbitrary coordinate this dissolves --
    the roles are returned for reading the differences, nothing more.

    ⚑ FREE PAIRS ARE A MEASUREMENT, NOT A GAP.  A pair whose endpoints land in the
    same class carries no precedence: the constraint system ADMITS both
    orientations, so the coupling is real and the ordering is not.  That is the
    honest form of what I nearly filed as "direction unknown" -- and nearly filed
    as an invented direction before that."""
    items = sorted({x for p in pairs for x in p[:2]})
    if nx is None:
        return {"roles": {}, "oriented": [], "free": [],
                "conflict": [], "unmeasured": "networkx absent"}
    g = nx.Graph()
    g.add_nodes_from(items)
    for a, b, *_rest in pairs:
        g.add_edge(a, b)

    roles, conflict = {}, []
    for comp in nx.connected_components(g):
        sub = g.subgraph(comp)
        try:
            colour = nx.bipartite.color(sub)
        except nx.NetworkXError:
            # an odd cycle: no coherent assignment for this component
            cyc = nx.find_cycle(sub)
            conflict.append([e[0] for e in cyc])
            for n in comp:
                roles[n] = None
            continue
        roles.update(colour)

    oriented, free = [], []
    for a, b, *rest in pairs:
        ra, rb = roles.get(a), roles.get(b)
        row = (a, b) + tuple(rest)
        if ra is None or rb is None:
            continue
        (oriented if ra != rb else free).append(row)
    return {"roles": roles, "oriented": oriented, "free": free,
            "conflict": conflict}


def weigh(nodes, successors):
    """{node: n_descendants} — every node's transitive weight, in ONE pass.

    ⚑ THE COLLAPSE IS WHERE THE LEVERAGE WAS BEING LOST (user, 2026-08-02:
    *"something that has hundreds or thousands of items doesn't get to have a
    leverage of any smaller than its deduped content"*).  An item is a FOLD of its
    population: `A5` is 216 ban keys shown as one row for legibility.  Ranking by
    warrants-that-cite-me charges 215 of those keys nothing, so the fold that made
    the worklist readable also made it mis-ordered -- `A5` (216 keys) and `G1` (1)
    sorted adjacently at the same `lev`.

    ⚑ AND THE FIX IS NOT A FLOOR RULE, IT IS PUTTING THE CONTENT IN THE GRAPH.  I
    was about to propose `leverage >= |deduped content|` as a rule to enforce.
    With each key as a node under its item, `len(descendants(A5)) >= 216` holds BY
    CONSTRUCTION -- no rule, no `size=` special case, no second grade to reconcile.
    The two-grade split (declared bib-closure vs evaluated witness-report) was
    never two quantities; it was one DAG missing most of its nodes, and "declared"
    is what you get counting only the top layer.

    ⚑ UNION, NEVER SUM -- this is the whole subtlety and summing gets it wrong.
    Children's weights double-count shared descendants: the three ban buckets
    overlap 60-75%, so `538+417+298` counts one subtree three times over a ~3400
    module tree.  Cardinality of the UNION of descendant SETS is exact.
    `nx.descendants` returns a set per node and the DAG is small, so this is a
    direct read rather than a hand-rolled reverse-topological fold -- the fold is
    the standard DAG dynamic program, and reaching for it here would be
    reinventing what the library already answers exactly.

    ⚑ WEIGHT IS PARTICIPATION, LIKE `cone`'s FIRST RETURN.  It says how much sits
    beneath a node, NOT how much clearing it would free; overlapping weights must
    never be summed across siblings.  Use `cone(..., against=)` for the
    exclusive question."""
    nodes = list(nodes)
    if nx is not None:
        g = nx.DiGraph()
        g.add_nodes_from(nodes)
        seen, stack = set(nodes), list(nodes)
        while stack:
            cur = stack.pop()
            for nxt in successors(cur):
                g.add_edge(cur, nxt)
                if nxt not in seen:
                    seen.add(nxt)
                    stack.append(nxt)
        return {n: len(nx.descendants(g, n)) for n in g.nodes}
    return {n: len(_reach_bfs([n], successors)) for n in nodes}


def layers(nodes, successors):
    """[[node, ...], ...] — topological generations, sources first.

    ⚑ `order()` COMPUTED THIS BY HAND.  Dependency layering is
    `nx.topological_generations`; a bespoke level assignment is the same
    reinvention as the BFS this module already retired.  Returned WHOLE and
    unsorted-within-layer -- ordering inside a generation is the caller's
    display decision, and baking one in here is the `[:5]` class."""
    if nx is None:
        raise RuntimeError("layers requires networkx; no honest fallback "
                           "(a hand-rolled layering is what this replaces)")
    g = nx.DiGraph()
    g.add_nodes_from(nodes)
    for n in list(nodes):
        for nxt in successors(n):
            g.add_edge(n, nxt)
    if not nx.is_directed_acyclic_graph(g):
        # ⚑ A CYCLE IS A FINDING, NOT A CRASH.  `reach` is cycle-safe by
        # construction; layering is not defined on one, so name the cycle rather
        # than silently returning a partial order.
        cyc = nx.find_cycle(g)
        raise ValueError("not a DAG; cycle: %s"
                         % " -> ".join(str(a) for a, _b, *_ in cyc))
    return [sorted(gen, key=str) for gen in nx.topological_generations(g)]


def cone(seeds, successors, against=()):
    """(reached, exclusive) — what a set BLOCKS, and what only it blocks.

    ⚑ `reached` IS PARTICIPATION, NOT LIBERATION.  Say "blocks N", never
    "frees N": the difference is the overlap with the other blocking sets, and
    it was most of the number every time it was measured.

    `against` is the other blocking sets to subtract.  Omitted, `exclusive` is
    None -- UNDEFINED, not equal to the cone.  With nothing to compare against
    there is no evidence of exclusivity, and defaulting to "all of it" would
    restate the overclaim this module exists to retire."""
    reached = reach(seeds, successors)
    if not against:
        return reached, None
    other = set()
    for grp in against:
        other |= reach(grp, successors)
    return reached, reached - other


def _selftest():
    cases = []

    def check(label, got, want):
        cases.append((label, got == want, got, want))

    #   a -> c -> d ,  b -> c
    edges = {"a": ["c"], "b": ["c"], "c": ["d"], "d": []}
    succ = lambda n: edges.get(n, [])

    check("reach is transitive", reach(["a"], succ), {"c", "d"})
    check("reach excludes the seeds", "a" in reach(["a"], succ), False)

    # ⚑ THE CASE THAT PINS THE WHOLE POINT: `a` and `b` both reach {c, d}, so
    # neither frees anything on its own.  A tool reporting `a` blocks 2 and
    # calling that "frees 2" is wrong by all of it.
    _r, _e = cone(["a"], succ, against=[["b"]])
    check("cone reports what the set reaches", _r, {"c", "d"})
    check("a fully-shared cone is exclusively EMPTY", _e, set())

    #   e -> f (nothing else reaches f)
    edges["e"] = ["f"]
    edges["f"] = []
    _r2, _e2 = cone(["e"], succ, against=[["a"]])
    check("an unshared cone is exclusively its whole self", _e2, {"f"})

    # ⚑ WITHOUT `against`, EXCLUSIVITY IS UNDEFINED -- not total.  Returning the
    # cone here would silently restate "clearing this frees all of it", the
    # overclaim this module was lifted to retire.
    _r3, _e3 = cone(["a"], succ)
    check("no comparison set means exclusivity is None", _e3, None)

    # a cycle must terminate — no depth bound, so the visited set is the guard
    edges["x"] = ["y"]
    edges["y"] = ["x"]
    check("a cycle terminates", reach(["x"], succ), {"y"})

    # ⚑ `rank` ORDERS SEEDS BY REACH, and returns ALL of them.  The body it was
    # lifted from truncated to `[:5]` -- a display cap baked into the
    # computation, so no caller could ask for the 6th.  A case pinning the
    # length is what stops that being re-introduced as "a sensible default".
    check("rank orders seeds by reach, largest first",
          [s for _n, s in rank(["a", "e"], succ)], ["a", "e"])
    check("rank returns every seed, never a truncated head",
          len(rank(["a", "b", "e", "x"], succ)), 4)
    check("rank reports the reach count alongside the seed",
          dict((s, n) for n, s in rank(["a", "e"], succ)), {"a": 2, "e": 1})

    # ⚑ THE FALLBACK MUST AGREE WITH THE PRIMARY, or a bare environment gets a
    # DIFFERENT answer and nobody notices until the two are compared.  This is
    # the `agda_files()` lesson applied to a deliberate second implementation:
    # keeping one is fine, letting it drift is not.
    for seed in ("a", "e", "x"):
        check("networkx and the fallback agree from %s" % seed,
              reach([seed], succ), _reach_bfs([seed], succ))

    # ⚑ THE CASE THAT SEPARATES UNION FROM SUM, and a sum-based `weigh` PASSES
    # every other case here.  `a` and `b` both reach {c, d}: the union is 2, the
    # naive `1 + weight(c)` fold summed over children of a shared node
    # double-counts.  This is the 538/417/298-over-3400 defect in miniature.
    w = weigh(["a", "b", "c", "d"], succ)
    check("weight is the transitive descendant count", w["a"], 2)
    check("a shared child is counted ONCE, not per parent", w["c"], 1)
    check("a leaf weighs nothing", w["d"], 0)

    # ⚑ THE COLLAPSE CASE: an item with N content nodes weighs AT LEAST N.  This
    # is the rule that does not need to be a rule -- putting the content in the
    # graph makes the floor hold by construction.
    edges["ITEM"] = ["k1", "k2", "k3"]
    for k in ("k1", "k2", "k3"):
        edges[k] = []
    w2 = weigh(["ITEM"], succ)
    check("an item weighs at least its deduped content", w2["ITEM"] >= 3, True)

    # layering: sources first, and the content sits below its item
    ls = layers(["ITEM", "k1", "k2", "k3"], succ)
    check("topological layers put an item above its content",
          (ls[0], sorted(ls[1])), (["ITEM"], ["k1", "k2", "k3"]))

    # ⚑ A CYCLE IS NAMED, NOT SWALLOWED.  `reach` tolerates one by design; a
    # layering on a cycle has no answer, and returning a partial order would be
    # the silent-truncation class.
    try:
        layers(["x", "y"], succ)
        check("layering refuses a cycle", "returned", "ValueError")
    except ValueError:
        check("layering refuses a cycle", "ValueError", "ValueError")

    # ── orient_hyper ─────────────────────────────────────────────────────
    # ⚑ THE DISCRIMINATING CASE, AND IT IS THE LIVE SHAPE.  Six items co-reading
    # ONE file is a 6-clique once shattered, and a clique on >=3 nodes is never
    # bipartite -- so `orient` reported it as a CONFLICT.  It is not a conflict;
    # it is one hyperedge with no precedence evidence, i.e. six mutually FREE
    # items.  This case fails against the pairwise model BY CONSTRUCTION.
    six = [("pycodemod.py", ["A5-as-reach", "DEPS", "T23",
                             "T25-globals", "T25-library", "T28-closure"])]
    sh = orient_hyper(six)
    check("a k=6 co-read is NOT a conflict", sh["conflict"], [])
    check("a k=6 co-read with no evidence is FREE",
          [f for f, _ms in sh["free"]], ["pycodemod.py"])
    check("and it is ONE relation, not 15 pairs", len(sh["free"]), 1)

    # the same data through the superseded model: an odd cycle it cannot colour
    pairs = [(a, b, "pycodemod.py")
             for i, a in enumerate(six[0][1]) for b in six[0][1][i + 1:]]
    check("⚑ the PAIRWISE model conflicts on the same data",
          len(orient(pairs)["conflict"]) > 0, True)
    check("⚑ ...and therefore orients NOTHING",
          len(orient(pairs)["oriented"]), 0)

    # evidence ORDERS members; without it there is nothing to order
    ev = [("f.py", ["a", "b"], [("a", "b")])]
    check("evidence orients a hyperedge",
          orient_hyper(ev)["oriented"], [("f.py", ["a", "b"])])

    # ⚑ COHERENCE IS ACYCLICITY: a genuine conflict is a DIRECTED cycle, which
    # the encoding cannot manufacture the way an odd cycle could.
    cyc = [("f.py", ["a", "b"], [("a", "b"), ("b", "a")])]
    check("a directed cycle IS reported", len(orient_hyper(cyc)["conflict"]) > 0,
          True)

    ok = sum(1 for _n, g, _a, _b in cases if g)
    for n, g, got, want in cases:
        if not g:
            print("  FAIL %s: got %r want %r" % (n, got, want))
    print("selftest: %d/%d" % (ok, len(cases)))
    return ok == len(cases)


if __name__ == "__main__":
    import sys
    sys.exit(0 if _selftest() else 1)
