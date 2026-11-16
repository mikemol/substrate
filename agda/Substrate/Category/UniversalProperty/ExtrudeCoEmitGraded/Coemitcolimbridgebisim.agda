------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitcolimbridgebisim
--
-- Defines: coemit-colim-bridge-bisim
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitcolimbridgebisim where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.R.Trace.Bisim.Op
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Prefixseparates
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Zerotrace
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Tracemul
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitmuunique
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitcolimbridge
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Foundation.Eq.Cong


-- (3) coemit-colim-bridge-bisim: the finite-prefix bridge (colim-bridge) COMPOSES to the bisim via prefix-separates.
--     take n (trace-mul r s) ≡ take n zero-trace for all n (colim-bridge) ⇒ trace-mul r s ~ zero-trace. So the μ
--     finite-shadow presentation yields the ν bisim — the SAME result as coemit-mu-unique, via the finite bridge.
coemit-colim-bridge-bisim : (r s : RealTrace) → trace-mul r s ~ zero-trace
coemit-colim-bridge-bisim r s = prefix-separates (trace-mul r s) zero-trace (coemit-colim-bridge r s)
