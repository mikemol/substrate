------------------------------------------------------------------------
-- Substrate.Logic.Evidence.ElAtlas.OrbitCloudRung3Wedge  (Ⓟ.3″ — the parity-line wedge)
--
-- The POSITIVE resolution of Ⓟ.3′'s flag. There I noted that the doc identifies
-- "the static antisymmetric-form witness kernel" with "the dynamic V₂-reflection's
-- −1 eigenline" as ONE line, but they differ. Recursing into the common structure
-- (re-expressing the reflection in CenterWitness's cycle coordinates — Ⓟ.3′ used
-- the probe's pseudo-inverse coords, a different basis) shows it is not a basis
-- artifact: there are TWO DISTINCT parity-distinguished lines — a WEDGE the doc
-- collapsed — and they are related by (I − T).
--
-- In CenterWitness coordinates the V₂ reflection is
--   T(a,b,c) = (b+c, a−c, c)        [T² = I, the idempotent species]
-- and:
--   * STATIC witness  w = (1,−1,1) = ker B₃ (Ξ★.1) — the antisymmetric-form radical.
--   * DYNAMIC axis    d = (1,−1,0) = T's −1 eigenline (T·d = −d).
--   * RELATION        d = (I − T)·w   (T·w = (0,0,1) = w − d): the dynamic axis is
--     exactly the DEVIATION of the static witness under the reflection. They are
--     distinct lines (the wedge), overlapping but not equal.
--   * CONTRAST        B₃·w = 0 (static = the kernel) but B₃·d ≠ 0 (dynamic is
--     representable) — the two facets sit oppositely wrt the static form.
--
-- So "static kernel" and "dynamic reflection axis" are two retained facets of the
-- rung-3 parity, glued by (I−T) — not one line (doc), not a coordinate artifact.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Logic.Evidence.ElAtlas.OrbitCloudRung3Wedge where

open import Substrate.Foundation.Vec using (Vec; _∷_; [])
open import Substrate.Foundation.Eq using (_≡_; refl; cong)
open import Substrate.Foundation.Empty using (⊥)
open import Substrate.Algebra.Z using (ℤ; +_; -ℤ_)
open import Substrate.Algebra.Z.Arithmetic using (_+ℤ_)
open import Substrate.Logic.Evidence.ElAtlas.CenterWitness using (apply-B₃; w; 𝟎)

V3 : Set
V3 = Vec ℤ 3

-- pointwise subtraction (for the (I−T) relation).
vsub : V3 → V3 → V3
vsub (a ∷ b ∷ c ∷ []) (x ∷ y ∷ z ∷ []) = (a +ℤ (-ℤ x)) ∷ (b +ℤ (-ℤ y)) ∷ (c +ℤ (-ℤ z)) ∷ []

-- The V₂ = (0 1)(2 3) reflection in CenterWitness cycle coordinates.
act-T : V3 → V3
act-T (a ∷ b ∷ c ∷ []) = (b +ℤ c) ∷ (a +ℤ (-ℤ c)) ∷ c ∷ []

-- the dynamic reflection axis (T's −1 eigenline). (w, the static witness, is
-- imported from CenterWitness = ker B₃.)
d : V3
d = (+ 1) ∷ (-ℤ (+ 1)) ∷ (+ 0) ∷ []

------------------------------------------------------------------------
-- T² = I (the idempotent species), on the standard basis.
------------------------------------------------------------------------

T²-e₁ : act-T (act-T ((+ 1) ∷ (+ 0) ∷ (+ 0) ∷ [])) ≡ ((+ 1) ∷ (+ 0) ∷ (+ 0) ∷ [])
T²-e₁ = refl
T²-e₂ : act-T (act-T ((+ 0) ∷ (+ 1) ∷ (+ 0) ∷ [])) ≡ ((+ 0) ∷ (+ 1) ∷ (+ 0) ∷ [])
T²-e₂ = refl
T²-e₃ : act-T (act-T ((+ 0) ∷ (+ 0) ∷ (+ 1) ∷ [])) ≡ ((+ 0) ∷ (+ 0) ∷ (+ 1) ∷ [])
T²-e₃ = refl

------------------------------------------------------------------------
-- The dynamic axis is T's −1 eigenline.
------------------------------------------------------------------------

dynamic-neg : act-T d ≡ ((-ℤ (+ 1)) ∷ (+ 1) ∷ (+ 0) ∷ [])      -- T·d = −d
dynamic-neg = refl

------------------------------------------------------------------------
-- THE WEDGE RELATION: d = (I − T)·w. The dynamic axis is the deviation of the
-- static witness under the reflection.
------------------------------------------------------------------------

wedge-relation : vsub w (act-T w) ≡ d
wedge-relation = refl

------------------------------------------------------------------------
-- The two lines sit OPPOSITELY under the static form B₃: w is its kernel,
-- d is representable (not the kernel) — and the lines are distinct (the wedge).
------------------------------------------------------------------------

static-in-kernel : apply-B₃ w ≡ 𝟎                              -- w = ker B₃
static-in-kernel = refl

dynamic-not-kernel : apply-B₃ d ≡ 𝟎 → ⊥                        -- B₃·d = (−2,−2,0) ≠ 0
dynamic-not-kernel ()

v₃ : V3 → ℤ
v₃ (_ ∷ _ ∷ z ∷ []) = z

w≢d : w ≡ d → ⊥                                                -- two distinct parity lines
w≢d eq with cong v₃ eq                                         -- w₃ = +1, d₃ = +0
... | ()
