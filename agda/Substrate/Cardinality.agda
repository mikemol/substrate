------------------------------------------------------------------------
-- Substrate.Cardinality
--
-- Slice 15: explicit Fin n bijections for the catalog's ATOMIC
-- small types. Makes the catalog's numerical claims machine-checked
-- rather than implicit in earlier slices' bijections.
--
-- Five atomic cardinality theorems:
--
--   Axis ↔ Fin 4         |Axis| = 4
--   V₄ ↔ Fin 4           |V₄| = 4
--   Pairing ↔ Fin 3      |Pairing| = 3
--   Chirality ↔ Fin 2    |Chirality| = 2
--   Bool ↔ Fin 2         |Bool| = 2  (↔-sym of stdlib's 2↔Bool)
--
-- "Atomic" here means: the source type is a direct sum-of-constants
-- (or stdlib primitive), not a product. Product cardinalities —
-- OrbitKey ↔ Fin 6 (= Pairing × Chirality), Axis × Bool ↔ Fin 8 —
-- live in Substrate.Cardinality.Product (slice 16), derived via
-- `cardinality-product` rather than re-enumerated. This split is
-- the [[feedback-expose-generator-not-orbit]] move: the product
-- forms are orbit elements of cardinality-product, and the
-- generator (= cardinality-product) is the right abstraction; only
-- the genuinely-primitive atomics need enumeration here.
--
-- Anchor-parametric ordering note (per
-- [[feedback-ordering-is-chirality-choice]]): each of these
-- bijections uses a SPECIFIC ORDERING (declaration order for Axis,
-- V₄, Pairing; even-before-odd for Chirality; false-before-true
-- inherited from stdlib's 2↔Bool). This is a CONVENTION, not a
-- structural fact. The cardinality (|X| = n) is the structural
-- claim; the bijection chooses one presentation among the possible
-- finite enumerations. (The "differs by an inner automorphism of
-- S_n" framing is prose-level; promoting it to a theorem would
-- require a permutation-action on enumerations, not developed
-- here.)
--
-- Downstream cardinalities (composed in slice 16 or deferred):
--
--   OrbitKey ↔ Fin 6     slice 16, via `cardinality-product
--                         pairing-↔-fin3 chirality-↔-fin2`.
--   Axis × Bool ↔ Fin 8  slice 16, via `cardinality-product
--                         axis-↔-fin4 bool-↔-fin2`.
--   OrbitKey × V₄ ↔ Fin 24
--                         slice 16.
--   TotalSpace ↔ Fin 24  slice 16 (definitional unfold).
--   Reserved ↔ Fin 8     via Reserved ↔ Axis × Bool (slice 10) +
--                         axis×bool-↔-fin8 (slice 16); deferred.
--   Permutation ↔[≈] Fin 24
--                         via TotalSpace ↔ Permutation (slice 4) +
--                         TotalSpace ↔ Fin 24. Modulo pointwise ≈,
--                         since strict _↔_ requires _≡_ on
--                         Permutation which would need funext.
--   Live ↔[≈] Fin 24     via Live ↔ Permutation (slice 11d).
--   Stab(anchor) ↔[≈] Fin 6
--                         via Stab(anchor) ↔ SFin.Permutation 3
--                         (slice 14d, parametric in anchor) +
--                         |SFin.Permutation 3| = 6 (= |S_3|, deferred
--                         to a future slice if downstream theorems
--                         need it).
--
-- No anchor-specific cardinality theorems are stated — there's no
-- |Stab(D)| = 6 here, only the parametric form.
--
-- See: catalog/cocycles.md § CY-5 — numerical claims.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cardinality where

open import Level using (0ℓ)
open import Substrate.Algebra.Bijection using (_↔_; mk↔ₛ′; ↔-sym)
open import Substrate.Foundation.Bool using (Bool; true; false)
open import Substrate.Foundation.Eq
  using (_≡_; refl; sym; trans; cong)
open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Fin.Cover using (fin-cover)
open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Product using (_,_)

open import Substrate.Axes using (Axis; D; C; S; W)
open import Substrate.Groups.V4 using (V₄; e; α; β; γ)
open import Substrate.Cocycles.V4Signature
  using (Pairing; α-pair; β-pair; γ-pair;
         Chirality; even; odd)

------------------------------------------------------------------------
-- Axis ↔ Fin 4
------------------------------------------------------------------------

axis-↔-fin4 : Axis ↔ Fin 4
axis-↔-fin4 = mk↔ₛ′ to from to-from from-to
  where
    to : Axis → Fin 4
    to D = zero
    to C = suc zero
    to S = suc (suc zero)
    to W = suc (suc (suc zero))

    from : Fin 4 → Axis
    from zero                       = D
    from (suc zero)                 = C
    from (suc (suc zero))           = S
    from (suc (suc (suc zero)))     = W

    to-from : (i : Fin 4) → to (from i) ≡ i
    to-from = fin-cover _ (refl , refl , refl , refl)

    from-to : (x : Axis) → from (to x) ≡ x
    from-to D = refl
    from-to C = refl
    from-to S = refl
    from-to W = refl

------------------------------------------------------------------------
-- V₄ ↔ Fin 4
------------------------------------------------------------------------

v4-↔-fin4 : V₄ ↔ Fin 4
v4-↔-fin4 = mk↔ₛ′ to from to-from from-to
  where
    to : V₄ → Fin 4
    to e = zero
    to α = suc zero
    to β = suc (suc zero)
    to γ = suc (suc (suc zero))

    from : Fin 4 → V₄
    from zero                       = e
    from (suc zero)                 = α
    from (suc (suc zero))           = β
    from (suc (suc (suc zero)))     = γ

    to-from : (i : Fin 4) → to (from i) ≡ i
    to-from = fin-cover _ (refl , refl , refl , refl)

    from-to : (v : V₄) → from (to v) ≡ v
    from-to e = refl
    from-to α = refl
    from-to β = refl
    from-to γ = refl

------------------------------------------------------------------------
-- Pairing ↔ Fin 3
------------------------------------------------------------------------

pairing-↔-fin3 : Pairing ↔ Fin 3
pairing-↔-fin3 = mk↔ₛ′ to from to-from from-to
  where
    to : Pairing → Fin 3
    to α-pair = zero
    to β-pair = suc zero
    to γ-pair = suc (suc zero)

    from : Fin 3 → Pairing
    from zero             = α-pair
    from (suc zero)       = β-pair
    from (suc (suc zero)) = γ-pair

    to-from : (i : Fin 3) → to (from i) ≡ i
    to-from = fin-cover _ (refl , refl , refl)

    from-to : (p : Pairing) → from (to p) ≡ p
    from-to α-pair = refl
    from-to β-pair = refl
    from-to γ-pair = refl

------------------------------------------------------------------------
-- Chirality ↔ Fin 2
------------------------------------------------------------------------

chirality-↔-fin2 : Chirality ↔ Fin 2
chirality-↔-fin2 = mk↔ₛ′ to from to-from from-to
  where
    to : Chirality → Fin 2
    to even = zero
    to odd  = suc zero

    from : Fin 2 → Chirality
    from zero       = even
    from (suc zero) = odd

    to-from : (i : Fin 2) → to (from i) ≡ i
    to-from = fin-cover _ (refl , refl)

    from-to : (c : Chirality) → from (to c) ≡ c
    from-to even = refl
    from-to odd  = refl

------------------------------------------------------------------------
-- Bool ↔ Fin 2
--
-- Re-export of stdlib's `2↔Bool : Fin 2 ↔ Bool` symmetrised, so the
-- convention is `false ↦ 0, true ↦ 1`. Used by slice 16 to compose
-- Axis × Bool ↔ Fin 8.
------------------------------------------------------------------------

bool-↔-fin2 : Bool ↔ Fin 2
bool-↔-fin2 = mk↔ₛ′ to from to-from from-to
  where
    to : Bool → Fin 2
    to false = zero
    to true  = suc zero

    from : Fin 2 → Bool
    from zero       = false
    from (suc zero) = true

    to-from : (i : Fin 2) → to (from i) ≡ i
    to-from = fin-cover _ (refl , refl)

    from-to : (b : Bool) → from (to b) ≡ b
    from-to false = refl
    from-to true  = refl

------------------------------------------------------------------------
-- Notes
--
-- 1. Each atomic cardinality lemma commits to a specific ORDERING
--    of its source type. The orderings are CONVENTIONS, not
--    structural facts — per [[feedback-ordering-is-chirality-
--    choice]], the cardinality (|X| = n) is structural; the
--    specific bijection is one presentation among the possible
--    finite enumerations. Downstream code MUST NOT depend on which
--    ordering was chosen (e.g., on whether D ↦ 0 or D ↦ 3).
--
-- 2. Why only ATOMIC enumerations live here: per [[feedback-expose-
--    generator-not-orbit]], product cardinalities like OrbitKey ↔
--    Fin 6 (= Pairing × Chirality) and Axis × Bool ↔ Fin 8 are
--    orbit elements of the `cardinality-product` generator
--    (Substrate.Cardinality.Product, slice 16). The generator is
--    the right abstraction; hand-enumerating its orbit elements
--    would be dead duplication. The five lemmas above are the
--    genuinely-primitive enumerations that the generator
--    consumes.
--
-- 3. Anchor-parametricity discipline: per slice 14a's redirect, no
--    Stab(D)-specific cardinality lemma exists. The Stab cardinality
--    is uniform across all 4 choices of anchor, matching the
--    structural fact that any axis can serve as the anchor (clarified
--    foundation rule 4).
--
-- 4. Cross-references:
--    * Slice 16: Cardinality.Product — product compositions
--      (orbitkey-↔-fin6, axis×bool-↔-fin8, orbitkey×v4-↔-fin24,
--      totalspace-↔-fin24).
--    * Slice 10: Reserved ↔ Axis × Bool.
--    * Slice 4: TotalSpace ↔ Permutation.
--    * Slice 11d: Live ↔ Permutation.
--    * Slice 14d: Stab(anchor) ↔ SFin.Permutation 3.
------------------------------------------------------------------------
