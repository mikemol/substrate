------------------------------------------------------------------------
-- Substrate.Groups.Actions.S3-on-V4.HomRotations
--
-- Re-export shim. The former per-rotation homomorphism leaves
-- (HomId/HomRot/HomRot2, each a 16-refl Cayley table) were retired: the
-- action's homomorphism property is now proved STRUCTURALLY in
-- HomSwaps.ActHomOnCanonical (rot-pow/swap-pow are iterates of the two
-- generator-homs rotate-IsHom/swap-αβ-IsHom), so the per-canonical tables
-- are corollaries and were dead. This shim now just surfaces Dispatch.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.S3-on-V4.HomRotations where

open import Substrate.Groups.Actions.S3-on-V4.Dispatch public
