------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.Codeword
--
-- The 24+8 = 32 = 2⁵ codeword ambient — the catalog's "raw codeword
-- space" reading of CY-5's signature structure, under the multi-
-- reading ambient discipline. File-per-lemma:
--
--   Codeword.Type                       — Codeword + bit accessors
--   Codeword.IsReserved                 — predicate + decidability
--   Codeword.Subtypes                   — Reserved (8) + Live (24)
--   Codeword.AxisBits                   — axis-from-bits / axis-to-bits
--                                          + round-trip identities
--   Codeword.ReservedSignedMaps         — reserved-to-signed +
--                                          signed-to-reserved
--   Codeword.ReservedSignedRoundTrip    — left-inv + right-inv proofs
--   Codeword.Iso                        — Reserved ↔ Axis × Bool
--
-- Discipline (see catalog clarification 2026-05-15):
--   * Ambient is the largest natural cardinality: 32 codewords / Bool⁵.
--   * Load-bearing predicate IsReserved : Codeword → Set carves the 8.
--   * Reserved / Live are derived Σ-subtypes.
--   * Each "reading" of 32+8 is a SEPARATE equivalence — Reserved ↔
--     Axis × Bool here, Live ↔ Permutation (= S₄) elsewhere, Hodge
--     swap at dim 4 elsewhere. None is privileged.
--
-- Bit encoding convention (multiple equivalent encodings exist):
--
--   b₀ b₁  | axis (4 options)           D = (false, false)
--                                       C = (true,  false)
--                                       S = (false, true)
--                                       W = (true,  true)
--   b₂     | reserved: sign; live: ordering selector
--   b₃ b₄  | (false, false) = reserved; otherwise = live
--
-- See:
--   * catalog/cocycles.md § CY-5 — 24+8 reading
--   * [[feedback-multi-reading-ambient-discipline]]
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.Codeword where

open import Substrate.Cocycles.V4Signature.Codeword.Type                    public
open import Substrate.Cocycles.V4Signature.Codeword.IsReserved              public
open import Substrate.Cocycles.V4Signature.Codeword.Subtypes                public
open import Substrate.Cocycles.V4Signature.Codeword.AxisBits                public
open import Substrate.Cocycles.V4Signature.Codeword.ReservedSignedMaps      public
open import Substrate.Cocycles.V4Signature.Codeword.ReservedSignedRoundTrip public
open import Substrate.Cocycles.V4Signature.Codeword.Iso                     public
