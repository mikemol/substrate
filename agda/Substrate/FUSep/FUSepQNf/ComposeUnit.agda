------------------------------------------------------------------------
-- Substrate.FUSep.FUSepQNf.ComposeUnit
--
-- Defines: compose-unit
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.FUSep.FUSepQNf; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.FUSep.FUSepQNf.ComposeUnit where

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
open import Substrate.FUSep.FUSepQNf.AppendFT
open import Substrate.FUSep.FUSepQSKI



------------------------------------------------------------------------
-- THE COMPOSED UNIT, free from fintrace-unit: reconstruct recovers the START t of
-- the whole reduction-then-peel path — reversibility carried end to end by the
-- backpointers (redW parents + peelW args), over the ONE common carrier. The
-- non-normal term t round-trips: the composition IS a plain FinTrace, so the unit
-- is not a new theorem — it is fintrace-unit, once the carrier is constructed.
------------------------------------------------------------------------
compose-unit : ∀ {s} (red : FinTrace recon s) (peel : FinTrace recon (baseState red))
             → reconstruct recon (appendFT red peel) ≡ s
compose-unit red peel = fintrace-unit recon (appendFT red peel)
