{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.S3-on-V4.Axioms.ActEpsilonN.EpsilonN where

-- Every S₃ element fixes V₄'s identity.

import Substrate.Groups.Coxeter.Cyclic.Existential 1 as Z₂E
import Substrate.Groups.Coxeter.Cyclic.Existential 2 as Z₃E
open import Substrate.Groups.V4.Bijection using (e)
open import Substrate.Foundation.Product using (_,_)
open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.Groups.Actions.S3-on-V4.Dispatch.Act using (act)
open import Substrate.Groups.Actions.S3-on-V4.Axioms.ActEpsilonN.OnCanonical
  using (act-ε-N-on-canonical)

act-ε-N : ∀ s → act s e ≡ e
act-ε-N (n , h) = act-ε-N-on-canonical (Z₃E.normalize-canonical n) (Z₂E.normalize-canonical h)
