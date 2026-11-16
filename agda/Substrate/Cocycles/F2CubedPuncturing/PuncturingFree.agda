------------------------------------------------------------------------
-- Substrate.Cocycles.F2CubedPuncturing.PuncturingFree
--
-- Defines: puncturing-free
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Cocycles.F2CubedPuncturing; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.F2CubedPuncturing.PuncturingFree where

open import Substrate.Groups.F2Cubed
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.CongTrans
open import Substrate.Foundation.Eq.SymTrans
open import Substrate.Cocycles.F2CubedPuncturing.PunctureIndex



------------------------------------------------------------------------
-- Torsor structure: F_2³ acts freely transitively on PunctureIndex.
--
-- Free: g + t ≡ t  ⇒  g ≡ ε.
--   Argument: from g + t ≡ t, add t to the right.
--   (g + t) + t ≡ t + t
--   g + (t + t) ≡ t + t       (assoc)
--   g + ε ≡ ε                  (+-self on each side)
--   g ≡ ε                      (right identity)
--
-- Transitive: for any t₁, t₂, witness g = t₂ + t₁.
--   (t₂ + t₁) + t₁ ≡ t₂ + (t₁ + t₁) ≡ t₂ + ε ≡ t₂.
------------------------------------------------------------------------

puncturing-free :
  (g : F₂³) (t : PunctureIndex) → g + t ≡ t → g ≡ ε
puncturing-free g t eq =
  sym-trans (+-identityʳ g)
   (cong-trans (g +_) (sym (+-self t))
    (sym-trans (+-assoc g t t)
     (cong-trans (_+ t) eq (+-self t))))
