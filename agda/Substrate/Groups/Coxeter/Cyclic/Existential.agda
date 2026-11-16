------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Cyclic.Existential
--
-- The single-index existential view Canonical-ex = Σ Fin Canonical-at,
-- + the ex-versions of c-ε / canonical-cover / insert-canonical /
-- inv-canonical, + opens ListPresentation's outer module (normalize
-- + normalize-canonical).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Product using (Σ; _,_; proj₁; proj₂)
open import Substrate.Groups.Coxeter.Word using (Word; [])
open import Substrate.Groups.Coxeter.Cyclic.Base.CanonicalAt
open import Substrate.Groups.Coxeter.Cyclic.Base.Gen

module Substrate.Groups.Coxeter.Cyclic.Existential (n : ℕ) where

-- ⚑ WAS `…Cyclic.Bridge n using (insert-canonical)` — a module DISSOLVED into
-- one leaf per theorem by the ban-decompose commit (771283c8).  The split ran;
-- the REWIRE did not, so this named a module with no file (Ⓑ2c-BRIDGE10).
open import Substrate.Groups.Coxeter.Cyclic.Bridge.InsertCanonical n
open import Substrate.Groups.Coxeter.Cyclic.Base n using (Gen; Canonical-at; c-here; insert; σ)
-- ⛑ Ⓡ2ᵈ: the `Defs` LEAVES this shard cites, derived by
-- `rewire_fcr --siblings Defs <file>` — a SET, not a prefix. `Defs`'s
-- re-opens are bare (Ⓡ1), so a leaf-defined name no longer arrives
-- through the root. Each leaf carries its OWN minimal telescope, so the
-- argument lists differ by leaf and are read from each header.
open import Substrate.Groups.Coxeter.Cyclic.Base.Insert n
open import Substrate.Groups.Coxeter.Cyclic.Base.Op n
-- ⚑ A SECOND DISSOLVED PARENT, same commit.  `Cyclic.Inverse` was split into
-- five leaves and its consumers were not rewired either; this file used three of
-- them (`inv`, `inv-pos`, `inv-canonical`), each now named at its own home.
open import Substrate.Groups.Coxeter.Cyclic.Inverse.Inv n
open import Substrate.Groups.Coxeter.Cyclic.Inverse.InvPos n
open import Substrate.Groups.Coxeter.Cyclic.Inverse.InvCanonical n


------------------------------------------------------------------------
-- Existential view.
------------------------------------------------------------------------

Canonical-ex : Word Gen → Set
Canonical-ex w = Σ (Fin (suc n)) (Canonical-at w)

------------------------------------------------------------------------
-- Generic position-parametric pattern synonym.
--
-- Replaces the per-Zₙ named ladder (c-aa / c-aaa / c-aaaa / …) with
-- one parametric form `c-pos k`. Downstream consumers that previously
-- pattern-matched on `Z₃.c-aa` etc. can write `Z₃.c-pos ₂`
-- — a single uniform shape across all cyclic groups.
------------------------------------------------------------------------

pattern c-pos k = k , c-here _

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

