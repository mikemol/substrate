# Type SPPF — motifs & isomorphisms (first pass, 2026-06-03)

Passing every `data`/`record` type through the wedge bottom-up: hash-cons the
structure (sub-type references replaced by the referenced type's structural
hash; recursion/mutual-ref = the SPPF cycle node `⟲`). Isomorphic types collapse
to one node; shared sub-shapes are motifs. Tool: `scripts/type_sppf.py`.

493 types → **411 distinct structural nodes**, **34 isomorphism classes** (≥2
types with identical structure up to sub-iso). The wedge's keep/forget reads
here: the *node hash* is the forget (collapse iso), the *class membership* is
the keep (which types share it).

## Isomorphism classes, triaged

- **Enum-by-arity (the bulk).** Finite types collapse by constructor count:
  - 2-enums (one node): `Bool`, **`F₂`** (≅ Bool — a real math iso),
    `BindingClass`, `EmissionSource`, `Permanence`, `SourceClass`, … (7).
  - 3-enums: **`Unfold`** (my `halt|loop|stop`), `Terminal`, `TenseMarker`,
    `SylowClass`, `HistoryPhase`, `LieGen` (6).
  - a 15-member small-enum/atom class (`Axis`, `Chirality`, `Gen`, `Line`,
    `Point`, `Pairing`, …).
  These are expected and mostly fine — each names a *distinct domain
  distinction* even though the carrier shape is shared. (The motif is "a finite
  set of K atoms"; the content is what the atoms *mean*.)

- **Empty-record / ⊤ class — structurally vacuous.** `TwoNaturalTransformation`,
  `TwoEquivalence`, `Preserves-CountMonoid/Ranking/Shannon/V4` collapse to `⊤`
  (no fields). Two sub-kinds:
  - *nominal tags* used as marker VALUES (`homomorphism-tag = Preserves-V4`) —
    `⊤`-content is correct for a tag (legit).
  - *signature-only stubs* ("substrate names the carrier; user supplies the
    data") — `TwoNaturalTransformation`/`TwoEquivalence`. Same family as the
    UP-topos `*-stated : Set` obligation surface / `SubstrateTopos`, but at the
    record-emptiness level. These are the broadened-vacuity finds: named
    concepts with no structural content. Decide per case (keep as declared
    placeholder, or fill).

- **Term-algebra families — generic-ization candidates.** `CascadeGen ≅ ConjGen
  ≅ LensGen` (single generator) and `CascadeTerm ≅ ConjTerm ≅ LensTerm` (free
  cons-list over it). The term-algebra-bridge construction repeated per domain
  (Cascade/Conj/Lens, and the DFT/Char/Pontryagin `*Gen` siblings). Exactly the
  pattern the generic `Coxeter.Cyclic` collapsed for `Zₙ`; a generic
  `TermAlgebra Gen` would absorb these.

- **Quantity families:** `ConditionalEntropy ≅ JointEntropy ≅ KLDivergence`
  (info-theory measures); `Cascade/Conj/Lens` Term/Gen as above.

## Top structural motifs (recurring field-shapes — the repo's DNA)

| count | shape | reading |
|---|---|---|
| 354 | `Set` | a Set-typed field — obligation slot / type parameter |
| 310 | `⟲` | self/mutual reference — recursive types |
| 214 | `→` | a function field |
| 109 | `→ ≡` | a field that is an EQUATION — a law |
| 80 | `ℕ` | a ℕ-indexed field |
| 62 | `Set₁` | a higher Set field |

So the structural DNA is: **obligations (Set) + recursion (⟲) + functions (→) +
laws (→≡)**. Records of laws over recursive carriers — the algebraic spine.

## Caveats & next

- The skeleton extractor is line-based and drops vars/implicits; **enum and
  empty-record signals are reliable**, deep-structure isos approximate. This is
  the "begin constructing the SPPF" pass.
- Next: (a) refine the parser (telescopes/implicits); (b) generic-ize the
  term-algebra `Gen`/`Term` families (one motif → one generic); (c) decide the
  empty-record signature-stubs (tag vs fill); (d) walk the SPPF *up* the dep
  chain to find cross-LAYER motifs (a foundation shape recurring at a high layer
  = an isomorphism across silos — the north-star bridge, found structurally).
