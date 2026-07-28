------------------------------------------------------------------------
-- Substrate.Groups.Actions.Z2-on-Z3.Canonical.ActCanonical
--
-- act lands in canonical form: normalising both arguments first and
-- then acting stays canonical. Relational (both carriers), one definition.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.Z2-on-Z3.Canonical.ActCanonical where

import Substrate.Groups.Coxeter.Cyclic.Existential 1 as Z₂E
import Substrate.Groups.Coxeter.Cyclic.Existential 2 as Z₃E

open import Substrate.Groups.Actions.Z2-on-Z3.Act using (act)
open import Substrate.Groups.Actions.Z2-on-Z3.Canonical.LetterCanonical
  using (act-letter-canonical)

act-canonical : ∀ h n → Z₃E.Canonical-ex (act h n)
act-canonical h n =
  act-letter-canonical
    (Z₂E.normalize-canonical h)
    (Z₃E.normalize-canonical n)
