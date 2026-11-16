------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitagreesisbisimfwd
--
-- Defines: coemit-agrees-is-bisim-fwd
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitagreesisbisimfwd where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.R.Trace.Bisim.Op
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Prefixseparates
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Foundation.Eq.Cong
open import Substrate.Algebra.F2.AES.KAT.Pre


------------------------------------------------------------------------
-- coemit CrossMul as GENUINE two-carrier mixing (operator: "CrossMul's purpose is to mix two carriers so their
-- terms lift into a common carrier space" — the diagonal was degenerate). The TWO carriers are coemit's TWO
-- FRAMINGS: A = the μ-framing (finite prefixes, take n — the halting/algebraic side) and B = the ν-framing
-- (RealTrace stream — the ~/coinductive side); they lift into the COMMON carrier List ℕ (finite observations),
-- and agreement there ⟺ bisimilarity. V₄'s 3 involutions = the 3 grading axes (μ/ν, head/tail, cyclic/aperiodic).
------------------------------------------------------------------------

-- (3, GENUINE) coemit-agrees-is-bisim: the two DISTINCT framings (μ = finite prefix take, ν = the stream) AGREE
-- in the common carrier List ℕ at EVERY grade ⟺ bisimilar. This is the REAL agreement (not the trivial diagonal):
-- lift-μ n r = take n r (the finite/halting framing); lift-ν = the stream via all its prefixes; agree ⟺ ~.
coemit-agrees-is-bisim-fwd : (r t : RealTrace) → ((n : ℕ) → take n t ≡ take n r) → t ~ r
coemit-agrees-is-bisim-fwd r t pre = prefix-separates t r pre
