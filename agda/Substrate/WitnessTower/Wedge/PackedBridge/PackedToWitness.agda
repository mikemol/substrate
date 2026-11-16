------------------------------------------------------------------------
-- THE MORPHISM: the binary carrier → the witness tower. respects-recon holds by
-- refl — decode IS insert-at ∘ slot.
-- Context: Substrate/WitnessTower/Wedge/PackedBridge/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.PackedBridge.PackedToWitness where

open import Substrate.Foundation.Fin.Fin
open import Substrate.Algebra.Wedge.Graded.Morphism
open import Substrate.Algebra.Wedge.VecGraded.VecGraded
open import Substrate.WitnessTower.Wedge.Graded
open import Substrate.WitnessTower.Wedge.PackedBridge.Slot
open import Substrate.WitnessTower.Wedge.PackedBridge.Decode
open import Substrate.Foundation.Eq

packed→witness : GradedDivStrMorphism (vec-graded (Fin 2)) tower-graded
packed→witness = record
  { map-C = decode
  ; map-R = slot
  ; respects-recon = λ n v a → refl
  }
