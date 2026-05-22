------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim3.MetricGauge
--
-- M-11.metric-gauge slice. Surfaces the 28-element metric gauge over
-- F₂³: non-degenerate symmetric bilinear forms, GL(3, F₂) congruence
-- action, and ONE concrete transitivity witness.
--
-- The metric is the "discrete Hodge ★" parameter at n=3 — different
-- metrics give different orthogonality structures on F₂³ and hence
-- different self-dual subspace structures. The 28 non-degenerate
-- forms form a SINGLE GL(3, F₂) orbit (= gauge), so any choice is
-- structurally equivalent under the GL(3, F₂) symmetry.
--
-- Per `feedback_expose_generator_not_orbit` + `feedback_coalgebraic_not_
-- consumer_driven`: this slice exposes the gauge structure via the
-- INFERENCE RULE (`NonDegenerate` predicate = `det ≡ 𝟙`) and the
-- GENERATOR (the GL(3, F₂) congruence action), NOT via enumeration
-- of all 28 forms. The cardinality 28 = 168/6 is a derived consequence
-- of orbit-stabiliser, not primary structure.
--
-- The 3 specific metrics defined here (metric-id / metric-mixed /
-- metric-fully-coupled) are **structural exemplars** of distinct
-- shape-classes under the S₃ axis-permutation subgroup of GL(3, F₂),
-- NOT enumeration positions. Under the full GL(3, F₂) they're all
-- gauge-equivalent in the same orbit.
--
-- Follow-on coalgebraic-unfolding slices: see M-11.metric-gauge.DBE.md.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim3.MetricGauge where

open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Vec using (Vec; []; _∷_; lookup)
open import Substrate.Foundation.Eq
  using (_≡_; refl; trans; cong)

open import Substrate.Algebra.F2
open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.Linear
open import Substrate.Algebra.F2.Linear.FromImages
  using (linear-from-images; apply-linear-from-images-basis)

------------------------------------------------------------------------
-- N-1: SymBilinForm-3 type + 6 named accessors.
--
-- A symmetric 3×3 matrix over F₂ has 6 independent entries:
--   [[ a  d  e ]
--    [ d  b  f ]
--    [ e  f  c ]]
--
-- We represent it as Vector 6 with entries (a, b, c, d, e, f) at
-- positions (0, 1, 2, 3, 4, 5).
------------------------------------------------------------------------

SymBilinForm-3 : Set
SymBilinForm-3 = Vector 6

-- Named accessors.
entry-a entry-b entry-c entry-d entry-e entry-f : SymBilinForm-3 → F₂
entry-a m = lookup m zero
entry-b m = lookup m (suc zero)
entry-c m = lookup m (suc (suc zero))
entry-d m = lookup m (suc (suc (suc zero)))
entry-e m = lookup m (suc (suc (suc (suc zero))))
entry-f m = lookup m (suc (suc (suc (suc (suc zero)))))

------------------------------------------------------------------------
-- N-2: det-sym3 — determinant of a symmetric 3×3 matrix over F₂.
--
-- Over F₂ (characteristic 2), the standard determinant formula
-- simplifies as follows. For [[a,d,e],[d,b,f],[e,f,c]]:
--
--   det = a(bc - f²) - d(dc - fe) + e(df - be)
--       = abc - af² - d²c + 2def - e²b           [expanding]
--       = abc + af + cd + eb                     [in F₂: x²=x, 2x=0, -x=x]
------------------------------------------------------------------------

det-sym3 : SymBilinForm-3 → F₂
det-sym3 m =
  let a = entry-a m; b = entry-b m; c = entry-c m
      d = entry-d m; e = entry-e m; f = entry-f m
  in a · b · c + a · f + c · d + e · b

------------------------------------------------------------------------
-- N-3: NonDegenerate predicate.
--
-- A form is non-degenerate iff its determinant is 𝟙. Decidability
-- inherits from F₂'s decidable equality.
------------------------------------------------------------------------

NonDegenerate : SymBilinForm-3 → Set
NonDegenerate m = det-sym3 m ≡ 𝟙

------------------------------------------------------------------------
-- N-4: Three structural-exemplar metrics (NOT enumeration positions).
--
-- These expose distinct shape-classes of non-degenerate forms under
-- the S₃ axis-permutation subgroup of GL(3, F₂):
--
--   metric-id              — diagonal identity (orthogonal class)
--   metric-mixed           — exactly one off-diagonal coupling (mixed class)
--   metric-fully-coupled   — all three off-diagonals nonzero (coupled class)
--
-- Under the full GL(3, F₂) they're all gauge-equivalent in the single
-- 28-element orbit. The 3 are exemplars exposing the orbit's INTERNAL
-- shape structure, not enumeration positions of a 28-form list.
--
-- Sizes of the shape-classes (verified by hand-count in the obs review):
--   1 diagonal + 9 one-interaction + 15 two-interaction + 3 fully-coupled = 28.
------------------------------------------------------------------------

-- The diagonal identity: a=b=c=1, d=e=f=0.
metric-id : SymBilinForm-3
metric-id = 𝟙 ∷ 𝟙 ∷ 𝟙 ∷ 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ []

metric-id-non-degenerate : NonDegenerate metric-id
metric-id-non-degenerate = refl

-- An exemplar mixed (one-coupling) form: a=0, b=0, c=1, d=1, e=f=0.
-- Matrix [[0, 1, 0], [1, 0, 0], [0, 0, 1]]. Det = 0·0·1 + 0·0 + 1·1 + 0·0 = 1.
metric-mixed : SymBilinForm-3
metric-mixed = 𝟘 ∷ 𝟘 ∷ 𝟙 ∷ 𝟙 ∷ 𝟘 ∷ 𝟘 ∷ []

metric-mixed-non-degenerate : NonDegenerate metric-mixed
metric-mixed-non-degenerate = refl

-- An exemplar fully-coupled form: a=1, b=0, c=0, d=e=f=1.
-- Det = 1·0·0 + 1·1 + 0·1 + 1·0 = 1.
metric-fully-coupled : SymBilinForm-3
metric-fully-coupled = 𝟙 ∷ 𝟘 ∷ 𝟘 ∷ 𝟙 ∷ 𝟙 ∷ 𝟙 ∷ []

metric-fully-coupled-non-degenerate : NonDegenerate metric-fully-coupled
metric-fully-coupled-non-degenerate = refl

------------------------------------------------------------------------
-- N-5: bilinear-form-of + congruence-act.
--
-- bilinear-form-of M v w computes v^T M w over F₂. For symmetric M
-- with entries (a, b, c, d, e, f):
--
--   v^T M w = v₀(a·w₀ + d·w₁ + e·w₂)
--           + v₁(d·w₀ + b·w₁ + f·w₂)
--           + v₂(e·w₀ + f·w₁ + c·w₂)
--
-- congruence-act T M produces the new symmetric form whose (i, j) entry
-- is bilinear-form-of M (T e_i) (T e_j). This IS the standard
-- T^T M T congruence action expressed via the bilinear-form interpretation.
------------------------------------------------------------------------

bilinear-form-of : SymBilinForm-3 → Vector 3 → Vector 3 → F₂
bilinear-form-of (a ∷ b ∷ c ∷ d ∷ e ∷ f ∷ [])
                 (v₀ ∷ v₁ ∷ v₂ ∷ [])
                 (w₀ ∷ w₁ ∷ w₂ ∷ []) =
  v₀ · (a · w₀ + d · w₁ + e · w₂) +
  v₁ · (d · w₀ + b · w₁ + f · w₂) +
  v₂ · (e · w₀ + f · w₁ + c · w₂)

congruence-act : Linear 3 3 → SymBilinForm-3 → SymBilinForm-3
congruence-act T M =
  bilinear-form-of M Te₀ Te₀ ∷
  bilinear-form-of M Te₁ Te₁ ∷
  bilinear-form-of M Te₂ Te₂ ∷
  bilinear-form-of M Te₀ Te₁ ∷
  bilinear-form-of M Te₀ Te₂ ∷
  bilinear-form-of M Te₁ Te₂ ∷ []
  where
    Te₀ = apply T (basis zero)
    Te₁ = apply T (basis (suc zero))
    Te₂ = apply T (basis (suc (suc zero)))

------------------------------------------------------------------------
-- N-6: ONE concrete transitivity witness — metric-id → metric-mixed.
--
-- Constructs an explicit T ∈ Linear 3 3 (invertible; det = 𝟙) with
--
--    congruence-act T metric-id ≡ metric-mixed
--
-- Choice of T: columns (1,1,0), (1,0,1), (1,1,1). Verifying:
--
--    t₀·t₀ = 0   (a')      t₀·t₁ = 1   (d')
--    t₁·t₁ = 0   (b')      t₀·t₂ = 0   (e')
--    t₂·t₂ = 1   (c')      t₁·t₂ = 0   (f')
--
-- which matches metric-mixed = (0, 0, 1, 1, 0, 0).
--
-- This is ONE instance of the orbit transitivity. Full structural
-- transitivity (= every non-degenerate form reduces to metric-id via
-- some T) is a coalgebraic-unfolding follow-on (M-11.metric-gauge.
-- orbit-characterisation in the DBE plan).
------------------------------------------------------------------------

T-id-to-mixed-images : Fin 3 → Vector 3
T-id-to-mixed-images zero          = 𝟙 ∷ 𝟙 ∷ 𝟘 ∷ []
T-id-to-mixed-images (suc zero)    = 𝟙 ∷ 𝟘 ∷ 𝟙 ∷ []
T-id-to-mixed-images (suc (suc _)) = 𝟙 ∷ 𝟙 ∷ 𝟙 ∷ []

T-id-to-mixed : Linear 3 3
T-id-to-mixed = linear-from-images T-id-to-mixed-images

-- Helpers: apply T-id-to-mixed at each basis vector reduces to the
-- corresponding image, via apply-linear-from-images-basis (universal-
-- property discipline).
T-on-e₀ : apply T-id-to-mixed (basis zero) ≡ (𝟙 ∷ 𝟙 ∷ 𝟘 ∷ [])
T-on-e₀ = apply-linear-from-images-basis T-id-to-mixed-images zero

T-on-e₁ : apply T-id-to-mixed (basis (suc zero)) ≡ (𝟙 ∷ 𝟘 ∷ 𝟙 ∷ [])
T-on-e₁ = apply-linear-from-images-basis T-id-to-mixed-images (suc zero)

T-on-e₂ : apply T-id-to-mixed (basis (suc (suc zero))) ≡ (𝟙 ∷ 𝟙 ∷ 𝟙 ∷ [])
T-on-e₂ = apply-linear-from-images-basis T-id-to-mixed-images (suc (suc zero))

-- The transitivity witness equation.
--
-- Goal: congruence-act T-id-to-mixed metric-id ≡ metric-mixed
-- After unfolding congruence-act, both sides are Vector 6 expressions
-- where the LHS has `apply T (basis i)` and the RHS has explicit
-- constants. The T-on-eᵢ rewrites substitute apply T results into
-- bilinear-form-of, after which both sides reduce to the same
-- 6-tuple by F₂ arithmetic.
--
-- We use ≡-from-lookup at the Vector 6 level, with each of the 6
-- entries closing by rewriting via T-on-eᵢ then refl.

congruence-id-to-mixed :
  congruence-act T-id-to-mixed metric-id ≡ metric-mixed
congruence-id-to-mixed = ≡-from-lookup _ _ goal
  where
    goal : (i : Fin 6) →
           lookup (congruence-act T-id-to-mixed metric-id) i ≡
           lookup metric-mixed i
    goal zero =
      -- Entry a' = bilinear-form-of metric-id (T e₀) (T e₀)
      -- After T-on-e₀: = bilinear-form-of metric-id (1,1,0) (1,1,0)
      -- Compute: 1·(1·1+0·1+0·0) + 1·(0·1+1·1+0·0) + 0·... = 1+1+0 = 0
      cong (λ x → bilinear-form-of metric-id x x) T-on-e₀
    goal (suc zero) =
      cong (λ x → bilinear-form-of metric-id x x) T-on-e₁
    goal (suc (suc zero)) =
      cong (λ x → bilinear-form-of metric-id x x) T-on-e₂
    goal (suc (suc (suc zero))) =
      -- Entry d' = bilinear-form-of metric-id (T e₀) (T e₁)
      trans (cong (λ x → bilinear-form-of metric-id x (apply T-id-to-mixed (basis (suc zero)))) T-on-e₀)
            (cong (bilinear-form-of metric-id (𝟙 ∷ 𝟙 ∷ 𝟘 ∷ [])) T-on-e₁)
    goal (suc (suc (suc (suc zero)))) =
      -- Entry e' = bilinear-form-of metric-id (T e₀) (T e₂)
      trans (cong (λ x → bilinear-form-of metric-id x (apply T-id-to-mixed (basis (suc (suc zero))))) T-on-e₀)
            (cong (bilinear-form-of metric-id (𝟙 ∷ 𝟙 ∷ 𝟘 ∷ [])) T-on-e₂)
    goal (suc (suc (suc (suc (suc zero))))) =
      -- Entry f' = bilinear-form-of metric-id (T e₁) (T e₂)
      trans (cong (λ x → bilinear-form-of metric-id x (apply T-id-to-mixed (basis (suc (suc zero))))) T-on-e₁)
            (cong (bilinear-form-of metric-id (𝟙 ∷ 𝟘 ∷ 𝟙 ∷ [])) T-on-e₂)

------------------------------------------------------------------------
-- N-7: Status documentation.
--
-- This slice exposes the metric gauge structure at n=3:
--
--   * The TYPE `Σ SymBilinForm-3 NonDegenerate` characterises the
--     28-element non-degenerate-form space via an inference rule
--     (no enumeration).
--   * `congruence-act` is the GL(3, F₂) action that generates the
--     orbit on this type.
--   * The 3 structural exemplars (metric-id / metric-mixed /
--     metric-fully-coupled) witness distinct shape-classes under the
--     axis-permutation S₃ subgroup; under the full GL(3, F₂) they're
--     gauge-equivalent.
--   * `congruence-id-to-mixed` is ONE concrete transitivity witness
--     proving the orbit-equivalence of two exemplars.
--
-- The cardinality 28 = 168/6 is a derived orbit-stabiliser consequence,
-- not primary structure. The follow-on coalgebraic-unfolding slices
-- (in M-11.metric-gauge.DBE.md) develop:
--   * Structural orbit-characterisation (every non-degenerate form
--     reduces to metric-id via explicit T; Gram-Schmidt-like).
--   * Coxeter-style GL(3, F₂) groupoid via generators + relations.
--   * O(3, F₂) = stabiliser of metric-id via Coxeter S₃ presentation.
--   * The existing `_·F_` dot product recast as
--     `bilinear-form-of metric-id`; parametric `bilinear-form-of M`
--     gives Hodge-orthogonality for any metric.
--   * Abstract orbit-stabiliser theorem.
--
-- This slice is the foundation; the unfoldings flow from it.
------------------------------------------------------------------------
