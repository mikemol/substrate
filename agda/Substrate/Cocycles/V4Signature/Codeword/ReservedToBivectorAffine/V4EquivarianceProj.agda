------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.Codeword.ReservedToBivectorAffine.V4EquivarianceProj
--
-- v4-equivariance-proj: V₄-equivariance at the bivector projection
-- level. The full Σ-level equality also requires the self-dual witness
-- agreement; the proj₁ part closes via bivector-equivariance.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.Codeword.ReservedToBivectorAffine.V4EquivarianceProj where

open import Substrate.Foundation.Product using (_,_; proj₁)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Cocycles.V4Signature.Codeword using (Reserved)
open import Substrate.Cocycles.V4Signature.Codeword.ReservedToBivectorAffine.V4
  using (V₄)
open import Substrate.Cocycles.V4Signature.Codeword.ReservedToBivectorAffine.ActReserved
  using (v4-act-reserved)
open import Substrate.Cocycles.V4Signature.Codeword.ReservedToBivectorAffine.ActSelfDual
  using (v4-act-selfdual)
open import Substrate.Cocycles.V4Signature.Codeword.ReservedToBivectorAffine.BaseBivector
  using (base-bivector)
open import Substrate.Cocycles.V4Signature.Codeword.ReservedToBivectorAffine.AffineBijection
  using (reserved-to-selfdual-affine)
open import Substrate.Cocycles.V4Signature.Codeword.ReservedToBivectorAffine.BivectorEquivariance
  using (bivector-equivariance)

v4-equivariance-proj :
  (v : V₄) (r : Reserved) →
  proj₁ (reserved-to-selfdual-affine (v4-act-reserved v r)) ≡
  proj₁ (v4-act-selfdual v (reserved-to-selfdual-affine r))
v4-equivariance-proj (a , b) ((b₀ , b₁ , b₂ , _ , _) , refl , refl) =
  bivector-equivariance a b b₀ b₁ (base-bivector b₂)
