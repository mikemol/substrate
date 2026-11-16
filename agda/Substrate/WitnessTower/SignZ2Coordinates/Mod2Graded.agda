------------------------------------------------------------------------
-- Substrate.WitnessTower.SignZ2Coordinates.Mod2Graded
--
-- Defines: mod2-graded
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.SignZ2Coordinates; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.WitnessTower.SignZ2Coordinates.Mod2Graded where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Algebra.N-to-F2-Parity
open import Substrate.Algebra.Wedge.Graded
open import Substrate.Algebra.Wedge.Graded.Morphism
open import Substrate.WitnessTower.LehmerTowerMorphism.F2Target
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
open import Substrate.WitnessTower.SignZ2Coordinates.NatTarget



-- mod-2: parity IS a graded morphism ℕ⁺-target → F₂-target (parity-+). The n=2
-- reduction; the analogous mod-n reduction exists for every n (Route A lifts to
-- all Fₙ) — but there is NO mod-n SIGN for n>2 (Sₙ's abelianisation is Z/2), so
-- Route B is F₂-terminal. That asymmetry is the retained route-distinction, sharp.
mod2-graded : GradedDivStrMorphism ℕ⁺-target F₂-target
mod2-graded = record
  { map-C = parity ; map-R = parity ; respects-recon = λ n b r → parity-+ r b }
