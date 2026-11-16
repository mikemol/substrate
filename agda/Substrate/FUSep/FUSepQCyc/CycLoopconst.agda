------------------------------------------------------------------------
-- Substrate.FUSep.FUSepQCyc.CycLoopconst
--
-- Defines: cyc-loop~const
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.FUSep.FUSepQCyc; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.FUSep.FUSepQCyc.CycLoopconst where

open import Substrate.Foundation.List
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
import Substrate.FUSep.FUSepQReduce as FUSepQReduce
open FUSepQReduce using (Tm-QReduce; Reduce)
open import Substrate.FUSep.FUSepQCyc.Stream
open import Substrate.FUSep.FUSepQCyc.CycGo
open import Substrate.FUSep.FUSepQCyc.Cyc
open import Substrate.FUSep.FUSepQCyc.Const
open import Substrate.FUSep.FUSepQCyc.Op



------------------------------------------------------------------------
-- THE COUNIT (period-1, the Ω / twos analog): cyc x [] ~ const x, by GUARDED
-- COINDUCTION. CycleWire proves cycle 2 [] ~ twos; this is that, generic. The
-- self-loop (Ω → Ω) is bisimilar to the constant periodic real — the greatest
-- fixed point's periodic point is unique up to bisimilarity.
------------------------------------------------------------------------
cyc-loop~const : {A : Set} (x : A) → cyc-go x [] [] ~ₛ const x
hd~ (cyc-loop~const x) = refl
tl~ (cyc-loop~const x) = cyc-loop~const x
