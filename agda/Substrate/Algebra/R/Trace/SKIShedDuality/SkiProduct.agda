------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.SKIShedDuality.SkiProduct
--
-- Defines: ski-product
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.R.Trace.SKIShedDuality; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Algebra.R.Trace.SKIShedDuality.SkiProduct where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Algebra.Wedge.Product
open import Substrate.Algebra.Wedge.Product.Term
open import Substrate.Algebra.R.Trace.Bisim.Op
open import Substrate.Algebra.R.Trace.Bisim.Refl
open import Substrate.Foundation.Eq
open import Substrate.Algebra.R.Trace.SKIShedDuality.Cost
open import Substrate.Algebra.R.Trace.SKIShedDuality.Shed
-- ⚑ `I` and `_∙_` ARE CONSTRUCTORS OF `Tm`, and the splitter's SEED could not see them.
-- The body uses `shed⟨ I ⟩` and `peeled s ∙ peeled t`; both names live in `.Tm`, indented
-- under `data Tm : Set where`. The seed computed this leaf's imports from TOP-LEVEL names,
-- so it imported `Cost` and `Shed` (whose heads it could see) and omitted the module
-- providing the constructors — leaving a leaf that had never typechecked.
-- ⚑⚑ SAME CLASS AS THE `leaf_map` DEFECT FIXED TODAY, one stage earlier: there the REWIRE's
-- name→leaf map missed `S`/`K`/`I`; here the SPLIT's own seed did. Fixing the map does not
-- fix the seed — they are two readers of the same blind spot.
open import Substrate.Algebra.R.Trace.SKIShedDuality.Tm



------------------------------------------------------------------------
-- ② THE SN / LEAST-FP SIDE: the inductive cost chain (WedgeTerm reskin), with the
-- leaf grades WIRED from cost automatically — ⟡ski-cost-autochain.
------------------------------------------------------------------------
-- ⟡set1-paydown: GradedProduct's carrier family is now its param (Shed).
ski-product : GradedProduct Shed
ski-product = record
  { u   = shed⟨ I ⟩
  ; _∧_ = λ {i}{j} s t → shed⟨ peeled s ∙ peeled t ⟩
  }
