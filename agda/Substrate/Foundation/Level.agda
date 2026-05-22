------------------------------------------------------------------------
-- Substrate.Foundation.Level
--
-- Substrate-native universe levels. Phase 2: imports directly from
-- Agda.Primitive (Agda compiler builtin, NOT stdlib).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Level where

open import Agda.Primitive public
  using (Level; _⊔_; Setω)
  renaming (lzero to zero; lsuc to suc)
