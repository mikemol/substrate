------------------------------------------------------------------------
-- Substrate.Groups.Z5-Coxeter-Fin
--
-- The Z₅-Coxeter ↔ Fin 5 chain as a thin instance of
-- Substrate.Groups.Coxeter-Fin-Generic.
--
-- Per [[expose-generator-not-orbit]]: the Z₃/Z₄/Z₅-Coxeter-Fin chain
-- shape — bijection + action + HasOrderPerm — is the orbit; the
-- generic IS the chain. This file supplies the per-Z₅ data and
-- applies the generic to get the consolidated chain.
--
-- Per [[feedback-roll-our-own-via-word-algebra]]: Z₅-Coxeter's relation
-- `a⁵ = ε` is the structural source of truth for σ₅'s order on Fin 5.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z5-Coxeter-Fin where

open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Product using (Σ; _,_; proj₁; proj₂)
open import Substrate.Foundation.Eq using (_≡_; refl)

import Substrate.Groups.Z5-Coxeter as Z₅
open import Substrate.Groups.Coxeter.Word using (Word; []; _∷_)
open import Substrate.Algebra.F2.Linear.FromImages.Permutation
  using (HasOrderPerm)
open import Substrate.Algebra.F2.Linear.FromImages.Permutation.Cycle5
  using (σ₅; σ₅-HasOrderPerm)

------------------------------------------------------------------------
-- Per-Z₅ data: bijection between (canonical Z₅-Words) and Fin 5.
------------------------------------------------------------------------

canonical-to-Fin : {w : Word Z₅.Gen} → Z₅.Canonical w → Fin 5
canonical-to-Fin Z₅.c-ε    = zero
canonical-to-Fin Z₅.c-a    = suc zero
canonical-to-Fin Z₅.c-aa   = suc (suc zero)
canonical-to-Fin Z₅.c-aaa  = suc (suc (suc zero))
canonical-to-Fin Z₅.c-aaaa = suc (suc (suc (suc zero)))

Fin-to-canonical : Fin 5 → Σ (Word Z₅.Gen) Z₅.Canonical
Fin-to-canonical zero                                  = [] , Z₅.c-ε
Fin-to-canonical (suc zero)                            = (Z₅.a ∷ []) , Z₅.c-a
Fin-to-canonical (suc (suc zero))                      = (Z₅.a ∷ Z₅.a ∷ []) , Z₅.c-aa
Fin-to-canonical (suc (suc (suc zero)))                = (Z₅.a ∷ Z₅.a ∷ Z₅.a ∷ []) , Z₅.c-aaa
Fin-to-canonical (suc (suc (suc (suc zero))))          = (Z₅.a ∷ Z₅.a ∷ Z₅.a ∷ Z₅.a ∷ []) , Z₅.c-aaaa

Fin-roundtrip : (i : Fin 5) →
  canonical-to-Fin (proj₂ (Fin-to-canonical i)) ≡ i
Fin-roundtrip zero                                  = refl
Fin-roundtrip (suc zero)                            = refl
Fin-roundtrip (suc (suc zero))                      = refl
Fin-roundtrip (suc (suc (suc zero)))                = refl
Fin-roundtrip (suc (suc (suc (suc zero))))          = refl

canonical-roundtrip : {w : Word Z₅.Gen} (c : Z₅.Canonical w) →
  Fin-to-canonical (canonical-to-Fin c) ≡ (w , c)
canonical-roundtrip Z₅.c-ε    = refl
canonical-roundtrip Z₅.c-a    = refl
canonical-roundtrip Z₅.c-aa   = refl
canonical-roundtrip Z₅.c-aaa  = refl
canonical-roundtrip Z₅.c-aaaa = refl

------------------------------------------------------------------------
-- Per-Z₅ data: action-of-a corresponds to σ₅.
------------------------------------------------------------------------

action-of-a-is-σ₅ :
  {w : Word Z₅.Gen} (c : Z₅.Canonical w) →
  canonical-to-Fin (Z₅.insert-canonical Z₅.a c) ≡ σ₅ (canonical-to-Fin c)
action-of-a-is-σ₅ Z₅.c-ε    = refl
action-of-a-is-σ₅ Z₅.c-a    = refl
action-of-a-is-σ₅ Z₅.c-aa   = refl
action-of-a-is-σ₅ Z₅.c-aaa  = refl
action-of-a-is-σ₅ Z₅.c-aaaa = refl

------------------------------------------------------------------------
-- σ₅-HasOrderPerm — the Coxeter a⁵ = ε relation lifted through the
-- bijection. Re-exported from Cycle5 under the chain's canonical
-- name; no per-position enumeration here (Cycle5 owns the witness).
------------------------------------------------------------------------

σ₅-HasOrderPerm-from-Z5-Coxeter : HasOrderPerm σ₅ 5
σ₅-HasOrderPerm-from-Z5-Coxeter = σ₅-HasOrderPerm

------------------------------------------------------------------------
-- Apply the generic chain: takes the per-Z₅ pieces, produces the
-- consolidated σₙ-HasOrderPerm under the chain's canonical name.
------------------------------------------------------------------------

open import Substrate.Groups.Coxeter-Fin-Generic
  5 Z₅.Gen Z₅.a Z₅.Canonical Z₅.insert Z₅.insert-canonical
  canonical-to-Fin Fin-to-canonical σ₅
  action-of-a-is-σ₅ σ₅-HasOrderPerm-from-Z5-Coxeter
  public

------------------------------------------------------------------------
-- Capstone — Z₅ word-algebra ↔ Fin 5 chain complete.
--
-- This file's structural value is the per-Z₅ data (bijection +
-- round-trips + action + order-witness); the consolidated chain
-- shape lives at [[Coxeter-Fin-Generic]] and ships across Z₃/Z₄/Z₅
-- uniformly.
------------------------------------------------------------------------
