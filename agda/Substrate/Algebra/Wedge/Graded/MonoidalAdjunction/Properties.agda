------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.Graded.MonoidalAdjunction.Properties
--
-- The proof-dependent faces of a GradedMonoidalAdjunction, kept out of the
-- record-declaring module so its closure stays proof-free (def/proof
-- separation policy; see scratch/def_proof_separation_policy.md):
--
--   * degree         — the flat Category.GradedMonoid via the Grothendieck
--                      flatten construction (Product.Laws.flatten-monoid),
--   * vec-gma        — the canonical Vec instance (needs the Vec law proofs),
--   * vec-gma-degree — its degree is exactly vec-flat-monoid (by refl).
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.Graded.MonoidalAdjunction.Properties where

open import Substrate.Foundation.Level using (0ℓ)
open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Vec using (Vec)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Algebra.Wedge.Product using (vec-product)
open import Substrate.Algebra.Wedge.Product.Laws
  using (flatten-monoid; vec-assoc; vec-unitˡ; vec-unitʳ; vec-flat-monoid)
open import Substrate.Algebra.Wedge.Graded.MonoidalAdjunction
  using (GradedMonoidalAdjunction; prod; assoc; unitˡ; unitʳ)
open import Substrate.Category.GradedMonoid using (GradedMonoid)

------------------------------------------------------------------------
-- The degree as a flat GradedMonoid (the Grothendieck flatten).
------------------------------------------------------------------------

-- ⟡set1-paydown: GradedMonoidalAdjunction is now parameterized over its carrier
-- family C (its `prod` is a `GradedProduct C`); C is inferred from the gma argument.
degree : {C : ℕ → Set} → GradedMonoidalAdjunction C → GradedMonoid 0ℓ
degree gma = flatten-monoid (prod gma) (assoc gma) (unitˡ gma) (unitʳ gma)

------------------------------------------------------------------------
-- The canonical instance: Vec. Its degree is exactly vec-flat-monoid.
------------------------------------------------------------------------

vec-gma : (A : Set) → GradedMonoidalAdjunction (Vec A)
vec-gma A = record
  { prod = vec-product A ; assoc = vec-assoc A
  ; unitˡ = vec-unitˡ A ; unitʳ = vec-unitʳ A }

vec-gma-degree : (A : Set) → degree (vec-gma A) ≡ vec-flat-monoid A
vec-gma-degree A = refl
