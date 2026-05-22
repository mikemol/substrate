------------------------------------------------------------------------
-- Substrate.Algebra.F2.SymBilinForm.NonDegenerate
--
-- Generic non-degeneracy witness for metric-id at any n. Proves
--
--   metric-id-non-degenerate-generic : NonDegenerate (metric-id {n})
--
-- as a single theorem parametric in n. The existing
-- HodgeDim4.MetricGauge.NonDegenerate.metric-id-4-non-degenerate
-- (and a dim-3 analog, when written) become INSTANTIATION COROLLARIES
-- of this proof (modulo SymBilinForm-{3,4} bridges).
--
-- Argument: if v is in the radical of metric-id (= pairs to 𝟘 with
-- every w), then in particular pairing with each basis vector eᵢ
-- gives lookup v i ≡ 𝟘. Conclude v ≡ 𝟎ⱽ by ≡-from-lookup.
--
-- Key auxiliary: `pair-metric-id-with-basis-generic`, which says
--
--   bilinear-form-of metric-id v (basis i) ≡ lookup v i
--
-- — the universal "metric-id evaluates against a basis vector to
-- extract the corresponding component." Proved via two δ-collapses
-- (the inner metric-id-collapse, and the outer one against
-- `lookup (basis i)` viewed as the same delta function as metric-id i
-- modulo `basis-row-eq-metric-id`).
--
-- Per `feedback_universal_property_discipline`: the "pair-with-basis-
-- extracts-component" lemma IS the universal property of metric-id
-- as the Kronecker delta — proved once, used as the inference rule
-- for non-degeneracy at any n.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.SymBilinForm.NonDegenerate where

open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Vec using (lookup)
open import Substrate.Foundation.Function using (const)
open import Substrate.Foundation.Eq
  using (_≡_; refl; sym; trans; cong)

open import Substrate.Algebra.F2
open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.Vector.Universal using (sum-F₂; sum-F₂-cong)
open import Substrate.Algebra.F2.SymBilinForm
  using (BilinForm; bilinear-form-of; metric-id;
         NonDegenerate; Radical; pair-eq-family)
open import Substrate.Algebra.F2.SymBilinForm.HodgeRecast
  using (metric-id-collapse)

open import Substrate.Category.Equalizer using (IsEqualised; equal)

------------------------------------------------------------------------
-- N-1: basis-row-eq-metric-id — the basis vector's lookup at j is
-- exactly metric-id i j.
--
-- Both `lookup (basis i) j` and `metric-id i j` are 𝟙 iff i=j, else 𝟘.
-- Proof by simultaneous induction on (i, j).
------------------------------------------------------------------------

basis-row-eq-metric-id :
  ∀ {n} (i j : Fin n) → lookup (basis i) j ≡ metric-id i j
basis-row-eq-metric-id zero    zero    = refl
basis-row-eq-metric-id zero    (suc j) = lookup-𝟎 j
basis-row-eq-metric-id (suc i) zero    = refl
basis-row-eq-metric-id (suc i) (suc j) = basis-row-eq-metric-id i j

------------------------------------------------------------------------
-- N-2: pair-metric-id-with-basis-generic — the universal extraction
-- lemma.
--
--   bilinear-form-of metric-id v (basis i) ≡ lookup v i
--
-- Path:
--   bf metric-id v (basis i)
-- = sum-F₂ (λ k → lookup v k · sum-F₂ (λ j → metric-id k j · lookup (basis i) j))  [definition]
-- = sum-F₂ (λ k → lookup v k · lookup (basis i) k)                                  [inner: metric-id-collapse k (basis i)]
-- = sum-F₂ (λ k → lookup v k · metric-id i k)                                       [basis-row-eq-metric-id i k]
-- = sum-F₂ (λ k → metric-id i k · lookup v k)                                       [·-comm]
-- = lookup v i                                                                       [metric-id-collapse i v]
------------------------------------------------------------------------

pair-metric-id-with-basis-generic :
  ∀ {n} (v : Vector n) (i : Fin n) →
  bilinear-form-of metric-id v (basis i) ≡ lookup v i
pair-metric-id-with-basis-generic {n} v i =
  trans
    -- Inner δ-collapse: sum-F₂ (λ j → metric-id k j · lookup (basis i) j) ≡ lookup (basis i) k
    (sum-F₂-cong {n} (λ k →
      cong (lookup v k ·_) (metric-id-collapse k (basis i))))
  (trans
    -- Replace lookup (basis i) k with metric-id i k.
    (sum-F₂-cong {n} (λ k →
      cong (lookup v k ·_) (basis-row-eq-metric-id i k)))
  (trans
    -- Swap factor order so metric-id is on the left.
    (sum-F₂-cong {n} (λ k →
      ·-comm (lookup v k) (metric-id i k)))
    -- Outer δ-collapse.
    (metric-id-collapse i v)))

------------------------------------------------------------------------
-- N-3: metric-id-non-degenerate-generic — the kernel-free witness at
-- any n.
--
-- If v is in the radical of metric-id (= for all w, the pairing is 𝟘),
-- specialise to w = basis i to extract `lookup v i ≡ 𝟘` for each i.
-- Conclude v ≡ 𝟎ⱽ by ≡-from-lookup.
------------------------------------------------------------------------

metric-id-non-degenerate-generic :
  ∀ {n} → NonDegenerate (metric-id {n})
metric-id-non-degenerate-generic {n} v in-radical = ≡-from-lookup v 𝟎ⱽ goal
  where
    -- lookup (𝟎ⱽ {n}) i reduces to 𝟘 by computation; no bridge needed.
    goal : (i : Fin n) → lookup v i ≡ lookup (𝟎ⱽ {n}) i
    goal i =
      trans (sym (pair-metric-id-with-basis-generic v i))
            (trans (equal (in-radical (basis i)))
                   (sym (lookup-𝟎 i)))

------------------------------------------------------------------------
-- N-4: Capstone — fixed-point reached for metric-id non-degeneracy.
--
-- After this slice, NonDegenerate metric-id at any n follows from one
-- universal proof. The substrate's existing
-- HodgeDim4.MetricGauge.NonDegenerate.metric-id-4-non-degenerate
-- (171 LoC for dim 4) becomes a one-liner instantiation modulo
-- SymBilinForm-4 ↔ SymBilinForm 4 bridge (deferred slice). At any
-- new n, `NonDegenerate (metric-id {n})` works immediately.
--
-- The pair-with-basis universal property
--   bilinear-form-of metric-id v (basis i) ≡ lookup v i
-- is also of independent interest: it's the categorical fact that
-- metric-id IS the Kronecker delta as a bilinear form. Useful for
-- any downstream slice that extracts components via bilinear pairing.
--
-- Per `feedback_categorical_name_first`: pair-metric-id-with-basis is
-- the universal property; metric-id-non-degenerate is its consequence
-- via the Wide-Meet / IsEqualised primitives. Both the universal
-- property and the consequence proven ONCE at generic n.
--
-- Deferred coalgebraic-unfolding follow-ons (continuing the chain):
--
--   * `is-symmetric-congruence-act` — congruence-act preserves
--     symmetry. Derivable from bilinearity (`bilinear-form-of-+ⱽ-{left,
--     right}`, `bilinear-form-of-*ₛ-{left, right}`) plus the symmetry
--     of the input bilinear form.
--
--   * `congruence-compose` — `congruence-act (T₁ ∘L T₂) M ≡
--     congruence-act T₂ (congruence-act T₁ M)`. Combined with
--     `FixedPoint-of-compose` from primitive #1, automates
--     StabiliserClosure-style cascades at any n.
--
--   * `bridges-dim-3-dim-4` — round-trip equivalences SymBilinForm-3
--     ↔ SymBilinForm 3 and SymBilinForm-4 ↔ SymBilinForm 4, demoting
--     existing per-dim proofs to corollaries.
------------------------------------------------------------------------
