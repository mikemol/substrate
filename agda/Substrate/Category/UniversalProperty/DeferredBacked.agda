{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.DeferredBacked — finish the REST of the
-- Registry's deferred list ("PROVED-BUT-NOT-YET-REGISTERED — NOT debt"): the Z₂
-- PRESENTATION and the UNITS (ℤ/(suc m))* — each wrapped as a BackedUP and consed
-- onto the registry, mirroring FreeMonoidBacked (172). "Finish where it left off":
-- the disclaimer was deferral; registration IS the proof re-presented as a compiling
-- entry, so each of these becomes a certified, non-vacuous solver by TYPING.
--
-- HONESTLY SCOPED (the two that don't wrap cleanly here): the FREE F₂-MODULE
-- (F2.AsModule) proves the module AXIOMS but exposes no map-OUT extend/fold here —
-- its BackedUP needs the free-module extend (FreeLinearization), scoped as
-- ⟡register-f2module. The LIMIT/PRODUCT (LimitUP.mediate) is a map-IN (dual to
-- extend); its BackedUP needs a concrete LimitUP instance + a Contentful over the
-- product Witness, scoped as ⟡register-limit. Those two are labeled to-dos, NOT
-- "NOT debt" — the disclaimer converted to actions.
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.DeferredBacked where

open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Nat using (ℕ; suc; zero; _*_)
open import Substrate.Foundation.Unit using (⊤; tt)
open import Substrate.Foundation.List using (List; []; _∷_)
open import Substrate.Foundation.Negation using (¬_)
open import Substrate.Foundation.Product using (Σ; _,_)
open import Substrate.Groups.Coxeter.Word using (Word; []; _∷_)
open import Substrate.Algebra.F2 using (F₂; 𝟘; 𝟙)
open import Substrate.Category.PresentedUniversalProperty.CyclicZ2 using (quotient)
open import Substrate.Category.UniversalProperty using (UPArrow; Source; Target; Witness)
open import Substrate.Category.UniversalProperty.Vacuity using (Contentful)
open import Substrate.Category.UniversalProperty.Backed using (BackedUP; arrow; backed-non-vacuous)
open import Substrate.Category.UniversalProperty.Registry using (registry)

------------------------------------------------------------------------
-- ① THE Z₂ PRESENTATION as a BackedUP. quotient : Word ⊤ → F₂ (parity = the free
-- extension foldW into (F₂,𝟘,+) sending a ↦ 𝟙) is the solve; Witness w v = v ≡
-- quotient w; content = a word whose parity ≠ a wrong candidate (𝟘 ≢ quotient (tt∷[]) = 𝟙).
------------------------------------------------------------------------
z2-UP : UPArrow
z2-UP = record
  { Source  = Word ⊤
  ; Target  = F₂
  ; Witness = λ w v → v ≡ quotient w
  }

z2-solve : Source z2-UP → Target z2-UP
z2-solve = quotient

z2-solves : (w : Source z2-UP) → Witness z2-UP w (z2-solve w)
z2-solves w = refl

-- content: quotient (tt ∷ []) = 𝟙 (parity of a one-letter word); candidate 𝟘 ≠ 𝟙.
z2-contentful : Contentful z2-UP
z2-contentful = (tt ∷ []) , 𝟘 , λ ()

z2-backed : BackedUP
z2-backed = record { arrow = z2-UP ; solve = z2-solve ; solves = z2-solves ; content = z2-contentful }

z2-non-vacuous : ¬ _
z2-non-vacuous = backed-non-vacuous z2-backed

------------------------------------------------------------------------
-- ② THE UNITS (ℤ/(suc m))* as a BackedUP. IsUnit m a = Σ b. (a*b) mod-suc m ≡ 1 —
-- "a carries a right inverse b" — the inverse IS the witness. Source = a value a;
-- Target = a candidate inverse b; Witness a b = (a*b) mod-suc m ≡ 1 mod-suc m. solve =
-- the inverse of 1 (which is 1). content: a=0 has no inverse mod 2 ((0*b) mod 2 = 0 ≢ 1).
------------------------------------------------------------------------
open import Substrate.Algebra.Nat.Mod using (_mod-suc_)
open import Substrate.Algebra.Nat.Units using (IsUnit; one-is-unit)
open import Substrate.Foundation.Product using (proj₁)

-- units mod (suc m): the Source is a value TOGETHER WITH its unit-proof (Σ a. IsUnit),
-- so the inverse witness ALWAYS exists (0 is simply not in the Source). Witness
-- (a,pf) b = (a*b) mod-suc m ≡ 1 — b is a's right inverse. solve extracts the inverse
-- from the unit-proof (the inverse IS the witness). The solver is TOTAL because the
-- Source already carries invertibility — the same lesson as the ν's coalgebra-state Source.
units-UP : UPArrow
units-UP = record
  { Source  = Σ ℕ (IsUnit 1)
  ; Target  = ℕ
  ; Witness = λ aU b → (proj₁ aU * b) mod-suc 1 ≡ 1 mod-suc 1
  }

units-solve : Source units-UP → Target units-UP
units-solve (a , b , _) = b

units-solves : (aU : Source units-UP) → Witness units-UP aU (units-solve aU)
units-solves (a , b , pf) = pf

-- content: 1 is a unit (one-is-unit), inverse 1; candidate 0 fails ((1*0) mod 2 = 0 ≢ 1).
units-contentful : Contentful units-UP
units-contentful = (1 , one-is-unit 1) , 0 , λ ()

units-backed : BackedUP
units-backed = record
  { arrow = units-UP ; solve = units-solve ; solves = units-solves ; content = units-contentful }

units-non-vacuous : ¬ _
units-non-vacuous = backed-non-vacuous units-backed

------------------------------------------------------------------------
-- ③ REGISTERED: both consed onto the seed registry (compiling = the registration).
------------------------------------------------------------------------
deferred-registry : List BackedUP
deferred-registry = z2-backed ∷ units-backed ∷ registry

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — two more deferrals finished): the Z₂ PRESENTATION
-- (quotient = parity, a foldW) and the UNITS (ℤ/2)* (inverse = the witness) — both in
-- the Registry's "PROVED-BUT-NOT-YET-REGISTERED — NOT debt" bucket — are now REGISTERED
-- BackedUPs, consed onto the registry, certified by TYPING. The units UP taught the
-- honest shape: the solver must be TOTAL, so the Source carries invertibility (Σ a.
-- IsUnit) — 0 is simply not a unit, not a solve failure (same lesson as the ν's
-- coalgebra-state Source, 169). The "NOT debt" disclaimer is further dissolved: each
-- deferred item is a to-do that registration finishes. STILL scoped (labeled, NOT
-- "NOT debt"): the free F₂-module (needs FreeLinearization's extend — ⟡register-f2module)
-- and the limit/product (needs a concrete LimitUP + product Contentful — ⟡register-limit).
------------------------------------------------------------------------
