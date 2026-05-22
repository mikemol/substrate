------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.Codeword.ReservedToBivectorAffine.V4Equivariance
--
-- v4-equivariance: the Σ-level V₄-equivariance. Combines
-- v4-equivariance-proj (bivector level) with selfdual-pred-irr
-- (proof-irrelevance) via Σ-≡,≡→≡.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.Codeword.ReservedToBivectorAffine.V4Equivariance where

open import Substrate.Foundation.Product using (_,_; Σ-≡,≡→≡)
open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.Cocycles.V4Signature.Codeword using (Reserved)
open import Substrate.Cocycles.V4Signature.Codeword.ReservedToBivectorAffine.V4
  using (V₄)
open import Substrate.Cocycles.V4Signature.Codeword.ReservedToBivectorAffine.ActReserved
  using (v4-act-reserved)
open import Substrate.Cocycles.V4Signature.Codeword.ReservedToBivectorAffine.ActSelfDual
  using (v4-act-selfdual)
open import Substrate.Cocycles.V4Signature.Codeword.ReservedToBivectorAffine.AffineBijection
  using (reserved-to-selfdual-affine)
open import Substrate.Cocycles.V4Signature.Codeword.ReservedToBivectorAffine.V4EquivarianceProj
  using (v4-equivariance-proj)
open import Substrate.Cocycles.V4Signature.Codeword.ReservedToBivectorAffine.SelfDualPredIrr
  using (selfdual-pred-irr)

v4-equivariance :
  (v : V₄) (r : Reserved) →
  reserved-to-selfdual-affine (v4-act-reserved v r) ≡
  v4-act-selfdual v (reserved-to-selfdual-affine r)
v4-equivariance v r =
  Σ-≡,≡→≡ (v4-equivariance-proj v r , selfdual-pred-irr _ _ _)
