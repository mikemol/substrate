------------------------------------------------------------------------
-- Substrate.Category.Coalgebra.LagrangeOrder
--
-- The Lagrange / Euler-Fermat lift of `HasOrder`: for a finite family
-- of endomaps `α : Fin n → Endomap X`, every member has order dividing
-- n. This is the structural content of Lagrange's theorem (in a group
-- of order n, every element's order divides n) lifted from the
-- group level to the action level.
--
-- Per `project_composite_torsion_euler_substrate`: this primitive
-- generalises [[FiniteOrder]]'s cyclic-prime `HasOrder γ k` to handle
-- composite / non-cyclic torsion structures. The substrate's V₄
-- (Klein 4-group) and Coxeter Weyl groups (S₃, S₄, ...) are
-- composite torsion structures that require this lift; pure cyclic
-- FLT doesn't reach them.
--
-- Per `feedback_categorical_name_first`: the categorical name for
-- this primitive is "finite group action" / "Lagrange's theorem on
-- element orders." The substrate-specific framing avoids requiring
-- full group infrastructure — it just states the order-divides-n
-- property for a finite family of endomaps, which is what Lagrange
-- guarantees for any group action.
--
-- Specialisations:
--
--   * cyclic case (n = k, α i = iterate i γ for a single γ):
--     `HasLagrangeOrder` reduces to `HasOrder γ k` plus the trivial
--     iteration lemmas.
--
--   * trivial action (α i = id-end for every i): every iteration is
--     identity; `HasLagrangeOrder n α` holds trivially.
--
-- Connection to existing primitives:
--
--   * `FixedPoint γ x` (Coalgebra): k=1-at-a-point case.
--   * `HasOrder γ k` (FiniteOrder): single-element cyclic torsion.
--   * `LagrangeOrder` (this slice): finite-family / composite case.
--
-- Composite-torsion targets ready to instantiate:
--
--   * V₄ acting on F₂² or F₂³: `HasLagrangeOrder 4 V₄-action`.
--   * S₃ stabiliser of metric-id at dim 3: `HasLagrangeOrder 6 S₃-action`.
--   * S₄ at dim 4 (when formalised): `HasLagrangeOrder 24 S₄-action`.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Coalgebra.LagrangeOrder where

open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Nat using (ℕ; _*_)
open import Substrate.Foundation.Level using (Level)
open import Substrate.Foundation.Eq
  using (_≡_; refl; trans; cong)

open import Substrate.Category.Coalgebra
  using (Endomap; FixedPoint; fixed)
open import Substrate.Category.Coalgebra.FiniteOrder
  using (iterate; HasOrder; HasOrder-multiple; FixedPoint→periodic)

private
  variable
    ℓ : Level
    X : Set ℓ

------------------------------------------------------------------------
-- N-1: Action n X — a finite family of endomaps indexed by Fin n.
--
-- Type alias for clarity: `Action n X = Fin n → Endomap X`. Each
-- index i ∈ Fin n names an endomap α i : Endomap X.
--
-- In group-action terms: n = group order, α picks the action of each
-- group element. This primitive doesn't require α to form a group
-- (closure under composition); the Lagrange property below is the
-- structural content that's true regardless.
------------------------------------------------------------------------

Action : ℕ → Set ℓ → Set ℓ
Action n X = Fin n → Endomap X

------------------------------------------------------------------------
-- N-2: HasLagrangeOrder — Lagrange's theorem at the action level.
--
-- For a finite family of n endomaps, every member has order dividing
-- n (= iterate n (α i) ≡ id-end pointwise).
--
-- Structural content: in any group of order n, every element g
-- satisfies g^n = e (Lagrange). Lifted to actions: every action
-- endomap iterated n times returns identity.
--
-- This is the **Euler-Fermat analog** at the substrate's structural
-- level — generalising FLT (cyclic-prime case via HasOrder) to
-- arbitrary finite n (composite or non-cyclic).
------------------------------------------------------------------------

HasLagrangeOrder : {X : Set ℓ} (n : ℕ) (α : Action n X) → Set ℓ
HasLagrangeOrder {X = X} n α = (i : Fin n) → HasOrder (α i) n

------------------------------------------------------------------------
-- N-2b: At-a-point variant — `HasLagrangeOrder-at n α x`.
--
-- Weaker than `HasLagrangeOrder n α`: the order-divides-n property
-- holds AT THE SPECIFIC POINT x rather than at every x. Useful for
-- group-action sites where the action fixes only certain points
-- (e.g., the stabiliser subgroup of a specific element).
--
-- For substrate's S₃ stabiliser of metric-id: each of the 6 S₃
-- elements has `congruence-act g metric-id ≡ metric-id`; this gives
-- HasLagrangeOrder-at 6 S₃-cong-action metric-id. The action doesn't
-- fix arbitrary M, only metric-id, so the at-a-point version is the
-- appropriate predicate.
------------------------------------------------------------------------

HasLagrangeOrder-at : {X : Set ℓ} (n : ℕ) (α : Action n X) (x : X) → Set ℓ
HasLagrangeOrder-at n α x = (i : Fin n) → iterate n (α i) x ≡ x

-- The all-points version implies the at-a-point version.
HasLagrangeOrder→at :
  {X : Set ℓ} {n : ℕ} {α : Action n X} {x : X} →
  HasLagrangeOrder n α → HasLagrangeOrder-at n α x
HasLagrangeOrder→at {x = x} hyp i = hyp i x

------------------------------------------------------------------------
-- N-3: Specialisation — every action element has HasOrder n.
--
-- Direct extraction: given HasLagrangeOrder n α and any index i,
-- we obtain HasOrder (α i) n. Lets downstream code work with each
-- action element through the cyclic FiniteOrder infrastructure.
------------------------------------------------------------------------

extract-HasOrder :
  {X : Set ℓ} {n : ℕ} {α : Action n X} →
  HasLagrangeOrder n α → (i : Fin n) → HasOrder (α i) n
extract-HasOrder hyp i = hyp i

------------------------------------------------------------------------
-- N-4: Periodic-point bridge — a fixed point of every action element
-- is jointly periodic.
--
-- If x is a fixed point of every action endomap α i (i.e., a
-- "global fixed point" of the family), then for every i and every
-- m, iterate m (α i) x ≡ x. This is the connection to
-- Coalgebra.FixedPoint: a globally-fixed point under the family
-- gives a HasOrder witness for every element at every order.
------------------------------------------------------------------------

global-fixed-point→periodic :
  {X : Set ℓ} {n : ℕ} {α : Action n X} {x : X} →
  ((i : Fin n) → FixedPoint (α i) x) →
  (i : Fin n) (m : ℕ) → iterate m (α i) x ≡ x
global-fixed-point→periodic global-fp i m =
  FixedPoint→periodic (global-fp i) m

------------------------------------------------------------------------
-- N-4b: HasLagrangeOrder-from-multiples — Lagrange from per-element
-- orders + their multiples-to-n.
--
-- If for each action index i we have HasOrder (α i) kᵢ where some
-- multiple mᵢ · kᵢ equals n, then HasLagrangeOrder n α follows.
-- Concrete shape:
--   For each i, the witness pack (kᵢ , mᵢ , prfᵢ : mᵢ * kᵢ ≡ n , HasOrder (α i) kᵢ)
--   gives, via HasOrder-multiple + subst, the required
--   HasOrder (α i) n.
--
-- Used for: any finite action where individual element orders are
-- known and divide n. Examples (deferred concrete instances):
--   * V₄'s 4 elements: orders 1, 2, 2, 2 all dividing 4.
--   * S₃'s 6 elements: orders 1, 2, 2, 2, 3, 3 all dividing 6.
--   * Z₄'s 4 elements via the Coxeter pattern: orders 1, 2, 4, 4
--     all dividing 4.
------------------------------------------------------------------------

open import Substrate.Foundation.Product using (Σ; _,_; _×_)
open import Substrate.Foundation.Eq using (subst)

HasLagrangeOrder-from-multiples :
  {X : Set ℓ} (n : ℕ) (α : Action n X) →
  ((i : Fin n) →
     Σ ℕ (λ k → Σ ℕ (λ m → (m * k ≡ n) × HasOrder (α i) k))) →
  HasLagrangeOrder n α
HasLagrangeOrder-from-multiples n α witnesses i x with witnesses i
... | k , m , prf , hyp =
  subst (λ q → iterate q (α i) x ≡ x) prf
        (HasOrder-multiple hyp m x)

------------------------------------------------------------------------
-- N-5: Capstone — Lagrange / Euler-Fermat at the substrate level.
--
-- After this slice, `HasLagrangeOrder n α` captures the structural
-- content of "n-element finite group acting on X has every element's
-- order dividing n":
--
--   * Every action endomap α i iterates to identity at n steps.
--   * The full family ⟨α⟩ has order dividing n (Lagrange).
--   * Specialises to HasOrder when α is a cyclic generator.
--
-- Per [[project-composite-torsion-euler-substrate]]:
--
--   * **FLT case** (cyclic prime k): single γ : Endomap X with
--     HasOrder γ k. Already in [[FiniteOrder]].
--
--   * **Euler-Fermat case** (composite n, cyclic or not): finite family
--     α : Fin n → Endomap X with HasLagrangeOrder n α. THIS slice.
--
--   * **CRT decomposition** (coprime factorisation): joint actions
--     ⟨α₁, α₂⟩ with coprime orders decompose via Bezout. Deferred.
--
--   * **Euclid + Bezout** (algorithmic backbone for joint composition):
--     `StructuralGCD` + `BezoutDecomposition` primitives. Deferred.
--
-- Substrate-relevant instances ready to formalise:
--
--   * **V₄ action**: 4-element family α : Fin 4 → Endomap (Vector 2)
--     (or any V₄-carrier). Lagrange: every V₄ element has order 1 or 2.
--     HasLagrangeOrder 4 V₄-action holds.
--
--   * **S₃ stabiliser of metric-id at dim 3**: 6-element family
--     α : Fin 6 → Endomap SymBilinForm-3 with α i = congruence-act gᵢ
--     where gᵢ are the 6 S₃ elements. Lagrange: every element has
--     order 1, 2, or 3 (dividing 6). HasLagrangeOrder 6 S₃-action.
--
--   * **S₄ stabiliser at dim 4** (when formalised): 24-element family.
--     Element orders divide 24.
--
--   * **GL(n, F₂) action** at dim n: Lagrange at the full general
--     linear group order. For dim 3: |GL(3, F₂)| = 168 = 2³ · 3 · 7;
--     element orders divide 168.
--
-- Deferred coalgebraic-unfolding follow-ons:
--
--   * **Exact-order generalisation** (HasOrder-divides): the property
--     "the minimal k with iterate k γ ≡ id-end" — substantively
--     different from HasLagrangeOrder, which doesn't enforce minimality.
--     Captures Euler-Fermat's "the order DIVIDES n" precisely.
--
--   * **Primitive-generator lemma** (Euler's totient at predicate
--     level): if HasOrder γ k and gcd(j, k) = 1, then iterate j γ
--     also generates the full ⟨γ⟩.
--
--   * **`HasLagrangeOrder`-composition**: if HasLagrangeOrder n α
--     and HasLagrangeOrder m β with α, β commuting and coprime,
--     then their joint action ⟨α, β⟩ has HasLagrangeOrder (n*m).
--     CRT-style decomposition.
--
--   * **Euclid as structural primitive**: for two commuting cyclic
--     actions, the gcd of orders gives the common cyclic substructure.
--     Algorithmic content of joint-action management.
------------------------------------------------------------------------
