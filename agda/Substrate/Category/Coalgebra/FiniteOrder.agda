------------------------------------------------------------------------
-- Substrate.Category.Coalgebra.FiniteOrder
--
-- Finite-order endomaps — the "torsion-element-of-automorphism"
-- structural primitive that unifies:
--
--   * Hodge ★ involution (order 2)
--   * Coxeter braid (sᵢsⱼ)^p = e (order p)
--   * Hodge dual as modular structure (the cyclic quotient X/⟨γ⟩)
--   * FLT for dimensional spaces (iterate k γ ≡ id-end for order-k γ)
--
-- Per `project_torsion_element_universal`: at every subspace supporting
-- a finite-order automorphism γ with γ^k = id-end, the local Z/k cyclic
-- group gives a k+1 split with the "+1" being γ^0 = identity (the
-- torsion-identity). The substrate's `3+1 parity universal` is the
-- k=2 (Hodge ★) instance of this.
--
-- Per `feedback_categorical_name_first`: the categorical name is
-- "finite-order endomap" / "torsion element of an automorphism group"
-- / "periodic endomap." The universal property is `iterate k γ ≡ id-end`
-- (pointwise; avoiding funext per substrate discipline).
--
-- Connection to primitive #1 (Coalgebra.FixedPoint):
-- `FixedPoint γ x` is the k=1 case AT A SPECIFIC POINT x. `HasOrder γ k`
-- is the everywhere statement at order k. The two compose: if x is a
-- fixed point of γ, then x is periodic with period dividing every k.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Coalgebra.FiniteOrder where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_; _*_)
open import Level using (Level)
open import Substrate.Foundation.Eq
  using (_≡_; refl; sym; trans; cong)

open import Substrate.Category.Coalgebra
  using (Endomap; FixedPoint; fixed)

private
  variable
    ℓ : Level
    X : Set ℓ

------------------------------------------------------------------------
-- N-1: iterate — finite iteration of an endomap.
--
--   iterate 0 γ = id-end
--   iterate (suc n) γ x = γ (iterate n γ x)
--
-- The substrate's universal "γ applied n times." For γ : Endomap X,
-- `iterate n γ` is again an Endomap X.
------------------------------------------------------------------------

iterate : {X : Set ℓ} → ℕ → Endomap X → Endomap X
iterate zero    γ x = x
iterate (suc n) γ x = γ (iterate n γ x)

------------------------------------------------------------------------
-- N-2: iterate-add — iteration is additive in the index.
--
--   iterate (m + n) γ x ≡ iterate m γ (iterate n γ x)
--
-- The structural fact that γ^(m+n) = γ^m ∘ γ^n, expressed pointwise.
-- Used throughout the finite-order theory.
------------------------------------------------------------------------

iterate-add :
  {X : Set ℓ} (γ : Endomap X) (m n : ℕ) (x : X) →
  iterate (m + n) γ x ≡ iterate m γ (iterate n γ x)
iterate-add γ zero    n x = refl
iterate-add γ (suc m) n x = cong γ (iterate-add γ m n x)

------------------------------------------------------------------------
-- N-3: HasOrder — the structural property "γ has order k pointwise."
--
--   HasOrder γ k = (x : X) → iterate k γ x ≡ x
--
-- This is the **dimensional-space analog of Fermat's little theorem**:
-- raising the endomap to the k-th power returns identity. At F₂ for
-- the Hodge ★ at order 2, this is ★² = id-end. For Coxeter braid
-- (sᵢsⱼ) at order p (= the Coxeter matrix entry), this is the braid
-- relation `(sᵢsⱼ)^p = e` lifted to the action level.
--
-- Stated pointwise to avoid function extensionality; structurally
-- equivalent to "γ^k = id-end as endomaps" under funext.
------------------------------------------------------------------------

HasOrder : {X : Set ℓ} → Endomap X → ℕ → Set ℓ
HasOrder {X = X} γ k = (x : X) → iterate k γ x ≡ x

------------------------------------------------------------------------
-- N-4: HasOrder-1 — the k=1 case (γ is the pointwise identity).
--
-- HasOrder γ 1 says `γ x ≡ x` for every x — i.e., γ acts as the
-- identity pointwise. This is the trivial "torsion subgroup is the
-- identity" instance.
------------------------------------------------------------------------

HasOrder-1 : {X : Set ℓ} (γ : Endomap X) →
             HasOrder γ 1 → (x : X) → γ x ≡ x
HasOrder-1 γ hyp x = hyp x

HasOrder-1-from-identity :
  {X : Set ℓ} (γ : Endomap X) →
  ((x : X) → γ x ≡ x) → HasOrder γ 1
HasOrder-1-from-identity γ id-pw x = id-pw x

------------------------------------------------------------------------
-- N-5: Fixed points are periodic at every order.
--
-- If x is a fixed point of γ (γ x ≡ x), then for every k,
-- iterate k γ x ≡ x. Connects primitive #1 (FixedPoint) to this
-- primitive (HasOrder): fixed points are the "always periodic" case.
------------------------------------------------------------------------

iterate-at-fixed-point :
  {X : Set ℓ} {γ : Endomap X} {x : X} →
  γ x ≡ x → (k : ℕ) → iterate k γ x ≡ x
iterate-at-fixed-point fp zero    = refl
iterate-at-fixed-point {γ = γ} {x = x} fp (suc k) =
  trans (cong γ (iterate-at-fixed-point fp k)) fp

-- Specialised: a FixedPoint witness gives periodicity at every order.
FixedPoint→periodic :
  {X : Set ℓ} {γ : Endomap X} {x : X} →
  FixedPoint γ x → (k : ℕ) → iterate k γ x ≡ x
FixedPoint→periodic fp = iterate-at-fixed-point (fixed fp)

------------------------------------------------------------------------
-- N-6: Order multiples — γ^(n·k) = id-end when γ has order k.
--
-- If γ has order k pointwise, then iterating n · k times also returns
-- identity. This is the "Z/k cyclic action" property: the cyclic
-- subgroup generated by γ has order dividing k, so any multiple of k
-- iterations is the identity.
--
-- The substrate's modular-structure reading: this IS the "mod ⟨γ⟩"
-- equivalence — two iteration counts are equivalent iff their
-- difference is a multiple of k.
------------------------------------------------------------------------

HasOrder-multiple :
  {X : Set ℓ} {γ : Endomap X} {k : ℕ} →
  HasOrder γ k → (n : ℕ) (x : X) →
  iterate (n * k) γ x ≡ x
HasOrder-multiple {γ = γ} {k = k} hyp zero    x = refl
HasOrder-multiple {γ = γ} {k = k} hyp (suc n) x =
  -- iterate ((suc n) * k) γ x
  -- = iterate (k + n * k) γ x        [stdlib: suc m * n = n + m * n]
  -- = iterate k γ (iterate (n * k) γ x)   [iterate-add]
  -- = iterate k γ x                  [IH: HasOrder-multiple hyp n x]
  -- = x                              [HasOrder hyp at x]
  trans (iterate-add γ k (n * k) x)
  (trans (cong (iterate k γ) (HasOrder-multiple hyp n x))
         (hyp x))

------------------------------------------------------------------------
-- N-6b: Iteration of iteration = product iteration.
--
--   iterate k (iterate j γ) x ≡ iterate (k * j) γ x
--
-- The structural fact that γ^j applied k times = γ^(k·j). Used by
-- HasOrder-iterate to lift the order property through power-of-γ
-- constructions.
--
-- Proof by induction on k:
--   k=0: iterate 0 (iterate j γ) x = x = iterate 0 γ x.
--   k=suc k': iterate (suc k') (iterate j γ) x
--             = iterate j γ (iterate k' (iterate j γ) x)
--             ≡ iterate j γ (iterate (k' * j) γ x)         [IH]
--             ≡ iterate (j + k' * j) γ x                   [sym iterate-add]
--             = iterate ((suc k') * j) γ x                 [stdlib *-suc]
------------------------------------------------------------------------

iterate-iterate :
  {X : Set ℓ} (γ : Endomap X) (k j : ℕ) (x : X) →
  iterate k (iterate j γ) x ≡ iterate (k * j) γ x
iterate-iterate γ zero    j x = refl
iterate-iterate γ (suc k) j x =
  trans (cong (iterate j γ) (iterate-iterate γ k j x))
        (sym (iterate-add γ j (k * j) x))

------------------------------------------------------------------------
-- N-6c: HasOrder-iterate — power of an order-k endomap has order
-- dividing k.
--
-- If `HasOrder γ k`, then for any j ∈ ℕ, `HasOrder (iterate j γ) k`.
-- I.e., γ^j also satisfies γ^(jk) = id.
--
-- Note: this is the "order DIVIDES k" form (HasOrder doesn't enforce
-- minimal order). The EXACT-order version (γ^j has order exactly k
-- iff gcd(j, k) = 1) is the φ-gauge content of Euler's totient —
-- substantial deferred work.
--
-- For this lemma:
--   iterate k (iterate j γ) x
--   ≡ iterate (k * j) γ x                  [iterate-iterate]
--   ≡ iterate (j * k) γ x                  [*-comm]
--   ≡ x                                     [HasOrder-multiple at n = j]
------------------------------------------------------------------------

open import Substrate.Foundation.Nat.Properties using (*-comm)

HasOrder-iterate :
  {X : Set ℓ} {γ : Endomap X} {k : ℕ} →
  HasOrder γ k → (j : ℕ) → HasOrder (iterate j γ) k
HasOrder-iterate {γ = γ} {k = k} hyp j x =
  trans (iterate-iterate γ k j x)
  (trans (cong (λ n → iterate n γ x) (*-comm k j))
         (HasOrder-multiple hyp j x))

------------------------------------------------------------------------
-- N-7: Capstone — the unification documented.
--
-- After this slice, `HasOrder γ k` is the substrate's universal
-- handle for finite-order endomaps:
--
--   * Hodge involution: HasOrder ★ 2 (at any dim n where ★ is defined).
--   * Coxeter braid: HasOrder (sᵢ ∘ sⱼ) p (where p = Coxeter matrix
--     entry mᵢⱼ).
--   * Fixed-point case: HasOrder γ 1 (γ is the pointwise identity)
--     — or, at a single point, FixedPoint γ x extended to every k.
--   * Periodic action: the cyclic subgroup ⟨γ⟩ ≅ Z/k acts on X via
--     iterate; HasOrder is the universal property of this action.
--
-- Multi-reading derived structures (per [[project-torsion-element-
-- universal]]):
--
--   * **FLT-for-dimensional-spaces reading**: iterate k γ ≡ id-end
--     IS the FLT-analog (raising k-th power = identity).
--
--   * **Hodge-as-modulus reading**: the cyclic group ⟨γ⟩ generated
--     by γ IS the "modulus"; two iteration counts equivalent iff
--     differ by a multiple of k (= HasOrder-multiple).
--
--   * **Transport between prime-based symmetry group and its lower
--     number**: ⟨γ⟩ ≤ AutGroup(X) is the cyclic subgroup; the
--     quotient X/⟨γ⟩ is the orbit space (= "lower number" of
--     equivalence classes); γ transports orbits.
--
-- Concrete substrate instances ready to retrofit:
--
--   * CoxeterRelations' `s₁²-on-v` ⇒ HasOrder (s₁ ∘L s₁ -as-endomap) 2
--   * CoxeterRelations' `s₂²-on-v` ⇒ HasOrder (s₂ ∘L s₂ -as-endomap) 2
--   * The braid (s₁s₂)³ = e (would require lifting braid-on-v to
--     HasOrder (s₁ ∘L s₂) 3 — needs the s₁ ∘L s₂ endomap, then
--     iterate 3 ≡ id).
--   * Future Hodge ★ at any dim: HasOrder ★ 2.
--
-- Deferred follow-ons:
--
--   * **OrbitSpace** primitive — the quotient X/⟨γ⟩ as a categorical
--     coequalizer (of iterate γ and id-end). The "modular structure"
--     reading made explicit.
--
--   * **CoxeterRelations as HasOrder retrofit** — lift the existing
--     apply-pointwise relations to HasOrder instances. Light slice
--     once the endomap encoding of s₁/s₂ acts is settled.
--
--   * **Hodge-★ at variable dim** — formalise `HodgeStar n` as an
--     endomap of Λᵏ(F₂ⁿ) and prove `HasOrder (HodgeStar n) 2`. The
--     universal Hodge-involution lemma at every dim.
--
--   * **3+1 parity as torsion identity** — make the connection
--     explicit: the "+1" of every 3+1 split is `iterate 0 γ x ≡ x`
--     (= refl) for the local γ, and the "3" is the (k-1)=1 other
--     orbit element (= γ x) combined with the other 2-dim subspace
--     structure.
------------------------------------------------------------------------
