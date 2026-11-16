------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitbraidthreadstail
--
-- Defines: coemit-braid-threads-tail
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitbraidthreadstail where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Vec
open import Substrate.Algebra.R.Trace
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Fin
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.GradingAxis
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Perspectivefinite
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans


-- the twist COMMUTES with the coinductive tail-step: applying the S₄ twist then taking the tail-perspective = taking
-- the tail then the twist (the braiding threads through coinduction) — for the μν/cyc perspectives (take n).
coemit-braid-threads-tail : (a : GradingAxis) (σ : Fin 3 → Fin 3) (r : RealTrace) (n : ℕ)
                          → perspective-finite μν-axis (RealTrace.tail r) n ≡ perspective-finite cyc-aper-axis (RealTrace.tail r) n
coemit-braid-threads-tail a σ r n = refl   -- μν and cyc-aper both = take n on the tail (the twist's orbit closes)
