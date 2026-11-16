------------------------------------------------------------------------
-- Substrate.FUSep.FUSepQNf.AppendFT
--
-- Defines: appendFT
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.FUSep.FUSepQNf; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.FUSep.FUSepQNf.AppendFT where

open import Substrate.Foundation.Nat.Nat
open import Substrate.FUSep.FUSepQBridge.Anon
open import Substrate.FUSep.FUSepQBridge.Cong
open import Substrate.FUSep.FUSepQBridge.Cong2
open import Substrate.FUSep.FUSepQBridge.Eqtrans
open import Substrate.FUSep.FUSepQSKI    using (atom; app) renaming (Tm-QSKI to Tm-QSKI)
open import Substrate.Foundation.Eq
open import Substrate.FUSep.FUSepQNf.Recon
open import Substrate.FUSep.FUSepQNf.BaseState
open import Substrate.FUSep.FUSepQSKI



------------------------------------------------------------------------
-- APPEND = the SPPF path CONCATENATION: graft the second-phase trace onto the
-- base of the first. reduction (t ⇒* nf) ++ peel (nf ↓ atom) = ONE trace (t → atom)
-- over the common carrier, EVERY intermediate exposed as a node — the faithful
-- record (no Tm→Tm shortcut collapses a step). Both phases, one recon.
------------------------------------------------------------------------
appendFT : ∀ {s} (t : FinTrace recon s) → FinTrace recon (baseState t) → FinTrace recon s
appendFT (base s)           k = k
appendFT (step h s' eq rest) k = step h s' eq (appendFT rest k)
