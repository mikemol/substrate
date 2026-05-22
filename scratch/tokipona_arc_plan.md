# Toki Pona small-fragment Agda arc — 10-slice plan

Planned per [[project-linguistic-rosetta-arc]] as the linear-side
sister to the just-landed Lojban arc. Decompose-by-entailment
applied: two costructure shadows + four composition operations +
one entailment, mirroring the Lojban shape but instantiating
**FreeLinearization** ([[project-freelinearization-names-linear-from-images]])
instead of Coxeter Word.

## Linguistic / substrate placement

Per [[project-linguistic-rosetta-arc]]:
- Discrete word-algebra (Lojban, just completed) → Coxeter Word +
  n-ary morphism
- Linear-field semantics (Toki Pona, this arc) → FreeLinearization +
  bilinear composition

The intersection at the universal-property level is the seam
established at Lojban's [L10 AsCCC.Bridge](agda/Substrate/Lojban/AsCCC.agda):
both arcs invoke a "free X over a basis" universal property; this
arc's T10 makes the intersection explicit without forcing
extraction of a shared parent primitive (deferred per [[feedback-coalgebraic-not-consumer-driven]]).

## Costructure shadows

- **`NimiSpace`** — the basis-to-vector lift via FreeLinearization.
  Universal property: any function `Nimi → V` extends uniquely to
  a linear map. Site: Substrate.Category.FreeLinearization.
- **`ModifierBilinear`** — the head-modifier composition primitive
  as a bilinear map `V → V → V`. Universal property: bilinearity
  in each argument plus a defining action on the basis.

## Composition operations

| Op | Signature | Role |
|----|-----------|------|
| `nimi-as-vector` | `Nimi → V` | basis embedding |
| `modify` | `V → V → V` | head-modifier bilinear contraction |
| `predicate` | `V → V → Sem` | subject-`li`-predicate evaluation |
| `with-object` | `V → Sem → Sem` | `e`-attached object |
| `particles` | `Particle → Sem → Sem` | F₂-graded markers (la/o) |

## Entailment claim

```
FreeLinearization(NimiSpace) → BilinearComposition(ModifierBilinear)
  → ∀ (s : TokiSentence). WellTyped s × Linear ⟦ s ⟧
```

Per [[feedback-universal-property-discipline]]: once the two
shadows satisfy their universal properties (T7 and T8), every
sentence's well-typedness and linearity follows mechanically.

## Ten slices

Annealing discipline ([[project-annealing-methodology]]) — one
degree of freedom per slice, typecheck between each, [[feedback-file-size-one-pass-rewrite]]
one Write per file.

### Phase 1 — Shadows (T1-T3)

- **T1 `Substrate.TokiPona.SemanticSpace`** — wrap
  Substrate.Algebra.F2.Vector as the carrier; expose the abstract
  vector-space interface (carrier, plus, zero) for Toki Pona's
  use. Thin module like Lojban's L2 was for Coxeter Word.

- **T2 `Substrate.TokiPona.Nimi`** — vocabulary basis: ~30-40
  nimi data declaration (selected to span the four lexical
  classes: nouns, verbs, modifiers, particles); arity-style class
  classification (content vs particle). Per [[feedback-expose-generator-not-orbit]]
  the nimi ARE the basis; flat enumeration is correct shape.

- **T3 `Substrate.TokiPona.NimiSpace`** — instantiate
  Substrate.Category.FreeLinearization with Nimi as the basis.
  Establishes the `nimi-as-vector : Nimi → Vector m` map and the
  uniqueness of linear extension. Sister to Lojban's L3 Gismu
  bridge but landing on FreeLinearization rather than Word lift.

### Phase 2 — Composition (T4-T6)

- **T4 `Substrate.TokiPona.ModifierBilinear`** — head-modifier
  composition as a bilinear map; defined by action on basis pairs
  via FreeLinearization's universal property at one side, then
  again at the other. Bilinearity is automatic from the universal-
  property factorisation. Real Toki Pona allows arbitrary modifier
  chains; the bilinear primitive composes naturally via
  fold/left-associative chaining (with `pi` as right-grouping marker).

- **T5 `Substrate.TokiPona.TokiSentence`** — the
  `subject li predicate (e object)` structure as a record. Maps
  to the n=2 case of the bilinear primitive: subject vector + verb
  vector → predicate-application; predicate + object vector →
  full bridi. Sister to Lojban's L5 Bridi but with bilinear
  (rather than n-ary) application.

- **T6 `Substrate.TokiPona.Particles`** — the structural markers:
  `li`, `e`, `pi`, `la`, `o`. Contrast with Lojban's L6 Cmavo:
  Lojban cmavo are **semantic wrappers** (post-composers on Sem);
  Toki Pona particles are **structural markers** that drive
  bilinear evaluation order. Each particle carries an F₂-graded
  marker bit; `li`/`e` mark predicate/object boundaries; `pi`
  modulates left/right grouping; `la`/`o` are sentence-prefix
  modifiers.

### Phase 3 — Entailment (T7-T8)

- **T7 `Substrate.TokiPona.Linearity`** — sister to Lojban L7
  Functoriality: states and discharges the coherence laws for
  bilinear composition and particle markers. Bilinearity in each
  argument is the headline obligation. Returns a `TokiLinearity`
  record analogous to `BridiFunctoriality`.

- **T8 `Substrate.TokiPona.LinearAlgebra`** — sister to Lojban L8
  WordAlgebra: discharges the FreeLinearization universal
  property for NimiSpace fully (constructs the
  `FreeLinearization n m` record with `extension-on-basis` and
  `uniqueness` witnesses). The discrete free-monoid and the
  linear extension are **siblings under the same "free X over
  basis"** universal property — surfaced explicitly in T10.

### Phase 4 — Whole + intersection (T9-T10)

- **T9 `Substrate.TokiPona.Fragment`** — top-level re-export plus
  worked example sentences with explicit witnesses:
  - `soweli li suli` (the animal is big)
  - `mi moku e kili` (I eat fruit)
  - `jan pona li toki e ijo` (good people speak about things)
  - `tomo lili pi soweli wawa` (small house of strong animals —
    demonstrates `pi` regrouping)
  - particle-stacking example demonstrating T7 coherence.
  Mirrors Lojban L9's worked-examples structure.

- **T10 `Substrate.TokiPona.AsLinearBridge`** — the categorical
  bridge AND the intersection with Lojban explicitly surfaced.
  - Provides `module Bridge (V) (nimi-as-vector)` mirroring
    Lojban's L10 `module Bridge (State) (gismu-as-opcode)`.
  - States and proves the universal-property analog:
    `program : NimiSequence → V → V` lifts from the basis.
  - Surfaces the intersection: a comment block + a small "shared
    universal property" lemma stating that **both bridges are
    instances of "free X over a basis"** at the universal-property
    level, with Lojban's monoid target and Toki Pona's vector
    target as the two carrier-class instances.
  - Does NOT yet extract the shared parent primitive (deferred per
    [[feedback-coalgebraic-not-consumer-driven]]).

## Substrate primitives engaged

FreeLinearization (the primary site); Substrate.Algebra.F2.Vector
(the carrier); Substrate.Algebra.F2.Linear (the morphism class);
Substrate.Category.Morphism (for `nimi-as-vector`'s preservation
predicate); CCC ([[project-rarc-lambda-vm-recognition]]) at T10
via the bridge module's monoid-instance-as-vector-space-instance
parallel; Cone ([[project-3plus1-is-cone-instance]]) as a
candidate shape for T7's bilinearity statement.

## Deferred (out of arc)

Full ~120-word vocabulary (T2 uses ~30-40); attitudinal/sentence-
type particles (a/ala/anu); compound numerals; the larger nimi
ku ones outside core nimi pu; sub-bridi (sentences as modifiers);
the `o`-vocative semantics beyond marker-only treatment. Per
[[feedback-comments-dont-overclaim]]: real Toki Pona semantics
are richer than F₂-vector polysemy captures; T6 and T7 explicitly
flag this as fragment-only.

## Carrier choice tradeoff

Substrate.Category.FreeLinearization is specialised to F₂. The
fragment uses F₂-vectors as feature-bag semantics for Toki Pona's
polysemy: each nimi activates certain semantic feature-bits;
"modifier" combinations are F₂ pointwise products / sums. Real
distributional Toki Pona semantics would want ℝ-valued vectors;
generalising FreeLinearization to abstract modules is a future
arc, not this one. The F₂ choice keeps the arc substrate-honest
and within the existing primitive's scope.

## Intersection design at T10

The substrate sees three universal-property "free X" sites after
this arc:
1. Free monoid (Lojban LojbanWord, L8 WordAlgebra)
2. Free F₂-module (Toki Pona NimiSpace, T8 LinearAlgebra)
3. CCC opcode algebra (the codec, Substrate.Category.OpcodeAlgebra)

T10 surfaces that these are sister instances of "free X over a
basis" without yet extracting the shared parent. Per
[[feedback-coalgebraic-not-consumer-driven]] the extraction
emerges coalgebraically when downstream sites force it; T10
records the alignment as a candidate for a future "free
construction over basis" primitive.

## Success criteria

1. All ten slices typecheck under `--safe --without-K`.
2. T7 + T8 prove the entailment as stated above.
3. T9 demonstrates ≥4 worked example sentences with witnesses
   (including a `pi`-regrouping example to exercise grouping
   semantics).
4. T10 establishes the linear-side categorical bridge AND
   surfaces the universal-property intersection with Lojban's L10
   as a comment-block + small lemma without forcing extraction
   of a shared parent.
