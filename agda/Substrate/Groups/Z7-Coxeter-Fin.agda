------------------------------------------------------------------------
-- Substrate.Groups.Z7-Coxeter-Fin
--
-- The Z₇-Coxeter ↔ Fin 7 chain as a thin instance of
-- Substrate.Groups.Coxeter-Fin-Generic.
--
-- Per [[expose-generator-not-orbit]]: the bijection (Canonical-world
-- ↔ Fin-world) is the irreducible per-Z₇ data; the chain shape +
-- σ₇-HasOrderPerm come free.
--
-- σ₇ is supplied by Cycle7 = cyclic-suc {6}; HasOrderPerm comes
-- structurally from cyclic-suc-HasOrderPerm — no per-position
-- enumeration at the Fin level.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z7-Coxeter-Fin where

open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Product using (Σ; _,_; proj₁; proj₂)
open import Substrate.Foundation.Eq using (_≡_; refl)

import Substrate.Groups.Z7-Coxeter as Z₇
open import Substrate.Groups.Coxeter.Word using (Word; []; _∷_)
open import Substrate.Algebra.F2.Linear.FromImages.Permutation
  using (HasOrderPerm)
open import Substrate.Algebra.F2.Linear.FromImages.Permutation.Cycle7
  using (σ₇; σ₇-HasOrderPerm)

------------------------------------------------------------------------
-- Per-Z₇ data: bijection between (canonical Z₇-Words) and Fin 7.
------------------------------------------------------------------------

canonical-to-Fin : {w : Word Z₇.Gen} → Z₇.Canonical w → Fin 7
canonical-to-Fin Z₇.c-ε      = zero
canonical-to-Fin Z₇.c-a      = suc zero
canonical-to-Fin Z₇.c-aa     = suc (suc zero)
canonical-to-Fin Z₇.c-aaa    = suc (suc (suc zero))
canonical-to-Fin Z₇.c-aaaa   = suc (suc (suc (suc zero)))
canonical-to-Fin Z₇.c-aaaaa  = suc (suc (suc (suc (suc zero))))
canonical-to-Fin Z₇.c-aaaaaa = suc (suc (suc (suc (suc (suc zero)))))

Fin-to-canonical : Fin 7 → Σ (Word Z₇.Gen) Z₇.Canonical
Fin-to-canonical zero
  = [] , Z₇.c-ε
Fin-to-canonical (suc zero)
  = (Z₇.a ∷ []) , Z₇.c-a
Fin-to-canonical (suc (suc zero))
  = (Z₇.a ∷ Z₇.a ∷ []) , Z₇.c-aa
Fin-to-canonical (suc (suc (suc zero)))
  = (Z₇.a ∷ Z₇.a ∷ Z₇.a ∷ []) , Z₇.c-aaa
Fin-to-canonical (suc (suc (suc (suc zero))))
  = (Z₇.a ∷ Z₇.a ∷ Z₇.a ∷ Z₇.a ∷ []) , Z₇.c-aaaa
Fin-to-canonical (suc (suc (suc (suc (suc zero)))))
  = (Z₇.a ∷ Z₇.a ∷ Z₇.a ∷ Z₇.a ∷ Z₇.a ∷ []) , Z₇.c-aaaaa
Fin-to-canonical (suc (suc (suc (suc (suc (suc zero))))))
  = (Z₇.a ∷ Z₇.a ∷ Z₇.a ∷ Z₇.a ∷ Z₇.a ∷ Z₇.a ∷ []) , Z₇.c-aaaaaa

Fin-roundtrip : (i : Fin 7) →
  canonical-to-Fin (proj₂ (Fin-to-canonical i)) ≡ i
Fin-roundtrip zero                                              = refl
Fin-roundtrip (suc zero)                                        = refl
Fin-roundtrip (suc (suc zero))                                  = refl
Fin-roundtrip (suc (suc (suc zero)))                            = refl
Fin-roundtrip (suc (suc (suc (suc zero))))                      = refl
Fin-roundtrip (suc (suc (suc (suc (suc zero)))))                = refl
Fin-roundtrip (suc (suc (suc (suc (suc (suc zero))))))          = refl

canonical-roundtrip : {w : Word Z₇.Gen} (c : Z₇.Canonical w) →
  Fin-to-canonical (canonical-to-Fin c) ≡ (w , c)
canonical-roundtrip Z₇.c-ε      = refl
canonical-roundtrip Z₇.c-a      = refl
canonical-roundtrip Z₇.c-aa     = refl
canonical-roundtrip Z₇.c-aaa    = refl
canonical-roundtrip Z₇.c-aaaa   = refl
canonical-roundtrip Z₇.c-aaaaa  = refl
canonical-roundtrip Z₇.c-aaaaaa = refl

------------------------------------------------------------------------
-- Per-Z₇ data: action-of-a corresponds to σ₇.
------------------------------------------------------------------------

action-of-a-is-σ₇ :
  {w : Word Z₇.Gen} (c : Z₇.Canonical w) →
  canonical-to-Fin (Z₇.insert-canonical Z₇.a c) ≡ σ₇ (canonical-to-Fin c)
action-of-a-is-σ₇ Z₇.c-ε      = refl
action-of-a-is-σ₇ Z₇.c-a      = refl
action-of-a-is-σ₇ Z₇.c-aa     = refl
action-of-a-is-σ₇ Z₇.c-aaa    = refl
action-of-a-is-σ₇ Z₇.c-aaaa   = refl
action-of-a-is-σ₇ Z₇.c-aaaaa  = refl
action-of-a-is-σ₇ Z₇.c-aaaaaa = refl

------------------------------------------------------------------------
-- σ₇-HasOrderPerm — re-exported from Cycle7 (= cyclic-suc {6}'s
-- structural HasOrderPerm witness).
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
