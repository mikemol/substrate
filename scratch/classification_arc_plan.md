# Categorical Linguistics Classification arc — 10-slice plan

**Replaces** the surreal-numbers arc plan (`surreal_arc_plan.md`) as
the immediate next arc. Surreals are queued as a later numeric-
carrier arc.

Planned per [[project-language-as-free-construction-classification]]
and [[feedback-coalgebraic-not-consumer-driven]] — with Lojban L8 +
Toki Pona T8 as two sister instances of "Free X over basis," a
third witness instance forces extraction of the parent primitive.
This arc extracts the parent AND populates four cells of the
language-classification lattice.

## Why this arc

Per the user's framework: the substrate's linguistic Rosetta arc
is the first two coordinates of a categorical classification of
languages by which free construction they freely-generate-into.
Lojban occupies the Free monoid cell; Toki Pona occupies the Free
F₂-module cell. **Multiple unexplored cells** the substrate can
fill:

| Cell                  | Witness language     | Substrate site                    |
| --------------------- | -------------------- | --------------------------------- |
| Free monoid           | Lojban (anchor)      | Substrate.Lojban.* (done)         |
| Free F₂-module        | Toki Pona (anchor)   | Substrate.TokiPona.* (done)       |
| **Free relation**     | Kēlen                | Substrate.Category.RuleAction     |
| **Free cyclic group** | Solresol             | Substrate.Groups.FreeCyclic       |
| **Free CCC**          | Lambda calculus      | Substrate.Category.OpcodeAlgebra  |
| **Free Lie algebra**  | (invented)           | Substrate.Category.LieAlgebra     |

This arc instantiates the four marked cells, surfaces the parent
primitive, and produces the cross-language Rosetta-style
classification table that [[user-rosetta-code-contrastive-pedagogy]]
prefers.

## Costructure shadows

- **`FreeOverBasis`** — the abstracted parent primitive: given a
  basis type B, a target structure (algebra of some class), and a
  basis-image map B → carrier, produce the unique structure-
  preserving extension. Generalises Lojban's free-monoid extension
  (L8) and Toki Pona's free-linear extension (T8).
- **`LanguageWitness`** — a record packaging (basis, free-
  construction class, target algebra, image-map) for a given
  language. The classification lattice indexes these.

## Composition operations

| Op | Signature | Role |
|----|-----------|------|
| `free-over-basis` | `(B, AlgebraClass, B → Carrier) → UniqueExtension` | parent constructor |
| `witness-of` | `Language → LanguageWitness` | classify a language |
| `cross-rosetta` | `Witness × Witness → AlignmentTable` | pairwise cross-link |

## Entailment claim

```
LanguageWitness(L₁) × LanguageWitness(L₂) × ... × LanguageWitness(Lₙ)
  ⊢ ∀ pair (Lᵢ, Lⱼ). CrossRosettaAlignment(Lᵢ, Lⱼ)
```

Once each language has a witness in the lattice, pairwise cross-
language Rosetta tables are mechanically generated. The classification
itself is the universal property of the FreeOverBasis parent.

## Ten slices

Annealing discipline ([[project-annealing-methodology]]). Per
[[feedback-minimize-stdlib-deps]]-strengthened: substrate-native
throughout; no `Data.List`, use `Substrate.Groups.Coxeter.Word`.

### Phase 1 — Extract parent primitive (C1-C3)

- **C1 `Substrate.Category.FreeOverBasis`** — the abstracted
  parent primitive: a record bundling (Basis, AlgebraClass laws,
  ImageMap, UniqueExtension, ExtensionOnBasis, Uniqueness).
  Parametrised by an algebra-class predicate (monoid, module,
  CCC, relation, ...). Per [[feedback-categorical-name-first]]
  this names the universal property at the parent level.

- **C2 `Substrate.Lojban.AsFreeOverBasis`** — retrofit Lojban L8
  WordAlgebra as a FreeOverBasis instance with AlgebraClass =
  Monoid. The free-monoid extension IS a FreeOverBasis-Monoid
  extension. Existing L8 proofs are reusable; this slice is the
  thin adapter.

- **C3 `Substrate.TokiPona.AsFreeOverBasis`** — retrofit Toki
  Pona T8 LinearAlgebra similarly as FreeOverBasis with
  AlgebraClass = F₂-Module. Existing T8 proofs reusable;
  adapter only.

### Phase 2 — New witness languages (C4-C7)

- **C4 `Substrate.Solresol.Fragment`** — Solresol as the
  **Free cyclic group** witness. Solresol uses 7 musical notes
  (do, re, mi, fa, sol, la, si) as syllables; word formation is
  ordered note sequences. Falls naturally into Z/7 (single
  octave) or Z/12 (chromatic). Lands on
  [[feedback-prefer-coxeter-backed]] via FreeCyclic; demonstrates
  the cyclic-group cell of the classification.

- **C5 `Substrate.Kelen.Fragment`** — Kēlen as the **Free
  relation** witness. Kēlen has 4 relations (la / nā / pa / jana)
  instead of verbs; sentences are relation-application records.
  Lands on Substrate.Category.RuleAction (or Span). Demonstrates
  the relational cell — fundamentally different from
  function-composition Lojban or feature-pooling Toki Pona.

- **C6 `Substrate.Lambda.Fragment`** — Pure lambda calculus / SKI
  combinators as the **Free CCC** witness. Each combinator
  (S/K/I/B/C) is a generator; combinator reduction is the
  semantics. Lands directly on Substrate.Category.OpcodeAlgebra
  ([[project-rarc-lambda-vm-recognition]]) — the substrate's
  existing lambda-VM IS this free CCC. Demonstrates the
  purest-form cell adjacent to Lojban's CCC-approximation.

- **C7 `Substrate.Invented.LieFragment`** — a substrate-native
  invented mini-language as the **Free Lie algebra** witness.
  Generators are "directions"; the bracket [X, Y] captures
  non-commutative interaction. Lands on
  Substrate.Category.LieAlgebra. Smaller than the other slices —
  primarily demonstrates the cell is reachable. Per
  [[feedback-coalgebraic-not-consumer-driven]] the full invented
  language is a future arc; C7 is the witness sketch.

### Phase 3 — Classification machinery (C8-C9)

- **C8 `Substrate.Linguistic.Classification`** — the lattice
  record. `LanguageWitness` packaging + the catalogue of all six
  witnesses (Lojban, Toki Pona, Solresol, Kēlen, Lambda, Lie-
  fragment). Demonstrates that the classification is a substrate-
  internal structure, not just a comment.

- **C9 `Substrate.Linguistic.RosettaTable`** — the cross-language
  Rosetta-table generator. Given two LanguageWitness instances,
  produce an alignment table (universal property comparison +
  shared/differing structural axes). Per
  [[user-rosetta-code-contrastive-pedagogy]] this IS the
  pedagogical-product surface the user has wanted from the start.

### Phase 4 — Capstone (C10)

- **C10 `Substrate.Linguistic.Capstone`** — top-level re-export +
  smoke tests across all witnesses + a cross-arc Rosetta table
  generated mechanically from C9. Includes a markdown-export
  helper (if substrate-honest) that produces a human-readable
  table from the classification — bridging the formal
  classification to the pedagogical output.

## Substrate primitives engaged

- Substrate.Category.FreeOverBasis (NEW, C1)
- Substrate.Lojban.* + Substrate.TokiPona.* (existing, retrofit)
- Substrate.Groups.FreeCyclic (existing, C4)
- Substrate.Category.RuleAction or Span (existing, C5)
- Substrate.Category.OpcodeAlgebra (existing, C6)
- Substrate.Category.LieAlgebra (existing, C7)
- Substrate.Groups.Coxeter.Word (throughout)

## Deferred (out of arc)

- Full Ithkuil / Láadan / Sona / Aymara fragments
- Free symmetric-monoidal invented language
- Full invented free-Lie-algebra language (only a sketch in C7)
- Mandarin / ASL fragments
- ℝ-valued semantic vectors (per [[feedback-q-over-r-constructive]],
  ℚ if anything)
- The surreals arc (`surreal_arc_plan.md`) — queued

## Success criteria

1. All ten slices typecheck under `--safe --without-K`.
2. C1 defines the FreeOverBasis parent primitive cleanly.
3. C2 + C3 retrofit BOTH child arcs as FreeOverBasis instances
   without changing the original Lojban L8 / Toki Pona T8 modules.
4. C4 + C5 + C6 add three new language witnesses, each at the
   small-fragment grain of the Lojban/Toki Pona arcs.
5. C7 sketches the Lie-algebra-language cell.
6. C8 + C9 produce the classification record + Rosetta-table
   generator.
7. C10 demonstrates the cross-language Rosetta table on a worked
   pair (e.g., Lojban × Toki Pona, Solresol × Lambda).

## Pedagogical payoff

After this arc, the substrate has:
- A categorical classification of natural and constructed languages
  by which free construction they instantiate
- Six language witnesses spread across the lattice
- A mechanical Rosetta-table generator for cross-language pedagogy
- The shared parent primitive surfaced and named

This is the substrate-honest realisation of
[[user-rosetta-code-contrastive-pedagogy]]: the contrast across
the six cells IS the pedagogy. Future arcs can add witnesses to
unfilled cells (Ithkuil, free-SMC, etc.) and the classification
extends mechanically.
