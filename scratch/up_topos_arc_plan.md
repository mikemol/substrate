# Universal-Property Topos arc + Higher-Cat content (80 slices)

Pivots the higher-cat sprint to use the UP-topos as the organising
frame. The category of universal properties + the Grothendieck topos
of sheaves over it lands first; higher-cat content (coherence,
braided/symmetric, double/fibered, ∞-categorical) then lands AS
instances and internal objects in the topos.

## Why this organisation

Per the substrate's [[homology-cohomology-recursion]] principle, the
catalogue of universal properties IS the substrate's *cohomology*.
Making it a category + topos exposes that cohomology as internal
structure. Each higher-cat concept (pentagon, braiding, fibration,
Kan filling) becomes an OBJECT in the topos rather than a scattered
record.

## UP-arc (40 slices) — category of UPs + Grothendieck topos

### Phase 1: UP-category foundations (UP1-UP10)
- UP1  UniversalProperty record (meta-object)
- UP2  UPMorphism record (refinement / transfer)
- UP3  Identity + composition of UPMorphisms
- UP4  UPMorphism category laws
- UP5  UPCategory record (the full meta-category)
- UP6  Concrete UP-objects (Free, Limit, Adjunction, ...) as instances
- UP7  UPMorphism examples (FreeOverBasis → FreeLinearization)
- UP8  UPCategory as sub-2-category of Cat
- UP9  Terminal UP-object (trivial)
- UP10 Phase-1 capstone

### Phase 2: Site structure on UPCategory (UP11-UP20)
- UP11 Site record (category + coverage)
- UP12 Coverage on UPCategory
- UP13 Sieve record
- UP14 Cover-stable sieve closure
- UP15 Pretopology on UPCategory
- UP16 Coverage axioms (stability, transitivity)
- UP17 Concrete covers
- UP18 Refinement of covers
- UP19 Saturation
- UP20 Site capstone

### Phase 3: Presheaves and sheaves (UP21-UP30)
- UP21 Presheaf on UPCategory
- UP22 Yoneda embedding よ : UPCategory → PSh
- UP23 Sheaf record (presheaf + descent)
- UP24 Matching family
- UP25 Sheafification signature
- UP26 Constant sheaves
- UP27 Pullback of sheaves
- UP28 Internal hom in PSh
- UP29 Substrate sheaf examples
- UP30 Sheaves capstone

### Phase 4: Grothendieck topos (UP31-UP40)
- UP31 Topos record
- UP32 Subobject classifier Ω
- UP33 Truth values for UP-membership
- UP34 Internal logic surface
- UP35 Powerset object
- UP36 Geometric morphism record
- UP37 Direct/inverse image pair
- UP38 Substrate UP-topos
- UP39 Higher-cat content as internal objects
- UP40 UP-arc capstone

## HC-arc (40 slices) — higher-cat content reorganised under UP-topos

### Sub-arc A: Coherence (HC1-HC10)
- HC1  Coherence as morphism-equality in UP-topos
- HC2  Pentagon as UP-instance
- HC3  Triangle as UP-instance
- HC4  Hexagon as UP-instance
- HC5  Interchange law (LanguageMorphism) full proof
- HC6  Adjunction triangle identities (full)
- HC7  2-Equivalence triangle coherence
- HC8  Mac Lane coherence statement
- HC9  F₂-Linear coherence package
- HC10 Coherence sub-arc capstone

### Sub-arc B: Braided / Symmetric (HC11-HC20)
- HC11 BraidedMonoidalCategory record
- HC12 Hexagon coherence
- HC13 BraidedFunctor
- HC14 SymmetricMonoidalCategory
- HC15 Coxeter braid as braiding instance
- HC16 Eckmann-Hilton
- HC17 F₂-Linear as SymMonoidal full coherence
- HC18 Cartesian-monoidal
- HC19 Drinfeld center signature
- HC20 BS sub-arc capstone

### Sub-arc C: Double / Fibered (HC21-HC30)
- HC21 DoubleCategory record
- HC22 Square composition
- HC23 Strict double category
- HC24 Span double category
- HC25 FiberedCategory record
- HC26 CartesianMorphism
- HC27 Grothendieck construction
- HC28 IndexedCategory + Indexed≃Fibered
- HC29 DescentTree as fibered
- HC30 DF sub-arc capstone

### Sub-arc D: ∞-categorical (HC31-HC40)
- HC31 SimplicialSet record
- HC32 Δ category
- HC33 Horn inclusion
- HC34 Kan complex + quasi-category
- HC35 ∞-Yoneda statement
- HC36 Adjunction in quasi-category
- HC37 Model category record
- HC38 Quillen adjunction
- HC39 ∞-categorical limit
- HC40 T2 sub-arc capstone

## Discipline

- All under `--safe --without-K`.
- Substrate-native; minimise stdlib deps.
- Signature-bearing where full proofs exceed slice budget.
- One Write per file.
- Each capstone re-exports + summarises closure.

## Closure narrative

After 80 slices: the substrate's structural cohomology is a NAMED
TOPOS. Every universal property is an object, every refinement a
morphism, every coherence diagram an internal-logic equation. Higher
categorical content lives AS internal structure of this topos rather
than as scattered records. Future arcs add new UPs by inhabiting the
category, not by adding ad-hoc record files.
