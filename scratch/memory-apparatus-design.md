# The memory analysis-and-reconstruction apparatus — clean-room design document

**Scope.** Everything needed to reimplement the apparatus living in
`~/.claude/projects/-home-mikemol-github-substrate/memory/` — 15 executable modules plus
one external dependency (`scratch/eliza`) — and get equivalent behaviour.

**Provenance discipline.** Every claim below is tagged where it matters:
· **[code]** read out of the implementation · **[prose]** taken from a docstring or comment
and *not* independently confirmed · **[divergence]** where prose and code disagree, code
wins and the disagreement is stated · **[gap]** where a constant's or design choice's
derivation is not recorded anywhere I could find. Section 8 collects the tags.

⚑ **This study was read-only.** No module was executed that writes. The behavioural claims
are derived from source, from on-disk artifacts, and from one already-verified incident
memory in the corpus itself (`memory-pipeline-gate-is-discarded.md`, dated 2026-08-19,
which hand-confirmed each of its load-bearing claims against live code).

---

## 0. What the thing is, in one paragraph

A corpus of ~250 hand-written markdown "memory" files accumulates in a flat directory. The
apparatus derives, mechanically, a navigable concept index over that corpus and writes it to
`MEMORY.md`, which is loaded into every Claude session. The derivation is *not* embedding
similarity and *not* an LLM summarisation. It is: tokenise every memory body into a content-word
sequence → concatenate all of them into one stream → run **Sequitur** grammar induction over
that stream → the induced rules are recurring phrases → phrases with ≥2 member memories become
**concept clusters** → each cluster is re-grammared over just its members and the resulting rules
are **stratified by how many members share them** (the "graded curve over sharing-breadth") →
that stratification, rendered, is a **synthetic apex memory** in `synth/<slug>.md` → `MEMORY.md`
is a list of links to those apexes. A gate (`synth_gate.py`) checks that no word in an apex's
rendered text lacks ≥2-member support in the corpus.

The design commitment underneath all of it: **the index must be derived, never authored.** A
concept exists because a phrase recurs, not because someone named it.

---

## 1. THE MATH

### 1.1 Sequitur — the grammar induction core

**[code]** The implementation is `eliza/sequitur.py` in `~/github/substrate/scratch/eliza/`,
imported by every analysis module. It is Nevill-Manning & Witten (1997) with **one deliberate
deviation that changes the output semantics** (§1.1.4).

#### 1.1.1 Data structures

- A **grammar** is `{rule_id: Rule}`, with rule 0 as the root (the start rule / "top rule").
- A **Rule** body is a *circular doubly-linked list* of `Node`s anchored by a sentinel
  `guard` node (`guard.next` … `guard.prev` is the body; `is_empty()` iff `guard.next is guard`).
  Each Rule carries a `uses` refcount. Rule 0 is initialised with `uses = 1` (the notional
  entry-point reference).
- A **Node** holds `sym` (a terminal, or an `NT`), `rule_id` (which rule's body it lives in),
  `prev`/`next`, and `is_guard`. A fresh node is self-looped (`prev = next = self`), which
  doubles as the detached-node sentinel.
- **`NT(rule_id, residue="e")`** is a frozen dataclass: a nonterminal reference. `residue` is
  a V₄ tag, only meaningful under the optional canonicalisation mode (§1.1.5) — the memory
  apparatus never enables it, so `residue == "e"` throughout and `NT` behaves as a plain
  rule reference.
- **`digrams: {(sym1, sym2) → Node}`** — the digram index. The value is the *first node* of the
  registered occurrence, so the occurrence is `(node, node.next)`.
- **`back_refs: {rule_id → set[Node]}`** — every node whose `sym` is `NT(rule_id)`. Only used by
  the (disabled) utility enforcement.
- **`_queue: deque[Node]`** — the work queue of nodes whose trailing digram may now violate
  uniqueness. This is what makes updates local instead of full rescans.

#### 1.1.2 The two invariants

Textbook Sequitur maintains:

1. **Digram uniqueness** — no `(sym1, sym2)` pair occurs twice anywhere in the rule set. A second
   occurrence triggers rule formation.
2. **Rule utility** — every non-root rule is referenced ≥2 times. A rule that drops to one
   reference is *inlined* into its single caller and deleted.

**[code]** This implementation maintains **(1) only.** See §1.1.4.

#### 1.1.3 The main loop

`observe(terminal)`:

1. Create `Node(sym=terminal, rule_id=0)` and splice it before rule 0's guard (append to root).
2. If the preceding node is not the guard, enqueue it — its trailing digram is new.
3. `_drain()`.

`_drain()` pops nodes until the queue is empty, skipping any node that has since been detached
(`node.next is node`), and calls `_handle_digram(first)` on each.

`_handle_digram(first)` — the whole algorithm:

```
d = (first.sym, first.next.sym)          # None if at a boundary → return
registered = digrams.get(d)
if registered is None:  digrams[d] = first;  return          # first sighting
if registered is first: return                                # already ours
if registered.next is first or first.next is registered:
        return                            # OVERLAPPING occurrence — refuse
                                          # (this is what stops "aaa" looping)
target_rid = find_exact_rule_for(d)      # a non-root rule whose body IS exactly this digram
if target_rid is None: target_rid = create_rule(d)
if first.rule_id      != target_rid: replace_pair_with_nt(first,      target_rid)
if registered.rule_id != target_rid: replace_pair_with_nt(registered, target_rid)
```

The `first.rule_id == target_rid` guard is the "don't replace a rule's body with a reference to
itself" case, which arises when the just-created rule's own two nodes are the registered
occurrence.

`_replace_pair_with_nt(first, rid)`:
- unregister the digram starting at `first.prev` (it is about to change), the `(first, second)`
  digram itself, and the digram starting at `second` (ditto);
- unlink both nodes (decrementing `uses` and `back_refs` for any NT among them);
- insert a fresh `NT(rid)` node in their place (which increments `rules[rid].uses` and records a
  back-ref);
- register **and enqueue** the two new boundary digrams — `(nt.prev, nt)` and `(nt, nt.next)`.
  Enqueueing is what makes the fix cascade: replacing a pair can create a *new* duplicate digram
  at either seam, and that seam gets re-examined on the next drain iteration.

`_create_rule(digram)` mints `rule_id = _next_id++`, builds a two-node body, and — critically —
sets `digrams[digram] = n1`, so the new rule's own body becomes the canonical registered
occurrence of that digram. Every subsequent sighting resolves against it.

**Complexity.** O(1) amortised per observed terminal *except* for `_find_exact_rule_for`, which
**[code]** linearly scans every rule looking for a length-2 body matching the digram — and
`Rule.length()` itself walks the list. So the real per-collision cost is O(#rules), and the
build is superlinear in practice. This is consistent with the observed ~78 s corpus grammar
build that `synth_scale.py` goes to lengths to cache (§3.3). A clean-room implementation can
replace this scan with a `{digram → rule_id}` side-map for a large speedup with identical
output; nothing depends on the scan order because at most one rule can have that exact body.

#### 1.1.4 ⚑ THE DEVIATION: rule utility is DISABLED

**[code]** In `_handle_digram`, the utility call is present but commented out, with a comment
naming the reason:

```
# Rule-utility check REMOVED per substrate-honest discipline:
# _maybe_inline_underused erases structural observations from
# the grammar. Every rule created here is a catalogued fact;
# don't garbage-collect.
# self._maybe_inline_underused()
```

`_maybe_inline_underused` and `_inline_or_drop` remain in the file, fully implemented and
**dead**. `_inline_or_drop` also consults `self.protected_rule_ids` (via `getattr` with a
`frozenset()` default) — an attribute never set anywhere in this module.

**Why a reimplementer must not "fix" this.** With utility enforcement on, a rule used once is
inlined and disappears. That is correct for *compression* — the grammar's job in Sequitur's
original setting. Here the grammar is not a compressor; it is a **catalogue of observed repeated
structure**, and the downstream consumers query rules by *how many member memories contain the
rule's expansion*. A rule referenced once in the concatenated stream may still be an expansion
that textually occurs in several memories, and more importantly, the whole "never discard
residue" discipline of this corpus says a once-seen structure is a fact to keep, not garbage.
Turning utility back on would silently shrink every apex's `pairwise` band — the band that
carries the deepest, most specific findings.

**Consequences a reimplementer must accept:** the rule set is larger than textbook Sequitur's,
grammar size grows faster, and the "grammar is a minimal lossless representation" property is
lost. It remains lossless (nothing is deleted), just not minimal.

#### 1.1.5 The V₄ canonicalisation mode (present, unused here)

**[code]** `Sequitur(v4_canonicalize=True)` indexes digrams by the lex-minimum of their V₄
(Klein four-group) orbit under transforms `e` (identity), `α` (swap the two symbols), `β`
(invert each symbol), `γ` (swap and invert). `_invert_sym_v4` maps a terminal `c` to
`chr(ord(c) ^ 3)` — i.e. it assumes terminals are the four codepoints 0–3 — and conjugates an
`NT`'s residue by β through the `_V4_COMPOSE` table. Because each transform is its own inverse
in V₄, the residue recovering the original from the canonical form equals the transform that
produced the canonical form.

**Every memory-apparatus call site constructs `Sequitur()` with no arguments**, so this mode is
off. It is documented here only so a reimplementer knows it can be omitted entirely without
affecting the memory apparatus. (`_invert_sym_v4`'s `ord(sym) ^ 3` would in fact crash or
corrupt on the word-tokens this apparatus feeds it — another reason the mode is not reachable
here.)

#### 1.1.6 Expansion — and why it is iterative

**[code]** Two near-identical `expand(seq, rules, max_out)` helpers exist, in
`pcr_corpus_grammar.py` (`max_out=40`) and `grammar_phrase_lattice.py` (`max_out=24`); the
latter is the one all synth modules import as `G.expand`.

```
out = []; stack = [(s, ()) for s in reversed(seq)]
while stack and len(out) < max_out:
    s, seen = stack.pop()
    if isinstance(s, NT):
        if s.rule_id in seen:  out.append(f"R{s.rule_id}")     # cycle guard
        else: push each child of rules[s.rule_id] in reverse, with seen+(rule_id,)
    else: out.append(s)
return out
```

Three load-bearing details:
- **Iterative, not recursive.** The docstring says the recursive walk *overflows the Python stack
  on the saturated grammar* — with utility disabled the rule nesting gets deep enough to blow
  the default recursion limit. **[prose, plausible and consistent with §1.1.4]**
- **`max_out` truncates.** An expansion longer than the cap is silently cut off. This means a
  rule's "expansion" as seen downstream may be a *prefix*. Since downstream filters demand
  `2 ≤ len(e) ≤ 14` (apex) or `≥ 3` (lattice), and the cap is 24, truncation only affects rules
  that would have been rejected as too long anyway — **but the cut is silent**, so a
  reimplementer should keep the cap above every downstream length filter.
- **The `seen` cycle guard emits the literal string `"R<id>"`** into the token sequence when a
  rule recurs within its own expansion. That token then flows into phrase text. Sequitur cannot
  produce genuinely cyclic rules, so this branch should be unreachable; it is defensive.

### 1.2 The graded curve over sharing-breadth — the conceptual heart

This is the part the user said they understand least, so it is developed from the ground up
with a worked example.

#### 1.2.1 What is being graded, precisely

**[code]** `synth_apex.build_apex(phrase, ctx)`. Given a cluster (a concept phrase and its member
memories):

1. Build a **fresh Sequitur grammar over only the member memories' token streams**, separated by
   a `∎` boundary token. Note this is a *second, cluster-local* grammar — not a slice of the
   corpus grammar. The corpus-wide grammar found *which* memories cluster; this one finds *what
   structure they share*.
2. For each non-root rule `rid`, compute its full expansion `e` (with `∎` stripped).
3. Keep it only if **all** of: `2 ≤ len(e) ≤ 14`; at least one token of `e` is in the
   corpus `gauge` vocabulary (§1.4); not *every* token of `e` is in the `DROP` set.
4. Compute its **member set** `mset = {j : the literal string " "+join(e)+" " occurs in member
   j's text}` — a *substring* test against the space-padded token join, not a grammar-derived
   membership.
5. Keep it only if `|mset| ≥ 2`. **This is the ≥2-witness rule at its origin** (§1.5).
6. Compute its **depth** `d = _rdepth(rid) = 1 + max(depth of NT children, default 0)` — i.e. how
   many levels of rule nesting the rule sits atop. A rule whose body is two terminals has depth 1.

Each surviving rule is therefore a triple **(phrase `e`, breadth `|mset|`, depth `d`)**.

**The grading is over breadth.** Let `M = |members|` and `hi = max(3, M // 2)`. Then:

| band | condition on breadth `ms = \|mset\|` | label |
|---|---|---|
| `universal` | `ms ≥ hi` | shared by ≥hi/M — universal skeleton (shallow) |
| `broad` | `3 ≤ ms < hi` | shared by 3–(hi−1) — broad motifs |
| `pairwise` | `ms == 2` | shared by exactly 2 — deep pairwise co-quotes (the residue) |

Bands are capped at 8 / 12 / 6 rows respectively. **[gap]** These three caps, and the `hi`
formula's `max(3, M//2)`, have no recorded derivation. They read as render-budget tuning.

#### 1.2.2 Why a curve and not a threshold

The empirical regularity the design exploits is an **inverse relation between breadth and depth**:
a phrase shared by most members of a cluster is almost always a short, shallow, generic
skeleton, and a phrase shared by exactly two members is almost always a long, deeply-nested,
highly specific co-quotation. A single threshold forces a choice between them:

- Threshold high (only broadly-shared phrases) → you get the skeleton and lose every specific
  finding. The apex reads as vacuous generality.
- Threshold low (any ≥2-shared phrase) → the specific findings drown in hundreds of shallow
  fragments, and the render blows its budget.

The curve keeps **both ends and the middle, labelled by which end they came from**, so a reader
descends it: the `universal` band tells you what the concept *is*, the `pairwise` band tells you
what two specific memories actually *said*. This is the same "never discard residue / find the
common structure without picking a side" discipline the corpus applies everywhere else, applied
to the index itself. It is called a *curve* because it is parameterised by breadth and
**truncatable at any point** — you can read the top band alone and get a coherent (if shallow)
answer, or read down for depth.

The sort orders encode the same asymmetry **[code]**:
- `universal` and `broad` sort by `(ms, d, len(e))` descending — **breadth first**. In a
  broadly-shared band, the more members the better.
- `pairwise` sorts by `(-d, -len(e))` — **depth first, breadth is constant at 2**. Once breadth
  carries no information, depth becomes the ranking signal.

And only the `pairwise` band renders its member edges (`[[name]] [[name]]`) and depth (`·d5·`).
Broad bands render only the count (`·8·`). Rationale **[inferred from code, not stated]**: two
names is a citable edge; nine names is a list nobody reads.

#### 1.2.3 Maximal-phrase deduplication

**[code]** Sequitur's nesting means a long rule and its sub-rules all survive the filters, so
`«a b c d»`, `«a b c»`, `«b c d»` would all appear. Before banding:

```
rinfo.sort(key = -len(e))                       # longest first
maximal = []
for (e, mset, d) in rinfo:
    if any( " "+join(e)+" " is a substring of " "+join(k_e)+" "  AND  mset ⊆ k_mset
            for k in maximal ):
        continue                                # subsumed
    maximal.append((e, mset, d))
```

A phrase is dropped only if it is **both** a contiguous sub-phrase of an already-kept longer one
**and** its member set is a subset of that one's. The second conjunct is what keeps a short
phrase that is *more widely shared* than the long one containing it — which is exactly the
universal-skeleton case. Dropping on substring alone would delete the top band.

This is O(n²) in surviving rules with a substring test inside; fine at cluster scale.

#### 1.2.4 Worked example

Take the on-disk apex `synth/suc-suc-suc.md`, cluster phrase `«suc suc suc»`, 4 members.
`M = 4`, so `hi = max(3, 4//2) = max(3, 2) = **3**`.

Rules surviving with their breadth:

| expansion | breadth | band |
|---|---|---|
| `suc suc suc` | 4 | `4 ≥ 3` → **universal** |
| `substrate foundation` | 3 | `3 ≥ 3` → **universal** |
| `foundation fin` | 3 | **universal** |
| `substrate foundation fin` | 2 | **pairwise** |
| `suc suc zero` | 2 | **pairwise** |
| `all consumers` | 2 | **pairwise** |

Note `«substrate foundation fin»` (breadth 2) survived dedup against `«substrate foundation»`
(breadth 3) because the *longer* phrase is processed first and the shorter one's member set is
**not** a subset of the longer's — it is a superset. Both are kept, in different bands. This is
the dedup rule doing exactly its intended job, visible in a live artifact.

Observe also the inverse relation in miniature: the breadth-4 phrase is 3 tokens at depth ~1;
the pairwise entries carry explicit depths `·d2·`, `·d1·`. In the larger `synth/reuse-search.md`
(19 members, `hi = 9`) the pairwise band reaches `·d5·` on a six-token phrase
(`«free-monoid freeup monoid-class gen word gen»`) while the universal band holds
`feedback reuse search ·18·` — three tokens. The relation is visible across both live apexes.

#### 1.2.5 ⚑ A REAL BUG IN THE PAIRWISE BAND'S WITNESS NAMES

**[divergence — code vs. artifact, discovered in this study]**

`build_apex` computes member sets in **member-local index space**:

```
memtext = [text[i] for i in members]                     # 0 .. len(members)-1
mset = frozenset(j for j in range(len(memtext)) if ...)  # j is member-local
```

but renders them in **global corpus index space**:

```
" ".join(f"[[{names[j]}]]" for j in sorted(mset))        # names is the GLOBAL list
```

`names[j]` for a member-local `j` names *the j-th memory in the whole corpus*, not the j-th
member of the cluster. The two spaces coincide only if the cluster's members happen to be the
first `M` files in sorted order — which they never are.

**Confirmed against the live artifact.** `synth/suc-suc-suc.md` declares its witnesses as
`project_cpos_migration_arc, project_fin_literals_arc, project_open_threads,
project_stdlib_audit_progress` — but its pairwise band cites `[[adjunction-is-the-wedge-residue-counit]]`,
`[[project_aa_arc_composed_reference]]`, `[[project_bb_arc_multiscale_rotation]]`,
`[[project_cc_arc_coxeter_bitshift]]` — **none of which are witnesses of that cluster.** They
are simply corpus files at low sorted positions.

So: the **`## witnesses` section is correct** (it renders `names[i] for i in members`, global
space throughout), the **band counts are correct**, and the **pairwise `[[links]]` are wrong**.

A clean-room implementation must render `names[members[j]]`, not `names[j]`. A reimplementer
who copies the visible behaviour would faithfully reproduce a defect. Note also that
`synth_gate.py` cannot catch this: it strips `[[...]]` from the render before checking
(§1.5), precisely because links are treated as pointers rather than claims.

### 1.3 Clustering — `cluster_phrases` (and the LSA module that is NOT it)

#### 1.3.1 ⚑ There are two clusterers and only one is live

**[divergence]** `cluster_memories.py` is a **standalone LSA experiment** and is **not part of
the live pipeline.** Nothing imports it. It writes `MEMORY.candidate.md`, never `MEMORY.md`. Its
own docstring records it as v4 of a refinement log (v1 max-df → v2 min-df → v3 IDF connected
components → v4 SVD). For completeness, its method **[code]**:

- Extract only the frontmatter `description` (not the body).
- Terms = `{ALLCAPS words ≥3 chars, lowercased}` ∪ `{lowercase words ≥5 chars} \ STOP`.
- Vocabulary = terms with `3 ≤ df ≤ 60`.
- Matrix `M[i,j] = log(N / df[w])` if memory *i* contains term *j*, else 0; rows L2-normalised.
- `U, sv, Vt = svd(M)`. Take modes **1..16** — **mode 0 is dropped** as "the trivial
  constant/centroid all-memories direction", following an "eliza convention" of starting at the
  Fiedler vector.
- Term→axis assignment is *gated*: a term joins axis `k` only if `|Vk[k,j]| ≥ 1.4 × second
  largest`; otherwise it is a **bridge** (cross-cutting, e.g. "residue") and is kept as such
  rather than forced onto one axis.
- Memory→axis membership is *soft/dual*: a memory joins its top axis, plus its second if
  `|load₂| ≥ 0.6 × |load₁|`.

**[gap]** `K=16`, `MARGIN=1.4`, the `0.6` soft-membership band, and `3 ≤ df ≤ 60` all appear
empirical; no derivation is recorded. The `df ≤ 60` cap recurs in four modules as the
"boilerplate cutoff" and is the single most-copied magic number in the apparatus.

**The live clusterer is `grammar_phrase_lattice.cluster_phrases`.** It is not vector-space at
all — no metric, no linkage, no dendrogram, no cut. It is **grammar-induced phrase membership
plus three union-find collapses.** A reimplementer expecting hierarchical clustering will build
the wrong thing.

#### 1.3.2 `cluster_phrases(items, phrase_min=3, min_members=2, tau=0.5)` — [code]

Input: `[(name, tokens)]`. Output: `[(phrase_string, frozenset(member_names))]`, sorted by
`(-|members|, phrase)`.

**Step 0 — raw phrase→member map.** Build one Sequitur grammar over all items' token streams
(`∎`-separated). For each non-root rule: expand; require `len(p) ≥ phrase_min` (3); compute
members by the space-padded substring test; require `|members| ≥ min_members` (2).

**Collapse 1 — prefix strip and merge.**
`PREFIX = {feedback, project, reference, discipline}` — the filename-namespace prefixes that
leak into token streams via `[[links]]` and titles. Strip any leading run of them, *unless*
doing so would leave fewer than 2 tokens. Phrases identical after stripping merge, **unioning**
their member sets. So `«feedback reuse search»` and `«project reuse search»` become one cluster
carrying both memberships.

**Collapse 2 — maximality within an identical member set.**
Group phrases by their exact member frozenset. Within each group, sort by length descending and
keep a phrase only if it is not a contiguous subsequence (`_subseq`) of an already-kept one.
Rationale: two phrases with the *same* members are two readings of one fact; keep the longest.
Different member sets are left alone — same principle as §1.2.3.

**Collapse 3 — kernel-merge by union-find.** For every pair of surviving units `(i, j)`, with
`a`, `b` their member sets and `tok[i]`, `tok[j]` their token sets, compute the **Jaccard**

```
jac = |a ∩ b| / |a ∪ b|
```

and merge (`union(i, j)`) iff

```
jac ≥ 0.8                                        # near-identical membership: the same cluster
                                                 # even with disjoint vocabulary ("the arc-template case")
     OR
( |tok[i] ∩ tok[j]| ≥ 2  AND  jac ≥ tau )        # a shared lexical KERNEL plus decent overlap
```

The two disjuncts are doing different jobs and a reimplementer must keep both. The first merges
clusters that *are* the same set of memories described in two vocabularies. The second is the
guarded merge: shared vocabulary alone is not enough (that was the v3 over-merge failure the LSA
module's log records), so it requires ≥2 shared tokens **and** ≥50% membership overlap.

**Representative.** Each connected component's phrase is `max(idxs, key=(|members|, |phrase|))` —
the widest-membership unit, longest phrase as tiebreak. Members are the union over the component.

**So the "cut" is not a dendrogram cut.** There is no height parameter. The resolution knobs are
`tau = 0.5`, the `0.8` near-identity shortcut, the `≥2 shared tokens` kernel size, and
`min_members = 2`. **[gap]** None of these four has a recorded derivation.

#### 1.3.3 The recursive/stratified layer (lattice only)

`grammar_phrase_lattice` builds a *tree*: `build_tree_from` re-runs `cluster_phrases` on each
top cluster's members to get sub-concepts, to `max_depth=2`, keeping a sub-node only if it is
strictly smaller than its parent. Members no sub-concept captures stay as the node's **direct
leaves** — residue preserved at every level.

`compute_tiers` / `stratify` add **recursive stratification**: cluster the corpus; take the
concepts whose membership is ≥ the **P90** of *this stratum's* cluster-size distribution
(`pct(vals, 90)` — a data-relative cut, explicitly not a fixed top-k); emit them; then re-run the
whole thing on **only the memories those concepts did not cover**. Each tier's discard is the
next tier's corpus, to `max_tiers=6`, ending in a `singletons` list. The recursion floor
`min_recurse` is itself a percentile — the **median** head-cluster size.

**[divergence]** All of this tier machinery is live code in `grammar_phrase_lattice.main()` and
produces `index/`. But `index/` on disk is **dated 2026-06-24** and has not been regenerated
since the synth-apex swap. `main()` is currently a **hazard**, not a step (§3.5).

### 1.4 The gauge — term → dominant SVD content-mode

**[code]** `synth_apex.build_context()`. This is a *reduced* version of the LSA machinery,
retained as a **relevance filter** inside the live pipeline:

1. Corpus = `**/*.md` under the memory dir, excluding `G.SKIP`, `index/`, and `synth/`.
2. Tokens = `G.words(G.full(f))` (§2.1).
3. `df` = document frequency over token *sets*.
4. `vocab = {w : 3 ≤ df[w] ≤ 60, w ∉ GENERIC}` — the ~40-word `GENERIC` process-word filter is
   `synth_apex`'s own addition on top of `G.STOP`.
5. Same IDF matrix and L2 row normalisation as §1.3.1.
6. `Vt` from SVD; **`Vk = Vt[1:4]`** — modes 1, 2, 3. Mode 0 dropped (the centroid).
7. `gauge = {w : argmax_k |Vk[k, vocab_index(w)]|}` — each vocabulary term's dominant content mode.

**What the gauge is actually used for in the live path is narrower than it looks.** In
`build_apex` the gauge is consulted only as a **set membership test**:
- `cdf` (the cluster's within-cluster document frequency, feeding the `meet`) counts only tokens
  `w in gauge`;
- a rule is kept only if `any(w in gauge for w in e)`.

The mode *value* (0/1/2) is never read in `build_apex`. So in the apex pipeline the entire SVD
reduces to "is this term in the distinctive vocabulary" — the `3 ≤ df ≤ 60` band and the
`GENERIC` filter do the real work, and the SVD is a no-op with respect to the output.

**[divergence]** A reimplementer could replace steps 5–7 with `gauge = set(vocab)` and produce
**identical apexes** at a fraction of the cost. The mode values *are* genuinely used — but only
in the two probes (`synth_reverse_probe`, `chamber_coord_probe`), never in the live path. The
docstring calls it "the mesh-derived gauge (term → dominant SVD content-mode)", which is
accurate about what is computed and misleading about what is consumed.

**The `meet`.** `meet = {w : cdf[w] ≥ 0.4 × |members|}`, sorted by descending `cdf` — the
vocabulary shared by ≥40% of the cluster's members. It is written into the apex's frontmatter
`description` (first 8 terms) and is the conceptual ancestor of the gate's ceiling (§1.5).
**[gap]** The `0.4` has no recorded derivation.

### 1.5 The ≥2-witness rule

It exists in **two distinct places with different definitions**, and conflating them is easy.

#### 1.5.1 Witness-at-construction (`synth_apex`) — a rule is a MEMBER count

`|mset| ≥ 2`: at least two *member memories of this cluster* contain the rule's expansion as a
literal substring. Enforced by `continue`; a rule with breadth 1 is never emitted. **This is
what makes "every line witnessed by ≥2 members" true by construction**, and this part of the
advertised claim is genuinely enforced. Note the witness is *textual containment of the
expansion*, not the grammar's own derivation — a deliberate and stricter test, since the grammar
could derive a phrase that occurs in only one place.

#### 1.5.2 Witness-at-gate (`synth_gate`) — a word is a CORPUS-WIDE df count

`synth_gate.py` asks a different question: **is every content word in the apex's rendered prose
supported by ≥2 of the apex's witnesses?**

```
witness_names = [[name]] links in the '## witnesses' section
wdf = Counter();  for each name: wdf.update(set(G.words(G.full(PATHS[name]))))
ceiling = { w : wdf[w] >= 2 }
```

**[code]** `PATHS` is built by a recursive glob, so a `[[name]]` resolves anywhere under
`memory/` including `archive/` and `discipline/`. A name that resolves to nothing is **silently
skipped** — `PATHS.get(nm)` returning `None` contributes nothing to `wdf`, which *lowers* the
ceiling and makes the gate stricter, so this fails safe (though it fails **silently**).

The **render** under test is the `## apex` section's `-`/`>` lines only, with `[[links]]`, `·N·`,
`·dN·` and `_(annotations)_` stripped — links are pointers, not claims.

A render word **passes** iff any of:
1. it is in the ~70-word `ALLOW` connective/meta list; or
2. `stem_match(w, ceiling)` — for `w` itself and each hyphen-part of `w`: exact membership, **or**
   a `ceiling` term `m` where one is a prefix of the other and `min(len(m), len(part)) ≥ 4`,
   **or** `len(commonprefix(part, m)) ≥ 5`. This is what makes `keeping ↔ keep`,
   `eea-trace ↔ eea + trace`, `instantiates ↔ instances` all pass; or
3. it appears in the file's `metadata.allow` — **[divergence]** the docstring promises this
   third route ("JUSTIFIED residue the 40%-meet missed"), and **the code never reads
   `metadata.allow`.** `gate()` parses only the `## witnesses` and `## apex` sections. A
   clean-room implementer following the docstring would build an escape hatch that does not
   exist. The `ALLOW` constant is a module-level global, not per-file.

Anything else is an **EXCEEDER**. `gate()` prints one line per file and returns a bool;
the module evaluates **all** paths before exiting (explicitly not short-circuiting at the first
FAIL) and `sys.exit(0 if all(results) else 1)`.

**Why it exists — [prose, and specific enough to be credible]:** the docstring names the
incident. When apexes were hand- or LLM-rendered, words like `lossless / retraction / reify`
— **outside knowledge, not present in any witness** — got written into an apex. The gate turns
"the render is bounded by the meet" from a stated intention into a mechanical refusal.

**Why the ceiling is ≥2 rather than ≥1 — [prose]:** "hub-robust: a single mega-file like
open_threads saying it doesn't license the claim; two members do." `project_open_threads.md` is
184 KB and would otherwise single-handedly license nearly any vocabulary.

#### 1.5.3 ⚑ AND THE GATE HAS NEVER BLOCKED ANYTHING

See §5.1. The gate is correct; its verdict is structurally unreachable.

### 1.6 `pcr_corpus_grammar.py` — and what a "phrase lattice" is here

**[divergence — the module does not do what its own name and first paragraph say.]**

The docstring opens: *"feed the WHOLE memory corpus through ONE eliza Engine REPEATEDLY
(PCR-style cyclic amplification) until the per-pass surprise stops dropping … The amplified
Sequitur rules ARE the corpus's recurring motifs."* An inline comment **eight lines into
`main()` retracts this**:

```
# (Sequitur explodes on identical-repetition — wrong tool for PCR; the Markov
#  operator is the right one.)
```

**[code]** What it actually runs: a `TrigramPredictor` (imported alongside `Sequitur`, which is
imported and **never instantiated**).

The algorithm:
1. Stream = concatenation of every memory's **`description` only** (`claim(p)`, not the body),
   tokenised, `∎`-separated.
2. `pred = TrigramPredictor(vocab_size = distinct + 64)`.
3. For up to 25 cycles, replay the *entire* stream, accumulating `surprise_bits(tok)` before
   `update(tok)`; `ps = total / n` is the pass's mean surprise.
4. **Convergence:** stop when `(prev_surp - ps) / prev_surp < 0.01` — a *relative* 1% drop.
   The comment gives the reason: "the large-vocab Laplace floor makes the absolute surprise
   asymptote slowly, never 0", so an absolute-delta test would never fire.
5. Read out **transition chains** `(c1, c2) → c3` from `pred.counts`, skipping any involving `∎`.

**The one genuinely subtle formula**, and it is flagged in the source:

```
per_pass = k / cycles          # NOT k
```

with the comment *"PCR multiplies every count by the cycle#, so ABSOLUTE count is meaningless —
the genuine cross-memory signal is PER-PASS recurrence (count/cycles ≥ 2)."* Cycling the same
stream N times multiplies every count by exactly N, so a raw count of 20 after 10 cycles means a
bigram seen **twice** in the corpus. The threshold is `per_pass ≥ 2` — occurring at least twice
*within one pass* — which is the cross-memory recurrence test. Chains are reported as
`(per_pass, k/total_for_context, c1, c2, c3)`, sorted descending; conditional probability
`p = k / Σ_c3 counts[(c1,c2)][c3]` is unaffected by the multiplication.

**[gap]** The 25-cycle cap, the 1% relative-convergence threshold, and the `per_pass ≥ 2` floor
have no recorded derivation.

**Status: this module is a diagnostic, not a pipeline stage.** Nothing imports it; it writes no
files; it prints a table.

**So what is the "phrase lattice"?** The name comes from `grammar_phrase_lattice.py`, and it is
**not a formal lattice object**. It is the partially-ordered structure that falls out of
Sequitur's rule hierarchy plus membership:

- **Elements**: (phrase, member-set) pairs derived from grammar rules.
- **One order** is *phrase containment* — `«a b»` ≤ `«a b c»` when the first is a contiguous
  subsequence of the second (the `_subseq` relation).
- **The dual order** is *member-set inclusion* — a longer phrase has a smaller or equal member
  set (a superstring cannot occur in more places than its substring).
- The **collapses of §1.3.2** are quotients of this structure: collapse 2 quotients by
  "same member set, keep the containment-maximal", collapse 3 quotients by a
  Jaccard-plus-kernel tolerance relation closed under union-find.
- The **grading of §1.2** reads the same structure along the member-count axis instead of
  quotienting it.

The relation to the grammar is direct: Sequitur's nesting **is** the containment order,
materialised — a rule literally contains its sub-rules, and `_rdepth` measures position in it.
The apparatus never builds a lattice data structure; it exploits the order the grammar hands it.

### 1.7 Scoring / ranking functions, collected

| where | formula | purpose |
|---|---|---|
| IDF weight | `M[i,j] = log(N / df[w])`, rows L2-normalised | term weight; normalisation stops long memories dominating |
| gauge | `argmax_k \|Vt[1:4][k, j]\|` | term → content mode (used as set-membership only in the live path) |
| vocabulary band | `3 ≤ df[w] ≤ 60` | drop rare noise and corpus-wide boilerplate |
| meet | `cdf[w] ≥ 0.4 × \|members\|` | the cluster's shared vocabulary (apex description) |
| cluster merge | `jac = \|a∩b\| / \|a∪b\|`; merge iff `jac ≥ 0.8` or (`\|tok_i ∩ tok_j\| ≥ 2` and `jac ≥ 0.5`) | union-find kernel merge |
| band cut | `hi = max(3, M // 2)` | universal / broad / pairwise boundary |
| rule depth | `d(r) = 1 + max(d(child NTs) ∪ {0})` | pairwise-band ranking |
| stratum cut | `pct(sizes, 90)` — the P90 of *this* stratum | data-relative concept admission (lattice) |
| recursion floor | median head-cluster size | when to recurse (lattice) |
| relevance | `pp_rank(n, all) = 100 · \|{v ≤ n}\| / \|all\|` | the `·pPP` percentile in the lattice root |
| gate stem match | exact ∨ (prefix, `min(len) ≥ 4`) ∨ `len(commonprefix) ≥ 5` | morphological tolerance |
| PCR recurrence | `per_pass = k / cycles ≥ 2` | cross-memory transition signal |
| PCR convergence | `(prev − cur) / prev < 0.01` | relative, because of the Laplace floor |
| LSA axis gate | `\|top\| ≥ 1.4 × \|second\|` else "bridge" | term→axis assignment (dead module) |
| LSA soft member | `\|load₂\| ≥ 0.6 × \|load₁\|` | dual-mode membership (dead module) |
| warrants apex | in-degree over resolved `from` edges; top 24, `indeg ≥ 2` | core-idea selection (dead module) |

**There is no cosine similarity, no embedding, no learned model anywhere in the apparatus.**

---

## 2. THE DATA MODEL

### 2.1 A memory file

`memory/<slug>.md`, or one level down in `memory/archive/` or `memory/discipline/`. The
recursive `**/*.md` glob picks up all three.

```markdown
---
name: reuse-search-structural-questions
description: "The reuse-search trigger fires on \"what IS X\" definitional questions, not just
  build-plans — search the tower/apex before posing an encoding or fork"
metadata:
  node_type: memory
  type: feedback
  originSessionId: d35bc15a-16b8-42c5-aad1-20966c9a9f8e
  modified: 2026-08-19T01:47:05.921Z
---

Body prose. Cites other memories as [[feedback_other_thing]], [[some-slug]].
```

**Fields, and who reads them:**

| field | consumed by | how |
|---|---|---|
| `name` | nothing | the filename stem is authoritative everywhere |
| `description` | `G.full` (prepended to the body), `cluster_memories`/`pcr_corpus_grammar`/`chamber_coord_probe` (as the *entire* input), `build_warrants` (as the claim) | regex `^description:\s*(.+)$`, `.strip('"')` |
| `metadata.type` | `build_warrants` only, as the bib `section` | regex `^\s*type:\s*([a-z]+)` |
| `metadata.node_type`, `originSessionId`, `modified` | nothing in this apparatus | harness-written |
| body `[[links]]` | `build_warrants` (`from` edges), `synth_gate` (witness resolution) | `\[\[([a-z0-9_/-]+)\]\]` |

⚑ **The frontmatter parse is a fragile regex, not YAML.** `re.match(r'^---\n(.*?)\n---\n(.*)$',
s, re.S)` — CRLF, a leading blank line, or a `---` inside the body all break it.
`grammar_phrase_lattice.full()` **fails open** (returns the whole file including the raw
frontmatter) when the match fails; `build_warrants.parse()` **fails closed** (returns `None`, the
file is dropped from the bib entirely). Same input, opposite behaviour, in one apparatus.
**[gap]** No record of this being a decision rather than an accident.

**Tokenisation.** Two tokenisers exist and a reimplementer must not merge them:

- **`G.words(t)`** (`grammar_phrase_lattice`, used by the whole live synth path):
  `[w for w in re.findall(r'[a-z][a-z-]{2,}', t.lower()) if w not in STOP]`.
  **Order-preserving, duplicates kept** — a sequence, because grammar induction needs order.
  Requires a leading letter and ≥3 chars total; **hyphens are internal-legal**, so
  `eea-trace` is one token. STOP is ~75 words.
- **`terms(t)`** (`cluster_memories`, `chamber_coord_probe`): a **set**, `{ALLCAPS ≥3}` ∪
  `{lowercase ≥5} \ STOP`. Longer minimum length, no hyphens, unordered.

**`G.full(p)`** returns `description + "\n" + body` with `re.sub(r'\S*/\S*', ' ', …)` applied —
stripping any whitespace-delimited run containing a slash, i.e. paths and URLs, which would
otherwise flood the grammar with unique tokens.

### 2.2 An apex file

`synth/<slug>.md` where `slug = re.sub(r'[^a-z0-9]+', '-', phrase.lower()).strip('-')`.

```markdown
---
name: synth_reuse_search
description: "SYNTHETIC apex of the «reuse search» cluster (19 memories): search, feasibility, …"
metadata:
  type: synthetic
  source: synth_apex.py — graded S(g) over sharing-breadth of the Sequitur grammar
  witnesses: 19
---

_SYNTHETIC apex — derived/regenerable, **proposal-not-truth**. …_

## apex — graded by sharing-breadth (S(g): truncatable; …)
### universal · shared by ≥9/19 — universal skeleton (shallow)
- feedback reuse search ·18·
### broad · shared by 3–8 — broad motifs
- witness tower ·8·
### pairwise · shared by exactly 2 — deep pairwise co-quotes (the residue)
- «free-monoid freeup monoid-class gen word gen» ·d5· [[name_a]] [[name_b]]

## witnesses
  [[name]], [[name]], …
```

Load-bearing conventions: `type: synthetic` marks it derived; the description's tail is the
`meet`'s top 8 terms; band rows carry `·breadth·` (broad/universal) or `·d<depth>· [[links]]`
(pairwise); `## apex` and `## witnesses` are the two section anchors `synth_gate` splits on —
**renaming either heading silently disables the gate** (`'## apex' in s` is false → empty
render → zero exceeders → PASS).

⚑ **Apexes are excluded from the corpus** (`synth/` filtered from every glob). Without this the
mesh would eat its own output and each regeneration would amplify the previous one's vocabulary.

### 2.3 `index/`

**[code + on-disk evidence]** Output of `grammar_phrase_lattice.main()`: one `<slug>.md` per
tier-1 concept node (sub-concepts with `../memory.md` links, plus direct members), and
`_deeper.md` (tiers 2+ and the singleton residue). The directory is `shutil.rmtree`d and
recreated on every run.

**It is dead.** Every file is dated 2026-06-24 — the synth-apex swap. The live `MEMORY.md`
links `synth/`, never `index/`. `index/` is a preserved artifact of the previous root
generation, and `main()` is now a hazard (§5.4).

### 2.4 `warrants.bib`

**[code]** Output of `build_warrants.py`. One `@misc` per memory:

```bibtex
@misc{feedback_never_discard_residue,
  section = {feedback},              % from metadata.type
  from    = {key, key, …},           % [[links]], normalised, self-link removed
  claim   = {the description},       % { } → ( )
  check   = {file:relative/path.md}
}
```

Key normalisation: `basename`, `-` → `_`. Link resolution is *forgiving*: an unresolvable link
`l` is retried as any key ending `_l` or `/l`, accepted only if **exactly one** candidate matches
— "a link names a core imprecisely (missing prefix)". Ambiguous or unmatched links are counted as
`junk` and reported.

The module then computes in-degree over resolved edges, takes the top `APEXN=24` with
`indeg ≥ 2` as **cores**, assigns each non-core memory a `parent` (its highest-in-degree
citation), folds transitively to an apex with a `seen` cycle guard, and emits
`MEMORY.candidate.md` — cores grouped by `type` in the order `user, feedback, project,
reference, misc`, with folded incidents and an `ungrounded` residue list.

**Verified state — [code + `bibstruct --entries`]:** the live `warrants.bib` holds **196 of 196
entries**, every one carrying exactly `check, claim, from, section`. It is dated **2026-06-23**
and is therefore **stale** — every memory added since (`census-green-is-a-fact-about-the-census`,
`sampled-state-cannot-see-events`, `a-go-must-carry-its-provenance`, and ~20 others) is absent.
Nothing in the live pipeline regenerates or reads it. **MEMORY.md's current preamble does not
mention it**, though `grammar_phrase_lattice`'s (dead) preamble still promises "Formal claims +
causality: `warrants.bib`".

So `warrants.bib` **contributes nothing to the live index.** It is a second, independent view of
the corpus — a citation DAG rather than a phrase lattice — frozen in June.

### 2.5 `MEMORY.md` — generated, with a hand-editable tail

**[code]** Written by `synth_wire.py`. Structure:

1. `PREAMBLE` — a hardcoded string describing the mesh.
2. `## concepts → graded synth apexes` then one `- [<phrase>](synth/<slug>.md) [<N>]` per wired
   concept, ordered by **descending member count**.
3. A blockquote caption: `> {linked} concepts wired; {dropped} template/fragment clusters filtered`.
4. `STAGING_MARKER` — an HTML comment — and below it, a hand-editable inbox preserved verbatim
   across regenerations.

**Which phrases get wired:** ranked by `len(members_of(ph, ctx))` descending; skipped if the slug
is already seen or `synth/<slug>.md` does not exist; then split by `is_concept(phrase)`:

```
if len(set(tokens)) < len(tokens):  return False   # repeated token ("sylow sylow")
if any(w in GLUE for w in tokens):  return False   # prose fragment
return True
```

`GLUE` is a ~60-word hand list. The filter is **purely lexical** — no member analysis. Rejects
are printed to stdout as `DROPPED (template/fragment)` and **their apex files stay on disk,
unlinked** (the "orphans" `synth_coverage --orphans` reports).

**Post-processing (both generators, identically):**
`re.sub(r'(?<!`)(_[^\s_`]*[^\sA-Za-z0-9_`][^\s_`]*_)(?!`)', r'`\1`', txt)` — wrap
underscore-delimited tokens containing a non-alphanumeric operator character in backticks.
Agda mixfix names (`_·_`, `_↔_`, `_⊗ˢ_`) read as markdownlint MD049 underscore-emphasis; they are
code. Deliberately conservative: it will not touch plain `_word_` emphasis (no operator char) and
will not re-wrap something already backticked.

**Staging.** Lines below the marker survive regeneration, except: lines starting (after stripping
`_>( `) with `empty` (the auto-placeholder), and lines all of whose references resolve to existing
memory files (integrated → drop from inbox). References are matched by
`\[\[?([a-z0-9_]+)\]?\]|\(\.\./([a-z0-9_]+)\.md\)`.

⚑ **[divergence, verified in this study]** The **live `MEMORY.md` contains no `STAGING_MARKER`
at all** — `mdstruct --headers` returns only the two headings, and the file ends at the
concept list. The self-clear defect described in §5.3 was real (the regex cannot match
`- [label with spaces](slug.md)`), and the block has since been removed by hand or by a
generator run against a file that had already lost it. Either way the *staging feature is
currently inert*: with no marker in the previous file, `prev.split(MARKER)` yields no prior
block, `kept` is empty, and each regeneration writes the `> empty — write memory/<slug>.md…`
placeholder afresh. **[gap]** Whether the marker was removed deliberately is not recorded.

⚑ **Two generators, two different markers.** `grammar_phrase_lattice.STAGING_MARKER` and
`synth_wire.STAGING_MARKER` are different strings. Preservation is exact-string keyed, so
running the wrong generator writes a marker the other cannot find and the next regeneration
drops the whole inbox silently.

### 2.6 Other on-disk state

| path | what |
|---|---|
| `synth/.cluster_cache.json` | `{"files": sorted names, "phrases": [phrase]}` — the ~78 s grammar build's output, keyed on the **file set only** |
| `.regen.lock` | `flock` target, single-instance guard |
| `.regen.log` | append target — **but only `synth_wire.py`'s stdout reaches it** (§5.1) |
| `MEMORY.md.bak-2026-06-24`, `MEMORY.md.pre-synth-bak` | manual backups from the swap |
| `ARCHIVE.md` | cold arcs, in `SKIP`, not indexed |
| `__pycache__/` | contains no `.md`, harmless to the glob |

⚑ **The two `.bak` files are `.md` and are NOT in `SKIP`.** `SKIP` lists `MEMORY.md`,
`ARCHIVE.md`, `MEMORY.candidate.md` (+ two more in the lattice's copy) by exact basename;
`MEMORY.md.bak-2026-06-24` matches none of them and matches `**/*.md`. **A 40 KB stale index and
a 5 KB one are being ingested as memories**, feeding a whole previous generation's phrase
vocabulary back into every cluster's support counts. This is the exact self-amplification the
`synth/` exclusion was written to prevent, leaking in through the back door.
**[code-confirmed; also independently recorded in the corpus's own incident memory.]**

---

## 3. THE PIPELINE

### 3.1 Dependency graph

```
                    eliza/sequitur.Sequitur, NT        eliza/{engine,router,alphabets,predictor}
                              │                                      │
                              ▼                                      │
                  grammar_phrase_lattice  ◄── (full, words, expand, SKIP, cluster_phrases)
                    │            │                                   │
        ┌───────────┘            └──────────────┐                    │
        │ (main(): DEAD/HAZARD)                 │                    │
        ▼                                       ▼                    │
   index/*.md                             synth_apex                 │
   MEMORY.md ⚠ 2nd writer         (build_context, members_of,        │
                                        build_apex)                  │
                                        │        │                   │
       ┌────────────────────────────────┘        └──────┐            │
       ▼                                                ▼            │
  synth_scale ──subprocess──► synth_gate           synth_wire        │
   │  │                        (exit code                │           │
   │  │                         DISCARDED)               ▼           │
   │  └──writes──► synth/<slug>.md ◄──gates──┐      MEMORY.md        │
   │                                                                 │
   └──writes──► synth/.cluster_cache.json                            │
                       ▲                                             │
                       │ (read-only)                                 │
                 synth_coverage                                      │
                                                                     │
   PROBES (all standalone, read-only, print-only):                   │
     synth_pi_probe ──────► grammar_phrase_lattice, Sequitur         │
     synth_typehole_probe ► + jea_pysim.Corpus, jea_pyalg.IR         │
     synth_grammar_read ──► grammar_phrase_lattice, Sequitur         │
     synth_reverse_probe ─► + eliza.engine ◄──────────────────────────┘
     chamber_coord_probe ─► eliza.{engine,router,alphabets} (standalone tokeniser)

   DEAD / PARALLEL (nothing imports; write MEMORY.candidate.md, not MEMORY.md):
     cluster_memories        (LSA/SVD experiment)
     build_warrants          (→ warrants.bib, stale since 2026-06-23)
     pcr_corpus_grammar      (trigram convergence diagnostic, print-only)

   ENTRY POINT:
     regen_if_stale.sh  ──[Stop + SessionStart hook]──► synth_scale.py 4 && synth_wire.py
```

`ELIZA` is located by `os.path.realpath(os.path.join(HERE, "../../../../github/substrate/scratch/eliza"))`
— **a relative path from the memory directory up four levels into the user's home**. Brittle:
it hardcodes the layout of `~/.claude/projects/<mangled-name>/memory/`. `synth_typehole_probe`
goes further and hardcodes two absolute paths under `/home/mikemol/`.

### 3.2 The live sequence

1. **Trigger** — `regen_if_stale.sh`, wired as a **Stop + SessionStart hook** in
   `~/.claude/settings.json`.
2. **Staleness gate** — cheap mtime test: any `*.md` under `memory/` newer than `MEMORY.md`,
   excluding `MEMORY.md`, `ARCHIVE.md`, and (by a `grep -vE '/index/|/synth/'` on find output)
   the two derived trees; **or** `synth_wire.py` itself newer than `MEMORY.md`. Not stale → exit 0.
3. **Detached single-instance launch** —
   `setsid flock -n .regen.lock -c "cd $MEM && timeout 560 python3 synth_scale.py 4 && python3 synth_wire.py >>.regen.log 2>&1" &`.
   `flock -n` means a second trigger during a run **skips silently**; the next hook re-gates.
   Always exits 0 — "best-effort, never breaks a session".
4. **`synth_scale.py 4`** — §3.3.
5. **`synth_wire.py`** — reads the cache, ranks, filters, writes `MEMORY.md`.

Cost: **~5 minutes** **[prose, from the script's own comment]**.

### 3.3 `synth_scale.py` — incrementality, and its two oracles

```
ctx = synth_apex.build_context()                        # corpus + gauge, once
phrases = cache["phrases"] if cache["files"] == sorted(ctx["names"]) and not --all
          else G.cluster_phrases(...)  (and rewrite the cache)
for ph in phrases:
    members = synth_apex.members_of(ph, ctx)
    if len(members) < MIN: continue                     # MIN=4 as wired
    if FORCE or stale(ph, members): build_apex(ph, ctx)  # IN-PROCESS
    else: skipped += 1
if regenerated: subprocess synth_gate.py <regenerated paths>
```

Two independent freshness oracles, both mtime-based:

- **Phrase-list cache** keyed on the **file set only**. A content edit that introduces a wholly
  new concept is invisible until a file is added or removed, or `--all` is passed. The docstring
  calls this a "documented trade-off". ⚑ `regen_if_stale.sh` **never passes `--all`.**
- **Per-apex staleness**: `stale(ph, members)` is true if the apex file is missing, or if any of
  (current members ∪ names parsed from the apex's own recorded `## witnesses`) has an mtime later
  than the apex's. Using the recorded witnesses means a memory that *left* the cluster still
  triggers a rebuild — correct. But `PATHS.get(nm)` failing (an unresolvable name) **fails
  open**: `any(...)` over an empty contribution is `False`, so the apex reads fresh.

`members_of(phrase, ctx)` is the membership definition used everywhere downstream:

```
p = " " + phrase + " "
[i for i in range(N) if p in text[i] or p in nametok[i]]
```

— body-substring **or** *namesake* (the filename, `_`→space, tokenised). The namesake clause is
why the canonical source memory joins its own cluster even if its body phrases the idea
differently.

### 3.4 What is idempotent, what is gated

| module | writes | idempotent? |
|---|---|---|
| `synth_apex.build_apex` | `synth/<slug>.md` | Yes — pure function of (phrase, corpus) |
| `synth_scale` | apexes + cache | Yes given a fixed corpus; **mtime-driven**, so `touch`/`cp`/`git checkout` perturbs it |
| `synth_wire` | `MEMORY.md` | Yes for the generated part; **not** for staging (§2.5) |
| `synth_gate` | nothing | Yes — pure, exit code only |
| `synth_coverage` | nothing | Yes — read-only **by construction** |
| `grammar_phrase_lattice.main` | `index/` (rmtree+recreate), `MEMORY.md` | Yes in itself, **destructive to the live root** |
| `build_warrants` | `warrants.bib`, `MEMORY.candidate.md` | Yes |
| `cluster_memories` | `MEMORY.candidate.md` | Yes |
| 4 probes, `synth_grammar_read`, `pcr_corpus_grammar` | nothing | Yes |

⚑ **No module anywhere in the tree has `--apply` or `--dry-run`.** Every write is unconditional,
and the whole chain is fired automatically by a hook. In a repo whose standing rule is
mutation-by-explicit-intent, this tree is the exception — and it is the exception that runs on
its own.

⚑ **The single sharpest hazard, and it is `import`-reachable.** `synth_wire.py` has **no
`main()` and no `if __name__ == "__main__"` guard.** Its module body runs top-to-bottom on
import and ends in `open(root_path, "w").write(txt)`. **`import synth_wire` rewrites the live
session index as a side effect.** `synth_coverage` documents this as its reason for extracting
`is_concept` by regex-and-`exec` rather than importing it (§4.5).

### 3.5 `regen_if_stale.sh`'s position

It is the **only** automatic entry point, and it is a *gate plus a launcher* rather than a stage.
Three design commitments worth preserving:

1. **Cheap gate before expensive work** — an mtime `find`, so the common (fresh) case costs
   nothing and the hook returns instantly.
2. **Detached + `setsid`** — the ~5-minute regeneration never blocks a turn.
3. **`flock -n`, not `flock -w`** — a concurrent trigger *skips* rather than queues; the next
   Stop/SessionStart re-gates and catches whatever was missed. Queuing would let hook triggers
   pile into a backlog of redundant 5-minute jobs.

`timeout 560` bounds the run below what is presumably a 600 s harness limit. ⚑ **A SIGKILL at
560 s can land mid-`write` on `MEMORY.md`** — the write is `open(path,"w").write(txt)` with no
temp-file-then-rename — **truncating the live index** with no backup in the current path.

---

## 4. THE PROBES

Five read-only investigative modules (the four named plus `synth_grammar_read`, which is the same
kind of thing). All take a cluster phrase as `argv[1]`, default `"never discard residue"`, and
print. **A probe here is an epistemic instrument: it exists to test whether a claim the pipeline
makes about itself is true.** Several encode a specific past error.

### 4.1 `synth_pi_probe.py` — is the apex a Π or a Σ?

**Question.** The apex renders as a *list* of phrases — a Σ (sum: "here are the alternatives").
Is there a Π (product: a single shared skeleton with a variable slot) underneath?

**Method.** Collect the cluster's recurring 2–5-token phrases (≥2 members). For each phrase and
each position `i`, form the skeleton `p[:i] + ("⟨⟩",) + p[i+1:]` and record `p[i]` as a filler.
A skeleton with **≥2 distinct fillers** is a real quotient: `⟨eea|algebra⟩ trace`.

**Positive result.** Templates exist ⇒ the commonality is *sequential/structural*: one skeleton
(the Π, the universal structure) plus a hole whose fillers are the retained per-member variation.

**Negative result is explicitly handled** and is the interesting half — the code prints:
> "no phrase shares a skeleton-with-one-hole — the cluster's commonality is lexical, not
> sequential: the apex is genuinely a Σ at the phrase level, a Π only at the token level"

**What it was built to catch — [prose, from the docstring]:** *"My projection was a SUM
(⊕ phrases — enumerate alternatives)."* The author caught themselves emitting an enumeration
where the corpus's own discipline demands finding the common structure. The probe is the
mechanised version of the question "is this list actually one thing?", and it can answer *no*,
which is what makes it a probe rather than a rhetorical device.

### 4.2 `synth_reverse_probe.py` — can the apex be *computed* rather than written?

**Question.** Can a cluster's apex skeleton be derived as a **group-theoretic address** instead
of rendered from text?

**Method.** Forward (lossy, "Forgetful"): route each member's distinctive terms through eliza's
`Engine` on the S₄ Cayley graph, using the SVD gauge (term → mode 0/1/2 → generator s1/s2/s3);
take each member's dominant orbit; histogram over members. Reverse ("Free"): the modal orbit's
shortlex-canonical word `s_i · s_j …` is a *section* — the apex skeleton. Decode each generator
back through the inverse gauge (mode → its top-loading terms), then intersect with the cluster's
**meet** (`cdf ≥ 0.4 × M`).

**Positive result.** Members **concentrate** in one orbit (the printout gives the percentage) ⇒
the cluster has a genuine group-invariant address, and the canonical word decomposes the shared
meaning along the SVD content axes.

**What it was built to catch — [prose + code].** Two things, and the second is sharper. (a) The
"lead with the instrument" discipline: it *calls* `eliza.engine.Engine` rather than
reimplementing a thinner spectral core. (b) An explicit anti-boilerplate correction, stated in a
code comment: the content is decoded **against the cluster's meet**, "which is boilerplate-free
BY CONSTRUCTION (the vocab cap df ≤ 60 drops the corpus-wide structural words; the meet is the
intersection, not a data-mode)" — i.e. an earlier reading that decoded content from the SVD mode's
top terms directly returned corpus boilerplate, and the fix was to intersect with the cluster's
own shared vocabulary. Its final line prints "the overclaim ceiling — apex may not exceed",
which is **the direct ancestor of `synth_gate.py`**: this probe discovered the ceiling, the gate
mechanised it.

⚑ Note its glob excludes `index/` but **not** `synth/` — unlike every live-path module. It
ingests apexes as corpus. A reimplementer should treat that as a bug in the probe.

### 4.3 `synth_typehole_probe.py` — is the shared structure *hierarchical*?

**Question.** `synth_pi_probe` finds holes at **one** slot, flat. Do the fillers of a hole
themselves share sub-structure — i.e. are the holes **nested**?

**Method.** Intern each cluster phrase as its Sequitur **rule tree** (not its flat expansion)
into `jea_pysim.Corpus`'s hash-consing interner: `IR(kind="tok", op=word)` for terminals,
`IR(kind="seq", children=…)` for rules, memoised per rule id. Identical sub-phrases hash-cons to
one node, so **fan-in ≥ 2 is a shared subtree** — the repo's SPPF wedge machinery applied to
phrases. Group trees by `(head child id, arity)` so they are positionally comparable, require
≥3 trees per group, then call the repo's real `Corpus.typehole()`, which recurses positionally:
a position whose fillers share sub-structure becomes a **skeleton with sub-holes**; only a
position whose fillers share nothing becomes a terminal hole.

**Positive result.** Groups at `depth ≥ 2` ⇒ genuine hierarchy. The module reports exactly that
count — `depth≥2 groups (genuine hierarchy): N` — which is the probe's verdict line.

**What it was built to catch — [prose].** The docstring frames it as *"the REAL
jea_pysim.typehole … vs my one-slot version"* — i.e. a check that the hand-rolled abstraction in
`synth_pi_probe` was not a thinner reimplementation of machinery the repo already had. That is
this repository's central recurring failure mode (reinvent-before-reuse), and the probe is its
correction applied to the author's own probe.

### 4.4 `chamber_coord_probe.py` — does a content-carrying gauge beat a content-blind one?

**Question.** Route every memory through eliza's real S₄ `Engine` and read its chamber
coordinate — orbit (S₄/V₄ ≅ S₃, 6 values), V₄ fiber, chirality, Fiedler value, turbulence value.
Does this coordinatise the corpus?

**Method.** Two gauges, selected by `argv[1]`:
- **`hash`** (default) — `blake2b(term)` mod 3 → generator. Same term → same generator across
  memories, but *the generator carries no meaning*, so orbits should be **uniform**.
- **`content`** — the SVD gauge (term → dominant mode 1–3 → generator). Shared *meaning* → shared
  generators → correlated walks → orbits should **cluster**.

It prints the final-chamber orbit distribution, the fiber and chirality distributions, and the
trajectory-dominant-orbit distribution.

**Positive result.** `content` produces a **skewed** orbit distribution where `hash` produces a
flat one ⇒ the geometry is carrying content, not just hashing.

**What it was built to catch.** The hash gauge is a **null control**, and that is the whole
design. Without it, any orbit distribution looks like a finding; with it, you can tell structure
from an artifact of the walk. It also answers a second self-check in its last line — whether the
*trajectory-dominant* orbit is more informative than the *final chamber* — i.e. whether the
coordinate should be read from the endpoint or the path. **[prose]** The docstring's framing
("lead-with-the-instrument … NOT a reimplementation of eliza's spectral core — it CALLS
eliza.engine.Engine, the way the user directed") records the same reuse-before-reinvent pressure
as §4.3, and "route-is-gauge: this gauge is one of many; we lead with it to SEE" is an explicit
refusal to treat the chosen gauge as canonical.

### 4.5 `synth_coverage.py` — the probe aimed at the pipeline itself

Not in the user's list of four, but it is the most instructive module in the tree and its comments
are the densest incident record. **Question:** *how much of the corpus actually reaches the index
that gets loaded into every session?*

**Why it exists — [prose, and it names the gap precisely]:** `synth_scale` prints
`regenerated N apexes, M skipped`; `synth_wire` prints `N concept→apex links`. **Both count
apexes. Neither counts memories.** A memory below the `MIN` floor is `continue`d before any
counter — "not filtered; INVISIBLE, and invisible with no diagnostic". A memory reaching no apex
is functionally absent from the mesh, because `MEMORY.md` is a list of apex links.

Modes: bare (the census), `--uncovered`, `--orphans`, `--min N`, `--sweep`, `--selftest`. Its
design decisions are each a defended position:

- **Read-only by construction** — "it takes no mutating mode at all, so it can never be the
  thing that truncates MEMORY.md."
- **Imports the pipeline's own `build_context`, never re-derives it** — "a second implementation
  would answer a question about ITSELF rather than about the pipeline."
- **Reports cache freshness alongside the number** — because the cache is file-set-keyed, a
  coverage number computed against a stale phrase list "is a fact about the cache".
- **`--sweep` reports cost beside coverage** — "coverage is MONOTONE in the floor by
  construction, so a coverage column alone always argues for floor 1."
- **The cost column is `MEMORY.md lines`, not apex files** — because `is_concept` drops ~9% of
  generated apexes (104 → 95 at the wired floor, per its comment), so apex counts overstate the
  index by the filter rate; and because disk counts are a fact about past runs, which "would
  report the same number five times and look like a measurement".
- **It reports the distribution, not just the total** — an `apexes per covered memory`
  histogram plus a count of memories hanging on a **single** apex, "one phrase-shift from
  invisible".
- **It has the tree's only selftest**, pinning the link regex (including that a prose mention
  `see synth/a-b.md` must *not* match), the floor semantics, and the borrowed predicate.

---

## 5. THE FAILURE MODES IT DEFENDS AGAINST — the incident ledger

Harvested from ⚑ comments, docstrings, and the corpus's own verified incident memory
`memory-pipeline-gate-is-discarded.md` (2026-08-19; its author states each claim was
hand-confirmed against live code, and I re-confirmed the code-shape of each below).

### 5.1 ⚑⚑ The gate's verdict is discarded by shell binding — AND the gate cannot block anyway

Two independent defects that **compose into "the pipeline is structurally incapable of reporting
a failure"**:

1. `regen_if_stale.sh`'s command is
   `… timeout 560 python3 synth_scale.py 4 && python3 synth_wire.py >>'$MEM/.regen.log' 2>&1`.
   **The redirect binds to the last command only.** `synth_scale.py`'s stdout — the *sole*
   emitter of the `=== GATE (regenerated): N PASS, M FAIL ===` line — falls through to the outer
   `>/dev/null 2>&1`. Measured by the incident memory: `grep -c GATE .regen.log` → **0** across a
   77 KB log of dozens of runs. (The log is now 86 KB.)
2. `synth_scale.py` runs the gate with `capture_output=True` and **never reads
   `g.returncode`**. It greps the captured stdout for `FAIL` lines and prints a count — and then
   continues regardless. Worse, **apexes are written before the gate runs**. A FAILing apex is
   already on disk and gets wired into `MEMORY.md`.

**Reimplementer's instruction:** `MEMORY.md`'s preamble claims "every line witnessed by ≥2 members
**and gated by `synth_gate.py`**". The ≥2-witness half is genuinely enforced at construction
(`synth_apex`'s `len(mset) >= 2`). The *gating* half **has never produced an observed verdict in
production.** Build it so the gate runs before the write, or make the write conditional on the
exit code, and let the verdict reach the log.

### 5.2 ⚑⚑ `import synth_wire` overwrites `MEMORY.md`

No `main()`, no `__name__` guard, module body ends in a write to the live index. A read-only
census that imported it to borrow one predicate would rewrite the session index as a side effect
of being asked a question. `synth_coverage._borrow_is_concept` extracts the `GLUE` assignment and
the `def is_concept` **by regex and `exec`s them in an empty namespace** rather than importing —
deliberately, so there is still exactly one authority for the predicate (an edit is picked up; a
rename **raises** rather than silently falling back to a stale copy).

⚑ **And the extraction regex itself carries an incident.** The first version bounded the capture
by indentation (`(?:^(?: {4}.*)?\n)*`), which **also matches blank lines**, so the capture ran
past `is_concept` into the next module-level statement and the `exec` died on `NameError: os`.
Fixed by anchoring on the predicate's literal last line, `    return True`. Caught by the
module's own selftest on its first run — which is why the borrow is pinned by cases rather than
trusted.

### 5.3 ⚑ Staging self-clear is dead → the index grew monotonically

`synth_wire.py`'s reference regex is `\[\[?([a-z0-9_]+)\]?\]|\(\.\./([a-z0-9_]+)\.md\)`. Live
staging entries are written as `- [label with spaces](slug.md)` — no `../` prefix, and
`[a-z0-9_]+` cannot match a label containing spaces or hyphens. So `slugs == []`, the
`if slugs and all(...)` guard is falsy, and **the line is kept forever**. Confirmed in the
incident memory: `reuse-search-structural-questions.md` existed since 2026-07-16 and its staging
line was still in `MEMORY.md` on 2026-08-19.

Named there as "the growth driver behind the 200-line read budget", with **no bound in code** —
`synth_wire.py` prints the KB size as a report, with no threshold and no non-zero exit.

**[divergence, this study]** The staging block and its marker are **now absent from the live
`MEMORY.md`**. The defect was real; the block is gone; whether by hand or by accident is
unrecorded. A reimplementer should fix the regex (accept any label text; resolve on the link
*target*) rather than reproduce either state.

### 5.4 ⚑ A second live writer to `MEMORY.md`, reachable by a bare invocation

`grammar_phrase_lattice.main()` writes `MEMORY.md` with a **different `STAGING_MARKER`** and
`shutil.rmtree`s `index/`. Staging preservation is exact-string-keyed, so running it writes a
marker `synth_wire` cannot find, and **the next regeneration silently drops the whole inbox**.
No flag is required — `python3 grammar_phrase_lattice.py` does it. The module is *also* the
import target every synth module depends on for `full`/`words`/`expand`/`SKIP`/`cluster_phrases`,
so it cannot simply be deleted. **A clean-room implementation must split the library from the
generator.**

### 5.5 ⚑ mtime, not content hash, is the freshness oracle

Both `stale()` and the shell gate compare mtimes. A `git checkout`, `cp`, or `touch` makes an
apex spuriously fresh (skipping a needed rebuild) or spuriously stale (a wasted 5-minute run).

### 5.6 ⚑ The cache is keyed on the file set only, and `--all` is never passed

A content edit that introduces a wholly new concept cannot surface until a file is added or
removed. The docstring calls it a documented trade-off; the hook never passes `--all`, so in
production the trade-off is permanent. `synth_coverage._load` defends downstream by reporting
`⚑ CACHE STALE vs corpus` beside any number it computes.

### 5.7 ⚑ Two confident zeros

- `synth_scale`'s `nothing outdated — every apex is newer than its members and witnesses` prints
  both when everything genuinely is fresh **and** when every wikilink target was unresolvable
  (`stale()` fails open on `PATHS.get(nm) → None`).
- Clusters below `MIN` are `continue`d **before** the skip counter, so the printed
  `regenerated N, skipped M` does not sum to the phrase count. This is the gap
  `synth_coverage` was written to close.

### 5.8 ⚑ Non-atomic write to the live index, under a kill timer

`open(root_path, "w").write(txt)`, no temp-then-rename, inside `timeout 560`. A SIGKILL mid-write
**truncates `MEMORY.md`** — the file loaded into every session — with no backup in the current
path.

### 5.9 ⚑ The `.bak` files are ingested as memories

`MEMORY.md.bak-2026-06-24` (40 KB) and `MEMORY.md.pre-synth-bak` (5 KB) are `.md`, are not in
`SKIP` (which matches exact basenames), and match the `**/*.md` glob. A whole previous
generation of the index is feeding phantom phrase support into every cluster. Any reimplementation
must filter by **prefix or extension pattern**, not an exact-basename set.

### 5.10 ⚑ The pairwise band's witness links are index-space-confused

Documented in full at §1.2.5, verified against a live artifact. Member-local indices used to
subscript the global names list. The `## witnesses` section is correct; the pairwise `[[links]]`
name unrelated memories. The gate cannot catch it because it strips links before checking.

### 5.11 ⚑ `--calls`-style censuses miss a capability spelled differently

Encoded in `synth_coverage`'s selftest philosophy and in the corpus's `census-keyed-on-one-spelling`
memory. Concretely here: the link regex `\]\(synth/([a-z0-9-]+)\.md\)` **also matches the
preamble's own format specimen** ``[concept](synth/slug.md) [N]``, which produced a phantom
`DANGLING slug` on the first run — *the instrument reporting its own documentation as a broken
edge*. Excluded by the literal placeholder name `slug`, **not by line position**, so moving the
preamble cannot resurrect it.

### 5.12 ⚑ Zero selftests outside `synth_coverage`; nothing gates any of it

`MEMORY.md` lives outside the repository, so no commit gate can see it. `synth_coverage
--selftest` is the only executable check in the tree, and it covers only `synth_coverage`.

### 5.13 ⚑ Rule utility disabled — do not "fix" it

§1.1.4. The single most likely well-intentioned regression a clean-room implementer following
the textbook would introduce.

### 5.14 ⚑ Recursive expansion overflows the stack

§1.1.6. Both `expand` implementations are explicitly iterative for this reason, with an
`out`-length cap and a `seen` cycle guard.

### 5.15 ⚑ Sequitur is the wrong tool for cyclic amplification

§1.6. `pcr_corpus_grammar`'s own comment: "Sequitur explodes on identical-repetition — wrong tool
for PCR; the Markov operator is the right one." The docstring above it still says Sequitur.

### 5.16 ⚑ PCR counts are multiplied by the cycle number

§1.6. Raw counts are meaningless after cyclic replay; `per_pass = k / cycles` is the only honest
statistic. The comment tags it `[don't-collapse: per-pass, not raw]`.

### 5.17 ⚑ Absolute convergence thresholds never fire under a Laplace floor

§1.6. The large-vocabulary Laplace smoothing floor makes surprise asymptote to a positive
constant. The test must be **relative** (`Δ/level < 1%`).

### 5.18 ⚑ Clustering history: three failed metrics before the current one

`cluster_memories`'s refinement log, preserved verbatim: v1 max-df → generic words; v2 min-df →
random rare words; v3 IDF connected components → over-merged (190 of 196 memories in one
component, no resolution control); v4 SVD/LSA, where orthogonality replaces transitive merge.
**The v3 failure is why `cluster_phrases`'s collapse 3 requires a Jaccard threshold *in addition
to* shared tokens** — transitive merge on lexical overlap alone collapses the corpus.

### 5.19 ⚑ Markdown lint pressure shaped the output format

Both generators carry: the mixfix-backtick regex (MD049), a blank line after every heading
(MD022/MD032), and the wired-count caption as a **blockquote** rather than bold text (MD036).
Cosmetic, but they are why the emitters look the way they do.

### 5.20 ⚑ Fragile frontmatter parsing, failing open in one module and closed in another

§2.1. `G.full` returns the raw file including frontmatter on a parse miss; `build_warrants.parse`
drops the file. Neither reports.

---

## 6. Clean-room build order

1. **Sequitur** (§1.1) with **utility disabled**, digram-uniqueness only, iterative `expand` with
   a length cap and cycle guard. Replace `_find_exact_rule_for`'s linear scan with a
   `{digram → rule_id}` map. Skip V₄ canonicalisation.
2. **Corpus I/O** (§2.1): the recursive glob with a **prefix-based** skip (not exact basenames),
   the `---`-fenced frontmatter reader, `full()` with path-stripping, and the order-preserving
   `words()` tokeniser. Exclude derived trees (`synth/`, `index/`) unconditionally.
3. **`cluster_phrases`** (§1.3.2): grammar → phrase/member pairs → prefix-strip merge →
   maximality-within-identical-members → Jaccard+kernel union-find.
4. **`build_context`** (§1.4): df-banded vocabulary + `GENERIC` filter. The SVD is optional for
   the apex path; include it only if you also build the probes.
5. **`build_apex`** (§1.2): cluster-local grammar → filters → member sets → maximal-phrase dedup →
   three-band grading → render. **Fix §1.2.5** (`names[members[j]]`).
6. **`synth_gate`** (§1.5.2): witness → corpus-df ceiling at ≥2, render extraction, `stem_match`.
   Either implement `metadata.allow` or delete the docstring's promise of it.
7. **`synth_scale`** (§3.3): the cache, the two staleness oracles, in-process regeneration — and
   **run the gate before the write, and read its exit code.**
8. **`synth_wire`** (§2.5): rank, `is_concept` filter, emit. **Give it a `main()` and a
   `__name__` guard.** Write via temp-file-then-`os.replace`.
9. **`synth_coverage`** (§4.5): the census, from the start. It is the only thing that can tell
   you whether steps 1–8 are working on the corpus rather than on themselves.
10. **The probes**, if you want the epistemic layer.
11. **The hook** (§3.5): cheap mtime gate, `setsid`, `flock -n`, `timeout`. **Redirect the whole
    compound command, not its last member** (wrap in `{ …; }` or redirect per-command).

Optional/parallel: `build_warrants` (a citation-DAG view), `cluster_memories` (LSA),
`pcr_corpus_grammar` (a convergence diagnostic). None is required for the index.

---

## 7. What I could not determine

- **[gap]** Derivations for: `K=16`, `MARGIN=1.4`, the `0.6` soft-membership band, `3 ≤ df ≤ 60`,
  `GENERIC`/`DROP`/`GLUE`/`ALLOW`/`STOP` word-list contents, `meet ≥ 0.4·M`, `tau=0.5`, the `0.8`
  near-identity shortcut, the `≥2 shared tokens` kernel size, `hi = max(3, M//2)`, band caps
  8/12/6, phrase-length window `2 ≤ len ≤ 14` (apex) vs `≥3` (lattice), `max_out` 24/40, the
  `MIN=4` member floor, `APEXN=24`, `max_tiers=6`, `max_depth=2`, P90, 25 PCR cycles, the 1%
  convergence threshold, `per_pass ≥ 2`, `stem_match`'s 4- and 5-character constants,
  `timeout 560`. All read as empirical tuning. Several appear in ≥3 modules and would be a
  single-source-of-truth candidate in a reimplementation.
- **[gap]** Whether `index/`, `warrants.bib`, `cluster_memories`, and `pcr_corpus_grammar` are
  *intentionally* retained as parallel views or are simply unreaped. Their staleness is a fact;
  the intent is not recorded.
- **[gap]** Whether the staging block's removal from the live `MEMORY.md` was deliberate.
- **[gap]** Whether the `MIN=4` floor's coverage cost has ever been read. `synth_coverage
  --sweep` exists to answer exactly this and I did not run it (it is read-only and safe to run,
  but it calls `build_context`, a multi-second corpus load, and the instruction was a read-only
  study).
- **[not run]** Every behavioural claim about runtimes (~78 s grammar build, ~5 min regeneration)
  is **[prose]** from the modules' own comments.
- **[not verified]** `eliza`'s `Engine`, `Router`, `TrigramPredictor`, `manifold`, `cocycle`, and
  `jea_pysim.Corpus.typehole` are used as black boxes here. I read `sequitur.py` in full because
  it is the load-bearing math; the others I characterised from their call sites only. A
  reimplementer needs `sequitur.py` and can treat the rest as probe-only dependencies.

---

## 8. Verified-by-code vs. taken-from-prose

**Read in full from source, and every claim above about them is code-derived:**
`eliza/sequitur.py`, `grammar_phrase_lattice.py`, `synth_apex.py`, `synth_scale.py`,
`synth_wire.py`, `synth_gate.py`, `synth_coverage.py`, `cluster_memories.py`,
`pcr_corpus_grammar.py`, `build_warrants.py`, `synth_grammar_read.py`, `synth_pi_probe.py`,
`synth_reverse_probe.py`, `synth_typehole_probe.py`, `chamber_coord_probe.py`,
`regen_if_stale.sh`.

**Verified against on-disk artifacts:** the corpus listing and its `archive/`/`discipline/`
subdirectories; `index/` contents and their 2026-06-24 date; `synth/` contents (118 files);
`MEMORY.md`'s heading structure and the **absence** of a staging marker; two full apex files
(`reuse-search`, `suc-suc-suc`); one memory file's frontmatter; `warrants.bib`'s 196 entries and
uniform field set via `bibstruct --entries`.

**Taken from prose (docstrings, comments) and NOT independently confirmed:** the ~78 s grammar
build time; the ~5 min regeneration time; the `104 → 95` apex-to-link filter rate; the
`grep -c GATE .regen.log → 0` measurement; the "eliza convention" for dropping SVD mode 0; the
claim that recursive expansion overflows the stack; the "lossless / retraction / reify" overclaim
incident that motivated the gate; the v1–v4 clustering refinement history; the ~9% `is_concept`
drop rate.

**Divergences found — code wins, and a clean-room implementer must not follow the prose:**

| # | prose says | code does |
|---|---|---|
| 1 | `pcr_corpus_grammar`: "amplified **Sequitur** rules ARE the corpus's motifs" | uses a **TrigramPredictor**; `Sequitur` is imported and never instantiated (a comment eight lines in retracts the docstring) |
| 2 | `synth_gate`: a word may pass via the file's `metadata.allow` | `metadata.allow` is **never read**; only the module-global `ALLOW` exists |
| 3 | `MEMORY.md` preamble: "gated by `synth_gate.py`" | the gate's verdict is unreachable in production (§5.1) |
| 4 | `synth_apex`: the gauge is "term → dominant SVD content-mode" | in the live apex path only **set membership** in the gauge is read; the mode value is used solely by two probes |
| 5 | `cluster_memories` presents as the corpus's clusterer | it is a dead parallel experiment writing `MEMORY.candidate.md`; the live clusterer is `cluster_phrases` |
| 6 | `grammar_phrase_lattice`'s preamble describes the live root and `index/` | that root was superseded on 2026-06-24; running `main()` is now destructive (§5.4) |
| 7 | `MEMORY.md`/`synth_wire` describe a staging inbox | no staging marker exists in the live file; the feature is inert |
| 8 | apex pairwise band presents `[[links]]` as that phrase's two witnesses | member-local indices subscript the global names list; the links name unrelated memories (§1.2.5, §5.10) |
| 9 | `grammar_phrase_lattice`'s preamble: "Formal claims + causality: `warrants.bib`" | `warrants.bib` is frozen at 2026-06-23 and read by nothing |
| 10 | Sequitur's own module docstring: "Invariants maintained continuously: 1. digram uniqueness 2. **rule utility**" | rule utility is **disabled** — the call is commented out with a reason (§1.1.4) |

Divergence 10 is the most dangerous of the ten: it appears in the *file header* of the algorithm
module, states a textbook invariant, and is contradicted only by a commented-out line 250 lines
below.
