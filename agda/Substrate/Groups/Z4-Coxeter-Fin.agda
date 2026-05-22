------------------------------------------------------------------------
-- Substrate.Groups.Z4-Coxeter-Fin
--
-- The Z₄-Coxeter ↔ Fin 4 chain as a thin instance of
-- Substrate.Groups.Coxeter-Fin-Generic, with cover-dispatched
-- payloads (canonical-cover-Z4 + fin-cover).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z4-Coxeter-Fin where

open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Fin.Cover using (fin-cover)
open import Substrate.Foundation.Product using (Σ; _,_; proj₁; proj₂)
open import Substrate.Foundation.Eq using (_≡_; refl)

import Substrate.Groups.Z4-Coxeter as Z₄
open import Substrate.Groups.Coxeter.Word using (Word; []; _∷_)
open import Substrate.Algebra.F2.Linear.FromImages.Permutation
  using (HasOrderPerm)
open import Substrate.Algebra.F2.Linear.FromImages.Permutation.Cycle4
  using (σ₄; σ₄-HasOrderPerm)

------------------------------------------------------------------------
-- Bijection.
------------------------------------------------------------------------

canonical-to-Fin : ∀ {w : Word Z₄.Gen} → Z₄.Canonical w → Fin 4
canonical-to-Fin = Z₄.canonical-cover (λ _ → Fin 4)
  ( zero
  , suc zero
  , suc (suc zero)
  , suc (suc (suc zero))
  )

Fin-to-canonical : Fin 4 → Σ (Word Z₄.Gen) Z₄.Canonical
Fin-to-canonical = fin-cover (λ _ → Σ (Word Z₄.Gen) Z₄.Canonical)
  ( ([] , Z₄.c-ε)
  , ((Z₄.a ∷ []) , Z₄.c-a)
  , ((Z₄.a ∷ Z₄.a ∷ []) , Z₄.c-aa)
  , ((Z₄.a ∷ Z₄.a ∷ Z₄.a ∷ []) , Z₄.c-aaa)
  )

Fin-roundtrip : (i : Fin 4) →
  canonical-to-Fin (proj₂ (Fin-to-canonical i)) ≡ i
Fin-roundtrip = fin-cover
  (λ i → canonical-to-Fin (proj₂ (Fin-to-canonical i)) ≡ i)
  (refl , refl , refl , refl)

canonical-roundtrip : ∀ {w : Word Z₄.Gen} (c : Z₄.Canonical w) →
  Fin-to-canonical (canonical-to-Fin c) ≡ (w , c)
canonical-roundtrip = Z₄.canonical-cover
  (λ {w} c → Fin-to-canonical (canonical-to-Fin c) ≡ (w , c))
  (refl , refl , refl , refl)

------------------------------------------------------------------------
-- Action correspondence.
------------------------------------------------------------------------

action-of-a-is-σ₄ :
  ∀ {w : Word Z₄.Gen} (c : Z₄.Canonical w) →
  canonical-to-Fin (Z₄.insert-canonical Z₄.a c) ≡ σ₄ (canonical-to-Fin c)
action-of-a-is-σ₄ = Z₄.canonical-cover
  (λ c → canonical-to-Fin (Z₄.insert-canonical Z₄.a c) ≡ σ₄ (canonical-to-Fin c))
  (refl , refl , refl , refl)

------------------------------------------------------------------------
-- σ₄-HasOrderPerm via Cycle4 (= cyclic-suc {3}'s structural witness).
------------------------------------------------------------------------

σ₄-HasOrderPerm-from-Z4-Coxeter : HasOrderPerm σ₄ 4
σ₄-HasOrderPerm-from-Z4-Coxeter = σ₄-HasOrderPerm

------------------------------------------------------------------------
-- Apply the generic chain.
------------------------------------------------------------------------

open import Substrate.Groups.Coxeter-Fin-Generic
  4 Z₄.Gen Z₄.a Z₄.Canonical Z₄.insert Z₄.insert-canonical
  canonical-to-Fin Fin-to-canonical σ₄
  action-of-a-is-σ₄ σ₄-HasOrderPerm-from-Z4-Coxeter
  public
