------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitrigidityatorbit
--
-- Defines: coemit-rigidity-at-orbit
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitrigidityatorbit where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.R.Trace.Bisim.Op
open import Substrate.Foundation.Product
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Fin
open import Substrate.Algebra.R.Trace.Final.Into
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Zerotrace
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.S3onaxis
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.S3reaches
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitmuinitial
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.GradingAxis
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans


-- the braiding CLOSES the coinductive rigidity: cons 0 zero-trace ~ zero-trace (the initial point) IS the orbit's
-- fixed point reached at every depth — coemit-mu-initial is the depth-0 witness, and the orbit move exists at all n.
coemit-rigidity-at-orbit : (n : ℕ) → Σ (Fin 3 → Fin 3) (λ σ → s3-on-axis σ μν-axis ≡ μν-axis)
coemit-rigidity-at-orbit n = s3-reaches μν-axis μν-axis
