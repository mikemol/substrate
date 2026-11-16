------------------------------------------------------------------------
-- Substrate.Lojban.AsCCC.RetroactiveAlignment.ProgramOnSingleIsOp
--
-- Defines: program-on-single-is-op
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Lojban.AsCCC.RetroactiveAlignment; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Lojban.AsCCC.RetroactiveAlignment.ProgramOnSingleIsOp where

open import Substrate.Lojban.Gismu
open import Substrate.Lojban.Word Gismu
open import Substrate.Lojban.AsCCC
open import Substrate.Foundation.Eq
open import Substrate.Algebra.F2.AES.Round



------------------------------------------------------------------------
-- 2. The AsCCC Bridge's `program` agrees with the basis-action on
-- single-symbol words.
--
-- For any State + per-gismu operation op, the Bridge program
-- applied to a single-gismu word IS the basis operation. This is
-- the FreeOverBasis η-coherence at the program layer.
--
-- (The substantive program-execute-agree from L10 is the n-gismu
-- generalisation; this is the n=1 specialisation that ties
-- directly to the FreeOverBasis structure's η field.)
------------------------------------------------------------------------

program-on-single-is-op :
  (State : Set) (op : Gismu → State → State) →
  (g : Gismu) (s : State) →
  Bridge.program State op (single g) s ≡ op g s
program-on-single-is-op _ _ _ _ = refl
