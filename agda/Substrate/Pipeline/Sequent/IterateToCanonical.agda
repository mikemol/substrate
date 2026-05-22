------------------------------------------------------------------------
-- Substrate.Pipeline.Sequent.IterateToCanonical
--
-- iterate-to-canonical: iterate the derivation with a step bound,
-- returning the result when the canonical predicate holds (just) or
-- failing (nothing) if the bound is exceeded.
-- Termination-by-construction via the ℕ counter.
------------------------------------------------------------------------

{-# OPTIONS --without-K #-}

module Substrate.Pipeline.Sequent.IterateToCanonical where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Maybe using (Maybe; just; nothing)
open import Substrate.Pipeline.Sequent.CanonicalSpec using (CanonicalSpec)

iterate-to-canonical
  : ∀ {A : Set}
  → (spec : CanonicalSpec A)
  → (decide : (a : A) → Maybe (CanonicalSpec.Canonical spec a))
  → (derivation : A → A)
  → ℕ
  → A → Maybe A
iterate-to-canonical spec decide _    zero    _ = nothing
iterate-to-canonical spec decide deriv (suc n) a with decide a
... | just _  = just a
... | nothing = iterate-to-canonical spec decide deriv n (deriv a)
