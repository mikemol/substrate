------------------------------------------------------------------------
-- Substrate.FUSep.FUSepQCyc.Op
--
-- Defines: _~ₛ_, hd~
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.FUSep.FUSepQCyc; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.FUSep.FUSepQCyc.Op where

open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
import Substrate.FUSep.FUSepQReduce as FUSepQReduce
open FUSepQReduce using (Tm-QReduce; Reduce)
open import Substrate.FUSep.FUSepQCyc.Stream



-- BISIMILARITY (Bisim._~_): head~ + coinductive tail~. The R-side equality.
record _~ₛ_ {A : Set} (s t : Stream A) : Set where      -- stream bisimilarity (distinct-shape from Trace.Bisim._~_, pinned)
  coinductive
  field hd~ : hd s ≡ hd t ; tl~ : tl s ~ₛ tl t
open _~ₛ_ public
