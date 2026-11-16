------------------------------------------------------------------------
-- Substrate.FUSep.FUSepQHexagon.BraidNat
--
-- Defines: braid-nat
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.FUSep.FUSepQHexagon; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.FUSep.FUSepQHexagon.BraidNat where

open import Substrate.Foundation.Product
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Eq
open import Substrate.FUSep.FUSepQHexagon.Braid
open import Substrate.FUSep.FUSepQHexagon.OtimesTo



------------------------------------------------------------------------
-- NATURALITY of the braiding (the componentwise square, Wedge/Monoidal §7): for
-- ANY index maps f : X→X', g : Y→Y', reordering-then-mapping = mapping-then-
-- reordering. The diamond COMMUTES WITH FURTHER REWRITING (functorial confluence).
--   braid ∘ (f ⊗→ g)  ≡  (g ⊗→ f) ∘ braid
------------------------------------------------------------------------
braid-nat : {X X' Y Y' : Set} (f : X → X') (g : Y → Y') (xy : X × Y)
          → braid ((f ⊗→ g) xy) ≡ (g ⊗→ f) (braid xy)
braid-nat f g xy = refl
