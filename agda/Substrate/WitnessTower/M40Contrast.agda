------------------------------------------------------------------------
-- Σ-SEAM-GLUE / ΞB3 — the contrast is REAL: S₄ is genuinely excluded.
--
-- SEAM_GLUE B3: with chirality REMOVED and transpositions in (the pure-S₄
-- primitives), the closure is S₄ — which HAS order-4 elements (the S₄
-- signature). A₄×ℤ₂ has NONE (M40Closure.no-order-4: g⁴=ι ⟹ g²=ι). So the
-- A₄×ℤ₂-vs-S₄ difference tracks exactly the chirality generator:
--   * chirality  — order-2 and CENTRAL (M40Closure.central-χ, ΞB2i)  → A₄×ℤ₂, NO order-4.
--   * a transposition — order-2, NON-central; its presence creates order-4 → S₄.
--
-- THIS FILE witnesses the S₄ side: an explicit order-EXACTLY-4 element of
-- Sym(V₄) = S₄ (a 4-cycle on the four masks {e,α,β,γ}). The pure-S₄
-- primitives close to all of Sym(V₄) (scratch/spectral_view.py
-- verify_pure_s4_primitives_generate_s4), so this element is in that closure.
--
-- SCOPE (not overclaimed): this gives the distinguishing INVARIANT
-- (S₄ has a genuine order-4 element; A₄×ℤ₂ does not). The fully machine-checked
-- ¬(A₄×ℤ₂ ≅ S₄) additionally needs an order-preserved-under-iso transport — a
-- further step, NOT claimed here. The invariant + no-order-4 are both in code.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.M40Contrast where

import Substrate.Groups.V4 as V4
open V4 using (V₄; e; α; β; γ)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Empty using (⊥)
open import Substrate.Foundation.Product using (_×_; _,_)
open import Substrate.Category.Coalgebra using (Endomap)
open import Substrate.Category.Coalgebra.FiniteOrder using (HasOrder; iterate)
-- cited for the contrast (the A₄×ℤ₂ side has no genuine order-4 element):
open import Substrate.WitnessTower.M40Closure using (no-order-4)

------------------------------------------------------------------------
-- The 4-cycle on the four masks: e → α → β → γ → e.  An element of Sym(V₄)=S₄.
------------------------------------------------------------------------

fc : Endomap V₄
fc e = α
fc α = β
fc β = γ
fc γ = e

-- fc⁴ = id (order divides 4) — pointwise over the four masks.
fc-order-4 : HasOrder fc 4
fc-order-4 e = refl
fc-order-4 α = refl
fc-order-4 β = refl
fc-order-4 γ = refl

-- ... but fc² ≠ id: fc² moves e to β, and β ≢ e (distinct V₄ constructors).
-- So fc has order EXACTLY 4 — the S₄ signature A₄×ℤ₂'s no-order-4 forbids.
fc-not-order-2 : iterate 2 fc e ≡ e → ⊥
fc-not-order-2 ()

-- fc⁴ = id makes fc a permutation (its inverse is fc³); together with fc²≠id it
-- is a genuine order-4 element. This is what Sym(V₄)=S₄ has and A₄×ℤ₂ lacks.
S₄-has-genuine-order-4 : HasOrder fc 4 × (iterate 2 fc e ≡ e → ⊥)
S₄-has-genuine-order-4 = fc-order-4 , fc-not-order-2

-- The contrast, in one place: A₄×ℤ₂'s `no-order-4` (g⁴=ι ⟹ g²=ι) FORBIDS exactly
-- the shape S₄-has-genuine-order-4 exhibits (fc⁴=id WITHOUT fc²=id). The two are
-- the A₄×ℤ₂-vs-S₄ distinguishing invariant; `no-order-4` is re-exported as the
-- A₄×ℤ₂ side so both live together.
a4z2-no-order-4 = no-order-4
