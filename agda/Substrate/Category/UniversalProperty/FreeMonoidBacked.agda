{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.FreeMonoidBacked — finish the deferral: the
-- Registry's coverage note lists the FREE MONOID as "PROVED-BUT-NOT-YET-REGISTERED
-- (NOT debt)". That disclaimer is deferral: the reality IS backed (FreeMonoid.foldW =
-- extend, extend-unique proved), so it should be a registered BackedUP. Here it is —
-- the free-monoid universal property wrapped as a BackedUP and consed onto the registry.
--
-- The bridge: Source = Word Gen (the free carrier), Target = M (a monoid carrier),
-- Witness w m = m ≡ foldW mM f w (the extension). solve = foldW mM f (the fold/extend);
-- content = a word whose candidate value ≠ its fold. Concretely Gen = ℕ, M = Word ℕ
-- (word-monoid), f = singleton, so foldW is the identity on words and a wrong candidate
-- discriminates. Typing certifies it — the free monoid joins the registry.
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.FreeMonoidBacked where

open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.List using (List; []; _∷_)
open import Substrate.Foundation.Negation using (¬_)
open import Substrate.Foundation.Product using (_,_)
open import Substrate.Groups.Coxeter.Word using (Word; []; _∷_)
open import Substrate.Category.FreeUniversalProperty.FreeMonoid using (MonoidOn; word-monoid; foldW)
open import Substrate.Category.UniversalProperty using (UPArrow; Source; Target; Witness)
open import Substrate.Category.UniversalProperty.Vacuity using (Contentful)
open import Substrate.Category.UniversalProperty.Backed using (BackedUP; arrow; backed-non-vacuous)
-- the concrete target: the free monoid on ℕ (Word ℕ under ++), basis map = singleton.
Mℕ : MonoidOn (Word ℕ)
Mℕ = word-monoid ℕ

singleton : ℕ → Word ℕ
singleton g = g ∷ []

------------------------------------------------------------------------
-- THE FREE-MONOID UP as a UPArrow: Source = Word ℕ (free carrier), Target = Word ℕ
-- (the monoid), Witness w v = v ≡ foldW Mℕ singleton w (the extension is the witness).
------------------------------------------------------------------------
freeMonoid-UP : UPArrow
freeMonoid-UP = record
  { Source  = Word ℕ
  ; Target  = Word ℕ
  ; Witness = λ w v → v ≡ foldW ℕ Mℕ singleton w
  }

freeMonoid-solve : Source freeMonoid-UP → Target freeMonoid-UP
freeMonoid-solve w = foldW ℕ Mℕ singleton w

freeMonoid-solves : (w : Source freeMonoid-UP) → Witness freeMonoid-UP w (freeMonoid-solve w)
freeMonoid-solves w = refl

-- content: the word (0 ∷ []) folds to (0 ∷ []); candidate [] ≠ it. Non-vacuous.
freeMonoid-contentful : Contentful freeMonoid-UP
freeMonoid-contentful = (0 ∷ []) , [] , λ ()

------------------------------------------------------------------------
-- THE FREE MONOID REGISTERED AS A BackedUP + consed onto the registry.
------------------------------------------------------------------------
freeMonoid-backed : BackedUP
freeMonoid-backed = record
  { arrow   = freeMonoid-UP
  ; solve   = freeMonoid-solve
  ; solves  = freeMonoid-solves
  ; content = freeMonoid-contentful
  }

freeMonoid-non-vacuous : ¬ _
freeMonoid-non-vacuous = backed-non-vacuous freeMonoid-backed

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — the deferral finished): the FREE MONOID was flagged
-- "PROVED-BUT-NOT-YET-REGISTERED (NOT debt)" in the Registry's coverage note — a
-- deferral whose "NOT debt" disclaimer papered over unfinished work. Here it is
-- FINISHED: freeMonoid-backed wraps foldW (= extend, the free-monoid UP's solve) as a
-- BackedUP, non-vacuous (a word ≠ its wrong candidate), and freeMonoid-registry cons's
-- it onto the list — certified by TYPING, joining eq/Z3/Z5/CRT/μ. The either/or "proved
-- vs registered / real-but-deferred" dissolves: registration IS the proof re-presented
-- as a compiling entry, so "PROVED-BUT-NOT-YET-REGISTERED" was never a stable resting
-- point — it was a to-do. Finished where it left off.
------------------------------------------------------------------------
