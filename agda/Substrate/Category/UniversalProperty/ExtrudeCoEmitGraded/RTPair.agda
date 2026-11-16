------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.RTPair
--
-- Defines: RTPair
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.RTPair where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.R.Trace
open import Substrate.Foundation.Product
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Obs
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Agreeupto
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)

------------------------------------------------------------------------
-- agree-upto-as-refinement: the shrinking prefix-agreement family (320) as a FORMAL refinement operator (contrast
-- the degenerate Φ-obs, 319). agree-upto decomposes as (head t ≡ head r) × agree-upto n (tail r) (tail t) — the
-- reference r THREADS with the trace, so the fiber is over PAIRS (r,t). Φ-pair adds one head-agreement per grade
-- (properly SHRINKING, recursing both tails); mono holds; Φ-iter n ⟺ agree-upto n; gfp (all grades) = the ~-class.
------------------------------------------------------------------------

-- (⟡set1-debt, DISCHARGED) A hand-rolled `FamP : Set₁ = RealTrace → RealTrace → Set` lived here, with
-- Φ-pair / P⁰ / Φ-iter / iter→agree / agree→iter / Φ-pair-gfp-is-bisim built on it. It was the module's ONLY
-- Set₁ site. It is also REDUNDANT: the canonical Refinement-based arm below (Φ-pair-exact, P⁰-pair,
-- pair-iter→agree, pair-agree→iter, νΦ-pair→bisim) proves the same facts over `RFam RTPair`, and Fam's Set₁
-- lives once, in Category.Allegory.Refinement, where it belongs. Removed: Set₁ in a consumer module is
-- POLICY DEBT (the operator, 359), not an exemption — parameterize or reuse the canonical family type.
-- Kept as residue-note (shadow, not deletion). The Refinement arm below is the single writer.


------------------------------------------------------------------------
-- phi-pair-exact-refinement: Φ-pair as an EXACT Refinement record (Category.Allegory.Refinement) over pairs. Fam
-- (RealTrace × RealTrace) = (RealTrace × RealTrace) → Set; uncurry Φ-pair; the record + its iterate is the formal
-- shrinking refinement whose iterate-chain IS agree-upto (via the curried iter↔agree above) and gfp = the ~-class.
------------------------------------------------------------------------

RTPair : Set
RTPair = RealTrace × RealTrace
