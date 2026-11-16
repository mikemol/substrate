------------------------------------------------------------------------
-- The action respects Z/2's product: act (h₁ · h₂) ≈ act h₁ ∘ act h₂.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.Z2-on-Z3.ActDot.Dot where

-- ⚑ `normalize` / `normalize-canonical` ARE `ListPresentation`'s, not
-- `Existential`'s (Ⓐ¹³′) — one application per index.  This file is the clearest
-- case for why that matters: it uses BOTH at once, and the unqualified name was
-- silently conflating two different instances of the same construction.
import Substrate.Groups.Coxeter.Cyclic.Base 1 as Z₂B
import Substrate.Groups.Coxeter.Cyclic.Base 2 as Z₃B
import Substrate.Groups.Coxeter.Cyclic.Existential 1 as Z₂E
import Substrate.Groups.Coxeter.Cyclic.Existential 2 as Z₃E
import Substrate.Groups.Coxeter.ListPresentation
  Z₂B.Gen Z₂E.Canonical-ex Z₂E.c-ε Z₂B.insert Z₂E.insert-canonical-ex as Z₂LP
import Substrate.Groups.Coxeter.ListPresentation
  Z₃B.Gen Z₃E.Canonical-ex Z₃E.c-ε Z₃B.insert Z₃E.insert-canonical-ex as Z₃LP
import Substrate.Groups.Capabilities.CoxeterGroup.Witness as CoxeterGroupW
open import Substrate.Groups.Coxeter.Word using (_++_)
open import Substrate.Groups.Actions.Z2-on-Z3.Act using (act; act-letter)
open import Substrate.Groups.Actions.Z2-on-Z3.ActDot.LetterCompose using (act-letter-compose)
open import Substrate.Groups.Actions.Z2-on-Z3.Canonical.LetterCanonical using (act-letter-canonical)
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Cong
open import Substrate.Generators
import Substrate.Groups.Coxeter.Cyclic.Core 1 as Z₂C
import Substrate.Groups.Coxeter.Cyclic.Core 2 as Z₃C
cap-Z₂ = CoxeterGroupW.cap 1

import Substrate.Groups.Coxeter.GroupFromCapability cap-Z₂ as Z₂G
cap-Z₃ = CoxeterGroupW.cap 2



import Substrate.Groups.Coxeter.GroupFromCapability cap-Z₃ as Z₃G
act-∙ : ∀ h₁ h₂ n → act (h₁ Z₂G.· h₂) n Z₃G.≈ act h₁ (act h₂ n)
act-∙ h₁ h₂ n =
  let
    inner-n = Z₃LP.normalize n
    c-n = Z₃LP.normalize-canonical n
    c₁ = Z₂LP.normalize-canonical h₁
    c₂ = Z₂LP.normalize-canonical h₂
    bridge-h : Z₂LP.normalize (Z₂LP.normalize (h₁ ++ h₂)) ≡
               Z₂LP.normalize (Z₂LP.normalize h₁ ++ Z₂LP.normalize h₂)
    bridge-h = trans (Z₂C.normalize-idem (h₁ ++ h₂))
                     (Z₂C.normalize-distrib h₁ h₂)
    composed : act-letter (Z₂LP.normalize (Z₂LP.normalize h₁ ++ Z₂LP.normalize h₂)) inner-n ≡
               act-letter (Z₂LP.normalize h₁) (act-letter (Z₂LP.normalize h₂) inner-n)
    composed = act-letter-compose c₁ c₂ c-n
    inner-canonical : Z₃LP.normalize (act-letter (Z₂LP.normalize h₂) inner-n) ≡
                      act-letter (Z₂LP.normalize h₂) inner-n
    inner-canonical = Z₃C.canonical-is-fixed (act-letter-canonical c₂ c-n)
  in
  trans (cong (λ x → Z₃LP.normalize (act-letter x inner-n)) bridge-h)
  (trans (cong Z₃LP.normalize composed)
         (sym (cong (λ x → Z₃LP.normalize (act-letter (Z₂LP.normalize h₁) x))
                    inner-canonical)))
