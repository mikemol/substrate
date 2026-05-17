------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.OrbitKey.Structural
--
-- N-5 of the M-12 DBE plan. The derived bijection
--   OrbitKey ↔ V4-Nonzero × F₂
-- bundled as a `Bijection`.
--
-- OrbitKey = Pairing × Chirality (the 6-orbit index in V4Signature.agda).
-- The structural form is V4-Nonzero × F₂. The bridge is the product
-- of N-3 (Pairing ↔ V4-Nonzero) and N-4 (Chirality ↔ F₂), assembled
-- via the `_×-bij_` combinator from Foundations.Bijection.
--
-- All round-trips are inherited from the component bridges (both
-- close by `refl` in this case, so the product round-trips
-- ultimately close by `refl` as well — but the proof is mechanical
-- via cong₂ either way).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.OrbitKey.Structural where

open import Substrate.Foundations.Bijection
open import Substrate.Cocycles.V4Signature using (OrbitKey)
open import Substrate.Cocycles.V4Signature.Pairing.Structural
  using (Pairing↔V4-Nonzero)
open import Substrate.Cocycles.V4Signature.Chirality.Structural
  using (Chirality↔F₂)

------------------------------------------------------------------------
-- The product bridge — assembled mechanically by _×-bij_.
------------------------------------------------------------------------

OrbitKey↔V4-Nonzero×F₂ : Bijection OrbitKey _
OrbitKey↔V4-Nonzero×F₂ = Pairing↔V4-Nonzero ×-bij Chirality↔F₂
