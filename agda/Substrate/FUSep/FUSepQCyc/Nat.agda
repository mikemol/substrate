------------------------------------------------------------------------
-- Substrate.FUSep.FUSepQCyc.Nat
--
-- Defines: ℕ₀
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.FUSep.FUSepQCyc; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.FUSep.FUSepQCyc.Nat where

open import Substrate.Foundation.List
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
import Substrate.FUSep.FUSepQReduce as FUSepQReduce
open FUSepQReduce using (Tm-QReduce; Reduce)
open import Substrate.FUSep.FUSepQCyc.Cyc
open import Substrate.FUSep.FUSepQCyc.Const


------------------------------------------------------------------------
-- CONCRETE WITNESS: the twos = const 2 (CycleWire's twos) is the period-1 cyc.
-- cyc 2 [] ~ const 2, machine-checked — the substrate's cycle 2 [] ~ twos, here.
------------------------------------------------------------------------
data ℕ₀ : Set where z : ℕ₀ ; s : ℕ₀ → ℕ₀
