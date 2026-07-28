------------------------------------------------------------------------
-- Substrate.Groups.Actions.Z2-on-Z3.Canonical.LetterCanonical
--
-- act-letter preserves canonicity.
--
-- This statement RELATES the two carriers — Z₂'s canonical words and
-- Z₃'s — so it names both. That is its content, not a carrier-locality
-- defect: the enclosing folder (Actions.Z2-on-Z3) is what says the two
-- are in play, and this module holds exactly one such definition.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.Z2-on-Z3.Canonical.LetterCanonical where

import Substrate.Groups.Coxeter.Cyclic.Existential 1 as Z₂E
import Substrate.Groups.Coxeter.Cyclic.Existential 2 as Z₃E
open import Substrate.Foundation.Fin.Literals using (₁)
open import Substrate.Foundation.Fin.Fin

open import Substrate.Groups.Actions.Z2-on-Z3.Act using (act-letter)

act-letter-canonical : ∀ {h n} → Z₂E.Canonical-ex h → Z₃E.Canonical-ex n →
                       Z₃E.Canonical-ex (act-letter h n)
act-letter-canonical (Z₂E.c-pos zero) c-n = c-n
act-letter-canonical (Z₂E.c-pos ₁) c-n = Z₃E.inv-canonical-ex c-n
