------------------------------------------------------------------------
-- Substrate.Conway.Examples
--
-- S3 of the Surreal-numbers arc per [scratch/surreal_arc_plan.md].
--
-- Day-0 (Zero) and Day-1 (One, NegOne) worked surreal examples
-- demonstrating the SurrealFinite recursive shape on concrete
-- values. Smoke tests verify the constructor pattern.
--
-- Per [[feedback-comments-dont-overclaim]]: these are the SIMPLEST
-- surreals — Conway's hierarchy extends much further (1/2 at
-- birthday 2, ω at limit-birthday ω, etc.); the fragment lands
-- only the first two birthdays as workable examples.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Conway.Examples where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Groups.Coxeter.Word using (Word; []; _∷_)
open import Substrate.Conway.SurrealFinite using (SurrealFinite; ⟨_∣_⟩)
open import Substrate.Conway.Birthday using (birthday)

------------------------------------------------------------------------
-- 1. Day-0: Zero.
--
-- Conway: 0 = ⟨ {} ∣ {} ⟩. In my indexing: SurrealFinite 1 with
-- empty L and R Words (both at the absent type SurrealFinite 0).
------------------------------------------------------------------------

Zero : SurrealFinite 1
Zero = ⟨ [] ∣ [] ⟩

Zero-birthday : birthday Zero ≡ 0
Zero-birthday = refl

------------------------------------------------------------------------
-- 2. Day-1: One.
--
-- Conway: 1 = ⟨ {0} ∣ {} ⟩. In my indexing: SurrealFinite 2 with
-- L = single Zero, R = empty.
------------------------------------------------------------------------

One : SurrealFinite 2
One = ⟨ Zero ∷ [] ∣ [] ⟩

One-birthday : birthday One ≡ 1
One-birthday = refl

------------------------------------------------------------------------
-- 3. Day-1: NegOne.
--
-- Conway: -1 = ⟨ {} ∣ {0} ⟩. In my indexing: SurrealFinite 2 with
-- L = empty, R = single Zero.
------------------------------------------------------------------------

NegOne : SurrealFinite 2
NegOne = ⟨ [] ∣ Zero ∷ [] ⟩

NegOne-birthday : birthday NegOne ≡ 1
NegOne-birthday = refl

------------------------------------------------------------------------
-- 4. Capstone for S3.
--
-- Three canonical inhabitants demonstrate the carrier. S4-S6 add
-- the order relation; S7-S8 add arithmetic; S9 embeds ℤ into the
-- surreal hierarchy by extending these examples to arbitrary
-- integers.
------------------------------------------------------------------------
