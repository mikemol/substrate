------------------------------------------------------------------------
-- Substrate.Category.Functor.Opposite
--
-- The Functor-on-Opposite coercion: a Functor C D induces a Functor
-- (Opposite C) (Opposite D), and vice versa, with the underlying
-- F-obj / F-mor data unchanged (only the morphism-direction typing
-- flips).
--
-- This is the structural bridge that unblocks the Limit/Colimit
-- (and similar dual-pair) absorptions via Opposite. Once a dual
-- structure depends on Functor data (not just Obj data, as Limit/
-- Colimit currently do), the dual specialization can be written as
-- the primal-skeleton applied to (Opposite-coerced inputs).
--
-- Per the pullback-as-skeleton principle: opposite-Functor is the
-- *projection* that lets the universal Functor-shaped skeleton
-- project onto both `Functor C D` and `Functor (Opposite C) (Opposite D)`
-- specializations.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Functor.Opposite where

open import Substrate.Foundation.Level using (Level)

open import Substrate.Category.CategoryOf using (CategoryOf)
open import Substrate.Category.Functor using (Functor; mkFunctor)
open import Substrate.Category.Opposite using (Opposite)

private
  variable
    ℓOC ℓMC ℓOD ℓMD : Level

------------------------------------------------------------------------
-- opposite-Functor : Functor C D → Functor (Opposite C) (Opposite D).
--
-- The F-obj and F-mor data are reused as-is; the type signatures
-- realign automatically because:
--   (Opposite C).Mor a b = C.Mor b a
--   F-mor on opposite gets the same data via alpha-renaming
--     (a, b → b, a in implicit args).
--
-- F-id is unchanged. F-compose is the same equation with f, g swapped
-- (composition order reverses in the opposite category, so the
-- equation that says "F preserves compose" naturally swaps its
-- f and g arguments).
------------------------------------------------------------------------

opposite-Functor :
  {ObjC : Set ℓOC} {MorC : ObjC → ObjC → Set ℓMC}
  {ObjD : Set ℓOD} {MorD : ObjD → ObjD → Set ℓMD}
  {C : CategoryOf ObjC MorC}
  {D : CategoryOf ObjD MorD} →
  Functor C D → Functor (Opposite C) (Opposite D)
opposite-Functor F = mkFunctor
  F.F-obj
  F.F-mor
  F.F-id
  (λ f g → F.F-compose g f)
  where module F = Functor F

------------------------------------------------------------------------
-- from-opposite-Functor : Functor (Opposite C) (Opposite D) → Functor C D.
--
-- The inverse direction. Same data; same shape; type signature
-- flips back. With Opposite (Opposite C) ≅ C (up to record-data
-- equality), this is the structural undo of opposite-Functor.
------------------------------------------------------------------------

from-opposite-Functor :
  {ObjC : Set ℓOC} {MorC : ObjC → ObjC → Set ℓMC}
  {ObjD : Set ℓOD} {MorD : ObjD → ObjD → Set ℓMD}
  {C : CategoryOf ObjC MorC}
  {D : CategoryOf ObjD MorD} →
  Functor (Opposite C) (Opposite D) → Functor C D
from-opposite-Functor F = mkFunctor
  F.F-obj
  F.F-mor
  F.F-id
  (λ f g → F.F-compose g f)
  where module F = Functor F
