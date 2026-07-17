------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.AsCompactClosed
--
-- O1 of the O-arc. F₂-Linear with joint SM + † coherence (= rigid
-- symmetric monoidal dagger category, "compact closed" in Selinger).
--
-- Per [[grothendieck-coherence-rule]]: the joint compatibility of
-- N7 SymmetricMonoidal + N8 DaggerCategory was an EMERGENT orphan
-- after the N-arc; O1 names it structurally as the bundle of both
-- + a compact-closed-coherence obligation (user-supplied).
--
-- Projects both the symmetric-monoidal AND dagger-category facets
-- from the bundled F2LinearCategoryStructures record. The compact-
-- closed coherence (= rigid + ⊗-† compatibility) remains the user
-- obligation; substrate names the SM + † pair as the joint structure.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Level using (Level)

open import Substrate.Algebra.F2.Linear.CategoryStructures
  using (F2LinearCategoryStructures)
open import Substrate.Category.DaggerCategory using (DaggerCategory)
open import Substrate.Category.SymmetricMonoidal using (SymmetricMonoidal)

module Substrate.Algebra.F2.Linear.AsCompactClosed
  {ℓO ℓM : Level}
  {Obj : Set ℓO} {Mor : Obj → Obj → Set ℓM}
  (structures : F2LinearCategoryStructures Obj Mor)
  where

F2Linear-AsCompactClosed-SM : SymmetricMonoidal Obj Mor
F2Linear-AsCompactClosed-SM =
  F2LinearCategoryStructures.asSymmetricMonoidal structures

F2Linear-AsCompactClosed-Dagger : DaggerCategory Obj Mor
F2Linear-AsCompactClosed-Dagger =
  F2LinearCategoryStructures.asDaggerCategory structures
