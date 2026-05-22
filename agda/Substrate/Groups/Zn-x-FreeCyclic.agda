------------------------------------------------------------------------
-- Substrate.Groups.Zn-x-FreeCyclic
--
-- Parametric module for the 2-D word algebra Zₙ × ℕ via DirectProduct.
--
-- Takes any cyclic Coxeter instance's Core data (Word, ++, ε, etc.)
-- and produces the DirectProduct with FreeCyclic-Coxeter.
--
-- Consolidates the Z3-x-FreeCyclic / Z4-x-FreeCyclic / Z5-x-FreeCyclic
-- per-n boilerplate: each instance becomes a one-line application.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Eq using (_≡_)

module Substrate.Groups.Zn-x-FreeCyclic
  (Zn-Word        : Set)
  (_Zn-++_        : Zn-Word → Zn-Word → Zn-Word)
  (Zn-ε           : Zn-Word)
  (Zn-++-assoc    : (a b c : Zn-Word) → (a Zn-++ b) Zn-++ c ≡ a Zn-++ (b Zn-++ c))
  (Zn-Canonical            : Zn-Word → Set)
  (Zn-normalize            : Zn-Word → Zn-Word)
  (Zn-normalize-canonical  : (w : Zn-Word) → Zn-Canonical (Zn-normalize w))
  (Zn-canonical-is-fixed   : {w : Zn-Word} → Zn-Canonical w → Zn-normalize w ≡ w)
  (Zn-normalize-distrib    : (a b : Zn-Word) →
    Zn-normalize (a Zn-++ b) ≡ Zn-normalize (Zn-normalize a Zn-++ Zn-normalize b))
  where

import Substrate.Groups.FreeCyclic-Coxeter as F

open import Substrate.Groups.Coxeter.DirectProduct
  Zn-Word _Zn-++_ Zn-ε Zn-++-assoc
    Zn-Canonical Zn-normalize Zn-normalize-canonical
    Zn-canonical-is-fixed Zn-normalize-distrib
  (F.Word F.Gen) (F._++_) F.ε F.++-assoc
    F.Canonical F.normalize F.normalize-canonical
    F.canonical-is-fixed-Free F.normalize-distrib
  public
