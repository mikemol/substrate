------------------------------------------------------------------------
-- Substrate.WitnessTower.SimplicialBoundary.ConsAll
--
-- Defines: consAll
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.SimplicialBoundary; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.SimplicialBoundary.ConsAll where

open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.List
open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Bool.Not
open import Substrate.Foundation.Bool.Xor
open import Substrate.Foundation.Bool.Properties.XorComm
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Trans
open import Substrate.WitnessTower.SimplicialBoundary.Private
open import Substrate.WitnessTower.SimplicialBoundary.DelAt



------------------------------------------------------------------------
-- 3. The (unsigned) boundary: the list of all codim-1 faces, one per vertex.
--    `boundary (x ∷ xs)` = the face dropping x (= xs), then x coned onto every
--    face of xs — i.e. exactly { delAt j (x ∷ xs) : j }.
------------------------------------------------------------------------

-- cone a vertex onto every face (self-contained; Foundation.List defers map).
consAll : A → List (List A) → List (List A)
consAll x []       = []
consAll x (f ∷ fs) = (x ∷ f) ∷ consAll x fs
