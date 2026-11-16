------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.ProofEq
--
-- Defines: ProofEq
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.ProofEq where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.R.Trace.Bisim.Op
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Foundation.Hedberg.DecidableUIP
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Natuip
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)


------------------------------------------------------------------------
-- (3) coemit-proof-eq: coinductive ~-PROOF-equality. Preflight: none in-tree ⇒ a contribution.
--     A ~-proof's observable content at each step is its head~ : an ℕ-equality, and ℕ has UIP (nat-uip, Hedberg).
--     So any two ~-proofs of the SAME endpoints agree at every step — ≡ constructed as the totality (351).
------------------------------------------------------------------------
record ProofEq {r s : RealTrace} (p q : r ~ s) : Set where
  coinductive
  field
    head-eq : head~ p ≡ head~ q
    tail-eq : ProofEq (tail~ p) (tail~ q)
open ProofEq
