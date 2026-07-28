------------------------------------------------------------------------
-- Substrate.WitnessTower.SharedMiddle
--
-- BUILD (not assert), on the SUBSTRATE'S REAL V₄ PRIMITIVE: three V₂'s
-- with the middle one participating in a V₄ role below and above.
--
-- The V₂ links are left-translations by the three V₄ involutions
-- α, β, γ (the double-transpositions of V₄ = Substrate.Groups.V4). Each
-- is an order-2 endomap of V₄:
--   (g ·_) ∘ (g ·_) = (g · g) ·_ = ε ·_ = id        (V₄ is exponent-2)
-- proved from the substrate's own inv-left / ·-assoc / ε-left
-- (V4.Axioms), with inv g = g (V4.Operations: every element self-inverse).
--
-- α, β, γ are the three V₂ subgroups of ONE V₄; using them as links makes
-- "two V₄ roles sharing a middle V₂" concrete: β is the shared link.
-- (This is the substrate-primitive replacement for the earlier Bool³ toy;
-- it cites V4's certified group axioms, not ad-hoc Bool flips.)
--
-- OPEN (POSITED, not built): that two DISTINCT V₄s (the gauge/interface
-- V₄s of S₄ = V₄ ⋊ S₃, dossier B3) intersect in EXACTLY this middle V₂
-- (the seam). That needs the S₄ structure + a subgroup-intersection
-- statement, which is not constructed here.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.SharedMiddle where

import Substrate.Groups.V4.Operations as V4
open import Substrate.Groups.V4.Bijection using (V₄; e; α; β; γ)
open import Substrate.Groups.V4.Operations using (_·_; inv)
open import Substrate.Groups.V4.Axioms.Assoc using (·-assoc)
open import Substrate.Groups.V4.Axioms.EpsilonLeft using (ε-left)
open import Substrate.Groups.V4.Axioms.InvLeft using (inv-left)
open import Substrate.Groups.V4.Axioms.Comm using (·-comm)
open import Substrate.Foundation.Eq using (_≡_; refl; trans; sym; cong)

open import Substrate.Category.Coalgebra using (Endomap; _∘E_)
open import Substrate.Category.Coalgebra.FiniteOrder using (HasOrder)
open import Substrate.Category.Coalgebra.StructuralGCD using (Commute)
open import Substrate.Category.Coalgebra.StructuralGCD.Properties
  using (HasOrder-compose-commute)

------------------------------------------------------------------------
-- 1. Left-translation by a V₄ element, as an endomap.
------------------------------------------------------------------------

trans-by : V₄ → Endomap V₄
trans-by g x = g · x

------------------------------------------------------------------------
-- 2. Generic: left-translation by any g is a V₂.
--
--   iterate 2 (g·_) x = g · (g · x)
--                     ≡ (g · g) · x      [·-assoc, sym]
--                     ≡ (inv g · g) · x  [inv g = g, refl — exponent-2]
--                     ≡ ε · x            [inv-left g]
--                     ≡ x                [ε-left]
-- (inv g ≡ g definitionally: V4.Operations inv x = x.)
------------------------------------------------------------------------

trans-by-V₂ : (g : V₄) → HasOrder (trans-by g) 2
trans-by-V₂ g x =
  trans (sym (·-assoc g g x))
        (trans (cong (λ z → (z · g) · x) (refl {x = g}))  -- inv g ≡ g
        (trans (cong (_· x) (inv-left g))                  -- (inv g · g) ≡ ε
               (ε-left x)))

------------------------------------------------------------------------
-- 3. The three V₂ links = translation by α, β, γ. Each proved a V₂.
------------------------------------------------------------------------

Lα Lβ Lγ : Endomap V₄
Lα = trans-by α
Lβ = trans-by β     -- the MIDDLE link (shared)
Lγ = trans-by γ

Lα-V₂ : HasOrder Lα 2
Lα-V₂ = trans-by-V₂ α
Lβ-V₂ : HasOrder Lβ 2
Lβ-V₂ = trans-by-V₂ β
Lγ-V₂ : HasOrder Lγ 2
Lγ-V₂ = trans-by-V₂ γ

------------------------------------------------------------------------
-- 4. Links commute (V₄ is abelian — ·-comm), so adjacent pairs compose
--    to V₄-order. Lβ is the literal shared factor of both pairs.
------------------------------------------------------------------------

-- commutativity of translations: (g·_)∘(h·_) = (h·_)∘(g·_) pointwise,
-- from V₄ commutativity + associativity.
trans-commute : (g h : V₄) → Commute (trans-by g) (trans-by h)
trans-commute g h = record { commute = λ x →
  trans (sym (·-assoc g h x))
        (trans (cong (_· x) (·-comm g h)) (·-assoc h g x)) }

V₄-lower : HasOrder (Lα ∘E Lβ) 4     -- ⟨α-link, β-link⟩
V₄-lower = HasOrder-compose-commute {γ₁ = Lα} {γ₂ = Lβ} {k₁ = 2} {k₂ = 2}
             (trans-commute α β) Lα-V₂ Lβ-V₂

V₄-upper : HasOrder (Lβ ∘E Lγ) 4     -- ⟨β-link, γ-link⟩
V₄-upper = HasOrder-compose-commute {γ₁ = Lβ} {γ₂ = Lγ} {k₁ = 2} {k₂ = 2}
             (trans-commute β γ) Lβ-V₂ Lγ-V₂

------------------------------------------------------------------------
-- 5. The shared middle: Lβ is definitionally the same endomap in both
--    V₄ compositions. (The deeper "intersection = ⟨Lβ⟩ exactly" is the
--    POSITED seam claim — not built here.)
------------------------------------------------------------------------

shared-middle : Lβ ≡ Lβ
shared-middle = refl
