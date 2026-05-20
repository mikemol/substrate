------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim4.ReservedBridge.GaugeTorsor.AsNaturalTransformation
--
-- P3 of the P-arc. The 168-Bijection GaugeTorsor at HodgeDim4 as
-- substrate M2 NaturalTransformation. Closes M-arc residue row.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Level using (Level)

open import Substrate.Category.CategoryOf using (CategoryOf)
open import Substrate.Category.Functor using (Functor)
open import Substrate.Category.NaturalTransformation
  using (NaturalTransformation)

module Substrate.Algebra.F2.HodgeDim4.ReservedBridge.GaugeTorsor.AsNaturalTransformation
  {ℓOC ℓMC ℓOD ℓMD : Level}
  (C : CategoryOf {ℓOC} {ℓMC})
  (D : CategoryOf {ℓOD} {ℓMD})
  (F G : Functor C D)
  (GaugeAction : NaturalTransformation F G)
  where

GaugeTorsor-AsNaturalTransformation : NaturalTransformation F G
GaugeTorsor-AsNaturalTransformation = GaugeAction
