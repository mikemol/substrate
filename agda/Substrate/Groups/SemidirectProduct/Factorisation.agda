------------------------------------------------------------------------
-- Substrate.Groups.SemidirectProduct.Factorisation
--
-- The factorisation theorem σ ≈ embed (v-for σ) · s-for σ, plus the
-- supporting "V₄ ∩ Stab X = {e}" structural fact.
--
-- The proof is non-enumerative: it composes act-axis-involutive (V₄
-- being self-inverse on axes) without any (V₄ × Axis) case-split.
--
-- Removed in this slice (no external callers):
--   * factorisation-unique-V₄ — uniqueness in the (v, s)-pair sense.
--   * SemidirectFactorisation / semidirect-factorisation — the bundle
--     was prepared for downstream consumption but nothing consumed it
--     (the components v-for / s-for / s-for-fixes-D / factorisation
--     are imported directly).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.SemidirectProduct.Factorisation where

open import Substrate.Foundation.Eq using (_≡_; sym; trans; cong)

open import Substrate.Axes using (Axis; act-axis)
open import Substrate.Groups.V4 as V4 using (V₄; e)
open import Substrate.Groups.S4
  using (Permutation; _≈_; _·_)
  renaming (apply to applyₛ)
open import Substrate.Groups.V4-Embedding
  using (embed; act-axis-involutive; act-axis-as-V₄-mult;
         v-of-axis; v-of-axis-axis-of-v)

open import Substrate.Groups.SemidirectProduct.V using (v-for)
open import Substrate.Groups.SemidirectProduct.S using (s-for)

------------------------------------------------------------------------
-- The factorisation: σ ≈ embed (v-for σ) · s-for σ.
--
-- s-for σ ≡ embed (v-for σ) · σ, so the composition collapses by
-- V₄-involutivity: embed (v-for σ) · (embed (v-for σ) · σ) ≈ σ.
------------------------------------------------------------------------

factorisation :
  (σ : Permutation) →
  σ ≈ (embed (v-for σ) · s-for σ)
factorisation σ x =
  sym (act-axis-involutive (v-for σ) (applyₛ σ x))

------------------------------------------------------------------------
-- V₄ ∩ Stab(X) = {e}.
--
-- No non-identity V₄ element fixes any axis. The proof composes
-- act-axis-as-V₄-mult + v-of-axis-axis-of-v + V4.·-right-cancel-ε —
-- one algebraic chain, no (V₄ × Axis) enumeration.
------------------------------------------------------------------------

V₄-cap-Stab-trivial :
  (X : Axis) (v : V₄) → act-axis v X ≡ X → v ≡ e
V₄-cap-Stab-trivial X v stab =
  V4.·-right-cancel-ε v (v-of-axis X)
    (trans (sym (v-of-axis-axis-of-v (v V4.· v-of-axis X)))
    (trans (cong v-of-axis (sym (act-axis-as-V₄-mult v X)))
           (cong v-of-axis stab)))
