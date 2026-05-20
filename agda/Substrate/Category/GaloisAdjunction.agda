------------------------------------------------------------------------
-- Substrate.Category.GaloisAdjunction
--
-- The Galois bridge between bottom-up and top-down views of a group:
-- a PresentedGroup (= generators + relations + propositional equality)
-- on one side, a ConjugationCoalgebra (= group + conjugacy classes)
-- on the other, plus a structure-preserving bridge map between them.
--
-- T4 of the prime-factored-gauge arc per
-- [[prime-factored-gauge-arc]]. Load-bearing for T8 (Monster), where:
--
--   * the PresentedGroup view (Y₅₅₅ + spider) exists abstractly but
--     is computationally intractable (word problem is hard at Monster
--     scale)
--   * the ConjugationCoalgebra view (194 classes from ATLAS) is
--     constructively populatable
--   * the bridge lets us state Monster facts in whichever view is
--     accessible, with the other view's content imported via the
--     bridge
--
-- Per [[universal-property-discipline]] + [[categorical-name-first]]:
-- "Galois adjunction" / "Galois connection" — standard categorical
-- naming. The full equivalence-of-categories (round-trip in BOTH
-- directions) is the IDEAL claim; in practice, for groups like the
-- Monster, only the forward direction (presentation → classes) is
-- constructively accessible. The substrate's record captures
-- whichever direction is available; full bidirectional adjunctions
-- can be specialised follow-on records.
--
-- Per [[coalgebraic-not-consumer-driven]]: the substrate is
-- coalgebraic; the bridge from algebra (presentation) to coalgebra
-- (class structure) is the natural substrate direction.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.GaloisAdjunction where

open import Level using (Level; _⊔_) renaming (suc to lsuc)
open import Relation.Binary.PropositionalEquality
  using (_≡_; refl)

open import Substrate.Category.PresentedGroup using (PresentedGroup)
open import Substrate.Category.ConjugationCoalgebra using (ConjugationCoalgebra)

private
  variable
    ℓ : Level

------------------------------------------------------------------------
-- The GaloisAdjunction record.
--
-- Bundles a PresentedGroup + ConjugationCoalgebra of the same
-- underlying abstract group, with a forward bridge map and
-- compatibility axioms.
--
-- Forward direction: bridge : Carrier presentation → G coalgebra.
-- This sends a presentation-word (or equivalence class thereof) to
-- the underlying group element in the coalgebra view.
--
-- Compatibility: the bridge is a group homomorphism (preserves ·, ε,
-- ⁻¹) AND descends through the presentation's equivalence (∼-equal
-- elements have ≡-equal images).
--
-- The reverse direction (coalgebra → presentation) is NOT a
-- substrate field — it's intractable for groups where the
-- presentation's word problem is undecidable. Specific instances
-- with bidirectional bridges can be specialised records.
--
-- Substrate-pattern minimum-axiom record: presupposes both inputs
-- (PresentedGroup, ConjugationCoalgebra) are coherent on their own;
-- internalizes only the structure-preserving bridge.
------------------------------------------------------------------------

record GaloisAdjunction : Set (lsuc ℓ) where
  constructor mkGaloisAdjunction
  field
    presentation : PresentedGroup {ℓ}
    coalgebra    : ConjugationCoalgebra {ℓ}

  open PresentedGroup presentation
    renaming (Carrier to Cₚ; _·_ to _·ₚ_; ε to εₚ; _⁻¹ to _⁻¹ₚ; _∼_ to _∼ₚ_)
  open ConjugationCoalgebra coalgebra
    renaming (G to Cₘ; _·_ to _·ₘ_; ε to εₘ; _⁻¹ to _⁻¹ₘ)

  field
    bridge      : Cₚ → Cₘ
    bridge-·    : (a b : Cₚ) → bridge (a ·ₚ b) ≡ (bridge a) ·ₘ (bridge b)
    bridge-ε    : bridge εₚ ≡ εₘ
    bridge-⁻¹   : (a : Cₚ) → bridge (a ⁻¹ₚ) ≡ (bridge a) ⁻¹ₘ
    bridge-∼    : (a b : Cₚ) → a ∼ₚ b → bridge a ≡ bridge b

------------------------------------------------------------------------
-- Capstone — the bridge primitive in place.
--
-- T4 of the prime-factored-gauge arc per
-- [[prime-factored-gauge-arc]]. Completes the foundational 5-slice
-- batch (T0-T4):
--
--   T0 SylowDecomposition         — prime-factor structure
--   T1 PrimeFactoredGauge         — gauge + Sylow + torsor
--   T2 PresentedGroup             — bottom-up (algebra)
--   T3 ConjugationCoalgebra       — top-down (coalgebra)
--   T4 GaloisAdjunction (THIS)    — bridge between T2 and T3
--
-- Concrete instances expected (next batch, T5-T8):
--
--   * GL(3, F₂): both directions constructive. PresentedGroup via
--     A₃-type Coxeter relations; ConjugationCoalgebra via standard
--     character-table data; bridge by direct identification.
--
--   * Monster M: forward direction (presentation → classes) cited
--     from external mathematical content; backward direction
--     (classes → presentation) intractable in general. The
--     GaloisAdjunction record holds the forward bridge; the backward
--     direction is a meta-claim.
--
--   * Abelian Z/(p₁...pₙ): CRT structure makes both directions
--     trivially constructive. The bridge is the identity on the
--     direct-product representation.
--
-- Per [[shadow-architecture]]: this is the load-bearing primitive
-- enabling top-down work on groups where bottom-up is intractable.
-- Without T4, the substrate cannot honestly state Monster facts
-- bidirectionally.
--
-- Per [[universal-property-discipline]]: GaloisAdjunction names the
-- universal property "two views agree on operations." Specialised
-- equivalences (= both-direction-constructive) can be follow-on
-- specialisations of this record.
------------------------------------------------------------------------
