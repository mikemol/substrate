------------------------------------------------------------------------
-- Substrate.Pipeline.Brick.EdgeAccessors
--
-- Edge accessors handy for composition: D-in-of, D-out-of, S-in-of,
-- S-out-of for an arbitrary Brick T.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Pipeline.Brick.EdgeAccessors where

open import Substrate.Pipeline.Brick.Type using (BrickType)
open import Substrate.Pipeline.Brick.Record using (Brick)

-- ⟡set1-paydown: BrickType's edges are now type indices, not projections — read them off the
-- implicit params (inferred from the brick's type) instead of `BrickType.D-in T`.
D-in-of : ∀ {D-in D-out S-in S-out : Set} {T : BrickType D-in D-out S-in S-out} {Tag : Set} → Brick T Tag → Set
D-in-of {D-in = d} _ = d

D-out-of : ∀ {D-in D-out S-in S-out : Set} {T : BrickType D-in D-out S-in S-out} {Tag : Set} → Brick T Tag → Set
D-out-of {D-out = d} _ = d

S-in-of : ∀ {D-in D-out S-in S-out : Set} {T : BrickType D-in D-out S-in S-out} {Tag : Set} → Brick T Tag → Set
S-in-of {S-in = s} _ = s

S-out-of : ∀ {D-in D-out S-in S-out : Set} {T : BrickType D-in D-out S-in S-out} {Tag : Set} → Brick T Tag → Set
S-out-of {S-out = s} _ = s
