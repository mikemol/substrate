------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.Codeword.ReservedToBivectorAffine.AffineBijection
--
-- reserved-to-selfdual-affine : Reserved → Σ Bivector SelfDual-Pred.
-- The affine bijection σ(cw) = base(cw.sign) +ⱽ shift(cw.axis).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.Codeword.ReservedToBivectorAffine.AffineBijection where

open import Substrate.Foundation.Bool using (false)
open import Substrate.Foundation.Product using (Σ; _,_)
open import Substrate.Foundation.Eq using (refl)
open import Substrate.Algebra.F2.HodgeDim4.Bivector using (Bivector)
open import Substrate.Algebra.F2.Vector using (_+ⱽ_)
open import Substrate.Algebra.F2.HodgeDim4.SelfDual using (SelfDual-Pred; sd-closed-+ⱽ)
open import Substrate.Cocycles.V4Signature.Codeword.Subtypes using (Reserved)
open import Substrate.Cocycles.V4Signature.Codeword.ReservedToBivectorAffine.Shift
  using (shift)
open import Substrate.Cocycles.V4Signature.Codeword.ReservedToBivectorAffine.ShiftSelfDual
  using (shift-sd)
open import Substrate.Cocycles.V4Signature.Codeword.ReservedToBivectorAffine.BaseBivector
  using (base-bivector; base-bivector-sd)

reserved-to-selfdual-affine :
  Reserved → Σ Bivector SelfDual-Pred
reserved-to-selfdual-affine ((b₀ , b₁ , b₂ , .false , .false) , refl , refl) =
  (base-bivector b₂ +ⱽ shift (b₀ , b₁)) ,
  sd-closed-+ⱽ (base-bivector b₂) (shift (b₀ , b₁))
    (base-bivector-sd b₂) (shift-sd (b₀ , b₁))
