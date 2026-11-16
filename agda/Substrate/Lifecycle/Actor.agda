------------------------------------------------------------------------
-- Substrate.Lifecycle.Actor
--
-- Defines: Actor
-- ⟡cap-128-forcing: one lemma, one elaboration unit.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Lifecycle.Actor where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Le
open import Substrate.Lifecycle.Boundary


------------------------------------------------------------------------
-- An ACTOR spans a stage boundary: it DRAWS from the upstream side and
-- FEEDS the downstream side.
--
-- An actor is anything that KNOWS AN INDEX — any stateful process, anything
-- with side effects. The only non-actor is a stateless function with no
-- knowledge of input or output index (a pure map, whose apparent stage is
-- really its caller's). So the population is censusable, never declared.
--
-- THE TWO WATERMARKS FACE OPPOSITE DIRECTIONS, and that asymmetry is the
-- content of the model:
--
--   draw-hwm  a bound the actor OBEYS      — imposed by upstream; reading
--             past it reads data that may not be settled.
--   feed-lwm  a promise the actor PUBLISHES — everything strictly below it
--             has been released downstream and is safe to reclaim.
--
-- `draws-before-feeding` is the invariant that makes them a pair rather than
-- two numbers: an actor cannot promise to have released what it was never
-- permitted to read. It is what fails, as a TYPE ERROR, if a schema stores a
-- feed position ahead of a draw bound.
------------------------------------------------------------------------

record Actor : Set where
  constructor actor
  field
    at                   : Boundary
    draw-hwm             : ℕ
    feed-lwm             : ℕ
    draws-before-feeding : feed-lwm ≤ draw-hwm
