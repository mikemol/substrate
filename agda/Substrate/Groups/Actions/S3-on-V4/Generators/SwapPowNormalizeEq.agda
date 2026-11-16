------------------------------------------------------------------------
-- Substrate.Groups.Actions.S3-on-V4.Generators.SwapPowNormalizeEq
--
-- swap-pow is invariant under normalising its Z/2 word. SINGLE carrier
-- (index 1); the two aliases are its two OWNERS, not two carriers.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.S3-on-V4.Generators.SwapPowNormalizeEq where

-- ⚑ `normalize` / `normalize-canonical` ARE `ListPresentation`'s (Ⓐ¹⁶).
import Substrate.Groups.Coxeter.Cyclic.Base 1 as Z₂B
import Substrate.Groups.Coxeter.Cyclic.Existential 1 as Z₂E
import Substrate.Groups.Coxeter.ListPresentation
  Z₂B.Gen Z₂E.Canonical-ex Z₂E.c-ε Z₂B.insert Z₂E.insert-canonical-ex as Z₂LP
open import Substrate.Groups.V4.Bijection.V4
open import Substrate.Groups.Coxeter.Word using (Word; []; _∷_)
open import Substrate.Foundation.Fin.Literals using (₁)
open import Substrate.Foundation.Fin.Fin

open import Substrate.Groups.Actions.S3-on-V4.Generators.SwapAB       using (swap-αβ)
open import Substrate.Groups.Actions.S3-on-V4.Generators.SwapPow      using (swap-pow)
open import Substrate.Groups.Actions.S3-on-V4.Generators.SwapSquareId using (swap-αβ²-id)
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong

swap-pow-normalize-eq : (w : Word Z₂B.Gen) (v : V₄) →
                        swap-pow w v ≡ swap-pow (Z₂LP.normalize w) v
swap-pow-normalize-eq []          v = refl
swap-pow-normalize-eq (Z₂B.a ∷ w) v =
  trans (cong swap-αβ (swap-pow-normalize-eq w v))
        (swap-step (Z₂LP.normalize-canonical w) v)
  where
    swap-step : ∀ {x} → Z₂E.Canonical-ex x → (v : V₄) →
                swap-αβ (swap-pow x v) ≡ swap-pow (Z₂B.insert Z₂B.a x) v
    swap-step (Z₂E.c-pos zero) _ = refl
    swap-step (Z₂E.c-pos ₁) v = swap-αβ²-id v
