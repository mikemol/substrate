------------------------------------------------------------------------
-- Substrate.FUSep.FUSepConv.Adjunction
--
-- Defines: Adjunction, Coin, Fin, coin-obs, fin-obs, fwd, obs
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.FUSep.FUSepConv; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.FUSep.FUSepConv.Adjunction where

open import Substrate.Foundation.Eq
open import Substrate.FUSep.FUSepConv.EqSetoid
open import Substrate.Category.UniversalProperty.DiagonalDoFComputable
open import Substrate.Category.UniversalProperty.ExtrudeIOCostreamBisim.Approx



------------------------------------------------------------------------
-- THE ADJUNCTION DATA, HetQ-style — one record, no loose parameters.
--   Fin  : the finite/initial equality (conversion ≈ — the ℚ side, cross-mult).
--   Coin : the coinductive/final equality (bisimilarity ≋ — the R side).
--   obs  : the head observation (the "leading quotient" / CF digit).
--   fwd  : the UNIT's forward leg — Fin ⟹ Coin (= ObsBisim.≈⟹≋ = ana, ADD 100).
--   coin-obs : Coin's head projection (= ObsBisim.obs-eq — same value ⟹ same head).
------------------------------------------------------------------------
-- ⟡set1-paydown (consumer of EqSetoid): EqSetoid now parameterizes its relation,
-- so the two per-side relations _≈ᶠ_/_≈ᶜ_ move into Adjunction as explicit fields
-- (they were previously read back via `_≈_ Fin` / `_≈_ Coin` projections).
-- ⟡set1-rp-smalltail: the two relations are PARAMETERS now (mirrors EqSetoid's own paydown
-- above); the record drops Set₁→Set.
record Adjunction (C : Set) (Obs : Set)
                  (_≈ᶠ_ : C → C → Set)     -- finite (conversion) relation — Fin's carrier-relation
                  (_≈ᶜ_ : C → C → Set)     -- coinductive (bisimilarity) relation — Coin's
                  : Set where
  field
    Fin      : EqSetoid C _≈ᶠ_
    Coin     : EqSetoid C _≈ᶜ_
    obs      : C → Obs
    fwd      : ∀ {a b} → a ≈ᶠ b → a ≈ᶜ b
    coin-obs : ∀ {a b} → a ≈ᶜ b → obs a ≡ obs b
    -- obs respects the finite equality (the head-invariant on the ℚ side).
    fin-obs  : ∀ {a b} → a ≈ᶠ b → obs a ≡ obs b
