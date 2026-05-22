# Yoneda Lift of the Language Classification — 10-slice plan

Planned per [[project-language-as-free-construction-classification]]
and the C10 capstone's flagged future work. The classification arc
produced **objects** (LanguageWitness) + **alignment data**
(RosettaEntry); this arc lifts those into a proper **category** with
composition + identity + the Yoneda embedding.

## Why this arc

The peer-review of the classification arc framed it precisely:

> Objects: LanguageWitness B A
> Morphisms: structural alignments / Rosetta tables
> Structure: inherited from underlying algebra classes
>
> This is the Yoneda move again: study objects via how they relate
> to each other.

C10 of the classification arc completed the OBJECTS layer (six
witnesses + classification). This arc adds the MORPHISMS layer +
the categorical structure (composition, identity, laws) + the
Yoneda embedding that lets us study languages via their hom-sets.

Per [[feedback-coalgebraic-not-consumer-driven]]: the classification
arc's RosettaEntry was already a morphism-shaped record. This arc
extracts the categorical content (composition, identity, Yoneda)
that was implicit in the RosettaEntry shape.

Per [[feedback-categorical-name-first]]: the construction is named
exactly — the **category of languages** in the substrate's own
formalisation, with the Yoneda lemma as the headline universal
property.

## Costructure shadows

- **`LanguageMorphism`** — a typed morphism between two
  LanguageWitness instances. A pair `(basis-map, carrier-map)` with
  η-coherence: carrier-map ∘ η(L₁) = η(L₂) ∘ basis-map. The minimal
  categorical morphism; cell-specific structure-preservation
  (monoid/module/CCC/relation-homomorphism) is per-cell richer.

- **`CategoryOfLanguages`** — the categorical bundle: objects +
  morphisms + composition + identity + associativity + identity-
  laws. Builds on Substrate.Category infrastructure.

## Composition operations

| Op | Signature | Role |
|----|-----------|------|
| `id-L` | `(L : LanguageWitness) → LanguageMorphism L L` | identity |
| `_∘L_` | `LanguageMorphism L₂ L₃ → LanguageMorphism L₁ L₂ → LanguageMorphism L₁ L₃` | composition |
| `Hom-L` | `LanguageWitness → LanguageWitness → Set` | hom-set |
| `よ` | `LanguageWitness → (LanguageWitness → Set)` | Yoneda embedding |

## Entailment claim

```
LanguageMorphism × Composition × Identity × CategoryLaws
  ⊢ ∀ (L : LanguageWitness). よ(L) determines L up to iso
```

The Yoneda lemma in the substrate-internal language-category: the
contravariant hom-functor よ(L) = Hom(-, L) is a fully faithful
embedding into Presheaf(Lang); equivalently, L is determined by
its incoming morphisms from every other language.

For the 10-slice fragment, the FULL Yoneda lemma may be too heavy;
the arc states the embedding + faithfulness, and defers naturality
+ the iso-recovery proof.

## Ten slices

Annealing discipline ([[project-annealing-methodology]]). Per
[[feedback-minimize-stdlib-deps]]-strengthened: substrate-native
throughout (no Data.List, prefer Substrate.Groups.Coxeter.Word).
Per [[feedback-file-size-one-pass-rewrite]]: one Write per file.

### Phase 1 — Morphisms (Y1-Y3)

- **Y1 `Substrate.Linguistic.Morphism`** — the LanguageMorphism
  record: pair `(basis-map : Basis L₁ → Basis L₂, carrier-map :
  FreeCarrier L₁ → FreeCarrier L₂)` plus η-coherence witness.
  Sister-shape to Substrate.Category.Morphism (the substrate's
  generic morphism primitive); this one specialises to
  LanguageWitness instances.

- **Y2 `Substrate.Linguistic.IdMorphism`** — identity morphism for
  each LanguageWitness. basis-map = id, carrier-map = id, coherence
  by refl. Six instances corresponding to the six witnesses; one
  generic construction parametric in the witness.

- **Y3 `Substrate.Linguistic.Compose`** — composition of morphisms.
  Given f : L₁→L₂ and g : L₂→L₃, produce g ∘L f : L₁→L₃ with
  composed basis-maps + carrier-maps + derived η-coherence.

### Phase 2 — Category laws (Y4-Y5)

- **Y4 `Substrate.Linguistic.CategoryLaws`** — associativity + left/
  right identity laws for the morphism category. Proven by refl /
  cong on the underlying basis-map and carrier-map associativity /
  identity properties.

- **Y5 `Substrate.Linguistic.CategoryOfLanguages`** — bundle the
  morphism layer into a CategoryOfLanguages record: objects =
  LanguageWitness, hom = LanguageMorphism, composition, identity,
  laws. Connects to Substrate.Category.CategoryOf if that primitive
  is generic enough; otherwise defines a stand-alone record.

### Phase 3 — Functoriality (Y6-Y7)

- **Y6 `Substrate.Linguistic.ClassFunctor`** — the
  `class : LanguageWitness → FreeConstructionClass` map is a
  FUNCTOR from CategoryOfLanguages to a discrete category on
  FreeConstructionClass (any morphism preserves the cell, or
  changes it). This is the "classification as a functor"
  observation: the cell-classification respects the category
  structure.

- **Y7 `Substrate.Linguistic.HomFunctor`** — `Hom(L, -) :
  LanguageWitness → Set` as a covariant functor. Given a fixed L,
  collect all morphisms FROM L TO X as a Set-valued function of X.
  The contravariant counterpart `Hom(-, L)` is the Yoneda
  embedding's value.

### Phase 4 — Yoneda + capstone (Y8-Y10)

- **Y8 `Substrate.Linguistic.YonedaEmbedding`** — the contravariant
  Yoneda embedding よ : Lang → Presheaf(Lang). For each L, よ(L) is
  the presheaf X ↦ Hom(X, L). Fully faithful (claimed; proof at
  Y9). Connects to Substrate.Category.YonedaEmbedding if that
  primitive is generic enough.

- **Y9 `Substrate.Linguistic.YonedaLemma`** — substrate-internal
  statement of the Yoneda lemma for languages: a morphism between
  presheaves よ(L) → よ(M) corresponds bijectively to a morphism
  L → M. Proven for the substrate's language category (may need
  per-pair pattern-matching for the fragment; full Yoneda is
  classical-strength). Worked examples demonstrating the
  bijection for selected pairs (Lojban↔Toki Pona, Kelen↔Lambda).

- **Y10 `Substrate.Linguistic.YonedaCapstone`** — re-export +
  smoke tests + the headline statement:
  "Each language is determined by its hom-set into all others."
  Concrete worked example: Lojban determined by its morphisms into
  the other five witnesses, demonstrated via a worked Yoneda-
  reconstruction lemma.

## Substrate primitives engaged

- Substrate.Category.Morphism (Y1 inherits the structure)
- Substrate.Category.CategoryOf (Y5 plugs into if compatible)
- Substrate.Category.NaturalTransformation (Y8 uses)
- Substrate.Category.PresheafCategory (Y8 uses)
- Substrate.Category.YonedaEmbedding (Y8 plugs into if compatible)
- The six language witnesses (Y1-Y9 operate on)

## Deferred (out of arc)

- Full natural-transformation Yoneda lemma proof (Y9 states + worked
  examples; full proof per-cell deferred per
  [[feedback-coalgebraic-not-consumer-driven]]).
- Cell-specific structure-preservation in morphisms (monoid-hom for
  Free-monoid pairs, linear-map for Free-F2-module pairs, etc.) —
  Y1's minimal η-coherence is the BASE morphism; richer per-cell
  preservation is a follow-up arc.
- 2-categorical lift: morphisms between morphisms (the
  bicategorification mentioned earlier in the conversation).

## Connection to prior arcs

- The Lojban + Toki Pona arcs gave the first two anchors.
- The Classification arc surfaced the parent primitive + six
  witnesses + RosettaEntry alignments.
- This arc gives the **category structure** + Yoneda embedding —
  the Yoneda move per the peer review's framing.

After this arc, the substrate has a **proper category of languages
classified by free construction**, with composition / identity /
Yoneda — the deepest categorical realisation of the linguistic
Rosetta theme so far.

## Success criteria

1. All ten slices typecheck under `--safe --without-K`.
2. Y4 proves associativity + identity laws for the morphism
   category.
3. Y5 bundles the CategoryOfLanguages record.
4. Y8 defines the Yoneda embedding for languages.
5. Y9 demonstrates the Yoneda-lemma bijection on at least one
   worked pair (e.g., Lojban-self with Yoneda-reconstruction).
6. Y10 provides the headline statement + worked example.

## Future arcs (post Yoneda lift)

- The Surreal-numbers arc (queued in `surreal_arc_plan.md`).
- The invented-language arcs (full free-SMC, full free-Lie).
- Bicategorical lift of the language category.
- A pedagogical-export arc that ingests the CategoryOfLanguages +
  Rosetta tables and produces markdown/HTML pages — the
  [[user-rosetta-code-contrastive-pedagogy]] tooling layer.
