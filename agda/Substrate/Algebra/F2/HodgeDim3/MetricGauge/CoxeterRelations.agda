------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations
--
-- Verifies the Coxeter relations for the S₃ presentation ⟨ s₁, s₂ |
-- s₁² = s₂² = (s₁s₂)³ = e ⟩ at the Linear 3 3 representation.
--
-- All three relations are stated as apply-equalities (pointwise on
-- vectors via linear-extensionality); full Linear-equality would
-- require function extensionality, which the substrate avoids.
--
--   * s₁²-on-v       : (v) → apply (s₁ ∘L s₁) v ≡ apply id-L v
--   * s₂²-on-v       : (v) → apply (s₂ ∘L s₂) v ≡ apply id-L v
--   * braid-on-v     : (v) → apply (s₁ ∘L s₂ ∘L s₁) v ≡
--                            apply (s₂ ∘L s₁ ∘L s₂) v
--
-- Each is proved via linear-extensionality + 3 basis-vector
-- evaluations using the s₁-on-eᵢ / s₂-on-eᵢ helpers from Stabiliser.agda.
--
-- The braid relation `s₁ ∘L s₂ ∘L s₁ ≡ s₂ ∘L s₁ ∘L s₂` (the third
-- Coxeter relation, equivalent to (s₁s₂)³ = e since each sᵢ is
-- involutive) is the structural fact that the two "swap-(0, 2)"
-- representatives in StabiliserClosure's 6-element witness list are
-- the SAME linear map. After this slice the witness count collapses
-- from 6 (with two equal representatives) to 5 distinct elements,
-- matching the order |S₃| = 6 minus the identity.
--
-- Per `feedback_v4_typeclass_architecture`: small finitely-presented
-- groups go through the Coxeter framework. Verifying the Coxeter
-- relations holds at the concrete Linear 3 3 representation is the
-- bridge between the Linear stabiliser and the abstract group
-- presentation.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations where

open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Vec using ([]; _∷_)
open import Substrate.Foundation.Eq
  using (_≡_; refl; sym; trans; cong)

open import Substrate.Algebra.F2
open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.Linear
open import Substrate.Algebra.F2.Linear.Universal using (linear-extensionality)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.Stabiliser
  using (s₁; s₂;
         s₁-on-e₀; s₁-on-e₁; s₁-on-e₂;
         s₂-on-e₀; s₂-on-e₁; s₂-on-e₂)

------------------------------------------------------------------------
-- N-1: s₁² = e (involution).
--
-- For each basis vector eᵢ:
--   apply (s₁ ∘L s₁) eᵢ ≡ apply s₁ (apply s₁ eᵢ)   [definition of ∘L]
--                       ≡ apply s₁ (sᵢ-image)        [s₁-on-eᵢ]
--                       ≡ eᵢ                          [s₁ swaps back]
-- where s₁-image of e₀ is e₁, of e₁ is e₀, of e₂ is e₂.
------------------------------------------------------------------------

-- Per-basis: s₁ ∘L s₁ acts as identity.
s₁²-on-e₀ : apply (s₁ ∘L s₁) (basis zero) ≡ basis zero
s₁²-on-e₀ = trans (cong (apply s₁) s₁-on-e₀) s₁-on-e₁

s₁²-on-e₁ : apply (s₁ ∘L s₁) (basis (suc zero)) ≡ basis (suc zero)
s₁²-on-e₁ = trans (cong (apply s₁) s₁-on-e₁) s₁-on-e₀

s₁²-on-e₂ : apply (s₁ ∘L s₁) (basis (suc (suc zero))) ≡ basis (suc (suc zero))
s₁²-on-e₂ = trans (cong (apply s₁) s₁-on-e₂) s₁-on-e₂

-- Pointwise: s₁ ∘L s₁ agrees with id-L on every v.
s₁²-on-v : (v : Vector 3) → apply (s₁ ∘L s₁) v ≡ apply id-L v
s₁²-on-v = linear-extensionality (s₁ ∘L s₁) id-L agree-on-basis
  where
    agree-on-basis : (i : Fin 3) →
                     apply (s₁ ∘L s₁) (basis i) ≡ apply id-L (basis i)
    agree-on-basis zero             = s₁²-on-e₀
    agree-on-basis (suc zero)       = s₁²-on-e₁
    agree-on-basis (suc (suc zero)) = s₁²-on-e₂

------------------------------------------------------------------------
-- N-2: s₂² = e (involution).
--
-- Same template as N-1, swapping s₁ ↔ s₂. s₂ acts:
--   e₀ ↦ e₀ (fixed)
--   e₁ ↦ e₂
--   e₂ ↦ e₁
------------------------------------------------------------------------

s₂²-on-e₀ : apply (s₂ ∘L s₂) (basis zero) ≡ basis zero
s₂²-on-e₀ = trans (cong (apply s₂) s₂-on-e₀) s₂-on-e₀

s₂²-on-e₁ : apply (s₂ ∘L s₂) (basis (suc zero)) ≡ basis (suc zero)
s₂²-on-e₁ = trans (cong (apply s₂) s₂-on-e₁) s₂-on-e₂

s₂²-on-e₂ : apply (s₂ ∘L s₂) (basis (suc (suc zero))) ≡ basis (suc (suc zero))
s₂²-on-e₂ = trans (cong (apply s₂) s₂-on-e₂) s₂-on-e₁

s₂²-on-v : (v : Vector 3) → apply (s₂ ∘L s₂) v ≡ apply id-L v
s₂²-on-v = linear-extensionality (s₂ ∘L s₂) id-L agree-on-basis
  where
    agree-on-basis : (i : Fin 3) →
                     apply (s₂ ∘L s₂) (basis i) ≡ apply id-L (basis i)
    agree-on-basis zero             = s₂²-on-e₀
    agree-on-basis (suc zero)       = s₂²-on-e₁
    agree-on-basis (suc (suc zero)) = s₂²-on-e₂

------------------------------------------------------------------------
-- N-3: Braid relation s₁ ∘L s₂ ∘L s₁ ≡ s₂ ∘L s₁ ∘L s₂.
--
-- Equivalent to (s₁s₂)³ = e since each sᵢ is involutive:
--   (s₁s₂)³ = e
--   ⟹ (s₁s₂)² = (s₁s₂)⁻¹ = s₂s₁ (each sᵢ self-inverse)
--   ⟹ s₁s₂s₁s₂ = s₂s₁
--   ⟹ s₁s₂s₁ = s₂s₁s₂   (multiply right by s₂)
--
-- Both compositions act as the swap (0, 2) on basis vectors:
--   e₀ → e₂, e₁ fixed, e₂ → e₀.
--
-- For each basis vector:
--   s₁s₂s₁ e₀ = s₁(s₂(s₁ e₀)) = s₁(s₂ e₁) = s₁ e₂ = e₂
--   s₂s₁s₂ e₀ = s₂(s₁(s₂ e₀)) = s₂(s₁ e₀) = s₂ e₁ = e₂   ✓
--   s₁s₂s₁ e₁ = s₁(s₂(s₁ e₁)) = s₁(s₂ e₀) = s₁ e₀ = e₁
--   s₂s₁s₂ e₁ = s₂(s₁(s₂ e₁)) = s₂(s₁ e₂) = s₂ e₂ = e₁   ✓
--   s₁s₂s₁ e₂ = s₁(s₂(s₁ e₂)) = s₁(s₂ e₂) = s₁ e₁ = e₀
--   s₂s₁s₂ e₂ = s₂(s₁(s₂ e₂)) = s₂(s₁ e₁) = s₂ e₀ = e₀   ✓
--
-- Reflexive on (0, 1, 0) for e₁, on (1, 0, 0) for e₂ → e₀, on
-- (0, 0, 1) for e₀ → e₂. Each LHS and RHS chain of `apply` reduces
-- to the same final basis vector.
--
-- Both sides parse as right-associated by infixr 9 _∘L_:
--   s₁ ∘L s₂ ∘L s₁ = s₁ ∘L (s₂ ∘L s₁)
--   s₂ ∘L s₁ ∘L s₂ = s₂ ∘L (s₁ ∘L s₂)
-- So apply (s₁ ∘L (s₂ ∘L s₁)) v = apply s₁ (apply (s₂ ∘L s₁) v)
--                                = apply s₁ (apply s₂ (apply s₁ v)).
------------------------------------------------------------------------

braid-on-e₀ :
  apply (s₁ ∘L s₂ ∘L s₁) (basis zero)
    ≡ apply (s₂ ∘L s₁ ∘L s₂) (basis zero)
braid-on-e₀ =
  trans (cong (apply s₁) (cong (apply s₂) s₁-on-e₀))
  (trans (cong (apply s₁) s₂-on-e₁)
  (trans s₁-on-e₂
  (trans (sym s₂-on-e₁)
  (trans (cong (apply s₂) (sym s₁-on-e₀))
         (cong (apply s₂) (cong (apply s₁) (sym s₂-on-e₀)))))))

braid-on-e₁ :
  apply (s₁ ∘L s₂ ∘L s₁) (basis (suc zero))
    ≡ apply (s₂ ∘L s₁ ∘L s₂) (basis (suc zero))
braid-on-e₁ =
  trans (cong (apply s₁) (cong (apply s₂) s₁-on-e₁))
  (trans (cong (apply s₁) s₂-on-e₀)
  (trans s₁-on-e₀
  (trans (sym s₂-on-e₂)
  (trans (cong (apply s₂) (sym s₁-on-e₂))
         (cong (apply s₂) (cong (apply s₁) (sym s₂-on-e₁)))))))

braid-on-e₂ :
  apply (s₁ ∘L s₂ ∘L s₁) (basis (suc (suc zero)))
    ≡ apply (s₂ ∘L s₁ ∘L s₂) (basis (suc (suc zero)))
braid-on-e₂ =
  trans (cong (apply s₁) (cong (apply s₂) s₁-on-e₂))
  (trans (cong (apply s₁) s₂-on-e₂)
  (trans s₁-on-e₁
  (trans (sym s₂-on-e₀)
  (trans (cong (apply s₂) (sym s₁-on-e₁))
         (cong (apply s₂) (cong (apply s₁) (sym s₂-on-e₂)))))))

-- Pointwise via linear-extensionality.
braid-on-v :
  (v : Vector 3) →
  apply (s₁ ∘L s₂ ∘L s₁) v ≡ apply (s₂ ∘L s₁ ∘L s₂) v
braid-on-v =
  linear-extensionality (s₁ ∘L s₂ ∘L s₁) (s₂ ∘L s₁ ∘L s₂) agree-on-basis
  where
    agree-on-basis : (i : Fin 3) →
                     apply (s₁ ∘L s₂ ∘L s₁) (basis i)
                       ≡ apply (s₂ ∘L s₁ ∘L s₂) (basis i)
    agree-on-basis zero             = braid-on-e₀
    agree-on-basis (suc zero)       = braid-on-e₁
    agree-on-basis (suc (suc zero)) = braid-on-e₂

------------------------------------------------------------------------
-- N-4: Retrofit — Coxeter relations as HasOrder instances.
--
-- Connects this file to Substrate.Category.Coalgebra.FiniteOrder
-- (primitive #1's HasOrder predicate). The involutions s₁² = s₂² = id
-- become HasOrder ★ 2 instances; the braid (s₁s₂)³ = e becomes a
-- HasOrder ★ 3 instance.
--
-- The HasOrder instances are derived directly from the apply-pointwise
-- relations above (no funext required). iterate 2 (apply sᵢ) v
-- reduces definitionally to apply (sᵢ ∘L sᵢ) v; apply id-L v reduces
-- to v. So `sᵢ²-on-v v : apply (sᵢ ∘L sᵢ) v ≡ apply id-L v` IS
-- `iterate 2 (apply sᵢ) v ≡ v` = HasOrder (apply sᵢ) 2 at v.
--
-- Per `feedback_categorical_name_first` and the [[project-torsion-
-- element-universal]] / [[project-composite-torsion-euler-substrate]]
-- discipline: the s₁²/s₂² involutions and the (s₁s₂)³ = e braid are
-- concrete instances of the substrate's torsion-element-of-automorphism
-- universal. Naming them as HasOrder retrofits surfaces the categorical
-- handle.
------------------------------------------------------------------------

open import Substrate.Category.Coalgebra using (Endomap)
open import Substrate.Category.Coalgebra.FiniteOrder
  using (HasOrder; iterate)

-- s₁ as an endomap of Vector 3.
s₁-endo : Endomap (Vector 3)
s₁-endo = apply s₁

-- s₂ as an endomap of Vector 3.
s₂-endo : Endomap (Vector 3)
s₂-endo = apply s₂

-- s₁∘L s₂ as an endomap.
s₁∘s₂-endo : Endomap (Vector 3)
s₁∘s₂-endo = apply (s₁ ∘L s₂)

-- HasOrder retrofits — involutions.
HasOrder-s₁ : HasOrder s₁-endo 2
HasOrder-s₁ = s₁²-on-v

HasOrder-s₂ : HasOrder s₂-endo 2
HasOrder-s₂ = s₂²-on-v

-- HasOrder retrofit — the 3-cycle s₁∘s₂.
-- (s₁s₂)³ = e in S₃; iterate 3 (apply (s₁∘L s₂)) v ≡ v for any v.
-- Proved per-basis using s₁-on-eᵢ + s₂-on-eᵢ chained 3 times, then
-- lifted to all v via linear-extensionality.

s₁∘s₂-cubed-on-e₀ :
  apply ((s₁ ∘L s₂) ∘L (s₁ ∘L s₂) ∘L (s₁ ∘L s₂)) (basis zero)
    ≡ apply id-L (basis zero)
s₁∘s₂-cubed-on-e₀ =
  -- (s₁s₂)³ e₀: e₀ ↦ s₂ e₀ = e₀ ↦ s₁ e₀ = e₁ (first s₁s₂)
  --              e₁ ↦ s₂ e₁ = e₂ ↦ s₁ e₂ = e₂ (second s₁s₂)
  --              e₂ ↦ s₂ e₂ = e₁ ↦ s₁ e₁ = e₀ (third s₁s₂) ✓
  trans (cong (apply (s₁ ∘L s₂)) (cong (apply (s₁ ∘L s₂))
              (cong (apply s₁) s₂-on-e₀)))
  (trans (cong (apply (s₁ ∘L s₂)) (cong (apply (s₁ ∘L s₂)) s₁-on-e₀))
  (trans (cong (apply (s₁ ∘L s₂)) (cong (apply s₁) s₂-on-e₁))
  (trans (cong (apply (s₁ ∘L s₂)) s₁-on-e₂)
  (trans (cong (apply s₁) s₂-on-e₂)
         s₁-on-e₁))))

s₁∘s₂-cubed-on-e₁ :
  apply ((s₁ ∘L s₂) ∘L (s₁ ∘L s₂) ∘L (s₁ ∘L s₂)) (basis (suc zero))
    ≡ apply id-L (basis (suc zero))
s₁∘s₂-cubed-on-e₁ =
  -- (s₁s₂)³ e₁: e₁ ↦ s₂ e₁ = e₂ ↦ s₁ e₂ = e₂ (first)
  --              e₂ ↦ s₂ e₂ = e₁ ↦ s₁ e₁ = e₀ (second)
  --              e₀ ↦ s₂ e₀ = e₀ ↦ s₁ e₀ = e₁ (third) ✓
  trans (cong (apply (s₁ ∘L s₂)) (cong (apply (s₁ ∘L s₂))
              (cong (apply s₁) s₂-on-e₁)))
  (trans (cong (apply (s₁ ∘L s₂)) (cong (apply (s₁ ∘L s₂)) s₁-on-e₂))
  (trans (cong (apply (s₁ ∘L s₂)) (cong (apply s₁) s₂-on-e₂))
  (trans (cong (apply (s₁ ∘L s₂)) s₁-on-e₁)
  (trans (cong (apply s₁) s₂-on-e₀)
         s₁-on-e₀))))

s₁∘s₂-cubed-on-e₂ :
  apply ((s₁ ∘L s₂) ∘L (s₁ ∘L s₂) ∘L (s₁ ∘L s₂)) (basis (suc (suc zero)))
    ≡ apply id-L (basis (suc (suc zero)))
s₁∘s₂-cubed-on-e₂ =
  -- (s₁s₂)³ e₂: e₂ ↦ s₂ e₂ = e₁ ↦ s₁ e₁ = e₀ (first)
  --              e₀ ↦ s₂ e₀ = e₀ ↦ s₁ e₀ = e₁ (second)
  --              e₁ ↦ s₂ e₁ = e₂ ↦ s₁ e₂ = e₂ (third) ✓
  trans (cong (apply (s₁ ∘L s₂)) (cong (apply (s₁ ∘L s₂))
              (cong (apply s₁) s₂-on-e₂)))
  (trans (cong (apply (s₁ ∘L s₂)) (cong (apply (s₁ ∘L s₂)) s₁-on-e₁))
  (trans (cong (apply (s₁ ∘L s₂)) (cong (apply s₁) s₂-on-e₀))
  (trans (cong (apply (s₁ ∘L s₂)) s₁-on-e₀)
  (trans (cong (apply s₁) s₂-on-e₁)
         s₁-on-e₂))))

-- HasOrder (apply (s₁∘L s₂)) 3 via linear-extensionality.
HasOrder-s₁∘s₂ : HasOrder s₁∘s₂-endo 3
HasOrder-s₁∘s₂ v =
  linear-extensionality
    ((s₁ ∘L s₂) ∘L (s₁ ∘L s₂) ∘L (s₁ ∘L s₂))
    id-L
    agree-on-basis
    v
  where
    agree-on-basis : (i : Fin 3) →
                     apply ((s₁ ∘L s₂) ∘L (s₁ ∘L s₂) ∘L (s₁ ∘L s₂)) (basis i)
                       ≡ apply id-L (basis i)
    agree-on-basis zero             = s₁∘s₂-cubed-on-e₀
    agree-on-basis (suc zero)       = s₁∘s₂-cubed-on-e₁
    agree-on-basis (suc (suc zero)) = s₁∘s₂-cubed-on-e₂

------------------------------------------------------------------------
-- N-4: Capstone documentation.
--
-- The Coxeter presentation ⟨ s₁, s₂ | s₁² = s₂² = (s₁s₂)³ = e ⟩ for
-- S₃ is now verified at the Linear 3 3 representation (modulo
-- function-extensionality — relations are stated as pointwise
-- apply-equalities, not Linear-equalities).
--
-- Structural consequences:
--
--   * StabiliserClosure's `s₁∘s₂∘s₁-stabilises-metric-id` and
--     `s₂∘s₁∘s₂-stabilises-metric-id` witness the SAME element of
--     the stabiliser subgroup (modulo `braid-on-v` extending to
--     full Linear-equality, which would need funext).
--
--   * The 6-element S₃ stabiliser of metric-id collapses to 5
--     distinct Linear maps once the braid identification is taken
--     as Linear-equality. Without funext, this remains 6 witnesses
--     with two of them apply-equal.
--
--   * This is the bridge between the concrete Linear 3 3 stabiliser
--     and the abstract Coxeter S₃ presentation. Combined with the
--     stabiliser FixedPoint witnesses in
--     {Stabiliser, StabiliserClosure}.agda, the substrate has both
--     the algebraic (Coxeter) and the action-theoretic (FixedPoint
--     under congruence-act) characterisations of the stabiliser.
--
-- Per `feedback_v4_typeclass_architecture`: small finitely-presented
-- groups go through the Coxeter framework. Verifying the relations
-- at the Linear representation is exactly the substrate's bridge
-- from concrete-representation to abstract-presentation.
--
-- Deferred follow-ons:
--
--   * **Linear-equality version**: lift `s₁²-on-v`, `s₂²-on-v`,
--     `braid-on-v` to `s₁ ∘L s₁ ≡ id-L` etc., requires
--     function-extensionality (`apply L ≡ apply M` from pointwise)
--     + record-equality of Linear (UIP on linearity proofs). The
--     substrate avoids funext; this lift would require a justified
--     funext usage or a different formulation.
--
--   * **bridge-to-Substrate.Groups.S3**: connect this concrete
--     verification to the abstract S₃ presented in the Coxeter
--     framework via Substrate.Groups.S3.
------------------------------------------------------------------------
