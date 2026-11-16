------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitstardivstrconjrecon
--
-- Defines: coemit-stardivstr-conj-recon
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitstardivstrconjrecon where

open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.R.Trace.Bisim.Cons
open import Substrate.Algebra.R.Trace.Bisim.Op
open import Substrate.Algebra.R.Trace.Bisim.Refl
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Algebra.R.Trace.Bisim.Refl
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Bar
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans


-- conj-recon against RealTrace-DivStr's recon (recon q b r = cons (head b) r): bar commutes with reconstruction
-- up to ~ — the head is pflip'd, the tail is bar'd, which is exactly recon of the conjugated pieces.
coemit-stardivstr-conj-recon : (q b r : RealTrace)
                             → bar (cons (RealTrace.head b) r) ~ cons (RealTrace.head (bar b)) (bar r)
head~ (coemit-stardivstr-conj-recon q b r) = refl
tail~ (coemit-stardivstr-conj-recon q b r) = ~-refl (bar r)
