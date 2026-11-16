# Making `event` reconstructible from (SPPF, reverse index)

**Question (user, 2026-08-07, asked twice):** *"Take time to think about how to make event
reconstructible from the reverse index and the sppf."*

⚑ **THE ANSWER IS THAT IT ALREADY IS, AND EVERYTHING BELOW THE NEXT SECTION IS ME ANALYSING
THE WRONG ARROW.** `ekey` is base64 of a JSON object carrying the full content:

```json
{"c": "Id", "ch": [15153], "i": null, "q": null}
```

`c`=ctor, `ch`=child local_ids, `i`=idx, `q`=qname. So `event`'s four non-key columns are a
DECODED PROJECTION OF ITS OWN KEY — not independent data — and `obs.ekey` carries the same
object per occurrence. **Nothing needs to be recovered from the SPPF at all.**

The two passes below reason carefully about what `project_sppf`'s head does and does not
preserve (`idx` dropped for non-`Var`, `ctor`/`qname` merged into `op`, a dot heuristic
reading them back). Every word of that is TRUE and NONE of it is load-bearing: reconstruction
never has to invert `head`, because the content never left `ekey`. I was asked this question
twice and answered the second time by finally READING A ROW — `schema.py --sample`, which did
not exist until I needed it.

**They are kept, not deleted.** The head's lossiness is a real property with real consequences
(it is why `raw_ctor` is re-read separately, and why the codomain qname is recovered by
checking for a dot), and a future reader asking "can I derive X from `_node`?" needs it. What
must not survive is the framing that it BLOCKS reconstruction.

---

## ⚑ THE GOVERNING CONSTRAINT: the product must RECONSTRUCT the event set

**User, 2026-08-07:** *"The product of the SPPF and (other table(s)) must ≡ the input event
set. That's what we're draining and tiering towards."*

This is the test every proposed tier must pass, and it rules out the thing I was about to
build. Having measured that `scope_fix`'s references are **380 rows against 74,223
observations (195×)**, I started designing a `ref(core_id, plid, ord, qname, args)` relation —
small, sufficient for the resolver, and **not a factor**. It keeps what one consumer reads and
drops the rest, so `SPPF × ref` reconstructs nothing. That is a SUMMARY chosen by a consumer,
not a decomposition of the data.

**The honest partition of one core** (`V4-as-PFG.agdai`, sandbox, after v2 recovery):

    74,223 observations
       380  carry a qname      (the references — what the resolver wants)
     1,383  carry an idx       (de Bruijn variables)
     8,578  carry a literal
    63,882  BARE — no payload at all                        86%

A reference projection retains 0.5% and discards 86% of the rows outright. It cannot be a
factor of anything.

**Where the bare rows actually factor:** they are not empty — they carry `(ctor, children)`,
which is exactly the SPPF's content. Measured: **31,026 distinct ekeys across 63,882 bare
rows — 2.06× sharing**, and that sharing IS the projection. So the decomposition is

    event set  ≡  SPPF (shared content)  ×  fibre (which occurrence, at which position)

with `obs`'s `(core_id, local_id)` as the fibre — dense, hence positional (`--fibre`, all
cores). Nothing is chosen for a consumer's convenience; each side is what the quotient
produces.

⚑ **AND A CONSUMER-SHAPED TABLE IS STILL LEGITIMATE — AS AN INDEX, NEVER AS A TIER.** A `ref`
relation would be a fine derived index for `scope_fix` (195× cheaper to scan), rebuildable
from the pair at any time. What it must not be is the thing the event tier drains INTO,
because a drain licensed by it would delete the 86% it never modelled.

### The identity is DIRECTIONAL, and orphans are how it breaks

Measured in the sandbox after re-ingesting one core under two keyings:

    obs 74,520 rows · 33,067 distinct ekeys
    event 33,455 rows
    → 388 event rows NOTHING OBSERVES

`SPPF × fibre → event set` still holds — every observation reconstructs. What fails is the
other direction: `event` now carries rows no fibre reaches. They are INERT (no live read finds
them, which is why `_gc_orphan_events` calls itself *"guard; inert for the projection"*), but
they mean **`event` is no longer exactly the product** — it is the product plus residue.

⚑ **THE CAUSE IS THAT RECOVERY CHANGES THE KEY, AND THAT IS A TIER-WIDE MIGRATION.** `obs_rec`
IS the ekey's content, so a node that now recovers `q`/`i` hashes differently than it did under
the v1-shaped reads — measured: `Def` records carry `"q": "Substrate.Foundation.Eq.≡"` inside
the key where they previously carried `"q": null`. **The 168 live cores are keyed the old way**,
so a partial re-ingest leaves the tier holding BOTH keyings: the same term interning to two ids
depending on when it was written, which is exactly the order-dependence the content-addressed
key exists to eliminate.

**So the re-ingest is all-or-nothing per tier.** This is the `full=True` case `write_events`
already documents — *"a shim/Agda toolchain change that alters decode WITHOUT changing .agdai
bytes+mtime"* — and it is why `--ingest-core --full` on a SUBSET of the live store is unsafe
even though it is exactly right in the sandbox.

## The design, now that the data has been read

Three encodings sit on top of each other, and only ONE of them is a quotient. Conflating them
is what produced two wrong analyses:

| layer | map | invertible? | needs a fibre? |
|---|---|---|---|
| `ekey` = b64(JSON) | content ⟷ key | **YES — decode it** | no |
| `head` = (kind,role,op,lit) | 5 cols → 4 fields | **NO — lossy** | *irrelevant* |
| `node_id` = b64(head ‖ child syms) | occurrence → class | reversible ENCODING over a genuine QUOTIENT | **yes** |

⚑ **`node_id` IS REVERSIBLE, WHICH I ASSUMED IT WAS NOT.** Measured with `--sample _node`:

    node_id  ⟨'AgdaCore' ‖ '' ‖ 'UType' ‖ '' ‖ ''⟩
    sym      ⟨'AgdaCore' ‖ '' ‖ 'UType' ‖ ''⟩

It is base64 of a NUL-delimited string, not a hash — and the 5th field is itself base64 of the
children's syms, recursively. So `_node` and `node_child` are DERIVED INDEXES over a
self-describing key; the `_node` columns are redundant with the key they are stored beside.

**What this means for each relation:**

- **`event`** — reconstructible from `ekey` by decoding. Its four non-key columns are a
  projection of the key. *No SPPF needed, no fibre needed.*
- **`edge`** — reconstructible from `obs.ekey` by decoding `ch`. **6,273,548 rows / 2,716 MB
  carrying nothing `obs` does not.** ✅ **MEASURED OVER THE FULL POPULATION: 152 of 152 cores
  EXACT, 0 mismatch** (`reconstruct.py --edge`), set-compared per core, not counted. The
  20-core run agreed, but `--spread`'s 152× max/median is why the whole population was run.
- **`obs`** — the genuine residue. `(core_id, local_id)` is the fibre over the interning
  quotient, and `--fibre` measured it dense, so it is a positional `ekey[]` per core.
- **`terms` / `path_seg`** — leaf dictionaries; separate question, and small (7k rows).

⚑ **SO THE DRAIN'S TARGET IS NOT WHAT I THOUGHT.** I had `obs` as the thing to keep and `event`
as the thing to drain. Backwards: **`obs` (6.3M) and `edge` (6.3M) are the redundant pair** —
`edge` derives from `obs`, and `obs` compresses to a positional array per core — while `event`
(2.1M) is the irreducible dictionary that everything decodes out of. The 5.1 GB of `obs`+`edge`
is the win; the 613 MB of `event` is the base.

## What the tiers actually are

```
event(ekey PK, ctor_id, qname_pid, idx, lit_id)          2,124,390 rows
obs(core_id, local_id, ekey)  UNIQUE(core_id, local_id)  6,274,182 rows
_node(node_id PK, sym, kind_id, role_id,
      op_term_id, op_path_id, lit_id)                    the interned projection
```

`obs`/`event` is ~2.95, which is the first thing to get right: **`event` is already the
interned dictionary** — one row per distinct observation *content* — and `obs` is the
occurrence table. So `event` is not a staged copy awaiting a rebuild; it is the base half of
a decomposition one level *below* the one I had been reasoning about.

    obs   = recon( event , (core_id, local_id) )      ← positional fibre, MEASURED dense
    _node = recon( event-head , child symbols  )      ← the SPPF's own interning

## The obstruction, located exactly

`sppf_db.project_sppf:550-555` builds the head that becomes `node_id`:

```python
for ekey, ctor, qname, idx, litval in QB.run(con, "event_head"):
    if ctor in ("Var", "PVar"):    role, op = f"db{idx}", ""
    elif ctor in FREE and qname:   role, op = "", qname
    else:                          role, op = "", (ctor or "")
    head[ekey] = ("AgdaCore", role, op, litval or "")
    sym[ekey]  = _b64("\x00".join(head[ekey]))
```

Five columns in, four fields out — and the map is many-to-one in three separate ways:

| event column | fate in the head | recoverable? |
|---|---|---|
| `ctor_id` | merged into `op` (branch 3) | **only when no qname** |
| `qname_pid` | merged into `op` (branch 2) | **only via a dot heuristic** |
| `idx` | `db{idx}` in `role` — **for `Var`/`PVar` ONLY** | **NO for every other ctor** |
| `lit_id` | carried verbatim as the 4th field | yes |
| — | `kind` = constant `"AgdaCore"` | carries zero information |

⚑ **`ctor` and `qname` share one slot, and the projection reads them back by GUESSING.**
Line 575 recovers the codomain qname as `qn = o if (o and "." in o) else None` — a **dot
heuristic**, not a stored fact. That is the tell: the encoding already cannot distinguish its
own branches, so the projection re-derives the distinction from the string's shape. A ctor
name containing a dot, or a qname without one, breaks it silently.

⚑ **`idx` IS THE HARD LOSS.** For a non-`Var` ctor nothing in the head depends on `idx` at
all. Two events differing *only* in `idx` produce the **same `sym`**, hence the same packing,
hence one `_node` row — and no fibre over `_node` can tell them apart, because the
distinguishing datum was discarded at line 554, before any interning happened.

⚑ **AND `raw_ctor` IS THE PROOF THE AUTHOR ALREADY KNEW.** Line 556 re-reads the true
constructor *separately* from the head:

```python
raw_ctor = {e: ct for e, ct in QB.run(con, "event_ctor")}   # true constructor for cod()
```

If the head preserved the ctor, this second read would be unnecessary. Its existence is a
standing admission that `_node` does not carry it.

## Why this is a lossy-encoding problem, not a fibre problem

The `obs` case works because the quotient is **content-addressed and total**: `_node` collapses
distinct occurrences of identical content, and the fibre records which occurrence fell into
which class. Nothing is destroyed; it is *relocated*. `event = recon(SPPF, fibre)` holds
because a quotient together with its fibres IS the original.

Here the composite is different:

    event ──lossy encode──▶ head ──intern──▶ _node
             (NOT injective)      (quotient, fibre-recoverable)

A fibre inverts the second arrow. **Nothing inverts the first**, because it is not a quotient
by an equivalence on *stored* data — it is a projection that drops columns. Adding a fibre over
`_node` would faithfully record "these ekeys share this node" and still leave `idx`
unrecoverable.

**This is `feedback_wedge_not_projection` firing for real, one layer down from where I first
cited it.** I invoked it wrongly against the `obs`/fibre split (there both halves are kept);
here it is exactly right — `head` discards residue rather than relocating it.

## ⚑ MEASURED 2026-08-07: THERE IS NO STORED `ekey → node` EDGE AT ALL

The projection ran (`--finalize`, exit 0) and produced **4,775 `_node`, 10,366 `node_child`,
634 `_unit`, 114,477 `unit_node`** from 6,274,182 obs. Then `reconstruct --core
Algebra/F2/F2.agdai` reported **297 of 297 ekeys unresolvable**, under BOTH candidate joins:

    JOIN _node n ON n.node_id = o.ekey     → 297 of 297 missing
    ekey ∈ (SELECT sym FROM _node)         → 297 of 297 missing

⚑ **MY FIRST ATTEMPT ACCUSED THE STORE OF A BUG IN MY OWN JOIN.** It printed *"the SPPF does
not cover this core"* — a claim about the substrate — when the SPPF covers it fine and the
join was wrong. A fact about the METHOD reported as a fact about the SUBSTRATE, in a tool
written to license deletion. Both spellings now fail, which is what makes the conclusion an
observation rather than a second guess.

**Three distinct keys exist and nothing connects the first to the others:**

    event.ekey    the event tier's content key                    STORED (event PK, obs FK)
    sym[ekey]   = b64(head)                  head-only, global    STORED as _node.sym
    node_id     = b64(head ‖ child symbols)  the packing          STORED as _node.node_id

`sppf_db:578-589` computes the `(core, local_id) → packing` map in a **local dict** and never
writes it:

```python
packing = {}
def pack(c, lid):
    key = (c, lid)
    if key in packing: return packing[key]
    ...
    packing[key] = pk
    return pk
```

**So the reverse index the drain needs is computed on every projection and discarded.** That
is a much more direct finding than the encoding analysis below, and it changes the priority:
before any question about whether `event`'s *columns* are recoverable, the *addressing* is
missing. Without `ekey → node_id`, reconstructing a core means recomputing the packing from
`edge` — redoing the projection, not reflecting it.

⚑ **AND THIS IS THE `obs` REFLECTION'S BLOCKER TOO, not only `event`'s.** `reflects_obs`
cannot pass for any core until this map exists, so the ONE relation I claimed coverage for is
also unreconstructible today. `--coverage`'s ✓ on `obs` is aspirational, not achieved.

**The cheapest fix is a relation the projection already computes:**

```sql
obs_node(core_id, local_id, node_id)   -- or equivalently ekey → node_id
```

written from `packing` at the moment it is built. That is not new derivation — it is
persisting a value the projection has in hand and throws away.

## Three ways to close it, in ascending cost

**(1) Make the head injective — the encoding fix.** Stop merging `ctor` and `qname` into one
slot and stop conditioning `idx` on the ctor. A head of `(kind, role, ctor, qname, idx, lit)`
with each field in its own position is injective on the event's content, so `sym` becomes a
faithful key and `event` is recoverable from `_node` by *decoding the base64*, with no fibre
needed at all.

- **Cost:** every `node_id` changes, so the whole SPPF re-projects and every downstream
  artifact keyed on node_id is invalidated. Not incremental.
- ⚑ **And it CHANGES THE QUOTIENT, which is the real objection.** Distinct `idx` values would
  now produce distinct nodes, so sharing DROPS — the packing exists to collapse structurally
  identical subtrees, and `idx` is a de Bruijn index that *should* often be irrelevant to
  structural identity. Making the head injective makes the SPPF a worse SPPF. This is a
  genuine tension, not an oversight in the original design.

**(2) A `head_residue` relation — keep the quotient, store what it drops.** Leave the packing
exactly as it is and materialize the difference:

```sql
head_residue(ekey PK, ctor_id, qname_pid, idx)   -- what the head does not encode
```

Then `event = recon(_node-decoded-head, head_residue)` per ekey, and `lit_id` needs no entry
since the head carries it verbatim.

- **Preserves sharing** — `_node` is untouched, so no re-projection.
- **Honest about the decomposition**: this IS the residue, written down, which is the same move
  the reverse index makes for `obs`.
- ⚑ **But measure before believing the saving.** At 2.1M events, three columns each is not
  obviously cheaper than `event`'s five — the win is only real if `ctor_id`/`qname_pid` are
  highly repetitive across events (they are term-ids, so plausibly yes) or if a large fraction
  of events are `Var`/`PVar`, whose `idx` is already in the head and needs no row. **Unmeasured.
  The mode to add is a census of how many events actually differ from their head's preimage.**

**(3) Accept that `event` does not drain.** `event` is 613 MB against `obs`+`edge`'s 5.1 GB, so
it is ~11% of the tier. Draining `obs` and `edge` — the two that dominate — may be the whole
win, with `event` retained as the base it already is.

- ⚑ **This is the option the ratio argues for and I nearly skipped it.** `event` being the
  interned dictionary means it is *supposed* to persist; asking it to reconstruct from its own
  projection may be the wrong question. The thing that should drain is the occurrence data.

## What must be measured before choosing

Each of these is a question the tooling cannot answer today, and each would change the answer:

1. **How many events are actually indistinguishable by their head?** If the fibre-collapse is
   tiny, (2) is nearly free; if large, (1)'s sharing loss is correspondingly large. `SELECT
   count(*) - count(DISTINCT sym)` over events — needs a mode.
2. **What fraction of events are `Var`/`PVar`?** Their `idx` is already encoded, so they need no
   residue row under (2).
3. **Does `edge` reconstruct from `node_child` + the fibre?** `edge` is 6.3M rows — larger than
   `event` — and if it drains, (3) becomes much more attractive. `node_child` holds the
   interned parent/child structure and `edge` the per-core positional form; the relationship
   looks like the same `recon` shape, but that is a hypothesis about 6.3M rows and must not be
   assumed.

⚑ **DO NOT PICK ONE FROM THIS DOCUMENT.** Every option above is stated with its cost and its
unmeasured premise; the tension in (1) is real and (3) may make the question moot. The next
step is the measurement, not the build.
