------------------------------------------------------------------------
-- Substrate.WitnessTower.SnGroup
--
-- The GROUP half of "the tower IS Sₙ": the genuine bijections on Fin n
-- (image vectors with lookup injective) are closed under the composition
-- `compose` that the censuses use, and that composition IS function
-- composition of the underlying maps. So the tower's permutations form a
-- group, and the map (vector ↦ its apply = lookup) is an injective group
-- homomorphism onto the bijections of Fin n under ∘ — i.e. Sₙ as a group,
-- the textbook symmetric group, not merely Sₙ as a set.
--
--   apply σ           = lookup σ                          (the action)
--   apply (compose σ τ) = apply σ ∘ apply τ              (homomorphism)
--   apply id-perm     = identity                          (unit)
--   apply σ ≡ apply τ ⟹ σ ≡ τ                            (faithful/injective)
--   IsPerm σ → IsPerm τ → IsPerm (compose σ τ)            (closure)
--
-- Together with the Fin (n!) ≅ Sₙ bijection (WitnessTower.Sn), this is the
-- machine-checked group isomorphism between the witnessing-insertion
-- construction and the symmetric group. (Bridging to the Groups.Symmetric
-- record additionally needs the inverse field; on Fin n injective ⟹
-- surjective supplies it — the mechanical remaining wrapper.)
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.SnGroup where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Fin using (Fin)
open import Substrate.Foundation.Vec using (lookup)
open import Substrate.Foundation.Vec.Properties using (lookup∘tabulate)
open import Substrate.Foundation.Eq using (_≡_; refl; trans; sym; cong)

open import Substrate.WitnessTower.Enumerate using (Perm)
open import Substrate.WitnessTower.FirstAppearance using (compose; id-perm)
open import Substrate.WitnessTower.IsPermutation using (IsPerm)
open import Substrate.WitnessTower.Decompose using (lookup-ext)

------------------------------------------------------------------------
-- 1. apply = lookup; the homomorphism and unit laws (apply level).
------------------------------------------------------------------------

apply : {n : ℕ} → Perm n → Fin n → Fin n
apply = lookup

-- compose realizes function composition of the applies.
apply-compose :
  {n : ℕ} (σ τ : Perm n) (i : Fin n) →
  apply (compose σ τ) i ≡ apply σ (apply τ i)
apply-compose σ τ i = lookup∘tabulate (λ k → lookup σ (lookup τ k)) i

-- the identity vector acts as the identity function.
apply-id : {n : ℕ} (i : Fin n) → apply (id-perm n) i ≡ i
apply-id i = lookup∘tabulate (λ k → k) i

------------------------------------------------------------------------
-- 2. Faithfulness: a permutation is determined by its action.
------------------------------------------------------------------------

apply-injective :
  {n : ℕ} {σ τ : Perm n} → ((i : Fin n) → apply σ i ≡ apply τ i) → σ ≡ τ
apply-injective {σ = σ} {τ} h = lookup-ext σ τ h

------------------------------------------------------------------------
-- 3. Closure: the bijections are closed under compose (a group).
------------------------------------------------------------------------

compose-is-perm :
  {n : ℕ} (σ τ : Perm n) → IsPerm σ → IsPerm τ → IsPerm (compose σ τ)
compose-is-perm σ τ σ-perm τ-perm i j eq =
  τ-perm i j (σ-perm (lookup τ i) (lookup τ j) lhs)
  where
    -- strip the tabulate on both sides: lookup (compose σ τ) k = σ (τ k).
    lhs : lookup σ (lookup τ i) ≡ lookup σ (lookup τ j)
    lhs = trans (sym (apply-compose σ τ i)) (trans eq (apply-compose σ τ j))

------------------------------------------------------------------------
-- 4. Unit laws as vector equations (via faithfulness + the apply laws).
------------------------------------------------------------------------

compose-id-left : {n : ℕ} (σ : Perm n) → compose (id-perm n) σ ≡ σ
compose-id-left σ = apply-injective
  (λ i → trans (apply-compose (id-perm _) σ i) (apply-id (apply σ i)))

compose-id-right : {n : ℕ} (σ : Perm n) → compose σ (id-perm n) ≡ σ
compose-id-right σ = apply-injective
  (λ i → trans (apply-compose σ (id-perm _) i) (cong (apply σ) (apply-id i)))
