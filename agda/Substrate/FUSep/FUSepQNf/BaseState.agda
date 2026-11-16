------------------------------------------------------------------------
-- Substrate.FUSep.FUSepQNf.BaseState
--
-- Defines: baseState
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.FUSep.FUSepQNf; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.FUSep.FUSepQNf.BaseState where

open import Substrate.Foundation.Nat.Nat
open import Substrate.FUSep.FUSepQBridge.Anon
open import Substrate.FUSep.FUSepQBridge.Cong
open import Substrate.FUSep.FUSepQBridge.Cong2
open import Substrate.FUSep.FUSepQBridge.Eqtrans
open import Substrate.FUSep.FUSepQSKI    using (atom; app) renaming (Tm-QSKI to Tm-QSKI)
open import Substrate.Foundation.Eq
open import Substrate.FUSep.FUSepQNf.Recon
open import Substrate.FUSep.FUSepQSKI



------------------------------------------------------------------------
-- baseState: where the trace's `base` sits (the nf, for a reduction phase).
------------------------------------------------------------------------
baseState : ∀ {s} → FinTrace recon s → Tm-QSKI
baseState {s} (base _)          = s
baseState     (step _ _ _ rest)  = baseState rest
