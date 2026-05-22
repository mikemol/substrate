------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim4.HodgeStar.AsSelfDualMorphism
--
-- P5 of the P-arc. Hodge ★ at HodgeDim4 as a self-dual 1-cell in
-- F₂-Linear (= ★ : V → V with V ≅ V* via ★ as the witness).
--
-- Thin projection from the two AsNamed skeletons (SymmetricMonoidal
-- + DaggerCategory). Each open + rename gives the substrate-named
-- handle for this site.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Level using (Level)

open import Substrate.Category.SymmetricMonoidal using (SymmetricMonoidal)
open import Substrate.Category.DaggerCategory using (DaggerCategory)

module Substrate.Algebra.F2.HodgeDim4.HodgeStar.AsSelfDualMorphism
  {ℓO ℓM : Level}
  (F2L-SM : SymmetricMonoidal {ℓO} {ℓM})
  (F2L-Dag : DaggerCategory {ℓO} {ℓM})
  where

open import Substrate.Category.SymmetricMonoidal.AsNamed F2L-SM public
  renaming (named-SymmetricMonoidal to HodgeStar-AsSelfDualMorphism-SM)

open import Substrate.Category.DaggerCategory.AsNamed F2L-Dag public
  renaming (named-DaggerCategory to HodgeStar-AsSelfDualMorphism-Dag)
