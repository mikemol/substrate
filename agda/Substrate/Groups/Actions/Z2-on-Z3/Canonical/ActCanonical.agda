------------------------------------------------------------------------
-- Substrate.Groups.Actions.Z2-on-Z3.Canonical.ActCanonical
--
-- act lands in canonical form: normalising both arguments first and
-- then acting stays canonical. Relational (both carriers), one definition.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.Z2-on-Z3.Canonical.ActCanonical where

-- ⚑ `normalize-canonical` IS `ListPresentation`'s, not `Existential`'s (Ⓐ¹³);
-- one application per index, each with that index's five arguments.
import Substrate.Groups.Coxeter.Cyclic.Base 1 as Z₂B
import Substrate.Groups.Coxeter.Cyclic.Base 2 as Z₃B
import Substrate.Groups.Coxeter.Cyclic.Existential 1 as Z₂E
import Substrate.Groups.Coxeter.Cyclic.Existential 2 as Z₃E
import Substrate.Groups.Coxeter.ListPresentation
  Z₂B.Gen Z₂E.Canonical-ex Z₂E.c-ε Z₂B.insert Z₂E.insert-canonical-ex as Z₂LP
import Substrate.Groups.Coxeter.ListPresentation
  Z₃B.Gen Z₃E.Canonical-ex Z₃E.c-ε Z₃B.insert Z₃E.insert-canonical-ex as Z₃LP

open import Substrate.Groups.Actions.Z2-on-Z3.Act using (act)
open import Substrate.Groups.Actions.Z2-on-Z3.Canonical.LetterCanonical
  using (act-letter-canonical)

act-canonical : ∀ h n → Z₃E.Canonical-ex (act h n)
act-canonical h n =
  act-letter-canonical
    (Z₂LP.normalize-canonical h)
    (Z₃LP.normalize-canonical n)
