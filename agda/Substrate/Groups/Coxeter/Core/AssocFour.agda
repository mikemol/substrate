------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Core.AssocFour
--
-- Section 8 of Coxeter.Core. 4-way associativity, used by per-instance
-- 4-product theorems.
--   (a ++ b) ++ (c ++ d) ≡ a ++ (b ++ (c ++ d))
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Eq using (_≡_)

module Substrate.Groups.Coxeter.Core.AssocFour
  (Word : Set)
  (_++_ : Word → Word → Word)
  (++-assoc : (a b c : Word) → (a ++ b) ++ c ≡ a ++ (b ++ c))
  where

++-assoc-4 : (a b c d : Word) →
             (a ++ b) ++ (c ++ d) ≡ a ++ (b ++ (c ++ d))
++-assoc-4 a b c d = ++-assoc a b (c ++ d)
