------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationUniversal
--
-- ⟡rig-UP (the Set₀ core) — the UNIVERSAL PROPERTY of the free ordering tower, done the way
-- we discussed: NOT the Σ ℕ / Set₁ collapse (which is exactly what blocks the existing
-- FreeUP/UPArrow — "UPArrow.Source : Set can't hold the graded thing"), NOT a new
-- 2-categorical framework. It is the TWO-WITNESS-TOWERS-MEET: the free tower and any target
-- tower meet at each rung, and the higher-order witness recording the meet is Set₀ — the
-- SAME construction as OrientationFixedPoint's decode-injective (the μΦ≅νΦ pairing-witness),
-- and the same as combining the generators into a tuple and witnessing their synchronized
-- action through the tower growth (FourPointReflection's wordAct-hom is the free monoid hom).
--
-- Concretely: LehmerPath IS the initial algebra μΦ of the tower functor. Its universal
-- property is the unique FOLD (catamorphism) into any graded LehmerAlgebra, with uniqueness
-- by LehmerPath induction — grade-by-grade, each grade Set₀.
--
--   fold        : LehmerAlgebra C → LehmerPath n → C n          -- THE unique structure-map
--   fold-unique : any g respecting (base, step) IS the fold     -- the Set₀ meet-witness
--
-- So the tower is the free/initial structure on its generators, formalized at Set₀. (The full
-- symmetric-RIG-functor UP layers the ⊕/⊗ operations on top of this initial-algebra UP.)
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationUniversal where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Inject using (inject+)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong)
open import Substrate.WitnessTower.LehmerPath using (LehmerPath; start; _◂_)
open import Substrate.WitnessTower.Wedge.OrientationSum using (_⊕_)

------------------------------------------------------------------------
-- 1. A LehmerAlgebra: a graded target (C : ℕ → Set, each grade Set₀) carrying the tower
--    functor's structure — a grade-0 base and a rung-step (the ◂ / insert operation).
------------------------------------------------------------------------

record LehmerAlgebra (C : ℕ → Set) : Set where
  field
    base : C 0
    step : ∀ {n} → C n → Fin (suc n) → C (suc n)

open LehmerAlgebra public

------------------------------------------------------------------------
-- 2. THE FOLD (catamorphism): the structure-map out of the initial algebra LehmerPath.
------------------------------------------------------------------------

fold : ∀ {C} → LehmerAlgebra C → ∀ {n} → LehmerPath n → C n
fold alg start    = base alg
fold alg (l ◂ p)  = step alg (fold alg l) p

------------------------------------------------------------------------
-- 3. UNIVERSALITY: any map g that respects the algebra structure IS the fold. The proof is
--    the two-tower-meet witnessed grade-by-grade (LehmerPath induction) — the Set₀
--    higher-order witness, structurally identical to OrientationFixedPoint's decode-injective.
--
-- ⚑ THE TARGET EQUALITY IS A PARAMETER (⟡fold-unique-over). `fold-unique` below is stated at
-- `_≡_`, and for a Set₀ point-carrier that is the right and only equality. But a
-- FUNCTION-VALUED carrier (C n = Fin (n * n) → A, the flat matrix; or `Endo n = Fin n → Fin n`,
-- OrientationBimonoidal:102) has no useful `_≡_` without funext — its consumers already work at
-- the POINTWISE equality instead (`_≐_`, "the funext-free target equality",
-- OrientationUniversalOver:76; `lookup-hom : GradedHomOver ⊗-over endo-over _≐_`). So the
-- uniqueness must be stated over the equality too, exactly as `GradedHomOver` relaxes
-- `GradedDivStrMorphism`'s hardcoded `_≡_` one layer down (OrientationBimonoidal:59-68). It is
-- the SAME relaxation applied to the initiality rather than to the morphism.
--
-- ⚑ WHAT `_≈_` MUST SATISFY — AND WHAT IT NEED NOT. The induction consumes exactly two things:
-- TRANSITIVITY (to chain the step hypothesis with the recursive call) and STEP-CONGRUENCE (to
-- push the recursive equality under `step alg _ p`). It needs NEITHER reflexivity NOR symmetry,
-- so `_≈_` need not be an equivalence — a preorder congruent for `step` suffices. Stating the
-- requirement exactly (rather than demanding an equivalence for tidiness) is the same
-- discipline `GradedHomOver` records at :61-62.
--
-- `fold-unique` is then this theorem's `_≡_` INSTANCE, not a parallel proof — so the ~12
-- existing call sites are unchanged, and the two readings are identified by construction
-- rather than asserted in prose.
------------------------------------------------------------------------

fold-unique-over :
  ∀ {C : ℕ → Set}
    (_≈_ : {n : ℕ} → C n → C n → Set)
    (≈-trans : {n : ℕ} {x y z : C n} → x ≈ y → y ≈ z → x ≈ z)
    (alg : LehmerAlgebra C)
    (≈-step : {n : ℕ} {x y : C n} (p : Fin (suc n)) → x ≈ y →
              step alg x p ≈ step alg y p)
    (g : ∀ {n} → LehmerPath n → C n) →
    (g start ≈ base alg) →
    (∀ {n} (l : LehmerPath n) (p : Fin (suc n)) → g (l ◂ p) ≈ step alg (g l) p) →
    ∀ {n} (l : LehmerPath n) → g l ≈ fold alg l
fold-unique-over _≈_ ≈-trans alg ≈-step g g-base g-step start   = g-base
fold-unique-over _≈_ ≈-trans alg ≈-step g g-base g-step (l ◂ p) =
  ≈-trans (g-step l p)
          (≈-step p (fold-unique-over _≈_ ≈-trans alg ≈-step g g-base g-step l))

-- the `_≡_` instance — the original statement, now DERIVED (the co-apex identification).
fold-unique : ∀ {C} (alg : LehmerAlgebra C) (g : ∀ {n} → LehmerPath n → C n) →
              (g start ≡ base alg) →
              (∀ {n} (l : LehmerPath n) (p : Fin (suc n)) → g (l ◂ p) ≡ step alg (g l) p) →
              ∀ {n} (l : LehmerPath n) → g l ≡ fold alg l
fold-unique alg =
  fold-unique-over _≡_ trans alg (λ p e → cong (λ z → step alg z p) e)

------------------------------------------------------------------------
-- 4. THE FOLD IS A ⊕-HOMOMORPHISM (the additive half of the rig-functor UP). If the target
--    carries a ⊕ᶜ that mirrors ⊕'s recursion on the (base, step) structure — `⊕ᶜ base y = y`
--    (start ⊕ l = l) and `⊕ᶜ (step x p) y = step (⊕ᶜ x y) (inject+ p)` ((l◂p) ⊕ l₂) — then
--    fold preserves ⊕, by LehmerPath induction. So the unique catamorphism is an additive
--    homomorphism: the free structure maps to any ⊕-compatible target respecting ⊕.
------------------------------------------------------------------------

fold-⊕ : ∀ {C} (alg : LehmerAlgebra C)
         (_⊕ᶜ_ : ∀ {i j} → C i → C j → C (i + j))
         (⊕ᶜ-base : ∀ {n} (y : C n) → (base alg ⊕ᶜ y) ≡ y)
         (⊕ᶜ-step : ∀ {m n} (x : C m) (p : Fin (suc m)) (y : C n) →
                    (step alg x p ⊕ᶜ y) ≡ step alg (x ⊕ᶜ y) (inject+ n p)) →
         ∀ {m n} (l₁ : LehmerPath m) (l₂ : LehmerPath n) →
         fold alg (l₁ ⊕ l₂) ≡ (fold alg l₁ ⊕ᶜ fold alg l₂)
fold-⊕ alg _⊕ᶜ_ cb cs start    l₂ = sym (cb (fold alg l₂))
fold-⊕ alg _⊕ᶜ_ cb cs (l₁ ◂ p) l₂ =
  trans (cong (λ z → step alg z (inject+ _ p)) (fold-⊕ alg _⊕ᶜ_ cb cs l₁ l₂))
        (sym (cs (fold alg l₁) p (fold alg l₂)))
