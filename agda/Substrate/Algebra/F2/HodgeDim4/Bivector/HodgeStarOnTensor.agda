------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim4.Bivector.HodgeStarOnTensor
--
-- The Hodge ★ involution lifted to the AntisymmetricTensor subtype.
--
-- Bivector-level hodge-star is the index-reversal involution
-- (`basis-permutation-Linear complement`). At the TensorProduct
-- level, the corresponding operation swaps the antisymmetric subspace
-- positions in complementary pairs: (0,1)↔(2,3), (0,2)↔(1,3),
-- (0,3)↔(1,2).
--
-- This module lifts hodge-star to AntisymmetricTensor 4 by routing
-- through the Bivector ↔ AntisymTensor bridge:
--
--   hodge-star-on-tensor T
--     = antisymmetric-from-bivector
--         (apply hodge-star (tensor-to-bivector (tensor T)))
--
-- After this module, downstream HodgeDim4 work can apply Hodge ★ at
-- the TensorProduct level without first descending to Bivector.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim4.Bivector.HodgeStarOnTensor where

open import Data.Fin using (Fin; zero; suc)
open import Data.Vec using ([]; _∷_; lookup)
open import Relation.Binary.PropositionalEquality using (_≡_; refl)

open import Substrate.Algebra.F2
open import Substrate.Algebra.F2.Linear using (apply)
open import Substrate.Algebra.F2.HodgeDim4.Bivector using (Bivector)
open import Substrate.Algebra.F2.HodgeDim4.Bivector.TensorProductBridge
  using (bivector-to-tensor; tensor-to-bivector)
open import Substrate.Algebra.F2.HodgeDim4.HodgeStar using (hodge-star)
open import Substrate.Category.TensorProduct.AntisymmetricTensor
  using (AntisymmetricTensor; tensor)

------------------------------------------------------------------------
-- N-1: bivector-to-tensor produces antisymmetric tensors.
--
-- Two structural witnesses: symmetric (T(i,j) = T(j,i)) and
-- diag-zero (T(i,i) = 𝟘). Both hold by construction of
-- bivector-to-tensor (the 4×4 matrix is hardcoded to be symmetric
-- with zero diagonal).
--
-- Proofs are case-by-case on (i, j): 16 refl positions for symmetric
-- (the symmetric matrix structure makes every lookup pair equal); 4
-- refl positions for diag-zero.
------------------------------------------------------------------------

bivector-to-tensor-symmetric :
  (v : Bivector) →
  (i j : Fin 4) →
  lookup (lookup (bivector-to-tensor v) i) j
    ≡ lookup (lookup (bivector-to-tensor v) j) i
bivector-to-tensor-symmetric (a ∷ b ∷ c ∷ d ∷ e ∷ f ∷ []) zero                            zero                            = refl
bivector-to-tensor-symmetric (a ∷ b ∷ c ∷ d ∷ e ∷ f ∷ []) zero                            (suc zero)                      = refl
bivector-to-tensor-symmetric (a ∷ b ∷ c ∷ d ∷ e ∷ f ∷ []) zero                            (suc (suc zero))                = refl
bivector-to-tensor-symmetric (a ∷ b ∷ c ∷ d ∷ e ∷ f ∷ []) zero                            (suc (suc (suc zero)))          = refl
bivector-to-tensor-symmetric (a ∷ b ∷ c ∷ d ∷ e ∷ f ∷ []) (suc zero)                      zero                            = refl
bivector-to-tensor-symmetric (a ∷ b ∷ c ∷ d ∷ e ∷ f ∷ []) (suc zero)                      (suc zero)                      = refl
bivector-to-tensor-symmetric (a ∷ b ∷ c ∷ d ∷ e ∷ f ∷ []) (suc zero)                      (suc (suc zero))                = refl
bivector-to-tensor-symmetric (a ∷ b ∷ c ∷ d ∷ e ∷ f ∷ []) (suc zero)                      (suc (suc (suc zero)))          = refl
bivector-to-tensor-symmetric (a ∷ b ∷ c ∷ d ∷ e ∷ f ∷ []) (suc (suc zero))                zero                            = refl
bivector-to-tensor-symmetric (a ∷ b ∷ c ∷ d ∷ e ∷ f ∷ []) (suc (suc zero))                (suc zero)                      = refl
bivector-to-tensor-symmetric (a ∷ b ∷ c ∷ d ∷ e ∷ f ∷ []) (suc (suc zero))                (suc (suc zero))                = refl
bivector-to-tensor-symmetric (a ∷ b ∷ c ∷ d ∷ e ∷ f ∷ []) (suc (suc zero))                (suc (suc (suc zero)))          = refl
bivector-to-tensor-symmetric (a ∷ b ∷ c ∷ d ∷ e ∷ f ∷ []) (suc (suc (suc zero)))          zero                            = refl
bivector-to-tensor-symmetric (a ∷ b ∷ c ∷ d ∷ e ∷ f ∷ []) (suc (suc (suc zero)))          (suc zero)                      = refl
bivector-to-tensor-symmetric (a ∷ b ∷ c ∷ d ∷ e ∷ f ∷ []) (suc (suc (suc zero)))          (suc (suc zero))                = refl
bivector-to-tensor-symmetric (a ∷ b ∷ c ∷ d ∷ e ∷ f ∷ []) (suc (suc (suc zero)))          (suc (suc (suc zero)))          = refl

bivector-to-tensor-diag-zero :
  (v : Bivector) →
  (i : Fin 4) →
  lookup (lookup (bivector-to-tensor v) i) i ≡ 𝟘
bivector-to-tensor-diag-zero (a ∷ b ∷ c ∷ d ∷ e ∷ f ∷ []) zero                            = refl
bivector-to-tensor-diag-zero (a ∷ b ∷ c ∷ d ∷ e ∷ f ∷ []) (suc zero)                      = refl
bivector-to-tensor-diag-zero (a ∷ b ∷ c ∷ d ∷ e ∷ f ∷ []) (suc (suc zero))                = refl
bivector-to-tensor-diag-zero (a ∷ b ∷ c ∷ d ∷ e ∷ f ∷ []) (suc (suc (suc zero)))          = refl

------------------------------------------------------------------------
-- N-2: antisymmetric-from-bivector — package the antisymmetry
-- witnesses into the subtype.
--
-- For any Bivector v, bivector-to-tensor v lives in the antisymmetric
-- subspace; this constructor surfaces that fact as an
-- AntisymmetricTensor 4.
------------------------------------------------------------------------

antisymmetric-from-bivector : Bivector → AntisymmetricTensor 4
antisymmetric-from-bivector v = record
  { tensor    = bivector-to-tensor v
  ; symmetric = bivector-to-tensor-symmetric v
  ; diag-zero = bivector-to-tensor-diag-zero v
  }

------------------------------------------------------------------------
-- N-3: hodge-star-on-tensor — Hodge ★ lifted to AntisymmetricTensor 4.
--
-- Route through the bridge: descend to Bivector, apply hodge-star,
-- ascend back to AntisymmetricTensor 4. The output is automatically
-- antisymmetric (bivector-to-tensor's image always is).
------------------------------------------------------------------------

hodge-star-on-tensor : AntisymmetricTensor 4 → AntisymmetricTensor 4
hodge-star-on-tensor T =
  antisymmetric-from-bivector (apply hodge-star (tensor-to-bivector (tensor T)))

------------------------------------------------------------------------
-- N-4: Capstone — Hodge ★ at the TensorProduct level.
--
-- After this slice:
--
--   * antisymmetric-from-bivector : Bivector → AntisymmetricTensor 4
--     packages any Bivector as an antisymmetric tensor.
--
--   * hodge-star-on-tensor : AntisymmetricTensor 4 → AntisymmetricTensor 4
--     applies Hodge ★ at the TensorProduct level.
--
-- Substrate-wide consequence: any HodgeDim4 work that operated on
-- Bivector can now be re-expressed at the AntisymTensor level via
-- this lift. The complement-position involution is now first-class
-- at the TensorProduct level.
--
-- Per [[project-torsion-element-universal]]: hodge-star-on-tensor
-- inherits hodge-star's order-2 structure via the bridge round-trips.
-- The HasOrder witness at the TensorProduct level lifts cleanly
-- through tensor-bivector-roundtrip + bivector-tensor-roundtrip.
--
-- Deferred follow-ons:
--
--   * **HasOrder-hodge-star-on-tensor**: lift HasOrder via the
--     bridge round-trips. Requires the AntisymTensor inner_~_ /
--     iterate equation to chase through the conversions.
--
--   * **Direct definition without bridge routing**: hodge-star-on-
--     tensor could be defined as a transformation of the underlying
--     tensor directly (swap rows i↔complement i and reshape). The
--     bridge-routed definition is the structural reading;
--     the direct definition would be a definitional / efficiency
--     optimisation.
------------------------------------------------------------------------
