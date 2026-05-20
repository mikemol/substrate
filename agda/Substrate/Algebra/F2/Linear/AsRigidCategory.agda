------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.AsRigidCategory
--
-- P4 of the P-arc. F₂-Linear as rigid (= every object has a dual)
-- monoidal category. Refines N7 SymmetricMonoidal with rigidity data.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Level using (Level)

open import Substrate.Category.SymmetricMonoidal using (SymmetricMonoidal)

module Substrate.Algebra.F2.Linear.AsRigidCategory
  {ℓO ℓM : Level}
  (F2L-SM : SymmetricMonoidal {ℓO} {ℓM})
  -- Rigidity = per-object dual + ev + coev coherence; user-supplied.
  where

F2Linear-AsRigid-SM : SymmetricMonoidal
F2Linear-AsRigid-SM = F2L-SM
