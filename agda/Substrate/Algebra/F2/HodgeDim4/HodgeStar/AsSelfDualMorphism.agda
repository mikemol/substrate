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
  {Obj : Set ℓO} {Mor : Obj → Obj → Set ℓM}
  (F2L-SM : SymmetricMonoidal Obj Mor)
  (F2L-Dag : DaggerCategory Obj Mor)
  where

open import Substrate.Category.DaggerCategory.AsNamed F2L-Dag
  renaming (named-DaggerCategory to HodgeStar-AsSelfDualMorphism-Dag)

open import Substrate.Category.SymmetricMonoidal.AsNamed F2L-SM
  renaming (named-SymmetricMonoidal to HodgeStar-AsSelfDualMorphism-SM)


