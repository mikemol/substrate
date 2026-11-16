---
name: named-categorical-structure-skeletons
description: "Substrate-naming AsX modules absorb via per-structure AsNamed skeletons (DaggerCategory.AsNamed, SymmetricMonoidal.AsNamed, Monad.DerivedCategoryOf) + per-site renaming projections."
metadata: 
  node_type: memory
  type: project
  originSessionId: c0656668-5986-42eb-b0c2-6df0ba57346b
---

When several substrate-naming modules take the shape "take a categorical
structure X, give it a substrate-specific name", the 1:N cone witness
absorbs them into one parametric skeleton per structure type X:

  - `Substrate.Category.DaggerCategory.AsNamed` — projects to
    HodgeStar.AsDaggerEndomap, F2.Linear.Bijection.AsDagger, …
  - `Substrate.Category.SymmetricMonoidal.AsNamed` — projects to
    HodgeStar.AsSelfDualMorphism (SM half),
    Bivector.AsCompactClosedDual (SM half), …
  - `Substrate.Category.Monad.DerivedCategoryOf` — projects to
    KleisliCategory, EilenbergMooreCategory.

Each leg becomes a 2-line `open import …AsNamed X public; renaming`
projection. Multi-structure sites (HodgeStar.AsSelfDualMorphism with
both SM + Dagger naming) open BOTH skeletons without needing a separate
combined skeleton — the projections compose naturally.

**Why:** the script (low threshold + heavy anonymization + typed
holes) surfaces these "named X" twins as 0.66-0.79 similarity pairs.
The absorption shifts duplicated content into the skeleton and makes
future "named X at site Y" specialisations a one-line addition.

**How to apply:** when [[skeleton-as-pullback]] fires on a 1:N cone
where N legs all wrap the same structure type X with different
substrate names, build `Substrate.Category.X.AsNamed` once and make
each leg a renaming projection. Multi-structure sites open all
relevant `*.AsNamed` skeletons.

**Pending candidates** (similar shape, ≥0.6 similarity post-this-refactor):
  - HodgeStar.AsNaturalTransformation ↔ GaugeTorsor/AsNaturalTransformation
    (would need NaturalTransformation.AsNamed)
  - LaxFunctor ↔ PseudoFunctor (both empty-record placeholders)
  - The F2.Linear.As* family already absorbed via [[skeleton-as-pullback]]
    using the F2LinearCategoryStructures record (different shape — a
    bundled record with projections per facet).
