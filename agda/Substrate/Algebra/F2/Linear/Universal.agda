------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.Universal
--
-- M-3.5 of the Cocycles structural-migration plan. The universal
-- property of linear maps: an F₂-linear map's behaviour on Vec F₂ n
-- is DETERMINED by its behaviour on basis vectors.
--
-- This is the THE structural bridge that makes downstream code
-- equalities (RM(r,m) via poly-eval = RM(r,m) via generator matrix;
-- Hamming [7,4,3] ≅ punctured RM(1,3); etc.) reduce to n basis-
-- check equalities — not 2ⁿ enumerations.
--
-- Composition: M-2's `≡-from-lookup` (Vec equality from lookup
-- equality) + M-2.5's `basis-decomp` (vectors as linear combinations
-- of basis vectors) + M-3's preserves-+/-*ₛ (linearity)
-- ⊢ linear-extensionality (this file).
--
-- The proof itself is ~8 trans-chain steps, each a single application
-- of a named lemma. Once written, downstream bridges become
-- one-liners.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Linear.Universal where

open import Data.Nat using (ℕ; zero; suc)
open import Data.Fin using (Fin; zero; suc)
open import Data.Vec using (Vec; lookup)
open import Function using (_∘_)
open import Relation.Binary.PropositionalEquality
  using (_≡_; refl; sym; trans; cong; cong₂)

open import Substrate.Algebra.F2
open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.Vector.Universal
open import Substrate.Algebra.F2.Linear

------------------------------------------------------------------------
-- sum-cong: vector sum respects pointwise equality on the family.
------------------------------------------------------------------------

sum-cong :
  ∀ {n m} {f g : Fin n → Vector m} →
  (∀ i → f i ≡ g i) → sum f ≡ sum g
sum-cong {zero}  _  = refl
sum-cong {suc _} eq = cong₂ _+ⱽ_ (eq zero) (sum-cong (eq ∘ suc))

------------------------------------------------------------------------
-- preserves-sum: every linear map distributes over sum.
--
-- apply L (Σᵢ f i) ≡ Σᵢ apply L (f i).
--
-- Proof: induction on the index range; base case uses preserves-𝟎,
-- step case uses preserves-+.
------------------------------------------------------------------------

preserves-sum :
  ∀ {n m k} (L : Linear n m) (f : Fin k → Vector n) →
  apply L (sum f) ≡ sum (apply L ∘ f)
preserves-sum {k = zero}  L f = preserves-𝟎 L
preserves-sum {k = suc _} L f =
  trans (preserves-+ L (f zero) (sum (f ∘ suc)))
        (cong (apply L (f zero) +ⱽ_) (preserves-sum L (f ∘ suc)))

------------------------------------------------------------------------
-- Linear-map extensionality.
--
-- Two linear maps that agree on all basis vectors agree on all
-- vectors. This is the universal-property bridge: future code
-- equalities reduce to n basis-checks (= the dimension of the source
-- space) rather than 2ⁿ value-checks.
--
-- Chain:
--   apply L v
--     ≡ apply L (Σᵢ (lookup v i) *ₛ basis i)        [basis-decomp]
--     ≡ Σᵢ apply L ((lookup v i) *ₛ basis i)        [preserves-sum]
--     ≡ Σᵢ (lookup v i) *ₛ apply L (basis i)        [preserves-*ₛ]
--     ≡ Σᵢ (lookup v i) *ₛ apply M (basis i)        [hypothesis]
--     ≡ Σᵢ apply M ((lookup v i) *ₛ basis i)        [preserves-*ₛ sym]
--     ≡ apply M (Σᵢ (lookup v i) *ₛ basis i)        [preserves-sum sym]
--     ≡ apply M v                                    [basis-decomp sym]
------------------------------------------------------------------------

linear-extensionality :
  ∀ {n m} (L M : Linear n m) →
  ((i : Fin n) → apply L (basis i) ≡ apply M (basis i)) →
  (v : Vector n) → apply L v ≡ apply M v
linear-extensionality {n} {m} L M agree v =
  trans (cong (apply L) (basis-decomp v))
  (trans (preserves-sum L (λ i → lookup v i *ₛ basis i))
  (trans (sum-cong (λ i → preserves-*ₛ L (lookup v i) (basis i)))
  (trans (sum-cong (λ i → cong (lookup v i *ₛ_) (agree i)))
  (trans (sum-cong (λ i → sym (preserves-*ₛ M (lookup v i) (basis i))))
  (trans (sym (preserves-sum M (λ i → lookup v i *ₛ basis i)))
         (cong (apply M) (sym (basis-decomp v))))))))
