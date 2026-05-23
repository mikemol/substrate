------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim3.MetricGauge.CongruenceBridge
--
-- Bridges the dim-3 specific `congruence-act` to the generic
-- `congruence-act` from Substrate.Algebra.F2.SymBilinForm, and uses
-- it to derive a dim-3 specific `congruence-compose-3` law from the
-- generic `congruence-compose-pointwise`.
--
-- Components:
--
--   * `congruence-act-bridge-3` — pointwise equality of the bridged
--     dim-3 congruence-act'd form with the generic congruence-act on
--     the bridged input.
--   * `bridge-injectivity-3` — the SymBilinForm-3 → BilinForm 3 bridge
--     reflects equality: pointwise (i, j) agreement on the bridges
--     implies SymBilinForm-3 equality.
--   * `congruence-compose-3` — the dim-3 specific composition law:
--       congruence-act (T₁ ∘L T₂) M ≡ congruence-act T₂ (congruence-act T₁ M)
--
-- After this slice: StabiliserClosure's 3-cycle proof (and any other
-- Coxeter-element-composition stabilisation) reduces to a 3-line
-- corollary via congruence-compose-3 + individual generator stabiliser
-- FixedPoint witnesses.
--
-- Per `feedback_categorical_name_first`: the dim-3 specific composition
-- law is now a derived corollary of the generic universal property
-- (congruence-compose-pointwise) + the dim-3 bridge.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim3.MetricGauge.CongruenceBridge where

open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Fin.Literals using (₁; ₂; ₃; ₄; ₅)
open import Substrate.Foundation.Vec using (lookup)
open import Substrate.Foundation.Eq
  using (_≡_; refl; sym; trans; cong)

open import Substrate.Algebra.F2
open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.Vector.Universal using (sum-F₂; sum-F₂-cong)
open import Substrate.Algebra.F2.Linear
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge
  using (SymBilinForm-3; bilinear-form-of; congruence-act)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.GenericBridge
  using (SymBilinForm-3-to-generic; is-symmetric-bridged-3;
         bilinear-form-of-bridge-3)

-- Generic infrastructure.
open import Substrate.Algebra.F2.SymBilinForm
  using (BilinForm)
  renaming (bilinear-form-of to bilinear-form-of-generic;
            congruence-act   to congruence-act-generic)
open import Substrate.Algebra.F2.SymBilinForm.CongruenceCompose
  using (congruence-compose-pointwise)
open import Substrate.Algebra.F2.SymBilinForm.Symmetry
  using (bilinear-form-of-sym-arg)

------------------------------------------------------------------------
-- N-1: congruence-act-bridge-3.
--
-- 9 cases: diagonal (3), upper off-diagonal (3), lower off-diagonal (3).
-- Diagonals + upper-tri: direct bilinear-form-of-bridge-3.
-- Lower-tri: bilinear-form-of-bridge-3 + bilinear-form-of-sym-arg
-- (since the dim-3 packing folds (i, j) and (j, i) to the same
-- off-diagonal slot).
------------------------------------------------------------------------

congruence-act-bridge-3 :
  (T : Linear 3 3) (M : SymBilinForm-3) (i j : Fin 3) →
  SymBilinForm-3-to-generic (congruence-act T M) i j
    ≡ congruence-act-generic T (SymBilinForm-3-to-generic M) i j
-- Diagonal cases.
congruence-act-bridge-3 T M zero zero =
  bilinear-form-of-bridge-3 M
    (apply T (basis zero)) (apply T (basis zero))
congruence-act-bridge-3 T M (suc zero) (suc zero) =
  bilinear-form-of-bridge-3 M
    (apply T (basis (suc zero))) (apply T (basis (suc zero)))
congruence-act-bridge-3 T M ₂ ₂ =
  bilinear-form-of-bridge-3 M
    (apply T (basis ₂)) (apply T (basis ₂))
-- Upper off-diagonal cases.
congruence-act-bridge-3 T M zero (suc zero) =
  bilinear-form-of-bridge-3 M
    (apply T (basis zero)) (apply T (basis (suc zero)))
congruence-act-bridge-3 T M zero ₂ =
  bilinear-form-of-bridge-3 M
    (apply T (basis zero)) (apply T (basis ₂))
congruence-act-bridge-3 T M (suc zero) ₂ =
  bilinear-form-of-bridge-3 M
    (apply T (basis (suc zero))) (apply T (basis ₂))
-- Lower off-diagonal cases: bridge then swap arguments via symmetry.
congruence-act-bridge-3 T M (suc zero) zero =
  trans (bilinear-form-of-bridge-3 M
           (apply T (basis zero)) (apply T (basis (suc zero))))
        (bilinear-form-of-sym-arg
           (SymBilinForm-3-to-generic M)
           (is-symmetric-bridged-3 M)
           (apply T (basis zero)) (apply T (basis (suc zero))))
congruence-act-bridge-3 T M ₂ zero =
  trans (bilinear-form-of-bridge-3 M
           (apply T (basis zero)) (apply T (basis ₂)))
        (bilinear-form-of-sym-arg
           (SymBilinForm-3-to-generic M)
           (is-symmetric-bridged-3 M)
           (apply T (basis zero)) (apply T (basis ₂)))
congruence-act-bridge-3 T M ₂ (suc zero) =
  trans (bilinear-form-of-bridge-3 M
           (apply T (basis (suc zero))) (apply T (basis ₂)))
        (bilinear-form-of-sym-arg
           (SymBilinForm-3-to-generic M)
           (is-symmetric-bridged-3 M)
           (apply T (basis (suc zero))) (apply T (basis ₂)))

------------------------------------------------------------------------
-- N-2: Pointwise-substitution helpers.
--
-- Without function extensionality, we use sum-F₂-cong-based helpers
-- to substitute pointwise-equal arguments in bilinear-form-of-generic
-- and congruence-act-generic.
------------------------------------------------------------------------

-- If two BilinForm n's agree pointwise, their bilinear-form-of
-- evaluations agree.
bilinear-form-of-generic-cong :
  ∀ {n} (M₁ M₂ : BilinForm n) (v w : Vector n) →
  ((i j : Fin n) → M₁ i j ≡ M₂ i j) →
  bilinear-form-of-generic M₁ v w ≡ bilinear-form-of-generic M₂ v w
bilinear-form-of-generic-cong {n} M₁ M₂ v w eq =
  sum-F₂-cong {n} (λ i →
    cong (lookup v i ·_)
         (sum-F₂-cong {n} (λ j →
           cong (_· lookup w j) (eq i j))))

-- If two BilinForm n's agree pointwise, their congruence-acted
-- versions agree pointwise.
congruence-act-generic-cong :
  ∀ {n} (T : Linear n n) (M₁ M₂ : BilinForm n) →
  ((i j : Fin n) → M₁ i j ≡ M₂ i j) →
  (i j : Fin n) →
  congruence-act-generic T M₁ i j ≡ congruence-act-generic T M₂ i j
congruence-act-generic-cong T M₁ M₂ eq i j =
  bilinear-form-of-generic-cong M₁ M₂
    (apply T (basis i)) (apply T (basis j)) eq

------------------------------------------------------------------------
-- N-3: bridge-injectivity-3.
--
-- Pointwise agreement of the bridged forms implies equality of the
-- original SymBilinForm-3 values. Extract each of 6 Vector 6 entries
-- via the appropriate (i, j) lookup of the bridge.
------------------------------------------------------------------------

bridge-injectivity-3 :
  (M₁ M₂ : SymBilinForm-3) →
  ((i j : Fin 3) → SymBilinForm-3-to-generic M₁ i j
                     ≡ SymBilinForm-3-to-generic M₂ i j) →
  M₁ ≡ M₂
bridge-injectivity-3 M₁ M₂ eq =
  ≡-from-lookup M₁ M₂ goal
  where
    goal : (k : Fin 6) → lookup M₁ k ≡ lookup M₂ k
    goal zero                                  = eq zero zero
    goal (suc zero)                            = eq (suc zero) (suc zero)
    goal ₂                      = eq ₂
                                                    ₂
    goal ₃                = eq zero (suc zero)
    goal ₄          = eq zero ₂
    goal ₅    = eq (suc zero)
                                                    ₂

------------------------------------------------------------------------
-- N-4: congruence-compose-3 — dim-3 specific composition law.
--
-- Strategy:
--   For each (i, j), show
--     bridge (congruence-act (T₁ ∘L T₂) M) i j
--       ≡ bridge (congruence-act T₂ (congruence-act T₁ M)) i j
--   via:
--     LHS_brid ≡ congruence-act-generic (T₁ ∘L T₂) (bridge M) i j
--             ≡ congruence-act-generic T₂ (congruence-act-generic T₁ (bridge M)) i j
--                                                      [compose-pointwise]
--             ≡ congruence-act-generic T₂ (bridge (congruence-act T₁ M)) i j
--                                                      [congruence-act-generic-cong
--                                                       + sym congruence-act-bridge-3]
--             ≡ RHS_brid
--   Then bridge-injectivity-3 lifts to SymBilinForm-3 equality.
------------------------------------------------------------------------

congruence-compose-3 :
  (T₁ T₂ : Linear 3 3) (M : SymBilinForm-3) →
  congruence-act (T₁ ∘L T₂) M ≡ congruence-act T₂ (congruence-act T₁ M)
congruence-compose-3 T₁ T₂ M =
  bridge-injectivity-3
    (congruence-act (T₁ ∘L T₂) M)
    (congruence-act T₂ (congruence-act T₁ M))
    bridges-agree
  where
    bridges-agree :
      (i j : Fin 3) →
      SymBilinForm-3-to-generic (congruence-act (T₁ ∘L T₂) M) i j
        ≡ SymBilinForm-3-to-generic
            (congruence-act T₂ (congruence-act T₁ M)) i j
    bridges-agree i j =
      trans (congruence-act-bridge-3 (T₁ ∘L T₂) M i j)
      (trans (congruence-compose-pointwise T₁ T₂
                (SymBilinForm-3-to-generic M) i j)
      (trans (congruence-act-generic-cong T₂
                (congruence-act-generic T₁ (SymBilinForm-3-to-generic M))
                (SymBilinForm-3-to-generic (congruence-act T₁ M))
                (λ i' j' → sym (congruence-act-bridge-3 T₁ M i' j'))
                i j)
             (sym (congruence-act-bridge-3 T₂
                     (congruence-act T₁ M) i j))))

------------------------------------------------------------------------
-- N-5: Capstone.
--
-- congruence-compose-3 is the dim-3 specific composition law for
-- congruence-act, derived as a corollary of the generic
-- congruence-compose-pointwise + the dim-3 bridge (with bilinear-
-- form-of-sym-arg handling lower-triangular index swap, and
-- bilinear-form-of-generic-cong + congruence-act-generic-cong
-- substituting pointwise-equal arguments without function extensionality).
--
-- Use case: StabiliserClosure's `s₁∘s₂-stabilises-metric-id` (and
-- analogous compositions s₂∘s₁, s₁∘s₂∘s₁, etc.) reduces to:
--
--   s₁∘s₂-stabilises-metric-id =
--     trans (congruence-compose-3 s₁ s₂ metric-id)
--           (trans (cong (congruence-act s₂) s₁-stabilises-metric-id)
--                  s₂-stabilises-metric-id)
--
-- — a 3-line derivation replacing the original per-cycle proof.
--
-- Per `feedback_categorical_name_first`: the dim-3 composition law
-- is now derived from the generic universal property; the per-cycle
-- algebraic template is no longer load-bearing.
--
-- Deferred follow-ons:
--
--   * Demote StabiliserClosure.agda — rewrite the 3-cycle proof
--     using congruence-compose-3. Separate slice for visibility of
--     the demotion.
--   * Analogous CongruenceBridge-4 at dim 4 (if a dim-4 stabiliser
--     story develops).
------------------------------------------------------------------------
