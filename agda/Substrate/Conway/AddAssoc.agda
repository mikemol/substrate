------------------------------------------------------------------------
-- Substrate.Conway.AddAssoc
--
-- G4 of the Conway game-induction tower per
-- [scratch/m_mod_arc_plan.md].
--
-- Names the associativity obligation for Conway addition.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Conway.AddAssoc where

open import Substrate.Foundation.Nat using (ℕ; suc; _+_)
open import Substrate.Foundation.Nat.Properties using (+-assoc)
open import Substrate.Foundation.Eq
  using (_≡_; sym; cong; subst)
open import Substrate.Conway.SurrealFinite using (SurrealFinite)
open import Substrate.Conway.AddGeneral using (ConwayAddType)

------------------------------------------------------------------------
-- 1. The associativity obligation.
--
-- Given `add : ConwayAddType`, associativity states:
--
--   add (m+n) k (add m n a b) c
--     ≡ subst-along-+-assoc (add m (n+k) a (add n k b c))
------------------------------------------------------------------------

ConwayAddAssociativity : ConwayAddType → Set
ConwayAddAssociativity add =
  (m n k : ℕ)
  (a : SurrealFinite (suc m))
  (b : SurrealFinite (suc n))
  (c : SurrealFinite (suc k)) →
  add (m + n) k (add m n a b) c
    ≡ subst SurrealFinite (cong suc (sym (+-assoc m n k)))
            (add m (n + k) a (add n k b c))

------------------------------------------------------------------------
-- 2. Capstone for G4.
--
-- Associativity obligation named. G5 handles order transitivity.
-- Full inductive proof deferred.
------------------------------------------------------------------------
