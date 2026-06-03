# Def/Proof Separation — the Costco Policy

**Goal:** one invariant, applied everywhere, mechanically enforced — so the
load-bound memory win ([[feedback_def_proof_separation_lever]]) is a
*maintained property*, not a pile of per-module judgment calls.

## The one rule (the SKU)

> **A module may import a proof module only if it is itself a proof module.**
>
> A *proof module* is any module whose final name component is
> `Properties`, `Laws`, or `Proofs` (e.g. `Foo.Properties`).
> Everything else is a *definition module*.

That's it. No content analysis, no `≡`-counting, no human "is this a
proof?" — the color is **the filename suffix**. (Content classifiers were
tried and rejected: they mislabel record-with-laws definitions like
`Monoid`/`Group` as proofs, and miss indented lemmas. Name-based = zero
false positives, zero diversity.)

### Why this is the right invariant

- **Load-bound mechanism:** importing deserializes the full transitive
  closure, including proof TERMS, at ~40× inflation
  ([[project_oom_load_bound_finding_2026_06]]). The rule guarantees a
  *definition module's closure contains no proof bodies* — so a consumer
  that only needs definitions never deserializes proofs it won't use.
  Measured: def-only import +1 MB vs def+proof +23 MB.
- **Already the convention:** Foundation does this (`Nat`/`Nat.Properties`,
  `Fin`/`Fin.Properties`); `Nat.agda` and `Fin.agda` import **zero**
  `.Properties`. The policy = make the existing pattern universal.
- **Costco property:** one rule, uniform, checkable by `grep`. No
  per-module decisions; maintenance is "does the linter pass," not "should
  this be split."
- **Respects low-touchpoint preference:** a definition-consumer keeps ONE
  import (`Foo`) and gets a small closure — strictly better than
  "import the exact leaf, more lines." Few touchpoints AND small closure.

## The file shape (apply everywhere)

For a subject `Foo`:

```
Foo.agda              -- DEFINITION module: data / record / functions.
                      --   imports: only other DEFINITION modules.
                      --   NEVER imports *.Properties/*.Laws/*.Proofs.
Foo/Properties.agda   -- PROOF module: the ≡-laws about Foo.
   (or Foo.Properties)--   imports Foo + whatever proof machinery it needs.
                      --   may import other *.Properties freely.
```

Consumers:
- "I need to USE Foo" → `import Foo` (cheap, no proof closure).
- "I need to PROVE with Foo's laws" → `import Foo.Properties`.

Composes with the one-theorem-per-file policy: `Foo/Properties/` can itself
be a directory of one-lemma files re-exported by `Foo/Properties.agda`.
Definitions are the thin spine; proofs hang off as siblings.

## Enforcement (the mechanical gate)

A linter script (`scripts/check_def_proof_separation.sh`) flags any
violation:

```sh
# A violation = a NON-proof module that imports a proof module.
grep -rlE 'import Substrate\.[A-Za-z0-9.]*\.(Properties|Laws|Proofs)' \
     --include=*.agda agda/Substrate/ | grep -v _build \
 | grep -vE '(Properties|Laws|Proofs)\.agda$'
# empty output = policy holds.
```

Wire into CI / pre-commit: non-empty output → fail. This is the whole
maintenance burden — one grep, binary pass/fail, no judgment.

## Migration (bounded backlog, NOT required up-front)

Current violations: a finite, enumerable set (def modules importing
`.Properties`). The policy holds **going forward** the moment the linter is
green on NEW files; existing violators are a backlog burned down by
priority = (consumers × proof-closure-shed), highest first.

Top split candidates by Σ(consumers×closure) (audit):
Linguistic.CategoryLaws (10 consumers), Cocycles…S4Iso (8),
Linguistic.YonedaEmbedding (8), TokiPona.LinearAlgebra (7),
Linguistic.RosettaTable (6). The `Linguistic.*` cluster dominates.

### Migration recipe per module `Foo` (mechanical, behaviour-preserving)

1. Create `Foo/Properties.agda`; MOVE every standalone ≡-lemma there.
2. Leave data/record/function definitions in `Foo.agda`; delete now-unused
   heavy imports from `Foo.agda`.
3. `Foo/Properties.agda` imports `Foo` + the heavy machinery.
4. For each consumer: if it used a lemma, add `import Foo.Properties`;
   if it only used definitions, it's now lighter automatically.
5. Verify STANDALONE (`agda --safe --without-K`), never via All.agda
   ([[feedback_never_build_all_agda]]). Confirm consumers still green.

## Caveats (don't overclaim)

- **Not additive across the repo:** closures overlap (the Foundation spine
  is in everyone's closure). Splitting frees a module's *unique* proof
  closure from its def-consumers, not the shared base. This is the best
  per-module (3)-class lever, but the DOMINANT OOM fix remains (1) shard
  the build so the whole closure is never co-resident.
- **`abstract`/`opaque`/`Prop` do NOT substitute:** they seal unfolding
  (check-time), not deserialization (load-time). Must be a real file split.
- **Records with law-fields stay definitions:** a `Group` record whose
  fields are ≡-equations is a DEFINITION module (the laws are part of the
  structure's signature, not standalone theorems). The name-based rule
  handles this correctly; a content classifier would not.

## Refinement that landed (important)

The enforced invariant is scoped to **definition-PROVIDERS** (files
declaring a `data`/`record`), NOT "every module". A pure-lemma file (no
data/record) that imports `.Properties` is fine — it is already on the
proof side and has no datatype to offer a def-only consumer. Scoping to
providers is what keeps the rule from firing on the one-theorem-per-file
lemma modules. Effect on the backlog: the naive "any module importing a
proof module" rule flagged 35; the correct provider-scoped rule flags
**2** (`Algebra/Nat/Bezout`, `Category/Coalgebra/StructuralGCD`).

## Status line

LANDED:
- `scripts/check_def_proof_separation.sh` — the linter (provider-scoped,
  name-based, one grep, exit 1 on violation). Run it in pre-commit/CI.
- First migration done: `Algebra/Nat/Bezout` split into `Bezout` (record
  only, 12.7 KB .agdai) + `Bezout/Properties` (base-bezout + EEA fold,
  24.1 KB, drags Nat.Properties). Consumer PrimitiveInstances green.
  Measured: def-only consumer 64 MB vs proof-consumer 68 MB; def .agdai
  halved. Violations 2 → 1.

BACKLOG CLEARED: both violators split — `Algebra/Nat/Bezout` and
`Category/Coalgebra/StructuralGCD` (each → def module + `.Properties`).
Repo-wide linter: **0 violations**.

ENFORCEMENT LIVE: `.githooks/pre-commit` (versioned) runs the linter;
`git config core.hooksPath .githooks` set. Proven: passes clean tree,
blocks a commit that makes a def-provider import a proof module.

`Linguistic.*` candidates from the closure audit (CategoryLaws,
YonedaEmbedding, …) were investigated and CORRECTLY NOT split: they
import zero named proof modules and have zero standalone ≡-lemmas — they
are single records whose cost is transitive CLOSURE (category machinery),
not separable proof content. Splitting them would be inventing diversity
the rule does not call for. The policy = the linter; the linter is green.

Lever proven mechanically ([[feedback_def_proof_separation_lever]]);
recipe proven end-to-end (Bezout + StructuralGCD); invariant enforced.
