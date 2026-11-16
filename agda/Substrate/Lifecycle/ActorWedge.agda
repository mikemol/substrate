------------------------------------------------------------------------
-- Substrate.Lifecycle.ActorWedge
--
-- Defines: actor-residue, actor-recon
-- ⟡cap-128-forcing: one lemma, one elaboration unit.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Lifecycle.ActorWedge where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Monus
open import Substrate.Lifecycle.Actor
open import Substrate.Lifecycle.Residue


------------------------------------------------------------------------
-- AN ACTOR IS A WEDGE: its draw position decomposes against its feed
-- position, with the in-flight work as the residue.
--
--     draw-hwm  =  feed-lwm  ℕ+  residue
--     ───┬────     ───┬────     ───┬───
--     grade n+1     base at n    the digit
--
-- This is `Substrate.Algebra.Wedge.Graded.DivStr`'s `recon` specialised to
-- the constant grading (C n = R n = ℕ): `recon _ b r = b ℕ+ r`. Naming it
-- makes the actor's two watermarks a DECOMPOSITION rather than two numbers
-- that happen to be ordered.
--
-- ⚑ THE RESIDUE IS THE OPERATIONALLY MEANINGFUL HALF. `Actor` records
-- `feed-lwm ≤ draw-hwm`, which says only that the pair is well-formed; the
-- GAP says how much work the actor is holding. Zero = fully caught up;
-- growing = backpressure. A registry storing one position could report
-- neither, which is why the store's floor could answer "how many rows" and
-- never "which actor is behind".
------------------------------------------------------------------------

actor-residue : Actor → Residue
actor-residue a = Actor.draw-hwm a ∸ Actor.feed-lwm a

actor-recon : Actor → ℕ
actor-recon a = Actor.feed-lwm a ℕ+ actor-residue a
