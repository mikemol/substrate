------------------------------------------------------------------------
-- The action respects Z/2's product: act (h₁ · h₂) ≈ act h₁ ∘ act h₂.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.Z2-on-Z3.ActDot.Dot where

import Substrate.Groups.Coxeter.Cyclic.Existential 1 as Z₂E
import Substrate.Groups.Coxeter.Cyclic.Existential 2 as Z₃E
import Substrate.Groups.Coxeter.Cyclic.Core 1 as Z₂C
import Substrate.Groups.Coxeter.Cyclic.Core 2 as Z₃C
import Substrate.Groups.Capabilities.CoxeterGroup.Witness as CoxeterGroupW
open import Substrate.Groups.Coxeter.Word using (_++_)
open import Substrate.Foundation.Eq using (_≡_; trans; sym; cong)
open import Substrate.Groups.Actions.Z2-on-Z3.Act using (act; act-letter)
open import Substrate.Groups.Actions.Z2-on-Z3.ActDot.LetterCompose using (act-letter-compose)
open import Substrate.Groups.Actions.Z2-on-Z3.Canonical.LetterCanonical using (act-letter-canonical)
cap-Z₂ = CoxeterGroupW.cap 1

import Substrate.Groups.Coxeter.GroupFromCapability cap-Z₂ as Z₂G
cap-Z₃ = CoxeterGroupW.cap 2



import Substrate.Groups.Coxeter.GroupFromCapability cap-Z₃ as Z₃G
act-∙ : ∀ h₁ h₂ n → act (h₁ Z₂G.· h₂) n Z₃G.≈ act h₁ (act h₂ n)
act-∙ h₁ h₂ n =
  let
    inner-n = Z₃E.normalize n
    c-n = Z₃E.normalize-canonical n
    c₁ = Z₂E.normalize-canonical h₁
    c₂ = Z₂E.normalize-canonical h₂
    bridge-h : Z₂E.normalize (Z₂E.normalize (h₁ ++ h₂)) ≡
               Z₂E.normalize (Z₂E.normalize h₁ ++ Z₂E.normalize h₂)
    bridge-h = trans (Z₂C.normalize-idem (h₁ ++ h₂))
                     (Z₂C.normalize-distrib h₁ h₂)
    composed : act-letter (Z₂E.normalize (Z₂E.normalize h₁ ++ Z₂E.normalize h₂)) inner-n ≡
               act-letter (Z₂E.normalize h₁) (act-letter (Z₂E.normalize h₂) inner-n)
    composed = act-letter-compose c₁ c₂ c-n
    inner-canonical : Z₃E.normalize (act-letter (Z₂E.normalize h₂) inner-n) ≡
                      act-letter (Z₂E.normalize h₂) inner-n
    inner-canonical = Z₃C.canonical-is-fixed (act-letter-canonical c₂ c-n)
  in
  trans (cong (λ x → Z₃E.normalize (act-letter x inner-n)) bridge-h)
  (trans (cong Z₃E.normalize composed)
         (sym (cong (λ x → Z₃E.normalize (act-letter (Z₂E.normalize h₁) x))
                    inner-canonical)))
