------------------------------------------------------------------------
-- Substrate.Groups.SemidirectProduct
--
-- S9 of slice 3: the V_4 ⋊ S_3 ≅ S_4 factorisation theorem.
--
-- Stab(D) ⊂ S_4: permutations fixing the D axis.
-- For each σ ∈ S_4, there exist UNIQUE (v ∈ V_4, s ∈ Stab(D))
-- with σ = v · s. This gives the semidirect product structure
-- (the catalog's M41 v19 K-V4-semidirect-S3-is-primary, theorem-form).
--
-- The argument is non-enumerative:
--   1. V_4 acts transitively on AXES (e→D, α→C, β→S, γ→W from D).
--   2. For σ, define v-for σ = the unique V_4 element with v(D) = σ(D).
--   3. Then s = (embed (v-for σ)) · σ fixes D (so s ∈ Stab(D)).
--   4. σ = (embed (v-for σ)) · s by V_4 being self-inverse.
--   5. Uniqueness: V_4 ∩ Stab(D) = {e}, because no non-identity V_4
--      element fixes D (α: D→C, β: D→S, γ: D→W).
--
-- This module proves all five steps without postulates.
--
-- See: catalog/cocycles.md § CY-5 — Hodge-dual reading;
--      catalog/cocycles.md § Metacircularity — V_4 ⋊ S_3 as primary
--      formal foundation;
--      ../../s4_structure.py:5-21 — the Python reference for the
--      same theorem.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.SemidirectProduct where

open import Level using (0ℓ)
open import Data.Product using (∃; _,_; -,_; proj₁; proj₂)
open import Relation.Binary.PropositionalEquality
  using (_≡_; refl; sym; trans; cong)

open import Substrate.Axes using (Axis; D; C; S; W; act-axis)
open import Substrate.Groups.V4 as V4 using (V₄; e; α; β; γ)
open import Substrate.Groups.S4 as S4
  using (Permutation; _≈_; _·_; _⁻¹; ε; ≈-refl)
  renaming (apply to applyₛ)
open import Substrate.Groups.V4-Embedding
  using (embed; act-axis-∙; act-axis-involutive; V₄-image; embed-in-image)

------------------------------------------------------------------------
-- Stab(axis) — the predicate: σ fixes a given axis.
--
-- The cocycle USES D as anchor but does not COMMIT to D; the same
-- predicate exists for each non-D axis as the corresponding gauge-
-- equivalent. Stab-C, Stab-S, Stab-W are added as siblings of
-- Stab-D to close the partial-coset finding the detector surfaced
-- (per [[feedback-use-vs-commit]]).
------------------------------------------------------------------------

Stab-D : Permutation → Set
Stab-D σ = applyₛ σ D ≡ D

Stab-C : Permutation → Set
Stab-C σ = applyₛ σ C ≡ C

Stab-S : Permutation → Set
Stab-S σ = applyₛ σ S ≡ S

Stab-W : Permutation → Set
Stab-W σ = applyₛ σ W ≡ W

------------------------------------------------------------------------
-- v-of-axis: given an axis x, the unique V_4 element sending D to x.
--
-- This works because V_4 acts simply transitively on AXES (orbit of
-- D under V_4 is all four axes; stabilizer of D is trivial).
------------------------------------------------------------------------

v-of-axis : Axis → V₄
v-of-axis D = e
v-of-axis C = α
v-of-axis S = β
v-of-axis W = γ

-- The defining property: v-of-axis x acts on D as x.
v-of-axis-sends-D : (x : Axis) → act-axis (v-of-axis x) D ≡ x
v-of-axis-sends-D D = refl
v-of-axis-sends-D C = refl
v-of-axis-sends-D S = refl
v-of-axis-sends-D W = refl

-- Uniqueness: v-of-axis is the ONLY V_4 element with this property.
-- Used in the semidirect product uniqueness proof.
v-of-axis-unique :
  (v : V₄) (x : Axis) → act-axis v D ≡ x → v ≡ v-of-axis x
v-of-axis-unique e D refl = refl
v-of-axis-unique α C refl = refl
v-of-axis-unique β S refl = refl
v-of-axis-unique γ W refl = refl
-- The remaining cases are vacuous: act-axis v D evaluates to a
-- specific axis per v, so the equation rules out incompatible (v, x).

------------------------------------------------------------------------
-- v-for σ: the V_4 element σ agrees with on D.
------------------------------------------------------------------------

v-for : Permutation → V₄
v-for σ = v-of-axis (applyₛ σ D)

-- Defining property of v-for: it sends D to σ(D).
v-for-sends-D :
  (σ : Permutation) → act-axis (v-for σ) D ≡ applyₛ σ D
v-for-sends-D σ = v-of-axis-sends-D (applyₛ σ D)

------------------------------------------------------------------------
-- The Stab(D) residue: s-for σ = (embed (v-for σ)) · σ.
--
-- This fixes D, because:
--   apply (s-for σ) D = act-axis (v-for σ) (apply σ D)    (composition)
--                     = act-axis (v-for σ) (act-axis (v-for σ) D)
--                       (since v-for sends D to apply σ D, sym)
--                     = D                                  (involutive)
------------------------------------------------------------------------

s-for : Permutation → Permutation
s-for σ = embed (v-for σ) · σ

s-for-fixes-D : (σ : Permutation) → Stab-D (s-for σ)
s-for-fixes-D σ =
  -- apply (s-for σ) D
  --   = apply (embed (v-for σ) · σ) D
  --   = act-axis (v-for σ) (apply σ D)
  --   = act-axis (v-for σ) (act-axis (v-for σ) D)   (sym (v-for-sends-D))
  --   = D                                            (act-axis-involutive)
  trans (cong (act-axis (v-for σ)) (sym (v-for-sends-D σ)))
        (act-axis-involutive (v-for σ) D)

------------------------------------------------------------------------
-- The factorisation: σ ≈ embed (v-for σ) · s-for σ.
--
-- Note: s-for σ ≡ embed (v-for σ) · σ, so
--   embed (v-for σ) · s-for σ
--   = embed (v-for σ) · (embed (v-for σ) · σ)
--   = (embed (v-for σ) · embed (v-for σ)) · σ        (assoc, sym)
--   = embed (v-for σ V4.· v-for σ) · σ              (embed homomorphism)
--   = embed e · σ                                    (V_4 self-inverse)
--   = ε · σ ≈ σ
--
-- We prove this pointwise via the act-axis structure.
------------------------------------------------------------------------

factorisation :
  (σ : Permutation) →
  σ ≈ (embed (v-for σ) · s-for σ)
factorisation σ x =
  -- apply σ x
  --   = act-axis (v-for σ) (act-axis (v-for σ) (apply σ x))  (involutive sym)
  --   = apply (embed (v-for σ) · (embed (v-for σ) · σ)) x   (composition)
  --   = apply (embed (v-for σ) · s-for σ) x                  (def of s-for)
  sym (act-axis-involutive (v-for σ) (applyₛ σ x))

------------------------------------------------------------------------
-- V_4 ∩ Stab(D) = {e}.
--
-- No non-identity V_4 element fixes D:
--   α D = C ≠ D, β D = S ≠ D, γ D = W ≠ D.
------------------------------------------------------------------------

V₄-cap-Stab-D-trivial :
  (v : V₄) → Stab-D (embed v) → v ≡ e
V₄-cap-Stab-D-trivial e _   = refl
V₄-cap-Stab-D-trivial α ()
V₄-cap-Stab-D-trivial β ()
V₄-cap-Stab-D-trivial γ ()

V₄-cap-Stab-C-trivial :
  (v : V₄) → Stab-C (embed v) → v ≡ e
V₄-cap-Stab-C-trivial e _   = refl
V₄-cap-Stab-C-trivial α ()
V₄-cap-Stab-C-trivial β ()
V₄-cap-Stab-C-trivial γ ()

V₄-cap-Stab-S-trivial :
  (v : V₄) → Stab-S (embed v) → v ≡ e
V₄-cap-Stab-S-trivial e _   = refl
V₄-cap-Stab-S-trivial α ()
V₄-cap-Stab-S-trivial β ()
V₄-cap-Stab-S-trivial γ ()

V₄-cap-Stab-W-trivial :
  (v : V₄) → Stab-W (embed v) → v ≡ e
V₄-cap-Stab-W-trivial e _   = refl
V₄-cap-Stab-W-trivial α ()
V₄-cap-Stab-W-trivial β ()
V₄-cap-Stab-W-trivial γ ()

------------------------------------------------------------------------
-- Uniqueness of factorisation.
--
-- If σ ≈ embed v₁ · s₁ ≈ embed v₂ · s₂ with v₁, v₂ ∈ V_4 and
-- s₁, s₂ ∈ Stab(D), then v₁ ≡ v₂ (and consequently s₁ ≈ s₂).
--
-- Proof: apply both factorisations to D.
--   apply (embed v₁ · s₁) D = act-axis v₁ (apply s₁ D) = act-axis v₁ D
--                                                       (s₁ fixes D)
--   Similarly apply (embed v₂ · s₂) D = act-axis v₂ D.
-- So act-axis v₁ D ≡ act-axis v₂ D. By v-of-axis-unique applied to
-- both sides equaling the same axis, v₁ ≡ v-of-axis (act-axis v₁ D)
-- and v₂ ≡ v-of-axis (act-axis v₂ D); hence v₁ ≡ v₂.
------------------------------------------------------------------------

factorisation-unique-V₄ :
  (σ : Permutation) (v₁ v₂ : V₄) (s₁ s₂ : Permutation) →
  Stab-D s₁ → Stab-D s₂ →
  σ ≈ embed v₁ · s₁ → σ ≈ embed v₂ · s₂ →
  v₁ ≡ v₂
factorisation-unique-V₄ σ v₁ v₂ s₁ s₂ s₁-fix s₂-fix eq₁ eq₂ =
  -- Step 1: apply σ D = act-axis v₁ (apply s₁ D) = act-axis v₁ D
  let
    σD₁ : applyₛ σ D ≡ act-axis v₁ D
    σD₁ = trans (eq₁ D) (cong (act-axis v₁) s₁-fix)
    σD₂ : applyₛ σ D ≡ act-axis v₂ D
    σD₂ = trans (eq₂ D) (cong (act-axis v₂) s₂-fix)
    -- v₁ ≡ v-of-axis (apply σ D) (by uniqueness of v-of-axis)
    v₁-eq : v₁ ≡ v-of-axis (applyₛ σ D)
    v₁-eq = v-of-axis-unique v₁ (applyₛ σ D) (sym σD₁)
    v₂-eq : v₂ ≡ v-of-axis (applyₛ σ D)
    v₂-eq = v-of-axis-unique v₂ (applyₛ σ D) (sym σD₂)
  in trans v₁-eq (sym v₂-eq)

------------------------------------------------------------------------
-- The semidirect product theorem (S9 main result).
--
-- Existence + uniqueness packaged: every σ ∈ S_4 has a unique
-- factorisation σ = (embed v) · s with v ∈ V_4 and s ∈ Stab(D).
------------------------------------------------------------------------

record SemidirectFactorisation (σ : Permutation) : Set where
  field
    v        : V₄
    s        : Permutation
    s-stab   : Stab-D s
    σ-eq     : σ ≈ embed v · s

semidirect-factorisation : (σ : Permutation) → SemidirectFactorisation σ
semidirect-factorisation σ = record
  { v      = v-for σ
  ; s      = s-for σ
  ; s-stab = s-for-fixes-D σ
  ; σ-eq   = factorisation σ
  }

------------------------------------------------------------------------
-- Notes for follow-on work
--
-- 1. To bundle Stab(D) as a Subgroup record: would need to show
--    closure under composition, identity ∈ Stab(D), and inverse
--    closure. Each follows from the definition (composition of
--    D-fixing permutations fixes D; etc.). Deferred — S9's
--    factorisation theorem is the load-bearing claim.
--
-- 2. For S10 (TotalSpace ≃ S_4) the construction will use:
--      total-to-s4 (ok , v) = embed v · orbit-key-to-stab-d ok
--      s4-to-total σ        = (stab-d-to-orbit-key (s-for σ) , v-for σ)
--    The orbit-key ↔ Stab(D) bijection is the case-analytic part of
--    S10 — see Substrate.Cocycles.V4Signature.S4Iso.
------------------------------------------------------------------------
