------------------------------------------------------------------------
-- Substrate.Groups.Z3-Coxeter-Action
--
-- The bridge between Z3-Coxeter's `insert a` operation on Canonical
-- words and the cyclic-shift σ₃ on Fin 3.
--
-- Z3-Coxeter encodes ℤ/3 via word algebra: `insert a` advances the
-- canonical-form cycle c-ε → c-a → c-aa → c-ε. Through the
-- Z3-Coxeter-Fin bijection, this corresponds to the cyclic-shift
-- σ₃ : Fin 3 → Fin 3 from Cycle3.
--
-- The structural identity:
--   canonical-to-Fin (insert-canonical a c) ≡ σ₃ (canonical-to-Fin c)
--
-- Three refl cases (one per Canonical constructor); the equation
-- holds by the way σ₃ and insert-a are defined.
--
-- Per [[feedback-roll-our-own-via-word-algebra]]: this is the
-- structural identification that makes Z₃-Coxeter the SOURCE OF
-- TRUTH for σ₃'s cyclic behavior. The relation `a³ = ε` in the word
-- algebra becomes `σ₃³ = id` on Fin 3 through this bridge (slice 7).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z3-Coxeter-Action where

open import Data.Fin using (Fin; zero; suc)
open import Relation.Binary.PropositionalEquality using (_≡_; refl)

import Substrate.Groups.Z3-Coxeter as Z₃
open import Substrate.Groups.Coxeter.Word using (Word; []; _∷_)
open import Substrate.Groups.Z3-Coxeter-Fin
  using (canonical-to-Fin)
open import Substrate.Algebra.F2.Linear.FromImages.Permutation.Cycle3
  using (σ₃)

------------------------------------------------------------------------
-- N-1: The action equation — `insert-canonical a` on Canonical
-- corresponds to σ₃ on Fin 3 via the Z3-Coxeter-Fin bijection.
--
-- Per Canonical constructor:
--   c-ε  ↦ canonical-to-Fin c-ε = 0   ; σ₃ 0 = 1 = canonical-to-Fin c-a
--                                     = canonical-to-Fin (insert-canonical a c-ε)
--   c-a  ↦ 1   ; σ₃ 1 = 2 = canonical-to-Fin c-aa
--   c-aa ↦ 2   ; σ₃ 2 = 0 = canonical-to-Fin c-ε   (wrap)
------------------------------------------------------------------------

action-of-a-is-σ₃ :
  {w : Word Z₃.Gen} (c : Z₃.Canonical w) →
  canonical-to-Fin (Z₃.insert-canonical Z₃.a c) ≡ σ₃ (canonical-to-Fin c)
action-of-a-is-σ₃ Z₃.c-ε  = refl
action-of-a-is-σ₃ Z₃.c-a  = refl
action-of-a-is-σ₃ Z₃.c-aa = refl

------------------------------------------------------------------------
-- N-2: Capstone — the action bridge lands.
--
-- After this slice:
--
--   action-of-a-is-σ₃ : the structural identity that the Z₃-Coxeter
--   word algebra's `insert a` operation is exactly the cyclic-shift
--   σ₃ on Fin 3.
--
-- Combined with the next slice (HasOrderPerm-from-cube-identity),
-- the Z₃-Coxeter relation `a³ = ε` mechanically gives `σ₃³ = id`
-- via the bridge.
--
-- Per [[feedback-categorical-name-first]]: the action-on-canonical
-- pattern IS the categorical "group acting on its own elements via
-- left multiplication" instance, made explicit at the substrate's
-- Fin-indexed level.
------------------------------------------------------------------------
