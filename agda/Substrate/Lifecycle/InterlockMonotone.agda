------------------------------------------------------------------------
-- Substrate.Lifecycle.InterlockMonotone
--
-- Defines: interlock-monotone
-- ⟡cap-128-forcing: one lemma, one elaboration unit.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Lifecycle.InterlockMonotone where

open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Nat.Properties.Order.LeTrans
open import Substrate.Lifecycle.Actor
open import Substrate.Lifecycle.Interlock


------------------------------------------------------------------------
-- THE INTERLOCK FORCES MONOTONICITY: a downstream actor's FEED can never
-- overtake an upstream actor's FEED.
--
--     feed-lwm down  ≤  draw-hwm down  ≤  feed-lwm up
--                    ↑                 ↑
--        the actor's own invariant     the interlock
--
-- So positions decrease monotonically along the pipeline, and a datum below
-- the LAST actor's feed is below every actor's feed — which is exactly the
-- reclamation criterion. The relational store computes that as
-- `min(feed)` over a registry; here it is a consequence of the structure,
-- so a schema that stored a downstream feed ahead of an upstream one would
-- be REFUSED rather than silently producing an unsafe floor.
------------------------------------------------------------------------

interlock-monotone : ∀ {up down} → Interlock up down
                   → Actor.feed-lwm down ≤ Actor.feed-lwm up
interlock-monotone {up} {down} lk =
  ≤-trans (Actor.draws-before-feeding down) (Interlock.permitted lk)
