{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.MuSolverUnique — ⟡mu-solver-unique: the μ solver
-- (mu-backed, 170/171) is the UNIQUE admissible solution. Existence is registered; this
-- adds the uniqueness half via solver-unique.
--
-- THE KEY (the μ side's nicer half): mu-UP's Witness is v ≡ collapse-fold(trace) — a
-- ≡-EQUATION that SELF-DETERMINES the target. So WitnessUnique holds with Adm = ⊤ (NO
-- bound): two witnesses t₁ ≡ fold, t₂ ≡ fold give t₁ ≡ t₂ by trans/sym — EXACTLY the
-- eq-witness-unique proof. Contrast the wedge side (wedge-witness-unique), whose Witness
-- is the wedge-eq and needs Adm = smallness (r < b) to pin (q, r). The either/or "μ's
-- unconditional uniqueness vs the wedge's bounded uniqueness" dissolves: BOTH are
-- WitnessUnique relative to the Adm the Witness REQUIRES — μ's ≡-Witness requires none
-- (⊤), the wedge's requires the bound. (This is the μ ≡-unique / ν bisim-unique split's
-- INDUCTIVE, unconditional half.)
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.MuSolverUnique where

open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans)
open import Substrate.Foundation.Unit using (⊤; tt)
open import Substrate.Algebra.Wedge using (ℕ-div)
open import Substrate.Category.UniversalProperty using (UPArrow; Source; Target; Witness)
open import Substrate.Category.UniversalProperty.Backed using (BackedUP; arrow; solve)
open import Substrate.Category.UniversalProperty.Unique using (WitnessUnique; solver-unique)
import Substrate.Category.UniversalProperty.MuBacked as Mu

-- the μ solver (the registered instance, 170/171 — already the top-level ℕ-div BackedUP).
mu-backed-ℕ : BackedUP
mu-backed-ℕ = Mu.mu-backed

------------------------------------------------------------------------
-- ① μ WITNESS-UNIQUENESS, UNCONDITIONAL (Adm = ⊤). The Witness v ≡ collapse-fold(trace)
-- self-determines v, so two witnesses coincide with NO bound — trans (sym w₁) w₂.
------------------------------------------------------------------------
mu-witness-unique : WitnessUnique (arrow mu-backed-ℕ) (λ _ _ → ⊤)
mu-witness-unique s t₁ t₂ _ _ w₁ w₂ = trans w₁ (sym w₂)

------------------------------------------------------------------------
-- ② THE μ SOLVER IS THE UNIQUE ADMISSIBLE SOLUTION. solver-unique feeds existence
-- (mu-backed-ℕ's solve/solves) ⊕ mu-witness-unique: any admissible t witnessing s IS
-- the solver's output. Adm = ⊤ everywhere (tt), so it holds for EVERY t (no bound).
------------------------------------------------------------------------
mu-solver-unique :
  (s : Source (arrow mu-backed-ℕ))
  (t : Target (arrow mu-backed-ℕ)) →
  Witness (arrow mu-backed-ℕ) s t →
  t ≡ solve mu-backed-ℕ s
mu-solver-unique s t wit-t =
  solver-unique mu-backed-ℕ (λ _ _ → ⊤) mu-witness-unique s tt t tt wit-t

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — μ's uniqueness is unconditional): mu-backed registered
-- EXISTENCE (170/171); mu-solver-unique adds UNIQUENESS — and because mu-UP's Witness is
-- a ≡-equation (v ≡ the fold value), the uniqueness is UNCONDITIONAL (Adm = ⊤), the SAME
-- trans/sym proof as eq-witness-unique. So the μ solver is not just A solver but THE
-- unique admissible solution, with no bound needed. This is the fold side's nicer half of
-- the μ ≡-unique / ν bisim-unique asymmetry: the initial-algebra fold's uniqueness is
-- inductive ≡ (trace-fold-unique / the ≡-Witness), needing no smallness window, whereas
-- the wedge/ν side needs Adm = r < b (wedge-witness-unique) or bisim (ana-unique). The
-- "unconditional vs bounded uniqueness" either/or dissolves into WitnessUnique-relative-
-- to-Adm: μ's ≡-Witness requires Adm = ⊤; the wedge's requires the bound.
------------------------------------------------------------------------
