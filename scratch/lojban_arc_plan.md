# Lojban small-fragment Agda arc — 10-slice plan

Planned per [[project-linguistic-rosetta-arc]]. Decompose-by-entailment applied:
two costructure shadows + four composition operations + one entailment.

## Costructure shadows

- **`Selbri n`** — typed n-ary morphism / Span. Universal property: n-ary
  application + composition law. Site: [[project-substrate-primitives-index]]
  n-ary morphism / Span infrastructure.
- **`LojbanWord`** — Coxeter Word over gismu alphabet with rafsi-merge
  relations. Universal property: word-algebra normal form. Site:
  [[feedback-prefer-coxeter-backed]] / [[feedback-roll-our-own-via-word-algebra]].

## Composition operations

| Op | Signature | Role |
|----|-----------|------|
| `gismu` | `Gismu → Σ n. Selbri n × LojbanWord` | basis assignment |
| `lujvo-merge` | `LojbanWord → LojbanWord → LojbanWord` | Coxeter composition |
| `apply` | `Selbri n → Vec Sumti n → Bridi` | n-ary morphism application |
| `cmavo` | `ScopeOp → Selbri n → Selbri n` | functorial wrapper |

## Entailment claim

```
NAryMorphism(Selbri) → CoxeterWordAlgebra(LojbanWord)
  → ∀ (e : LojbanFragment). WellTyped e × Functorial ⟦ e ⟧
```

Once the two shadows satisfy their universal properties, every fragment
expression's well-typedness and functorial semantics follows mechanically
via standard application/composition lemmas (cf.
[[feedback-universal-property-discipline]]).

## Ten slices

Annealing discipline ([[project-annealing-methodology]]) — one degree of
freedom per slice, typecheck between each. Per
[[feedback-file-size-one-pass-rewrite]] each slice lands in one Write.

### Phase 1 — Shadows (L1-L3)

- **L1 `Substrate.Lojban.PlaceStructure`** — `Selbri n` as n-ary morphism
  shadow: arity types (`ℕ`), application combinator, composition law.
  Reusable cross-arc (Toki Pona's head-modifier discrete skeleton).

- **L2 `Substrate.Lojban.Word`** — `LojbanWord` as Coxeter Word adapter
  over a small gismu alphabet; rafsi-merge as Coxeter relations.
  Reuses existing `Coxeter.{Word,Core,ListPresentation}`.

- **L3 `Substrate.Lojban.Gismu`** — small vocabulary table (20-30 gismu)
  with arities: `klama` (5-place), `prenu` (1-place), `tavla` (4-place),
  etc. Bridge `Gismu → Σ n. Selbri n × LojbanWord`. The vocabulary IS
  the basis per [[feedback-expose-generator-not-orbit]].

### Phase 2 — Composition (L4-L6)

- **L4 `Substrate.Lojban.Lujvo`** — lujvo construction via Coxeter Word
  composition with rafsi-merge; arity inheritance from head gismu.
  Example: `prenu-klama → bevri`-like compounds (rafsi-composed).

- **L5 `Substrate.Lojban.Bridi`** — sentence application: `Selbri n × Vec
  Sumti n → Bridi`. The n-ary morphism application IS the bridi
  construction. Includes minimal Sumti type (Names + bound vars).

- **L6 `Substrate.Lojban.Cmavo`** — small scope/tense set: `PU` (tense
  markers `pu`/`ca`/`ba`), `NA` (negation), `KU` (terminator) as
  functorial wrappers on `Selbri n` / `Bridi`. Defer SE/TE/VE / attitudinals.

### Phase 3 — Entailment (L7-L8)

- **L7 `Substrate.Lojban.Functoriality`** — Grothendieck coherence
  ([[feedback-grothendieck-coherence-rule]]): place-structure + cmavo
  composition respects composition. Proves the entailment claim above.

- **L8 `Substrate.Lojban.WordAlgebra`** — lujvo composition is a strict
  monoid homomorphism into the semantic interpretation. Closes the
  word-algebra universal-property obligation.

### Phase 4 — Whole + bridge (L9-L10)

- **L9 `Substrate.Lojban.Fragment`** — top-level re-export; worked
  examples with explicit well-typed witnesses (`mi klama le zarci`,
  `mi pu tavla do`); smoke tests via `_≡_` against expected normal forms.

- **L10 `Substrate.Lojban.AsCCC`** — bridge to
  [[project-rarc-lambda-vm-recognition]] CCC: Lojban fragment as
  objects+morphisms in existing CCC infrastructure. **This is the
  natural slot where Toki Pona's FreeLinearization side will eventually
  intersect via universal properties** (per [[project-linguistic-rosetta-arc]]) —
  not forced now, but the seam is at L10 by construction.

## Substrate primitives engaged

n-ary morphism / Span; Coxeter Word (Core, ListPresentation,
Normalization); CCC ([[project-rarc-lambda-vm-recognition]]); Functoriality /
composition; Grothendieck coherence; possibly Cone ([[project-3plus1-is-cone-instance]])
at L7 for the entailment's limit shape. Pre-engages FreeLinearization
([[project-freelinearization-names-linear-from-images]]) at L10 via
the bridge slot, but does not invoke it.

## Deferred (out of arc)

SE/TE/VE conversion, attitudinals (UI cmavo), MEX (mathematical
expressions), phonotactics, proper-name particles (LA), numerals.
These are surface features without substrate-primitive alignment in
the small fragment; revisit only after the core layer lands.

## Success criteria

1. All ten slices typecheck under `--safe`.
2. L7 + L8 prove the entailment as stated above.
3. L9 demonstrates ≥3 worked example sentences with witnesses.
4. L10 establishes the CCC bridge so the Toki Pona FreeLinearization
   intersection has a typed seam to land at later.
