------------------------------------------------------------------------
-- Substrate.Groups.Actions.Z2-on-Z3.Canonical
--
-- Canonicality of the action's output. act-letter sends a canonical
-- (h, n) to a Z/3-canonical word; act fixes a Z/3-normalize sandwich.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.Z2-on-Z3.Canonical where

import Substrate.Groups.Z2-Coxeter as Z₂
import Substrate.Groups.Z3-Coxeter as Z₃
open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.Foundation.Fin using (zero; suc)

open import Substrate.Groups.Actions.Z2-on-Z3.Act using (act-letter; act)

act-letter-canonical : ∀ {h n} → Z₂.Canonical h → Z₃.Canonical n →
                       Z₃.Canonical (act-letter h n)
act-letter-canonical (Z₂.c-pos zero) c-n = c-n
act-letter-canonical (Z₂.c-pos (suc zero)) c-n = Z₃.inv-canonical c-n

act-canonical : ∀ h n → Z₃.Canonical (act h n)
act-canonical h n =
  act-letter-canonical
    (Z₂.normalize-canonical h)
    (Z₃.normalize-canonical n)

normalize-act : ∀ h n → Z₃.normalize (act h n) ≡ act h n
normalize-act h n = Z₃.canonical-is-fixed (act-canonical h n)
