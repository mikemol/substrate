------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ObjectSite
--
-- ⟡odecode-hom (Phase B linchpin of ⟡ta-upterm-O-decode): the CONCRETE Hom
-- for the self-constructed object universe O = Σ ℕ TmDB (ObjectUniverse.agda).
--
-- ObjectUniverse builds O (the witness-tower total space of de-Bruijn TmDB
-- object codes) but deliberately leaves `Hom : O → O → Set` an ABSTRACT
-- parameter. This module COMMITS the concrete Hom — the piece the whole
-- remaining arc folds through (⟡odecode-residues instantiates over it;
-- ⟡odecode-decode6's function-space codes travel through it).
--
-- THE CHOICE (the minimal FAITHFUL Hom, matching O-alg.step = app c (var i)):
-- a GENERATOR X → Y is a TOWER-STEP — a de-Bruijn witnessing choice
-- i : Fin (suc (grade X)) whose target Y is the rung-raised object
-- (suc grade , app (code X) (var i)). The morphisms of the site are then
-- `UPTerm O Hom` (the FREE category on these generators; id = [], compose =
-- ++ᵤ via UPCategory-canonical) — paths up the tower. This is the FREE
-- construction, primary; a concrete non-free eval-target category (making
-- `Hom` itself a category so `eval : UPTerm O Hom → Hom` instantiates) is a
-- downstream ENRICHMENT, not needed here.
--
-- NOTE (a refinement to the residue recipe): because the tower-step generators
-- are NOT a category (Hom X X is empty — a step always raises the grade), the
-- residues work over the FREE category via ++ᵤ + its laws (word-structure), NOT
-- via `eval`-into-a-rich-Hom (which needs `Hom` to be a UPCategory).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.ObjectSite where

open import Substrate.Foundation.Nat using (ℕ; suc)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.To
open import Substrate.Foundation.Product using (Σ; _,_; proj₁; proj₂)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Category.UniversalProperty.TmDBGodel using (TmDB; var; app)
open import Substrate.Category.UniversalProperty.ObjectUniverse using (O; C)
open import Substrate.Category.UniversalProperty.Term using (UPTerm; []; _∷_; _++ᵤ_)
open import Substrate.Category.UniversalProperty.Category using (UPCategory; UPCategory-canonical)

------------------------------------------------------------------------
-- 1. The concrete Hom: tower-step GENERATORS.
------------------------------------------------------------------------

Hom : O → O → Set
Hom X Y = Σ (Fin (suc (proj₁ X)))
            (λ i → Y ≡ (suc (proj₁ X) , app (proj₂ X) (var (toℕ i))))

-- The generator constructor: the i-th tower-step out of X.
step-gen : (X : O) (i : Fin (suc (proj₁ X)))
         → Hom X (suc (proj₁ X) , app (proj₂ X) (var (toℕ i)))
step-gen X i = i , refl

------------------------------------------------------------------------
-- 2. The site: objects = O, morphisms = the FREE category on Hom (words of
--    tower-steps). id = [], compose = ++ᵤ (via the canonical instance).
------------------------------------------------------------------------

site-hom : O → O → Set
site-hom = UPTerm O Hom

O-site : UPCategory O site-hom
O-site = UPCategory-canonical O Hom

-- Identity and composition of the site (the residues consume these).
site-id : (X : O) → site-hom X X
site-id _ = []

site-compose : {X Y Z : O} → site-hom X Y → site-hom Y Z → site-hom X Z
site-compose f g = f ++ᵤ g
