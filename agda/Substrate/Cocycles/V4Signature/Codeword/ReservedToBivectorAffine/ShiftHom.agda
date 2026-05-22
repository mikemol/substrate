------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.Codeword.ReservedToBivectorAffine.ShiftHom
--
-- shift-hom : (v w : V₄) → shift (v +V₄ w) ≡ shift v +ⱽ shift w.
-- The "factor through the group structure" pattern: 16 cases (4 × 4),
-- each closing via Vector arithmetic (+ⱽ-identityˡ/ʳ, +ⱽ-self-inverse,
-- +ⱽ-comm/assoc).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.Codeword.ReservedToBivectorAffine.ShiftHom where

open import Substrate.Foundation.Bool using (false; true)
open import Substrate.Foundation.Product using (_,_)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong)
open import Substrate.Algebra.F2.Vector
  using (_+ⱽ_; +ⱽ-identityˡ; +ⱽ-identityʳ; +ⱽ-assoc; +ⱽ-comm; +ⱽ-self-inverse)
open import Substrate.Algebra.F2.HodgeDim4.SelfDual using (sd-pair-01-23; sd-pair-02-13)
open import Substrate.Cocycles.V4Signature.Codeword.ReservedToBivectorAffine.V4
  using (V₄; _+V₄_)
open import Substrate.Cocycles.V4Signature.Codeword.ReservedToBivectorAffine.Shift
  using (shift)

shift-hom : (v w : V₄) → shift (v +V₄ w) ≡ shift v +ⱽ shift w
shift-hom (false , false) w = sym (+ⱽ-identityˡ (shift w))
shift-hom (true , false) (false , false) = sym (+ⱽ-identityʳ sd-pair-01-23)
shift-hom (true , false) (true , false) =
  sym (+ⱽ-self-inverse sd-pair-01-23)
shift-hom (true , false) (false , true) = refl
shift-hom (true , false) (true , true) =
  sym (trans (sym (+ⱽ-assoc sd-pair-01-23 sd-pair-01-23 sd-pair-02-13))
       (trans (cong (_+ⱽ sd-pair-02-13) (+ⱽ-self-inverse sd-pair-01-23))
              (+ⱽ-identityˡ sd-pair-02-13)))
shift-hom (false , true) (false , false) = sym (+ⱽ-identityʳ sd-pair-02-13)
shift-hom (false , true) (true , false) = +ⱽ-comm sd-pair-02-13 sd-pair-01-23
shift-hom (false , true) (false , true) =
  sym (+ⱽ-self-inverse sd-pair-02-13)
shift-hom (false , true) (true , true) =
  sym (trans (cong (sd-pair-02-13 +ⱽ_) (+ⱽ-comm sd-pair-01-23 sd-pair-02-13))
      (trans (sym (+ⱽ-assoc sd-pair-02-13 sd-pair-02-13 sd-pair-01-23))
      (trans (cong (_+ⱽ sd-pair-01-23) (+ⱽ-self-inverse sd-pair-02-13))
             (+ⱽ-identityˡ sd-pair-01-23))))
shift-hom (true , true) (false , false) =
  sym (+ⱽ-identityʳ (sd-pair-01-23 +ⱽ sd-pair-02-13))
shift-hom (true , true) (true , false) =
  sym (trans (+ⱽ-comm (sd-pair-01-23 +ⱽ sd-pair-02-13) sd-pair-01-23)
      (trans (sym (+ⱽ-assoc sd-pair-01-23 sd-pair-01-23 sd-pair-02-13))
      (trans (cong (_+ⱽ sd-pair-02-13) (+ⱽ-self-inverse sd-pair-01-23))
             (+ⱽ-identityˡ sd-pair-02-13))))
shift-hom (true , true) (false , true) =
  sym (trans (+ⱽ-assoc sd-pair-01-23 sd-pair-02-13 sd-pair-02-13)
      (trans (cong (sd-pair-01-23 +ⱽ_) (+ⱽ-self-inverse sd-pair-02-13))
             (+ⱽ-identityʳ sd-pair-01-23)))
shift-hom (true , true) (true , true) =
  sym (+ⱽ-self-inverse (sd-pair-01-23 +ⱽ sd-pair-02-13))
