------------------------------------------------------------------------
-- Substrate.Category.Allegory.Refinement  (ALG-7)
--
-- The Φ-FLOOR and its fusion to the wedge.  The recursion's bottom is ONE
-- monotone operator `Φ` on fiber families `Fam A = A → Set`; the allegory
-- (ALG-0..6) is Φ's arrows-and-composition, a map is the singleton-fiber
-- readout (ALG-5), and the wedge's uniqueness certificate is that readout.
--
-- PROVEN HERE (--safe --without-K):
--   * `Refinement A` — a monotone operator Φ on fiber families, with a FRESH
--     family-preorder `_⊑ᶠ_` (the repo's `ShadowArchitecture.Persistence._⊑_`
--     orders cotypes, NOT families — it is the WRONG order for Φ).
--   * `iterate` (Rⁿ = Φⁿ R⁰) + `chain` (from a pre-fixed-point, the iterate
--     DESCENDS: Rⁿ⁺¹ ⊑ᶠ Rⁿ — "inhabitants only shrink", grade n = pruning depth).
--   * `isSingleton` — the map/relation readout (μΦ a singleton ⟺ a map, ALG-5).
--   * `bounded-wedge-det` — THE FUSION: the bounded ℕ-wedge decomposition is
--     `deterministic` (ALG-5), proven directly from `recon-bounded-unique`
--     (`Algebra/Wedge/BoundedIso`).  The wedge's uniqueness certificate IS
--     allegory determinism = a singleton fiber = a map.  Now a checked theorem.
--
-- IDENTIFIED, NOT YET PROVEN (honest deferrals — the LARGE remainder):
--   * `Trace` (inductive, `Algebra/Wedge.agda`) = μΦ; `RealTrace` (coinductive
--     `--guardedness`, `Algebra/R/Trace.agda`) = νΦ.  Both EXIST as repo objects
--     and are the two fixed-point endpoints; proving `Trace ≅ μ` of a specific Φ
--     (and `RealTrace ≅ ν`) is a further obligation.
--   * `CertifiedWedge.small` (`measure (rem) < measure b`) is the well-founded
--     measure that drives `chain`; wiring it to a concrete `Refinement` is next.
--   * NOTE the recon flagged a FALSE shortcut: `GradedDivStr.R` is NOT itself a
--     Φ-iterate (its instances `vec-graded R n = A`, `tower-graded R n = Fin(suc n)`
--     are fixed/non-shrinking).  `GradedDivStr.R` is the fiber-family SHAPE Φ acts
--     on; the iterate lives on a Φ built from the wedge STEP, not on raw `R`.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Allegory.Refinement where

open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong₂)
open import Substrate.Foundation.Product using (Σ; _,_; _×_; proj₁; proj₂)
open import Substrate.Foundation.Nat using (ℕ; zero; suc; _<_)
open import Substrate.Algebra.Wedge using (recon; ℕ-div)
open import Substrate.Algebra.Wedge.BoundedIso using (recon-bounded-unique)
open import Substrate.Category.Allegory using (Rel)
open import Substrate.Category.Allegory.Maps using (deterministic)

------------------------------------------------------------------------
-- PART A — the Φ floor: a monotone refinement operator on fiber families.
------------------------------------------------------------------------

Fam : Set → Set₁
Fam A = A → Set

infix 4 _⊑ᶠ_
_⊑ᶠ_ : {A : Set} → Fam A → Fam A → Set
_⊑ᶠ_ {A} P Q = (a : A) → P a → Q a

⊑ᶠ-refl : {A : Set} {P : Fam A} → P ⊑ᶠ P
⊑ᶠ-refl _ p = p

⊑ᶠ-trans : {A : Set} {P Q R : Fam A} → P ⊑ᶠ Q → Q ⊑ᶠ R → P ⊑ᶠ R
⊑ᶠ-trans p q a x = q a (p a x)

record Refinement (A : Set) : Set₁ where
  field
    Φ    : (A → Set) → A → Set
    mono : {P Q : Fam A} → P ⊑ᶠ Q → Φ P ⊑ᶠ Φ Q

open Refinement

-- the stage-n iterate Rⁿ = Φⁿ R⁰.
iterate : {A : Set} → Refinement A → ℕ → (A → Set) → A → Set
iterate Φr zero    R⁰ = R⁰
iterate Φr (suc n) R⁰ = Φ Φr (iterate Φr n R⁰)

-- from a pre-fixed-point Φ R⁰ ⊑ R⁰, the iterate is a DESCENDING chain
-- (inhabitants only shrink): Rⁿ⁺¹ ⊑ Rⁿ. The grade n = how far Φ has pruned.
chain : {A : Set} (Φr : Refinement A) {R⁰ : Fam A}
      → (Φ Φr R⁰ ⊑ᶠ R⁰) → (n : ℕ) → iterate Φr (suc n) R⁰ ⊑ᶠ iterate Φr n R⁰
chain Φr pre zero    = pre
chain Φr pre (suc n) = mono Φr (chain Φr pre n)

-- the singleton READOUT (map ⟷ relation): a fiber family is map-like when each
-- fiber is a subsingleton.  μΦ a singleton ⟺ the limit is a map (ALG-5).
isSingleton : {A : Set} → Fam A → Set
isSingleton {A} P = (a : A) (x y : P a) → x ≡ y

------------------------------------------------------------------------
-- PART B — the concrete fusion: the bounded ℕ-wedge is a MAP.
------------------------------------------------------------------------

-- the bounded decomposition dividend ↦ (quotient, remainder), divisor (suc b).
BWedge : ℕ → ℕ → ℕ × ℕ → Set
BWedge b a qr = (proj₂ qr < suc b) × (a ≡ recon ℕ-div (proj₁ qr) (suc b) (proj₂ qr))

-- recon-bounded-unique (the wedge's uniqueness certificate) IS allegory
-- determinism = the fiber is a singleton = the certified wedge is a map.
bounded-wedge-det : (b : ℕ) → deterministic (BWedge b)
bounded-wedge-det b a (q₁ , r₁) (q₂ , r₂) (lt₁ , eq₁) (lt₂ , eq₂) =
  let u = recon-bounded-unique q₁ q₂ b r₁ r₂ lt₁ lt₂ (trans (sym eq₁) eq₂)
  in cong₂ _,_ (proj₁ u) (proj₂ u)
