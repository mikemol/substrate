------------------------------------------------------------------------
-- Substrate.Groups.Actions.S3-on-V4.Generators.SwapPowNormalizeEq
--
-- swap-pow is invariant under normalising its Z/2 word. SINGLE carrier
-- (index 1); the two aliases are its two OWNERS, not two carriers.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.S3-on-V4.Generators.SwapPowNormalizeEq where

import Substrate.Groups.Coxeter.Cyclic.Base 1 as Z₂B
import Substrate.Groups.Coxeter.Cyclic.Existential 1 as Z₂E
open import Substrate.Groups.V4.Bijection using (V₄)
open import Substrate.Groups.Coxeter.Word using (Word; []; _∷_)
open import Substrate.Foundation.Eq using (_≡_; refl; trans; cong)
open import Substrate.Foundation.Fin.Literals using (₁)
open import Substrate.Foundation.Fin.Fin

open import Substrate.Groups.Actions.S3-on-V4.Generators.SwapAB       using (swap-αβ)
open import Substrate.Groups.Actions.S3-on-V4.Generators.SwapPow      using (swap-pow)
open import Substrate.Groups.Actions.S3-on-V4.Generators.SwapSquareId using (swap-αβ²-id)

swap-pow-normalize-eq : (w : Word Z₂B.Gen) (v : V₄) →
                        swap-pow w v ≡ swap-pow (Z₂E.normalize w) v
swap-pow-normalize-eq []          v = refl
swap-pow-normalize-eq (Z₂B.a ∷ w) v =
  trans (cong swap-αβ (swap-pow-normalize-eq w v))
        (swap-step (Z₂E.normalize-canonical w) v)
  where
    swap-step : ∀ {x} → Z₂E.Canonical-ex x → (v : V₄) →
                swap-αβ (swap-pow x v) ≡ swap-pow (Z₂B.insert Z₂B.a x) v
    swap-step (Z₂E.c-pos zero) _ = refl
    swap-step (Z₂E.c-pos ₁) v = swap-αβ²-id v
