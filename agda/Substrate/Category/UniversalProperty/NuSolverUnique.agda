{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.NuSolverUnique — ⟡nu-solver-unique: the ν STEP
-- solver (nu-backed-ℕ, 184) is THE UNIQUE admissible solution — RELATIVE TO THE SMALLNESS
-- BOUND Adm = r < b (bounded), the DUAL of mu-solver-unique (185, unconditional Adm = ⊤).
--
-- A CORRECTION of ADD 185's framing: I said "nu-solver-unique is bisim, a different proof".
-- GROUNDING (NuBacked's own comment) corrects this: nu-backed is the ν's per-STEP solver
-- (the wedge; Source (a,b), Target (q,r), Witness a ≡ recon q b r), and its per-step
-- ≡-uniqueness DOES fit WitnessUnique — RELATIVE TO Adm = r < b (wedge-witness-unique, via
-- recon-bounded-unique). It is the WHOLE-ν (the coinductive stream) whose uniqueness is
-- BISIM (ana-unique, Final.agda) — a DIFFERENT object, not nu-backed's solver-uniqueness.
-- So ⟡nu-solver-unique IS dischargeable in the WitnessUnique frame, BOUNDED; the bisim is
-- the whole-ν residue (⟡nu-whole-bisim), not this.
--
-- The either/or "μ unconditional vs ν bounded uniqueness" dissolves: BOTH are solver-unique
-- bridges in the SAME WitnessUnique frame — μ's ≡-Witness self-determines (Adm = ⊤); ν's
-- wedge-Witness needs the smallness bound (Adm = r < b) to pin (q,r). The smallness of the
-- ℕ-coalg solver's OWN output is mod-suc-bound (construct-wedge's r<b) — so Adm holds at it.
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.NuSolverUnique where

open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.Foundation.Nat using (ℕ; suc; _<_)
open import Substrate.Foundation.Product using (_,_; proj₂)
open import Substrate.Category.UniversalProperty using (Source; Target; Witness)
open import Substrate.Category.UniversalProperty.Backed using (BackedUP; arrow; solve)
open import Substrate.Category.UniversalProperty.WedgeUP using (wedge-UP)
open import Substrate.Category.UniversalProperty.Unique using (WitnessUnique; wedge-witness-unique; solver-unique)
open import Substrate.Category.UniversalProperty.NuRegistryEntry using (nu-backed-ℕ; ℕ-coalg)

-- the smallness bound Adm (a,b)(q,r) = r < b — the wedge's halting condition.
Adm-small : Source wedge-UP → Target wedge-UP → Set
Adm-small ab qr = proj₂ qr < proj₂ ab

------------------------------------------------------------------------
-- ① THE ν STEP-SOLVER IS UNIQUE, relative to Adm = r < b. solver-unique feeds
-- nu-backed-ℕ's existence (solve/solves) ⊕ wedge-witness-unique (the bounded ≡-uniqueness):
-- any admissible (small) t witnessing s IS the solver's output — PROVIDED the solver's own
-- output is small (Adm s (solve s)), which the caller supplies (mod-suc-bound at suc b).
------------------------------------------------------------------------
nu-solver-unique :
  (s : Source (arrow nu-backed-ℕ))
  (adm-solve : Adm-small s (solve nu-backed-ℕ s))     -- the solver's output is small
  (t : Target (arrow nu-backed-ℕ)) →
  Adm-small s t →                                       -- t is small (admissible)
  Witness (arrow nu-backed-ℕ) s t →
  t ≡ solve nu-backed-ℕ s
nu-solver-unique s adm-solve t adm-t wit-t =
  solver-unique nu-backed-ℕ Adm-small wedge-witness-unique s adm-solve t adm-t wit-t

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — ν's uniqueness is BOUNDED ≡, the wedge side's half; the
-- whole-ν bisim is a DIFFERENT object): nu-backed (the ν STEP solver) registered EXISTENCE
-- (169/184); nu-solver-unique adds UNIQUENESS — and because the wedge-Witness (a ≡ recon q
-- b r) does NOT self-determine (q, r) without a bound, the uniqueness is RELATIVE TO Adm =
-- r < b (wedge-witness-unique, via recon-bounded-unique). This is the DUAL of mu-solver-
-- unique (185): μ's ≡-Witness gives UNCONDITIONAL uniqueness (Adm = ⊤); ν's wedge-Witness
-- gives BOUNDED uniqueness (Adm = r < b). BOTH are solver-unique bridges in the SAME
-- WitnessUnique frame — the "unconditional vs bounded" either/or dissolves into the Adm the
-- Witness requires. The ν STEP solver's uniqueness IS in the ≡ frame (bounded) — CORRECTING
-- ADD 185's claim that "nu-solver-unique is bisim". It is the WHOLE-ν (the coinductive
-- RealTrace stream) whose uniqueness is BISIM (ana-unique, Final.agda) — a DIFFERENT object
-- (⟡nu-whole-bisim), NOT nu-backed's per-step solver-uniqueness. So the μ ⊣ ν uniqueness
-- symmetry is: μ ≡-unconditional (185) ⊣ ν ≡-bounded (185's step, here) at the STEP level,
-- and the whole-ν adds a THIRD coinductive bisim layer (ana-unique) the step does not need.
------------------------------------------------------------------------
