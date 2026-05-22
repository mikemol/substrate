------------------------------------------------------------------------
-- Substrate.ShadowArchitecture.Weight
--
-- Slice 1.3 of the shadow-architecture arc (Shadow B).
--
-- Hamming weight on the seven Fano points and the induced
-- S₃-orbit partition into {weight-1, weight-2, weight-3=★}.
--
-- The substrate's existing `S₃Stabiliser` infrastructure realises S₃
-- as the order-6 stabiliser of the metric-id; its action permutes the
-- three coordinates of F₂³, hence preserves Hamming weight, hence
-- preserves the partition. We don't reprove that here — we work
-- in the partition's "image" view: each point gets a weight (1, 2,
-- or 3) and each orbit is the fibre of the weight function.
--
-- Same partition on lines: a line ℓ has weight = weight of its
-- normal-vector (by the duality of `Substrate.ShadowArchitecture.Duality`).
-- The three line orbits {L₁,L₂,L₃} / {L₄,L₅,L₆} / {L₇} match the
-- point orbits on the nose.
--
-- ★ the weight-3 point e₁₂₃ and the weight-3 line L₇ are the only
-- S₃-fixed members of their respective sets; together they form a
-- non-incident fixed pair (e₁₂₃ ∉ L₇), surfaced in
-- `Substrate.ShadowArchitecture.SelfReference`.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.ShadowArchitecture.Weight where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Eq
  using (_≡_; refl)

open import Substrate.ShadowArchitecture.FanoLabeling
open import Substrate.ShadowArchitecture.Duality using (normal-vector)

------------------------------------------------------------------------
-- 1. Point weight.
--
-- Direct case analysis. The bit-pattern aliases make the values
-- read off as the count of 1s.
------------------------------------------------------------------------

point-weight : Point → ℕ
point-weight p₁₀₀ = 1
point-weight p₀₁₀ = 1
point-weight p₀₀₁ = 1
point-weight p₁₁₀ = 2
point-weight p₁₀₁ = 2
point-weight p₀₁₁ = 2
point-weight p₁₁₁ = 3

------------------------------------------------------------------------
-- 2. Orbit index. Three S₃-orbits on points; we label them 0, 1, 2
-- for weight-1, weight-2, weight-3 respectively.
------------------------------------------------------------------------

Orbit : Set
Orbit = Fin 3

pattern wt-1 = zero
pattern wt-2 = suc zero
pattern wt-3 = suc (suc zero)

point-orbit : Point → Orbit
point-orbit p₁₀₀ = wt-1
point-orbit p₀₁₀ = wt-1
point-orbit p₀₀₁ = wt-1
point-orbit p₁₁₀ = wt-2
point-orbit p₁₀₁ = wt-2
point-orbit p₀₁₁ = wt-2
point-orbit p₁₁₁ = wt-3

------------------------------------------------------------------------
-- 3. Line weight and line orbit (via the normal-vector duality).
--
-- The duality preserves the orbit partition: weight of a line equals
-- weight of its normal-vector, so the three line orbits coincide
-- (as sets, under the bijection) with the three point orbits.
------------------------------------------------------------------------

line-weight : Line → ℕ
line-weight ℓ = point-weight (normal-vector ℓ)

line-orbit : Line → Orbit
line-orbit ℓ = point-orbit (normal-vector ℓ)

------------------------------------------------------------------------
-- 4. Orbit-membership predicates on points (boolean reading of
-- point-orbit).
------------------------------------------------------------------------

-- Predicate form, since substrate prefers Set-valued predicates for
-- structural facts (matches the existing FanoPlane / Cocycles style).

InOrbit-wt-1 : Point → Set
InOrbit-wt-1 p = point-orbit p ≡ wt-1

InOrbit-wt-2 : Point → Set
InOrbit-wt-2 p = point-orbit p ≡ wt-2

InOrbit-wt-3 : Point → Set
InOrbit-wt-3 p = point-orbit p ≡ wt-3

------------------------------------------------------------------------
-- 5. Orbit membership: every point is in its declared orbit.
--
-- These are the 7 + 7 facts that close the partition.
------------------------------------------------------------------------

p₁₀₀-wt-1 : InOrbit-wt-1 p₁₀₀
p₁₀₀-wt-1 = refl
p₀₁₀-wt-1 : InOrbit-wt-1 p₀₁₀
p₀₁₀-wt-1 = refl
p₀₀₁-wt-1 : InOrbit-wt-1 p₀₀₁
p₀₀₁-wt-1 = refl
p₁₁₀-wt-2 : InOrbit-wt-2 p₁₁₀
p₁₁₀-wt-2 = refl
p₁₀₁-wt-2 : InOrbit-wt-2 p₁₀₁
p₁₀₁-wt-2 = refl
p₀₁₁-wt-2 : InOrbit-wt-2 p₀₁₁
p₀₁₁-wt-2 = refl
p₁₁₁-wt-3 : InOrbit-wt-3 p₁₁₁
p₁₁₁-wt-3 = refl

------------------------------------------------------------------------
-- 6. Same partition on lines (via the duality).
--
-- L₁, L₂, L₃ are weight-1 (their normals are the three basis vectors).
-- L₄, L₅, L₆ are weight-2 (their normals are the three weight-2 sums).
-- L₇ is weight-3 (its normal is the unique S₃-fixed vector).
------------------------------------------------------------------------

L₁-orbit : line-orbit L₁ ≡ wt-1
L₁-orbit = refl
L₂-orbit : line-orbit L₂ ≡ wt-1
L₂-orbit = refl
L₃-orbit : line-orbit L₃ ≡ wt-1
L₃-orbit = refl
L₄-orbit : line-orbit L₄ ≡ wt-2
L₄-orbit = refl
L₅-orbit : line-orbit L₅ ≡ wt-2
L₅-orbit = refl
L₆-orbit : line-orbit L₆ ≡ wt-2
L₆-orbit = refl
L₇-orbit : line-orbit L₇ ≡ wt-3
L₇-orbit = refl
