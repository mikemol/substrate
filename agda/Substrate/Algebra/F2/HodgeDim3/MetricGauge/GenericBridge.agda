------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim3.MetricGauge.GenericBridge
--
-- Bridges the dim-3 specific SymBilinForm-3 (Vector 6 packing) to the
-- generic SymBilinForm at n=3 (Fin 3 → Fin 3 → F₂ + symmetry).
--
-- After this slice:
--
--   * `SymBilinForm-3-to-generic M : BilinForm 3` — convert the
--     Vector 6 packing into a 3×3 matrix function.
--   * `is-symmetric-bridged-3` — the bridged matrix is automatically
--     symmetric.
--   * `bilinear-form-of-bridge-3` — the dim-3 specific
--     bilinear-form-of (with its left-associated 9-term expansion)
--     equals the generic bilinear-form-of (with its right-associated
--     double sum-F₂) modulo associativity / +-identityʳ cleanups.
--   * `metric-id-3-eq-bridged` — the dim-3 metric-id bridges to the
--     generic metric-id pointwise.
--
-- Enables downstream demotions:
--
--   * `·F-eq-metric-id-bilin` in HodgeDim3.MetricGauge.HodgeRecast
--     becomes a corollary of generic recast + this bridge at metric-id.
--
--   * Eventually, StabiliserClosure's 3-cycle proof becomes a
--     corollary of FixedPoint-of-compose + congruence-compose-pointwise
--     + a congruence-act bridge (separate follow-on slice).
--
-- Per `feedback_categorical_name_first`: this is the bridge between
-- the dim-3-specific representation (Vector 6 packing — the
-- substrate's original encoding) and the n-parametric representation
-- governing the categorical fixed-point.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim3.MetricGauge.GenericBridge where

open import Data.Fin using (Fin; zero; suc)
open import Data.Vec using ([]; _∷_)
open import Relation.Binary.PropositionalEquality
  using (_≡_; refl; sym; trans; cong; cong₂)

open import Substrate.Algebra.F2
open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge
  using (SymBilinForm-3; bilinear-form-of; metric-id;
         entry-a; entry-b; entry-c; entry-d; entry-e; entry-f)

-- Generic infrastructure.
open import Substrate.Algebra.F2.SymBilinForm
  using () renaming (BilinForm to BilinForm-generic;
                     IsSymmetric to IsSymmetric-generic;
                     bilinear-form-of to bilinear-form-of-generic;
                     metric-id to metric-id-generic)

------------------------------------------------------------------------
-- N-1: SymBilinForm-3-to-generic — convert Vector 6 packing into
-- a Fin 3 → Fin 3 → F₂ matrix function.
--
-- The Vector 6 packing puts diagonal entries (a, b, c) at positions
-- 0, 1, 2 and off-diagonal entries (d = M(0,1), e = M(0,2),
-- f = M(1,2)) at positions 3, 4, 5. By symmetry the (i, j) lookup
-- with i > j returns the corresponding upper-triangular entry.
------------------------------------------------------------------------

SymBilinForm-3-to-generic : SymBilinForm-3 → BilinForm-generic 3
SymBilinForm-3-to-generic M zero             zero             = entry-a M
SymBilinForm-3-to-generic M zero             (suc zero)       = entry-d M
SymBilinForm-3-to-generic M zero             (suc (suc zero)) = entry-e M
SymBilinForm-3-to-generic M (suc zero)       zero             = entry-d M
SymBilinForm-3-to-generic M (suc zero)       (suc zero)       = entry-b M
SymBilinForm-3-to-generic M (suc zero)       (suc (suc zero)) = entry-f M
SymBilinForm-3-to-generic M (suc (suc zero)) zero             = entry-e M
SymBilinForm-3-to-generic M (suc (suc zero)) (suc zero)       = entry-f M
SymBilinForm-3-to-generic M (suc (suc zero)) (suc (suc zero)) = entry-c M

------------------------------------------------------------------------
-- N-2: Symmetry of the bridged matrix.
--
-- The Vector 6 packing only carries upper-triangular data; the
-- bridge fills in lower-triangular by symmetry. Each pair (i, j)
-- and (j, i) returns the same entry by construction.
------------------------------------------------------------------------

is-symmetric-bridged-3 : (M : SymBilinForm-3) →
                         IsSymmetric-generic (SymBilinForm-3-to-generic M)
is-symmetric-bridged-3 M zero             zero             = refl
is-symmetric-bridged-3 M zero             (suc zero)       = refl
is-symmetric-bridged-3 M zero             (suc (suc zero)) = refl
is-symmetric-bridged-3 M (suc zero)       zero             = refl
is-symmetric-bridged-3 M (suc zero)       (suc zero)       = refl
is-symmetric-bridged-3 M (suc zero)       (suc (suc zero)) = refl
is-symmetric-bridged-3 M (suc (suc zero)) zero             = refl
is-symmetric-bridged-3 M (suc (suc zero)) (suc zero)       = refl
is-symmetric-bridged-3 M (suc (suc zero)) (suc (suc zero)) = refl

------------------------------------------------------------------------
-- N-3: bilinear-form-of-bridge-3 — the two definitions agree.
--
-- Dim-3 specific bilinear-form-of M v w (with M = (a, b, c, d, e, f),
-- v = (v₀, v₁, v₂), w = (w₀, w₁, w₂)) expands as:
--
--   ((v₀ · ((a·w₀ + d·w₁) + e·w₂) + v₁ · ((d·w₀ + b·w₁) + f·w₂))
--     + v₂ · ((e·w₀ + f·w₁) + c·w₂))
--
-- left-associated (since `_+_` is infixl).
--
-- Generic bilinear-form-of (SymBilinForm-3-to-generic M) v w expands
-- as a double sum-F₂; with bridged M-entries substituted, each row
-- is right-associated with a trailing 𝟘:
--
--   v₀ · (a·w₀ + (d·w₁ + (e·w₂ + 𝟘))) +
--   (v₁ · (d·w₀ + (b·w₁ + (f·w₂ + 𝟘))) +
--   (v₂ · (e·w₀ + (f·w₁ + (c·w₂ + 𝟘))) + 𝟘))
--
-- Bridge: each row's inner expression and the outer expression
-- need to be left-associated + trailing-𝟘-cleaned. Per row: 2 steps
-- (kill 𝟘 + reassoc). Outer: 2 steps (kill 𝟘 + reassoc). 4 rows
-- worth of conversions.
------------------------------------------------------------------------

bilinear-form-of-bridge-3 :
  (M : SymBilinForm-3) (v w : Vector 3) →
  bilinear-form-of M v w
    ≡ bilinear-form-of-generic (SymBilinForm-3-to-generic M) v w
bilinear-form-of-bridge-3
    (a ∷ b ∷ c ∷ d ∷ e ∷ f ∷ [])
    (v₀ ∷ v₁ ∷ v₂ ∷ [])
    (w₀ ∷ w₁ ∷ w₂ ∷ []) =
  -- Both sides have 3 row-contributions. Per-row bridge: from the
  -- LHS left-assoc form to the RHS right-assoc-with-trailing-𝟘 form.
  -- Then outer bridge.
  trans LHS→canonical (sym RHS←canonical)
  where
    -- Canonical row form (right-assoc with trailing 𝟘 — matches RHS).
    row-canonical : (x y z : F₂) → F₂
    row-canonical x y z = x + (y + (z + 𝟘))

    -- Per-row bridge LHS-row→canonical.
    -- LHS row: (x + y) + z; canonical: x + (y + (z + 𝟘)).
    row-LHS→canonical :
      (x y z : F₂) → (x + y) + z ≡ x + (y + (z + 𝟘))
    row-LHS→canonical x y z =
      trans (+-assoc x y z)
            (cong (x +_) (cong (y +_) (sym (+-identityʳ z))))

    -- Each row LHS shape: v · ((p + q) + r). Bring to v · canonical
    -- via cong (v ·_) + row-LHS→canonical.
    row-bridge :
      (v p q r : F₂) → v · ((p + q) + r) ≡ v · row-canonical p q r
    row-bridge v p q r = cong (v ·_) (row-LHS→canonical p q r)

    -- LHS overall (left-assoc): ((row0 + row1) + row2)
    -- → ((row0' + row1') + row2') where row-i' = row-bridge applied
    LHS→canonical :
      (v₀ · ((a · w₀ + d · w₁) + e · w₂)
        + v₁ · ((d · w₀ + b · w₁) + f · w₂))
        + v₂ · ((e · w₀ + f · w₁) + c · w₂)
      ≡
      (v₀ · row-canonical (a · w₀) (d · w₁) (e · w₂)
        + v₁ · row-canonical (d · w₀) (b · w₁) (f · w₂))
        + v₂ · row-canonical (e · w₀) (f · w₁) (c · w₂)
    LHS→canonical =
      cong₂ _+_
        (cong₂ _+_ (row-bridge v₀ (a · w₀) (d · w₁) (e · w₂))
                   (row-bridge v₁ (d · w₀) (b · w₁) (f · w₂)))
        (row-bridge v₂ (e · w₀) (f · w₁) (c · w₂))

    -- RHS bridge: outer is right-assoc with trailing 𝟘:
    --   row0 + (row1 + (row2 + 𝟘))
    -- Convert to canonical LHS shape:
    --   (row0 + row1) + row2
    -- Row abbreviations to keep the proof readable.
    row₀ row₁ row₂ : F₂
    row₀ = v₀ · row-canonical (a · w₀) (d · w₁) (e · w₂)
    row₁ = v₁ · row-canonical (d · w₀) (b · w₁) (f · w₂)
    row₂ = v₂ · row-canonical (e · w₀) (f · w₁) (c · w₂)

    RHS←canonical :
      row₀ + (row₁ + (row₂ + 𝟘)) ≡ (row₀ + row₁) + row₂
    RHS←canonical =
      trans (cong (row₀ +_) (cong (row₁ +_) (+-identityʳ row₂)))
            (sym (+-assoc row₀ row₁ row₂))

------------------------------------------------------------------------
-- N-4: metric-id bridge — the dim-3 metric-id maps to the generic
-- metric-id pointwise.
--
-- Both are the diagonal identity at n=3; the bridged matrix from
-- the Vector 6 packing (a=b=c=𝟙, d=e=f=𝟘) agrees with the
-- recursive metric-id-generic definition entry-by-entry.
------------------------------------------------------------------------

metric-id-3-eq-bridged :
  (i j : Fin 3) →
  SymBilinForm-3-to-generic metric-id i j ≡ metric-id-generic i j
metric-id-3-eq-bridged zero             zero             = refl
metric-id-3-eq-bridged zero             (suc zero)       = refl
metric-id-3-eq-bridged zero             (suc (suc zero)) = refl
metric-id-3-eq-bridged (suc zero)       zero             = refl
metric-id-3-eq-bridged (suc zero)       (suc zero)       = refl
metric-id-3-eq-bridged (suc zero)       (suc (suc zero)) = refl
metric-id-3-eq-bridged (suc (suc zero)) zero             = refl
metric-id-3-eq-bridged (suc (suc zero)) (suc zero)       = refl
metric-id-3-eq-bridged (suc (suc zero)) (suc (suc zero)) = refl

------------------------------------------------------------------------
-- N-5: bilinear-form-of-metric-id-bridge — direct equality at
-- metric-id specifically.
--
-- bilinear-form-of metric-id v w ≡ bilinear-form-of-generic
-- metric-id-generic v w.
--
-- Proof: chain bilinear-form-of-bridge-3 (at M = metric-id, dropping
-- to SymBilinForm-3-to-generic metric-id) with sum-F₂-cong applied
-- at metric-id-3-eq-bridged (substituting bridged-metric-id with
-- metric-id-generic).
--
-- The sum-F₂-cong substitution requires the bridged matrix to match
-- generic metric-id at every (i, j) — N-4 provides this.
------------------------------------------------------------------------

open import Substrate.Algebra.F2.Vector.Universal using (sum-F₂; sum-F₂-cong)
open import Data.Vec using (lookup)

bilinear-form-of-metric-id-bridge :
  (v w : Vector 3) →
  bilinear-form-of metric-id v w
    ≡ bilinear-form-of-generic metric-id-generic v w
bilinear-form-of-metric-id-bridge v w =
  trans (bilinear-form-of-bridge-3 metric-id v w)
        (sum-F₂-cong {3} (λ i →
          cong (lookup v i ·_)
               (sum-F₂-cong {3} (λ j →
                 cong (_· lookup w j) (metric-id-3-eq-bridged i j)))))

------------------------------------------------------------------------
-- N-6: Capstone documentation.
--
-- After this slice, the dim-3 metric-gauge layer is bridgeable to
-- the n-parametric SymBilinForm layer:
--
--   * Type: SymBilinForm-3 → SymBilinForm 3 via (SymBilinForm-3-to-
--     generic, is-symmetric-bridged-3).
--
--   * Evaluation: bilinear-form-of M v w ≡ bilinear-form-of-generic
--     (bridged M) v w, at any M (not just metric-id).
--
--   * Metric-id-specific: bilinear-form-of metric-id v w ≡
--     bilinear-form-of-generic metric-id-generic v w.
--
-- Enables (as follow-on slices):
--
--   * Demote `·F-eq-metric-id-bilin` in HodgeDim3.MetricGauge.HodgeRecast:
--       ·F-eq-metric-id-bilin v w = trans ·F-eq-metric-id-bilin-generic v w
--                                         (sym (bilinear-form-of-metric-id-bridge v w))
--
--   * Eventually demote StabiliserClosure's 3-cycle proof via
--     FixedPoint-of-compose + congruence-compose-pointwise + a
--     congruence-act bridge (separate slice).
--
-- The reverse bridge (SymBilinForm 3 → SymBilinForm-3) is also
-- a natural slice, but not yet needed — current demotions all go
-- forward (dim-3 → generic). The reverse becomes useful when
-- substrate code starts producing values in the generic layer and
-- wants to deliver them as dim-3 values.
------------------------------------------------------------------------
