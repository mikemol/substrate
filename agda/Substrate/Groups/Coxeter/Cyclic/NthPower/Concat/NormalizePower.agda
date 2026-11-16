------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Cyclic.NthPower.Concat.NormalizePower
--
-- Defines: normalize-power
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Groups.Coxeter.Cyclic.NthPower.Concat; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

-- ⚑ ABOVE THE HEADER because the telescope names these types;
-- an import below the header binds nothing for the header itself.
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Groups.Coxeter.Word
open import Substrate.Groups.Coxeter.Cyclic.Base.Gen
module Substrate.Groups.Coxeter.Cyclic.NthPower.Concat.NormalizePower (n : ℕ) where

open import Substrate.Groups.Coxeter.Cyclic.Existential n
open import Substrate.Groups.Coxeter.Cyclic.Base n
-- ⛑ Ⓡ2ᵈ: the `Defs` LEAVES this shard cites, derived by
-- `rewire_fcr --siblings Defs <file>` — a SET, not a prefix. `Defs`'s
-- re-opens are bare (Ⓡ1), so a leaf-defined name no longer arrives
-- through the root. Each leaf carries its OWN minimal telescope, so the
-- argument lists differ by leaf and are read from each header.
open import Substrate.Groups.Coxeter.Cyclic.Base.Insert n
open import Substrate.Groups.Coxeter.Cyclic.Base.Power
open import Substrate.Groups.Coxeter.Cyclic.Core n
-- ⚑ `normalize` REACHED THROUGH TWO CONDUITS pre-split (Existential → List-
-- Presentation), named nowhere (Ⓑ2c-BRIDGE10″).  Applied to the same five
-- arguments `Core` supplies, so both see the SAME instance — a second, differently
-- applied copy would give `normalize` a distinct type and fail at the use site.
open import Substrate.Groups.Coxeter.ListPresentation
  Gen Canonical-ex c-ε insert insert-canonical-ex



------------------------------------------------------------------------
-- 2. normalize-power + iter-power-mod / power-cyclic-normalize.
--
-- Connects the cyclic structure on canonical positions to the
-- unbounded Word form via mod-suc.
------------------------------------------------------------------------

normalize-power : (k : ℕ) → normalize (power k) ≡ iter k (insert a) []
normalize-power zero    = refl
normalize-power (suc k) = cong (insert a) (normalize-power k)
