------------------------------------------------------------------------
-- Substrate.Groups.Actions.S3-on-V4.Composition.ActDot
--
-- act-∙: full action composition via act-cong + S₃.∙-cong over
-- normalize-idem, dispatching to act-∙-canonical on the canonical
-- normalize-canonical witnesses.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.S3-on-V4.Composition.ActDot where

-- ⚑ `normalize` and `normalize-canonical` ARE `ListPresentation`'s (Ⓐ¹⁶″); the
-- `Cyclic.Base` imports are NEW, since the application needs `Gen`/`insert`.
import Substrate.Groups.Coxeter.Cyclic.Base 1 as Z₂B
import Substrate.Groups.Coxeter.Cyclic.Base 2 as Z₃B
import Substrate.Groups.Coxeter.Cyclic.Existential 1 as Z₂E
import Substrate.Groups.Coxeter.Cyclic.Existential 2 as Z₃E
import Substrate.Groups.Coxeter.ListPresentation
  Z₂B.Gen Z₂E.Canonical-ex Z₂E.c-ε Z₂B.insert Z₂E.insert-canonical-ex as Z₂LP
import Substrate.Groups.Coxeter.ListPresentation
  Z₃B.Gen Z₃E.Canonical-ex Z₃E.c-ε Z₃B.insert Z₃E.insert-canonical-ex as Z₃LP
import Substrate.Groups.S3 as S₃
open import Substrate.Foundation.Product using (_,_)

open import Substrate.Groups.Actions.S3-on-V4.Dispatch.Act using (act)
open import Substrate.Groups.Actions.S3-on-V4.Axioms.ActCong using (act-cong)
open import Substrate.Groups.Actions.S3-on-V4.Composition.ActDotCanonical using (act-∙-canonical)
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Generators
import Substrate.Groups.Coxeter.Cyclic.Core 1 as Z₂C
import Substrate.Groups.Coxeter.Cyclic.Core 2 as Z₃C

act-∙ : ∀ s₁ s₂ v → act (s₁ S₃.∙ s₂) v ≡ act s₁ (act s₂ v)
act-∙ (n₁ , h₁) (n₂ , h₂) v =
  trans
    (act-cong {s₁ = (n₁ , h₁) S₃.∙ (n₂ , h₂)}
              {s₂ = (Z₃LP.normalize n₁ , Z₂LP.normalize h₁) S₃.∙ (Z₃LP.normalize n₂ , Z₂LP.normalize h₂)}
              {v₁ = v} {v₂ = v}
      (S₃.∙-cong {a₁ = n₁ , h₁} {a₂ = Z₃LP.normalize n₁ , Z₂LP.normalize h₁}
                  {b₁ = n₂ , h₂} {b₂ = Z₃LP.normalize n₂ , Z₂LP.normalize h₂}
                  (sym (Z₃C.normalize-idem n₁) , sym (Z₂C.normalize-idem h₁))
                  (sym (Z₃C.normalize-idem n₂) , sym (Z₂C.normalize-idem h₂)))
      refl)
    (act-∙-canonical (Z₃LP.normalize-canonical n₁) (Z₂LP.normalize-canonical h₁)
                     (Z₃LP.normalize-canonical n₂) (Z₂LP.normalize-canonical h₂) v)
