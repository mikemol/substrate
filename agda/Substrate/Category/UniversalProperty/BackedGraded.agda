------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.BackedGraded — ⟡C2-param: the CARRIER-GENERIC (Set₀) backing.
--
-- THE REPLACEMENT for `Backed.BackedUP : Set₁`. The flat BackedUP fielded `arrow : UPArrow`
-- (Set₁, because UPArrow HELD its carriers `Source Target : Set` as fields) — the Set₁ the
-- mission dissolves. Here the backing is built on `UPArrowᴳ (Spec Sol : ℕ → Set)` (the graded
-- arrow, Category.UPArrowGraded): carriers are grade-indexed PARAMETERS (never fields), and the
-- proof-relevant Witness-span is the CONSTRUCTIVE `solve : {n} → Spec n → Sol n` (the map that
-- BUILDS the solution). So a `BackedUPᴳ Spec Sol` TERM inhabits Set₀ — registrations stop costing
-- Set₁ (the whole point). The heterogeneous registry / ⊗-ring is then a GRADED structure over the
-- carrier-grade (GradedProductOver / RigAlgebra), NOT a Set₁ Σ-bundle.
--
-- `Contentfulᴳ` is the graded non-vacuity: at some grade n there is a spec whose SOLUTION differs
-- from some candidate — the solve genuinely discriminates (a ⊤-collapse, Sol a singleton at every
-- grade, has none). `backedᴳ-non-vacuous` mirrors the flat `backed-non-vacuous`.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.BackedGraded where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.Foundation.Negation using (¬_)
open import Substrate.Foundation.Product using (Σ; _,_)
open import Substrate.Category.UPArrowGraded using (UPArrowᴳ; solve; mkUP)

------------------------------------------------------------------------
-- 1. Graded non-vacuity: some grade n has a spec s and a candidate t that is NOT its solution.
------------------------------------------------------------------------

Contentfulᴳ : {Spec Sol : ℕ → Set} → UPArrowᴳ Spec Sol → Set
Contentfulᴳ {Spec} {Sol} u = Σ ℕ (λ n → Σ (Spec n) (λ s → Σ (Sol n) (λ t → ¬ (t ≡ solve u s))))

-- the graded ⊤-collapse: the solve determines nothing to distinguish — every candidate is the
-- solution (Sol a singleton at every used grade). Contentfulᴳ says this is refused.
Vacuousᴳ : {Spec Sol : ℕ → Set} → UPArrowᴳ Spec Sol → Set
Vacuousᴳ {Spec} {Sol} u = {n : ℕ} (s : Spec n) (t : Sol n) → t ≡ solve u s

------------------------------------------------------------------------
-- 2. The Set₀ backing: the constructive universal arrow + its non-vacuity certificate.
------------------------------------------------------------------------

record BackedUPᴳ (Spec Sol : ℕ → Set) : Set where
  field
    arrowᴳ  : UPArrowᴳ Spec Sol
    content : Contentfulᴳ arrowᴳ

open BackedUPᴳ public

-- non-vacuity is FORCED by content (as in the flat layer): a backed graded UP cannot be the
-- ⊤-collapse — the discriminating candidate refutes universal agreement.
backedᴳ-non-vacuous : {Spec Sol : ℕ → Set} (b : BackedUPᴳ Spec Sol) → ¬ (Vacuousᴳ (arrowᴳ b))
backedᴳ-non-vacuous b vac with content b
... | (n , s , t , ¬eq) = ¬eq (vac s t)
