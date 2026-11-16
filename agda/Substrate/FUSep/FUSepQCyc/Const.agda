------------------------------------------------------------------------
-- Substrate.FUSep.FUSepQCyc.Const
--
-- Defines: const
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.FUSep.FUSepQCyc; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.FUSep.FUSepQCyc.Const where

open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
import Substrate.FUSep.FUSepQReduce as FUSepQReduce
open FUSepQReduce using (Tm-QReduce; Reduce)
open import Substrate.FUSep.FUSepQCyc.Stream



-- the constant stream (period-1 unfolding — the Ω / twos case).
const : {A : Set} → A → Stream A
hd (const x) = x
tl (const x) = const x
