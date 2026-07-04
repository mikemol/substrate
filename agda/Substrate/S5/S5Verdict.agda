{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- S5Verdict: fuel-windowed evaluation with ALL residues retained.
--
-- Discipline (operator correction, this session):
--   * NO absurdity pattern anywhere in this module. Every case arm
--     returns an element; the carrier contains its own boundary
--     elements, in the style of EEA (gcd a 0 carries the answer),
--     CF (the empty fraction is a value), CRT (modulus 1 is the unit),
--     and the wedge (r = 0 is the retraction case).
--   * The zero-progress window is ε — a CONSTRUCTOR, not an
--     impossibility. `run zero s = suspended s` is the Godel floor
--     kept as data: the system cannot recognize its own zero-progress
--     element from inside, so it carries it. ε is the UNIT of window
--     composition; discharging it by absurdity would destroy the
--     monoid that schedule-invariance (L2) lives on.
--   * `value` passes through `resume` unchanged: verdict monotonicity
--     (L1) is thereby a COROLLARY of the composition law, proved
--     equationally, with no impossible cases to eliminate.
--
-- Scope (honest): single-fuel runner over an abstract deterministic
-- step. Next rungs, owed: the two-fuel meters (traversal/calculation
-- as a monotone memo table), the cycle verdict (needs decidable state
-- equality), and the ~ fixed point of the self-interpreter (needs the
-- coinductive tier: Bisim's _~_).
------------------------------------------------------------------------

module Substrate.S5.S5Verdict where

-- the cluster's foundation, re-exported from Foundation.* so S5 dependents that
-- pull stdlib from S5Verdict (their mini-foundation) keep resolving unchanged.
open import Substrate.Foundation.Nat  using (ℕ; zero; suc; _+_) public
open import Substrate.Foundation.Eq   using (_≡_; refl; sym; trans; cong) public
open import Substrate.Foundation.List using (List; []; _∷_) public

sum : List ℕ → ℕ
sum []       = zero
sum (n ∷ ns) = n + sum ns

-- the machine, abstractly ----------------------------------------------

-- The step function announces its own progress: `final` CARRIES the
-- state (a residue-retaining alternative to deciding equality, and to
-- Maybe's information-discarding `nothing`).
data Progress (S : Set) : Set where      -- ⟦shape:cbe99ef5 final,stepped⟧
  final   : S → Progress S
  stepped : S → Progress S

-- Verdicts: `suspended` carries its state — the resumable residue.
data Verdict (S : Set) : Set where      -- ⟦shape:9d52a4e9 value,suspended⟧
  value     : S → Verdict S
  suspended : S → Verdict S

module Machine (S : Set) (next : S → Progress S) where

  -- the fuel-windowed runner; ε-window retained, never absurd
  handle : ℕ → Progress S → Verdict S
  run    : ℕ → S → Verdict S

  run zero    s = suspended s          -- ε: zero progress, kept as data
  run (suc n) s = handle n (next s)

  handle n (final v)    = value v
  handle n (stepped s') = run n s'

  -- resumption: values pass through UNCHANGED (the residue-retaining
  -- eliminator — no case is impossible, no case is collapsed)
  resume : ℕ → Verdict S → Verdict S
  resume m (value v)     = value v
  resume m (suspended s) = run m s

  ----------------------------------------------------------------------
  -- ε-laws: the zero window is the unit of composition
  ----------------------------------------------------------------------

  ε-run : ∀ (s : S) → run zero s ≡ suspended s
  ε-run s = refl

  ε-unit : ∀ (m : ℕ) (s : S) → resume m (run zero s) ≡ run m s
  ε-unit m s = refl

  ----------------------------------------------------------------------
  -- L2 (window composition): resuming after n is running n + m.
  -- The base case of the induction IS the ε-unit law: the "impossible"
  -- case other designs discharge by absurdity is here the foundation
  -- the proof stands on.
  ----------------------------------------------------------------------

  resume-handle : ∀ (m n : ℕ) (p : Progress S)
                → resume m (handle n p) ≡ handle (n + m) p
  resume-run    : ∀ (m n : ℕ) (s : S)
                → resume m (run n s) ≡ run (n + m) s

  resume-run m zero    s = refl                        -- ε at the base
  resume-run m (suc n) s = resume-handle m n (next s)

  resume-handle m n (final v)    = refl
  resume-handle m n (stepped s') = resume-run m n s'

  ----------------------------------------------------------------------
  -- L2 generalized: ANY schedule of windows equals its one-shot sum.
  ----------------------------------------------------------------------

  runSchedule : List ℕ → S → Verdict S
  runSchedule []       s = suspended s                 -- the empty schedule is ε
  runSchedule (w ∷ ws) s = resumeSchedule ws (run w s)
    where
      resumeSchedule : List ℕ → Verdict S → Verdict S
      resumeSchedule []       v = v
      resumeSchedule (u ∷ us) v = resumeSchedule us (resume u v)

  -- stated over the fold directly:
  resumeAll : List ℕ → Verdict S → Verdict S
  resumeAll []       v = v
  resumeAll (u ∷ us) v = resumeAll us (resume u v)

  resumeAll-run : ∀ (ws : List ℕ) (n : ℕ) (s : S)
                → resumeAll ws (run n s) ≡ run (n + sum ws) s
  resumeAll-run [] n s = cong (λ k → run k s) (sym (+zero n))
    where
      +zero : ∀ (k : ℕ) → k + zero ≡ k
      +zero zero    = refl
      +zero (suc k) = cong suc (+zero k)
  resumeAll-run (u ∷ us) n s =
    trans (cong (resumeAll us) (resume-run u n s))
          (trans (resumeAll-run us (n + u) s)
                 (cong (λ k → run k s) (+assoc n u (sum us))))
    where
      +assoc : ∀ (a b c : ℕ) → (a + b) + c ≡ a + (b + c)
      +assoc zero    b c = refl
      +assoc (suc a) b c = cong suc (+assoc a b c)

  ----------------------------------------------------------------------
  -- L1 (verdict monotonicity): a COROLLARY, proved equationally.
  -- No case analysis, no impossible arms: the ε-retaining resume
  -- equations make monotonicity a rewrite.
  ----------------------------------------------------------------------

  value-monotone : ∀ (m n : ℕ) (s : S) (v : S)
                 → run n s ≡ value v
                 → run (n + m) s ≡ value v
  value-monotone m n s v eq =
    trans (sym (resume-run m n s)) (cong (resume m) eq)
