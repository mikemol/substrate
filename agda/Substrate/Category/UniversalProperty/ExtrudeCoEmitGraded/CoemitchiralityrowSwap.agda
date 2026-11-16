------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.CoemitchiralityrowSwap
--
-- Defines: coemit-chirality-rowSwap
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.CoemitchiralityrowSwap where

open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Cocycles.V4Signature.Chirality.Type
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Category.Comonoid.Sites.V4
import Substrate.Algebra.R.Trace.V4FullCocycle as V4


-- (3) coemit-chirality-orientation: the CANONICAL orientation is chirality = which coset of A₄ in S₄ (even/odd),
--     NOT my dual-grade₃ guess. Reuse the canonical Chirality +F V4Full's chirality-of (rowSwap is the parity flip).

coemit-chirality-rowSwap : V4.chirality-of V4.rowSwap-gen ≡ odd    -- the det-flip generator is the ODD coset (S₄\A₄)
coemit-chirality-rowSwap = V4.chirality-rowSwap
