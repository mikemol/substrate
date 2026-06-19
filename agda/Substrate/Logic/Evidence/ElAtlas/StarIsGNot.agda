------------------------------------------------------------------------
-- Substrate.Logic.Evidence.ElAtlas.StarIsGNot  (Ξ★.2 — MECHANIZE-STAR rung 2)
--
-- ★ = G_NOT, in --safe Agda (POINT_CLOUD_HODGE_FORMALIZATION §4.3-4.4).
--
-- The abstract strictification (§4.1-4.2) checked ★ as a *chosen* involution (a
-- diagonal in an orthogonalised basis). The Kirchhoff/g-calculus grounding
-- FORCES it instead: ★ is G_NOT — the reciprocal / numerator-denominator swap,
-- the conductance↔resistance (series↔parallel) duality — and ★²=id is then the
-- swap being its own inverse, a STRUCTURAL fact (it reduces by `refl` on the
-- num/den swap), not a property of a posited orthogonal matrix.
--
-- ★ := GValueAsQ.recip (= G_NOT = the antipode G(¬P)). Discharged:
--   * ★-involution      ★²=id (§4.1/4.3): recip∘recip ≡ id on every G-value —
--                        the swap is self-inverse, forced from the model.
--   * ★-fixes-balance    §4.2 analog: ★ fixes the self-dual axis G=1 (the
--                        balance point, Nedge L=0; numerator=denominator), the
--                        G-value image of "★ fixes the witness axis".
--   * ★-swaps-series∥    §4.4: ★(G_OR) ≈ G_AND(★,★) — ★ exchanges parallel
--                        (G_OR=Σ) and series (G_AND) conductance. This IS
--                        GValueAsQ.demorgan (re-exported), the exact DeMorgan.
--
-- NOT claimed: a pole-swap G→0 ↔ G→∞. In this TOTAL affine ℚ encoding recip
-- fixes 0 (the junk clause), so the projective center↔periphery exchange (§5)
-- is not an identity here; it composes with the rung-3 center in Ξ★.3.
--
-- Sibling: Ξ★.1 = ElAtlas.CenterWitness (the rung-3 cycle-space witness/centre,
-- over ℤ). Ξ★.3 will compose the two: the rung-3 centre (witness line) IS this
-- ★=G_NOT-fixed locus (the single center-is-★ identity, §7.1, still open).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Logic.Evidence.ElAtlas.StarIsGNot where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Algebra.Q using (ℚ)
open import Substrate.Algebra.Q.Equiv using (_≈ℚ_)
open import Substrate.Logic.Evidence.GValueAsQ
  using (gvalue; recip; balance; antipode-of; gor; gand; demorgan)

------------------------------------------------------------------------
-- ★ IS G_NOT: the reciprocal / num-den swap (the conductance↔resistance fold).
------------------------------------------------------------------------

★ : ℚ → ℚ
★ = recip

------------------------------------------------------------------------
-- §4.1/4.3 — ★² = id: the swap is its own inverse, on every positive G-value.
-- This is `refl`: recip (mkℚ (+ suc n) d) = mkℚ (+ suc d) n swaps the
-- numerator-predecessor and denominator-index, so applying it twice restores
-- the pair. The involution is STRUCTURAL (forced by the swap), not posited.
------------------------------------------------------------------------

★-involution : (na' db : ℕ) → ★ (★ (gvalue na' db)) ≡ gvalue na' db
★-involution na' db = refl

------------------------------------------------------------------------
-- §4.2 (analog) — ★ FIXES THE SELF-DUAL AXIS G = 1: the balance point
-- (numerator = denominator, class 1, Nedge L = 0). Its G-value gvalue n n is a
-- ★-fixed point — the g-calculus image of "★ fixes the witness axis".
------------------------------------------------------------------------

★-fixes-balance : (n : ℕ) → ★ (gvalue n n) ≡ gvalue n n
★-fixes-balance n = refl

★-fixes-1 : ★ balance ≡ balance        -- balance = gvalue 0 0 = 1ℚ
★-fixes-1 = refl

------------------------------------------------------------------------
-- §4.4 — ★ SWAPS SERIES ↔ PARALLEL: ★(G_OR(G₁,G₂)) ≈ G_AND(★ G₁, ★ G₂).
-- This is exactly GValueAsQ.demorgan (the exact DeMorgan over ≈ℚ); re-exported
-- here as the ★ statement.
------------------------------------------------------------------------

★-swaps-series∥parallel :
  (na'₁ db₁ na'₂ db₂ : ℕ) →
  ★ (gor (gvalue na'₁ db₁) (gvalue na'₂ db₂))
  ≈ℚ gand (★ (gvalue na'₁ db₁)) (★ (gvalue na'₂ db₂))
★-swaps-series∥parallel = demorgan
