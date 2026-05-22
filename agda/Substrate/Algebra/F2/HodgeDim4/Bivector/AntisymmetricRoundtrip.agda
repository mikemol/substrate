------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim4.Bivector.AntisymmetricRoundtrip
--
-- The reverse-direction round-trip for the Bivector ↔ TensorProduct
-- bridge at dim 4: `bivector-to-tensor (tensor-to-bivector T) ≡ T`
-- whenever T is in the antisymmetric subspace of TensorProduct 4 4.
--
-- Closes the deferred gap from Substrate.Algebra.F2.HodgeDim4.
-- Bivector.TensorProductBridge: the forward round-trip
-- (tensor-to-bivector ∘ bivector-to-tensor ≡ id) is refl after
-- pattern-matching on Bivector; the reverse requires the input to BE
-- antisymmetric, which is what the AntisymmetricTensor subtype now
-- carries.
--
-- Per [[feedback-categorical-name-first]]: the pair forms an
-- isomorphism on the antisymmetric subspace, not on all of
-- TensorProduct 4 4. The subtype packaging makes this restriction
-- explicit.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim4.Bivector.AntisymmetricRoundtrip where

open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Vec using (Vec; []; _∷_; lookup)
open import Substrate.Foundation.Eq
  using (_≡_; refl; cong; cong₂)
  renaming (sym to ≡-sym)

open import Substrate.Algebra.F2
open import Substrate.Algebra.F2.HodgeDim4.Bivector using (Bivector)
open import Substrate.Algebra.F2.HodgeDim4.Bivector.TensorProductBridge
  using (bivector-to-tensor; tensor-to-bivector)
open import Substrate.Category.TensorProduct using (TensorProduct)
open import Substrate.Category.TensorProduct.AntisymmetricTensor
  using (AntisymmetricTensor; tensor; symmetric; diag-zero)

------------------------------------------------------------------------
-- Generic ≡-from-lookup for Vec of any element type.
--
-- The substrate's existing `≡-from-lookup` is specialised to
-- `Vector n = Vec F₂ n`. The proof body is structural and works for
-- any element type. Local helper here to avoid a stdlib dependency
-- on Data.Vec.Properties.
------------------------------------------------------------------------

private
  ≡-from-lookup-A :
    ∀ {ℓ} {A : Set ℓ} {n} (u v : Vec A n) →
    ((i : Fin n) → lookup u i ≡ lookup v i) →
    u ≡ v
  ≡-from-lookup-A []      []      _  = refl
  ≡-from-lookup-A (x ∷ u) (y ∷ v) eq =
    cong₂ _∷_ (eq zero) (≡-from-lookup-A u v (λ i → eq (suc i)))

------------------------------------------------------------------------
-- N-1: tensor-bivector-roundtrip-raw — reverse round-trip with the
-- antisymmetry hypotheses as explicit arguments.
--
-- For any T : TensorProduct 4 4 satisfying symmetric + diagonal-zero,
--   bivector-to-tensor (tensor-to-bivector T) ≡ T
--
-- Proof via double ≡-from-lookup at each (i, j) ∈ Fin 4 × Fin 4. The
-- 16 positions split into:
--   * 4 diagonal positions: LHS = 𝟘, RHS = T(i,i); use sym (dz i).
--   * 6 upper-triangular: LHS = T(i,j) by definition of tensor-to-
--     bivector and bivector-to-tensor; use refl.
--   * 6 lower-triangular: LHS = T(j,i) (the upper-triangular partner);
--     use symmetric T j i to bridge.
------------------------------------------------------------------------

tensor-bivector-roundtrip-raw :
  (T : TensorProduct 4 4) →
  ((i j : Fin 4) → lookup (lookup T i) j ≡ lookup (lookup T j) i) →
  ((i : Fin 4) → lookup (lookup T i) i ≡ 𝟘) →
  bivector-to-tensor (tensor-to-bivector T) ≡ T
tensor-bivector-roundtrip-raw T sym dz =
  ≡-from-lookup-A _ T (λ i →
    ≡-from-lookup-A _ (lookup T i) (λ j → entry-eq i j))
  where
    entry-eq : (i j : Fin 4) →
      lookup (lookup (bivector-to-tensor (tensor-to-bivector T)) i) j
        ≡ lookup (lookup T i) j
    -- Row 0: (𝟘 ∷ a ∷ b ∷ c ∷ [])  where a=T(0,1), b=T(0,2), c=T(0,3)
    entry-eq zero                            zero                            = ≡-sym (dz zero)
    entry-eq zero                            (suc zero)                      = refl
    entry-eq zero                            (suc (suc zero))                = refl
    entry-eq zero                            (suc (suc (suc zero)))          = refl
    -- Row 1: (a ∷ 𝟘 ∷ d ∷ e ∷ [])  where d=T(1,2), e=T(1,3)
    entry-eq (suc zero)                      zero                            = sym zero (suc zero)
    entry-eq (suc zero)                      (suc zero)                      = ≡-sym (dz (suc zero))
    entry-eq (suc zero)                      (suc (suc zero))                = refl
    entry-eq (suc zero)                      (suc (suc (suc zero)))          = refl
    -- Row 2: (b ∷ d ∷ 𝟘 ∷ f ∷ [])  where f=T(2,3)
    entry-eq (suc (suc zero))                zero                            = sym zero (suc (suc zero))
    entry-eq (suc (suc zero))                (suc zero)                      = sym (suc zero) (suc (suc zero))
    entry-eq (suc (suc zero))                (suc (suc zero))                = ≡-sym (dz (suc (suc zero)))
    entry-eq (suc (suc zero))                (suc (suc (suc zero)))          = refl
    -- Row 3: (c ∷ e ∷ f ∷ 𝟘 ∷ [])
    entry-eq (suc (suc (suc zero)))          zero                            = sym zero (suc (suc (suc zero)))
    entry-eq (suc (suc (suc zero)))          (suc zero)                      = sym (suc zero) (suc (suc (suc zero)))
    entry-eq (suc (suc (suc zero)))          (suc (suc zero))                = sym (suc (suc zero)) (suc (suc (suc zero)))
    entry-eq (suc (suc (suc zero)))          (suc (suc (suc zero)))          = ≡-sym (dz (suc (suc (suc zero))))

------------------------------------------------------------------------
-- N-2: tensor-bivector-roundtrip — subtype version.
--
-- The AntisymmetricTensor subtype carries the symmetry + diagonal-
-- zero witnesses by construction; the round-trip restated at the
-- subtype is a one-line wrapper around the raw version.
------------------------------------------------------------------------

tensor-bivector-roundtrip :
  (T : AntisymmetricTensor 4) →
  bivector-to-tensor (tensor-to-bivector (tensor T)) ≡ tensor T
tensor-bivector-roundtrip T =
  tensor-bivector-roundtrip-raw (tensor T) (symmetric T) (diag-zero T)

------------------------------------------------------------------------
-- N-3: Capstone — reverse round-trip closes.
--
-- After this slice, the Bivector ↔ TensorProduct 4 4 bridge is a
-- BIJECTION on the antisymmetric subspace:
--
--   bivector-tensor-roundtrip : tensor-to-bivector ∘ bivector-to-tensor ≡ id
--   tensor-bivector-roundtrip : bivector-to-tensor ∘ tensor-to-bivector ≡ id
--     (on AntisymmetricTensor 4 inputs)
--
-- The two directions package together as the substrate's first
-- iso-BCSquare instance (slice 10).
--
-- Per [[project-3plus1-parity-universal]]: the 6-dim Bivector at F₂⁴
-- IS the 6-dim antisymmetric subspace of TensorProduct 4 4 — same
-- categorical object via two presentations. The bridge is the
-- identification.
------------------------------------------------------------------------
