---
name: feedback_def_proof_separation_lever
description: separating definition-modules from proof-modules cuts load-bound memory at the closure level; measured +1 MB (split) vs +23 MB (combined) for a def-only user; abstract/opaque does NOT help (load-bound ≠ check-bound)
metadata: 
  node_type: memory
  type: feedback
  originSessionId: b0f173b0-7c01-42e2-bd3c-cbed23f2d66a
---

User's insight (validated): "I recompile everything I import because I
deserialize everything I import, and a USER of a definition doesn't need
the PROOFS about it." Correct mechanism: Agda caches type-checking in
.agdai (it does NOT re-prove on import), but LOADING a module
DESERIALIZES the full transitive closure — including proof TERMS — into
the ~40× in-memory representation ([[project_oom_load_bound_finding_2026_06]]).
So a def-user pays to deserialize proof closures it never uses.

**Why:** the OOM is load-bound; resident cost tracks CLOSURE SIZE, not
import count (Z2-Coxeter: 8 imports, closure 71, 103 MB). Splitting a
heavy proof into its own module removes that proof's heavy imports from a
def-user's closure entirely.

**Measured (controlled experiment, def-only user, floor 62 MB):**
- import a DefPart (def only)                → 63 MB  (+1)
- import Combined (def + proof + heavy dep)  → 85 MB  (+23)
- import CombinedAbstract (abstract proof, heavy dep present) → 84 MB (+22)
⇒ split = the lever; `abstract`/`opaque`/Prop do NOT help load-bound cost
(they seal UNFOLDING = check-time; the body is still in the closure and
still deserialized). The intuitive fix (abstract) is the wrong one here.

**How to apply:** factor `Foo` into `Foo` (data/record/function defs, lean
imports) + `Foo.Properties` / `Foo.Proofs` (the ≡-laws, heavy imports).
Consumers that USE the definition import `Foo` (tiny closure); only
modules that need the laws import `Foo.Properties`. This ALSO satisfies
the user's touchpoint concern (a def-user keeps ONE narrow import and a
small closure — strictly better than the "import the exact leaf, more
lines" tradeoff). It is the standard stdlib `X` / `X.Properties` split,
and it composes with the one-theorem-per-file policy: defs are the thin
spine, proofs hang off in siblings.

**Top split candidates by Σ(consumers×closure)** (audit
/tmp/split_audit.py logic — def-providing modules, closure≥20, ≥1
consumer; ~33 total): Linguistic.CategoryLaws (10 consumers, cl 43),
Cocycles.V4Signature.S4Iso (8, 52), Linguistic.YonedaEmbedding (8, 44),
TokiPona.LinearAlgebra (7, 21), Linguistic.RosettaTable (6, 41),
Cocycles…Codeword.Live (5, 28). Linguistic.* dominates the list.

**ENFORCEMENT LANDED:** `scripts/check_def_proof_separation.sh` — the
linter. Invariant is provider-scoped: only files declaring a `data`/
`record` may not import a `*.Properties/Laws/Proofs` module (pure-lemma
files importing proofs are fine — they're already proof-side; this is what
stops the rule firing on one-theorem-per-file lemma modules). Name-based
proof color, one grep, exit 1 on violation → pre-commit/CI. Provider-scoped
backlog = 2 (naive "any importer" rule = 35; scoping matters).
BACKLOG CLEARED (both providers split, repo-wide linter = 0 violations):
- `Algebra/Nat/Bezout` → `Bezout` (record, 12.7 KB .agdai) +
  `Bezout/Properties` (base-bezout/EEA fold, drags Nat.Properties);
  def-only user 64 MB vs proof-user 68 MB.
- `Category/Coalgebra/StructuralGCD` → def (Commute record + commute-sym)
  + `StructuralGCD/Properties` (commute-iterate-r, iterate-split-commute,
  HasOrder-compose-commute; drags Nat.Properties *-comm).
Consumer PrimitiveInstances green throughout.

ENFORCEMENT LIVE: `.githooks/pre-commit` (versioned) +
`git config core.hooksPath .githooks`. Proven to pass clean and block a
def-provider→proof-module import.

Linguistic.* closure-audit candidates (CategoryLaws/YonedaEmbedding/…)
CORRECTLY NOT split: zero named-proof imports, zero standalone ≡-lemmas —
single records heavy by transitive CLOSURE not local proofs. The
closure-size audit is NOT the same as the def/proof-split rule; only the
linter (provider imports named proof module) defines a violation.
Policy: scratch/def_proof_separation_policy.md.

**CAVEAT (don't overclaim):** the +1 vs +23 MB is a clean single-hop
demo. Repo-wide relief is NOT additive — closures overlap heavily (the
Foundation spine is in everyone's closure), so splitting one module frees
its UNIQUE proof closure from its def-consumers, not the shared base. The
dominant OOM lever remains (1) don't co-resident the whole closure (shard
the build); def/proof split is the best (3)-class per-module lever and the
one that respects the user's low-touchpoint preference. Validate any
specific split by measuring the consumer's RSS before/after, not by the
proxy.
