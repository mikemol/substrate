{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- S5Fixpoint — ⟡N1b-Type, CORRECTED (operator): the section is DERIVED, not
-- stored. My S5Carrier stored a `sec : Section` tag; that is a SECOND source
-- of truth about the state (no-double-truth, ADD 16). The value/progressing
-- distinction is a ONE-FUEL-UNIT PROBE: a normal form is a FIXPOINT of `next`
-- (next s ≡ s by interning id), exactly as the Python does
--   (k2 = _reduce_step(k); if k2 == k: break).
-- So: no Progress tag, no Section field. The carrier is JUST the state (a
-- suspended generator, always); `is-value s = next s ≟ s` derives the section
-- on demand. This ALSO removes S5Carrier's 3 section-disjointness absurdities:
-- there are no sibling constructors to exclude — val/prog is a Dec branch.
------------------------------------------------------------------------

module Substrate.S5.S5Fixpoint where

open import Substrate.S5.S5Verdict using (_≡_; refl; sym; trans; cong; ℕ; zero; suc; _+_)
open import Substrate.Foundation.Empty    using (⊥) public
open import Substrate.Foundation.Negation using (Dec; yes; no) public
open import Substrate.Foundation.Bool     using (Bool; true; false) public

module Machine
  (S : Set)
  (next : S → S)                         -- one reduction step (Python _reduce_step)
  (fix? : (s : S) → Dec (next s ≡ s))    -- the one-step fixpoint probe (id compare)
  where

  ----------------------------------------------------------------------
  -- run: step until a FIXPOINT (normal form) or fuel out. Returns JUST the
  -- state — a suspended generator. No tag. Mirrors the Python's k2==k break.
  ----------------------------------------------------------------------
  run : ℕ → S → S
  run zero    s = s
  run (suc n) s with fix? s
  ... | yes _ = s                        -- fixpoint reached: value, stop
  ... | no  _ = run n (next s)           -- progresses: spend the fuel

  -- the SECTION, DERIVED (one fuel unit), never stored:
  is-value : S → Bool
  is-value s with fix? s
  ... | yes _ = true
  ... | no  _ = false

  ----------------------------------------------------------------------
  -- A fixpoint is STABLE under run: once next s ≡ s, any fuel returns s.
  -- (This is why resume = run — a value resumes to itself.)
  ----------------------------------------------------------------------
  fix-stable : (m : ℕ) (s : S) → next s ≡ s → run m s ≡ s
  fix-stable zero    s p = refl
  fix-stable (suc m) s p with fix? s
  ... | yes _ = refl
  ... | no ¬p = ⊥-elim (¬p p)
    where ⊥-elim : {A : Set} → ⊥ → A
          ⊥-elim ()

  ----------------------------------------------------------------------
  -- L2 window composition: run m (run n s) ≡ run (n + m) s. resume = run,
  -- because run on a fixpoint is the identity (fix-stable). Base is ε.
  ----------------------------------------------------------------------
  resume-run : (m n : ℕ) (s : S) → run m (run n s) ≡ run (n + m) s
  resume-run m zero    s = refl
  resume-run m (suc n) s with fix? s
  ... | yes p = fix-stable m s p                      -- s is a value: stays put
  ... | no  _ = resume-run m n (next s)

  ----------------------------------------------------------------------
  -- L1 as a DERIVED-section equation: once run n s is a value (a fixpoint),
  -- more fuel keeps the SAME state. No stored tag, no constructor exclusion —
  -- monotonicity is fix-stable composed with window composition.
  ----------------------------------------------------------------------
  value-monotone : (m n : ℕ) (s : S)
                 → next (run n s) ≡ run n s          -- run n s is a value (probe)
                 → run (n + m) s ≡ run n s
  value-monotone m n s isv =
    trans (sym (resume-run m n s)) (fix-stable m (run n s) isv)
