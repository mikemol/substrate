------------------------------------------------------------------------
-- Substrate.Lifecycle.Terminal
--
-- Defines: Terminal
-- ⟡cap-128-forcing: one lemma, one elaboration unit.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Lifecycle.Terminal where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Eq
open import Substrate.Lifecycle.Actor


------------------------------------------------------------------------
-- A TERMINAL actor DRAWS but does not FEED: it releases nothing downstream,
-- so its feed position is pinned at zero forever.
--
-- `scope_fix` is one — it reads observations bounded by source-liveness and
-- publishes no promise. In the relational store this had to be spelled as a
-- consumer "registered at 0 that must never advance", i.e. a rule enforced
-- by comment and by a runtime refusal; the honest reading is that the
-- registry had no way to say "draws but does not feed", so a nullable column
-- stood in for a type.
--
-- ⚑ AND IT EXPLAINS WHY A TERMINAL ACTOR CAN NEVER ADVANCE, rather than
-- forbidding it: an actor with no feed side has nothing to release, so
-- "advance" is not an operation it has. That is a stronger statement than a
-- guard that refuses the call — the operation is absent, not rejected.
--
-- Note the interaction with `Actor.draws-before-feeding` (feed ≤ draw): a
-- terminal actor satisfies it trivially for ANY draw bound, which is why it
-- pins the reclamation floor at 0 while still reading arbitrarily far.
------------------------------------------------------------------------

record Terminal (a : Actor) : Set where      -- ⟦shape:59e216d4 feeds-nothing⟧
  constructor terminal
  field
    feeds-nothing : Actor.feed-lwm a ≡ zero
