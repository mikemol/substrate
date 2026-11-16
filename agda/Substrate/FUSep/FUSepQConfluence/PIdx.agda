------------------------------------------------------------------------
-- Substrate.FUSep.FUSepQConfluence.PIdx
--
-- Defines: PIdx
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.FUSep.FUSepQConfluence; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.FUSep.FUSepQConfluence.PIdx where

open import Substrate.Foundation.Product
import Substrate.Foundation.Product as FP   -- for the ⟡def-eq projection witnesses
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Eq
-- ⚑ Ⓑ11: `Tm⟦27e68fcc⟧` WAS NEVER A REAL NAME — it is a dedup-pass ALIAS. The
-- pre-split parent (3b0635cc:29) read
--     open import …FUSepQSKI using (atom; app) renaming (Tm to Tm⟦27e68fcc⟧)
-- ⚑ THAT LINE IS A QUOTATION OF `3b0635cc` AND MUST NOT BE REWRITTEN. A later
-- `rename_at_source Tm → Tm-QSKI` rewrote it to `renaming (Tm-QSKI to …)`,
-- corrupting the historical record into something the commit never said — the
-- Ⓕ-PROSE-DECORRUPT class, where a sweep edits prose describing the past.
-- ⚑ AND THE `⟦hash⟧` DOES NOT MARK DEFINITIONAL EQUALITY — it is a SHAPE pin
-- minted by `_agdatext.shape_decls` and demanded by `check_import_shape` when a
-- name has DIFFERING shapes across modules. My earlier reading here was backwards.
-- The ban sweep stripped
-- that `renaming`, and the split then emitted leaves citing an alias with NO
-- source anywhere in the tree (`agda_defs Tm⟦27e68fcc⟧` → no definer), which is
-- why this read as a MISSING DEFINITION rather than a dropped import.
-- The bare name is the ban-compliant spelling; `FUSepQSKI` is its one home.
open import Substrate.FUSep.FUSepQSKI


PIdx = Tm-QSKI × Tm-QSKI    -- (arg, function)
