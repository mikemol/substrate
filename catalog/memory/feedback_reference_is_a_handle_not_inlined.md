---
name: feedback_reference_is_a_handle_not_inlined
description: "a cross-reference in a graded/recursive key must be a BOUNDED content-addressed HANDLE (id into the existing interner), never the referent's inlined key — reuse jea_pyalg.Intern/orbit_node, don't hand-roll or inline"
metadata:
  node_type: memory
  type: feedback
  originSessionId: d35bc15a-16b8-42c5-aad1-20966c9a9f8e
---

When a graded / recursive / fixpoint key references ANOTHER item (a def referencing a companion def, a node
referencing a child), the reference must be a **bounded content-addressed HANDLE** — an id into the existing
interner — NOT the referent's full inlined key.

**Why (the concrete failure, 2026-07-13):** `graded_orbit.orbit_key`'s `body_bag` embedded
`orbit_key_of(ref)` = the referent's FULL `(tkey, bkey)` nested tuple, recursing to depth 3. At full-corpus
scale (~14k defs) this is ≈ fanout³ per key → the process ballooned to **29 GB VDATA**, overwhelmed zram,
spilled to the disk swapfile, and MAJFLT-thrashed (never completed). The fix — make a reference the referent's
bounded **int handle** from `jea_pyalg.Intern` (children-as-ids: `IR(kind='orbit', op=<structural sig>,
children=<sorted ref-handles>)`) — cut peak RSS **29 GB → 597 MB** and runtime **25 min(killed) → 60 s**, with
identical collapse semantics (twins share a handle, divergence gets distinct handles). `a = recon(orbit-rep,
residue)` — the rep is a handle, the residue is the wedge remainder (see [[adjunction-is-the-wedge-residue-counit]]).

**The reuse-search trigger fires on KEY / STORE REPRESENTATION, not just on new data/def/lemma/module.**
Before choosing how a key/index/store represents cross-references, name the existing content-addressing center
it specialises: `jea_pyalg.Intern` (hash-cons, `children` are ids — `jea_pyalg.py:44`), the SPPF packing
(`pack`/`opk` = `base64(head ‖ child-syms)`), `orbit_node`+`orbit_child` (`child_id` refs). The substrate
already content-addresses graded items by reference; re-materialising the full expansion (Python nested
tuples, `_b64(repr(k))`, or a hand-rolled `hashlib` digest) **duplicates and defeats** it. I nearly reinvented
it twice in one session (inlined tuples, then almost a `hashlib` hash) — both are the same miss.

**The same trap at the PERSISTENCE layer (2026-07-13, ⟡orbit-def-by-reference).** Persisting the graded-orbit
DAG, I gave each node a "stable Merkle id" `_b64(kind ‖ op ‖ sorted(child stable-ids))` — but **base64 is NOT
fixed-size**, so each id's length grew with its children's ids, and up the DAG it reproduced the fanout³
blowup ONE LEVEL UP (the persisted id). The 2 GiB `membudget` cgroup cap OOM-killed it — the diagnostic
working as designed. Fix = the interner's own **int handle** (`str(gid)`), a bounded within-build-consistent
id (`graded_orbit.dump_graded`; consumers only compare graded_key for equality within one build, so cross-run
stability was a property NObody needed). **A content-address MUST be fixed-size**: the interner's handle, or a
fixed-width digest — never `base64`/`repr` of recursive content (it grows). A recursive Merkle needs a
fixed-size hash of the children, not their concatenated ids. If cross-run stability is ever genuinely needed,
THAT is when a fixed-size digest earns its place — not for within-build grouping.

**How to apply:** a reference in a key OR a persisted id ⇒ a bounded, FIXED-SIZE handle (the interner's int
id / `orbit_child` edge / a fixed-width digest), never the inlined referent and never a growing
`base64`/`repr` of recursive content. Depth-3 self-collapse ([[feedback_bound_recursion_at_self_collapse_depth]])
bounds the fixpoint DEPTH; fixed-size handles bound the id/value SIZE. **Verify boundedness by measuring peak
RSS on the FULL corpus under `membudget` (the cap turns a size regression into a clean diagnostic), not a
4-item test** (the tiny test masks fanout³). Relates to [[jea-pysim-clusters]], [[wedge-projection]],
[[split-idempotent-apex]], [[feedback_sql_declarative_over_materialized_enumeration]], [[feedback_always_membudget]].
