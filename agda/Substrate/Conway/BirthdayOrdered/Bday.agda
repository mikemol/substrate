------------------------------------------------------------------------
-- Substrate.Conway.BirthdayOrdered.Bday
--
-- Defines: bday
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Conway.BirthdayOrdered; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Conway.BirthdayOrdered.Bday where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Conway.SurrealFinite
open import Substrate.Conway.Birthday
open import Substrate.Conway.BirthdayOrdered.BirthdayOrdered



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
