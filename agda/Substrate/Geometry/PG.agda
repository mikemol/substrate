------------------------------------------------------------------------
-- Substrate.Geometry.PG
--
-- M-11 full machinery sub-slice 2. The projective space PG(n, F₂) =
-- (F₂^(n+1) \ {𝟎}) / F₂* as a parametric type.
--
-- Since F₂* = {𝟙} (the multiplicative group of F₂ has just one
-- element), the quotient is trivial:
--
--   PG(n, F₂) = F₂^(n+1) \ {𝟎}
--   |PG(n, F₂)| = 2^(n+1) − 1
--
-- Specific instances in the codebase:
--   PG(0, F₂) = F₂ \ {𝟎} = {𝟙}                  (1 point)
--   PG(1, F₂) = F₂² \ {𝟎}                       (3 points = projective line)
--   PG(2, F₂) = F₂³ \ {𝟎}                       (7 points = Fano plane, M-9)
--   PG(3, F₂) = F₂⁴ \ {𝟎}                       (15 points)
--
-- PG(n, F₂) is the "chirality-choice phase space" at dimension n+1
-- in the chirality-rotation conjecture: each 1-dim subspace ⟨v⟩
-- corresponds to a chirality axis, and v ↦ ⟨v⟩ is a bijection (in
-- F₂) since the quotient is trivial.
--
-- The GL(n+1, F₂) action permutes points via the "preserves-nonzero"
-- property of invertible linear maps. The cardinality of GL(n+1, F₂)
-- grows as 2^(n+1 choose 2) · ∏ (2^(n+1) − 2^i); at n=2 this is 168.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Geometry.PG where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Product using (Σ; _,_; proj₁; proj₂)
open import Substrate.Foundation.Eq
  using (_≡_)
open import Substrate.Foundation.Negation using (¬_)

open import Substrate.Algebra.F2
open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.Linear

------------------------------------------------------------------------
-- The projective space type.
--
-- PG n = {v ∈ F₂^(n+1) : v ≠ 𝟎ⱽ}. Cardinality = 2^(n+1) − 1.
--
-- Note: in F₂ specifically, the projective equivalence (v ~ λv for
-- λ ∈ F₂*) is trivial (only λ = 𝟙 works), so PG n is literally the
-- nonzero subset of F₂^(n+1).
------------------------------------------------------------------------

PG : ℕ → Set
PG n = Σ (Vector (Data.Nat.suc n)) (λ v → ¬ (v ≡ 𝟎ⱽ))

------------------------------------------------------------------------
-- Projection: PG point → underlying F₂-vector.
------------------------------------------------------------------------

PG-coords : ∀ {n} → PG n → Vector (Data.Nat.suc n)
PG-coords = proj₁

PG-nonzero : ∀ {n} (p : PG n) → ¬ (PG-coords p ≡ 𝟎ⱽ)
PG-nonzero = proj₂

------------------------------------------------------------------------
-- Action of an F₂-linear map on PG.
--
-- An F₂-linear `τ : Linear (suc n) (suc n)` acts on `PG n` provided
-- it preserves nonzeroness. This is the "preserves-nonzero" property:
-- if v ≠ 𝟎ⱽ then `apply τ v ≠ 𝟎ⱽ`.
--
-- For invertible (GL) elements, preserves-nonzero is automatic
-- (an invertible map sends nonzero to nonzero). For general linear
-- maps, this hypothesis must be supplied explicitly.
--
-- The action permutes points of PG when τ is invertible — this is
-- the GL(n+1, F₂) action on PG(n, F₂). Demonstrated concretely at
-- n=2 by `Substrate.Geometry.HodgeDim3.Gl3`'s σ and τ generators.
------------------------------------------------------------------------

Preserves-Nonzero :
  ∀ {n} → Linear (Data.Nat.suc n) (Data.Nat.suc n) → Set
Preserves-Nonzero {n} L =
  ∀ (v : Vector (Data.Nat.suc n)) → ¬ (v ≡ 𝟎ⱽ) → ¬ (apply L v ≡ 𝟎ⱽ)

PG-act :
  ∀ {n} (L : Linear (Data.Nat.suc n) (Data.Nat.suc n)) →
  Preserves-Nonzero L →
  PG n → PG n
PG-act L pres (v , v≢𝟎) = (apply L v , pres v v≢𝟎)

------------------------------------------------------------------------
-- Connection to existing types (documentation).
--
-- * Fano (M-9): `Substrate.Geometry.Fano.Point = Fin 7` parametrises
--   the 7 elements of PG(2, F₂) via `point-coords : Fin 7 → Vector 3`.
--   A formal `Bijection Point (PG 2)` requires a "decoder" from
--   Vector 3 ≠ 𝟎ⱽ to Fin 7 (syndrome lookup); deferred.
--
-- * M-11.fano: chirality at Fano point p ↔ chirality at PG-coords p ∈ PG 2.
--   The parametric chirality-projection from M-11.fano lifts to any
--   PG element directly.
--
-- * M-11.dim3 / M-11.fano: at n=2, GL(3, F₂) acts transitively on PG 2
--   (= the 7 Fano points). Gl3.agda provides σ and τ generators;
--   transitivity of the orbit is concrete via the combined cycle
--   structures (3+3+1 from σ, 2+2+1+1+1 from τ).
------------------------------------------------------------------------
