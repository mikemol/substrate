------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.LimitBackedGraded — ⟡C2g-m-limit (graded): the limit/product
-- (map-IN mediating) UP as a Set₀ graded backing.
--
-- Migrates the flat `limit-backed : BackedUP` (LimitBacked.agda:49). Class B CARE-HIGHEST: Sol is
-- MAP-valued (⊤ → Fin 1 → ℕ) and the flat Witness is a Π-indexed cone-commute, not `_≡_`; the graded
-- Contentfulᴳ demands propositional equality of the mediating MAPS. So content refutes t ≡ mediate f
-- not by a bare `λ ()` but by cong-applying at the point (tt, fzero) to extract 1 ≡ 0, then refuting.
-- solve = mediate theLimit; `solves` (mediate-commutes) is dropped.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.LimitBackedGraded where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Unit using (⊤; tt)
open import Substrate.Foundation.Eq using (_≡_; cong)
open import Substrate.Foundation.Negation using (¬_)
open import Substrate.Foundation.Product using (_,_)
open import Substrate.Category.LimitUniversalProperty using (product-mediate)
open import Substrate.Category.UniversalProperty using (SourceP; TargetP)
open import Substrate.Category.UniversalProperty.Instances using (ConeLimit-UP)
open import Substrate.Category.UPArrowGraded using (UPArrowᴳ; mkUP)
open import Substrate.Category.UniversalProperty.BackedGraded using (BackedUPᴳ)

-- solve = mediate into the concrete product limit (product-LimitUP 1 (λ _ → ℕ), apex ⊤ — the same
-- instance ConeLimit-UP wraps). Inlined (NOT a top-level `theLimit : LimitUP` def) so no Set₁-inhabiting
-- term is added — the flat LimitBacked already contributes that one to the ratchet baseline.
limit-solve : SourceP ConeLimit-UP → TargetP ConeLimit-UP
limit-solve f = product-mediate 1 (λ _ → ℕ) f

limit-arrowᴳ : UPArrowᴳ (λ _ → SourceP ConeLimit-UP) (λ _ → TargetP ConeLimit-UP)
limit-arrowᴳ = mkUP limit-solve

-- refute 1 ≡ 0.
1≢0ᴸ : ¬ (1 ≡ 0)
1≢0ᴸ ()

-- content: the all-0 cone mediates to the all-0 map; candidate (λ _ _ → 1) differs at (tt, fzero).
limit-backedᴳ : BackedUPᴳ (λ _ → SourceP ConeLimit-UP) (λ _ → TargetP ConeLimit-UP)
limit-backedᴳ = record
  { arrowᴳ  = limit-arrowᴳ
  ; content = 0 , (λ _ _ → 0) , (λ _ _ → 1) , λ eq → 1≢0ᴸ (cong (λ h → h tt fzero) eq)
  }
