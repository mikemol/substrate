------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationUniversalOver
--
-- ⟡lift-generic + ⟡rig-UP-mul — the ADDITIVE and MULTIPLICATIVE universal maps of the
-- graded Lehmer rig, exhibited as the TWO INSTANCES of the ONE generic graded
-- homomorphism (OrientationBimonoidal.GradedHomOver). This is the recursion bottoming
-- out in an invariant rather than picking a side:
--
--   fold  (additive)        is a GradedHomOver ⊕-over Q _≡_    -- fold-⊕, catamorphism
--   lookup (multiplicative) is a GradedHomOver ⊗-over endo-over _≐_  -- ⊗-combine, a LOOKUP
--
-- The two fibres differ ONLY in the target equality (the GradedHomOver parameter):
--   * additive: the target carrier is DATA, so _≈_ = _≡_ (strict, funext-free);
--   * multiplicative: the target carrier is the Fin-endofunction Fin n → Fin n, so _≈_ is
--     POINTWISE equality _≐_ — the funext-free reading (Perm = Vec, lookup-extensional).
--
-- ⟡rig-UP-mul is a LOOKUP, not a derivation: `_⊗_` is DEFINED as `tabulate (λ k → combine
-- (lookup σ …) (lookup τ …))`, so `lookup (σ ⊗ τ) k` unfolds by lookup∘tabulate to exactly
-- the combine-product of the looked-up factors — the map-∧ law is `lookup∘tabulate` itself.
-- (Confirms the prior structural finding: ⊗ is NOT a ◂-catamorphism; its universal content
-- is the intertwining of ⊗ with combine under decode — the wreath action — and that is a
-- graded hom into endo-Fin, funext-free once the target equality is the pointwise one.)
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationUniversalOver where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_; _*_)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Inject using (inject+)
open import Substrate.Foundation.Fin.Combine using (combine)
open import Substrate.Foundation.Fin.RemQuot using (remQuot)
open import Substrate.Foundation.Vec using (Vec; lookup; tabulate)
open import Substrate.Foundation.Vec.Properties using (lookup∘tabulate)
open import Substrate.Foundation.Product using (proj₁; proj₂)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans)
open import Substrate.WitnessTower.Enumerate using (Perm)
open import Substrate.WitnessTower.LehmerPath using (LehmerPath; start; _◂_)
open import Substrate.WitnessTower.Wedge.OrientationUniversal
  using (LehmerAlgebra; base; step; fold; fold-⊕; fold-unique-over)
open import Substrate.WitnessTower.Wedge.OrientationProduct using (_⊗_; 1#)
open import Substrate.WitnessTower.Wedge.OrientationBimonoidal
  using (GradedProductOver; GradedHomOver; Endo; u; _∧_; map₀; map-u; map-∧)
open import Substrate.WitnessTower.Wedge.OrientationBimonoidal.Properties
  using (⊕-over; ⊗-over)

------------------------------------------------------------------------
-- 1. THE ADDITIVE INSTANCE — fold is a graded homomorphism into any target ⊕ᶜ-algebra Q
--    whose unit is the algebra's base and whose product mirrors ⊕'s recursion. Strict
--    (_≡_): the target carrier is data. map-u is (sym u≡base) [fold 0# = base
--    definitionally, 0# = start]; map-∧ IS fold-⊕. So the initial-algebra catamorphism
--    is a GradedHomOver — the additive half of the rig-functor universal property.
------------------------------------------------------------------------

fold-hom :
  {C : ℕ → Set} (alg : LehmerAlgebra C) (Q : GradedProductOver _+_ 0 C) →
  (u Q ≡ base alg) →
  (⊕ᶜ-base : ∀ {n} (y : C n) → (_∧_ Q (base alg) y) ≡ y) →
  (⊕ᶜ-step : ∀ {m n} (x : C m) (p : Fin (suc m)) (y : C n) →
             (_∧_ Q (step alg x p) y) ≡ step alg (_∧_ Q x y) (inject+ n p)) →
  GradedHomOver ⊕-over Q _≡_
fold-hom alg Q u≡base cb cs = record
  { map₀  = fold alg
  ; map-u = sym u≡base
  ; map-∧ = fold-⊕ alg (_∧_ Q) cb cs
  }

------------------------------------------------------------------------
-- 2. THE MULTIPLICATIVE INSTANCE (⟡rig-UP-mul) — lookup/decode is a graded homomorphism
--    from ⊗-over onto the combine-product of finite endofunctions, POINTWISE (_≐_).
------------------------------------------------------------------------

-- pointwise equality (the funext-free target equality; Fin-endofunctions are compared
-- index-by-index, exactly as Perm tables are via lookup-ext).
_≐_ : {n : ℕ} → Endo n → Endo n → Set
_≐_ {n} f g = (k : Fin n) → f k ≡ g k

-- endo-over: id at grade 1, and at grade i·j the combine-product that splits an index by
-- remQuot, acts by (f, g) on the two factors, and re-combines. This IS the pointwise skeleton
-- of _⊗_ (which tabulates exactly this function) — the carrier-hole filled with endofunctions.
endo-over : GradedProductOver _*_ 1 Endo
endo-over = record
  { u   = λ k → k
  ; _∧_ = λ {i} {j} f g k →
            combine (f (proj₁ (remQuot {i} j k))) (g (proj₂ (remQuot {i} j k)))
  }

-- lookup 1# ≐ id: Fin 1 has only `zero`, and lookup (zero ∷ []) zero = zero.
lookup-1#-id : lookup 1# ≐ u endo-over
lookup-1#-id zero = refl

-- lookup (σ ⊗ τ) ≐ (lookup σ ∧ lookup τ): pure lookup∘tabulate — _⊗_ tabulates precisely
-- the endo-over product of the looked-up factors, so the law is the tabulate round-trip.
lookup-⊗-combine : {i j : ℕ} (σ : Perm i) (τ : Perm j) →
                   lookup (_∧_ ⊗-over σ τ) ≐ _∧_ endo-over (lookup σ) (lookup τ)
lookup-⊗-combine σ τ k = lookup∘tabulate _ k

-- ⟡rig-UP-mul: decode is the multiplicative graded homomorphism.
lookup-hom : GradedHomOver ⊗-over endo-over _≐_
lookup-hom = record
  { map₀  = lookup
  ; map-u = lookup-1#-id
  ; map-∧ = lookup-⊗-combine
  }

------------------------------------------------------------------------
-- 3. ⟡fold-unique-over — THE INITIALITY REACHES THE POINTWISE SIDE TOO.
--
-- This module already carries the `_≡_` / `_≐_` split at the HOMOMORPHISM level:
-- §1's `fold-hom` lands at `_≡_`, while §2's `lookup-hom` MUST land at `_≐_`,
-- because `Endo n = Fin n → Fin n` is function-valued and `_≡_` on it needs
-- funext. The split reaches the INITIALITY identically — `fold-unique`
-- (OrientationUniversal) is ≡-stated, so it can conclude nothing about a
-- function-valued carrier — and it is closed the same way: by taking the target
-- equality as a parameter (`fold-unique-over`), exactly as `GradedHomOver`
-- relaxes `GradedDivStrMorphism`'s hardcoded `_≡_`.
--
-- The instance below is the NON-VACUITY POLE for that generalization: it is
-- stated at the REAL `Endo` carrier this module already uses, not a synthetic
-- one, so it witnesses a conclusion `fold-unique` cannot reach.
------------------------------------------------------------------------

-- transitivity is one of the two things the induction consumes (the other is the
-- step-congruence, supplied per-algebra below). Note `_≐_` is NOT assumed to be
-- an equivalence: no ≐-refl or ≐-sym is needed or defined here.
≐-trans : {n : ℕ} {x y z : Endo n} → x ≐ y → y ≐ z → x ≐ z
≐-trans p q k = trans (p k) (q k)

-- Initiality of the ordering tower at a FUNCTION-VALUED carrier, POINTWISE:
-- any g respecting (base, step) up to `_≐_` IS the fold, up to `_≐_`.
fold-unique-≐ :
  (alg : LehmerAlgebra Endo)
  (≐-step : {n : ℕ} {x y : Endo n} (p : Fin (suc n)) →
            x ≐ y → step alg x p ≐ step alg y p)
  (g : ∀ {n} → LehmerPath n → Endo n) →
  (g start ≐ base alg) →
  (∀ {n} (l : LehmerPath n) (p : Fin (suc n)) → g (l ◂ p) ≐ step alg (g l) p) →
  ∀ {n} (l : LehmerPath n) → g l ≐ fold alg l
fold-unique-≐ alg ≐-step = fold-unique-over _≐_ ≐-trans alg ≐-step
