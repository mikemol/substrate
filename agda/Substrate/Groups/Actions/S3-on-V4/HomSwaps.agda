------------------------------------------------------------------------
-- Substrate.Groups.Actions.S3-on-V4.HomSwaps
--
-- V₄-homomorphism witnesses for the three swap-type canonical S₃
-- elements + the act-hom dispatcher and lifted full-action property
-- (file-per-lemma):
--   HomSwaps.HomSwapAB           — swap αβ ([], [a])
--   HomSwaps.HomSwapAG           — swap αγ ([a], [a])
--   HomSwaps.HomSwapBG           — swap βγ ([a,a], [a])
--   HomSwaps.ActHomOnCanonical   — 6-case dispatcher
--   HomSwaps.ActHom              — full action lifted via normalize-canonical
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.S3-on-V4.HomSwaps where

open import Substrate.Groups.Actions.S3-on-V4.HomRotations              public
open import Substrate.Groups.Actions.S3-on-V4.HomSwaps.HomSwapAB         public
open import Substrate.Groups.Actions.S3-on-V4.HomSwaps.HomSwapAG         public
open import Substrate.Groups.Actions.S3-on-V4.HomSwaps.HomSwapBG         public
open import Substrate.Groups.Actions.S3-on-V4.HomSwaps.ActHomOnCanonical public
open import Substrate.Groups.Actions.S3-on-V4.HomSwaps.ActHom            public
