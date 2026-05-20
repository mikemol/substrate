------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim4.HodgeStar.AsSelfDualMorphism
--
-- P5 of the P-arc. Hodge ★ at HodgeDim4 as a self-dual 1-cell in
-- F₂-Linear (= ★ : V → V with V ≅ V* via ★ as the witness).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Level using (Level)

open import Substrate.Category.SymmetricMonoidal using (SymmetricMonoidal)
open import Substrate.Category.DaggerCategory using (DaggerCategory)

module Substrate.Algebra.F2.HodgeDim4.HodgeStar.AsSelfDualMorphism
  {ℓO ℓM : Level}
  (F2L-SM : SymmetricMonoidal {ℓO} {ℓM})
  (F2L-Dag : DaggerCategory {ℓO} {ℓM})
  where

HodgeStar-AsSelfDualMorphism-SM : SymmetricMonoidal
HodgeStar-AsSelfDualMorphism-SM = F2L-SM

HodgeStar-AsSelfDualMorphism-Dag : DaggerCategory
HodgeStar-AsSelfDualMorphism-Dag = F2L-Dag
