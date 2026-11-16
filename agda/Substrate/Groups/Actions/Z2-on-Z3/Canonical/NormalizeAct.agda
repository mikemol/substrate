------------------------------------------------------------------------
-- Substrate.Groups.Actions.Z2-on-Z3.Canonical.NormalizeAct
--
-- The action's result is already normalised — a SINGLE-carrier fact
-- (Z₃ only), which is why it is its own module.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.Z2-on-Z3.Canonical.NormalizeAct where

-- ⚑ `normalize` IS `ListPresentation`'s, not `Existential`'s (Ⓐ¹³′).
import Substrate.Groups.Coxeter.Cyclic.Base 2 as Z₃B
import Substrate.Groups.Coxeter.Cyclic.Existential 2 as Z₃E
import Substrate.Groups.Coxeter.ListPresentation
  Z₃B.Gen Z₃E.Canonical-ex Z₃E.c-ε Z₃B.insert Z₃E.insert-canonical-ex as Z₃LP

open import Substrate.Groups.Actions.Z2-on-Z3.Act using (act)
open import Substrate.Groups.Actions.Z2-on-Z3.Canonical.ActCanonical
  using (act-canonical)
open import Substrate.Foundation.Eq
open import Substrate.Generators
import Substrate.Groups.Coxeter.Cyclic.Core 2 as Z₃C

normalize-act : ∀ h n → Z₃LP.normalize (act h n) ≡ act h n
normalize-act h n = Z₃C.canonical-is-fixed (act-canonical h n)
