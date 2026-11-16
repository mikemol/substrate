------------------------------------------------------------------------
-- Substrate.Category.Allegory.Refinement.BoundedWedgeDet
--
-- Defines: bounded-wedge-det
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.Allegory.Refinement; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Allegory.Refinement.BoundedWedgeDet where

open import Substrate.Foundation.Product
open import Substrate.Foundation.Nat.Lt
open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.Wedge
open import Substrate.Algebra.Wedge.BoundedIso
open import Substrate.Category.Allegory.Maps
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Category.Allegory.Refinement.BWedge



-- recon-bounded-unique (the wedge's uniqueness certificate) IS allegory
-- determinism = the fiber is a singleton = the certified wedge is a map.
bounded-wedge-det : (b : ℕ) → deterministic (BWedge b)
bounded-wedge-det b a (q₁ , r₁) (q₂ , r₂) (lt₁ , eq₁) (lt₂ , eq₂) =
  let u = recon-bounded-unique q₁ q₂ b r₁ r₂ lt₁ lt₂ (trans (sym eq₁) eq₂)
  in cong₂ _,_ (proj₁ u) (proj₂ u)
