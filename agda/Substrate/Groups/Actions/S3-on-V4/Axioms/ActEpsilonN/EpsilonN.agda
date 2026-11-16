{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.S3-on-V4.Axioms.ActEpsilonN.EpsilonN where

-- Every S₃ element fixes V₄'s identity.

-- ⚑ `normalize-canonical` IS `ListPresentation`'s (Ⓐ¹⁶″); the `Cyclic.Base`
-- imports are NEW — the application needs `Gen`/`insert` and this file had no
-- Base binding at either index.
import Substrate.Groups.Coxeter.Cyclic.Base 1 as Z₂B
import Substrate.Groups.Coxeter.Cyclic.Base 2 as Z₃B
import Substrate.Groups.Coxeter.Cyclic.Existential 1 as Z₂E
import Substrate.Groups.Coxeter.Cyclic.Existential 2 as Z₃E
import Substrate.Groups.Coxeter.ListPresentation
  Z₂B.Gen Z₂E.Canonical-ex Z₂E.c-ε Z₂B.insert Z₂E.insert-canonical-ex as Z₂LP
import Substrate.Groups.Coxeter.ListPresentation
  Z₃B.Gen Z₃E.Canonical-ex Z₃E.c-ε Z₃B.insert Z₃E.insert-canonical-ex as Z₃LP
open import Substrate.Groups.V4.Bijection.V4
open import Substrate.Foundation.Product using (_,_)
open import Substrate.Groups.Actions.S3-on-V4.Dispatch.Act using (act)
open import Substrate.Groups.Actions.S3-on-V4.Axioms.ActEpsilonN.OnCanonical
  using (act-ε-N-on-canonical)
open import Substrate.Foundation.Eq

act-ε-N : ∀ s → act s e ≡ e
act-ε-N (n , h) = act-ε-N-on-canonical (Z₃LP.normalize-canonical n) (Z₂LP.normalize-canonical h)
