------------------------------------------------------------------------
-- Substrate.Groups.Actions.S3-on-V4.HomSwaps
--
-- Re-export shim for the S₃-on-V₄ homomorphism story. The per-swap
-- Cayley-table leaves (HomSwapAB/AG/BG) were retired along with the
-- rotation leaves: ActHomOnCanonical now proves the action is a
-- homomorphism STRUCTURALLY (act-on-canonical ≡ rot-pow ∘ swap-pow,
-- iterates of the two generator-homs), so the 6 per-canonical tables are
-- corollaries and were dead. Surfaces the live pieces:
--   HomSwaps.ActHomOnCanonical — homomorphism for every canonical n,h
--   HomSwaps.ActHom            — full action lifted via normalize-canonical
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.S3-on-V4.HomSwaps where

open import Substrate.Groups.Actions.S3-on-V4.HomRotations
open import Substrate.Groups.Actions.S3-on-V4.HomSwaps.ActHomOnCanonical
open import Substrate.Groups.Actions.S3-on-V4.HomSwaps.ActHom