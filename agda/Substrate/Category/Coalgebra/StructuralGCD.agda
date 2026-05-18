------------------------------------------------------------------------
-- Substrate.Category.Coalgebra.StructuralGCD
--
-- The Euclid-algorithmic backbone for joint cyclic actions. Names
-- the substrate's structural primitive for composing two commuting
-- finite-order endomaps:
--
--   Commute γ₁ γ₂   — pointwise commutativity
--   iterate-split   — iterate of composition splits via commutativity
--   HasOrder-compose-commute — γ₁ ∘E γ₂ has order dividing k₁ · k₂
--
-- Per [[project-composite-torsion-euler-substrate]]: this is the
-- composite-torsion-via-commuting-factors lift. When γ₁ of order k₁
-- and γ₂ of order k₂ commute, their joint generates a cyclic
-- substructure whose order divides k₁ · k₂ (with the tighter
-- lcm(k₁, k₂) bound deferred — requires stdlib's GCD).
--
-- The substrate-relevant connection to Euclid's algorithm: gcd(k₁, k₂)
-- computes the COMMON cyclic substructure of ⟨γ₁⟩ ∩ ⟨γ₂⟩ when both
-- act on the same carrier with commuting actions. lcm(k₁, k₂) is the
-- joint order. The k₁ · k₂ bound is sharp when gcd = 1 (coprime case);
-- otherwise lcm < k₁ · k₂ and the joint has structure not captured
-- by simple multiplication.
--
-- Per `feedback_categorical_name_first`: "Commute" is the categorical
-- name for commuting endomorphisms (or for an abelian subgroup of an
-- automorphism group). HasOrder-compose-commute IS the Lagrange-style
-- result for the abelian-subgroup case.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Coalgebra.StructuralGCD where

open import Data.Nat using (ℕ; zero; suc; _*_)
open import Data.Nat.Properties using (*-comm)
open import Level using (Level)
open import Relation.Binary.PropositionalEquality
  using (_≡_; refl; sym; trans; cong)

open import Substrate.Category.Coalgebra using (Endomap; _∘E_)
open import Substrate.Category.Coalgebra.FiniteOrder
  using (iterate; iterate-add; HasOrder; HasOrder-multiple)

private
  variable
    ℓ : Level
    X : Set ℓ

------------------------------------------------------------------------
-- N-1: Commute — two endomaps commute pointwise.
--
-- Captures: γ₁ ∘E γ₂ ≡ γ₂ ∘E γ₁ at the function level (via pointwise
-- equality, avoiding funext).
--
-- An abelian subgroup of Aut(X) consists of pairwise-commuting
-- endomorphisms.
------------------------------------------------------------------------

record Commute {X : Set ℓ} (γ₁ γ₂ : Endomap X) : Set ℓ where
  field
    commute : (x : X) → γ₁ (γ₂ x) ≡ γ₂ (γ₁ x)

open Commute public

-- Commutativity is symmetric.
commute-sym : {X : Set ℓ} {γ₁ γ₂ : Endomap X} →
              Commute γ₁ γ₂ → Commute γ₂ γ₁
commute-sym c = record { commute = λ x → sym (commute c x) }

------------------------------------------------------------------------
-- N-2: Commuting endomaps interact compatibly with iteration.
--
-- If γ commutes with η, then γ commutes with iterate n η for any n.
-- (γ slides through any number of η-applications.)
--
-- Proof by induction on n.
------------------------------------------------------------------------

commute-iterate-r :
  {X : Set ℓ} {γ η : Endomap X} →
  Commute γ η →
  (n : ℕ) (x : X) →
  γ (iterate n η x) ≡ iterate n η (γ x)
commute-iterate-r {γ = γ} {η = η} c zero    x = refl
commute-iterate-r {γ = γ} {η = η} c (suc n) x =
  -- γ (iterate (suc n) η x) = γ (η (iterate n η x))
  --   ≡ η (γ (iterate n η x))   [Commute c]
  --   ≡ η (iterate n η (γ x))    [IH]
  --   = iterate (suc n) η (γ x)
  trans (commute c (iterate n η x))
        (cong η (commute-iterate-r c n x))

------------------------------------------------------------------------
-- N-3: iterate-split-commute — k-fold composition splits via
-- commutativity.
--
-- For commuting endomaps γ₁, γ₂:
--   iterate k (γ₁ ∘E γ₂) x ≡ iterate k γ₁ (iterate k γ₂ x)
--
-- I.e., applying (γ₁ ∘E γ₂) k times equals applying γ₁ k times
-- followed by γ₂ k times. This is the "abelian rearrangement"
-- that commutativity enables.
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
  -- iterate (suc k) (γ₁ ∘E γ₂) x = γ₁ (γ₂ (iterate k (γ₁ ∘E γ₂) x))
  --   ≡ γ₁ (γ₂ (iterate k γ₁ (iterate k γ₂ x)))   [IH inside cong γ₁ ∘ cong γ₂]
  --   ≡ γ₁ (iterate k γ₁ (γ₂ (iterate k γ₂ x)))   [γ₂ commutes with iterate k γ₁]
  --   = iterate (suc k) γ₁ (iterate (suc k) γ₂ x) [definition]
  cong γ₁
       (trans (cong γ₂ (iterate-split-commute c k x))
              (commute-iterate-r (commute-sym c) k _))

------------------------------------------------------------------------
-- N-4: HasOrder of composition of commuting endomaps.
--
-- If γ₁ has order k₁, γ₂ has order k₂, and they commute, then
-- γ₁ ∘E γ₂ has order dividing k₁ · k₂.
--
-- Proof chain:
--   iterate (k₁ * k₂) (γ₁ ∘E γ₂) x
--   ≡ iterate (k₁ * k₂) γ₁ (iterate (k₁ * k₂) γ₂ x)   [iterate-split-commute]
--   ≡ iterate (k₁ * k₂) γ₁ x                          [HasOrder-multiple at n = k₁]
--   ≡ x                                                [HasOrder-multiple at n = k₂]
--
-- Tighter `lcm` bound is deferred — requires stdlib's GCD/lcm
-- infrastructure for the divisibility arithmetic.
------------------------------------------------------------------------

HasOrder-compose-commute :
  {X : Set ℓ} {γ₁ γ₂ : Endomap X} {k₁ k₂ : ℕ} →
  Commute γ₁ γ₂ →
  HasOrder γ₁ k₁ → HasOrder γ₂ k₂ →
  HasOrder (γ₁ ∘E γ₂) (k₁ * k₂)
HasOrder-compose-commute {γ₁ = γ₁} {γ₂ = γ₂} {k₁ = k₁} {k₂ = k₂} c h₁ h₂ x =
  -- iterate (k₁ * k₂) (γ₁ ∘E γ₂) x
  trans (iterate-split-commute c (k₁ * k₂) x)
  -- ≡ iterate (k₁ * k₂) γ₁ (iterate (k₁ * k₂) γ₂ x)
  (trans (cong (iterate (k₁ * k₂) γ₁)
               (HasOrder-multiple h₂ k₁ x))
  -- ≡ iterate (k₁ * k₂) γ₁ x
  (trans (cong (λ n → iterate n γ₁ x) (*-comm k₁ k₂))
  -- ≡ iterate (k₂ * k₁) γ₁ x
         (HasOrder-multiple h₁ k₂ x)))
  -- ≡ x

------------------------------------------------------------------------
-- N-5: Capstone — Euclid backbone for composite torsion.
--
-- After this slice, the substrate has the COMMUTATIVE composite-
-- torsion infrastructure:
--
--   * `Commute γ₁ γ₂` — pointwise commutativity primitive.
--   * `iterate-split-commute` — k-fold composition splits via
--     commutativity (the "abelian rearrangement").
--   * `HasOrder-compose-commute` — for commuting γ₁ (order k₁), γ₂
--     (order k₂): γ₁ ∘E γ₂ has order dividing k₁ · k₂.
--
-- Per [[project-composite-torsion-euler-substrate]]:
--
--   * **Euclid's algorithm** structurally: computes gcd(k₁, k₂) at
--     the order level; the common cyclic substructure of ⟨γ₁⟩ ∩ ⟨γ₂⟩
--     has order gcd(k₁, k₂). The k₁ · k₂ bound here is the LOOSE
--     bound; the tight bound is lcm(k₁, k₂) = k₁ · k₂ / gcd(k₁, k₂).
--
--   * **Bezout (Extended Euclid)** at the structural level: when
--     gcd(k₁, k₂) = 1 (coprime), there exist s, t ∈ ℤ with
--     s · k₁ + t · k₂ = 1. Structurally: every element of the joint
--     ⟨γ₁, γ₂⟩ ≅ Z/k₁ × Z/k₂ can be written explicitly as
--     γ₁^a · γ₂^b. CRT decomposition.
--
--   * **Substrate's V₄ as non-coprime case**: V₄ = Z/2 × Z/2 with
--     gcd(2, 2) = 2 ≠ 1, so Bezout doesn't decompose it; this is
--     why V₄ is structurally distinct from Z/4 (which has the same
--     |G| = 4 but is cyclic).
--
-- Substrate-relevant uses:
--
--   * Hodge ★ + Coxeter braid (when they commute on a shared
--     carrier): joint torsion structure via HasOrder-compose-commute.
--
--   * V₄ as composition of two commuting involutions
--     (V₄ = ⟨g₁, g₂ | g₁² = g₂² = e, g₁g₂ = g₂g₁⟩): each generator
--     has order 2, V₄'s exponent is 2, but the joint structure
--     k₁ · k₂ = 4 = |V₄|. ✓
--
--   * Future S₄, S₅, ... actions: identify commuting subactions to
--     decompose via this primitive.
--
-- Deferred coalgebraic-unfolding follow-ons:
--
--   * **lcm-tight bound**: HasOrder-compose-commute at lcm(k₁, k₂)
--     rather than k₁ · k₂. Requires stdlib's Data.Nat.GCD.
--
--   * **Bezout decomposition primitive**: at coprime k₁, k₂, the
--     explicit CRT decomposition (Z/(k₁·k₂) ≅ Z/k₁ × Z/k₂) at the
--     action level. Names the algorithmic content of Extended Euclid.
--
--   * **`StructuralGCDLattice`**: the lattice of cyclic subgroups
--     of a finite abelian group, structured by divisibility of orders.
--
--   * **Non-commuting case (general Lagrange)**: when γ₁, γ₂ don't
--     commute, the joint group is non-abelian; the structure is more
--     complex (e.g., Coxeter Weyl groups). LagrangeOrder primitive
--     handles this without requiring commutativity but loses the
--     fine structural decomposition.
------------------------------------------------------------------------
