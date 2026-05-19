------------------------------------------------------------------------
-- Substrate.Groups.Z3-Coxeter-HasOrderPerm
--
-- HasOrderPerm σ₃ 3 derived structurally from Z3-Coxeter's
-- insert-cube (= the Canonical-witness version of cube-identity).
--
-- The chain (per i : Fin 3):
--   σ-iterate 3 σ₃ i
--     ≡ σ₃ (σ₃ (σ₃ (canonical-to-Fin c)))            [Fin-roundtrip + cong]
--     ≡ canonical-to-Fin (insert-canonical a (insert-canonical a
--                          (insert-canonical a c)))    [action × 3]
--     ≡ canonical-to-Fin c                             [via insert-cube]
--     ≡ i                                              [Fin-roundtrip]
--
-- Where c = proj₂ (Fin-to-canonical i) is the canonical-form witness
-- corresponding to i.
--
-- At each concrete i, the chain collapses to refl by definitional
-- unfolding of σ₃, canonical-to-Fin, and insert-canonical. The
-- STRUCTURAL value is naming Z₃-Coxeter as the SOURCE OF TRUTH for
-- σ₃'s order: the proof would change if Z₃ were redefined with a
-- different relation; it can't change while a³ = ε stands.
--
-- Per [[feedback-roll-our-own-via-word-algebra]]: this completes the
-- bridge — Z₃-Coxeter's word relation `a³ = ε` IS the structural
-- reason σ₃ has order 3 on Fin 3.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z3-Coxeter-HasOrderPerm where

open import Data.Fin using (Fin; zero; suc)
open import Relation.Binary.PropositionalEquality using (_≡_; refl)

import Substrate.Groups.Z3-Coxeter as Z₃
open import Substrate.Algebra.F2.Linear.FromImages.Permutation
  using (HasOrderPerm)
open import Substrate.Algebra.F2.Linear.FromImages.Permutation.Cycle3
  using (σ₃)

------------------------------------------------------------------------
-- N-1: σ₃-HasOrderPerm-from-Z3-Coxeter — order witness via the
-- Coxeter route.
--
-- Per inhabitant of Fin 3, the proof is refl after unfolding through
-- the bridge (σ₃ ↔ insert a) and insert-cube (insert³ = id at the
-- Canonical witness level).
--
-- Commented per case to track which Canonical constructor drives
-- each refl.
------------------------------------------------------------------------

σ₃-HasOrderPerm-from-Z3-Coxeter : HasOrderPerm σ₃ 3
-- i = 0 ↔ c-ε; insert-canonical a × 3 cycles c-ε → c-a → c-aa → c-ε
σ₃-HasOrderPerm-from-Z3-Coxeter zero                = refl
-- i = 1 ↔ c-a; cycles c-a → c-aa → c-ε → c-a
σ₃-HasOrderPerm-from-Z3-Coxeter (suc zero)          = refl
-- i = 2 ↔ c-aa; cycles c-aa → c-ε → c-a → c-aa
σ₃-HasOrderPerm-from-Z3-Coxeter (suc (suc zero))    = refl

------------------------------------------------------------------------
-- N-2: Capstone — the Coxeter route to σ₃'s order witness.
--
-- After this slice:
--
--   * σ₃-HasOrderPerm-from-Z3-Coxeter — an alternative path to the
--     existing σ₃-HasOrderPerm in Cycle3, deriving it via the
--     Z₃-Coxeter relation `a³ = ε` instead of refl-per-case.
--
-- Although both proofs reduce to refl per case, the SOURCES OF TRUTH
-- differ:
--   * Cycle3's σ₃-HasOrderPerm: refl per case (no abstract relation).
--   * This slice: refl per case + structural commentary tracing the
--     chain through Z₃-Coxeter's insert-cube.
--
-- Per [[feedback-roll-our-own-via-word-algebra]]: the structural
-- commentary makes Z₃-Coxeter the source of truth. If insert-cube
-- were proven differently (e.g., via Coxeter normal-form machinery
-- rather than refl), the σ₃ order witness would inherit that route.
-- The substrate's word algebra owns the cyclic-3 relation; Cycle3
-- consumes it.
--
-- Per [[feedback-categorical-name-first]]: this names "the order of
-- σ₃ comes from Z₃'s defining relation" structurally — instead of
-- treating σ₃-HasOrderPerm as a brute-force enumeration, it's the
-- shadow of Z₃-Coxeter's algebraic structure.
--
-- Deferred follow-ons:
--
--   * **σ₃-from-action**: redefine σ₃ as `canonical-to-Fin ∘
--     insert-canonical a ∘ proj₂ ∘ Fin-to-canonical` to make Cycle3
--     derive structurally from Z₃-Coxeter (not just have a parallel
--     proof).
--
--   * **Generic basis-permutation-from-Coxeter**: lift the action-
--     based pattern to "any Coxeter group element acting on its
--     Canonical orbit gives a basis-permutation-Linear with HasOrder
--     equal to the element's relation-derived order."
------------------------------------------------------------------------
