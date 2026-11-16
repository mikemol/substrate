------------------------------------------------------------------------
-- Substrate.FUSep.FUSepQConfluence.Packed
--
-- Defines: packed
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.FUSep.FUSepQConfluence; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.FUSep.FUSepQConfluence.Packed where

open import Substrate.Foundation.Product
import Substrate.Foundation.Product as FP   -- for the ⟡def-eq projection witnesses
open import Substrate.Foundation.Nat.Nat
open import Substrate.FUSep.FUSepQSKI    using (atom; app) renaming (Tm-QSKI to Tm-QSKI)
open import Substrate.Foundation.Eq
open import Substrate.FUSep.FUSepQConfluence.Span
open import Substrate.FUSep.FUSepQConfluence.Diamond
open import Substrate.FUSep.FUSepQSKI



-- both indexes reconstruct the SAME s: the reduce-backpointer and the peel-
-- reconstruction are EQUAL (both = s), so the SPPF packs them at ONE node — the
-- braided pair over the shared bucket is COHERENT (the diamond closes). This is
-- the packed-forest property: many derivations, one shared node.
packed : (s : Tm-QSKI) (sp : Span s) → rBack sp ≡ app (viaP sp) (pBack sp)
packed = diamond
