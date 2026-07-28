------------------------------------------------------------------------
-- …Twist.ActEqualsPow — the canonical dispatch IS rot-pow ∘ swap-pow.
-- TWO carriers, kept distinct by their definers: Z/3 (index 2) and
-- Z/2 (index 1).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.S3-on-V4.Twist.ActEqualsPow where

open import Substrate.Groups.V4.Operations using (v4-cover)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Fin.Literals using (₁; ₂)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Product using (_,_)

import Substrate.Groups.Coxeter.Cyclic.Existential 2 as Z₃E
import Substrate.Groups.Coxeter.Cyclic.Existential 1 as Z₂E

open import Substrate.Groups.Actions.S3-on-V4.Dispatch.ActOnCanonical using (act-on-canonical)
open import Substrate.Groups.Actions.S3-on-V4.Generators.RotPow using (rot-pow)
open import Substrate.Groups.Actions.S3-on-V4.Generators.SwapPow using (swap-pow)

act-equals-pow : ∀ {n h} → Z₃E.Canonical-ex n → Z₂E.Canonical-ex h → ∀ v →
                 act-on-canonical n h v ≡ rot-pow n (swap-pow h v)
act-equals-pow (Z₃E.c-pos zero) (Z₂E.c-pos zero) = v4-cover _ (refl , refl , refl , refl)
act-equals-pow (Z₃E.c-pos ₁)    (Z₂E.c-pos zero) = v4-cover _ (refl , refl , refl , refl)
act-equals-pow (Z₃E.c-pos ₂)    (Z₂E.c-pos zero) = v4-cover _ (refl , refl , refl , refl)
act-equals-pow (Z₃E.c-pos zero) (Z₂E.c-pos ₁)    = v4-cover _ (refl , refl , refl , refl)
act-equals-pow (Z₃E.c-pos ₁)    (Z₂E.c-pos ₁)    = v4-cover _ (refl , refl , refl , refl)
act-equals-pow (Z₃E.c-pos ₂)    (Z₂E.c-pos ₁)    = v4-cover _ (refl , refl , refl , refl)
