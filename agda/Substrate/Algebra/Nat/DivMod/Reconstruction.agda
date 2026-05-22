------------------------------------------------------------------------
-- Substrate.Algebra.Nat.DivMod.Reconstruction
--
-- The fundamental DivMod equation:
--
--   div-mod-eq : ∀ a b → a ≡ (a mod-suc b) + (a div-suc b) * (suc b)
--
-- Mirrors stdlib's `m≡m%n+[m/n]*n`. Proof by induction on `a`,
-- dispatching on the same with-clause that defines _mod-suc_ and
-- _div-suc_. The NO branch (mod-suc wraps) uses Order.≤-tight to
-- conclude `a mod-suc b ≡ b`.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.DivMod.Reconstruction where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_; _*_; _<?_; s≤s)
open import Substrate.Foundation.Nat.Properties.Order using (≤-tight)
open import Substrate.Foundation.Negation using (yes; no)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong)
open import Substrate.Algebra.Nat.Mod using (_mod-suc_; mod-suc-bound)
open import Substrate.Algebra.Nat.DivMod.DivSuc using (_div-suc_)

div-mod-eq : (a b : ℕ) → a ≡ (a mod-suc b) + (a div-suc b) * (suc b)
div-mod-eq zero    _ = refl
div-mod-eq (suc a) b with suc (a mod-suc b) <? suc b | mod-suc-bound a b | div-mod-eq a b
... | yes _ | _      | ih = cong suc ih
... | no ¬p | bound  | ih =
  cong suc
    (trans ih
           (cong (_+ (a div-suc b) * suc b)
                 (≤-tight (a mod-suc b) b bound (λ p → ¬p (s≤s p)))))
