------------------------------------------------------------------------
-- Substrate.Conway.Mul.Anon
--
-- Defines: _
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Conway.Mul; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Conway.Mul.Anon where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Conway.SurrealFinite
open import Substrate.Conway.Mul.ConwayMulType
open import Substrate.Conway.AddGeneral.ConwayAddSignature



------------------------------------------------------------------------
-- 2. The ConwayMul signature record.
------------------------------------------------------------------------

-- ⟡set1-paydown: parameterize the four per-axiom `Set` obligation
-- placeholders out of the record (they were `field : Set`, the Set₁ source);
-- the record now bundles only `mul` and lands in Set. A downstream slice
-- instantiates the obligations by choosing the four Set parameters.
module _ (one-identity-stated commutativity-stated
          associativity-stated distributivity-stated : Set) where
  record ConwayMulSignature : Set where
    field
      mul : ConwayMulType

------------------------------------------------------------------------
-- 3. Capstone for G7.
--
-- Multiplication signature named. G8 names distributivity
-- explicitly; G9 packages surreals as a Field-obligation; G10
-- caps the arc.
------------------------------------------------------------------------
