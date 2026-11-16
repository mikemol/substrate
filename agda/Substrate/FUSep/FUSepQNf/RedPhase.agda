------------------------------------------------------------------------
-- Substrate.FUSep.FUSepQNf.RedPhase
--
-- Defines: redPhase
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.FUSep.FUSepQNf; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.FUSep.FUSepQNf.RedPhase where

open import Substrate.Foundation.Nat.Nat
open import Substrate.FUSep.FUSepQBridge.Anon
open import Substrate.FUSep.FUSepQBridge.Cong
open import Substrate.FUSep.FUSepQBridge.Cong2
open import Substrate.FUSep.FUSepQBridge.Eqtrans
open import Substrate.FUSep.FUSepQSKI    using (atom; app) renaming (Tm-QSKI to Tm-QSKI)
open import Substrate.Foundation.Eq
open import Substrate.FUSep.FUSepQNf.Wit
open import Substrate.FUSep.FUSepQNf.Recon
open import Substrate.FUSep.FUSepQNf.Private
open import Substrate.FUSep.FUSepQSKI


redPhase : FinTrace recon t
redPhase = step (redW t) nf refl (base nf)

-- peel phase: nf peels off its argument 1₀, backpointer = 1₀ (recomputable).
