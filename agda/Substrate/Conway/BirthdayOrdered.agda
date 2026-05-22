------------------------------------------------------------------------
-- Substrate.Conway.BirthdayOrdered
--
-- G1 of the Conway game-induction sibling tower per
-- [scratch/m_mod_arc_plan.md].
--
-- Bundles SurrealFinite with its birthday extraction into a single
-- "BirthdayOrdered" record. The birthday equips SurrealFinite with
-- the strict-descent measure on which Conway's recursive
-- order / addition / multiplication terminate ("Conway induction").
--
-- This slice names the inductive structure; G2-G8 build the
-- arithmetic + order theorems via birthday-recursion.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Conway.BirthdayOrdered where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Conway.SurrealFinite using (SurrealFinite)
open import Substrate.Conway.Birthday using (birthday)

------------------------------------------------------------------------
-- 1. The BirthdayOrdered record.
--
-- A BirthdayOrdered is a (Σ-bundled) SurrealFinite with its index
-- exposed at the type level for recursion-tracking.
------------------------------------------------------------------------

record BirthdayOrdered : Set where
  field
    index   : ℕ
    surreal : SurrealFinite (suc index)

open BirthdayOrdered public

------------------------------------------------------------------------
-- 2. Birthday extraction at the bundled level.
------------------------------------------------------------------------

bday : BirthdayOrdered → ℕ
bday b = birthday (surreal b)

------------------------------------------------------------------------
-- 3. Capstone for G1.
--
-- BirthdayOrdered bundles the carrier + index. Conway-induction on
-- BirthdayOrdered descends through `index` strictly; this is the
-- measure on which G2-G8's recursive constructions terminate.
------------------------------------------------------------------------
