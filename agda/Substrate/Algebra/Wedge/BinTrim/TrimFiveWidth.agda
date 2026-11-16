------------------------------------------------------------------------
-- Residue witness: 5 = 101 (LSB-first), predicted 3, exact 3 — the
-- prediction is tight and the residue is empty.
-- Context: Substrate/Algebra/Wedge/BinTrim/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.BinTrim.TrimFiveWidth where

open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Bool.BoolToNat
open import Substrate.Foundation.Vec
open import Substrate.Algebra.Wedge.BinTrim.Trim
open import Substrate.Algebra.Wedge.BinTrim.ExactWidth
open import Substrate.Foundation.Eq

trim-five-width : exact-width (trim (true ∷ false ∷ true ∷ [])) ≡ 3
trim-five-width = refl
