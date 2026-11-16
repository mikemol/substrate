------------------------------------------------------------------------
-- Substrate.FUSep.FUSepQNf.Op
--
-- Defines: _
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.FUSep.FUSepQNf; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.FUSep.FUSepQNf.Op where

open import Substrate.Foundation.Nat.Nat
open import Substrate.FUSep.FUSepQBridge.Anon
open import Substrate.FUSep.FUSepQBridge.Cong
open import Substrate.FUSep.FUSepQBridge.Cong2
open import Substrate.FUSep.FUSepQBridge.Eqtrans
open import Substrate.FUSep.FUSepQSKI    using (atom; app) renaming (Tm-QSKI to Tm-QSKI)
open import Substrate.Foundation.Eq
open import Substrate.FUSep.FUSepQNf.ComposeUnit
open import Substrate.FUSep.FUSepQNf.Private
open import Substrate.FUSep.FUSepQNf.RedPhase
open import Substrate.FUSep.FUSepQNf.PeelPhase
open import Substrate.FUSep.FUSepQSKI


_ : compose-unit redPhase peelPhase ≡ refl
_ = refl
