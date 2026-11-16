------------------------------------------------------------------------
-- Substrate.Algebra.F1.GL.IdGLF1
--
-- Defines: id-GL-F₁
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.F1.GL; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F1.GL.IdGLF1 where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
open import Substrate.Algebra.PointedSet
open import Substrate.Algebra.PointedSet.Map.Anon
open import Substrate.Algebra.PointedSet.Map.IdPointedSetMap
open import Substrate.Foundation.Eq
open import Substrate.Algebra.F1.GL.F1N
open import Substrate.Algebra.F1.GL.GLF1



------------------------------------------------------------------------
-- 3. Identity element of GL(n, F₁).
--
-- The identity automorphism — the only canonical element guaranteed
-- structurally; the full Sₙ structure is in Substrate.Coxeter.
------------------------------------------------------------------------


id-GL-F₁ : (n : ℕ) → GL-F₁ n
id-GL-F₁ n = record
  { forward   = id-PointedSetMap (F₁ⁿ n)
  ; backward  = id-PointedSetMap (F₁ⁿ n)
  ; inv-left  = λ _ → refl
  ; inv-right = λ _ → refl
  }

------------------------------------------------------------------------
-- 4. Capstone for F1m4.
--
-- GL-F₁ n landed as the type of basepoint-preserving bijections of
-- (Fin (suc n), zero). The identification with Sₙ at the group-
-- structure level routes through substrate's existing Coxeter-Sₙ
-- machinery (Substrate.Coxeter framework per [[v4-typeclass-
-- architecture]]). F1m5 captures the arc.
------------------------------------------------------------------------
