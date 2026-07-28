------------------------------------------------------------------------
-- …Twist.RotPowSwapTwist — swap conjugates rot-pow to its inverse.
-- SINGLE carrier: Z/3 (index 2).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.S3-on-V4.Twist.RotPowSwapTwist where

open import Substrate.Groups.V4.Bijection using (V₄)
open import Substrate.Groups.V4.Operations using (v4-cover)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Fin.Literals using (₁; ₂)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Product using (_,_)

import Substrate.Groups.Coxeter.Cyclic.Existential 2 as Z₃E
import Substrate.Groups.Coxeter.Cyclic.Inverse 2 as Z₃I

open import Substrate.Groups.Actions.S3-on-V4.Generators.RotPow using (rot-pow)
open import Substrate.Groups.Actions.S3-on-V4.Generators.SwapAB using (swap-αβ)

rot-pow-swap-twist : ∀ {n} → Z₃E.Canonical-ex n → (v : V₄) →
                     swap-αβ (rot-pow n v) ≡ rot-pow (Z₃I.inv n) (swap-αβ v)
rot-pow-swap-twist (Z₃E.c-pos zero) = v4-cover _ (refl , refl , refl , refl)
rot-pow-swap-twist (Z₃E.c-pos ₁)    = v4-cover _ (refl , refl , refl , refl)
rot-pow-swap-twist (Z₃E.c-pos ₂)    = v4-cover _ (refl , refl , refl , refl)
