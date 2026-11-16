------------------------------------------------------------------------
-- Substrate.Foundation.Bool.BoolToNat
--
-- Defines: boolToℕ
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Bool; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Bool.BoolToNat where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Bool.Not




-- ⟡A4: the canonical Bool→ℕ indicator (true↦1, false↦0). A DEFINITION, so it lives in the def
-- module (not Bool.Properties) — definition-provider consumers may use it without breaking
-- def/proof separation. Single source for the sites that re-defined it (boolToℕ / bToℕ / bit).
boolToℕ : Bool → ℕ
boolToℕ true  = suc zero
boolToℕ false = zero
