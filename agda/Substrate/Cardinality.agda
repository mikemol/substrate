------------------------------------------------------------------------
-- Substrate.Cardinality
--
-- Slice 15: explicit Fin n bijections for the catalog's small types.
-- Makes the catalog's numerical claims (24 signatures, 6 orbits, 8
-- reserved, 4 V_4-translates per orbit, etc.) machine-checked rather
-- than implicit in earlier slices' bijections.
--
-- Six basic cardinality theorems:
--
--   Axis ↔ Fin 4         |Axis| = 4
--   V₄ ↔ Fin 4           |V₄| = 4
--   Pairing ↔ Fin 3      |Pairing| = 3
--   Chirality ↔ Fin 2    |Chirality| = 2
--   OrbitKey ↔ Fin 6     |OrbitKey| = 6 (Pairing × Chirality)
--   Axis × Bool ↔ Fin 8  |Reserved-shape| = 8
--
-- Anchor-parametric ordering note (per
-- [[feedback-ordering-is-chirality-choice]]): each of these
-- bijections uses a SPECIFIC ORDERING (declaration order for Axis,
-- V₄, Pairing; even-before-odd for Chirality; etc.). This is a
-- CONVENTION, not a structural fact. The cardinality (|X| = n) is
-- the structural claim; the bijection chooses one presentation
-- among the possible finite enumerations. (The "differs by an
-- inner automorphism of S_n" framing is prose-level; promoting it
-- to a theorem would require a permutation-action on enumerations,
-- not developed here.)
--
-- Downstream cardinalities follow by composition with existing
-- bijections; deferred:
--
--   Reserved ↔ Fin 8     via Reserved ↔ Axis × Bool (slice 10)
--                         + Axis × Bool ↔ Fin 8 (here).
--   TotalSpace ↔ Fin 24  via OrbitKey × V₄ (= TotalSpace) + product.
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
open import Data.Bool using (Bool; true; false)
open import Data.Nat using (ℕ; zero; suc)
open import Data.Fin using (Fin; zero; suc)
open import Data.Product using (_×_; _,_; proj₁; proj₂)
open import Function.Bundles using (_↔_; mk↔ₛ′)
open import Relation.Binary.PropositionalEquality
  using (_≡_; refl; sym; trans; cong)

open import Substrate.Axes using (Axis; D; C; S; W)
open import Substrate.Groups.V4 using (V₄; e; α; β; γ)
open import Substrate.Cocycles.V4Signature
  using (Pairing; α-pair; β-pair; γ-pair;
         Chirality; even; odd;
         OrbitKey)

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
    to-from zero                       = refl
    to-from (suc zero)                 = refl
    to-from (suc (suc zero))           = refl
    to-from (suc (suc (suc zero)))     = refl

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
    to-from zero                       = refl
    to-from (suc zero)                 = refl
    to-from (suc (suc zero))           = refl
    to-from (suc (suc (suc zero)))     = refl

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
    to-from zero             = refl
    to-from (suc zero)       = refl
    to-from (suc (suc zero)) = refl

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
    to-from zero       = refl
    to-from (suc zero) = refl

    from-to : (c : Chirality) → from (to c) ≡ c
    from-to even = refl
    from-to odd  = refl

------------------------------------------------------------------------
-- OrbitKey ↔ Fin 6
--
-- The 6 (Pairing, Chirality) combinations, enumerated in
-- (α, β, γ) × (even, odd) order.
------------------------------------------------------------------------

orbitkey-↔-fin6 : OrbitKey ↔ Fin 6
orbitkey-↔-fin6 = mk↔ₛ′ to from to-from from-to
  where
    to : OrbitKey → Fin 6
    to (α-pair , even) = zero
    to (α-pair , odd)  = suc zero
    to (β-pair , even) = suc (suc zero)
    to (β-pair , odd)  = suc (suc (suc zero))
    to (γ-pair , even) = suc (suc (suc (suc zero)))
    to (γ-pair , odd)  = suc (suc (suc (suc (suc zero))))

    from : Fin 6 → OrbitKey
    from zero                                   = α-pair , even
    from (suc zero)                             = α-pair , odd
    from (suc (suc zero))                       = β-pair , even
    from (suc (suc (suc zero)))                 = β-pair , odd
    from (suc (suc (suc (suc zero))))           = γ-pair , even
    from (suc (suc (suc (suc (suc zero)))))     = γ-pair , odd

    to-from : (i : Fin 6) → to (from i) ≡ i
    to-from zero                                   = refl
    to-from (suc zero)                             = refl
    to-from (suc (suc zero))                       = refl
    to-from (suc (suc (suc zero)))                 = refl
    to-from (suc (suc (suc (suc zero))))           = refl
    to-from (suc (suc (suc (suc (suc zero)))))     = refl

    from-to : (k : OrbitKey) → from (to k) ≡ k
    from-to (α-pair , even) = refl
    from-to (α-pair , odd)  = refl
    from-to (β-pair , even) = refl
    from-to (β-pair , odd)  = refl
    from-to (γ-pair , even) = refl
    from-to (γ-pair , odd)  = refl

------------------------------------------------------------------------
-- Axis × Bool ↔ Fin 8
--
-- The 8 (Axis × Bool) combinations, enumerated in (D, C, S, W) ×
-- (false, true) order.
------------------------------------------------------------------------

axis×bool-↔-fin8 : (Axis × Bool) ↔ Fin 8
axis×bool-↔-fin8 = mk↔ₛ′ to from to-from from-to
  where
    to : Axis × Bool → Fin 8
    to (D , false) = zero
    to (D , true)  = suc zero
    to (C , false) = suc (suc zero)
    to (C , true)  = suc (suc (suc zero))
    to (S , false) = suc (suc (suc (suc zero)))
    to (S , true)  = suc (suc (suc (suc (suc zero))))
    to (W , false) = suc (suc (suc (suc (suc (suc zero)))))
    to (W , true)  = suc (suc (suc (suc (suc (suc (suc zero))))))

    from : Fin 8 → Axis × Bool
    from zero                                                       = D , false
    from (suc zero)                                                 = D , true
    from (suc (suc zero))                                           = C , false
    from (suc (suc (suc zero)))                                     = C , true
    from (suc (suc (suc (suc zero))))                               = S , false
    from (suc (suc (suc (suc (suc zero)))))                         = S , true
    from (suc (suc (suc (suc (suc (suc zero))))))                   = W , false
    from (suc (suc (suc (suc (suc (suc (suc zero)))))))             = W , true

    to-from : (i : Fin 8) → to (from i) ≡ i
    to-from zero                                                       = refl
    to-from (suc zero)                                                 = refl
    to-from (suc (suc zero))                                           = refl
    to-from (suc (suc (suc zero)))                                     = refl
    to-from (suc (suc (suc (suc zero))))                               = refl
    to-from (suc (suc (suc (suc (suc zero)))))                         = refl
    to-from (suc (suc (suc (suc (suc (suc zero))))))                   = refl
    to-from (suc (suc (suc (suc (suc (suc (suc zero)))))))             = refl

    from-to : (xb : Axis × Bool) → from (to xb) ≡ xb
    from-to (D , false) = refl
    from-to (D , true)  = refl
    from-to (C , false) = refl
    from-to (C , true)  = refl
    from-to (S , false) = refl
    from-to (S , true)  = refl
    from-to (W , false) = refl
    from-to (W , true)  = refl

------------------------------------------------------------------------
-- Notes
--
-- 1. Each cardinality lemma above commits to a specific ORDERING of
--    its source type. The orderings are CONVENTIONS, not structural
--    facts — per [[feedback-ordering-is-chirality-choice]], the
--    cardinality (|X| = n) is structural; the specific bijection is
--    one presentation among the possible finite enumerations.
--    Downstream code MUST NOT depend on which ordering was chosen
--    (e.g., on whether D ↦ 0 or D ↦ 3).
--
-- 2. The six lemmas combine into downstream cardinalities by
--    composition with the bijections from earlier slices:
--
--    Reserved ↔ Fin 8:
--      slice 10's `Reserved↔SignedAxis` ⊕ `axis×bool-↔-fin8`.
--
--    TotalSpace ↔ Fin 24 (= |OrbitKey × V₄| = 6 × 4 = 24):
--      composition over OrbitKey × V₄. Needs a `Fin m × Fin n ↔ Fin
--      (m * n)` lemma (stdlib has `combine`/`remQuot`; integration
--      deferred).
--
--    Permutation ↔[≈] Fin 24:
--      slice 4's `TotalSpace↔Permutation` ⊕ `TotalSpace ↔ Fin 24`,
--      modulo pointwise ≈ on Permutation (strict _≡_ on Permutation
--      would need funext).
--
--    Live ↔[≈] Fin 24:
--      slice 11d's `Live≃Permutation` ⊕ `Permutation ↔[≈] Fin 24`.
--
--    Stab(anchor) ↔[≈] Fin 6:
--      slice 14d's `stab≃s₃ anchor` ⊕ |SFin.Permutation 3| = 6 (the
--      "S_3 has 6 elements" enumeration, deferred). Parametric in
--      anchor — no anchor-specific cardinality is stated.
--
-- 3. Anchor-parametricity discipline: per slice 14a's redirect, no
--    Stab(D)-specific cardinality lemma exists. The Stab cardinality
--    is uniform across all 4 choices of anchor, matching the
--    structural fact that any axis can serve as the anchor (clarified
--    foundation rule 4).
--
-- 4. Cross-references:
--    * Slice 10: Reserved ↔ Axis × Bool.
--    * Slice 4: TotalSpace ↔ Permutation.
--    * Slice 11d: Live ↔ Permutation.
--    * Slice 14d: Stab(anchor) ↔ SFin.Permutation 3.
------------------------------------------------------------------------
