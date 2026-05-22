------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Cyclic.Existential
--
-- The single-index existential view Canonical-ex = Σ Fin Canonical,
-- + the ex-versions of c-ε / canonical-cover / insert-canonical /
-- inv-canonical, + opens ListPresentation's outer module (normalize
-- + normalize-canonical).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Nat using (ℕ; suc)
open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Product using (Σ; _,_; proj₁; proj₂)
open import Substrate.Groups.Coxeter.Word using (Word; [])

module Substrate.Groups.Coxeter.Cyclic.Existential (n : ℕ) where

open import Substrate.Groups.Coxeter.Cyclic.Inverse n public

------------------------------------------------------------------------
-- Existential view.
------------------------------------------------------------------------

Canonical-ex : Word Gen → Set
Canonical-ex w = Σ (Fin (suc n)) (Canonical w)

c-ε : Canonical-ex []
c-ε = zero , c-here zero

canonical-cover-ex :
  ∀ {ℓ} (P : ∀ {w} → Canonical-ex w → Set ℓ) →
  ((k : Fin (suc n)) → P (k , c-here k)) →
  ∀ {w} (c : Canonical-ex w) → P c
canonical-cover-ex P f (k , c-here .k) = f k

insert-canonical-ex : (g : Gen) {w : Word Gen} → Canonical-ex w → Canonical-ex (insert g w)
insert-canonical-ex g (k , c) = σ k , insert-canonical g c

inv-canonical-ex : ∀ {w} → Canonical-ex w → Canonical-ex (inv w)
inv-canonical-ex (k , c) = inv-pos k , inv-canonical c

------------------------------------------------------------------------
-- Open ListPresentation's outer module — provides normalize +
-- normalize-canonical (using Canonical-ex as the single-index view).
------------------------------------------------------------------------

open import Substrate.Groups.Coxeter.ListPresentation
  Gen Canonical-ex c-ε insert insert-canonical-ex public
