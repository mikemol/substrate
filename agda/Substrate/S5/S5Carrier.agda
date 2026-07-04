{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- S5Carrier — ⟡N1b-Type. The kernel's verdict RETYPED so the value|suspended
-- SIBLING constructors vanish (correction #14 / ADD 39). Every run yields a
-- SUSPENDED CARRIER (a resumable generator, state always present); value /
-- cycle / regress / prog are SECTIONS read off it — mirroring the Python
-- run_cover (outer tag always suspended). "Never value" is now a SECTION
-- equation (sec ≢ val), not a constructor exclusion, so the incoherence the
-- operator flagged is gone by construction.
--
-- Mirrors S5Verdict's proofs faithfully (ε-run, resume-run, resumeAll-run,
-- monotone) in the carrier+section type; the base case is still ε, resume
-- now matches on the SECTION (val = resume-fixpoint, prog = resume-progress).
------------------------------------------------------------------------

module Substrate.S5.S5Carrier where

open import Substrate.S5.S5Verdict
  using (_≡_; refl; sym; trans; cong; ℕ; zero; suc; final; stepped; _+_; List; []; _∷_; sum)
  renaming (Progress to Progress⟦cbe99ef5⟧)

------------------------------------------------------------------------
-- The SECTION: the classification read off the suspended carrier. `val` is
-- the resume-FIXPOINT (normal form / empty successor); `prog` is resume-
-- PROGRESSING (fuel-bounded cut); `cyc`/`reg` are the overlap sections a
-- detector-equipped machine mints (carried here so the type matches the
-- full cover — the base Machine below produces only val/prog).
------------------------------------------------------------------------
data SectionC (S : Set) : Set where      -- ⟦shape:0ceff485 val,cyc,reg⟧
  val  : SectionC S
  cyc  : S → SectionC S
  reg  : S → SectionC S
  prog : SectionC S

-- The CARRIER: a suspended generator = a state plus its section. ALWAYS this;
-- there is no non-suspended verdict.
record Susp (S : Set) : Set where
  constructor susp
  field
    state : S
    sec   : SectionC S
open Susp public

module Machine (S : Set) (next : S → Progress⟦cbe99ef5⟧ S) where

  handle : ℕ → Progress⟦cbe99ef5⟧ S → Susp S
  run    : ℕ → S → Susp S

  run zero    s = susp s prog                    -- ε: progressing, not done
  run (suc n) s = handle n (next s)

  handle n (final v)    = susp v val             -- the value SECTION
  handle n (stepped s') = run n s'

  -- resume matches on the SECTION: val is the fixpoint (done stays done),
  -- prog resumes by running. cyc/reg are terminal sections too.
  resume : ℕ → Susp S → Susp S
  resume m (susp st val)     = susp st val
  resume m (susp st (cyc w)) = susp st (cyc w)
  resume m (susp st (reg w)) = susp st (reg w)
  resume m (susp st prog)    = run m st

  ----------------------------------------------------------------------
  -- ε-laws: the zero window is the unit (base is prog, the ε section).
  ----------------------------------------------------------------------
  ε-run  : (s : S) → run zero s ≡ susp s prog
  ε-run  s = refl

  ε-unit : (m : ℕ) (s : S) → resume m (run zero s) ≡ run m s
  ε-unit m s = refl

  ----------------------------------------------------------------------
  -- L2 window composition, mirrored exactly (base = ε).
  ----------------------------------------------------------------------
  resume-handle : (m n : ℕ) (p : Progress⟦cbe99ef5⟧ S)
                → resume m (handle n p) ≡ handle (n + m) p
  resume-run    : (m n : ℕ) (s : S)
                → resume m (run n s) ≡ run (n + m) s

  resume-run m zero    s = refl
  resume-run m (suc n) s = resume-handle m n (next s)

  resume-handle m n (final v)    = refl
  resume-handle m n (stepped s') = resume-run m n s'

  ----------------------------------------------------------------------
  -- L2 generalized: any schedule = its one-shot sum.
  ----------------------------------------------------------------------
  resumeAll : List ℕ → Susp S → Susp S
  resumeAll []       v = v
  resumeAll (u ∷ us) v = resumeAll us (resume u v)

  resumeAll-run : (ws : List ℕ) (n : ℕ) (s : S)
                → resumeAll ws (run n s) ≡ run (n + sum ws) s
  resumeAll-run [] n s = cong (λ k → run k s) (sym (+zero n))
    where
      +zero : (k : ℕ) → k + zero ≡ k
      +zero zero    = refl
      +zero (suc k) = cong suc (+zero k)
  resumeAll-run (u ∷ us) n s =
    trans (cong (resumeAll us) (resume-run u n s))
          (trans (resumeAll-run us (n + u) s)
                 (cong (λ k → run k s) (+assoc n u (sum us))))
    where
      +assoc : (a b c : ℕ) → (a + b) + c ≡ a + (b + c)
      +assoc zero    b c = refl
      +assoc (suc a) b c = cong suc (+assoc a b c)

  ----------------------------------------------------------------------
  -- L1, now a SECTION equation (correction #14): once the section is `val`
  -- it stays `val` under more fuel. NO constructor disjointness — value is a
  -- section, so monotonicity is a rewrite on the section, exactly as before.
  ----------------------------------------------------------------------
  val-monotone : (m n : ℕ) (s : S)
               → sec (run n s) ≡ val
               → sec (run (n + m) s) ≡ val
  val-monotone m n s eq =
    trans (cong sec (sym (resume-run m n s))) (resume-val m (run n s) eq)
    where
      -- resume preserves the val section. The non-val cases are ruled out by
      -- the hypothesis sec v ≡ val (prog/cyc/reg ≡ val is impossible) — a
      -- SECTION-level disjointness (honest: val genuinely differs from the
      -- progressing/overlap sections), transported through a code family.
      data ⊥ : Set where
      Code : SectionC S → Set
      Code val      = S → S     -- val ↦ inhabited (⊤-like)
      Code (cyc _)  = ⊥
      Code (reg _)  = ⊥
      Code prog     = ⊥
      notVal : {x : SectionC S} → x ≡ val → Code x → ⊥ → ⊥
      notVal _ _ b = b
      -- from sec v ≡ val we get Code (sec v); at non-val that is ⊥.
      transport : {x y : SectionC S} → x ≡ y → Code x → Code y
      transport refl c = c
      resume-val : (m : ℕ) (v : Susp S) → sec v ≡ val → sec (resume m v) ≡ val
      resume-val m (susp st val)     e = refl
      resume-val m (susp st (cyc w)) e with transport (sym e) (λ x → x)
      ... | ()
      resume-val m (susp st (reg w)) e with transport (sym e) (λ x → x)
      ... | ()
      resume-val m (susp st prog)    e with transport (sym e) (λ x → x)
      ... | ()
