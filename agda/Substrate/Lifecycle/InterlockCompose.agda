------------------------------------------------------------------------
-- Substrate.Lifecycle.InterlockCompose
--
-- Defines: interlock-compose
-- ⟡cap-128-forcing: one lemma, one elaboration unit.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Lifecycle.InterlockCompose where

open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Nat.Properties.Order.LeTrans
open import Substrate.Lifecycle.Actor
open import Substrate.Lifecycle.Interlock
open import Substrate.Lifecycle.InterlockMonotone


------------------------------------------------------------------------
-- INTERLOCKS COMPOSE — this is the algebra's composition law, and it is why
-- the model is a PIPELINE rather than a list of adjacent pairs.
--
-- `interlock-monotone` proves the one-step case (feed down ≤ feed up for a
-- single interlocked pair). Composition lifts it to a CHAIN: a stall
-- anywhere bounds every actor upstream of it, transitively, with nothing
-- scheduling that propagation.
--
-- ⚑ NOTE THE DIRECTION. The proof composes RIGHT-to-LEFT along the data
-- flow: `feed down ≤ feed mid ≤ feed up`. Data moves up→down; the CONSTRAINT
-- moves down→up. That inversion is the content — the reclamation floor is
-- set by the SLOWEST downstream actor, which is why a stalled consumer pins
-- everything behind it and why auto-evicting one to "unblock" reclamation
-- would break the guarantee rather than restore it.
--
-- Together with `Actor.draws-before-feeding` this makes the whole pipeline's
-- positions monotone from end to end — a theorem about the chain, not a
-- paragraph in a docstring, and not a `min()` over a registry that a caller
-- must remember to compute correctly.
------------------------------------------------------------------------

interlock-compose : ∀ {up mid down}
                  → Interlock up mid
                  → Interlock mid down
                  → Actor.feed-lwm down ≤ Actor.feed-lwm up
interlock-compose lk₁ lk₂ =
  ≤-trans (interlock-monotone lk₂) (interlock-monotone lk₁)
