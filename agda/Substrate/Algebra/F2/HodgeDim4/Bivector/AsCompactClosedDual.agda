------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim4.Bivector.AsCompactClosedDual
--
-- P6 of the P-arc. Λ²(F₂⁴) as compact-closed-dual object (Bivector
-- as its own dual via complement involution).
--
-- Thin projection from the two AsNamed skeletons (SymmetricMonoidal
-- + DaggerCategory). Each open + rename gives the substrate-named
-- handle for this site.
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

open import Substrate.Category.SymmetricMonoidal.AsNamed F2L-SM public
  renaming (named-SymmetricMonoidal to Bivector-AsCompactClosedDual-SM)

open import Substrate.Category.DaggerCategory.AsNamed F2L-Dag public
  renaming (named-DaggerCategory to Bivector-AsCompactClosedDual-Dag)
