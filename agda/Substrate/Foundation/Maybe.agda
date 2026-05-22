------------------------------------------------------------------------
-- Substrate.Foundation.Maybe
--
-- Substrate-native Maybe (option/partial-value sum). Mono-universe;
-- if a polymorphic version is needed, lift via a wrapping module.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Maybe where

data Maybe (A : Set) : Set where
  just    : A → Maybe A
  nothing : Maybe A
