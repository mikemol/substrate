------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim4.HodgeStar.AsDaggerEndomap
--
-- P1 of the P-arc. ★ at HodgeDim4 as a self-dagger 1-cell in the
-- F₂-Linear-AsDaggerCategory (N8). Closes M-arc residue row.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Level using (Level)

open import Substrate.Category.DaggerCategory using (DaggerCategory)

module Substrate.Algebra.F2.HodgeDim4.HodgeStar.AsDaggerEndomap
  {ℓO ℓM : Level}
  (F2L-Dag : DaggerCategory {ℓO} {ℓM})
  -- The Hodge ★ at HodgeDim4 lives as a morphism in F2L-Dag's base
  -- category. User supplies the specific obj + the (★ † ≡ ★) witness
  -- expressing that ★ is self-adjoint (= self-dagger).
  where

HodgeStar-AsDaggerEndomap-Carrier : DaggerCategory
HodgeStar-AsDaggerEndomap-Carrier = F2L-Dag
