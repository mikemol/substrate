------------------------------------------------------------------------
-- Substrate.Lifecycle.Residue
--
-- Defines: Residue
-- ⟡cap-128-forcing: one lemma, one elaboration unit.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Lifecycle.Residue where

open import Substrate.Foundation.Nat.Nat


------------------------------------------------------------------------
-- THE RESIDUE AT A BOUNDARY: drawn but not yet fed.
--
-- ⚑ THIS IS THE WEDGE, AND I BUILT THE SPECIAL CASE WITHOUT NAMING THE
-- GENERATOR (user, 2026-08-06: *"it's like watching the LehmerPath arc all
-- over again"*). `Substrate.Algebra.Wedge.Graded.DivStr` already declares
--
--     recon : (n : ℕ) → C n → R n → C (suc n)
--
-- a grade-n base plus a RESIDUE reconstructing grade n+1 — and
-- `Graded.Wedge` adds the witness `a ≡ recon n b rem` that makes it an exact
-- decomposition rather than two unrelated numbers. An `Actor` is that: its
-- feed position is the base, its draw position the reconstructed grade, and
-- the gap between them the residue.
--
-- ⚑ AND THE REPO KEEPS ARRIVING AT ONE STRUCTURE UNDER FOUR SPELLINGS:
-- `Chain` (ε / _▷_), `Pipe` ([] / _∷_), `LehmerPath` (start / _◂_ with a
-- BOUNDED digit `Fin (suc k)`), and now this. Memory
-- [[adjunction-is-the-wedge-residue-counit]] records the identity outright:
-- `a = recon q b r`, where the residue IS the Lehmer digit, the orientation,
-- the counit defect. The reuse-search should have fired on "cons-list with a
-- position index" before `Chain` was written, and again before `Interlock`.
--
-- ⚑ WHAT THE RESIDUE MEANS OPERATIONALLY, and why it is not decoration: it
-- is exactly the in-flight work an actor holds — read from upstream, not yet
-- released downstream. A residue of zero is an actor fully caught up (its
-- feed has reached its draw); a growing residue is backpressure. The scalar
-- floor could report neither, because it kept only one of the two positions.
------------------------------------------------------------------------

Residue : Set
Residue = ℕ
