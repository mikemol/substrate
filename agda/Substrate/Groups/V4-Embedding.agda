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
-- Architecture (per [[feedback-v4-typeclass-architecture]]): act-axis
-- itself is now defined STRUCTURALLY in Substrate.Axes as
-- `axis-of-v (v V4.· v-of-axis x)` — the V₄-torsor structure IS the
-- foundation. Consequently `act-axis-as-V₄-mult` is a definitional
-- identity (1-line refl), and act-axis-∙ / act-axis-involutive are
-- short algebraic derivations through V4-Generic's group axioms.
-- No (V₄ × Axis) enumeration anywhere.
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

-- Axis + bijection (v-of-axis / axis-of-v) + round-trips + act-axis
-- now live in Substrate.Axes. Re-exported here so downstream code
-- importing this module keeps working unchanged.
open import Substrate.Axes public
  using (Axis; D; C; S; W; act-axis;
         v-of-axis; axis-of-v;
         axis-of-v-v-of-axis; v-of-axis-axis-of-v)
open import Substrate.Groups.V4 as V4 using (V₄; e; α; β; γ; V₄-Group)
open import Substrate.Groups.S4 as S4
  using (Permutation; _≈_; _·_; _⁻¹; ε; S₄-Group)
  renaming (apply to applyₛ; invₐ to invₐₛ)

------------------------------------------------------------------------
-- act-axis IS V₄ multiplication on Axis — DEFINITIONAL identity.
--
--   act-axis v x ≡ axis-of-v (v V4.· v-of-axis x)
--
-- True by `refl`: act-axis is *defined* this way in Substrate.Axes.
-- Retained as a named lemma for downstream modules that compose
-- through it explicitly (they get a no-op proof obligation).
------------------------------------------------------------------------

act-axis-as-V₄-mult :
  (v : V₄) (x : Axis) →
  act-axis v x ≡ axis-of-v (v V4.· v-of-axis x)
act-axis-as-V₄-mult _ _ = refl

------------------------------------------------------------------------
-- act-axis as a V₄-action.
--
-- act-id: act-axis e x ≡ x.
--   Under the structural definition, this is no longer definitional
--   for variable x (V₄'s ε-left needs to fire). Proof: chain
--   V4.ε-left + axis-of-v-v-of-axis through cong axis-of-v.
--
-- act-∙: act-axis (g · h) x ≡ act-axis g (act-axis h x).
--   Algebraic chain through V4.·-assoc + v-of-axis-axis-of-v
--   round-trip. No (V₄ × V₄ × Axis) enumeration.
------------------------------------------------------------------------

act-axis-id : (x : Axis) → act-axis e x ≡ x
act-axis-id x =
  trans (cong axis-of-v (V4.ε-left (v-of-axis x)))
        (axis-of-v-v-of-axis x)

act-axis-∙ :
  (g h : V₄) (x : Axis) →
  act-axis (g V4.· h) x ≡ act-axis g (act-axis h x)
act-axis-∙ g h x =
  trans (cong axis-of-v (V4.·-assoc g h (v-of-axis x)))
        (cong (λ w → axis-of-v (g V4.· w))
              (sym (v-of-axis-axis-of-v (h V4.· v-of-axis x))))

------------------------------------------------------------------------
-- act-axis involutivity — derived from act-axis-∙ + V_4 self-inverse.
--
--   act-axis g (act-axis g x)
--     ≡ act-axis (g · g) x   [sym act-axis-∙]
--     ≡ act-axis ε x         [V4.inv-left g, since inv = id on V₄]
--     ≡ x                    [act-axis-id, after V4.ε reduces to e]
--
-- Under the structural act-axis, the final step is no longer
-- definitional and routes through act-axis-id.
------------------------------------------------------------------------

act-axis-involutive : (g : V₄) (x : Axis) → act-axis g (act-axis g x) ≡ x
act-axis-involutive g x =
  trans (sym (act-axis-∙ g g x))
        (trans (cong (λ v → act-axis v x) (V4.inv-left g))
               (act-axis-id x))

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

-- Every V₄-image is self-inverse (since every V₄ element is). One-line
-- corollary of act-axis-involutive; lifted here from V4-Normality so
-- S4-Iso can consume it without pulling in the entire Normality proof.
embed-self-inverse : (v : V₄) → (embed v · embed v) ≈ ε
embed-self-inverse v x = act-axis-involutive v x

------------------------------------------------------------------------
-- Note: The previous Is-V₄ instance for Axis (typeclass-style index
-- into Bool × Bool via the F₂² bijection) has been retired alongside
-- V4-Index and V4-Generic. The Axis ↔ V₄ correspondence now lives
-- directly above via `v-of-axis`/`axis-of-v` (which are the relevant
-- Axis-side names) plus V₄'s 4-ctor data type. No downstream code
-- consumed Axis-is-V₄, so its deletion is safe.
------------------------------------------------------------------------

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
-- 1. Replace `postulate V₄-normal` with the constructive normality
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
-- 2. Prove |V_4-image| = 4 (i.e., the embedding is injective). Easy
--    once act-axis is known to be injective per g.
--
-- 3. Construct Stab(D) ⊂ S_4 as the S_3 complement; prove the
--    semidirect product theorem (the next-next slice, S9).
--
-- 4. Construct the bijection TotalSpace ≃ S_4 (S10) once S9 exists.
------------------------------------------------------------------------
