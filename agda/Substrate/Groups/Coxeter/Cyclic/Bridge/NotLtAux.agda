------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Cyclic.Bridge.NotLtAux
--
-- Defines: not-lt-aux
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Groups.Coxeter.Cyclic.Bridge; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Coxeter.Cyclic.Bridge.NotLtAux where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Lt
open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Negation.Not
open import Substrate.Foundation.Empty.BotElim



------------------------------------------------------------------------
-- For k : Fin (suc n) where ¬ (toℕ k < n), toℕ k must equal n.
------------------------------------------------------------------------

not-lt-aux : (x y : ℕ) → x < suc y → ¬ (x < y) → x ≡ y
not-lt-aux zero    zero    _              _      = refl
not-lt-aux zero    (suc y) _              ¬0<sy  = ⊥-elim (¬0<sy (s≤s z≤n))
not-lt-aux (suc x) zero    (s≤s ())       _
not-lt-aux (suc x) (suc y) (s≤s x<sy)     ¬sx<sy = cong suc
  (not-lt-aux x y x<sy (λ x<y → ¬sx<sy (s≤s x<y)))
