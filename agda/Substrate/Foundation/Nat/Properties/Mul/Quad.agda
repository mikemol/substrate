------------------------------------------------------------------------
-- Substrate.Foundation.Nat.Properties.Mul.Quad
--
-- Defines: quad
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Nat.Properties.Mul; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Nat.Properties.Mul.Quad where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Times
open import Substrate.Foundation.Nat.Properties.Mul.TimesComm
open import Substrate.Foundation.Nat.Properties.Mul.TimesAssoc
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans



------------------------------------------------------------------------
-- Middle-factor interchange of a product of two products (reusable for
-- multi-factor reassociations, e.g. ℚ distributivity denominators).
------------------------------------------------------------------------

quad : (w x y z : ℕ) → (w * x) * (y * z) ≡ (w * y) * (x * z)
quad w x y z =
  trans (*-assoc w x (y * z))
  (trans (cong (w *_) (sym (*-assoc x y z)))
  (trans (cong (λ t → w * (t * z)) (*-comm x y))
  (trans (cong (w *_) (*-assoc y x z))
         (sym (*-assoc w y (x * z))))))
