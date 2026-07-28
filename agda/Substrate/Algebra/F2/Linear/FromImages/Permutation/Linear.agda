------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.FromImages.Permutation.Linear
--
-- basis-permutation-Linear: the linear map induced by a basis
-- permutation σ : Fin n → Fin n, with composition + identity laws
-- at the basis level.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Linear.FromImages.Permutation.Linear where

open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Eq using (_≡_; sym; trans; cong)

open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.Linear
open import Substrate.Algebra.F2.Linear.FromImages
  using (linear-from-images; apply-linear-from-images-basis)

------------------------------------------------------------------------
-- basis-permutation-Linear σ = linear-from-images (basis ∘ σ).

basis-permutation-Linear : ∀ {n} → (Fin n → Fin n) → Linear n n
basis-permutation-Linear σ = linear-from-images (λ j → basis (σ j))

apply-basis-permutation-Linear :
  ∀ {n} (σ : Fin n → Fin n) (i : Fin n) →
  apply (basis-permutation-Linear σ) (basis i) ≡ basis (σ i)
apply-basis-permutation-Linear σ i =
  apply-linear-from-images-basis (λ j → basis (σ j)) i

------------------------------------------------------------------------
-- Composition law at the basis level.

basis-permutation-compose-at-basis :
  ∀ {n} (σ τ : Fin n → Fin n) (i : Fin n) →
  apply (basis-permutation-Linear (λ x → σ (τ x))) (basis i)
    ≡ apply (basis-permutation-Linear σ ∘L basis-permutation-Linear τ) (basis i)
basis-permutation-compose-at-basis σ τ i =
  trans (apply-basis-permutation-Linear (λ x → σ (τ x)) i)
  (trans (sym (apply-basis-permutation-Linear σ (τ i)))
         (sym (cong (apply (basis-permutation-Linear σ))
                    (apply-basis-permutation-Linear τ i))))

------------------------------------------------------------------------
-- Identity law at the basis level.

basis-permutation-id-at-basis :
  ∀ {n} (i : Fin n) →
  apply (basis-permutation-Linear (λ x → x)) (basis i) ≡ apply id-L (basis i)
basis-permutation-id-at-basis i =
  apply-basis-permutation-Linear (λ x → x) i
