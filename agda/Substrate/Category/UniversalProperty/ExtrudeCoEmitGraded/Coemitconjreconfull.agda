------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitconjreconfull
--
-- Defines: coemit-conj-recon-full
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitconjreconfull where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.R.Trace.Bisim.Cons
open import Substrate.Algebra.R.Trace.Bisim.Op
open import Substrate.Algebra.R.Trace.Bisim.Refl
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Algebra.R.Trace.Bisim.Refl

open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Pflip
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Bar
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans


------------------------------------------------------------------------
-- (4) coemit-conj-recon-full: the GENERAL conj-recon law with the q argument present, against RealTrace-DivStr's
--     recon (recon q b r = cons (head b) r — q is discarded by the flat reconstruction).
--     conj (recon q b r) ≈ recon (conj q) (conj b) (conj r), with ≈ := ~ (the setoid's equality).
------------------------------------------------------------------------
coemit-conj-recon-full : (q b r : RealTrace)
                       → bar (cons (RealTrace.head b) r) ~ cons (RealTrace.head (bar b)) (bar r)
head~ (coemit-conj-recon-full q b r) = refl      -- pflip (head b) on both sides
tail~ (coemit-conj-recon-full q b r) = ~-refl (bar r)
