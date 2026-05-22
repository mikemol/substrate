------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Cyclic.InvCanonical
--
-- Generic inverse-canonical properties for cyclic Coxeter groups
-- (file-per-lemma):
--
--   InvCanonical.InvPosAddMod  — (toℕ (inv-pos k) + toℕ k) mod-suc n ≡ 0
--   InvCanonical.Left          — normalize (inv w ++ w) ≡ []
--   InvCanonical.Right         — normalize (w ++ inv w) ≡ []
--   InvCanonical.InvInv        — inv (inv w) ≡ w
--
-- All proved once over `Canonical-ex w` so per-Zₙ-Coxeter no longer
-- needs the cover-by-refl variants for these three lemmas.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Nat using (ℕ)

module Substrate.Groups.Coxeter.Cyclic.InvCanonical (n : ℕ) where

open import Substrate.Groups.Coxeter.Cyclic.InvCanonical.InvPosAddMod n public
open import Substrate.Groups.Coxeter.Cyclic.InvCanonical.Left          n public
open import Substrate.Groups.Coxeter.Cyclic.InvCanonical.Right         n public
open import Substrate.Groups.Coxeter.Cyclic.InvCanonical.InvInv        n public
