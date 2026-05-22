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

D-in-of : ∀ {T : BrickType} → Brick T → Set
D-in-of {T} _ = BrickType.D-in T

D-out-of : ∀ {T : BrickType} → Brick T → Set
D-out-of {T} _ = BrickType.D-out T

S-in-of : ∀ {T : BrickType} → Brick T → Set
S-in-of {T} _ = BrickType.S-in T

S-out-of : ∀ {T : BrickType} → Brick T → Set
S-out-of {T} _ = BrickType.S-out T
