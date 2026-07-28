{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.S3-on-V4.Axioms.ActEpsilonN.OnCanonical where

-- act-on-canonical fixes V₄'s identity, on canonical words. Relational.

import Substrate.Groups.Coxeter.Cyclic.Existential 1 as Z₂E
import Substrate.Groups.Coxeter.Cyclic.Existential 2 as Z₃E
open import Substrate.Groups.V4.Bijection using (e)
open import Substrate.Foundation.Fin.Literals using (₁; ₂)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Groups.Actions.S3-on-V4.Dispatch.ActOnCanonical using (act-on-canonical)

act-ε-N-on-canonical : ∀ {n h} → Z₃E.Canonical-ex n → Z₂E.Canonical-ex h →
                       act-on-canonical n h e ≡ e
act-ε-N-on-canonical (Z₃E.c-pos zero) (Z₂E.c-pos zero) = refl
act-ε-N-on-canonical (Z₃E.c-pos ₁)    (Z₂E.c-pos zero) = refl
act-ε-N-on-canonical (Z₃E.c-pos ₂)    (Z₂E.c-pos zero) = refl
act-ε-N-on-canonical (Z₃E.c-pos zero) (Z₂E.c-pos ₁) = refl
act-ε-N-on-canonical (Z₃E.c-pos ₁)    (Z₂E.c-pos ₁) = refl
act-ε-N-on-canonical (Z₃E.c-pos ₂)    (Z₂E.c-pos ₁) = refl
