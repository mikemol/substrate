------------------------------------------------------------------------
-- Substrate.Lifecycle.Interlock
--
-- Defines: Interlock
-- ⟡cap-128-forcing: one lemma, one elaboration unit.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Lifecycle.Interlock where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Le
open import Substrate.Lifecycle.Actor


------------------------------------------------------------------------
-- TWO ADJACENT ACTORS, INTERLOCKED: what upstream has RELEASED is what
-- downstream is PERMITTED to read.
--
-- `up`'s feed-lwm is a promise it publishes; `down`'s draw-hwm is a bound it
-- obeys. The interlock is that the second cannot exceed the first — a
-- downstream actor may not read past what upstream has actually released.
--
-- THIS IS WHY A STALL PROPAGATES BACKWARDS. Nothing schedules that
-- propagation: it is forced by the chain of these bounds. If `down` cannot
-- advance its feed, its draw stays put, which caps what the actor below it
-- may read, and so on to the end of the pipeline. The "system of dynamics"
-- is this field, iterated — not a policy anyone implements.
--
-- Composed with `Actor.draws-before-feeding` (feed-lwm ≤ draw-hwm for a
-- single actor), a pipeline's positions are monotone from end to end, and
-- that is a THEOREM about the chain rather than a paragraph in a docstring.
------------------------------------------------------------------------

record Interlock (up down : Actor) : Set where
  constructor interlock
  field
    permitted : Actor.draw-hwm down ≤ Actor.feed-lwm up
