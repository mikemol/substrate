------------------------------------------------------------------------
-- Substrate.Groups.Z7-Coxeter-Fin
--
-- The Z₇-Coxeter ↔ Fin 7 chain as a thin instance of
-- Substrate.Groups.Coxeter-Fin-Generic, with cover-dispatched
-- payloads. canonical-cover lives in Substrate.Groups.Z7-Coxeter-Cover
-- (separate file because Z7-Coxeter itself is queued for decomposition).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z7-Coxeter-Fin where

open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Fin.Cover using (fin-cover)
open import Substrate.Foundation.Product using (Σ; _,_; proj₁; proj₂)
open import Substrate.Foundation.Eq using (_≡_; refl)

import Substrate.Groups.Z7-Coxeter as Z₇
open import Substrate.Groups.Z7-Coxeter-Cover using (canonical-cover)
open import Substrate.Groups.Coxeter.Word using (Word; []; _∷_)
open import Substrate.Algebra.F2.Linear.FromImages.Permutation
  using (HasOrderPerm)
open import Substrate.Algebra.F2.Linear.FromImages.Permutation.Cycle7
  using (σ₇; σ₇-HasOrderPerm)

------------------------------------------------------------------------
-- Bijection: cover-dispatched on both sides.
------------------------------------------------------------------------

canonical-to-Fin : ∀ {w : Word Z₇.Gen} → Z₇.Canonical w → Fin 7
canonical-to-Fin = canonical-cover (λ _ → Fin 7)
  ( zero
  , suc zero
  , suc (suc zero)
  , suc (suc (suc zero))
  , suc (suc (suc (suc zero)))
  , suc (suc (suc (suc (suc zero))))
  , suc (suc (suc (suc (suc (suc zero)))))
  )

Fin-to-canonical : Fin 7 → Σ (Word Z₇.Gen) Z₇.Canonical
Fin-to-canonical = fin-cover (λ _ → Σ (Word Z₇.Gen) Z₇.Canonical)
  ( ([] , Z₇.c-ε)
  , ((Z₇.a ∷ []) , Z₇.c-a)
  , ((Z₇.a ∷ Z₇.a ∷ []) , Z₇.c-aa)
  , ((Z₇.a ∷ Z₇.a ∷ Z₇.a ∷ []) , Z₇.c-aaa)
  , ((Z₇.a ∷ Z₇.a ∷ Z₇.a ∷ Z₇.a ∷ []) , Z₇.c-aaaa)
  , ((Z₇.a ∷ Z₇.a ∷ Z₇.a ∷ Z₇.a ∷ Z₇.a ∷ []) , Z₇.c-aaaaa)
  , ((Z₇.a ∷ Z₇.a ∷ Z₇.a ∷ Z₇.a ∷ Z₇.a ∷ Z₇.a ∷ []) , Z₇.c-aaaaaa)
  )

Fin-roundtrip : (i : Fin 7) →
  canonical-to-Fin (proj₂ (Fin-to-canonical i)) ≡ i
Fin-roundtrip = fin-cover
  (λ i → canonical-to-Fin (proj₂ (Fin-to-canonical i)) ≡ i)
  (refl , refl , refl , refl , refl , refl , refl)

canonical-roundtrip : ∀ {w : Word Z₇.Gen} (c : Z₇.Canonical w) →
  Fin-to-canonical (canonical-to-Fin c) ≡ (w , c)
canonical-roundtrip = canonical-cover
  (λ {w} c → Fin-to-canonical (canonical-to-Fin c) ≡ (w , c))
  (refl , refl , refl , refl , refl , refl , refl)

------------------------------------------------------------------------
-- Action correspondence: insert a ↔ σ₇ via the bijection.
------------------------------------------------------------------------

action-of-a-is-σ₇ :
  ∀ {w : Word Z₇.Gen} (c : Z₇.Canonical w) →
  canonical-to-Fin (Z₇.insert-canonical Z₇.a c) ≡ σ₇ (canonical-to-Fin c)
action-of-a-is-σ₇ = canonical-cover
  (λ c → canonical-to-Fin (Z₇.insert-canonical Z₇.a c) ≡ σ₇ (canonical-to-Fin c))
  (refl , refl , refl , refl , refl , refl , refl)

------------------------------------------------------------------------
-- σ₇-HasOrderPerm via Cycle7 (= cyclic-suc {6}'s structural witness).
------------------------------------------------------------------------

σ₇-HasOrderPerm-from-Z7-Coxeter : HasOrderPerm σ₇ 7
σ₇-HasOrderPerm-from-Z7-Coxeter = σ₇-HasOrderPerm

------------------------------------------------------------------------
-- Apply the generic chain.
------------------------------------------------------------------------

open import Substrate.Groups.Coxeter-Fin-Generic
  7 Z₇.Gen Z₇.a Z₇.Canonical Z₇.insert Z₇.insert-canonical
  canonical-to-Fin Fin-to-canonical σ₇
  action-of-a-is-σ₇ σ₇-HasOrderPerm-from-Z7-Coxeter
  public
