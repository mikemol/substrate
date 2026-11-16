# InfCapstone — Substrate.Category.HC.InfCapstone

A capstone is a **directory with a README**, not a module. It ATTESTS a
roster; it does not import one. The former `InfCapstone.agda` was a pure barrel —
prose and imports, no definitions of its own — so the attestation is prose
and the roster is a table. A consumer that wants one of these names binds
it at its OWNER, directly.

```
Substrate.Category.HC.InfCapstone

HC40 — ∞-categorical sub-arc capstone (HC31-HC40) + FULL HC-arc
+ 80-SLICE SPRINT CLOSURE.

===================================================================
80-SLICE SPRINT FULL CLOSURE
===================================================================

UP-arc (UP1-UP40) : UPCategory + Grothendieck topos of UPs.
  Phase 1 : UPArrow + UPMorphism + UPTerm + ArrowOfArrow + FixedPoint
            + UPCategory + Instances + Terminal
  Phase 2 : Site + UPCover + Sieve + Pretopology + axioms
            + ConcreteCovers + Refinement + Saturation
  Phase 3 : UPPresheaf + Yoneda + UPSheaf + MatchingFamily
            + Sheafify + ConstantSheaf + Pullback + InternalHom
  Phase 4 : UPTopos + Ω + TruthValues + InternalLogic
            + Powerset + GeometricMorphism + AdjointPair
            + Substrate-UPTopos + HigherCatAsInternal

HC-arc (HC1-HC40) : 40 distinguished UPArrow objects in UPCategory.
  Coherence sub-arc (HC1-HC10)
  Braided / Symmetric sub-arc (HC11-HC20)
  Double / Fibered sub-arc (HC21-HC30)
  ∞-categorical sub-arc (HC31-HC40)

===================================================================
STRUCTURAL CLOSURE
===================================================================

The substrate's category-of-universal-properties IS a named topos.
Every higher-categorical concept (pentagon, hexagon, braided,
symmetric, Drinfeld center, double cat, fibered cat, simplicial
set, quasi-category, ∞-Yoneda, model category, Quillen adj,
∞-limit) IS a named UPArrow object in the topos.

The user's "favourite category" — the fixed-point object in the
category of arrow categories — is the substrate's UPCategory
exhibited at UP5 (UPArrow²) + UP6 (ι and promote). The
tetrative-metacircularity now has a typed home.

Future arcs add UPs by inhabiting the UPCategory; coherence
diagrams become internal-logic equations; sheaf cohomology
of UPCategory becomes the substrate's structural cohomology
typed natively.
```

∞-categorical sub-arc re-exports

Full HC-arc re-exports
UP-arc re-export

## Roster

| name | owner |
|---|---|
| `SimplicialSet-UP` | `Substrate.Category.HC.SimplicialSet` |
| `DeltaCategory-UP` | `Substrate.Category.HC.DeltaCategory` |
| `HornInclusion-UP` | `Substrate.Category.HC.HornInclusion` |
| `QuasiCategory-UP` | `Substrate.Category.HC.QuasiCategory` |
| `InfYoneda-UP` | `Substrate.Category.HC.InfYoneda` |
| `InfAdjunction-UP` | `Substrate.Category.HC.InfAdjunction` |
| `ModelCategory-UP` | `Substrate.Category.HC.ModelCategory` |
| `QuillenAdjunction-UP` | `Substrate.Category.HC.QuillenAdjunction` |
| `InfLimit-UP` | `Substrate.Category.HC.InfLimit` |
| *(whole module)* | `Substrate.Category.HC.CoherenceCapstone` |
| *(whole module)* | `Substrate.Category.HC.BraidedSymCapstone` |
| *(whole module)* | `Substrate.Category.HC.DoubleFiberedCapstone` |
| *(whole module)* | `Substrate.Category.UniversalProperty.Capstone` |
