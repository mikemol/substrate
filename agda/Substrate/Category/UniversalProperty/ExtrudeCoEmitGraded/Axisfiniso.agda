------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Axisfiniso
--
-- Defines: axis-fin-iso
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Axisfiniso where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Fin
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.GradingAxis
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Axisfin
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Finaxis
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans


-- axis↔fin is a round-trip iso (the 3 axes ARE Fin 3, S₃'s carrier) — so S₃ genuinely permutes the 3 axes.
axis-fin-iso : (a : GradingAxis) → fin→axis (axis→fin a) ≡ a
axis-fin-iso μν-axis        = refl
axis-fin-iso head-tail-axis = refl
axis-fin-iso cyc-aper-axis  = refl
