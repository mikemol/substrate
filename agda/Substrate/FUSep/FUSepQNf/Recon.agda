------------------------------------------------------------------------
-- Substrate.FUSep.FUSepQNf.Recon
--
-- Defines: recon
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.FUSep.FUSepQNf; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.FUSep.FUSepQNf.Recon where

open import Substrate.Foundation.Nat.Nat
open import Substrate.FUSep.FUSepQBridge.Anon
open import Substrate.FUSep.FUSepQBridge.Cong
open import Substrate.FUSep.FUSepQBridge.Cong2
open import Substrate.FUSep.FUSepQBridge.Eqtrans
open import Substrate.FUSep.FUSepQSKI    using (atom; app) renaming (Tm-QSKI to Tm-QSKI)
open import Substrate.Foundation.Eq
open import Substrate.FUSep.FUSepQNf.Wit
open import Substrate.FUSep.FUSepQSKI
open import Substrate.Category.CentralizerDescent.Tree



-- the SINGLE recon over the common carrier — follows the backpointer, uniformly.
recon : Wit → Tm-QSKI → Tm-QSKI
recon (redW parent) _ = parent      -- follow the SPPF backpointer to the parent
recon (peelW a)     f = app f a      -- recompute the parent from the residue arg
