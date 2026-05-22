------------------------------------------------------------------------
-- Substrate.Groups.Actions.S3-on-V4.HomRotations
--
-- V₄-homomorphism witnesses for the three rotation-type canonical S₃
-- elements (file-per-lemma):
--   HomRotations.HomId    — identity ([], [])
--   HomRotations.HomRot   — rotation ([a], [])
--   HomRotations.HomRot2  — rotation² ([a,a], [])
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.S3-on-V4.HomRotations where

open import Substrate.Groups.Actions.S3-on-V4.Dispatch              public
open import Substrate.Groups.Actions.S3-on-V4.HomRotations.HomId    public
open import Substrate.Groups.Actions.S3-on-V4.HomRotations.HomRot   public
open import Substrate.Groups.Actions.S3-on-V4.HomRotations.HomRot2  public
