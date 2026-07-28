------------------------------------------------------------------------
-- Substrate.Category.Coalgebra.StructuralGCD.Properties
--
-- PROOF MODULE for Substrate.Category.Coalgebra.StructuralGCD (per the
-- def/proof separation policy, scratch/def_proof_separation_policy.md).
--
-- The proof-bearing composite-torsion results: iteration compatibility,
-- the abelian rearrangement, and the order of a composition of commuting
-- endomaps.  These import Nat.Properties (*-comm); keeping them out of
-- the definition module means a consumer that only needs the `Commute`
-- structure never deserializes this arithmetic-proof closure.
--
-- Per [[project-composite-torsion-euler-substrate]]: HasOrder-compose-
-- commute IS the Lagrange-style result for the abelian-subgroup case;
-- for commuting γ₁ (order k₁), γ₂ (order k₂), γ₁ ∘E γ₂ has order
-- dividing k₁ · k₂ (tighter lcm bound deferred — requires GCD).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Coalgebra.StructuralGCD.Properties where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _*_)
open import Substrate.Foundation.Nat.Properties.Mul using (*-comm)
open import Substrate.Foundation.Level using (Level)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong)

open import Substrate.Category.Coalgebra using (Endomap; _∘E_)
open import Substrate.Category.Coalgebra.FiniteOrder
  using (iterate; iterate-add; HasOrder; HasOrder-multiple)
open import Substrate.Category.Coalgebra.StructuralGCD
  using (Commute; commute; commute-sym)

private
  variable
    ℓ : Level
    X : Set ℓ

------------------------------------------------------------------------
-- N-2: Commuting endomaps interact compatibly with iteration.
--
-- If γ commutes with η, then γ commutes with iterate n η for any n.
-- Proof by induction on n.
------------------------------------------------------------------------

commute-iterate-r :
  {X : Set ℓ} {γ η : Endomap X} →
  Commute γ η →
  (n : ℕ) (x : X) →
  γ (iterate n η x) ≡ iterate n η (γ x)
commute-iterate-r {γ = γ} {η = η} c zero    x = refl
commute-iterate-r {γ = γ} {η = η} c (suc n) x =
  trans (commute c (iterate n η x))
        (cong η (commute-iterate-r c n x))

------------------------------------------------------------------------
-- N-3: iterate-split-commute — k-fold composition splits via
-- commutativity.
--
--   iterate k (γ₁ ∘E γ₂) x ≡ iterate k γ₁ (iterate k γ₂ x)
--
-- Proof by induction on k.
------------------------------------------------------------------------

iterate-split-commute :
  {X : Set ℓ} {γ₁ γ₂ : Endomap X} →
  Commute γ₁ γ₂ →
  (k : ℕ) (x : X) →
  iterate k (γ₁ ∘E γ₂) x ≡ iterate k γ₁ (iterate k γ₂ x)
iterate-split-commute c zero    x = refl
iterate-split-commute {γ₁ = γ₁} {γ₂ = γ₂} c (suc k) x =
  cong γ₁
       (trans (cong γ₂ (iterate-split-commute c k x))
              (commute-iterate-r (commute-sym c) k _))

------------------------------------------------------------------------
-- N-4: HasOrder of composition of commuting endomaps.
--
-- If γ₁ has order k₁, γ₂ has order k₂, and they commute, then
-- γ₁ ∘E γ₂ has order dividing k₁ · k₂.
------------------------------------------------------------------------

HasOrder-compose-commute :
  {X : Set ℓ} {γ₁ γ₂ : Endomap X} {k₁ k₂ : ℕ} →
  Commute γ₁ γ₂ →
  HasOrder γ₁ k₁ → HasOrder γ₂ k₂ →
  HasOrder (γ₁ ∘E γ₂) (k₁ * k₂)
HasOrder-compose-commute {γ₁ = γ₁} {γ₂ = γ₂} {k₁ = k₁} {k₂ = k₂} c h₁ h₂ x =
  trans (iterate-split-commute c (k₁ * k₂) x)
  (trans (cong (iterate (k₁ * k₂) γ₁)
               (HasOrder-multiple h₂ k₁ x))
  (trans (cong (λ n → iterate n γ₁ x) (*-comm k₁ k₂))
         (HasOrder-multiple h₁ k₂ x)))
