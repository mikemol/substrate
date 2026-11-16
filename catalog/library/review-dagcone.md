# External review — `scratch/dagcone.py`

**Provenance.** External reviewer, supplied by the user 2026-08-02. Verbatim below the
rule; nothing edited, elided, or reordered.

⚑ **STATUS: EXTERNAL, NOT VERIFIED BY ME.** Every claim is a hypothesis until
re-measured. Do not cite a figure from this file as measured.

⚑ **AND A RECORDED FINDING IS A HYPOTHESIS AT A LATER TREE STATE** (§24).

---

This script is a masterclass in defensive architecture and "institutional memory as code." The inline documentation doesn’t just explain *what* the code does; it aggressively defends *why* it does it this way, preempting the exact mistakes (silent truncation, double-counting, semantic drift) that clearly burned previous iterations of the system.

Here is a breakdown of the architectural strengths, along with a few technical concerns regarding performance and Python idioms.

### Architecture & Philosophy

**The Duality of Edges:**
Your realization that `rests-on` and `enables` are just a single relationship read from different directions is the strongest conceptual breakthrough in the file. When facing an either/or decision—like deciding between a grounding graph or a sequencing graph—the structurally sound answer is always to look for the correspondence between the two, recursively. By recognizing them as the exact same edge traversed differently, you eliminated an artificial fork in the logic and collapsed two fragmented authorities into one ground truth.

**Union over Sum:**
The distinction between the union of descendant sets and the sum of weights is mathematically precise and absolutely critical for dependency graphs. The 538/417/298 overlapping example flawlessly illustrates why naive tree-folds fail on DAGs.

**Refusal of "Judgement-as-Code":**
Stripping out the `[:5]` truncation and removing the `reach_where` filter are excellent moves. A core domain library should return the absolute truth of the mathematical structure; display caps and domain-specific filters belong at the presentation layer.

---

### Technical Concerns

While the philosophy is bulletproof, the implementation of the graph traversals leaves some performance on the table, specifically in how it interacts with `networkx`.

**1. Repeated Graph Materialization**
In `reach`, `weigh`, and `layers`, you are lazily instantiating a new `nx.DiGraph()` and populating it via a `while` loop that calls `successors(cur)`.

* **The risk:** If these functions are called repeatedly in a tight loop by the consumer, you are paying the overhead of allocating and populating a new `networkx` graph object every single time.
* **The mitigation:** If the underlying DAG is static during these operations, it might be worth offering an entry point that accepts a pre-built `nx.DiGraph` to avoid re-walking the `successors` closure.

**2. Quadratic Complexity in `weigh`**

```python
return {n: len(nx.descendants(g, n)) for n in g.nodes}
```

While elegant, this is computationally expensive. `nx.descendants` performs a traversal (BFS/DFS) to find all reachable nodes. By calling it inside a comprehension over every node in the graph, the time complexity becomes $O(V \times (V + E))$. For a ~3400 module tree, this means potentially millions of edge checks.

**3. Redundant Cycle Checking in `layers`**

```python
if not nx.is_directed_acyclic_graph(g):
    cyc = nx.find_cycle(g)
    raise ValueError(...)
```

`is_directed_acyclic_graph` traverses the graph to look for cycles. If it finds one, you then call `find_cycle`, which traverses the graph *again* to extract the cycle path. You can halve the work by using a `try/except` block, as `find_cycle` raises an `nx.NetworkXNoCycle` exception if the graph is a valid DAG.

---

### Minor Code Quality Notes

* **Broad Exception Catching:** Catching `Exception` on the `networkx` import is slightly dangerous as it could mask a syntax error or a corrupted environment. It is safer to catch `ImportError` or `ModuleNotFoundError`.
* **Type Hinting:** Given the strictness of the domain rules here, adding Python type hints (e.g., `successors: Callable[[Hashable], Iterable[Hashable]]`) would act as an enforceable contract for the consumers providing the edges.

---

## Reading, for the unification planning

### ⚑ THE REVIEWER'S HEADLINE PRAISE IS FOR A CLAIM THE USER CORRECTED TODAY — AND THE CORRECTION MAKES IT *MORE* RIGHT, NOT LESS

The review calls the `rests-on`/`enables` collapse *"the strongest conceptual
breakthrough in the file"* — a single relationship read from two directions. That is
the docstring's claim and it is what I wrote.

**The user refuted my READING of it on 2026-08-02**, on the `OBS-DEADLINE` witness
which carries BOTH `from = {OBS}` and `enables = {OBS}`. I called that "a cycle under
the engine." It is not:

> *"under no reading is that truly a cycle if you read it as properties attached to
> edge directions."*

Two relations over the same pair of nodes is a **multigraph**, not a cycle. A cycle
requires ONE relation to close on itself, and `dep_order` traverses only `from`, so it
never sees the second edge. Each relation projects to its own DAG over the same nodes;
both projections are acyclic; nothing needs reconciling.

⚑ **SO THE COLLAPSE IS CORRECT AND MY EXPLANATION OF IT WAS WRONG IN A WAY THAT WOULD
HAVE PROPAGATED.** I collapsed the relations to their ENDPOINTS, and endpoints alone
are what make two distinct edges look like a contradiction. **The direction is not the
whole fact — WHICH RELATION is.** The reviewer endorsing the one-edge-two-directions
framing is endorsing the half that holds; the half that needs saying is that an edge
carries a *relation*, and a consumer reads one.

**Consequence for the plan:** `T28-edges`' warrant currently justifies itself by
citing a cycle that does not exist. Right conclusion (make work-order legible without
conflating it with citation order), wrong mechanism — the warrant must be rewritten so
a later reader does not reason from a false hazard. *That is a filed correction, not a
new item.*

### Concern 2 IS ALREADY A MEASURED, FIXED DEFECT ELSEWHERE — and the fix was NOT the obvious one

The reviewer flags `weigh`'s `O(V × (V+E))` over a ~3400-module tree. §55 hit exactly
this shape in `split_pipeline` and the diagnosis is the transferable part:

> `_blast_radius` re-ran `gen_build_makefiles.parse_tree()` on EVERY call — **121
> identical tree walks to build one DAG.** Memoised at the single owner:
> **300s+ → 2.7s.**
>
> ⚑ **Before reaching for concurrency, check whether the work is REPEATED.**
> Parallelising 121 redundant walks would only have made the same mistake run faster.

⚑ **BUT NOTE THE DIFFERENCE, because conflating them would be the error.** §55's fix
was *stop rebuilding the same graph*; the reviewer's concern 2 is *one graph, V
traversals over it*, which memoisation does not touch. **Concern 1 is the §55 class
(repeated materialization); concern 2 is a genuinely distinct algorithmic point.** The
reviewer separated them correctly and they should stay separate — a single "make
dagcone faster" item would hide that one half is already-solved-elsewhere and the
other is not.

⚑ **AND `weigh` IS ON THE CRITICAL PATH.** `C4`/`--leverage` ranks the worklist by
measured cone, and `A4`'s ordering depends on it (§55 measured `V4-Coxeter` blocking
**501** modules where citation count said 54 — a ~10× inversion). A `weigh` that is
too slow to run is a `weigh` whose ranking gets replaced by my judgement, which is
precisely the §59 sunk-cost-ordering failure. **UNVERIFIED whether it is currently too
slow** — no timing measured. Do not act on the complexity bound without one; §55's
own lesson is that the wrong performance fix is the one chosen before measuring.

### Concern 3 is CORRECT AND CHEAP — but the refusal itself is load-bearing

Halving the cycle work via `try/except nx.NetworkXNoCycle` is right. ⚑ **What must NOT
change is that `layers` REFUSES a cycle BY NAME rather than silently ordering it.**
That refusal is the tool's contract: a cycle in a dependency graph is a finding, and a
`layers` that returned *something* for a cyclic graph would be the silent-truncation
class the reviewer praises the file for avoiding.

⚑ **AND THE MULTIGRAPH CORRECTION ABOVE RAISES A QUESTION THE REVIEW COULD NOT SEE:**
if two relations share a node pair, a caller that merges them before calling `layers`
would trigger a cycle refusal on a graph that has none *per relation*. **`layers`
operates on ONE projection**; whether anything currently merges relations before
calling it is UNMEASURED and worth checking, because a false cycle refusal reads as a
data defect rather than a caller defect.

### The two "minor" notes are NOT minor here, and one is already a filed item

* **Broad `except Exception` on the networkx import** — masks a syntax error or
  corrupted environment as "networkx absent." That is the **absent-dependency-scores-
  as-a-pass** class, ruled on twice in this repo (`jea_circuit.py:197` returning `True`
  on `SKIP (numpy absent)`; `mdstruct` reporting `0/0` and PASSING when pandoc was
  missing). Same shape, third instance. `ImportError`/`ModuleNotFoundError` is the fix.
* **Type hints as an enforceable contract** — this is `T16`, already wired: the mypy
  ratchet is live with a **108-key census**. So the reviewer is naming an existing
  paydown lane rather than a new build, and `dagcone`'s `successors` callable is
  exactly the kind of consumer-supplied contract the ratchet exists to make checkable.

### What this review does NOT cover

The reviewer did not exercise `reach`'s correctness against a real DAG, did not
comment on the union-vs-sum implementation (only endorsed the reasoning), and did not
see `--leverage`/`C4`, which is `dagcone`'s principal live consumer. Silence there is
scope, not a pass.
