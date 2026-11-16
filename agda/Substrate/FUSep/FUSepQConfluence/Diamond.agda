------------------------------------------------------------------------
-- Substrate.FUSep.FUSepQConfluence.Diamond
--
-- Defines: diamond
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.FUSep.FUSepQConfluence; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.FUSep.FUSepQConfluence.Diamond where

open import Substrate.Foundation.Product
import Substrate.Foundation.Product as FP   -- for the ⟡def-eq projection witnesses
open import Substrate.Foundation.Nat.Nat
open import Substrate.FUSep.FUSepQSKI    using (atom; app) renaming (Tm-QSKI to Tm-QSKI)
open import Substrate.Foundation.Eq
open import Substrate.FUSep.FUSepQConfluence.Op
open import Substrate.FUSep.FUSepQConfluence.Span
open import Substrate.FUSep.FUSepQSKI



-- LOCAL CONFLUENCE (the diamond): the two edges out of s CONVERGE — both paths
-- reconstruct the SAME node s via their residues. The braiding σ reorders the two
-- indexes; this proves the reorder lands on the same bucket node. THIS is
-- confluence as the braiding of the two hierarchical indexes.
diamond : (s : Tm-QSKI) (sp : Span s) → rBack sp ≡ app (viaP sp) (pBack sp)
diamond s sp = trans-≡ (sym-≡ (r-recon sp)) (p-recon sp)
  where
    sym-≡ : {A : Set} {x y : A} → x ≡ y → y ≡ x
    sym-≡ refl = refl
    trans-≡ : {A : Set} {x y z : A} → x ≡ y → y ≡ z → x ≡ z
    trans-≡ refl q = q
