{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- S5Section — CORRECTION #14 (operator): value ⊂ suspended, not value ⊥
-- suspended. The regress-soundness of S5Regress was proved in S5Verdict's
-- value|suspended SIBLING framing (pre-ADD-21). But every generator's result
-- IS a suspended generator; value/cycle/regress are SECTIONS read off that
-- carrier (ADD 21, the Python cover retype: outer tag ALWAYS suspended).
--
-- This module reconciles: it shows every Verdict yields a CARRIER state
-- (intrinsically a resumable/suspended generator), that VALUE is the
-- resume-FIXPOINT section (not a non-suspended sibling), and restates
-- regress-soundness at the SECTION level — where it belongs. The old
-- constructor-disjointness `no-value` is retained as residue (content-correct,
-- sibling-framed); THIS is the ADD-21-consistent statement.
------------------------------------------------------------------------

module Substrate.S5.S5Section where

import Substrate.S5.S5Verdict as S5Verdict
open S5Verdict
  using (_≡_; refl; sym; trans; cong; final; stepped;
         Verdict; value; suspended; ℕ; zero; suc)
  renaming (Progress to Progress⟦cbe99ef5⟧)
import Substrate.S5.S5Regress as S5Regress
open S5Regress using (Σ; _,_)

-- the two sections we need (value/regress refine these; open = progressing)
data SectionTag : Set where
  val   : SectionTag        -- the resume-FIXPOINT section: a normal form reached
  prog  : SectionTag        -- the resume-PROGRESSING section: more to come

module Sect (S : Set) (next : S → Progress⟦cbe99ef5⟧ S) where
  open S5Verdict.Machine S next
  open S5Regress.Regress S next using (Loop; regress-sound)

  ----------------------------------------------------------------------
  -- EVERY verdict yields a carrier state — "intrinsically a suspended
  -- generator". value and suspended are NOT ontologically disjoint: both
  -- carry a state (both are resumable); they differ only in SECTION.
  ----------------------------------------------------------------------
  carrier : Verdict S → S
  carrier (value v)     = v
  carrier (suspended s) = s

  section : Verdict S → SectionTag
  section (value _)     = val
  section (suspended _) = prog

  ----------------------------------------------------------------------
  -- VALUE IS THE RESUME-FIXPOINT (the distinguished section over the
  -- uniformly-resumable carrier); suspended is resume-progressing. THIS is
  -- why value ⊂ suspended-generators — it is the fixpoint section, not a
  -- sibling. Both are `refl` from S5Verdict.resume's definition.
  ----------------------------------------------------------------------
  value-fixpoint : (m : ℕ) (v : S) → resume m (value v) ≡ value v
  value-fixpoint m v = refl

  suspended-progresses : (m : ℕ) (s : S) → resume m (suspended s) ≡ run m s
  suspended-progresses m s = refl

  ----------------------------------------------------------------------
  -- REGRESS SOUNDNESS, corrected: under a Loop invariant the SECTION is never
  -- `val` — the always-present carrier never reaches its resume-fixpoint. The
  -- carrier-suspension is INTRINSIC (every result has a carrier); the content
  -- is entirely in the section. This is the coherent form of "never value":
  -- not "the result is not a suspended generator" (it always is) but "the
  -- suspended generator never becomes the fixpoint section".
  ----------------------------------------------------------------------
  regress-sound-section :
    (P : S → Set) → Loop P →
    (n : ℕ) (s : S) → P s → section (run n s) ≡ prog
  regress-sound-section P lp n s ps with regress-sound P lp n s ps
  ... | (w , eq) = cong section eq

  -- and the carrier is always extractable (intrinsic suspension), regress or
  -- not — the result is a generator you can read a state off, at every fuel.
  carrier-total : (n : ℕ) (s : S) → S
  carrier-total n s = carrier (run n s)
