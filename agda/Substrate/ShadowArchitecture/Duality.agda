------------------------------------------------------------------------
-- Substrate.ShadowArchitecture.Duality
--
-- Slice 1.2 of the shadow-architecture arc. The Fano plane is
-- self-dual: each line has a unique normal-vector (a nonzero F₂³
-- vector orthogonal to every point on the line under the standard
-- inner product), and each point determines the line whose normal it
-- is. Together these give a bijection Point ↔ FanoLine.
--
-- This is Shadow A of the arc plan. The two ★ self-references
-- (L₆-normal = 110 = e₁₂, L₇-normal = 111 = e₁₂₃) follow as `refl`
-- facts from the definitions and are surfaced in
-- `Substrate.ShadowArchitecture.SelfReference`.
--
-- Computation table (line → normal):
--   L₁ = {100, 010, 110}  → 001 = e₃     (weight 1)
--   L₂ = {100, 001, 101}  → 010 = e₂     (weight 1)
--   L₃ = {010, 001, 011}  → 100 = e₁     (weight 1)
--   L₄ = {100, 011, 111}  → 011 = e₂₃   (weight 2)
--   L₅ = {010, 101, 111}  → 101 = e₁₃   (weight 2)
--   L₆ = {001, 110, 111}  → 110 = e₁₂   (weight 2) ★
--   L₇ = {110, 101, 011}  → 111 = e₁₂₃  (weight 3) ★
--
-- Each normal is the unique nonzero vector orthogonal to every point
-- on the line (since each line is a 2-dim F₂-subspace of F₂³, the
-- orthogonal complement is 1-dim, hence a single nonzero point).
--
-- Note that the weight-orbit of the line and the weight-orbit of its
-- normal coincide (lines L₁,L₂,L₃ all have weight-1 normals; lines
-- L₄,L₅,L₆ all have weight-2 normals; L₇ has the weight-3 normal).
-- This orbit-preservation is the cleanly-stated face of the duality
-- preserving the S₃-orbit partition (proved in
-- `Substrate.ShadowArchitecture.Weight`).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.ShadowArchitecture.Duality where
open import Substrate.Algebra.F2.FanoPlane using (FanoLine; Point; point-to-vec)

open import Substrate.Foundation.Eq
  using (_≡_; refl)
open import Substrate.Foundation.Product using (_×_; _,_)

open import Substrate.Algebra.F2 using (F₂; 𝟘)
open import Substrate.Algebra.F2.Vector using (Vector)
open import Substrate.Algebra.F2.Vector.DotProduct using (_·F_)

open import Substrate.ShadowArchitecture.FanoLabeling

------------------------------------------------------------------------
-- 1. Normal-vector map.
--
-- The line → point function realising the self-duality. Defined by
-- direct case analysis on the line; correctness (orthogonality with
-- every point on the line) is proven below.
------------------------------------------------------------------------

normal-vector : FanoLine → Point
normal-vector L₁ = p₀₀₁
normal-vector L₂ = p₀₁₀
normal-vector L₃ = p₁₀₀
normal-vector L₄ = p₀₁₁
normal-vector L₅ = p₁₀₁
normal-vector L₆ = p₁₁₀
normal-vector L₇ = p₁₁₁

------------------------------------------------------------------------
-- 2. Inverse: dual-line map.
--
-- The inverse Point → FanoLine of normal-vector. Defined directly; that
-- normal-vector ∘ dual-line ≡ id and dual-line ∘ normal-vector ≡ id
-- are stated as round-trip lemmas below (each closes by case analysis
-- + refl).
------------------------------------------------------------------------

dual-line : Point → FanoLine
dual-line p₀₀₁ = L₁
dual-line p₀₁₀ = L₂
dual-line p₁₀₀ = L₃
dual-line p₀₁₁ = L₄
dual-line p₁₀₁ = L₅
dual-line p₁₁₀ = L₆
dual-line p₁₁₁ = L₇

------------------------------------------------------------------------
-- 3. Round-trip: the two maps are mutually inverse.
--
-- Per [[feedback-expose-generator-not-orbit-applies]] Layer 1 — the
-- 7-constructor Point/FanoLine enumerations collapse via per-type covers
-- that dispatch a heterogeneous refl-tuple. Each refl literal infers
-- its own implicit {x}.
------------------------------------------------------------------------

private
  point-cover :
    ∀ {ℓ} (P : Point → Set ℓ) →
    P p₀₀₁ × P p₀₁₀ × P p₁₀₀ × P p₀₁₁ × P p₁₀₁ × P p₁₁₀ × P p₁₁₁ →
    ∀ p → P p
  point-cover _ (p , _ , _ , _ , _ , _ , _) p₀₀₁ = p
  point-cover _ (_ , p , _ , _ , _ , _ , _) p₀₁₀ = p
  point-cover _ (_ , _ , p , _ , _ , _ , _) p₁₀₀ = p
  point-cover _ (_ , _ , _ , p , _ , _ , _) p₀₁₁ = p
  point-cover _ (_ , _ , _ , _ , p , _ , _) p₁₀₁ = p
  point-cover _ (_ , _ , _ , _ , _ , p , _) p₁₁₀ = p
  point-cover _ (_ , _ , _ , _ , _ , _ , p) p₁₁₁ = p

  line-cover :
    ∀ {ℓ} (P : FanoLine → Set ℓ) →
    P L₁ × P L₂ × P L₃ × P L₄ × P L₅ × P L₆ × P L₇ →
    ∀ l → P l
  line-cover _ (p , _ , _ , _ , _ , _ , _) L₁ = p
  line-cover _ (_ , p , _ , _ , _ , _ , _) L₂ = p
  line-cover _ (_ , _ , p , _ , _ , _ , _) L₃ = p
  line-cover _ (_ , _ , _ , p , _ , _ , _) L₄ = p
  line-cover _ (_ , _ , _ , _ , p , _ , _) L₅ = p
  line-cover _ (_ , _ , _ , _ , _ , p , _) L₆ = p
  line-cover _ (_ , _ , _ , _ , _ , _ , p) L₇ = p

normal-dual-line : ∀ (p : Point) → normal-vector (dual-line p) ≡ p
normal-dual-line =
  point-cover _ (refl , refl , refl , refl , refl , refl , refl)

dual-line-normal : ∀ (ℓ : FanoLine) → dual-line (normal-vector ℓ) ≡ ℓ
dual-line-normal =
  line-cover _ (refl , refl , refl , refl , refl , refl , refl)

------------------------------------------------------------------------
-- 4. Orthogonality: the normal-vector is F₂-orthogonal to every point
-- on its line.
--
-- We unfold `line-points ℓ = (a, b, c)` and state three obligations:
-- normal-vector ℓ · a ≡ 𝟘, … · b ≡ 𝟘, … · c ≡ 𝟘 (under the F₂
-- inner product `_·F_`). Each closes by `refl` because the dot
-- product reduces by computation on concrete F₂³ vectors.
--
-- We package the three obligations as a single record `Orthogonal`
-- and provide one instance per line.
------------------------------------------------------------------------

private
  _⊥_ : Point → Point → Set
  p ⊥ q = (point-to-vec p ·F point-to-vec q) ≡ 𝟘

orthogonal-L₁-a : normal-vector L₁ ⊥ p₁₀₀
orthogonal-L₁-a = refl
orthogonal-L₁-b : normal-vector L₁ ⊥ p₀₁₀
orthogonal-L₁-b = refl
orthogonal-L₁-c : normal-vector L₁ ⊥ p₁₁₀
orthogonal-L₁-c = refl

orthogonal-L₂-a : normal-vector L₂ ⊥ p₁₀₀
orthogonal-L₂-a = refl
orthogonal-L₂-b : normal-vector L₂ ⊥ p₀₀₁
orthogonal-L₂-b = refl
orthogonal-L₂-c : normal-vector L₂ ⊥ p₁₀₁
orthogonal-L₂-c = refl

orthogonal-L₃-a : normal-vector L₃ ⊥ p₀₁₀
orthogonal-L₃-a = refl
orthogonal-L₃-b : normal-vector L₃ ⊥ p₀₀₁
orthogonal-L₃-b = refl
orthogonal-L₃-c : normal-vector L₃ ⊥ p₀₁₁
orthogonal-L₃-c = refl

orthogonal-L₄-a : normal-vector L₄ ⊥ p₁₀₀
orthogonal-L₄-a = refl
orthogonal-L₄-b : normal-vector L₄ ⊥ p₀₁₁
orthogonal-L₄-b = refl
orthogonal-L₄-c : normal-vector L₄ ⊥ p₁₁₁
orthogonal-L₄-c = refl

orthogonal-L₅-a : normal-vector L₅ ⊥ p₀₁₀
orthogonal-L₅-a = refl
orthogonal-L₅-b : normal-vector L₅ ⊥ p₁₀₁
orthogonal-L₅-b = refl
orthogonal-L₅-c : normal-vector L₅ ⊥ p₁₁₁
orthogonal-L₅-c = refl

orthogonal-L₆-a : normal-vector L₆ ⊥ p₀₀₁
orthogonal-L₆-a = refl
orthogonal-L₆-b : normal-vector L₆ ⊥ p₁₁₀
orthogonal-L₆-b = refl
orthogonal-L₆-c : normal-vector L₆ ⊥ p₁₁₁
orthogonal-L₆-c = refl

orthogonal-L₇-a : normal-vector L₇ ⊥ p₁₁₀
orthogonal-L₇-a = refl
orthogonal-L₇-b : normal-vector L₇ ⊥ p₁₀₁
orthogonal-L₇-b = refl
orthogonal-L₇-c : normal-vector L₇ ⊥ p₀₁₁
orthogonal-L₇-c = refl
