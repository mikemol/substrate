{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.MuBacked — ⟡mu-as-backedup: register the μ
-- initial-algebra (Trace, the fold half of the allegory-fixed-point arc) as a
-- BackedUP — the DUAL of ADD 169's ν (NuBacked). Where the ν's solver was the wedge
-- UNFOLD (divide, coinductive, whole-uniqueness = bisim), the μ's solver is the
-- trace FOLD (trace-fold, inductive) — and its whole-uniqueness is ≡ (trace-fold-
-- unique, the initial-algebra property), fitting WitnessUnique's ≡ frame DIRECTLY.
-- That is the honest dual asymmetry: μ (initial/inductive) is the NICER half — ≡
-- throughout, no bisim escape; ν (terminal/coinductive) needed the finite window.
--
-- The substrate itself flags it: trace-fold-unique is "the DUAL of the terminal-
-- coalgebra ana-unique." So μ-as-BackedUP mirrors 169 with the fold for the unfold,
-- and REPLACES the bisim-uniqueness with genuine ≡-uniqueness (trace-fold-unique).
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.MuBacked where

open import Substrate.Foundation.Eq using (_≡_; refl; sym)
open import Substrate.Foundation.Product using (Σ; _×_; _,_; proj₁; proj₂)
open import Substrate.Foundation.Negation using (¬_)
open import Substrate.Algebra.Wedge using (DivStr; z; rem; Trace; done; more; collapse; collapse-fold; collapse-fold≡collapse; trace-fold-unique) renaming (Wedge to Wedge⟦478f66a6⟧)
open import Substrate.Category.UniversalProperty using (UPArrow; Source; Target; Witness)
open import Substrate.Category.UniversalProperty.Vacuity using (Contentful)
open import Substrate.Category.UniversalProperty.Backed using (BackedUP; arrow; solve; solves; content; backed-non-vacuous)

module _ {C : Set} (D : DivStr C) where

  ------------------------------------------------------------------------
  -- ① THE μ FOLD-UP: the initial-algebra span. Source = a trace (a packaged
  -- Σ over its endpoints); Target = the carrier C D; Witness = "the value is the
  -- collapse (gcd-index) read of the trace". solve = collapse-fold (a trace-fold).
  -- The problem "read this whole trace to its index" is solved by the fold.
  ------------------------------------------------------------------------
  -- a trace with its endpoints packaged (so Source is a plain Set).
  SomeTrace : Set
  SomeTrace = Σ C (λ a → Σ C (λ b → Σ C (λ g → Trace D a b g)))

  the-trace : SomeTrace → Σ C (λ a → Σ C (λ b → C))
  the-trace (a , b , g , _) = a , b , g

  fold-UP : UPArrow
  fold-UP = record
    { Source  = SomeTrace
    ; Target  = C
    -- the value is the collapse-fold read of the trace (the gcd index g).
    ; Witness = λ st v → v ≡ collapse-fold (proj₂ (proj₂ (proj₂ st)))
    }

  -- solve: fold the trace to its index (collapse-fold = trace-fold to C D).
  mu-solve : Source fold-UP → Target fold-UP
  mu-solve (a , b , g , t) = collapse-fold t

  -- solves: the fold IS the collapse read — refl (mu-solve st ≡ collapse-fold …).
  mu-solves : (st : Source fold-UP) → Witness fold-UP st (mu-solve st)
  mu-solves (a , b , g , t) = refl

  ------------------------------------------------------------------------
  -- ② NON-VACUITY: a trace whose candidate value is NOT its fold. Take the trace
  -- `done a` over any a ≢ z... but we need a CONCRETE contentful witness. done a :
  -- Trace a z a, collapse-fold (done a) = a. A candidate value v with v ≢ a fails.
  -- We need two distinct carrier elements — use z D and any a with a ≢ z, OR just
  -- exhibit: for done (z D), collapse-fold = z D; a candidate must differ. To stay
  -- carrier-generic we instead register the μ over ℕ-div below where 0 ≢ 1 is decidable.
  ------------------------------------------------------------------------
  -- THE μ ≡-UNIQUENESS (the initial-algebra property, trace-fold-unique): any read h
  -- agreeing with the collapse algebra on done/more IS collapse-fold. This is ≡
  -- (NOT bisim) — the dual's nicer half, fitting the UP frame directly.
  mu-fold-unique :
    (h : {a b g : C} → Trace D a b g → C)
    (h-done : (a : C) → h (done a) ≡ a)
    (h-more : {a g : C} (b : C) (w : Wedge⟦478f66a6⟧ D a b) (tr : Trace D b (rem w) g) →
              h (more b w tr) ≡ h tr) →
    {a b g : C} (t : Trace D a b g) → h t ≡ collapse-fold t
  mu-fold-unique h h-done h-more t =
    trace-fold-unique (λ a → a) (λ _ _ rec → rec) h h-done h-more t

------------------------------------------------------------------------
-- ③ THE ℕ-div REGISTRATION: content needs two distinct carrier elements. Over
-- ℕ-div, done 0 : Trace 0 0 0 has collapse-fold = 0; candidate value 1 ≢ 0 fails
-- the Witness — the non-vacuous certificate. So mu-backed is a real BackedUP.
------------------------------------------------------------------------
open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Algebra.Wedge using (ℕ-div)

-- the fold-UP over ℕ-div.
fold-UP-ℕ : UPArrow
fold-UP-ℕ = fold-UP ℕ-div

-- contentful: source = (done 0), candidate value = 1, and 1 ≢ collapse-fold (done 0) = 0.
mu-contentful : Contentful fold-UP-ℕ
mu-contentful = (0 , 0 , 0 , done 0) , 1 , λ ()

-- THE μ REGISTERED AS A BackedUP (over ℕ-div): solve = the fold, non-vacuous.
mu-backed : BackedUP
mu-backed = record
  { arrow   = fold-UP-ℕ
  ; solve   = mu-solve ℕ-div
  ; solves  = mu-solves ℕ-div
  ; content = mu-contentful
  }

-- the μ solver is non-vacuous — FORCED by typing.
mu-non-vacuous : ¬ _
mu-non-vacuous = backed-non-vacuous mu-backed

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — μ as a BackedUP, the DUAL of ν, the nicer half):
-- the μ initial-algebra (Trace) is a registered BackedUP — its solver is the trace
-- FOLD (collapse-fold = trace-fold to the index), returning the witness (the gcd
-- index g), non-vacuous (done 0 vs candidate 1 over ℕ-div). Typing CERTIFIES it. The
-- DUAL asymmetry with 169 (ν): the ν's whole-uniqueness was BISIM (ana-unique, the
-- coinductive finite-window escape); the μ's whole-uniqueness is ≡ (mu-fold-unique =
-- trace-fold-unique, the initial-algebra property) — fitting WitnessUnique's ≡ frame
-- DIRECTLY, no bound, no escape. So the fold⊣unfold duality (ADD 149) is now NAMED in
-- the UP frame on BOTH sides: μ (fold, initial, ≡-unique, 170) and ν (unfold, terminal,
-- bisim-unique, 169), the SAME wedge read in opposite directions (recon builds/free/μ,
-- divide unfolds/cofree/ν). The either/or "μ vs ν" dissolves into ONE wedge, TWO
-- BackedUP registrations — the substrate's flag "trace-fold-unique is the DUAL of
-- ana-unique" realized as two registered solvers. The arc's both halves are NAMED.
------------------------------------------------------------------------
