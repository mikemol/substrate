------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.S4Iso
--
-- S10 of slice 3: the bijection TotalSpace ≃ S₄ — the catalog's
-- "the 24 ARE S₄" identification (M41 v19) made constructive.
--
-- TotalSpace of the CY-5 cocycle = Σ OrbitKey (λ _ → V₄) — pairs of
-- (orbit-key, V₄ fiber-position). Under the V₄ ⋊ S₃ ≅ S₄
-- factorisation (proved in Substrate.Groups.SemidirectProduct), each
-- such pair corresponds bijectively to a permutation in S₄.
--
-- DECOMPOSED 2026-05-21 per [[file-size-one-pass-rewrite]]: the
-- former 638-line module is now a thin re-export shim over six
-- submodules in S4Iso/.
--
-- Submodule decomposition:
--   S4Iso.Injective     — σ-injective + 9 Axis-constructor distinctness
--                          lemmas (C≢D, S≢D, ..., W≢S).
--   S4Iso.StabElements  — stab-id, stab-sw, stab-cs, stab-cw,
--                          stab-csw, stab-cws + fixes-* proofs.
--   S4Iso.Anchor        — orbit-key-to-stab-anchor + D/C/S/W
--                          specialisations + stop-anchoring theorems.
--   S4Iso.Classify      — TotalSpace, total-to-s4, classify-CS,
--                          stab-d-to-orbit-key, s4-to-total,
--                          ok-round-trip.
--   S4Iso.Cases         — 6 per-case lemmas (case-α-even, ..., case-γ-odd).
--   S4Iso.Roundtrips    — stab-round-trip, σ-round-trip,
--                          total-round-trip.
--
-- The bundled TotalSpace≃S₄ record + bijection are defined here.
--
-- All public names from the original file remain available via the
-- re-exports below; existing callers need no edits.
--
-- See: catalog/cocycles.md § CY-5 — "The 24 ARE S₄".
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.S4Iso where

open import Substrate.Foundation.Product using (_,_)
open import Substrate.Foundation.Eq using (_≡_)

open import Substrate.Groups.S4 using (Permutation; _≈_)

open import Substrate.Cocycles.V4Signature.S4Iso.Injective    public
open import Substrate.Cocycles.V4Signature.S4Iso.StabElements public
open import Substrate.Cocycles.V4Signature.S4Iso.Anchor       public
open import Substrate.Cocycles.V4Signature.S4Iso.Classify     public
open import Substrate.Cocycles.V4Signature.S4Iso.Cases        public
open import Substrate.Cocycles.V4Signature.S4Iso.Roundtrips   public

------------------------------------------------------------------------
-- TotalSpace ≃ S₄: the bijection packaged.
--
-- Cannot use stdlib's `_↔_` (= Inverse on propositional setoids), since
-- σ-round-trip is `_≈_` (pointwise) rather than `_≡_`.
------------------------------------------------------------------------

record TotalSpace≃S₄ : Set where
  field
    to       : TotalSpace → Permutation
    from     : Permutation → TotalSpace
    to-from  : (σ : Permutation) → to (from σ) ≈ σ
    from-to  : (tot : TotalSpace) → from (to tot) ≡ tot

TotalSpace≃S₄-bijection : TotalSpace≃S₄
TotalSpace≃S₄-bijection = record
  { to      = total-to-s4
  ; from    = s4-to-total
  ; to-from = σ-round-trip
  ; from-to = total-round-trip
  }
