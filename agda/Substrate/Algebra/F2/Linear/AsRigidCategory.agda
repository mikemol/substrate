------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.AsRigidCategory
--
-- P4 of the P-arc. F₂-Linear as rigid (= every object has a dual)
-- monoidal category. Refines N7 SymmetricMonoidal with rigidity data.
--
-- Projects the rigid-category facet from the bundled
-- F2LinearCategoryStructures record.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Level using (Level)

open import Substrate.Algebra.F2.Linear.CategoryStructures
  using (F2LinearCategoryStructures)
open import Substrate.Category.SymmetricMonoidal using (SymmetricMonoidal)

module Substrate.Algebra.F2.Linear.AsRigidCategory
  {ℓO ℓM : Level}
  {Obj : Set ℓO} {Mor : Obj → Obj → Set ℓM}
  (structures : F2LinearCategoryStructures Obj Mor)
  where

F2Linear-AsRigid-SM : SymmetricMonoidal Obj Mor
F2Linear-AsRigid-SM =
  F2LinearCategoryStructures.asRigidCategory structures
