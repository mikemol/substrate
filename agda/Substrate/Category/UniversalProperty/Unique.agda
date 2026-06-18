------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.Unique
--
-- The UNIVERSALITY (uniqueness) half of a universal property — the layer
-- BackedUP does NOT carry. BackedUP certifies a non-vacuous SOLVER
-- (existence + content); it says nothing about uniqueness. This module
-- supplies the missing half, and supplies it HONESTLY: uniqueness of the
-- solution is available only RELATIVE TO A BOUND (an admissibility predicate
-- on targets). The wedge is the canonical witness that the bound is
-- essential — Euclidean division has a UNIQUE (q, r) only once r is bounded
-- (r < b); drop the bound and (q, r) and (q−1, r+b) both decompose a.
--
--   WitnessUnique U Adm : at most one admissible target witnesses each
--                         source. Adm IS the gauge certificate / bound.
--
-- Instances (the two corners of "how much bound is needed"):
--   * wedge-witness-unique — the BOUNDED exemplar. Adm (a,b)(q,r) = r < b,
--     via WedgeUP.wedge-unique (← BoundedIso.recon-bounded-unique ←
--     divmod-unique). For divisor 0 the bound r < 0 is uninhabited, so it is
--     vacuously unique; for suc b it is the real arithmetic uniqueness.
--   * eq-witness-unique — the UNCONDITIONAL corner. eq-UP's Witness is _≡_,
--     so two witnesses coincide with NO bound (Adm ≡ ⊤).
--
-- And the bridge to BackedUP: solver-unique shows a backed solver IS the
-- unique admissible solution (existence ⊕ WitnessUnique ⟹ "the" solution).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.Unique where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _<_)
open import Substrate.Foundation.Unit using (⊤; tt)
open import Substrate.Foundation.Eq using (_≡_; sym; trans; cong₂)
open import Substrate.Foundation.Product using (_×_; _,_; proj₁; proj₂)
open import Substrate.Category.UniversalProperty using (UPArrow; Source; Target; Witness)
open import Substrate.Category.UniversalProperty.Vacuity using (eq-UP)
open import Substrate.Category.UniversalProperty.Backed using (BackedUP; arrow; solve; solves)
open import Substrate.Category.UniversalProperty.WedgeUP using (wedge-UP; wedge-unique)

------------------------------------------------------------------------
-- 1. WitnessUnique — uniqueness of the witnessing target, relative to a
--    bound Adm. THE common structure under the wedge's bounded uniqueness.
------------------------------------------------------------------------

WitnessUnique : (U : UPArrow) → (Source U → Target U → Set) → Set
WitnessUnique U Adm =
  (s : Source U) (t₁ t₂ : Target U)
  → Adm s t₁ → Adm s t₂ → Witness U s t₁ → Witness U s t₂ → t₁ ≡ t₂

------------------------------------------------------------------------
-- 2. The wedge: the BOUNDED exemplar (the bound is ESSENTIAL).
------------------------------------------------------------------------

wedge-witness-unique : WitnessUnique wedge-UP (λ ab qr → proj₂ qr < proj₂ ab)
-- divisor 0: the bound r < 0 = suc r ≤ 0 is uninhabited → vacuously unique.
wedge-witness-unique (a , zero)  (q₁ , r₁) _         ()  _   _  _
-- divisor suc b: the genuine arithmetic uniqueness, via wedge-unique.
wedge-witness-unique (a , suc b) (q₁ , r₁) (q₂ , r₂) lt₁ lt₂ w₁ w₂ =
  cong₂ _,_ (proj₁ u) (proj₂ u)
  where u = wedge-unique a b q₁ r₁ q₂ r₂ lt₁ lt₂ w₁ w₂

------------------------------------------------------------------------
-- 3. The equality UP: the UNCONDITIONAL corner (no bound needed).
------------------------------------------------------------------------

eq-witness-unique : WitnessUnique eq-UP (λ _ _ → ⊤)
eq-witness-unique s t₁ t₂ _ _ w₁ w₂ = trans (sym w₁) w₂

------------------------------------------------------------------------
-- 4. Bridge to BackedUP: existence (solve/solves) ⊕ WitnessUnique ⟹ the
--    backed solver IS the unique admissible solution.
------------------------------------------------------------------------

solver-unique :
  (b : BackedUP) (Adm : Source (arrow b) → Target (arrow b) → Set) →
  WitnessUnique (arrow b) Adm →
  (s : Source (arrow b)) → Adm s (solve b s) →
  (t : Target (arrow b)) → Adm s t → Witness (arrow b) s t →
  t ≡ solve b s
solver-unique b Adm wu s adm-solve t adm-t wit-t =
  wu s t (solve b s) adm-t adm-solve wit-t (solves b s)

------------------------------------------------------------------------
-- 5. The bound is a finite WINDOW, not a wall — the coinductive escape.
--
-- WitnessUnique's `Adm` is a finiteness bound: for the wedge it is the
-- HALTING condition r < b. That is not the end of uniqueness — it is the
-- finite/halting reading of ONE universal property whose unbounded reading
-- the repo already proves COINDUCTIVELY and constructively:
--
--   bounded / halting  (ℚ, finite trace)   : WitnessUnique here, inductive `≡`.
--   unbounded / non-halting (R, suspended generator) : `Final.ana-unique` —
--      ANY coalgebra morphism into RealTrace is bisimilar (`Bisim._~_`) to the
--      anamorphism, the TERMINAL-coalgebra universal property by guarded
--      coinduction. Bisimilarity IS equality in the terminal coalgebra (the
--      dual of induction), so no finiteness bound is needed there.
--
-- They are the two faces of the SAME wedge coalgebra (Algebra.R.Trace.
-- WedgeBridge: the bounded ℕ-wedge is its halting trace, RealTrace its
-- non-halting one). So `Adm` marks where the halting view applies; past it,
-- uniqueness lives at the generator level as a bisimulation, not as a wall.
-- See [[feedback-suspended-generators-not-approximations]],
-- [[feedback-finite-window-constructive-lem]].
------------------------------------------------------------------------
