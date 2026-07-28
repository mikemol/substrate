------------------------------------------------------------------------
-- Substrate.Groups.Actions.Z2-on-Z3.ActEpsilonN.LetterEpsilon
--
-- Every canonical Z/2 letter fixes the empty Z/3 word. SINGLE carrier
-- (Z₂ only) — hence its own module.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.Z2-on-Z3.ActEpsilonN.LetterEpsilon where

import Substrate.Groups.Coxeter.Cyclic.Existential 1 as Z₂E
open import Substrate.Groups.Coxeter.Word using ([])
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Fin.Literals using (₁)
open import Substrate.Foundation.Fin.Fin

open import Substrate.Groups.Actions.Z2-on-Z3.Act using (act-letter)

act-letter-ε : ∀ {h} → Z₂E.Canonical-ex h → act-letter h [] ≡ []
act-letter-ε (Z₂E.c-pos zero) = refl
act-letter-ε (Z₂E.c-pos ₁) = refl
