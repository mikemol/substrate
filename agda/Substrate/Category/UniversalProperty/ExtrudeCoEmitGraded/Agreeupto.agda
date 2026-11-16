------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Agreeupto
--
-- Defines: agree-upto
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Agreeupto where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.R.Trace
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Fin
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.R
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Obs
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Prefixseparates
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Foundation.Eq.Cong


------------------------------------------------------------------------
-- coemit-shrinking-phi: a genuinely SHRINKING grading (contrast 319's degenerate Φ-obs, νΦ-obs=R⁰). Fix a
-- reference trace r; the fiber at grade n = the traces AGREEING with r on the first n digits. This SHRINKS as n
-- grows (take-drop: agreeing on suc n ⇒ agreeing on n), and its LIMIT (all grades) IS the bisimilarity class of
-- r (agree-limit = prefix-separates). So THIS refinement's gfp is SUBSTANTIVE (the ~-class), unlike Φ-obs's R⁰.
------------------------------------------------------------------------
agree-upto : ℕ → RealTrace → RealTrace → Set
agree-upto n r t = take n t ≡ take n r
