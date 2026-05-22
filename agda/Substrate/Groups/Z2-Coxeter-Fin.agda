------------------------------------------------------------------------
-- Substrate.Groups.Z2-Coxeter-Fin
--
-- The Z₂-Coxeter ↔ Fin 2 chain as a thin instance of
-- Substrate.Groups.Coxeter-Fin-Generic.
--
-- Per [[feedback-expose-generator-not-orbit]]: this file uses
-- canonical-cover-Z2 (dispatch on Canonical) + fin-cover (dispatch on
-- Fin) instead of hand-spelled per-constructor enumeration. The
-- payload tuples are the only per-Z₂ data; the dispatch structure is
-- a generic combinator.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z2-Coxeter-Fin where

open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Fin.Cover using (fin-cover)
open import Substrate.Foundation.Product using (Σ; _,_; proj₁; proj₂)
open import Substrate.Foundation.Eq using (_≡_; refl)

import Substrate.Groups.Z2-Coxeter as Z₂
open import Substrate.Groups.Coxeter.Word using (Word; []; _∷_)
open import Substrate.Algebra.F2.Linear.FromImages.Permutation
  using (HasOrderPerm)
open import Substrate.Algebra.F2.Linear.FromImages.Permutation.Cycle2
  using (σ₂; σ₂-HasOrderPerm)

------------------------------------------------------------------------
-- Bijection between (canonical Z₂-Words) and Fin 2, via the cover
-- combinators. canonical-to-Fin dispatches via canonical-cover-Z2;
-- Fin-to-canonical via fin-cover.
------------------------------------------------------------------------

canonical-to-Fin : ∀ {w : Word Z₂.Gen} → Z₂.Canonical w → Fin 2
canonical-to-Fin =
  Z₂.canonical-cover-Z2 (λ _ → Fin 2) (zero , suc zero)

Fin-to-canonical : Fin 2 → Σ (Word Z₂.Gen) Z₂.Canonical
Fin-to-canonical = fin-cover (λ _ → Σ (Word Z₂.Gen) Z₂.Canonical)
  ( ([] , Z₂.c-ε)
  , ((Z₂.a ∷ []) , Z₂.c-a)
  )

Fin-roundtrip : (i : Fin 2) →
  canonical-to-Fin (proj₂ (Fin-to-canonical i)) ≡ i
Fin-roundtrip = fin-cover
  (λ i → canonical-to-Fin (proj₂ (Fin-to-canonical i)) ≡ i)
  (refl , refl)

canonical-roundtrip : ∀ {w : Word Z₂.Gen} (c : Z₂.Canonical w) →
  Fin-to-canonical (canonical-to-Fin c) ≡ (w , c)
canonical-roundtrip = Z₂.canonical-cover-Z2
  (λ {w} c → Fin-to-canonical (canonical-to-Fin c) ≡ (w , c))
  (refl , refl)

------------------------------------------------------------------------
-- Action correspondence: insert a ↔ σ₂ via the bijection.
------------------------------------------------------------------------

action-of-a-is-σ₂ :
  ∀ {w : Word Z₂.Gen} (c : Z₂.Canonical w) →
  canonical-to-Fin (Z₂.insert-canonical Z₂.a c) ≡ σ₂ (canonical-to-Fin c)
action-of-a-is-σ₂ = Z₂.canonical-cover-Z2
  (λ c → canonical-to-Fin (Z₂.insert-canonical Z₂.a c) ≡ σ₂ (canonical-to-Fin c))
  (refl , refl)

------------------------------------------------------------------------
-- σ₂-HasOrderPerm — re-exported from Cycle2 (= cyclic-suc {1}'s
-- structural witness).
------------------------------------------------------------------------

σ₂-HasOrderPerm-from-Z2-Coxeter : HasOrderPerm σ₂ 2
σ₂-HasOrderPerm-from-Z2-Coxeter = σ₂-HasOrderPerm

------------------------------------------------------------------------
-- Apply the generic chain.
------------------------------------------------------------------------

open import Substrate.Groups.Coxeter-Fin-Generic
  2 Z₂.Gen Z₂.a Z₂.Canonical Z₂.insert Z₂.insert-canonical
  canonical-to-Fin Fin-to-canonical σ₂
  action-of-a-is-σ₂ σ₂-HasOrderPerm-from-Z2-Coxeter
  public
