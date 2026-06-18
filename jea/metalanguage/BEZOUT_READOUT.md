# The Bézout framing of the grammar readout — and why it matters

*A note for AI-Q (and any future reader). The post-handoff audit correctly caught two stale
docstrings, but those were surface artifacts. The substantive content is below: the readout is the
extended Euclidean algorithm's back-substitution, and recognizing that is what forced the
materialization fix. The typos were a symptom of an arc that ended somewhere the docstrings hadn't
caught up to; this explains where it ended.*

---

## 1. The claim, stated once

> Recognition is the forward pass of the extended Euclidean algorithm (EEA). The grammar readout is
> its back-substitution. The Bézout coefficients you read off the back-substitution *are* the grammar
> rules. And because EEA back-substitution streams — it emits each coefficient as it walks the
> retained chain, holding nothing — the SPPF → ABNF readout streams too, in O(1) working set,
> regardless of forest size.

Everything else here is the unpacking of that, and the consequence: a 50 GiB SPPF emits to ABNF in
constant memory, and the reason it can is structural, not a clever trick.

---

## 2. What EEA actually does (the shape, not the arithmetic)

The extended Euclidean algorithm computes `gcd(a, b)` *and* the Bézout coefficients `(s, t)` with
`s·a + t·b = gcd`. It runs in two coupled directions:

**Forward (the division descent).** Repeatedly divide: `a = q·b + r`, then recurse on `(b, r)`. Each
step *registers a smaller subproblem* and *stores its quotient* `q`. The descent strictly decreases
the remainder, so it terminates at `r = 0` — the base case, where the current divisor is the gcd.

**Backward (the substitution).** Once the base case is reached, walk *back up* the chain of stored
steps. At each step you already know the Bézout coefficients of the subproblem below you; you compose
them with *this* step's stored quotient to get this step's coefficients. The gcd's certificate is
assembled from the bottom up.

The two facts that matter for us:

1. **Every step is retained.** EEA does not mutate a running pair of coefficients toward an answer; it
   keeps the whole chain `(r₀,q₀), (r₁,q₁), …` and reads the answer off it. (In our substrate this is
   not an analogy — `jea_divstr.trace_fold` literally folds this retained Euclidean descent, and
   `jea_pyalg.Trace` is "the decomposition chain = the GRADING.")

2. **The Bézout coefficients come off the retained chain by a walk.** You do not recompute them; you
   *traverse* the chain, grabbing each step's stored `q` and composing. Back-substitution is a read
   over a structure that already exists.

Hold onto both. They are the entire payload.

---

## 3. The isomorphism: Earley = EEA = SPPF

The substrate already had this identification recorded ("predictor/completer ARE EEA's two passes")
but treated it as a slogan. It is exact. Line it up:

| EEA | Earley parsing | jea_core primitive |
|---|---|---|
| divide `a = q·b + r`, recurse on `(b,r)` | **predict / scan** — expect a symbol, descend into its productions / consume a token | `wedge` (decompose a node into head + first-child + remainder) |
| store the quotient `q` at this step | **the dotted item** — a partial production with its progress and span | a normal interned node (the wedge's components, retained) |
| the chain of retained steps | **the chart** — all items, kept | `trace` (the retained decomposition chain = the grading) |
| back-substitute: compose this step's `q` with the sub-result | **complete** — advance a waiting item by composing the finished sub-parse | `recon` (rebuild + re-intern the advanced node) |
| reach `r = 0` (the gcd) | **accept** — the start symbol spans the whole input | a structural readout (does the node exist?) |
| **read the Bézout coefficients off the chain** | **read the grammar off the parse forest** | **the backward walk — `stream_rhs`** |

The last row is the one this note is about. The first five rows say *recognition is the forward EEA
descent, run by interning consequences to a fixpoint*. The last row says *the readout is the backward
substitution*. One retained chain, two reads: forward composes the obligations into a result; backward
reads the witness back out.

**Why the Bézout coefficients are literally the grammar rules.** When you back-substitute over a parse
forest, the "coefficient" you grab at each step is the symbol that step consumed — the base child of
the wedge. Walk the chain of a `parse(S)` node and the bases you collect, in order, *are* the
right-hand side of S's production: `S → a S b` falls out of the chain as `[a, S, b]`. The grammar is
not something you reconstruct into a separate dictionary and then format. The grammar **is** the chain
of Bézout components; emitting ABNF is dumping the chain as you walk it.

This is exactly the line in the code:

```python
def stream_rhs(I, parse_node):
    cur = parse_node
    while True:
        w = D.wedge(cur)          # one division step
        if w is None: return      # reached the atom (r = 0)
        nb = I.nodes[w.base]
        yield nb.payload[0] if (nb.kind == "tok" and nb.payload) else nb.op   # the Bézout component
        if w.rem == -1: return
        cur = w.rem               # descend to the next step
```

`wedge` is one division step. The loop is the back-substitution walk. The `yield` is "grab this step's
coefficient." There is no grammar dictionary, no parse-tree object, no fold accumulator — the chain is
the output, in order.

---

## 4. The substantive finding: where the materialization was hiding

This is what the audit did not surface. The reason the readout was *rewritten* (not just renamed from
`read_rhs` to `stream_rhs`) is a real defect that the Bézout framing made visible, and it was a
**triple** materialization — three stacked copies of the whole forest, where zero are needed.

A first, natural-looking design for "SPPF → ABNF" is:

1. walk the parse forest, **building a grammar dict** `{S: [[a,S,b],[a,b]], …}`;
2. then format that dict as ABNF text.

Ask the diagnostic question: *what happens if the SPPF is 50 GiB?* Step 1 is fatal. The dict is
O(forest) in size, it must exist in full before step 2 emits a single byte, and you have just built a
second 50 GiB structure beside the first. That is the "ew" — the grammar dict is the forbidden digest
the substrate warns against (`chart[k]` wearing grammar clothes), reintroduced one level up.

But the dict was only the *top* of the stack. Underneath it, the obvious "faithful" readout —
`trace_fold` over `trace(node)` — has the same disease twice more:

- **`trace(node)` materializes eagerly.** It recurses building the entire nested `Trace` object
  *before* any fold runs. On a 50 GiB forest, `trace` of the root allocates the whole chain first.
- **`trace_fold` accumulates to the base before composing.** Look at its shape:
  `step(head, base, trace_fold(...))` — it recurses all the way to the base case, *then* composes on
  the way back up. Even with a lazy trace, nothing is emitted until the deepest call returns; the
  entire call stack (= the entire chain) is held.

So `read_rhs = trace_fold(over trace(node))` was **two** materializations, and the grammar dict on top
made **three**. All three vanish under the Bézout reading, because back-substitution as *actually run*
never builds-then-folds — it emits each coefficient *as the forward steps produce them*, in order. The
faithful readout is therefore a **loop over `wedge`** that `yield`s, which is precisely `stream_rhs`:
O(1) working set, nothing held beyond the current step, a 50 GiB SPPF emitted in constant memory.

`trace_fold` is correct and valuable — for small terms, where materialization is free, it is the clean
"different targets = different reads of the same trace" recursor. It is the wrong tool *only* at scale,
and the Bézout framing is what tells you that crisply: back-substitution streams; a fold that descends-
then-composes does not.

---

## 5. The deepest correction: *retain all intermediates* is the forest's job, not the readout's

The substrate's central operation (the "Σ-OBLIGATION spine") had been stated as:

> discharge an obligation by composing the discharges it depends on, **retaining all intermediates**.

The 50 GiB case forces a correction to that sentence, and it is the single most important conceptual
takeaway here:

> **Retention is a property of the FOREST. It is not a property of the READOUT.**
> The forest keeps everything — every interned node persists, shared, hash-consed. The *read* of the
> forest must keep **nothing** — O(1) state, streaming, holding only the current step.

These are opposite requirements, and conflating them was the bug under all three materializations. "We
retain all intermediates" is true and load-bearing — it is why the forest *is* an SPPF, why sharing
and grading work, why nothing is ever a digest. But it describes the *stored structure*. It says
nothing about how you *traverse* that structure, and the naive inference "since everything is retained,
the readout may hold it all" is exactly backwards. The retained structure is enormous *on purpose*; the
traversal of it must be frugal *on purpose*. A 50 GiB SPPF is tractable precisely because those two are
separated: it is retained in the store and emitted by a streaming walk.

This is the EEA discipline restated. EEA retains every division step (the chain persists) *and*
back-substitution streams over that chain (it holds one step at a time). Retention and streaming are
not in tension; they are the two halves of the same algorithm. The forest is the retained chain; the
readout is the streaming walk.

---

## 6. Why this generalizes (it is not about grammars)

`stream_rhs` reads a *grammar* out of a *parse forest*. But nothing in the argument is about grammars.
The same shape is every readout in the substrate:

- **`emit_octave` / `project_cuda` / `project_unified`** are all the same backward walk over a retained
  structure, emitting a target carrier as they go. They are Bézout reads with different `step`
  interpretations — "different reads of the same kept trace."
- The **verification gate's "realizes"**, **CrossMix's cross-term**, **`resolve(·,domain)`**, and the
  **lspace→exp witness fold** are all the forward direction — register an obligation, discharge it by
  composing its dependencies.

So the practical rule this yields, for any readout over a large interned structure:

> Do not build an intermediate (a dict, a fully-materialized `Trace`, an accumulated fold result).
> Drive the single-step primitive (`wedge`) in a loop and `yield`. The structure you are reading is
> already retained in the forest; your job is to walk it, not to copy it.

And the report that rides with this to the core: **`trace()` and `trace_fold()` in canonical
`jea_pyalg` are eager.** They are fine at current scales but cannot stream; a lazy/generator `trace`
(yield one `wedge` step at a time) would make streaming the default and let every `trace_fold` consumer
inherit O(1) state. That is `Σ-TRACE-LAZY`, and it is the one core change this whole arc actually
motivates — offered as a report, not a unilateral edit, because `jea_pyalg` is shared ground.

---

## 7. One-paragraph summary

Earley recognition is EEA's forward division descent, run as an intern-to-fixpoint; the chart is the
retained chain; completion is back-substitution's compose step. The grammar readout is EEA's
back-substitution: the Bézout coefficients you collect along the retained chain *are* the production
right-hand sides, and you emit them by walking the chain and yielding — `stream_rhs`, a `wedge`-loop,
no dict, no `trace`, no `trace_fold`. This streams because back-substitution always could: retention
lives in the forest, frugality lives in the walk, and a 50 GiB SPPF emits to ABNF in constant memory
as a direct consequence. The docstring typos the audit caught were the visible edge of this rewrite;
this is the rewrite.
