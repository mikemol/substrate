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
