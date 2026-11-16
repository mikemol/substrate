------------------------------------------------------------------------
-- Substrate.FUSep.FUSepQHexagon.BraidInvolutive
--
-- Defines: braid-involutive
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.FUSep.FUSepQHexagon; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.FUSep.FUSepQHexagon.BraidInvolutive where

open import Substrate.Foundation.Product
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Eq
open import Substrate.FUSep.FUSepQHexagon.Braid



------------------------------------------------------------------------
-- INVOLUTIVITY (Wedge/Monoidal.braid-involutive; = ADD 107's σ∘σ≡id): the
-- symmetric-monoidal law, the diamond closing exactly.
------------------------------------------------------------------------
braid-involutive : {X Y : Set} (xy : X × Y) → braid (braid xy) ≡ xy
braid-involutive xy = refl
