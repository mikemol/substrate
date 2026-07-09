{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- FUSepConv — ⟡FU-sep-conv, via the ℚ ⊣ R adjunction + HetQ (operator, twice).
--
-- THE OBJECTION DISSOLVED (the quote): I asked to "extract a finite ≈ from an
-- infinite ≋ in general" — impossible without normalization AND the wrong ask.
-- The substrate never does that (RationalAdjunction, CycleWire, HetQ):
--   • Equality of INFINITE objects IS the bisimulation ≋ (final-coalgebra
--     equality), proved FINITELY on SELF-SIMILAR fixpoints (periodic CF /
--     quadratic irrational — CycleWire: cycle 2 [] ~ twos by coinduction).
--   • ≈ vs ≋ is the ℚ ⊣ R ADJUNCTION: ≈ the finite/INITIAL side (ℚ = a finite EEA
--     trace hitting base at the gcd), ≋ the coinductive/FINAL side (R = terminal
--     coalgebra). They COINCIDE on the FINITE IMAGE — unit ℚ → R → ℚ = id.
--
-- THE HetQ LESSON (structural, the operator's second pointer): HetQ's equality is
-- CROSS-MULTIPLICATION `a·d ≡ c·b` — a VALUE equality independent of presentation,
-- PACKAGED AS A SETOID (Quotient), reusing ONE equivalence machinery. My mixfix/
-- parameter friction (threading ≋ + its projections as loose params) was self-
-- inflicted: BUNDLE the equivalence into a record (like HetQ's CrossEq), and the
-- coincidence stands on its own with no parameter threading. This module does that.
------------------------------------------------------------------------

module Substrate.FUSep.FUSepConv where

open import Substrate.Foundation.Eq      using (_≡_; refl)
open import Substrate.Foundation.Product using (_×_; _,_)

-- ≡ helpers, local
private
  ≡sym : {A : Set} {x y : A} → x ≡ y → y ≡ x
  ≡sym refl = refl
  ≡trans : {A : Set} {x y z : A} → x ≡ y → y ≡ z → x ≡ z
  ≡trans refl q = q

------------------------------------------------------------------------
-- A SETOID: a carrier with an equivalence — the HetQ packaging. Bundling the
-- relation + its laws into ONE record is what avoids the mixfix/parameter
-- threading; the coincidence below takes TWO setoids over one carrier (the
-- finite ≈ side and the coinductive ≋ side) plus an observation.
------------------------------------------------------------------------
-- ⟡set1-paydown: parameterize the relation _≈_ : C → C → Set out of the record
-- (substrate stance: the carrier AND its relation are params, never fields). C was
-- already a record param; _≈_ joins it, so the record drops from Set₁ to Set.
-- Consumers write `EqSetoid C _≈_`; projection calls (`trans≈ Fin`) are unchanged.
record EqSetoid (C : Set) (_≈_ : C → C → Set) : Set where  -- cluster-local bundled setoid (refl≈/sym≈/trans≈); distinct-shape from Algebra.Setoid, pinned
  field
    refl≈ : ∀ {a} → a ≈ a
    sym≈  : ∀ {a b} → a ≈ b → b ≈ a
    trans≈ : ∀ {a b c} → a ≈ b → b ≈ c → a ≈ c
open EqSetoid public

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
record Adjunction (C : Set) (Obs : Set) : Set₁ where
  field
    _≈ᶠ_     : C → C → Set     -- finite (conversion) relation — Fin's carrier-relation
    _≈ᶜ_     : C → C → Set     -- coinductive (bisimilarity) relation — Coin's
    Fin      : EqSetoid C _≈ᶠ_
    Coin     : EqSetoid C _≈ᶜ_
    obs      : C → Obs
    fwd      : ∀ {a b} → a ≈ᶠ b → a ≈ᶜ b
    coin-obs : ∀ {a b} → a ≈ᶜ b → obs a ≡ obs b
    -- obs respects the finite equality (the head-invariant on the ℚ side).
    fin-obs  : ∀ {a b} → a ≈ᶠ b → obs a ≡ obs b

module _ {C Obs : Set} (A : Adjunction C Obs) where
  open Adjunction A       -- brings _≈ᶠ_ / _≈ᶜ_ (now Adjunction fields) into scope

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
