------------------------------------------------------------------------
-- Substrate.Category.PrimeFactoredGauge
--
-- The unifying costructure: a GTorsor whose underlying group has a
-- SylowDecomposition. Together these give the universal-property
-- packaging of any gauge-freedom space whose symmetry group has a
-- known prime factorization with joint-generating Sylows.
--
-- The substrate's prior multi-route arc (closing the V₄-equivariance
-- question at GL(3, F₂)) becomes the FIRST INSTANCE; the Monster
-- (via Griess / ConjugationCoalgebra) becomes the canonical extreme
-- instance. Both are PrimeFactoredGauge values.
--
-- Per [[prime-factored-gauge-arc]]: T1 of the arc. With T0
-- (SylowDecomposition) + T1 in place, T5's generic multi-route
-- equivariance theorem can be stated as: "for any
-- PrimeFactoredGauge τ, between any two orbit points x, y ∈ X there
-- exists a Sylow-product gauge element taking x to y." The proof
-- chains GTorsor.transitive + SylowDecomposition.joint-generated.
--
-- Per [[expose-generator-not-orbit]]: this is the substrate-side
-- statement that gauge-freedom decomposes via Sylow generators, not
-- orbit enumeration.
--
-- Per [[multi-route-equivariance-recovery]]: this primitive names
-- the universal structure that the prior memo described
-- operationally; the operation (Sylow product, Sylow joint-
-- generation, Galois-conjugate switch) become structural moves
-- ON instances of this primitive.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.PrimeFactoredGauge where

open import Substrate.Foundation.Level using (Level; _⊔_) renaming (suc to lsuc)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Product using (Σ; _,_; proj₁; proj₂)

open import Substrate.Category.GTorsor using (GTorsor; act; transitive; free)
open import Substrate.Category.SylowDecomposition
  using (SylowDecomposition; primes; multiplicity;
         joint-generated; InGenerated)

------------------------------------------------------------------------
-- 1. PrimeFactoredGauge — the costructure.
--
-- Bundles:
--   * factorization : SylowDecomposition G with n distinct primes
--   * torsor        : GTorsor G X (with equivalences ≈G, ≈X)
--
-- The atlas-of-charts is IMPLICIT: each Sylow i provides a "chart"
-- by restricting the G-action to Sylow-i-elements. The G-equivariance
-- on X (full atlas) follows from:
--   1. The torsor's transitive: any (x, y) connects by some g ∈ G.
--   2. The factorization's joint-generated: g = product of Sylow
--      elements (InGenerated chain).
-- The chain IS the "extended-Euclid-style" decomposition through the
-- Sylow generation, naming the gauge element constructively.
--
-- T5 of the arc formalises this construction as a generic theorem
-- on any PrimeFactoredGauge instance.
------------------------------------------------------------------------

-- ⟡set1-rp-pfg: the record's lsuc was inherited SOLELY from its `factorization` field's type
-- (SylowDecomposition, whose Set-valued `Sylow` field is a param now) — thread the predicate as
-- a param here too and the level drops to the plain ⊔ (GTorsor never carried an lsuc).
record PrimeFactoredGauge
  {ℓG ℓX ℓEG ℓEX : Level}
  (G : Set ℓG) (X : Set ℓX)
  (_·G_ : G → G → G) (εG : G)
  (_≈G_ : G → G → Set ℓEG)
  (_≈X_ : X → X → Set ℓEX)
  (n : ℕ)
  (Sylow : Fin n → (G → Set ℓG)) : Set (ℓG ⊔ ℓX ⊔ ℓEG ⊔ ℓEX) where
  constructor mkPFG
  field
    factorization : SylowDecomposition G _·G_ εG n Sylow
    torsor        : GTorsor G X _·G_ εG _≈G_ _≈X_

open PrimeFactoredGauge public

------------------------------------------------------------------------
-- 2. Convenience accessors.
--
-- The atlas-of-charts is exposed via the SylowDecomposition's Sylow
-- predicates and the torsor's act function.
------------------------------------------------------------------------

-- The chart of Sylow-pᵢ: a restricted action where the acting group
-- element must satisfy the Sylow-i predicate. Just the torsor's act
-- with a membership-witness requirement.
chart-of-Sylow :
  {ℓG ℓX ℓEG ℓEX : Level}
  {G : Set ℓG} {X : Set ℓX}
  {_·G_ : G → G → G} {εG : G}
  {_≈G_ : G → G → Set ℓEG} {_≈X_ : X → X → Set ℓEX}
  {n : ℕ} {Sylow : Fin n → (G → Set ℓG)}
  (τ : PrimeFactoredGauge G X _·G_ εG _≈G_ _≈X_ n Sylow) →
  (i : Fin n) →
  (g : G) → Sylow i g → X → X
chart-of-Sylow τ i g _ = act (torsor τ) g

------------------------------------------------------------------------
-- 3. The atlas-witness: every orbit-point pair is connected by a
-- chain of Sylow elements.
--
-- This is the LOAD-BEARING fact that T5's generic theorem will
-- consume. Stated here as a derived property from the GTorsor +
-- SylowDecomposition fields.
--
-- Construction:
--   1. transitive τ gives the unique g ∈ G with act g x = y.
--   2. joint-generated τ g gives an InGenerated chain proving g lies
--      in the subgroup generated by ⋃ Sylow.
-- The chain IS the atlas-of-charts decomposition.
------------------------------------------------------------------------

atlas-decomposition :
  {ℓG ℓX ℓEG ℓEX : Level}
  {G : Set ℓG} {X : Set ℓX}
  {_·G_ : G → G → G} {εG : G}
  {_≈G_ : G → G → Set ℓEG} {_≈X_ : X → X → Set ℓEX}
  {n : ℕ} {Sylow : Fin n → (G → Set ℓG)}
  (τ : PrimeFactoredGauge G X _·G_ εG _≈G_ _≈X_ n Sylow) →
  (x y : X) →
  Σ G (λ g →
    Σ (_≈X_ (act (torsor τ) g x) y) (λ _ →
      InGenerated (λ z → Σ (Fin n) (λ i → Sylow i z))
                  _·G_ εG g))
atlas-decomposition τ x y =
  let (g , eq) = transitive (torsor τ) x y
      chain    = joint-generated (factorization τ) g
  in (g , (eq , chain))

------------------------------------------------------------------------
-- 4. Capstone — the costructure in place.
--
-- T1 of the prime-factored-gauge arc per
-- [[prime-factored-gauge-arc]]. With T0 (SylowDecomposition) + T1
-- (this) landed, the foundation for the generic multi-route
-- equivariance is complete.
--
-- Instances expected (T6, T7, T8 of the arc):
--   * GL(3, F₂) acting on the Reserved↔SelfDual bridge space
--     (HodgeDim4 GaugeTorsor — closes [[reserved-selfdual-bijection-
--     gauge]] structurally).
--   * Abelian Z/(p₁...pₙ) acting on its own coset space (CRT case,
--     joint-generation trivial because Sylows are normal).
--   * Monster M acting on V♮ (the Moonshine VOA — the canonical
--     extreme instance). Joint-generation cited from CFSG.
--
-- The atlas-decomposition function above IS the substrate-side
-- formalisation of "extended Euclid for groups" — given any two
-- orbit points, construct the Sylow-product gauge element.
--
-- Per [[shadow-architecture]]: T0 + T1 are DBE-foundational; the
-- remaining T2-T4 (PresentedGroup, ConjugationCoalgebra,
-- GaloisAdjunction) deliver the bottom-up/top-down machinery for
-- T8's Monster instance.
------------------------------------------------------------------------
