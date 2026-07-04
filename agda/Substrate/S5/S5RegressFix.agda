{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- S5RegressFix — ⟡N1b-Port. Regress soundness ported onto S5Fixpoint's
-- DERIVED-section kernel (next : S → S, value = fixpoint, no stored tag).
-- In this frame the sibling/tagged verdict is gone, so the proof is far
-- cleaner than S5Regress (no code-family disjointness): a LOOP invariant is
-- a set inside which `next` always PROGRESSES (next s ≢ s = not a value) and
-- stays; `run` stays inside it; therefore run n s is NEVER a value. That IS
-- regress soundness — the one-fuel value-probe never fires along the orbit.
--
-- Retires to residue: S5Verdict (sibling constructors), S5Carrier (stored
-- tag), S5Regress (soundness in the sibling frame), S5Section (the
-- reconciliation — now SUBSUMED: is-value is the derived section, fix-stable
-- is value-is-resume-fixpoint, both already in S5Fixpoint).
------------------------------------------------------------------------

module Substrate.S5.S5RegressFix where

open import Substrate.S5.S5Verdict using (_≡_; refl; sym; trans; cong; ℕ; zero; suc)
import Substrate.S5.S5Fixpoint as S5Fixpoint
open S5Fixpoint using (⊥; Dec; yes; no)
open import Substrate.Foundation.Negation using (¬_)
open import Substrate.Foundation.Product  using (_×_; _,_) renaming (proj₁ to fst; proj₂ to snd)

module Regress
  (S : Set) (next : S → S) (fix? : (s : S) → Dec (next s ≡ s))
  where
  open S5Fixpoint.Machine S next fix?

  ----------------------------------------------------------------------
  -- LOOP invariant (fixpoint frame): inside P, `next` PROGRESSES (never a
  -- fixpoint = never a value) and the successor stays in P. This is the
  -- "recurring generator, no normal form" of ADD 36 stated for next : S → S.
  ----------------------------------------------------------------------
  Loop : (S → Set) → Set
  Loop P = (s : S) → P s → (¬ (next s ≡ s)) × P (next s)

  -- run stays inside a Loop invariant. (The fixpoint branch of run is
  -- Loop-impossible, but even there run returns s and P s holds — no ⊥-elim.)
  run-in-P : (P : S → Set) → Loop P → (n : ℕ) (s : S) → P s → P (run n s)
  run-in-P P lp zero    s ps = ps
  run-in-P P lp (suc n) s ps with fix? s
  ... | yes _ = ps                                   -- run returns s; P s = ps
  ... | no  _ = run-in-P P lp n (next s) (snd (lp s ps))

  loop-not-value : (P : S → Set) → Loop P → (s : S) → P s → ¬ (next s ≡ s)
  loop-not-value P lp s ps = fst (lp s ps)

  ----------------------------------------------------------------------
  -- REGRESS SOUNDNESS: under a Loop invariant, run n s is NEVER a value
  -- (the one-fuel probe next (run n s) ≟ run n s always says "progressing").
  -- Declining to return a value is sound — no value exists at any fuel.
  ----------------------------------------------------------------------
  regress-sound : (P : S → Set) → Loop P → (n : ℕ) (s : S) → P s
                → ¬ (next (run n s) ≡ run n s)
  regress-sound P lp n s ps =
    loop-not-value P lp (run n s) (run-in-P P lp n s ps)
