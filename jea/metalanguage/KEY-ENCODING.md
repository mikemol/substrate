# The content-addressed key: what it buys, what it costs, and what postgres would prefer

**User, 2026-08-07:** *"the reason for the base64 trick was to achieve idempotence for
internment and ensuring that 'what order something entered the database' wouldn't actually
impact its id. The key contains everything needed to hash-cons bijectively. But I doubt it's
an efficient approach for pgsql...but I don't know what would be."*

## ⚑ THE COMBINED KEY IS A SQLITE WORKAROUND, NOT A DESIGN CHOICE

**User, 2026-08-07:** *"The combined ID is the way it is because sqlite couldn't do
multicolumn PKs. There's also the question of efficient querying."*

That reframes everything below. I had been treating the concatenated key as a deliberate
encoding to be traded off against width — it is a **constraint from a database the store no
longer runs on**, carried forward unexamined. Postgres has had multicolumn primary keys
since forever.

So the real question is not *"which serialization is narrowest"* but **"what does this key
look like when it stops pretending it has to be one column?"** Those give different answers:
a narrower blob is still a blob, while a composite key is *structured* — and structure is
what an index and a query planner can use.

⚑ **AND THE QUERYING COST IS THE HALF I HAD NOT MEASURED AT ALL.** I sized the key by
`pg_column_size` and stopped, which measures storage. The predicate cost is separate and
worse:

- **Every query against the key's PARTS must decode base64 first.** `ctor`, `idx`, `qname` and
  the child list live inside the blob, so "find every observation whose ctor is `Pi`" cannot
  use an index — it is a full scan with a decode per row. Today nothing asks that question,
  which is a fact about the QUERY SURFACE, not about the data: `query_defs.py` declares all 44
  tables as `Column(c, String)`, so the entire read layer treats these ids as opaque by
  construction. **The queries that would be expensive were never written, so the cost never
  showed up.**
- **`core_id` is 56 B as text vs 4 B as int** (measured), and it is the LEADING column of
  three indexes — `ix_obs_pk (core_id, local_id)`, `ix_edge_pk (core_id, plid, ord)`,
  `ix_edge_child (core_id, clid)` — over 12.5M rows. The width is paid in the heap AND in
  every index that leads with it.

## What the design buys — state it first, because every alternative must preserve it

`ekey = b64(json({"c": ctor, "ch": [child local_ids], "i": idx, "q": qname}))`

Three properties, and they are the reason the ingest is safe at all:

1. **Order-independence.** Identity is a function of content, so the same core ingested twice —
   or two cores sharing a subterm — produces the same id. Nothing depends on insertion
   sequence, which is what makes `ON CONFLICT DO NOTHING` *correct by construction* rather than
   a race that usually works.
2. **Idempotent interning.** Re-ingesting is a no-op, so an interrupted run resumes rather than
   duplicating. (Measured: an ingest was interrupted mid-corpus and the store is consistent.)
3. **Bijective hash-consing.** The key contains everything needed to reconstruct the value, so
   `event`'s four non-key columns are a decoded projection of its own PK — no lookup table, no
   fibre, no dependence on the SPPF. This is the property that makes the drain analysis work
   (`EVENT-REFLECTION.md`).

⚑ **(3) IS THE ONE MOST EASILY LOST, AND IT IS NOT OBVIOUSLY WORTH ITS PRICE.** A digest gives
1 and 2 at a fraction of the width; only 3 needs the key to *carry* the content. Any proposal
below must say explicitly which of the three it keeps.

## What it costs — measured, not estimated

Per-value width for one real key (`{"c": "Id", "ch": [26703], "i": null, "q": null}`), via
`pg_column_size` on the live server:

| encoding | bytes | keeps reversibility? |
|---|---|---|
| **base64 TEXT (today)** | **68** | yes |
| raw JSON text | 52 | yes |
| `bytea` | 52 | yes |
| `jsonb` | 66 | yes (and queryable) |
| `uuid` (128-bit digest) | **16** | **no** |

At 68 bytes inline (well under the ~2KB TOAST threshold, so uncompressed and not out-of-line),
across `obs` 6,274,182 + `event` 2,124,390 rows.

On-disk today: **`obs` 2,616 MB / 6,274,182 rows ≈ 437 B/row** for `(core_id, local_id, ekey,
seq)`, plus `edge` 2,716 MB and `event` 624 MB — 5,956 MB of the store's 6,022 MB.

## The cost is THREE separable things, and only one is the base64

Reading one row makes the breakdown obvious:

    core_id   ⟨'Algebra/CayleyDickson/Grade/OrAnf.agdai'⟩     52 B, repeated 26,704×
    local_id  26704                                            4 B
    ekey      ⟨'{"c": "Id", "ch": [26703], "i": null, ...}'⟩  68 B, repeated per occurrence
    seq       2419205                                          8 B

1. **The JSON envelope is the bulk.** The payload is `Id` and `26703`; the rest is syntax —
   quoted keys, spaces, and `"i": null, "q": null` written out in full on every row where they
   are absent. Base64 then inflates whatever remains by 4/3.
2. **`core_id` is a 52-byte string repeated once per row.** An `INT` FK to `core_fp` is 4 bytes.
   This has nothing to do with content-addressing — the core's identity is not the term's.
3. **`ekey` is repeated per occurrence in `obs`**, which is exactly what `event` already
   dedupes. `obs` stores the full key where a reference to the dictionary would do.

⚑ **NONE OF THE THREE IS INHERENT TO HASH-CONSING.** The idea is sound and cheap; this
particular *serialization* is what costs. Conflating "content-addressed identity" with "base64
of pretty-printed JSON stored inline on every row" is what makes the design look expensive.

## Options, each with the property it sacrifices

⚑ **(A0) IS THE ONE THE SQLITE FRAMING MAKES VISIBLE, AND IT WAS NOT ON MY LIST.**

**(A0) Stop concatenating — a native composite key.** The blob exists because sqlite needed
one column; postgres does not.

⚑ **AND MY FIRST DRAFT PUT ALL FIVE COLUMNS IN THE KEY, WHICH IS THE BLOB'S SHAPE CARRIED
ACROSS UNEXAMINED** (user, 2026-08-07: *"Things which might be null are not part of the
pkey."*). That rule is not a postgres technicality — it is the definition of identity: a
column that may be absent cannot be part of what makes a row *that* row. I had reasoned about
a NULL sentinel for `idx` when the correct move is to observe that `idx` **is not identity at
all**. It is payload.

⚑ **MEASURED (`--nullity event`, the mode this question required), AND IT IS FAR STRONGER
THAN "SOMETIMES NULL":**

    column        null        empty   distinct   verdict
    ekey             0            0  2,124,390   identity candidate
    ctor_id          0            0      1,830   identity candidate
    qname_pid  2,124,390          0          0   PAYLOAD — null on EVERY row
    idx        2,124,390          0          0   PAYLOAD — null on EVERY row
    lit_id           0    2,124,390          1   CONSTANT — one distinct value

**Three of the five columns carry nothing whatsoever.** `qname_pid` and `idx` are NULL on all
2.1M rows; `lit_id` is `''` on all of them. So `event` is really `(ekey, ctor_id)` — and
`ctor_id` has only **1,830 distinct values** across 2.1M rows.

⚑ **THIS RETIRES THE `head`-LOSSINESS ANALYSIS A THIRD TIME, AND MORE COMPLETELY.**
`EVENT-REFLECTION.md` reasons at length about `idx` being dropped for non-`Var` ctors. On this
corpus `idx` is null EVERYWHERE — there is no `idx` to lose. The whole concern was about a
column that is, in the ingested data, entirely unpopulated. (Whether that is correct — whether
the decoder SHOULD be emitting `idx` for `Var`/`PVar` and is not — is a separate question I
have not answered, and it is now the more interesting one.)

So the composite key is narrower than I proposed:

```sql
event(ctor_id INT NOT NULL, ch INT[] NOT NULL,
      qname_id INT, idx INT, lit_id INT,        -- payload: nullable, OUTSIDE the key
      PRIMARY KEY (ctor_id, ch))
```

- **Keeps all three properties.** Identity is still content-determined — a composite PK IS
  content-addressing, expressed in the engine's own vocabulary rather than encoded around it.
  Order-independence and idempotence come from the PK, not from the encoding.
- **Property 3 becomes trivial** rather than clever: reconstruction is `SELECT *`, not
  base64-decode-then-JSON-parse. The key does not need to *carry* content because the row IS
  the content.
- **The parts become indexable.** `WHERE ctor_id = …` uses an index instead of scanning and
  decoding 6.3M blobs. This is the querying half, and no narrower blob buys it.
- ⚑ **VERIFIED IN POSTGRES, not assumed** — the array-valued component is the part I would
  have hand-waved. `VALUES (1,0,ARRAY[26703]), (1,0,ARRAY[26704]), (1,0,ARRAY[26703]),
  (2,-1,ARRAY[]::int[])` gives **4 rows → 3 distinct keys**: postgres compares `int[]` BY
  VALUE, so the duplicate collapses exactly as the base64 key does. **Hash-consing survives
  natively; the encoding was never what provided it.**
- ⚑ **AND A REAL CONSTRAINT FOUND THE SAME WAY: A PK COLUMN CANNOT BE NULL.** My first probe
  failed with `NotNullViolation` on `idx`, and that is not a test artifact — `"i": null, "q":
  null` is the COMMON case in the data (every leaf row sampled). So (A0) needs either a
  sentinel (`idx INT NOT NULL DEFAULT -1`) or a `UNIQUE` constraint instead of a PK, since
  `UNIQUE` permits NULLs — but then `NULL != NULL` and two identical null-idx events would
  NOT collide, silently breaking property 2. **The sentinel is forced**, and it is the kind of
  detail that turns a clean idea into a migration with a footgun in it.
- **Cost:** the largest migration of the options — every id changes, every join rewrites, and
  the 44 `Column(c, String)` declarations in `query_defs.py` stop being honest.
- ⚑ **AND IT NEEDS THE SAME CANONICALIZER (C) DOES**, for `ctor`/`qname`/`lit` — those are
  already `*_id` term references, so the interning exists; this makes them integers instead of
  base64 strings. Same fork as (C): a canonical function of the text, or arbitrary-but-stored.

**(A) Tighten the serialization, keep the blob.** Drop the JSON envelope for a compact
delimited form (the SPPF's own `"\x00".join(...)` is already this shape) and store `bytea`
rather than base64 TEXT. Keeps all three properties; the id changes, so the store re-interns.
*Estimated 68 → ~20-30 B for typical keys, unmeasured.*
⚑ **Buys width and NOT queryability** — a narrower blob is still a blob, so every
predicate on a part still decodes. Under the sqlite framing this is *optimizing the
workaround* rather than removing it.

**(B) `uuid` digest as the stored PK, full key retained in `event` only.** `obs`/`edge`
reference a 16-byte uuid; `event` keeps the reversible key as a payload column. Keeps 1 and 2
everywhere, keeps 3 *where it is needed* (the dictionary), and pays 16 B in the 6.3M-row
relations instead of 68.
⚑ **This matches what the tiers already ARE** — `event` is the dictionary and `obs` is the
occurrence table, so only `event` needs to carry content.
⚑ **And it introduces a collision assumption** where today there is none. 128-bit over ~2.1M
keys is astronomically safe, but "astronomically safe" is a different kind of claim from
"bijective by construction", and it should be stated rather than absorbed.
⚑ **It also does not help querying** — a digest is maximally opaque. (B) and (A0) are the two
ends: (B) says the key is only an identity and content lives in one place; (A0) says the key
IS the content, structurally. Both are coherent; the blob is neither.

**(C) Normalize `core_id` to an INT FK — AND IT NEEDS A CANONICALIZER.** Orthogonal to the key
question, applies to `obs`/`edge`/`unit_*`, ~12.6M rows at ~48 B each.

⚑ **I WROTE "AN INT FK WOULD BE 4 BYTES" AS IF THE INT WERE FREE** (user, 2026-08-07:
*"you'll need a canonicalizer to get that integer, because you're collapsing structure to a
scalar"*). `core_id` **is** the relpath — `b64('Algebra/CayleyDickson/Grade/OrAnf.agdai')` —
so an integer is not a cheaper spelling of it, it is a *different object* with the structure
projected out. Something must hold the map back, and naming the 4 bytes without naming the
map is the collapse-to-smallest-representable reflex
([[feedback_dont_collapse_to_smallest_representable]],
[[bounded-residue-uniqueness-needs-canonicalizer]] — on ℕ the canonicalizer is `id`; here it
is emphatically not).

⚑ **THE CANONICALIZER IS HALF-BUILT ALREADY, WHICH IS WHY THIS IS CHEAPER THAN IT LOOKS.**
`core_fp(core_id PK, mtime, producer)` is exactly the one-row-per-core table an FK needs — 168
rows, `core_id` as PK. What it lacks is the **scalar side**: no `core_num` column, so the map
exists with nothing to be canonical *to*. The work is one `IDENTITY` column on an existing
table, not a new relation.

⚑ **AND THE ASSIGNMENT MUST NOT BE INSERTION-ORDERED, or (C) silently breaks property 1.** An
`IDENTITY` column hands out numbers in arrival order, so re-ingesting a corpus into a fresh
store yields *different* `core_num` values for the same cores — reintroducing exactly the
order-dependence the base64 key exists to eliminate, one level up. Either the number is
derived from the path (a canonical function, order-free) or it is arbitrary-but-stored and the
store is no longer reproducible from its sources. **This is a real fork and it is not
addressed by "add an FK".**

**(D) Drop `obs`/`edge` rather than shrink them.** Per `EVENT-REFLECTION.md`: `edge` derives
from `obs.ekey`, and `obs` compresses to a positional `ekey[]` per core. If that lands, the
5.3 GB question dissolves and the encoding width matters far less.

## ⚑ THE node↔edge TRANSLATION — `★` AS A REPRESENTATION CHANGE (user, 2026-08-07)

> *"what you want is hodge★; the ability to translate a node between being an identity and
> being a connection between two identities. This would let you take two binary trees and
> capture two views: tree 1's `node(child1, child2)`; tree 2's `edge(parent,child1)`;
> `edge(parent,child2)`. And because they have identical structure, they fold into the same
> table as a hypergraph."*

**The two views already exist as two relations, and they are already the same hypergraph:**

| view | relation | rows | distinct |
|---|---|---|---|
| identity — a node IS a thing | `_node` | 4,775 | 4,775 node_id |
| connection — a node IS an edge pair | `node_child` | 10,366 | 3,001 parent · 4,766 child |

`node_id` and `child_id` draw from the SAME domain, which is what makes them foldable rather
than merely joinable. And 4,775 − 4,766 = **9 nodes that are never a child** — the roots,
falling out of the arithmetic rather than needing a flag.

⚑ **I MEASURED ARITY AS THOUGH IT COULD REFUTE THE TRANSLATION, AND IT CANNOT** (user: *"All
trees can be deconstructed into binary nodes."*). I built `--arity` to ask "is the forest
binary?" and read the 1008-child node as a counterexample to `node(c₁,c₂) ↔ edge(p,c₁);
edge(p,c₂)`. **Arity is a property of the REPRESENTATION, not the structure** — that node is
an unfolded spine, and folding it back loses nothing. The question the numbers answer is what
binarization COSTS:

⚑ **THE FIRST NUMBERS I GAVE FOR THIS WERE FAN-IN, NOT ARITY — corrected below.** Measured
from `edge` (per-core, pre-intern), which is where term arity actually lives:

    observations    6,274,182
    leaves          3,522,609   (56%)
    internal        2,751,573
    arity spread    0:3.52M  1:1.19M  2:397k  3:813k  4:93k  5:76k  6:180k  …  max 22
    BINARIZED       2,751,573 → 4,712,657 internal   (a spine of n−1 per n-ary node)

**1.71×**, not the 2.9× I first quoted. That is the real trade: a storage cost paid to buy a
uniform rule, and smaller than it first appeared because true arity is small (0–3 covers 5.9M
of 6.3M observations) while the apparent 1008 was sharing.

⚑ **AND THE TOWER ALREADY NAMES THIS, WITH THE OBSTRUCTION STATED.** `WitnessTower.Hodge:39`
gives ★ as *"a STRUCTURAL involution on Fin (suc n)"*, k ↦ n−k — a node with 2 children is a
grade-2 cell, its two edges are grade-1 cells, so node↔edge IS Λ¹↔Λ². And
`EdgeComplement.★-edge-is-edge` proves ★ sends edges to edges at Δ³ *because Λ¹ is
self-paired there*.

**But `Hodge:50-53` is explicit that the clean involution is at the LABEL level only:** *"the
cell COUNTS behind the grades (Δ³: 4 vertices, 6 edges, 4 faces, 1 cell) are NOT
label-symmetric — that divergence (6 edges vs 4 faces) is the grading boundary made
manifest."* So ★ does not give a bijection on CELLS, and the fold is not free: binarization is
precisely the price of making the counts line up. **The 2.9× is the count asymmetry, paid.**

⚑ **THE `ord` ANOMALY, CHASED — AND IT CORRECTS MY OWN ARITY NUMBER.** I reported "max arity
1008" from `--arity`, which counts `node_child` ROWS per `node_id`. But `ord` has only **22
distinct values**, in `node_child` AND in the 6.3M-row pre-intern `edge` — so the source
fanout never exceeds 22 and 1008 is not an arity.

The resolution is in the schema: `ix_nc_edge` is `UNIQUE (node_id, ord, child_id)` — unique on
the **triple**, not on `(node_id, ord)`. So **one node may hold many DISTINCT children at the
same ordinal**, and a 1008-row node is ~1008 children spread over ≤22 positions, not a
1008-wide term.

⚑ **THAT IS THE SHARING, VISIBLE AS A COUNT.** `node_child` is the interned edge set: many
per-core parents collapse to one packing, and their children accumulate under it. So a "wide"
node is a heavily-SHARED node, which is the SPPF working — not a wide constructor.

**Consequences, and they matter for the fold:**
- **The binarization cost above is overstated.** It was computed from row-counts-as-arity
  (3,001 → 8,688, 2.9×). The true per-term arity is ≤22, so the real spine cost is smaller —
  **unmeasured, because `--arity` cannot currently distinguish source fanout from interned
  fan-in.** Do not quote the 2.9×.
- **A scheme keyed on `(node_id, ord)` is UNSOUND here** — it is not unique, by construction.
- ⚑ **AND `--arity` IS MEASURING FAN-IN AS THOUGH IT WERE FAN-OUT.** The mode needs to report
  both, from `edge` (per-core, pre-intern) for arity and from `node_child` for sharing. As
  built it answers a question I did not ask and labelled the answer with the question I did.

## What must be measured before choosing

- **(A)'s real width** on the actual key distribution, not one sample — keys with long qnames
  and many children behave differently from `{"c": "Id", "ch": [n]}`.
- **How much of `obs` is `core_id`** — (C) is free and possibly the biggest win, so it should
  be sized before anything that costs a property.
- **Whether (D) makes the rest moot.** The full-population `--edge` check is what settles it.

⚑ **DO NOT PICK FROM THIS DOCUMENT.** (C) is free and (D) may dissolve the question; both
should be settled before trading away a property to buy width.
