------------------------------------------------------------------------
-- Substrate.FUSep.FUSepQHexagon.P2
--
-- Defines: p₂
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.FUSep.FUSepQHexagon; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.FUSep.FUSepQHexagon.P2 where

open import Substrate.Foundation.Product
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Eq


p₂ : {A B : Set} → A × B → B
p₂ (_ , b) = b

------------------------------------------------------------------------
-- THE INDEXES over the shared node bucket (ADD 107): reduce and peel, each a
-- hierarchical edge set. Naturality is about MAPS between index sets — a further
-- rewrite transforms an index. `RIdx`/`PIdx`/`QIdx` are three index sets (the
-- hexagon needs three, for the 3-way coherence).
------------------------------------------------------------------------
RIdx PIdx QIdx : Set
