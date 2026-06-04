------------------------------------------------------------------------
-- Substrate.Algebra.F2.Transfer
--
-- M-11 full machinery sub-slice 3. Section/lift operations + the
-- transfer map: the cohomological composite F₂^m → F₂^n → F₂^n → F₂^m
-- (lift via a section, apply an automorphism, project back).
--
-- This is the formal machinery for the "lift-with-torsion / apply
-- automorphism / project-down-with-torsion" composite that the
-- chirality-rotation conjecture identifies as the mechanism for
-- transitioning between chirality phases via codes.
--
-- Structure:
--   * `Section m n` record bundles (lift, drop, drop-lift-witness)
--     for a left-inverse pair `lift : Linear m n` and `drop : Linear n m`
--     with `drop ∘L lift ≡ id` (pointwise).
--   * `transfer-map S τ` for τ : Linear n n produces an endomorphism
--     of F₂^m: `drop ∘L (τ ∘L lift)`.
--   * For τ = id-L, the transfer reduces to drop ∘L lift = id (via
--     the section property). For non-identity τ, the transfer can be
--     a non-trivial endomorphism — this is the cohomological transfer.
--
-- The "torsion" in the chirality-rotation conjecture corresponds to:
--   * Choice of section (different sections = different "lift-with-
--     torsion" rules); a section is determined by what value the lift
--     puts in the dropped coordinates.
--   * The automorphism τ in F₂^n need not commute with the section.
--
-- Concrete consumers (deferred to follow-up slices):
--   * F₂³ ↔ F₂⁵ sections for chirality rotation through Codeword.
--   * F₂³ ↔ F₂⁸ sections for chirality rotation through ExtHamming.
--   * Computation of specific transfer maps for given τ ∈ GL(n, F₂).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Transfer where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Eq
  using (_≡_; refl; trans; cong)

open import Substrate.Algebra.F2
open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.Linear

------------------------------------------------------------------------
-- Section record: a left-inverse pair of F₂-linear maps.
--
-- (lift : Linear m n, drop : Linear n m) with `drop ∘ lift ≡ id`.
-- The section "lifts" m-dim vectors into n-dim space (n ≥ m); drop
-- "projects" back. The drop-lift property ensures we can recover the
-- original m-dim vector after lifting + dropping (information is
-- preserved by the section).
--
-- The section's "torsion content" is implicit in the choice of lift
-- — the lift assigns specific values to the "extra" coordinates that
-- drop discards.
------------------------------------------------------------------------

record Section (m n : ℕ) : Set where      -- ⟦shape:35bdd582 lift,drop,drop-lift⟧
  field
    lift      : Linear m n
    drop      : Linear n m
    drop-lift : ∀ (v : Vector m) → apply drop (apply lift v) ≡ v

------------------------------------------------------------------------
-- The transfer map: F₂^m → F₂^m through F₂^n via lift, automorphism,
-- and drop.
--
--   transfer-map S τ = drop ∘L (τ ∘L lift)
--
-- For τ = id-L, this reduces to drop ∘L lift = id (via drop-lift).
-- For non-trivial τ (in particular, τ that does NOT commute with the
-- section), the transfer is a non-identity endomorphism of F₂^m. This
-- captures the cohomological transfer: rotating chirality phases by
-- "lifting through" a higher-dimensional automorphism.
------------------------------------------------------------------------

transfer-map :
  ∀ {m n} → Section m n → Linear n n → Linear m m
transfer-map S τ = drop S ∘L (τ ∘L lift S)
  where open Section

------------------------------------------------------------------------
-- The transfer-id property: transfer with identity automorphism is
-- the identity endomorphism (by the section's drop-lift property).
--
-- This validates that the transfer machinery is well-defined: in the
-- "trivial" case (τ = identity), nothing happens. Non-trivial rotation
-- of chirality phases requires non-identity τ.
------------------------------------------------------------------------

transfer-id :
  ∀ {m n} (S : Section m n) (v : Vector m) →
  apply (transfer-map S id-L) v ≡ v
transfer-id S v = drop-lift v
  where open Section S

------------------------------------------------------------------------
-- Cohomological interpretation (documentation).
--
-- The transfer map p ∘ τ ∘ σ is the standard "transfer" operation
-- between cohomology groups, restricted here to F₂-vector spaces.
-- In the chirality-rotation context:
--
--   * σ (= lift) IS the choice of representative for each "phase"
--     at the lower scale (chirality-axis embeddings into the larger
--     space). Different sections = different phase choices.
--
--   * τ ∈ GL(n, F₂) IS the automorphism at the higher scale that
--     "rotates between phases." When τ permutes chirality choices
--     at the lower scale (via PG action), the transfer realizes that
--     permutation at the lower scale.
--
--   * p (= drop) IS the projection that maps back to the lower scale.
--     The projection respects the V₄/chirality split (per the 3+1
--     parity / Hodge-dual analysis).
--
-- The full chirality-rotation framework will use:
--   * For chirality-axis swap at n=3: F₂³ → F₂⁵ section (axes = 0),
--     GL(5, F₂) automorphism swapping axis bits, projection back.
--     The transfer permutes the 7 chirality choices at F₂³ (or fixes
--     them, depending on τ).
--   * Higher scales: analogous via larger sections.
------------------------------------------------------------------------
