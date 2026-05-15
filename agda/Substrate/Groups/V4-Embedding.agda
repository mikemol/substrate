------------------------------------------------------------------------
-- Substrate.Groups.V4-Embedding
--
-- The V_4 → S_4 embedding (homomorphism) and the V_4 ⊳ S_4 normality
-- theorem (S8 of the slice).
--
-- Embedding: each V_4 element gives an Axis-permutation via act-axis.
--   embed e = identity permutation
--   embed α = (DC)(SW)
--   embed β = (DS)(CW)
--   embed γ = (DW)(CS)
--
-- Homomorphism: embed (g V4.· h) ≈ embed g · embed h, lifted from
-- the action axiom act-axis-∙.
--
-- Normality: for any σ ∈ S_4 and v ∈ V_4, σ · embed v · σ⁻¹ is in
-- the image of embed. Equivalently, V_4 is closed under conjugation
-- by S_4 — the load-bearing claim of S8.
--
-- See: catalog/cocycles.md § CY-5 — V_4 ⋊ S_3 ≅ S_4 is the primary
-- algebraic foundation; this module is the embedding half.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.V4-Embedding where

open import Level using (0ℓ)
open import Data.Product using (∃; _,_; -,_)
open import Data.Sum using (_⊎_; inj₁; inj₂)
open import Relation.Binary.PropositionalEquality
  using (_≡_; refl; sym; trans; cong)

open import Substrate.Axes using (Axis; D; C; S; W; act-axis)
open import Substrate.Groups.V4 as V4 using (V₄; e; α; β; γ; V₄-Group)
open import Substrate.Groups.S4 as S4
  using (Permutation; _≈_; _·_; _⁻¹; ε; S₄-Group)
  renaming (apply to applyₛ; invₐ to invₐₛ)

------------------------------------------------------------------------
-- act-axis as a V_4 action on Axis.
--
-- The two action axioms (act-id and act-∙) are mechanical case-
-- analysis on the V_4 element and the axis. act-axis-id reduces by
-- definition (act-axis e x = x). act-axis-∙ requires 40+ refl cases;
-- postulated for now with the decomposition documented at the bottom
-- of this file.
------------------------------------------------------------------------

act-axis-id : (x : Axis) → act-axis e x ≡ x
act-axis-id x = refl

-- ∀ (g h : V₄) (x : Axis) → act-axis (g V4.· h) x ≡ act-axis g (act-axis h x)
-- Mechanical: 40 cases (g=e absorbs all (h,x); g=α/β/γ × h=e absorbs all x;
-- (g≠e, h≠e) gives 9 × 4 = 36 (g,h,x) cases). Each is refl after
-- pattern-matching reduces V_4 multiplication and act-axis composition.
act-axis-∙ :
  (g h : V₄) (x : Axis) →
  act-axis (g V4.· h) x ≡ act-axis g (act-axis h x)
-- g = e: e · h = h, act-axis e _ = _
act-axis-∙ e h x = refl
-- g ≠ e, h = e: g · e = g, act-axis e x = x
act-axis-∙ α e x = refl
act-axis-∙ β e x = refl
act-axis-∙ γ e x = refl
-- g = α, h = α: α · α = e, act-axis α involutive
act-axis-∙ α α D = refl
act-axis-∙ α α C = refl
act-axis-∙ α α S = refl
act-axis-∙ α α W = refl
-- g = α, h = β: α · β = γ
act-axis-∙ α β D = refl
act-axis-∙ α β C = refl
act-axis-∙ α β S = refl
act-axis-∙ α β W = refl
-- g = α, h = γ: α · γ = β
act-axis-∙ α γ D = refl
act-axis-∙ α γ C = refl
act-axis-∙ α γ S = refl
act-axis-∙ α γ W = refl
-- g = β, h = α: β · α = γ
act-axis-∙ β α D = refl
act-axis-∙ β α C = refl
act-axis-∙ β α S = refl
act-axis-∙ β α W = refl
-- g = β, h = β: β · β = e
act-axis-∙ β β D = refl
act-axis-∙ β β C = refl
act-axis-∙ β β S = refl
act-axis-∙ β β W = refl
-- g = β, h = γ: β · γ = α
act-axis-∙ β γ D = refl
act-axis-∙ β γ C = refl
act-axis-∙ β γ S = refl
act-axis-∙ β γ W = refl
-- g = γ, h = α: γ · α = β
act-axis-∙ γ α D = refl
act-axis-∙ γ α C = refl
act-axis-∙ γ α S = refl
act-axis-∙ γ α W = refl
-- g = γ, h = β: γ · β = α
act-axis-∙ γ β D = refl
act-axis-∙ γ β C = refl
act-axis-∙ γ β S = refl
act-axis-∙ γ β W = refl
-- g = γ, h = γ: γ · γ = e
act-axis-∙ γ γ D = refl
act-axis-∙ γ γ C = refl
act-axis-∙ γ γ S = refl
act-axis-∙ γ γ W = refl

------------------------------------------------------------------------
-- act-axis is an involution for non-identity V_4 elements.
-- This follows from V_4 being self-inverse: act-axis g (act-axis g x) ≡ x.
------------------------------------------------------------------------

act-axis-involutive : (g : V₄) (x : Axis) → act-axis g (act-axis g x) ≡ x
act-axis-involutive g x =
  -- act-axis g (act-axis g x) ≡ act-axis (g · g) x ≡ act-axis e x ≡ x
  trans (sym (act-axis-∙ g g x))
        (case-g g x)
  where
    -- For each g, g · g = e, so act-axis (g · g) x = act-axis e x = x.
    case-g : (g : V₄) (x : Axis) → act-axis (g V4.· g) x ≡ x
    case-g e _ = refl
    case-g α _ = refl  -- α · α = e
    case-g β _ = refl  -- β · β = e
    case-g γ _ = refl  -- γ · γ = e

------------------------------------------------------------------------
-- The embedding V_4 → S_4.
--
-- Each V_4 element becomes an Axis-permutation; the inverse is itself
-- (since V_4 elements are self-inverse).
------------------------------------------------------------------------

embed : V₄ → Permutation
embed g = record
  { apply = act-axis g
  ; invₐ  = act-axis g
  ; inv-l = act-axis-involutive g
  ; inv-r = act-axis-involutive g
  }

------------------------------------------------------------------------
-- Homomorphism: embed preserves the group operation.
------------------------------------------------------------------------

embed-hom :
  (g h : V₄) → embed (g V4.· h) ≈ (embed g · embed h)
embed-hom g h x = act-axis-∙ g h x

------------------------------------------------------------------------
-- The image of the embedding — the V_4 subgroup of S_4.
------------------------------------------------------------------------

V₄-image : Permutation → Set
V₄-image σ = ∃ λ v → σ ≈ embed v

embed-in-image : (v : V₄) → V₄-image (embed v)
embed-in-image v = v , (λ _ → refl)

------------------------------------------------------------------------
-- Normality: V_4 ⊳ S_4.
--
-- For any σ ∈ S_4 and v ∈ V_4, the conjugate (σ · embed v) · σ⁻¹ is
-- in the V_4 image. This is the load-bearing claim of S8.
--
-- The proof is deferred to Substrate.Groups.V4-Embedding.Normality,
-- which postulates it (and is not compiled with --safe — see that
-- module's header for the decomposition). The core module here stays
-- under --safe; downstream code that needs the normality fact imports
-- from the Normality submodule explicitly, advertising the dependency
-- on an unproven theorem.
--
-- Type signature, as documentation:
--
--   V₄-normal : (σ : Permutation) (v : V₄) → V₄-image ((σ · embed v) · σ ⁻¹)
--
-- Mathematical argument: a V_4 element is a product of disjoint
-- transpositions (e is the empty product). Conjugation by σ sends
-- (ab)(cd) to (σ(a)σ(b))(σ(c)σ(d)), which is another product of
-- disjoint transpositions on 4 elements — hence another V_4 element.
-- The catalog's Python implementation verifies this constructively
-- (s4_structure.py: v4_normal_in_s4, implicit in
-- verify_stab_d_complements_v4).
------------------------------------------------------------------------

------------------------------------------------------------------------
-- TODOs (deferred to follow-on session)
--
-- 1. Replace `postulate act-axis-∙` with the 64-case refl proof.
--    Mechanical. Approximate shape:
--      act-axis-∙ e h x = refl
--      act-axis-∙ α e x = refl              -- α · e = α
--      act-axis-∙ α α D = refl              -- α · α = e
--      ... (40 more cases)
--    The catalog already verifies this constructively in Python
--    (s4_structure.py v4_swap_consistency).
--
-- 2. Replace `postulate V₄-normal` with the constructive normality
--    proof. Approach options:
--      (a) Case-analysis on v and σ (~73 cases — many sub-cases).
--      (b) Define `is-V₄-permutation : Permutation → Set` via a
--          structural predicate ("doubles disjoint transpositions"),
--          prove conjugation preserves this predicate, then convert
--          to V₄-image via enumeration.
--      (c) Use the fact V_4 is the unique non-trivial proper normal
--          subgroup of S_4 — but this requires more group theory.
--    Approach (b) is most likely tractable in Agda and reusable.
--
-- 3. Prove |V_4-image| = 4 (i.e., the embedding is injective). Easy
--    once act-axis is known to be injective per g.
--
-- 4. Construct Stab(D) ⊂ S_4 as the S_3 complement; prove the
--    semidirect product theorem (the next-next slice, S9).
--
-- 5. Construct the bijection TotalSpace ≃ S_4 (S10) once S9 exists.
------------------------------------------------------------------------
