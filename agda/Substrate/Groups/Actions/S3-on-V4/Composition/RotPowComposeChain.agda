------------------------------------------------------------------------
-- …Composition.RotPowComposeChain — rot-pow over a doubly-normalised
-- concatenation is the composite. SINGLE carrier: Z/3 (index 2).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.S3-on-V4.Composition.RotPowComposeChain where

open import Substrate.Groups.V4.Bijection using (V₄)
open import Substrate.Groups.Coxeter.Word using (Word; _++_)
open import Substrate.Foundation.Eq using (_≡_; sym; trans; cong)

import Substrate.Groups.Coxeter.Cyclic.Base 2 as Z₃B
import Substrate.Groups.Coxeter.Cyclic.Existential 2 as Z₃E
import Substrate.Groups.Coxeter.Cyclic.Core 2 as Z₃C

open import Substrate.Groups.Actions.S3-on-V4.Generators.RotPow using (rot-pow)
open import Substrate.Groups.Actions.S3-on-V4.Generators.RotPowAppend using (rot-pow-append)
open import Substrate.Groups.Actions.S3-on-V4.Generators.RotPowNormalizeEq using (rot-pow-normalize-eq)

rot-pow-compose-chain :
  ∀ (n₁ n₂' : Word Z₃B.Gen) (v' : V₄) →
  rot-pow (Z₃E.normalize (Z₃E.normalize (n₁ ++ n₂'))) v' ≡
    rot-pow n₁ (rot-pow n₂' v')
rot-pow-compose-chain n₁ n₂' v' =
  trans (cong (λ w → rot-pow w v') (Z₃C.normalize-idem (n₁ ++ n₂')))
  (trans (sym (rot-pow-normalize-eq (n₁ ++ n₂') v'))
         (rot-pow-append n₁ n₂' v'))
