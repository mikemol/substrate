------------------------------------------------------------------------
-- Substrate.Groups.Actions.Z2-on-Z3.Canonical.NormalizeAct
--
-- The action's result is already normalised — a SINGLE-carrier fact
-- (Z₃ only), which is why it is its own module.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.Z2-on-Z3.Canonical.NormalizeAct where

import Substrate.Groups.Coxeter.Cyclic.Existential 2 as Z₃E
import Substrate.Groups.Coxeter.Cyclic.Core 2 as Z₃C
open import Substrate.Foundation.Eq using (_≡_)

open import Substrate.Groups.Actions.Z2-on-Z3.Act using (act)
open import Substrate.Groups.Actions.Z2-on-Z3.Canonical.ActCanonical
  using (act-canonical)

normalize-act : ∀ h n → Z₃E.normalize (act h n) ≡ act h n
normalize-act h n = Z₃C.canonical-is-fixed (act-canonical h n)
