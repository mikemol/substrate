------------------------------------------------------------------------
-- Substrate.Category.BeckChevalley
--
-- Primitive #5 in the Substrate.Category.Primitives roadmap.
-- Names the Beck-Chevalley square / 2-cell — the categorical handle
-- for "when do two paths around a square agree, and when don't they?"
--
-- Substrate-friendly Set-level scoping: full Beck-Chevalley at the
-- functor/adjoint level requires adjoint pairs of functors and the
-- canonical natural transformation between transpose composites.
-- The Set-level version reduces to a square of functions with a
-- commutativity 2-cell.
--
-- Substrate-relevant use:
--
--   * The recurring [[project-3plus1-parity-universal]] manifests at
--     each meta-level as a BC-style square where two quotient paths
--     do NOT commute trivially — the "3+1" structure IS the 2-cell.
--
--   * The substrate's bridges (dim-3 ↔ dim-4 SymBilinForm,
--     ReservedBridge ↔ SelfDual, etc.) instantiate BC squares; the
--     bridge commutativity is the BC 2-cell.
--
--   * Non-commuting quotients across meta-levels of
--     [[project-tetrative-metacircularity]] are BC-failure 2-cells:
--     at each level, the next-meta-level structure measures the
--     non-commutativity of the current level's quotients.
--
-- Per `feedback_categorical_name_first`: Beck-Chevalley is the
-- standard categorical name. The substrate's "quotient curvature"
-- (per [[project-eliza-concept-orbit-catalog]]) is exactly the BC
-- failure 2-cell.
--
-- Per `feedback_multi_reading_ambient_discipline`: BC has multiple
-- readings — "non-commuting quotients," "natural transformation
-- between transpose-composite functors," "permutability of
-- congruences." All are aspects of the ambient BC square + cell.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.BeckChevalley where

open import Substrate.Foundation.Level using (Level)
open import Substrate.Foundation.Eq
  using (_≡_; refl; sym; trans; cong)

private
  variable
    ℓ : Level
    A B C D Z : Set ℓ

------------------------------------------------------------------------
-- N-1: BCSquare — a square of functions with a commutativity cell.
--
-- Given f : A → B, g : A → C, h : B → D, k : C → D, the BC square
-- packages the would-be commutativity:
--
--       f
--   A ----> B
--   |       |
-- g |       | h
--   v       v
--   C ----> D
--       k
--
-- with `cell` witnessing `h ∘ f = k ∘ g` pointwise.
------------------------------------------------------------------------

record BCSquare {A B C D : Set ℓ}
                (f : A → B) (g : A → C)
                (h : B → D) (k : C → D) : Set ℓ where
  field
    cell : (a : A) → h (f a) ≡ k (g a)

open BCSquare public

------------------------------------------------------------------------
-- N-2: BCSquare-identity — the trivial commuting case.
--
-- If h ∘ f and k ∘ g are literally the same function at every input
-- (cell = refl pointwise), the BC condition holds in the strongest
-- sense.
------------------------------------------------------------------------

bc-trivial : {A B C D : Set ℓ}
             (f : A → B) (g : A → C) (h : B → D) (k : C → D) →
             ((a : A) → h (f a) ≡ k (g a)) →
             BCSquare f g h k
bc-trivial f g h k commutes = record { cell = commutes }

------------------------------------------------------------------------
-- N-3: BC-failure-2-cell — the non-iso case.
--
-- The classical BC condition is "the canonical 2-cell is iso." At
-- the Set level, this is "h ∘ f ≡ k ∘ g" (the cell is refl). BC
-- FAILURE corresponds to the cell being non-trivial: there's a
-- bridge h(f(a)) ≡ k(g(a)) but it's not refl, capturing structural
-- content.
--
-- Substrate's [[project-3plus1-parity-universal]] at each meta-level
-- IS a BC-failure 2-cell: the "non-commutativity" of two quotients
-- (e.g., V4-orbit then chirality-axis vs the reverse) gives a non-
-- trivial cell. The "3+1" structure is the cell's structural content.
--
-- A `BCSquare` with `cell` provided IS the BC condition stated; the
-- iso/non-iso distinction is downstream (BC condition HOLDS at iso,
-- has failure-2-cell content at non-iso).
------------------------------------------------------------------------

-- The cell of a BC square, as a standalone function.
bc-cell : {A B C D : Set ℓ}
          {f : A → B} {g : A → C} {h : B → D} {k : C → D} →
          BCSquare f g h k → (a : A) → h (f a) ≡ k (g a)
bc-cell sq = cell sq

------------------------------------------------------------------------
-- N-3.5: Two specialised constructors for common BC patterns.
--
-- factor-via-pair-BCSquare — the "bilinear factors through TensorProduct
-- via the ⊗-Hom adjunction unit" shape. The g-side is identity; the
-- agreement is stated in the natural "direct ≡ lin ∘ embed" direction
-- (= the universal property's "the bilinear is recovered by composing
-- with the unit"). The combinator absorbs the sym.
--
--       embed
--   A ----> B
--   |       |
-- id|       | lin
--   v       v
--   A ----> D
--      direct
--
-- Used by:
--   * polynomial multiplication via TensorProduct (anti-diag-sum ∘ pair)
--   * bilinear-form-of evaluation via TensorProduct
--   * any other "linear function out of tensor product" instance
------------------------------------------------------------------------

factor-via-pair-BCSquare :
  {A B D : Set ℓ}
  (embed  : A → B)
  (lin    : B → D)
  (direct : A → D) →
  ((a : A) → direct a ≡ lin (embed a)) →
  BCSquare embed (λ x → x) lin direct
factor-via-pair-BCSquare embed lin direct agrees =
  bc-trivial embed (λ x → x) lin direct (λ a → sym (agrees a))

------------------------------------------------------------------------
-- section-BCSquare — the "round-trip closes" shape. The g- and k-sides
-- are identity, so the cell is exactly extract ∘ embed ≡ id (= embed
-- has a left inverse / is a section).
--
--       embed
--   A ----> B
--   |       |
-- id|       | extract
--   v       v
--   A ----> A
--       id
--
-- Used by any bridge with a one-sided round-trip witness (Bivector ↔
-- antisymmetric TensorProduct 4 4, etc.).
------------------------------------------------------------------------

section-BCSquare :
  {A B : Set ℓ}
  (embed   : A → B)
  (extract : B → A) →
  ((a : A) → extract (embed a) ≡ a) →
  BCSquare embed (λ x → x) extract (λ x → x)
section-BCSquare embed extract roundtrip =
  bc-trivial embed (λ x → x) extract (λ x → x) roundtrip

------------------------------------------------------------------------
-- retraction-BCSquare — counterpart to section-BCSquare. The "other
-- round-trip closes" shape: embed ∘ extract ≡ id_B (= embed has a
-- right inverse / extract is a retraction).
--
--       extract
--   B ----> A
--   |       |
-- id|       | embed
--   v       v
--   B ----> B
--       id
--
-- Used by bridges whose REVERSE round-trip closes (often on a
-- subtype, e.g., Bivector ↔ AntisymmetricTensor 4 closes the reverse
-- on antisymmetric inputs). Pairs with section-BCSquare to give a
-- full iso (both round-trips close).
------------------------------------------------------------------------

retraction-BCSquare :
  {A B : Set ℓ}
  (extract : B → A)
  (embed   : A → B) →
  ((b : B) → embed (extract b) ≡ b) →
  BCSquare extract (λ x → x) embed (λ x → x)
retraction-BCSquare extract embed roundtrip =
  bc-trivial extract (λ x → x) embed (λ x → x) roundtrip

------------------------------------------------------------------------
-- N-4: Capstone — BC primitive #5 introduced.
--
-- After this slice, the Category roadmap covers:
--
--   #1 Coalgebra (+ FiniteOrder + LagrangeOrder) ✓
--   #2 Equalizer ✓
--   #3 Pullback ✓
--   #4 Adjunction ✓
--   #5 BeckChevalley — THIS slice ✓ (Set-level)
--   #6 FreeLinearization — Prong B / continuous-side bridge, deferred
--
-- Substrate-level reading of BC:
--
--   * A BCSquare names the "two paths around a square commute" claim.
--     cell : h ∘ f ≡ k ∘ g pointwise.
--
--   * BC condition HOLDS when cell is refl-like (the simplest 2-cell).
--     Captures "the quotients permute / the bridges compose trivially."
--
--   * BC condition FAILS when cell is structurally non-trivial. The
--     2-cell's content IS the substrate's [[project-3plus1-parity-
--     universal]] manifestation at that level.
--
-- Concrete substrate instances ready to retrofit as BC squares:
--
--   * Dim-3 ↔ dim-4 SymBilinForm bridge: BCSquare relating bridged
--     metric-id and generic metric-id via the bridge equation.
--
--   * ReservedBridge: the 168-gauge family of identifications gives
--     a BCSquare with cell measuring the gauge choice's commutativity
--     with other operations.
--
--   * V₄-orbit decomposition + chirality-axis split: a BCSquare with
--     the "3+1" cell measuring non-commutativity (= the parity
--     universal).
--
--   * Hodge ★ + congruence action: BCSquare with cell measuring how
--     ★ commutes (or doesn't) with congruence-act.
--
-- Per [[project-tetrative-metacircularity]]: each meta-level's
-- structure may be readable as the BC 2-cell of the previous level's
-- quotient pair. This makes the meta-level ladder a sequence of
-- BC squares + cells.
--
-- Deferred follow-ons:
--
--   * **Full functor adjunction BC**: when both h and k are right
--     adjoints, the canonical 2-cell between their LEFT-adjoint
--     composites; BC asks whether this 2-cell is iso. Requires
--     adjoint-pair-of-functors infrastructure.
--
--   * **BC-iso predicate**: `IsBCIso : BCSquare → Set` measuring
--     whether the cell is iso (≡ refl in Set, ≅ in higher category).
--
--   * **Concrete BC instances**: V₄ + chirality decomposition,
--     dim-3 ↔ dim-4 bridges, ReservedBridge gauge family — each
--     as a `BCSquare` instance with cell + structural interpretation.
--
--   * **3+1 parity as BC failure capstone**: a memory connecting
--     [[project-3plus1-parity-universal]] to the BC failure
--     interpretation, completing the categorical naming.
------------------------------------------------------------------------
