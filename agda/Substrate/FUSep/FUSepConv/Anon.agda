------------------------------------------------------------------------
-- Substrate.FUSep.FUSepConv.Anon
--
-- Defines: _, conv, val
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.FUSep.FUSepConv; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.FUSep.FUSepConv.Anon where

open import Substrate.Foundation.Product
open import Substrate.Foundation.Eq
open import Substrate.FUSep.FUSepConv.Eqsym
open import Substrate.FUSep.FUSepConv.Eqtrans
open import Substrate.FUSep.FUSepConv.EqSetoid
open import Substrate.FUSep.FUSepConv.Adjunction
open import Substrate.Category.UniversalProperty.DiagonalDoFComputable
open import Substrate.Category.UniversalProperty.ExtrudeIOCostreamBisim.Approx



module _ {C Obs : Set} {_≈ᶠ_ _≈ᶜ_ : C → C → Set} (A : Adjunction C Obs _≈ᶠ_ _≈ᶜ_) where
  open Adjunction A       -- (the relations are module params now; Fin/Coin/obs/laws from A)

  --------------------------------------------------------------------
  -- THE FINITE IMAGE (the ℚ side): a term REACHES A VALUE = converts (finitely)
  -- to a v. "The finite EEA trace hits base at the gcd" — the CF terminates.
  --------------------------------------------------------------------
  record Reaches (a : C) : Set where
    constructor reaches
    field
      val  : C
      conv : a ≈ᶠ val
  open Reaches public

  --------------------------------------------------------------------
  -- THE COINCIDENCE (⟡FU-sep-conv): given the RETRACTION on values — two VALUES
  -- with equal observation are finitely-equal (convergent recovers the rational;
  -- CFInvariance's shape-value-invariance on the finite side; HetQ's cross-mult:
  -- same value ⟹ finitely equal) — then ≋ REFLECTS to ≈ on value-reaching terms.
  -- With fwd (the forward unit), ≈ = ≋ ON THE FINITE IMAGE: the unit is id.
  --------------------------------------------------------------------
  module Coincidence
    (value-reflect : ∀ {a b} (ra : Reaches a) (rb : Reaches b)
                   → obs (val ra) ≡ obs (val rb) → val ra ≈ᶠ val rb)
    where

    -- ≋ REFLECTS to ≈ on the finite image.
    ≋⟹≈-finite : ∀ {a b} → Reaches a → Reaches b → a ≈ᶜ b → a ≈ᶠ b
    ≋⟹≈-finite ra rb a≋b =
      trans≈ Fin (conv ra)
        (trans≈ Fin (value-reflect ra rb obs-vals)
                    (sym≈ Fin (conv rb)))
      where
        obs-vals : obs (val ra) ≡ obs (val rb)
        obs-vals = ≡trans (≡sym (fin-obs (conv ra)))
                          (≡trans (coin-obs a≋b) (fin-obs (conv rb)))

    -- THE UNIT IS id ON THE FINITE IMAGE: ≈ = ≋ there. Off it (self-similar
    -- fixpoints) only fwd holds; ≋ is the correct equality, proved finitely on
    -- the fixpoint (CycleWire) — the dissolved objection, made precise.
    unit-id-on-finite :
      ∀ {a b} → Reaches a → Reaches b → (a ≈ᶠ b → a ≈ᶜ b) × (a ≈ᶜ b → a ≈ᶠ b)
    unit-id-on-finite ra rb = fwd , ≋⟹≈-finite ra rb
