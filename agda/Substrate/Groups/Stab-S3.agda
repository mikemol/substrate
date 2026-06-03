------------------------------------------------------------------------
-- Substrate.Groups.Stab-S3
--
-- Slice 14: parametric Stab(anchor) ≅ S_3 — anchor as a parameter.
-- Closes the second iso in S_4/V_4(anchor) ≅ S_3 for every anchor ∈
-- Axis.
--
-- Anchor-parametrisation rationale: there is nothing D-specific
-- about Stab(D). Every anchor a ∈ Axis defines a 6-element subgroup
-- Stab(a) ⊂ S_4 of permutations fixing a, and each is ≅ S_3.
-- Slice 3's `Stab-D` is the D-instance of this parametric Stab; the
-- two are definitionally equal (`Stab D σ ≡ Stab-D σ` syntactically),
-- so existing modules using Stab-D remain unaffected.
--
-- Per clarified_foundation.md rule 4 — anchor parametrisation.
--
-- The iso uses SFin.Permutation 3 (slice 5) as the canonical S_3.
-- The 12-case axis ↔ Fin 3 bridge is anchor-dependent.
--
-- IMPORTANT (chirality discipline): the specific ordering of the 3
-- non-anchor axes — "skip anchor, then list in declaration-order
-- (D, C, S, W)" — IS A CONVENTION, not a structural fact. There is
-- no privileged ordering; calling it "standard" would be a chirality-
-- level rigidification of the same shape as the Type-D drift in
-- CY-5 (see catalog clarification 2026-05-15 and
-- [[feedback-multi-reading-ambient-discipline]]).
--
-- The bijection is unique only up to composition with an arbitrary
-- S_3 permutation. Any of the 6 declaration-orderings of the 3
-- non-anchor axes gives an equally-valid bridge, and the resulting
-- Stab(anchor) ↔ Fin 3 ↔ S_3 chain differs by an inner S_3-
-- automorphism (conjugation). For Slice 14 we pick one specific
-- convention; downstream code MUST NOT rely on which one.
--
-- See: catalog/clarified_foundation.md rule 4;
--      Substrate.Groups.SemidirectProduct (slice 3) — Stab-D = Stab D;
--      Substrate.Groups.SFin (slice 5) — Permutation Fin 3.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Stab-S3 where

open import Substrate.Foundation.Level using (0ℓ)
open import Substrate.Foundation.Fin.Literals using (₁; ₂)
open import Substrate.Foundation.Empty using (⊥; ⊥-elim)
open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Vec using (Vec; []; _∷_; lookup)
open import Substrate.Foundation.Product using (Σ; _,_; proj₁; proj₂; _×_)
open import Substrate.Foundation.Eq
  using (_≡_; _≢_; refl; sym; trans; cong; sym-trans; trans-sym; cong-trans)

open import Substrate.Axes using (Axis; D; C; S; W; axis-cover; axis×axis-cover)
open import Substrate.Foundation.Fin.Cover using (fin-cover)
open import Substrate.Groups.S4 as S4
  using (Permutation; _≈_; _·_; _⁻¹; ε; ≈-refl; ≈-sym; inv-l; inv-r)
  renaming (apply to applyₛ; invₐ to invₐₛ)
import Substrate.Groups.SFin as SFin

------------------------------------------------------------------------
-- The parametric Stab predicate.
------------------------------------------------------------------------

Stab : Axis → Permutation → Set
Stab anchor σ = applyₛ σ anchor ≡ anchor

------------------------------------------------------------------------
-- Basic helpers.
------------------------------------------------------------------------

σ-injective :
  (σ : Permutation) (x y : Axis) →
  applyₛ σ x ≡ applyₛ σ y → x ≡ y
σ-injective σ x y eq =
  sym-trans (inv-l σ x) (cong-trans (invₐₛ σ) eq (inv-l σ y))

stab-preserves-≢ :
  (anchor : Axis) (σ : Permutation) → Stab anchor σ →
  (x : Axis) → x ≢ anchor → applyₛ σ x ≢ anchor
stab-preserves-≢ anchor σ σ-stab x x≢anc σx≡anc =
  x≢anc (σ-injective σ x anchor (trans-sym σx≡anc σ-stab))

Stab-inv :
  (anchor : Axis) (σ : Permutation) → Stab anchor σ → Stab anchor (σ ⁻¹)
Stab-inv anchor σ σ-stab =
  sym-trans (cong (invₐₛ σ) σ-stab) (inv-l σ anchor)

------------------------------------------------------------------------
-- Fin 3 ↔ non-anchor-axis bridges. 12 cases each direction.
------------------------------------------------------------------------

-- The common substructure of the forward bridge: the 3 non-anchor
-- axes of each anchor, "skip anchor, then declaration order (D,C,S,W)".
-- THIS vector IS the gauge convention the module header documents; the
-- forward map is lookup into it. (Any other ordering is an equally-valid
-- bridge differing by an inner S_3-automorphism — see header.)
--
-- NOTE: structurally this bridge pair IS the punctured-finite-set
-- bijection Fin (suc n) ∖ {k} ≅ Fin n, named generically in
-- Substrate.Foundation.Fin.Punctured (punchIn / punchOut) and
-- transported to the Axis layer in Substrate.Axes.Punctured.  Routing
-- THESE definitions through that primitive was attempted and reverted:
-- the transport makes the bridge non-definitional, which breaks the
-- DEFINITIONAL round-trip proofs in Stab-S3-Iso / Stab-S3-Hom (they
-- rely on `refl` reducing the concrete-anchor cases).  Migrating those
-- two consumers to subst-based round-trips is a scoped follow-up; until
-- then the lookup form below is kept because it preserves the 7
-- consumers' definitional proofs.
non-anchors : Axis → Vec Axis 3
non-anchors D = C ∷ S ∷ W ∷ []
non-anchors C = D ∷ S ∷ W ∷ []
non-anchors S = D ∷ C ∷ W ∷ []
non-anchors W = D ∷ C ∷ S ∷ []

fin3-to-non-anchor : Axis → Fin 3 → Axis
fin3-to-non-anchor anchor = lookup (non-anchors anchor)

fin3-to-non-anchor-≢ :
  (anchor : Axis) (i : Fin 3) → fin3-to-non-anchor anchor i ≢ anchor
fin3-to-non-anchor-≢ = axis-cover _
  ( fin-cover _ ((λ ()) , (λ ()) , (λ ()))
  , fin-cover _ ((λ ()) , (λ ()) , (λ ()))
  , fin-cover _ ((λ ()) , (λ ()) , (λ ()))
  , fin-cover _ ((λ ()) , (λ ()) , (λ ()))
  )

non-anchor-to-fin3 : (anchor x : Axis) → x ≢ anchor → Fin 3
non-anchor-to-fin3 D D x≢a = ⊥-elim (x≢a refl)
non-anchor-to-fin3 D C _   = zero
non-anchor-to-fin3 D S _   = suc zero
non-anchor-to-fin3 D W _   = suc ₁
non-anchor-to-fin3 C D _   = zero
non-anchor-to-fin3 C C x≢a = ⊥-elim (x≢a refl)
non-anchor-to-fin3 C S _   = suc zero
non-anchor-to-fin3 C W _   = suc ₁
non-anchor-to-fin3 S D _   = zero
non-anchor-to-fin3 S C _   = suc zero
non-anchor-to-fin3 S S x≢a = ⊥-elim (x≢a refl)
non-anchor-to-fin3 S W _   = suc ₁
non-anchor-to-fin3 W D _   = zero
non-anchor-to-fin3 W C _   = suc zero
non-anchor-to-fin3 W S _   = suc ₁
non-anchor-to-fin3 W W x≢a = ⊥-elim (x≢a refl)

fin3-non-anchor-fin3 :
  (anchor : Axis) (i : Fin 3) →
  non-anchor-to-fin3 anchor (fin3-to-non-anchor anchor i)
                            (fin3-to-non-anchor-≢ anchor i) ≡ i
fin3-non-anchor-fin3 = axis-cover _
  ( fin-cover _ (refl , refl , refl)
  , fin-cover _ (refl , refl , refl)
  , fin-cover _ (refl , refl , refl)
  , fin-cover _ (refl , refl , refl)
  )

non-anchor-fin3-non-anchor :
  (anchor x : Axis) (x≢a : x ≢ anchor) →
  fin3-to-non-anchor anchor (non-anchor-to-fin3 anchor x x≢a) ≡ x
non-anchor-fin3-non-anchor = axis×axis-cover _
  ( ( (λ x≢a → ⊥-elim (x≢a refl)) , (λ _ → refl) , (λ _ → refl) , (λ _ → refl) )
  , ( (λ _ → refl) , (λ x≢a → ⊥-elim (x≢a refl)) , (λ _ → refl) , (λ _ → refl) )
  , ( (λ _ → refl) , (λ _ → refl) , (λ x≢a → ⊥-elim (x≢a refl)) , (λ _ → refl) )
  , ( (λ _ → refl) , (λ _ → refl) , (λ _ → refl) , (λ x≢a → ⊥-elim (x≢a refl)) )
  )

------------------------------------------------------------------------
-- Forward restriction at the function level: Σ Permutation (Stab
-- anchor) → (Fin 3 → Fin 3). Bundles into SFin.Permutation 3 in
-- slice 14b along with the inv-l / inv-r proofs (which need
-- proof-irrelevance for non-anchor-to-fin3's ≢-component to chain
-- cleanly).
------------------------------------------------------------------------

restrict-apply :
  (anchor : Axis) (σ : Permutation) → Stab anchor σ → Fin 3 → Fin 3
restrict-apply anchor σ σ-stab i =
  non-anchor-to-fin3 anchor
    (applyₛ σ (fin3-to-non-anchor anchor i))
    (stab-preserves-≢ anchor σ σ-stab
                       (fin3-to-non-anchor anchor i)
                       (fin3-to-non-anchor-≢ anchor i))

restrict-invₐ :
  (anchor : Axis) (σ : Permutation) → Stab anchor σ → Fin 3 → Fin 3
restrict-invₐ anchor σ σ-stab =
  restrict-apply anchor (σ ⁻¹) (Stab-inv anchor σ σ-stab)

------------------------------------------------------------------------
-- Notes (Slice 14a scope)
--
-- This slice establishes parametric Stab(anchor) plus the bridges
-- Axis ↔ Fin 3 (anchor-skipping) with round trips, plus the forward
-- restriction `restrict-apply` and `restrict-invₐ` as functions.
--
-- Anchor-parametricity is now demonstrated: every anchor a ∈ Axis
-- gives a Stab(a) ⊂ S_4 subgroup that restricts to a Fin 3 → Fin 3
-- function. The discipline from clarified_foundation.md rule 4 is
-- applied at the slice 14a layer.
--
-- Slice 14b will:
--   * Add `non-anchor-to-fin3-irr` proof-irrelevance lemma (12 cases
--     refl + 4 ⊥-elim).
--   * Bundle restrict-apply + restrict-invₐ into SFin.Permutation 3
--     via the inv-l / inv-r proofs (chain via proof-irrelevance +
--     bridge round trips + S_4's inv-l / inv-r).
--   * Define the reverse `extend` map.
--   * Round-trips and Iso bundle.
--
-- Cross-references:
--   * Slice 3: Stab-D = Stab D (definitionally equal).
--   * Slice 5: SFin.Permutation 3 = S_3 carrier.
--   * Slice 12: Stab-D-Subgroup (which is Stab D-Subgroup).
--   * Clarified-foundation rule 4: anchor parametrisation.
------------------------------------------------------------------------
