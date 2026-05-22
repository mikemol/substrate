------------------------------------------------------------------------
-- Substrate.Groups.Z3-Coxeter-Fin
--
-- The Z₃-Coxeter ↔ Fin 3 chain as a thin instance of
-- Substrate.Groups.Coxeter-Fin-Generic.
--
-- Per [[feedback-expose-generator-not-orbit]]: dispatches via
-- canonical-cover-Z3 (Canonical-side) + fin-cover (Fin-side); per-Z₃
-- data is the payload tuples.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z3-Coxeter-Fin where

open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Fin.Cover using (fin-cover)
open import Substrate.Foundation.Product using (Σ; _,_; proj₁; proj₂)
open import Substrate.Foundation.Eq using (_≡_; refl)

import Substrate.Groups.Z3-Coxeter as Z₃
open import Substrate.Groups.Coxeter.Word using (Word; []; _∷_)
open import Substrate.Algebra.F2.Linear.FromImages.Permutation
  using (HasOrderPerm)
open import Substrate.Algebra.F2.Linear.FromImages.Permutation.Cycle3
  using (σ₃; σ₃-HasOrderPerm)

------------------------------------------------------------------------
-- Bijection: cover-dispatched on both sides.
------------------------------------------------------------------------

canonical-to-Fin : ∀ {w : Word Z₃.Gen} → Z₃.Canonical w → Fin 3
canonical-to-Fin = Z₃.canonical-cover (λ _ → Fin 3)
  ( zero
  , suc zero
  , suc (suc zero)
  )

Fin-to-canonical : Fin 3 → Σ (Word Z₃.Gen) Z₃.Canonical
Fin-to-canonical = fin-cover (λ _ → Σ (Word Z₃.Gen) Z₃.Canonical)
  ( ([] , Z₃.c-ε)
  , ((Z₃.a ∷ []) , Z₃.c-a)
  , ((Z₃.a ∷ Z₃.a ∷ []) , Z₃.c-aa)
  )

Fin-roundtrip : (i : Fin 3) →
  canonical-to-Fin (proj₂ (Fin-to-canonical i)) ≡ i
Fin-roundtrip = fin-cover
  (λ i → canonical-to-Fin (proj₂ (Fin-to-canonical i)) ≡ i)
  (refl , refl , refl)

canonical-roundtrip : ∀ {w : Word Z₃.Gen} (c : Z₃.Canonical w) →
  Fin-to-canonical (canonical-to-Fin c) ≡ (w , c)
canonical-roundtrip = Z₃.canonical-cover
  (λ {w} c → Fin-to-canonical (canonical-to-Fin c) ≡ (w , c))
  (refl , refl , refl)

------------------------------------------------------------------------
-- Action correspondence.
------------------------------------------------------------------------

action-of-a-is-σ₃ :
  ∀ {w : Word Z₃.Gen} (c : Z₃.Canonical w) →
  canonical-to-Fin (Z₃.insert-canonical Z₃.a c) ≡ σ₃ (canonical-to-Fin c)
action-of-a-is-σ₃ = Z₃.canonical-cover
  (λ c → canonical-to-Fin (Z₃.insert-canonical Z₃.a c) ≡ σ₃ (canonical-to-Fin c))
  (refl , refl , refl)

------------------------------------------------------------------------
-- σ₃-HasOrderPerm via Cycle3 (= cyclic-suc {2}'s structural witness).
------------------------------------------------------------------------

σ₃-HasOrderPerm-from-Z3-Coxeter : HasOrderPerm σ₃ 3
σ₃-HasOrderPerm-from-Z3-Coxeter = σ₃-HasOrderPerm

------------------------------------------------------------------------
-- Apply the generic chain.
------------------------------------------------------------------------

open import Substrate.Groups.Coxeter-Fin-Generic
  3 Z₃.Gen Z₃.a Z₃.Canonical Z₃.insert Z₃.insert-canonical
  canonical-to-Fin Fin-to-canonical σ₃
  action-of-a-is-σ₃ σ₃-HasOrderPerm-from-Z3-Coxeter
  public
