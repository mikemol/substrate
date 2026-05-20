------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim4.Bivector.AsCompactClosedDual
--
-- P6 of the P-arc. Λ²(F₂⁴) as compact-closed-dual object (Bivector
-- as its own dual via complement involution).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Level using (Level)

open import Substrate.Category.SymmetricMonoidal using (SymmetricMonoidal)
open import Substrate.Category.DaggerCategory using (DaggerCategory)

module Substrate.Algebra.F2.HodgeDim4.Bivector.AsCompactClosedDual
  {ℓO ℓM : Level}
  (F2L-SM : SymmetricMonoidal {ℓO} {ℓM})
  (F2L-Dag : DaggerCategory {ℓO} {ℓM})
  where

Bivector-AsCompactClosedDual-SM : SymmetricMonoidal
Bivector-AsCompactClosedDual-SM = F2L-SM

Bivector-AsCompactClosedDual-Dag : DaggerCategory
Bivector-AsCompactClosedDual-Dag = F2L-Dag
