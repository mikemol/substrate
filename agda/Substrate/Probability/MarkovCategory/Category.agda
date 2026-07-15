------------------------------------------------------------------------
-- Substrate.Probability.MarkovCategory.Category
--
-- T2: the Markov category presented as a term-algebra category. With the term
-- carrier dissolved to Set₀ (Term = a cons-list over a Set₀ object-alphabet O
-- with kernel-generator payload; identity = [], composition = ++ₘ), the category
-- laws hold STRUCTURALLY and are exposed as Set₀ proofs. The `CategoryOf` bundle
-- itself (Set₁, and unused outside this module) is dropped — the laws below ARE
-- the morphism layer, witnessing the named category primitive without holding a
-- Set₁ record. (The genuine Markov-category structure — copy/delete/swap/tensor —
-- is the separate `Substrate.Probability.MarkovCategory` record.)
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Probability.MarkovCategory.Category where

open import Substrate.Foundation.Eq using (_≡_; refl; cong)

open import Substrate.Probability.MarkovCategory.Term

module _ (O : Set) (K : Set) where

  -- Identity and composition at the term level.
  id-MarkovTerm : (X : O) → MarkovTerm O K X X
  id-MarkovTerm _ = []

  compose-MarkovTerm :
    {X Y Z : O} →
    MarkovTerm O K Y Z → MarkovTerm O K X Y → MarkovTerm O K X Z
  compose-MarkovTerm g f = f ++ₘ g

  -- Category laws (structural, mechanical cons-list induction).
  ++ₘ-identityˡ : {X Y : O} (t : MarkovTerm O K X Y) → ([] ++ₘ t) ≡ t
  ++ₘ-identityˡ _ = refl

  ++ₘ-identityʳ : {X Y : O} (t : MarkovTerm O K X Y) → (t ++ₘ []) ≡ t
  ++ₘ-identityʳ []       = refl
  ++ₘ-identityʳ (x ∷ xs) = cong (x ∷_) (++ₘ-identityʳ xs)

  ++ₘ-assoc :
    {X Y Z W : O}
    (t : MarkovTerm O K X Y) (u : MarkovTerm O K Y Z) (v : MarkovTerm O K Z W) →
    ((t ++ₘ u) ++ₘ v) ≡ (t ++ₘ (u ++ₘ v))
  ++ₘ-assoc []       u v = refl
  ++ₘ-assoc (x ∷ xs) u v = cong (x ∷_) (++ₘ-assoc xs u v)
