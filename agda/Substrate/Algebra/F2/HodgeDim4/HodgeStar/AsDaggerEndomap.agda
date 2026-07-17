------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim4.HodgeStar.AsDaggerEndomap
--
-- P1 of the P-arc. ★ at HodgeDim4 as a self-dagger 1-cell in the
-- F₂-Linear-AsDaggerCategory (N8). Closes M-arc residue row.
--
-- Thin projection from Substrate.Category.DaggerCategory.AsNamed:
-- the substrate's "named DaggerCategory" skeleton, with
-- `named-DaggerCategory` renamed to `HodgeStar-AsDaggerEndomap-Carrier`
-- for this specialisation.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Level using (Level)

open import Substrate.Category.DaggerCategory using (DaggerCategory)

module Substrate.Algebra.F2.HodgeDim4.HodgeStar.AsDaggerEndomap
  {ℓO ℓM : Level}
  {Obj : Set ℓO} {Mor : Obj → Obj → Set ℓM}
  (F2L-Dag : DaggerCategory Obj Mor)
  -- The Hodge ★ at HodgeDim4 lives as a morphism in F2L-Dag's base
  -- category. User supplies the specific obj + the (★ † ≡ ★) witness
  -- expressing that ★ is self-adjoint (= self-dagger).
  where

open import Substrate.Category.DaggerCategory.AsNamed F2L-Dag public
  renaming (named-DaggerCategory to HodgeStar-AsDaggerEndomap-Carrier)
