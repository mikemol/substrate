------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitorbitkeyof
--
-- Defines: coemit-orbitkey-of
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitorbitkeyof where

open import Substrate.Foundation.Product
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Cocycles.V4Signature.Chirality.Type
open import Substrate.Cocycles.V4Signature.Pairing.Type
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.F2
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitv4pairings
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitorbitkey
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans


-- the 6 orbit-keys: each pairing (3) × each chirality (2). Coemit's grading supplies the Pairing side (via V₄) and
-- the Chirality side (the orientation) — together the Stab(D)-rep index. (The 3 axes are the carrier, not the index.)
coemit-orbitkey-of : F₂ → F₂ → Chirality → coemit-orbitkey
coemit-orbitkey-of m o c = coemit-v4-pairings m o , c
