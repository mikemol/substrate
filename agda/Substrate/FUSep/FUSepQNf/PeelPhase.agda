------------------------------------------------------------------------
-- Substrate.FUSep.FUSepQNf.PeelPhase
--
-- Defines: peelPhase
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.FUSep.FUSepQNf; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.FUSep.FUSepQNf.PeelPhase where

open import Substrate.Foundation.Nat.Nat
open import Substrate.FUSep.FUSepQBridge.Anon
open import Substrate.FUSep.FUSepQBridge.Cong
open import Substrate.FUSep.FUSepQBridge.Cong2
open import Substrate.FUSep.FUSepQBridge.Eqtrans
open import Substrate.FUSep.FUSepQSKI    using (atom; app) renaming (Tm-QSKI to Tm-QSKI)
open import Substrate.Foundation.Eq
open import Substrate.FUSep.FUSepQNf.Wit
open import Substrate.FUSep.FUSepQNf.Recon
open import Substrate.FUSep.FUSepQNf.BaseState
open import Substrate.FUSep.FUSepQNf.Private
open import Substrate.FUSep.FUSepQNf.RedPhase
open import Substrate.FUSep.FUSepQSKI


peelPhase : FinTrace recon (baseState redPhase)
peelPhase = step (peelW 1₀) 0₀ refl (base 0₀)

-- the whole path round-trips t — end to end, non-normal term, ONE recon.
