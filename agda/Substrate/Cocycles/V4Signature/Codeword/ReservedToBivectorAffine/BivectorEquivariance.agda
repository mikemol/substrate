------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.Codeword.ReservedToBivectorAffine.BivectorEquivariance
--
-- bivector-equivariance: the bivector-level identity behind V₄
-- equivariance. shift-hom + +ⱽ-comm + +ⱽ-assoc.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.Codeword.ReservedToBivectorAffine.BivectorEquivariance where

open import Substrate.Foundation.Bool using (Bool)
open import Substrate.Foundation.Product using (_,_)
open import Substrate.Foundation.Eq using (_≡_; sym; trans; cong)
open import Substrate.Algebra.F2.HodgeDim4.Bivector using (Bivector)
open import Substrate.Algebra.F2.Vector using (+ⱽ-assoc; +ⱽ-comm)
open import Substrate.Algebra.F2.Vector using (_+ⱽ_)
open import Substrate.Cocycles.V4Signature.Codeword.ReservedToBivectorAffine.Shift
  using (shift)
open import Substrate.Cocycles.V4Signature.Codeword.ReservedToBivectorAffine.ShiftHom
  using (shift-hom)

bivector-equivariance :
  (a b b₀ b₁ : Bool) (β₂ : Bivector) →
  β₂ +ⱽ shift ((a Substrate.Foundation.Bool.xor b₀) , (b Substrate.Foundation.Bool.xor b₁)) ≡
  (β₂ +ⱽ shift (b₀ , b₁)) +ⱽ shift (a , b)
bivector-equivariance a b b₀ b₁ β₂ =
  trans (cong (β₂ +ⱽ_) (shift-hom (a , b) (b₀ , b₁)))
  (trans (cong (β₂ +ⱽ_) (+ⱽ-comm (shift (a , b)) (shift (b₀ , b₁))))
         (sym (+ⱽ-assoc β₂ (shift (b₀ , b₁)) (shift (a , b)))))
