------------------------------------------------------------------------
-- Substrate.Algebra.F2.SymBilinForm
--
-- The n-parametric symmetric bilinear form on F₂ⁿ — the categorical
-- fixed point of the substrate's metric-gauge work. Replaces per-dim
-- definitions (SymBilinForm-3, SymBilinForm-4) with a single generic
-- type, parametric over n. Bridges to existing dim-3 / dim-4
-- infrastructure are follow-on slices; this slice establishes the
-- generic LAYER.
--
-- Design (per `feedback_categorical_name_first` and
-- `feedback_expose_generator_not_orbit`):
--
--   * `BilinForm n` is the data — a matrix `Fin n → Fin n → F₂`.
--     Not all bilinear forms are symmetric; symmetry is a separate
--     predicate, not baked into the type.
--
--   * `IsSymmetric M` is the property `M(i, j) ≡ M(j, i)`. Decidable;
--     orthogonal to the data.
--
--   * `SymBilinForm n = Σ (BilinForm n) IsSymmetric` is the subtype
--     of symmetric forms.
--
--   * `bilinear-form-of M v w` is the generic double-sum formula
--     `Σᵢ vᵢ · Σⱼ M(i,j) · wⱼ`, working on any BilinForm.
--
--   * `metric-id` is the n-parametric diagonal identity (recursive
--     definition on Fin); `is-symmetric-metric-id` proves it
--     symmetric (recursive proof, no decidable equality needed).
--
--   * `congruence-act T M` is the generic T^T M T action via
--     `bilinear-form-of M (apply T (basis i)) (apply T (basis j))`.
--
--   * `NonDegenerate M` is the kernel-free predicate expressed via
--     the categorical Wide-Meet + IsEqualised primitives —
--     non-degeneracy at any n is the SAME categorical structure.
--
-- After this slice: the language for metric-gauge work is the
-- categorical primitive layer. Adding dim n requires zero new
-- infrastructure; `bilinear-form-of metric-id v w` at any n is the
-- generic dot product; `NonDegenerate M` at any n is the categorical
-- predicate.
--
-- Deferred to follow-on slices:
--
--   * Bridges `SymBilinForm-3 ↔ SymBilinForm 3` and `SymBilinForm-4
--     ↔ SymBilinForm 4` — round-trip equivalences keeping existing
--     dim-3 / dim-4 proofs alive.
--
--   * Generic `·F-eq-metric-id-bilin : v ·F w ≡ bilinear-form-of
--     metric-id v w` proved once at any n, instantiating both the
--     dim-3 and dim-4 recast lemmas as corollaries.
--
--   * Generic `metric-id-non-degenerate` proved once at any n.
--
--   * Generic `bilinearity-of-bilinear-form-of` (additivity + scalar
--     respect in each argument) — unblocks the `congruence-compose`
--     lemma at any n, which in turn (via FixedPoint-of-compose from
--     primitive #1) automates StabiliserClosure-style cascades at
--     any n.
--
--   * `is-symmetric-congruence-act`: congruence-act preserves
--     symmetry — derivable from bilinearity-of-bilinear-form-of.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.SymBilinForm where

open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Product using (Σ; _,_; proj₁; proj₂)
open import Substrate.Foundation.Vec using (lookup)
open import Substrate.Foundation.Function using (const)
open import Substrate.Foundation.Eq
  using (_≡_; refl; sym; trans; cong; cong₂)

open import Substrate.Algebra.F2
open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.Vector.Universal using (sum-F₂)
open import Substrate.Algebra.F2.Linear

open import Substrate.Category.Equalizer using (IsEqualised)
open import Substrate.Category.Pullback using (Wide-Meet)

------------------------------------------------------------------------
-- N-1: BilinForm — a general (not necessarily symmetric) bilinear
-- form over F₂ⁿ, as the data of a matrix.
------------------------------------------------------------------------

BilinForm : ℕ → Set
BilinForm n = Fin n → Fin n → F₂

------------------------------------------------------------------------
-- N-2: IsSymmetric — predicate "M(i, j) ≡ M(j, i)".
--
-- Orthogonal to the BilinForm data; SymBilinForm = (M, symmetry-witness).
------------------------------------------------------------------------

IsSymmetric : ∀ {n} → BilinForm n → Set
IsSymmetric {n} M = (i j : Fin n) → M i j ≡ M j i

SymBilinForm : ℕ → Set
SymBilinForm n = Σ (BilinForm n) IsSymmetric

bilin-of : ∀ {n} → SymBilinForm n → BilinForm n
bilin-of = proj₁

is-symmetric : ∀ {n} (M : SymBilinForm n) → IsSymmetric (bilin-of M)
is-symmetric = proj₂

------------------------------------------------------------------------
-- N-3: bilinear-form-of — generic double-sum evaluation.
--
--   bilinear-form-of M v w  =  Σᵢ vᵢ · Σⱼ M(i,j) · wⱼ
--
-- Works on any BilinForm (symmetric or not). The substrate's per-dim
-- definitions (SymBilinForm-3.bilinear-form-of, SymBilinForm-4.
-- bilinear-form-of-4) are pattern-expanded versions of this same
-- generic formula at fixed n.
------------------------------------------------------------------------

bilinear-form-of : ∀ {n} → BilinForm n → Vector n → Vector n → F₂
bilinear-form-of {n} M v w =
  sum-F₂ {n} (λ i → lookup v i · sum-F₂ {n} (λ j → M i j · lookup w j))

------------------------------------------------------------------------
-- N-4: metric-id — the n-parametric diagonal identity.
--
-- Defined recursively on Fin: M(i, j) = 𝟙 iff i = j as Fin patterns,
-- else 𝟘. No decidable equality needed — pattern-match on the two
-- Fins simultaneously.
------------------------------------------------------------------------

metric-id : ∀ {n} → BilinForm n
metric-id zero    zero    = 𝟙
metric-id zero    (suc _) = 𝟘
metric-id (suc _) zero    = 𝟘
metric-id (suc i) (suc j) = metric-id i j

-- metric-id is symmetric. Recursive proof, no decidable equality.
is-symmetric-metric-id : ∀ {n} → IsSymmetric (metric-id {n})
is-symmetric-metric-id zero    zero    = refl
is-symmetric-metric-id zero    (suc _) = refl
is-symmetric-metric-id (suc _) zero    = refl
is-symmetric-metric-id (suc i) (suc j) = is-symmetric-metric-id i j

-- metric-id packaged as a SymBilinForm.
metric-id-Sym : ∀ {n} → SymBilinForm n
metric-id-Sym = metric-id , is-symmetric-metric-id

------------------------------------------------------------------------
-- N-5: congruence-act — the generic T^T M T action.
--
--   (congruence-act T M)(i, j) = bilinear-form-of M (T eᵢ) (T eⱼ)
--
-- Works on any BilinForm. Preservation of symmetry under congruence-
-- act is a derived consequence of bilinearity-of-bilinear-form-of
-- (deferred slice).
------------------------------------------------------------------------

congruence-act : ∀ {n} → Linear n n → BilinForm n → BilinForm n
congruence-act T M i j =
  bilinear-form-of M (apply T (basis i)) (apply T (basis j))

------------------------------------------------------------------------
-- N-6: NonDegenerate — kernel-free predicate via categorical primitives.
--
-- The radical of M is the wide meet over w of the per-w equalizer
-- of (u ↦ bilinear-form-of M u w) and (const 𝟘) — i.e., the set
-- of v's that pair to 𝟘 with EVERY w. NonDegenerate says the radical
-- contains only 𝟎ⱽ.
--
-- This expresses the substrate's recurring kernel-free pattern
-- purely in categorical terms (Wide-Meet of IsEqualised). The
-- existing per-dim predicates (NonDegenerate, NonDegenerate-4) are
-- specializations of this generic version.
------------------------------------------------------------------------

-- The per-w equalizer family: each w gives the equalizer of
-- (u ↦ bilinear-form-of M u w) and the constant-𝟘 function.
pair-eq-family : ∀ {n} → BilinForm n → Vector n → Vector n → Set
pair-eq-family {n} M w v =
  IsEqualised (λ u → bilinear-form-of M u w) (const 𝟘) v

-- The radical of M as a Wide-Meet over w of the per-w equalizers.
Radical : ∀ {n} → BilinForm n → Vector n → Set
Radical {n} M = Wide-Meet (pair-eq-family M)

-- M is non-degenerate iff the radical contains only the trivial element.
NonDegenerate : ∀ {n} → BilinForm n → Set
NonDegenerate {n} M = (v : Vector n) → Radical M v → v ≡ 𝟎ⱽ

------------------------------------------------------------------------
-- N-7: Capstone — the categorical fixed-point achieved.
--
-- After this slice, the metric-gauge language is parametric in n,
-- not per-dim:
--
--   * SymBilinForm n               — generic data
--   * bilinear-form-of M v w        — generic evaluation (double sum-F₂)
--   * NonDegenerate M               — generic predicate (Wide-Meet of
--                                     IsEqualised, both categorical)
--   * congruence-act T M            — generic GL(n, F₂) action
--   * metric-id : SymBilinForm n   — generic diagonal identity
--   * is-symmetric-metric-id        — generic symmetry proof
--
-- The categorical primitives (FixedPoint, IsEqualised, Wide-Meet,
-- Pullback) NOW govern the metric-gauge work. New dimensions require
-- ZERO new infrastructure — just instantiate at the desired n.
--
-- Concrete consequences:
--
--   * `bilinear-form-of metric-id v w` at n=5, n=6, ... — works
--     immediately, no per-dim slice needed.
--
--   * `NonDegenerate metric-id` proved once at generic n (deferred
--     slice) — both the dim-3 and dim-4 existing witnesses become
--     instantiation corollaries.
--
--   * The catalog's "Reserved = SelfDual" identification at any
--     dim parametrizes via `SymBilinForm n` instead of dim-
--     rigidifying.
--
-- Deferred coalgebraic-unfolding follow-on slices:
--
--   * **bridges-dim-3-dim-4**: round-trip isomorphisms
--     `SymBilinForm-3 ↔ SymBilinForm 3` and
--     `SymBilinForm-4 ↔ SymBilinForm 4` (where left-hand-sides are
--     the existing Vector 6 / Vector 10 packings). Keeps existing
--     dim-3 / dim-4 proofs alive without rewriting them.
--
--   * **HodgeRecast-generic**: `v ·F w ≡ bilinear-form-of metric-id
--     v w` at any n. Both HodgeDim3.MetricGauge.HodgeRecast and
--     HodgeDim4.MetricGauge.HodgeRecast become corollaries.
--
--   * **metric-id-non-degenerate-generic**: kernel-free witness for
--     `metric-id` at any n (the per-basis pairing argument generalised).
--     Both NonDegenerate (dim-3, when written) and NonDegenerate-4
--     (existing) instantiate this.
--
--   * **bilinearity-of-bilinear-form-of**: additivity + scalar-respect
--     in each argument. Unblocks `congruence-compose` and
--     `is-symmetric-congruence-act` at any n.
--
--   * **congruence-compose**: `congruence-act (T₁ ∘L T₂) M ≡
--     congruence-act T₂ (congruence-act T₁ M)` at any n. With
--     FixedPoint-of-compose from primitive #1, this automates the
--     StabiliserClosure cascade at any n — at dim 3, the 6-element
--     S₃ stabiliser becomes derivable from the 2 Coxeter generators'
--     fixed-point witnesses.
--
--   * **L_metric-as-functor**: the assignment n ↦ SymBilinForm n,
--     together with the GL(n, F₂) action, is a functor / action
--     groupoid. Naming this surfaces the "metric gauge tower" as
--     a single categorical object across all n. Primitive-#6-adjacent.
--
-- Per `feedback_coalgebraic_not_consumer_driven`: these unfoldings
-- progressively land the fixed-point as the operating language; not
-- "if downstream consumers need them" but "this IS the work."
------------------------------------------------------------------------
