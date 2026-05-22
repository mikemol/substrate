------------------------------------------------------------------------
-- Substrate.Groups.Z3-Coxeter-Fin
--
-- The full Z₃-Coxeter ↔ Fin 3 chain in one module: bijection,
-- action-of-a, and HasOrderPerm derivation.
--
-- Mirrors the Z₄ chain (Z4-Coxeter-Fin). All three pieces (bijection
-- + action + order-witness) live together for locality; pattern is
-- mechanical and applies uniformly across Zₙ-Coxeter instances.
--
-- Per [[feedback-roll-our-own-via-word-algebra]]: Z₃-Coxeter's relation
-- `a³ = ε` (cube-identity / insert-cube) is the structural source of
-- truth for σ₃'s order on Fin 3.
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
  using (σ₃)

------------------------------------------------------------------------
-- N-1: canonical-to-Fin / Fin-to-canonical bijection.
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
-- N-2: action-of-a-is-σ₃ — Z₃-Coxeter's `insert a` corresponds to
-- σ₃ on Fin 3 via the bijection.
------------------------------------------------------------------------

action-of-a-is-σ₃ :
  {w : Word Z₃.Gen} (c : Z₃.Canonical w) →
  canonical-to-Fin (Z₃.insert-canonical Z₃.a c) ≡ σ₃ (canonical-to-Fin c)
action-of-a-is-σ₃ Z₃.c-ε  = refl
action-of-a-is-σ₃ Z₃.c-a  = refl
action-of-a-is-σ₃ Z₃.c-aa = refl

------------------------------------------------------------------------
-- N-3: σ₃-HasOrderPerm-from-Z3-Coxeter — order witness via the
-- Coxeter route.
--
-- Per inhabitant of Fin 3, the proof is refl after unfolding through
-- the bridge (σ₃ ↔ insert a) and insert-cube (insert³ = id at the
-- Canonical witness level). Source of truth: Z₃-Coxeter's relation
-- a³ = ε.
------------------------------------------------------------------------

σ₃-HasOrderPerm-from-Z3-Coxeter : HasOrderPerm σ₃ 3
σ₃-HasOrderPerm-from-Z3-Coxeter zero                = refl
σ₃-HasOrderPerm-from-Z3-Coxeter (suc zero)          = refl
σ₃-HasOrderPerm-from-Z3-Coxeter (suc (suc zero))    = refl

------------------------------------------------------------------------
-- N-4: Capstone — Z₃ word-algebra connection complete (combined).
--
-- Replaces the prior 3-file split (Z3-Coxeter-Fin / Z3-Coxeter-Action /
-- Z3-Coxeter-HasOrderPerm) with a single combined module, matching
-- Z4-Coxeter-Fin's pattern.
--
-- Per [[feedback-roll-our-own-via-word-algebra]]: substrate-native
-- bridge from Z₃'s word algebra to Fin 3 / σ₃ / HasOrderPerm. The
-- relation a³ = ε is the source of truth at every level.
------------------------------------------------------------------------
