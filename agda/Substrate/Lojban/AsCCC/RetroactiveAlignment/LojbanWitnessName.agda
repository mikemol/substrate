------------------------------------------------------------------------
-- Substrate.Lojban.AsCCC.RetroactiveAlignment.LojbanWitnessName
--
-- Defines: lojban-witness-name
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Lojban.AsCCC.RetroactiveAlignment; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Lojban.AsCCC.RetroactiveAlignment.LojbanWitnessName where

open import Substrate.Lojban.AsFreeOverBasis.LojbanWitness
open import Substrate.Category.FreeOverBasis
open import Substrate.Foundation.Eq



lojban-witness-name : name lojban-witness ≡ Lojban
lojban-witness-name = refl

------------------------------------------------------------------------
-- 4. Capstone.
--
-- The "shared parent extraction is deferred" note from L10 AsCCC
-- is SUPERSEDED. The parent primitive (FreeOverBasis) exists;
-- the Lojban Bridge is structurally an instance via lojban-witness;
-- the basis-action lifts through the L8 free-monoid universal
-- property (Substrate.Lojban.WordAlgebra) which the parent
-- primitive abstractly named.
--
-- D7 provides the sister retroactive alignment on the Toki Pona
-- side; D8 unifies both into a single substrate-internal record.
------------------------------------------------------------------------
