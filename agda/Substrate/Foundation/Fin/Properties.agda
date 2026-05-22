------------------------------------------------------------------------
-- Substrate.Foundation.Fin.Properties
--
-- Substrate-native properties of Fin. Phase 2: re-exports the
-- decidable-equality + ordering helpers from Foundation.Fin so
-- downstream files migrating from stdlib's Data.Fin.Properties can
-- target this module.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Fin.Properties where

open import Substrate.Foundation.Fin public using (_≟_; _<_; _≤_)
