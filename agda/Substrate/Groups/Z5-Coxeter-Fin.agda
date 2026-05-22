------------------------------------------------------------------------
-- Substrate.Groups.Z5-Coxeter-Fin
--
-- The Z₅-Coxeter ↔ Fin 5 chain as a thin instance of
-- Substrate.Groups.Coxeter-Fin-Generic, with cover-dispatched
-- payloads. canonical-cover-Z5 lives in Substrate.Groups.Z5-Coxeter-Cover
-- (separate file because Z5-Coxeter itself is queued for decomposition).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z5-Coxeter-Fin where

open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Fin.Cover using (fin-cover)
open import Substrate.Foundation.Product using (Σ; _,_; proj₁; proj₂)
open import Substrate.Foundation.Eq using (_≡_; refl)

import Substrate.Groups.Z5-Coxeter as Z₅
open import Substrate.Groups.Z5-Coxeter-Cover using (canonical-cover-Z5)
open import Substrate.Groups.Coxeter.Word using (Word; []; _∷_)
open import Substrate.Algebra.F2.Linear.FromImages.Permutation
  using (HasOrderPerm)
open import Substrate.Algebra.F2.Linear.FromImages.Permutation.Cycle5
  using (σ₅; σ₅-HasOrderPerm)

------------------------------------------------------------------------
-- Bijection.
------------------------------------------------------------------------

canonical-to-Fin : ∀ {w : Word Z₅.Gen} → Z₅.Canonical w → Fin 5
canonical-to-Fin = canonical-cover-Z5 (λ _ → Fin 5)
  ( zero
  , suc zero
  , suc (suc zero)
  , suc (suc (suc zero))
  , suc (suc (suc (suc zero)))
  )

Fin-to-canonical : Fin 5 → Σ (Word Z₅.Gen) Z₅.Canonical
Fin-to-canonical = fin-cover (λ _ → Σ (Word Z₅.Gen) Z₅.Canonical)
  ( ([] , Z₅.c-ε)
  , ((Z₅.a ∷ []) , Z₅.c-a)
  , ((Z₅.a ∷ Z₅.a ∷ []) , Z₅.c-aa)
  , ((Z₅.a ∷ Z₅.a ∷ Z₅.a ∷ []) , Z₅.c-aaa)
  , ((Z₅.a ∷ Z₅.a ∷ Z₅.a ∷ Z₅.a ∷ []) , Z₅.c-aaaa)
  )

Fin-roundtrip : (i : Fin 5) →
  canonical-to-Fin (proj₂ (Fin-to-canonical i)) ≡ i
Fin-roundtrip = fin-cover
  (λ i → canonical-to-Fin (proj₂ (Fin-to-canonical i)) ≡ i)
  (refl , refl , refl , refl , refl)

canonical-roundtrip : ∀ {w : Word Z₅.Gen} (c : Z₅.Canonical w) →
  Fin-to-canonical (canonical-to-Fin c) ≡ (w , c)
canonical-roundtrip = canonical-cover-Z5
  (λ {w} c → Fin-to-canonical (canonical-to-Fin c) ≡ (w , c))
  (refl , refl , refl , refl , refl)

------------------------------------------------------------------------
-- Action correspondence.
------------------------------------------------------------------------

action-of-a-is-σ₅ :
  ∀ {w : Word Z₅.Gen} (c : Z₅.Canonical w) →
  canonical-to-Fin (Z₅.insert-canonical Z₅.a c) ≡ σ₅ (canonical-to-Fin c)
action-of-a-is-σ₅ = canonical-cover-Z5
  (λ c → canonical-to-Fin (Z₅.insert-canonical Z₅.a c) ≡ σ₅ (canonical-to-Fin c))
  (refl , refl , refl , refl , refl)

------------------------------------------------------------------------
-- σ₅-HasOrderPerm via Cycle5 (= cyclic-suc {4}'s structural witness).
------------------------------------------------------------------------

σ₅-HasOrderPerm-from-Z5-Coxeter : HasOrderPerm σ₅ 5
σ₅-HasOrderPerm-from-Z5-Coxeter = σ₅-HasOrderPerm

------------------------------------------------------------------------
-- Apply the generic chain.
------------------------------------------------------------------------

open import Substrate.Groups.Coxeter-Fin-Generic
  5 Z₅.Gen Z₅.a Z₅.Canonical Z₅.insert Z₅.insert-canonical
  canonical-to-Fin Fin-to-canonical σ₅
  action-of-a-is-σ₅ σ₅-HasOrderPerm-from-Z5-Coxeter
  public
