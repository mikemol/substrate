------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitcolimbridge
--
-- Defines: coemit-colim-bridge
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitcolimbridge where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Vec
open import Substrate.Foundation.List
open import Substrate.Algebra.R.Trace
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Fin
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Zerotrace
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Tracemul
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Perspectivefinite
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.CoemitMuCarrier
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Foundation.Eq.Cong


-- (3) coemit-colim-bridge: the TWO μ-presentations agree. CoemitMuCarrier (the trace-mul carrier, collapses to z)
--     and 336's perspective-finite (the finite prefix take n) meet: the finite prefix of a trace-mul product equals
--     the finite prefix of zero-trace (both all-zeros) — the composition-carrier's collapse IS the zero-prefix.
coemit-colim-bridge : (r s : RealTrace) (n : ℕ) → take n (trace-mul r s) ≡ take n zero-trace
coemit-colim-bridge r s zero    = refl
coemit-colim-bridge r s (suc n) = cong (_∷_ 0) (coemit-colim-bridge (RealTrace.tail r) (RealTrace.tail s) n)
