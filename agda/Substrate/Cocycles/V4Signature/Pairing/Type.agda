------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.Pairing.Type
--
-- Pairing: which V₄ partition of AXES the orbit corresponds to.
--   α-pair = {D,C}|{S,W}; β-pair = {D,S}|{C,W}; γ-pair = {D,W}|{C,S}
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.Pairing.Type where

data Pairing : Set where
  α-pair β-pair γ-pair : Pairing
