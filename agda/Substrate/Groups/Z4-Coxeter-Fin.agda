------------------------------------------------------------------------
-- Substrate.Groups.Z4-Coxeter-Fin
--
-- The Z₄-Coxeter ↔ Fin 4 chain as a thin instance of
-- Substrate.Groups.Coxeter-Fin-Generic.
--
-- Per [[expose-generator-not-orbit]]: the Z₃/Z₄/Z₅-Coxeter-Fin chain
-- shape — bijection + action + HasOrderPerm — is the orbit; the
-- generic IS the chain. This file supplies the per-Z₄ data and
-- applies the generic to get the consolidated chain.
--
-- Per [[feedback-roll-our-own-via-word-algebra]]: Z₄-Coxeter's relation
-- `a⁴ = ε` is the structural source of truth for σ₄'s order on Fin 4.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z4-Coxeter-Fin where

open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Product using (Σ; _,_; proj₁; proj₂)
open import Substrate.Foundation.Eq using (_≡_; refl)

import Substrate.Groups.Z4-Coxeter as Z₄
open import Substrate.Groups.Coxeter.Word using (Word; []; _∷_)
open import Substrate.Algebra.F2.Linear.FromImages.Permutation
  using (HasOrderPerm)
open import Substrate.Algebra.F2.Linear.FromImages.Permutation.Cycle4
  using (σ₄)

------------------------------------------------------------------------
-- Per-Z₄ data: bijection between (canonical Z₄-Words) and Fin 4.
------------------------------------------------------------------------

canonical-to-Fin : {w : Word Z₄.Gen} → Z₄.Canonical w → Fin 4
canonical-to-Fin Z₄.c-ε   = zero
canonical-to-Fin Z₄.c-a   = suc zero
canonical-to-Fin Z₄.c-aa  = suc (suc zero)
canonical-to-Fin Z₄.c-aaa = suc (suc (suc zero))

Fin-to-canonical : Fin 4 → Σ (Word Z₄.Gen) Z₄.Canonical
Fin-to-canonical zero                            = [] , Z₄.c-ε
Fin-to-canonical (suc zero)                      = (Z₄.a ∷ []) , Z₄.c-a
Fin-to-canonical (suc (suc zero))                = (Z₄.a ∷ Z₄.a ∷ []) , Z₄.c-aa
Fin-to-canonical (suc (suc (suc zero)))          = (Z₄.a ∷ Z₄.a ∷ Z₄.a ∷ []) , Z₄.c-aaa

Fin-roundtrip : (i : Fin 4) →
  canonical-to-Fin (proj₂ (Fin-to-canonical i)) ≡ i
Fin-roundtrip zero                            = refl
Fin-roundtrip (suc zero)                      = refl
Fin-roundtrip (suc (suc zero))                = refl
Fin-roundtrip (suc (suc (suc zero)))          = refl

canonical-roundtrip : {w : Word Z₄.Gen} (c : Z₄.Canonical w) →
  Fin-to-canonical (canonical-to-Fin c) ≡ (w , c)
canonical-roundtrip Z₄.c-ε   = refl
canonical-roundtrip Z₄.c-a   = refl
canonical-roundtrip Z₄.c-aa  = refl
canonical-roundtrip Z₄.c-aaa = refl

------------------------------------------------------------------------
-- Per-Z₄ data: action-of-a corresponds to σ₄.
------------------------------------------------------------------------

action-of-a-is-σ₄ :
  {w : Word Z₄.Gen} (c : Z₄.Canonical w) →
  canonical-to-Fin (Z₄.insert-canonical Z₄.a c) ≡ σ₄ (canonical-to-Fin c)
action-of-a-is-σ₄ Z₄.c-ε   = refl
action-of-a-is-σ₄ Z₄.c-a   = refl
action-of-a-is-σ₄ Z₄.c-aa  = refl
action-of-a-is-σ₄ Z₄.c-aaa = refl

------------------------------------------------------------------------
-- Per-Z₄ data: σ₄-HasOrderPerm — the Coxeter aⁿ = ε relation lifted
-- through the bijection. Per-position enumeration at Fin 4.
------------------------------------------------------------------------

σ₄-HasOrderPerm-from-Z4-Coxeter : HasOrderPerm σ₄ 4
σ₄-HasOrderPerm-from-Z4-Coxeter zero                            = refl
σ₄-HasOrderPerm-from-Z4-Coxeter (suc zero)                      = refl
σ₄-HasOrderPerm-from-Z4-Coxeter (suc (suc zero))                = refl
σ₄-HasOrderPerm-from-Z4-Coxeter (suc (suc (suc zero)))          = refl

------------------------------------------------------------------------
-- Apply the generic chain: takes the per-Z₄ pieces, produces the
-- consolidated σₙ-HasOrderPerm under the chain's canonical name.
------------------------------------------------------------------------

open import Substrate.Groups.Coxeter-Fin-Generic
  4 Z₄.Gen Z₄.a Z₄.Canonical Z₄.insert Z₄.insert-canonical
  canonical-to-Fin Fin-to-canonical σ₄
  action-of-a-is-σ₄ σ₄-HasOrderPerm-from-Z4-Coxeter
  public

------------------------------------------------------------------------
-- Capstone — Z₄ word-algebra ↔ Fin 4 chain complete.
--
-- This file's structural value is the per-Z₄ data (bijection +
-- round-trips + action + order-witness); the consolidated chain
-- shape lives at [[Coxeter-Fin-Generic]] and ships across Z₃/Z₄/Z₅
-- uniformly.
------------------------------------------------------------------------
