------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.Codeword.Type
--
-- Codeword = Bool⁵ — the 32-element ambient. Plus the 5 bit accessors.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.Codeword.Type where

open import Substrate.Foundation.Bool using (Bool)
open import Substrate.Foundation.Product using (_×_; _,_)

Codeword : Set
Codeword = Bool × Bool × Bool × Bool × Bool

bit₀ bit₁ bit₂ bit₃ bit₄ : Codeword → Bool
bit₀ (x , _ , _ , _ , _) = x
bit₁ (_ , x , _ , _ , _) = x
bit₂ (_ , _ , x , _ , _) = x
bit₃ (_ , _ , _ , x , _) = x
bit₄ (_ , _ , _ , _ , x) = x
