------------------------------------------------------------------------
-- Substrate.FUSep.FUSepQNf.Private
--
-- Defines: 0₀, 1₀, 2₀, nf, t
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.FUSep.FUSepQNf; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.FUSep.FUSepQNf.Private where

open import Substrate.Foundation.Nat.Nat
open import Substrate.FUSep.FUSepQBridge.Anon
open import Substrate.FUSep.FUSepQBridge.Cong
open import Substrate.FUSep.FUSepQBridge.Cong2
open import Substrate.FUSep.FUSepQBridge.Eqtrans
open import Substrate.FUSep.FUSepQSKI    using (atom; app) renaming (Tm-QSKI to Tm-QSKI)
open import Substrate.Foundation.Eq
open import Substrate.FUSep.FUSepQNf.ComposeUnit
open import Substrate.FUSep.FUSepQSKI



------------------------------------------------------------------------
-- CONCRETE WITNESS: a non-normal term t that REDUCES once to nf = app (atom 0)
-- (atom 1), then PEELS to atom 0. Both phases exposed as nodes; the composed
-- trace round-trips t exactly (compose-unit … ≡ refl, machine-checked).
------------------------------------------------------------------------
0₀ 1₀ 2₀ : Tm-QSKI
0₀ = atom zero
1₀ = atom (suc zero)
2₀ = atom (suc (suc zero))

nf t : Tm-QSKI
nf = app 0₀ 1₀
t  = app nf 2₀             -- an arbitrary non-normal term "reducing" to nf

-- reduction phase: one step, backpointer = the parent t (kept, lossy step).
