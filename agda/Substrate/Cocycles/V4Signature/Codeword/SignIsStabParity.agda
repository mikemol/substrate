------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.Codeword.SignIsStabParity
--
-- DISCOVERABILITY cross-link (⟡codeword-sign-home). The theorem "the live
-- codeword's permutation-sign is the S₃-stabiliser parity" is PROVEN in
-- WitnessTower.CodewordSignEqualsStabParity, but that file lives under
-- WitnessTower/. This file re-exports it HERE, beside the Codeword.LiveS4
-- machinery it is about, so a search from the codeword side (LiveS4,
-- live-to-permutation, Selector) finds the sign result without rebuilding the
-- perm4 transport.
--
-- The result, and the CORRECTION it carries: the naive guess "selector bit
-- b₂ = sign" is FALSE (b₂ is the ordering selector, a different bit). The
-- true, proven statement is:
--   codeword-sign a sel ≡ stab-parity sel        (24 cases, refl)
--   codeword-sign is V₄-axis-INDEPENDENT         (V₄ ⊂ A₄, even)
-- and generally (all of S₄, WitnessTower.SignStabTotal):
--   sign(perm4 σ) ≡ sign(perm4 (s-for σ))        (sign factors through Stab).
--
-- --safe --without-K. Verified on Agda 2.8.0.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.Codeword.SignIsStabParity where

-- The 24-case codeword-domain result (sign = stab parity, axis-independent).
open import Substrate.WitnessTower.CodewordSignEqualsStabParity
  using (codeword-sign; stab-parity;
         codeword-sign-is-stab-parity;
         axis-independent-DC; axis-independent-DS; axis-independent-DW)

-- The general (all-of-S₄) orientation-anchored form: sign factors through the
-- Stab retraction s-for; the V₄-coset is the exact fibre.
open import Substrate.WitnessTower.SignStabTotal
  using (sign-of; sign-stab-total; sign-factors-through-s-for)
