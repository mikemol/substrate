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

open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Literals using (₁; ₂; ₃; ₄)
open import Substrate.Foundation.Fin.Cover using (fin-cover; fin-cover-2⁴)
open import Substrate.Foundation.Vec using ([]; _∷_; lookup)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Product using (_×_; _,_)
open import Substrate.Groups.Coxeter.CanonicalCover using (n-refls)

------------------------------------------------------------------------
-- F₂² ↔ Fin 4 conversion. V₄ ≅ F₂² makes Fin 4 the binary fan-out
-- (i₁, i₂) ∈ Fin 2 × Fin 2 ↔ i ∈ Fin 4. Used to dispatch the 16-cell
-- 4×4 Cayley as a 2⁴ binary tree via `fin-cover-2⁴`.
------------------------------------------------------------------------

private
  to-fin4 : Fin 2 → Fin 2 → Fin 4
  to-fin4 zero       zero       = zero
  to-fin4 zero       ₁ = suc zero
  to-fin4 ₁ zero       = suc ₁
  to-fin4 ₁ ₁ = suc ₂

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

-- Cayley enumeration collapsed via compositional cover from
-- Substrate.Foundation.Fin.Cover: the 16-case Fin 4 × Fin 4 table
-- IS the orbit of two fin4-cover applications composed via the
-- product structure (the atlas-of-charts view, per the user's
-- observation: the 4 blocks of 4 lines in any 4×4-cover are
-- screaming for the tensor decomposition). Refl tokens are nested
-- into 4-tuples-of-4-tuples matching the row structure; each refl's
-- {x} unifies independently with its position's predicate.
-- Binary fan-out dispatch: Fin 4 × Fin 4 = (Fin 2 × Fin 2) × (Fin 2 ×
-- Fin 2) = F₂⁴. The 16-cell Cayley reads as four nested binary
-- decisions via `fin-cover-2⁴`. Each `refl` literal carries its own
-- implicit {x} (heterogeneous cells per (i₁, i₂, j₁, j₂) bit pattern).
bivector-to-tensor-symmetric-bin :
  (v : Bivector) →
  (i₁ i₂ j₁ j₂ : Fin 2) →
  lookup (lookup (bivector-to-tensor v) (to-fin4 i₁ i₂)) (to-fin4 j₁ j₂)
    ≡ lookup (lookup (bivector-to-tensor v) (to-fin4 j₁ j₂)) (to-fin4 i₁ i₂)
bivector-to-tensor-symmetric-bin (a ∷ b ∷ c ∷ d ∷ e ∷ f ∷ []) =
  fin-cover-2⁴ _
    ((((refl , refl) , (refl , refl)) , ((refl , refl) , (refl , refl))) ,
     (((refl , refl) , (refl , refl)) , ((refl , refl) , (refl , refl))))

-- Original Fin 4 × Fin 4 surface, derived by composing the binary
-- dispatch with the bit-decomposition of each Fin 4 index.
bivector-to-tensor-symmetric :
  (v : Bivector) →
  (i j : Fin 4) →
  lookup (lookup (bivector-to-tensor v) i) j
    ≡ lookup (lookup (bivector-to-tensor v) j) i
bivector-to-tensor-symmetric v i j =
  fin4-fin4-route i j
  where
    -- Bit-decompose i, j ∈ Fin 4 to (Fin 2 × Fin 2) × (Fin 2 × Fin 2)
    -- and dispatch via the binary cover.
    fin4-fin4-route : (i j : Fin 4) →
      lookup (lookup (bivector-to-tensor v) i) j
        ≡ lookup (lookup (bivector-to-tensor v) j) i
    fin4-fin4-route zero                     zero                     = bivector-to-tensor-symmetric-bin v zero zero zero zero
    fin4-fin4-route zero                     ₁               = bivector-to-tensor-symmetric-bin v zero zero zero ₁
    fin4-fin4-route zero                     ₂         = bivector-to-tensor-symmetric-bin v zero zero ₁ zero
    fin4-fin4-route zero                     ₃   = bivector-to-tensor-symmetric-bin v zero zero ₁ ₁
    fin4-fin4-route ₁               zero                     = bivector-to-tensor-symmetric-bin v zero ₁ zero zero
    fin4-fin4-route ₁               ₁               = bivector-to-tensor-symmetric-bin v zero ₁ zero ₁
    fin4-fin4-route ₁               ₂         = bivector-to-tensor-symmetric-bin v zero ₁ ₁ zero
    fin4-fin4-route ₁               ₃   = bivector-to-tensor-symmetric-bin v zero ₁ ₁ ₁
    fin4-fin4-route ₂         zero                     = bivector-to-tensor-symmetric-bin v ₁ zero zero zero
    fin4-fin4-route ₂         ₁               = bivector-to-tensor-symmetric-bin v ₁ zero zero ₁
    fin4-fin4-route ₂         ₂         = bivector-to-tensor-symmetric-bin v ₁ zero ₁ zero
    fin4-fin4-route ₂         ₃   = bivector-to-tensor-symmetric-bin v ₁ zero ₁ ₁
    fin4-fin4-route ₃   zero                     = bivector-to-tensor-symmetric-bin v ₁ ₁ zero zero
    fin4-fin4-route ₃   ₁               = bivector-to-tensor-symmetric-bin v ₁ ₁ zero ₁
    fin4-fin4-route ₃   ₂         = bivector-to-tensor-symmetric-bin v ₁ ₁ ₁ zero
    fin4-fin4-route ₃   ₃   = bivector-to-tensor-symmetric-bin v ₁ ₁ ₁ ₁

-- diag-zero is the UNIFORM case (every cell reduces to 𝟘 ≡ 𝟘), so
-- the polymorphic `4-refls` from CanonicalCover applies directly:
-- one polymorphic {x = 𝟘} unifies across all 4 positions.
bivector-to-tensor-diag-zero :
  (v : Bivector) →
  (i : Fin 4) →
  lookup (lookup (bivector-to-tensor v) i) i ≡ 𝟘
bivector-to-tensor-diag-zero (a ∷ b ∷ c ∷ d ∷ e ∷ f ∷ []) =
  fin-cover _ (n-refls 4)

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
