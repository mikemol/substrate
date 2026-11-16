------------------------------------------------------------------------
-- Residue witness: 1 = 001 (LSB-first), predicted 3, exact 1 — two bits
-- of the prediction are slack.
-- Context: Substrate/Algebra/Wedge/BinTrim/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.BinTrim.TrimOneWidth where

open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Bool.BoolToNat
open import Substrate.Foundation.Vec
open import Substrate.Algebra.Wedge.BinTrim.Trim
open import Substrate.Algebra.Wedge.BinTrim.ExactWidth
open import Substrate.Foundation.Eq

trim-one-width : exact-width (trim (true ∷ false ∷ false ∷ [])) ≡ 1
trim-one-width = refl
