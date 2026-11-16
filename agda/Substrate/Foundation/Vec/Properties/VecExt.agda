------------------------------------------------------------------------
-- Substrate.Foundation.Vec.Properties.VecExt
--
-- Defines: vec-ext
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Vec.Properties; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Vec.Properties.VecExt where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Vec
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Vec.Properties.Private
open import Substrate.Foundation.Vec.Properties.TabulateComplookup
open import Substrate.Foundation.Vec.Properties.TabulateCong



vec-ext :
  {A : Set ℓ} {n : ℕ}
  (u v : Vec A n) → ((i : Fin n) → lookup u i ≡ lookup v i) → u ≡ v
vec-ext u v p =
  trans (sym (tabulate∘lookup u))
        (trans (tabulate-cong (lookup u) (lookup v) p) (tabulate∘lookup v))
