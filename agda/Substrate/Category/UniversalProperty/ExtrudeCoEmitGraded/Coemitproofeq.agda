------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitproofeq
--
-- Defines: coemit-proof-eq
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitproofeq where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.R.Trace.Bisim.Op
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Foundation.Hedberg.DecidableUIP
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Natuip
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.ProofEq
open ProofEq
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)


-- ~-proof-irrelevance, CONSTRUCTED: any two proofs of r ~ s agree at every step (head by UIP, tail corecursively).
coemit-proof-eq : {r s : RealTrace} (p q : r ~ s) → ProofEq p q
head-eq (coemit-proof-eq p q) = nat-uip (head~ p) (head~ q)
tail-eq (coemit-proof-eq p q) = coemit-proof-eq (tail~ p) (tail~ q)
