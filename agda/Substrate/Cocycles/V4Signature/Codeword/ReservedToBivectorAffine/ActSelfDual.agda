------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.Codeword.ReservedToBivectorAffine.ActSelfDual
--
-- v4-act-selfdual : V₄ → Σ Bivector SelfDual-Pred → ...
-- V₄ acts on SelfDual by translation by shift v.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.Codeword.ReservedToBivectorAffine.ActSelfDual where

open import Substrate.Foundation.Product using (Σ; _,_)
open import Substrate.Algebra.F2.HodgeDim4.Bivector using (Bivector)
open import Substrate.Algebra.F2.Vector using (_+ⱽ_)
open import Substrate.Algebra.F2.HodgeDim4.SelfDual using (SelfDual-Pred; sd-closed-+ⱽ)
open import Substrate.Cocycles.V4Signature.Codeword.ReservedToBivectorAffine.V4
  using (V₄)
open import Substrate.Cocycles.V4Signature.Codeword.ReservedToBivectorAffine.Shift
  using (shift)
open import Substrate.Cocycles.V4Signature.Codeword.ReservedToBivectorAffine.ShiftSelfDual
  using (shift-sd)

v4-act-selfdual : V₄ → Σ Bivector SelfDual-Pred → Σ Bivector SelfDual-Pred
v4-act-selfdual v (ω , sd) =
  (ω +ⱽ shift v) ,
  sd-closed-+ⱽ ω (shift v) sd (shift-sd v)
