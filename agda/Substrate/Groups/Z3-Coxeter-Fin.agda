------------------------------------------------------------------------
-- Substrate.Groups.Z3-Coxeter-Fin
--
-- The Z₃-Coxeter ↔ Fin 3 chain as a thin instance of
-- Substrate.Groups.Coxeter-Fin-Generic.
--
-- Per [[expose-generator-not-orbit]]: the Z₃/Z₄/Z₅-Coxeter-Fin chain
-- shape — bijection + action + HasOrderPerm — is the orbit; the
-- generic IS the chain. This file supplies the per-Z₃ data and
-- applies the generic to get the consolidated chain.
--
-- Per [[feedback-roll-our-own-via-word-algebra]]: Z₃-Coxeter's relation
-- `a³ = ε` is the structural source of truth for σ₃'s order on Fin 3.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z3-Coxeter-Fin where

open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Product using (Σ; _,_; proj₁; proj₂)
open import Substrate.Foundation.Eq using (_≡_; refl)

import Substrate.Groups.Z3-Coxeter as Z₃
open import Substrate.Groups.Coxeter.Word using (Word; []; _∷_)
open import Substrate.Algebra.F2.Linear.FromImages.Permutation
  using (HasOrderPerm)
open import Substrate.Algebra.F2.Linear.FromImages.Permutation.Cycle3
  using (σ₃; σ₃-HasOrderPerm)

------------------------------------------------------------------------
-- Per-Z₃ data: bijection between (canonical Z₃-Words) and Fin 3.
------------------------------------------------------------------------

canonical-to-Fin : {w : Word Z₃.Gen} → Z₃.Canonical w → Fin 3
canonical-to-Fin Z₃.c-ε  = zero
canonical-to-Fin Z₃.c-a  = suc zero
canonical-to-Fin Z₃.c-aa = suc (suc zero)

Fin-to-canonical : Fin 3 → Σ (Word Z₃.Gen) Z₃.Canonical
Fin-to-canonical zero                = [] , Z₃.c-ε
Fin-to-canonical (suc zero)          = (Z₃.a ∷ []) , Z₃.c-a
Fin-to-canonical (suc (suc zero))    = (Z₃.a ∷ Z₃.a ∷ []) , Z₃.c-aa

Fin-roundtrip : (i : Fin 3) →
  canonical-to-Fin (proj₂ (Fin-to-canonical i)) ≡ i
Fin-roundtrip zero                = refl
Fin-roundtrip (suc zero)          = refl
Fin-roundtrip (suc (suc zero))    = refl

canonical-roundtrip : {w : Word Z₃.Gen} (c : Z₃.Canonical w) →
  Fin-to-canonical (canonical-to-Fin c) ≡ (w , c)
canonical-roundtrip Z₃.c-ε  = refl
canonical-roundtrip Z₃.c-a  = refl
canonical-roundtrip Z₃.c-aa = refl

------------------------------------------------------------------------
-- Per-Z₃ data: action-of-a corresponds to σ₃.
------------------------------------------------------------------------

action-of-a-is-σ₃ :
  {w : Word Z₃.Gen} (c : Z₃.Canonical w) →
  canonical-to-Fin (Z₃.insert-canonical Z₃.a c) ≡ σ₃ (canonical-to-Fin c)
action-of-a-is-σ₃ Z₃.c-ε  = refl
action-of-a-is-σ₃ Z₃.c-a  = refl
action-of-a-is-σ₃ Z₃.c-aa = refl

------------------------------------------------------------------------
-- σ₃-HasOrderPerm — the Coxeter a³ = ε relation lifted through the
-- bijection. Re-exported from Cycle3 under the chain's canonical
-- name; no per-position enumeration here (Cycle3 owns the witness).
------------------------------------------------------------------------

σ₃-HasOrderPerm-from-Z3-Coxeter : HasOrderPerm σ₃ 3
σ₃-HasOrderPerm-from-Z3-Coxeter = σ₃-HasOrderPerm

------------------------------------------------------------------------
-- Apply the generic chain: takes the per-Z₃ pieces, produces the
-- consolidated σₙ-HasOrderPerm under the chain's canonical name.
------------------------------------------------------------------------

open import Substrate.Groups.Coxeter-Fin-Generic
  3 Z₃.Gen Z₃.a Z₃.Canonical Z₃.insert Z₃.insert-canonical
  canonical-to-Fin Fin-to-canonical σ₃
  action-of-a-is-σ₃ σ₃-HasOrderPerm-from-Z3-Coxeter
  public

------------------------------------------------------------------------
-- Capstone — Z₃ word-algebra ↔ Fin 3 chain complete.
--
-- This file's structural value is the per-Z₃ data (bijection +
-- round-trips + action + order-witness); the consolidated chain
-- shape lives at [[Coxeter-Fin-Generic]] and ships across Z₃/Z₄/Z₅
-- uniformly.
------------------------------------------------------------------------
