------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.F2cancel
--
-- Defines: f2-cancel
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.F2cancel where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.R.Trace
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitViaTrace.CoemitTrace
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Algebra.R.Trace.Bisim.Trans
open import Substrate.Category.UniversalProperty.ExtrudeBisimUpTo
open import Substrate.Algebra.Wedge.Mul
open import Substrate.Algebra.R.Trace.Bisim.Refl
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.F2
open import Substrate.Category.Lawvere
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Anon
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Anon2
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Anon3
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans


------------------------------------------------------------------------
-- (1) coemit-torsor-atom: TorsorAtom for the V₄-coords carrier. fix→unit is the ANCHOR LAW — "only the unit fixes
--     a point" (347's D-fixed-point-is-anchor, canonically). On V4Full (= F₂², additive) cancellation is immediate:
--     v ⊕ x = x ⇒ v = 𝟘 componentwise. The anchor e = v4 𝟘 𝟘 corresponds to Axis D (v-of-axis D = e).
------------------------------------------------------------------------

-- F₂ cancellation: a ⊕ b ≡ b ⇒ a ≡ 𝟘 (the additive-group law, x ⊕ x = 𝟘).
f2-cancel : (a b : F₂) → (a ⊕₂ b) ≡ b → a ≡ 𝟘
f2-cancel 𝟘 𝟘 _ = refl
f2-cancel 𝟘 𝟙 _ = refl
f2-cancel 𝟙 𝟘 ()
f2-cancel 𝟙 𝟙 ()
