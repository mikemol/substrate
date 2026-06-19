------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim3.HodgeStar.AsGenericHodge  (Ⓗ)
--
-- The HodgeDim3 Hodge ★ : Vector 3 ≅ Vector 3 as an instance of L5
-- [[GenericHodgeStar]] — the n=3, k=1 rung, PARALLEL to HodgeDim4's n=4, k=2
-- instance (HodgeDim4.HodgeStar.AsGenericHodge). Both rungs now witness the ONE
-- generic Λᵏ ≅ Λⁿ⁻ᵏ primitive, built by the ONE generator
-- (`basis-permutation-Linear` of the 2-blade complement) — the parallel-rung
-- "either/or" between Dim3 and Dim4 collapsed into a shared generator with two
-- instances ([[feedback_expose_generator_not_orbit]]).
--
-- At n=3, k=1: LamK = Λ¹(F₂³) = Vector 3, LamNk = Λ²(F₂³) = Vector 3 (dim
-- C(3,2)=3). star = star-inv = apply hodge-star-3 (because ★² = id); section and
-- retraction are both hodge-involution-3. Note k=1 ≠ n−k=2 (cross-grade, unlike
-- Dim4's self-dual middle grade) — the generic accommodates both.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim3.HodgeStar.AsGenericHodge where

open import Substrate.Foundation.Fin.Literals using (₁)

open import Substrate.Algebra.F2.Vector using (Vector)
open import Substrate.Algebra.F2.Linear using (apply)
open import Substrate.Algebra.F2.HodgeDim3.HodgeStar
  using (hodge-star-3; hodge-involution-3)

open import Substrate.Category.GenericHodgeStar
  using (GenericHodgeStar; mkGenericHodgeStar)

------------------------------------------------------------------------
-- HodgeDim3 ★ as a GenericHodgeStar instance (n=3, k=1).
------------------------------------------------------------------------

HodgeStar-Dim3-AsGenericHodge : GenericHodgeStar
HodgeStar-Dim3-AsGenericHodge = mkGenericHodgeStar
  3                                  -- n = 3
  ₁                                  -- k = 1 ∈ Fin 4
  (Vector 3)                         -- LamK = Λ¹(F₂³)
  (Vector 3)                         -- LamNk = Λ²(F₂³) (dim C(3,2) = 3)
  (apply hodge-star-3)               -- star
  (apply hodge-star-3)               -- star-inv = star (involution)
  hodge-involution-3                 -- section
  hodge-involution-3                 -- retraction
