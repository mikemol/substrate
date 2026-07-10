{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.NuBacked — ⟡nu-as-backedup: register the ν
-- greatest-fixed-point (the allegory-fixed-point arc, ADD 157-168) as a BackedUP —
-- mechanizing its EXISTENCE + non-vacuity into the substrate's UP-conformance frame,
-- with its uniqueness placed HONESTLY (step-level ≡ via smallness; whole-ν bisim).
--
-- The ν's per-step solver IS the wedge (divide : (a b) → Wedge a b, ADD 160/164 —
-- the coalgebra unfold, cofree-dual of recon). So the ν existence is backed by the
-- wedge-UP: Source = (a,b), Target = (q,r), Witness = a ≡ recon q b r; solve returns
-- divide's (quot, rem); solves = divide's wedge-eq; content = wedge-contentful. The
-- Registry then certifies (by TYPING) that the ν unfold is a real, non-vacuous solver.
--
-- UNIQUENESS (honest, the BackedUP split): EXISTENCE (here) is unconditional; the
-- ≡-uniqueness is RELATIVE TO THE SMALLNESS BOUND Adm = r < b (WitnessUnique, the
-- EXISTING wedge-witness-unique ← recon-bounded-unique — the SAME certificate as my
-- 166 cwrem-uniq). The WHOLE-ν (coinductive) uniqueness is BISIMILARITY (ana-unique,
-- ADD 161), NOT ≡ — outside WitnessUnique's ≡ frame; the Unique module names this the
-- "finite WINDOW, not a wall — the coinductive escape." So: existence backed (≡),
-- step-uniqueness bounded (≡ under smallness), whole-ν uniqueness coinductive (~).
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.NuBacked where

open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Nat using (_<_)
open import Substrate.Foundation.Product using (_×_; _,_; proj₁; proj₂)
open import Substrate.Algebra.Wedge using (DivStr; quot; rem; wedge-eq; recon; ℕ-div)
open import Substrate.Algebra.Wedge.Coalgebra using (WedgeCoalg; divide)
open import Substrate.Category.UniversalProperty using (UPArrow; Source; Target; Witness)
open import Substrate.Category.UniversalProperty.Vacuity using (Contentful)
open import Substrate.Category.UniversalProperty.Backed using (BackedUP; arrow; solve; solves; content; backed-non-vacuous)
open import Substrate.Category.UniversalProperty.WedgeUP using (wedge-UP; wedge-contentful)
open import Substrate.Category.UniversalProperty.Unique using (WitnessUnique; wedge-witness-unique)

------------------------------------------------------------------------
-- ① THE ν EXISTENCE-SOLVER, backed by a WedgeCoalg's divide. Given a WedgeCoalg co
-- over ℕ-div, divide co a b : Wedge ℕ-div a b — the canonical unfold step. Its
-- (quot, rem) solves the wedge-UP spec (a,b): a ≡ recon (quot) b (rem) by wedge-eq.
-- This is the ν's per-step solver, the coalgebra unfold returning the witness.
------------------------------------------------------------------------
module _ (co : WedgeCoalg ℕ-div) where

  -- solve: the unfold step returns (quotient, remainder) for each (value, divisor).
  nu-solve : Source wedge-UP → Target wedge-UP
  nu-solve (a , b) = quot (divide co a b) , rem (divide co a b)

  -- solves: the coherence — divide's (q,r) genuinely decomposes a (its wedge-eq).
  nu-solves : (s : Source wedge-UP) → Witness wedge-UP s (nu-solve s)
  nu-solves (a , b) = wedge-eq (divide co a b)

  ------------------------------------------------------------------------
  -- ② THE ν REGISTERED AS A BackedUP. arrow = wedge-UP (the per-step span), solve =
  -- the divide-unfold, solves = its wedge-eq, content = wedge-contentful (non-vacuous:
  -- (0,1)/(0,1) does not decompose). Typing FORCES existence + non-vacuity.
  ------------------------------------------------------------------------
  nu-backed : BackedUP
  nu-backed = record
    { arrow   = wedge-UP
    ; solve   = nu-solve
    ; solves  = nu-solves
    ; content = wedge-contentful
    }

  -- the ν solver is non-vacuous — FORCED by typing (backed-non-vacuous).
  nu-non-vacuous : _
  nu-non-vacuous = backed-non-vacuous nu-backed

------------------------------------------------------------------------
-- ③ THE UNIQUENESS, relative to the smallness bound Adm = r < b (the EXISTING
-- wedge-witness-unique ← recon-bounded-unique — the SAME bound as ADD 166's cwrem-
-- uniq). This is the ≡-uniqueness of the ν's STEP; the bound is ESSENTIAL (drop it
-- and (q,r),(q−1,r+b) both decompose a). REUSED, not re-derived.
------------------------------------------------------------------------
nu-step-unique : WitnessUnique wedge-UP (λ ab qr → proj₂ qr < proj₂ ab)
nu-step-unique = wedge-witness-unique

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — the ν as a BackedUP, honestly split): the ν
-- greatest-fixed-point's EXISTENCE is a registered BackedUP — its per-step solver is
-- the wedge (divide, the coalgebra unfold), returning the witness (quot, rem) that
-- decomposes a (wedge-eq), non-vacuous (wedge-contentful). Typing certifies this. The
-- UNIQUENESS splits EXACTLY along the BackedUP/WitnessUnique line: EXISTENCE
-- unconditional (nu-backed); ≡-uniqueness of the STEP relative to smallness Adm = r<b
-- (nu-step-unique = wedge-witness-unique ← recon-bounded-unique, the SAME bound as 166);
-- and the WHOLE-ν coinductive uniqueness is BISIMILARITY (ana-unique, 161), the "finite
-- window, not a wall." The either/or "ν existence vs ν uniqueness" the 157-168 arc kept
-- hitting DISSOLVES into the BackedUP split: existence backed + non-vacuous, uniqueness
-- bound-relative (smallness) — the smallness r<b the SHARED Adm across the whole wedge
-- universal-property story (WitnessUnique's Adm = 165's wrem-uniq = 166's cwrem-uniq =
-- 167's certified functor). The arc was an un-named BackedUP instance; here it is named.
------------------------------------------------------------------------
