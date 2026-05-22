------------------------------------------------------------------------
-- Substrate.Groups.Actions.S3-on-V4.Twist
--
-- The dihedral generator-level twist relations (file-per-lemma):
--   Twist.ActEqualsPow      — act-on-canonical ↔ rot-pow ∘ swap-pow
--   Twist.SwapRotateTwist   — swap-αβ ∘ rotate ≡ rotate² ∘ swap-αβ
--   Twist.RotPowSwapTwist   — lifted twist on canonical n
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.S3-on-V4.Twist where

open import Substrate.Groups.Actions.S3-on-V4.Generators              public
open import Substrate.Groups.Actions.S3-on-V4.Twist.ActEqualsPow     public
open import Substrate.Groups.Actions.S3-on-V4.Twist.SwapRotateTwist  public
open import Substrate.Groups.Actions.S3-on-V4.Twist.RotPowSwapTwist  public
