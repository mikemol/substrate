------------------------------------------------------------------------
-- Substrate.FUSep.FUSepQHexagon.Private
--
-- Defines: a0, a1, a2
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.FUSep.FUSepQHexagon; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.FUSep.FUSepQHexagon.Private where

open import Substrate.Foundation.Nat.Nat
open import Substrate.FUSep.FUSepQSKI    using (atom; app) renaming (Tm-QSKI to Tm-QSKI)
open import Substrate.Foundation.Eq
open import Substrate.FUSep.FUSepQSKI



------------------------------------------------------------------------
-- THE HEXAGON AS 3-WAY CONFLUENCE: three edges out of a node (reduce r, peel p,
-- and a third q) reorder coherently — braiding r past (p,q) equals braiding r
-- past p then past q. This is the Yang-Baxter tiling: the elementary diamonds
-- fit together, so local confluence PROPAGATES. Machine-witnessed concretely.
------------------------------------------------------------------------
a0 a1 a2 : Tm-QSKI
a0 = atom zero
a1 = atom (suc zero)
a2 = atom (suc (suc zero))

-- three concrete edges (each an index entry: (backpointer, child)).
