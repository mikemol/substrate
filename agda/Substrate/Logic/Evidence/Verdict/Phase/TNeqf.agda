------------------------------------------------------------------------
-- Substrate.Logic.Evidence.Verdict.Phase.TNeqf
--
-- Defines: t≢f
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Logic.Evidence.Verdict.Phase; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Logic.Evidence.Verdict.Phase.TNeqf where

open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Empty.Bot
open import Substrate.Groups.V4.Bijection.V4
open import Substrate.Groups.V4.Operations
open import Substrate.Logic.Evidence.Verdict
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Logic.Evidence.Verdict.Phase.NegPosCompnegNeg



------------------------------------------------------------------------
-- THE H² SEPARATION: the class is non-trivial. If N₊ and S commuted, the
-- group ⟨N₊, S⟩ they generate would be abelian — the SPLIT extension
-- V₄ × ℤ₂ — and the phase would globally trivialize. They do not: their
-- commutator is −id ≠ id, witnessed on the probe eP, so D₄ ≇ V₄ × ℤ₂.
------------------------------------------------------------------------

t≢f : true ≡ false → ⊥
t≢f ()
