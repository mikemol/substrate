{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.X8aBacked — ⟡x8a-backed: register the EXTRUDER
-- (the reduction-to-fixpoint solver, the python x7 _reduce_step formalized as
-- S5Fixpoint.Machine.run) as a BackedUP — the THIRD solver joining μ (MuBacked, the
-- initial-algebra fold) and ν (NuBacked, the terminal-coalgebra unfold). Where μ's solver
-- is the trace-FOLD and ν's is the wedge-UNFOLD, the extruder's solver is the FIXPOINT
-- RUN: step via `next` until a normal form (fixpoint of next), exactly as the Python does.
--
-- The bridge is COMMON (mirrors MuBacked/NuBacked exactly): Source = a fuelled start
-- (fuel , state); Target = the state; Witness s v = "v ≡ the run's result" (the value IS
-- the fixpoint/normal-form the reduction reaches); solve = run; solves = refl (run computes
-- it); content = a concrete (s , t) whose t is NOT the run result (non-vacuous — the
-- Witness discriminates). Instantiated at the concrete decidable machine over ℕ so content
-- is a real inequality. The Registry then certifies (by TYPING) that the extruder is a
-- real, non-vacuous solver — the third registered alongside μ/ν.
--
-- Grounded-then-instantiated (ADD 208/210/211 mapped the whole foundation upstream): the
-- fixpoint kernel is S5Fixpoint.run; the confluence/uniqueness backdrop is FUSep's SKI
-- Church-Rosser; the ~-frame is FUSep.ObsBisim. Here we register EXISTENCE (the solver runs
-- and its value is the fixpoint) — unconditional, exactly as MuBacked/NuBacked register the
-- fold/unfold existence, the ≡-uniqueness being the confluence story (FUSep) upstream.
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.X8aBacked where

open import Substrate.Foundation.Product using (Σ; _,_; proj₁; proj₂)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Negation using (¬_; Dec; yes; no)
open import Substrate.Foundation.Nat using (ℕ; zero; suc; _≟_)
open import Substrate.Category.UniversalProperty using (UPArrow; Source; Target; Witness)
open import Substrate.Category.UniversalProperty.Vacuity using (Contentful)
open import Substrate.Category.UniversalProperty.Backed
  using (BackedUP; arrow; solve; solves; content; backed-non-vacuous)
open import Substrate.S5.S5Fixpoint using (module Machine)

------------------------------------------------------------------------
-- ① THE CONCRETE EXTRUDER MACHINE: the reduction step over ℕ. `next` is one
--    _reduce_step; the normal form is a FIXPOINT of next. Here the demonstrator step is
--    "predecessor" (suc n ↦ n, zero ↦ zero) — a terminating reduction whose fixpoint (0)
--    is the normal form, decidable (ℕ has _≟_), so `content` is a real inequality.
------------------------------------------------------------------------
next : ℕ → ℕ
next zero    = zero
next (suc n) = n

fix? : (s : ℕ) → Dec (next s ≡ s)
fix? zero    = yes refl
fix? (suc n) = no λ ()          -- next (suc n) = n ≢ suc n

open Machine ℕ next fix? using (run)

------------------------------------------------------------------------
-- ② THE EXTRUDER UP: Source = (fuel , start); Target = ℕ; Witness = "v ≡ run fuel start".
--    The problem "reduce this start to its normal form" is solved by the fixpoint run.
------------------------------------------------------------------------
Fuelled : Set
Fuelled = Σ ℕ (λ _ → ℕ)          -- (fuel , start)

x8a-UP : UPArrow
x8a-UP = record
  { Source  = Fuelled
  ; Target  = ℕ
  ; Witness = λ fs v → v ≡ run (proj₁ fs) (proj₂ fs)
  }

-- solve: run the reduction to its fixpoint/normal-form (the extruder proper).
x8a-solve : Source x8a-UP → Target x8a-UP
x8a-solve (fuel , start) = run fuel start

-- solves: the run IS the value — refl (solve computes exactly run fuel start).
x8a-solves : (s : Source x8a-UP) → Witness x8a-UP s (x8a-solve s)
x8a-solves (fuel , start) = refl

------------------------------------------------------------------------
-- ③ NON-VACUITY: a concrete (s , t) whose t is NOT the run result — the Witness
--    discriminates. Take fuel=1, start=1: run 1 1 = next 1 = 0 (one step to the fixpoint);
--    candidate value 1 ≢ 0. So the extruder UP is Contentful, hence non-vacuous.
------------------------------------------------------------------------
x8a-contentful : Contentful x8a-UP
x8a-contentful = (suc zero , suc zero) , suc zero , λ eq → bad eq
  where
    -- Witness ((1,1)) 1  =  (1 ≡ run 1 1) = (1 ≡ 0); refute it.
    bad : ¬ (suc zero ≡ run (suc zero) (suc zero))
    bad ()

------------------------------------------------------------------------
-- ④ THE BACKEDUP: the extruder registered — the third solver joining μ/ν.
------------------------------------------------------------------------
x8a-backed : BackedUP
x8a-backed = record
  { arrow   = x8a-UP
  ; solve   = x8a-solve
  ; solves  = x8a-solves
  ; content = x8a-contentful
  }

-- and it is non-vacuous (its content cannot collapse to ⊤) — the Registry's invariant.
x8a-non-vacuous : ¬ ((s : Source x8a-UP) (t : Target x8a-UP) → Witness x8a-UP s t)
x8a-non-vacuous = backed-non-vacuous x8a-backed

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — the extruder IS a BackedUP, the third solver): the
-- reduction-to-fixpoint run (S5Fixpoint.Machine.run, the python x7 _reduce_step) is now
-- registered as a BackedUP with the SAME common bridge as μ (fold) and ν (unfold) —
-- Source/Target/Witness/solve/solves/content — differing only in that its solver is the
-- FIXPOINT RUN. So the μ⊣ν pair gains its third member: fold (initial algebra), unfold
-- (terminal coalgebra), and RUN (the fixpoint machine), all three backed by the common
-- solve-bridge, all three non-vacuous by typing. The either/or "the extruder is a big
-- build vs it's already done" bottoms out here: grounded across ADD 208/210/211 (combinator
-- infra + FUSep SKI-CR + ObsBisim ~-frame + S5 fixpoint-machine ALL upstream), the extruder
-- is this ONE BackedUP assembling that foundation — existence registered (unconditional,
-- as μ/ν register fold/unfold existence), the ≡-uniqueness being FUSep's confluence upstream.
------------------------------------------------------------------------
