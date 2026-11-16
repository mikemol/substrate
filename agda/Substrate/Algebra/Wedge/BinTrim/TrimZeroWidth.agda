------------------------------------------------------------------------
-- Residue witness: 0 = 000, predicted width 3, exact width 0.
-- Context: Substrate/Algebra/Wedge/BinTrim/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.BinTrim.TrimZeroWidth where

open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Bool.BoolToNat
open import Substrate.Foundation.Vec
open import Substrate.Algebra.Wedge.BinTrim.Trim
open import Substrate.Algebra.Wedge.BinTrim.ExactWidth
open import Substrate.Foundation.Eq

trim-zero-width : exact-width (trim (false ∷ false ∷ false ∷ [])) ≡ 0
trim-zero-width = refl
