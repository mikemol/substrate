------------------------------------------------------------------------
-- Substrate.Foundation.Bool
--
-- Substrate-native Bool. Phase 2: native datatype + BUILTIN BOOL.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Bool where

data Bool : Set where
  true  : Bool
  false : Bool

{-# BUILTIN BOOL  Bool  #-}
{-# BUILTIN TRUE  true  #-}
{-# BUILTIN FALSE false #-}

infixr 6 _∧_
infixr 5 _∨_ _xor_

_∧_ : Bool → Bool → Bool
true  ∧ b = b
false ∧ _ = false

_∨_ : Bool → Bool → Bool
true  ∨ _ = true
false ∨ b = b

not : Bool → Bool
not true  = false
not false = true

_xor_ : Bool → Bool → Bool
true  xor b = not b
false xor b = b

if_then_else_ : {A : Set} → Bool → A → A → A
if true  then x else _ = x
if false then _ else y = y

open import Substrate.Foundation.Nat using (ℕ; zero; suc)

-- ⟡A4: the canonical Bool→ℕ indicator (true↦1, false↦0). A DEFINITION, so it lives in the def
-- module (not Bool.Properties) — definition-provider consumers may use it without breaking
-- def/proof separation. Single source for the sites that re-defined it (boolToℕ / bToℕ / bit).
boolToℕ : Bool → ℕ
boolToℕ true  = suc zero
boolToℕ false = zero
