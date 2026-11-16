------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.FromImages.Permutation.Involution
--
-- For σ : Fin n → Fin n with σ² = id pointwise, the linear map
-- linear-from-images (basis ∘ σ) squares to identity on basis vectors.
-- The order-2 specialization of the order-k pattern.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Linear.FromImages.Permutation.Involution where

open import Substrate.Foundation.Fin.Fin

open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.Linear.CompL
open import Substrate.Algebra.F2.Linear.CompLAssoc
open import Substrate.Algebra.F2.Linear.CompLIdentityL
open import Substrate.Algebra.F2.Linear.CompLIdentityR
open import Substrate.Algebra.F2.Linear.IdL
open import Substrate.Algebra.F2.Linear.Linear
open import Substrate.Algebra.F2.Linear.Preserves
open import Substrate.Algebra.F2.Linear.FromImages
  using (linear-from-images; apply-linear-from-images-basis)
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong

basis-permutation-involution :
  ∀ {n} (σ : Fin n → Fin n) →
  ((i : Fin n) → σ (σ i) ≡ i) →
  (i : Fin n) →
  apply (linear-from-images (λ j → basis (σ j)))
        (apply (linear-from-images (λ j → basis (σ j))) (basis i))
    ≡ basis i
basis-permutation-involution σ σ-invol i =
  trans (cong (apply (linear-from-images (λ j → basis (σ j))))
              (apply-linear-from-images-basis (λ j → basis (σ j)) i))
  (trans (apply-linear-from-images-basis (λ j → basis (σ j)) (σ i))
         (cong basis (σ-invol i)))
