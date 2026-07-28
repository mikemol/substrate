------------------------------------------------------------------------
-- Substrate.Algebra.F1.GL
--
-- F1m4 of the F₁-modules arc per [scratch/m_mod_arc_plan.md].
--
-- The deep F₁ semantics: GL(n, F₁) = Sₙ.
--
-- In ordinary linear algebra over F_q, GL(n, F_q) is the group of
-- invertible n×n matrices. As q → 1, the q-analog formula
-- |GL(n, F_q)| = ∏ᵢ (q^n - q^i) collapses to n! — the order of Sₙ.
-- This is the canonical "F₁ semantics" claim.
--
-- Substrate-native realisation: an F₁-vector space of dimension n
-- is a pointed set of size n+1 (basepoint + n distinct elements).
-- An F₁-linear-automorphism is a basepoint-preserving bijection,
-- which is exactly a permutation of the n non-basepoint elements:
-- Sₙ.
--
-- This slice surfaces the IDENTIFICATION at the type level: GL(n,F₁)
-- IS the type of basepoint-preserving involutions on (Fin (suc n))
-- that fix `zero` (the basepoint) and permute the rest. The full
-- automorphism-group structure is delegated to substrate-existing
-- Coxeter-S_n infrastructure (Substrate.Coxeter.PermutationGroup
-- or the bicategorical S_n derived from the Coxeter framework).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F1.GL where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Eq
  using (_≡_; refl; sym; trans; cong)

open import Substrate.Algebra.PointedSet using (PointedSet; Carrier; base)
open import Substrate.Algebra.PointedSet.Map
  using (PointedSetMap; apply; base-preserv)

------------------------------------------------------------------------
-- 1. The F₁-vector space of dimension n: (Fin (suc n), zero).
------------------------------------------------------------------------

-- ⟡set1-paydown: PointedSet is now carrier-indexed; the carrier is Fin (suc n).
F₁ⁿ : (n : ℕ) → PointedSet (Fin (suc n))
F₁ⁿ n = record
  { base = zero
  }

------------------------------------------------------------------------
-- 2. GL(n, F₁) = basepoint-preserving bijections of F₁ⁿ.
--
-- A "linear automorphism" of F₁ⁿ is a PointedSetMap with a two-
-- sided inverse. The bundled record names the automorphism shape.
------------------------------------------------------------------------

record GL-F₁ (n : ℕ) : Set where
  field
    forward    : PointedSetMap (F₁ⁿ n) (F₁ⁿ n)
    backward   : PointedSetMap (F₁ⁿ n) (F₁ⁿ n)
    inv-left   : (x : Fin (suc n)) →
                 apply backward (apply forward x) ≡ x
    inv-right  : (x : Fin (suc n)) →
                 apply forward (apply backward x) ≡ x

open GL-F₁ public

------------------------------------------------------------------------
-- 3. Identity element of GL(n, F₁).
--
-- The identity automorphism — the only canonical element guaranteed
-- structurally; the full Sₙ structure is in Substrate.Coxeter.
------------------------------------------------------------------------

open import Substrate.Algebra.PointedSet.Map using (id-PointedSetMap)

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
