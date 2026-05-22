------------------------------------------------------------------------
-- Substrate.Category.ReferenceOrbit.Permanence
--
-- The second axis: permanence — whether the reference grows the
-- rule table (PermanentRule) or is one-shot (OneShot).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.ReferenceOrbit.Permanence where

data Permanence : Set where
  PermanentRule  : Permanence
  OneShot        : Permanence
