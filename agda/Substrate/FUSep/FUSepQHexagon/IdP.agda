------------------------------------------------------------------------
-- Substrate.FUSep.FUSepQHexagon.IdP
--
-- Defines: idP
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.FUSep.FUSepQHexagon; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.FUSep.FUSepQHexagon.IdP where

open import Substrate.Foundation.Product
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Eq
open import Substrate.FUSep.FUSepQHexagon.PIdx
open import Substrate.FUSep.FUSepQHexagon.Braid
open import Substrate.FUSep.FUSepQHexagon.OtimesTo
open import Substrate.FUSep.FUSepQHexagon.AssocTo



------------------------------------------------------------------------
-- THE HEXAGON (Wedge/Monoidal.hexagon): the braiding coheres with the associator
-- — three rewrites (R,P,Q) reorder coherently. Both paths reshuffle ((r,p),q) to
-- (p,(q,r)). THIS is the 3-way confluence coherence (Yang-Baxter): the tiling of
-- diamonds that lets local confluence PROPAGATE. All refl (product carrier).
--   assoc→ ∘ braid ∘ assoc→        (braid R past (P⊗Q))
--     ≡  (id ⊗→ braid) ∘ assoc→ ∘ (braid ⊗→ id)   (braid R past P, then past Q)
------------------------------------------------------------------------
idP : PIdx → PIdx
idP x = x
