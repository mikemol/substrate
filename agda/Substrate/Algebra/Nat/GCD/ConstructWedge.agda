------------------------------------------------------------------------
-- Substrate.Algebra.Nat.GCD.ConstructWedge
--
-- construct-wedge : (a b : ℕ) → Wedge a (suc b).
-- Bridges substrate-native DivMod (`_div-suc_` + `_mod-suc_` +
-- `div-mod-eq`) to the Wedge structural decomposition record.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.GCD.ConstructWedge where

open import Substrate.Foundation.Nat using (ℕ; suc; _+_; _*_)
open import Substrate.Foundation.Nat.Properties.Add using (+-comm)
open import Substrate.Foundation.Eq using (trans)
open import Substrate.Algebra.Nat.DivMod
  using (_mod-suc_; _div-suc_; mod-suc-bound; div-mod-eq)
open import Substrate.Algebra.Nat.GCD.Wedge using () renaming (Wedge to Wedge⟦b7e6a995⟧)
construct-wedge : (a b : ℕ) → Wedge⟦b7e6a995⟧ a (suc b)
construct-wedge a b = record
  { quotient  = a div-suc b
  ; remainder = a mod-suc b
  ; wedge-eq  =
      trans (div-mod-eq a b)
            (+-comm (a mod-suc b) ((a div-suc b) * suc b))
  ; r<b       = mod-suc-bound a b
  }
