{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- FUSepQSKI — ⟡FU-sep-Q-ski: a CONCRETE SKI HaltSystem instantiating FUSepQHalts.
--
-- THE CORRECTION (operator): I took the LOSSY reduction s → s' and was surprised
-- it is no longer invertible. The substrate NEVER inverts a lossy map — the WEDGE
-- is the step action precisely because it PRODUCES THE RESIDUE as a WITNESS, and
-- the residue (the remainder / Bézout coefficient) is what makes the step
-- REVERSIBLE. So the ℚ-side step for SKI is NOT reduction — it is the STRUCTURE
-- PEEL (application deconstruction), which keeps the ARGUMENT as the residue
-- witness, so `app` reconstructs the parent DEFINITIONALLY (the recon-eq is refl).
--
-- The wedge here: an application `app f a` peels into its function `f` (next
-- state) keeping its argument `a` as the residue. Reconstruction rcn a f = app f a
-- is EXACT (invertible) because the residue a was retained — exactly as the EEA
-- wedge keeps the remainder so a = q·b + r reconstructs. Reduction discards
-- information; the wedge does not. This is why the wedge — not reduction — is the
-- step action for the finite (ℚ) side.
------------------------------------------------------------------------

module Substrate.FUSep.FUSepQSKI where

open import Substrate.Foundation.Eq          using (_≡_; refl)
open import Substrate.Foundation.Nat         using (ℕ; zero; suc)
open import Substrate.Foundation.WellFounded using (Acc; acc)
open import Substrate.FUSep.FUSepQBridge      using (FinTrace; base; step; reconstruct; fintrace-unit)
import Substrate.FUSep.FUSepQHalts as FUSepQHalts
open FUSepQHalts using (Progress; isVal; stepsD; HaltSystem)

-- minimal SKI term structure: atoms (S/K/I/vars = the base) and application
-- (the wedge node). This is the Böhm-tree / normal-form STRUCTURE, not reduction.
data Tm : Set where      -- ⟦shape:27e68fcc atom,app⟧
  atom : ℕ → Tm
  app  : Tm → Tm → Tm

-- the WEDGE order: `f ◁ app f a` — the function part is the strictly-smaller next
-- state, the argument a is the retained residue. Structural, hence well-founded.
data _◁_ : Tm → Tm → Set where
  ◁-fun : ∀ {f a} → f ◁ (app f a)

-- Acc for the wedge order, by STRUCTURAL INDUCTION on Tm (no numeric measure —
-- the peel is structurally decreasing, exactly like EEA's remainder shrinks).
tm-acc : (t : Tm) → Acc _◁_ t
tm-acc (atom n)  = acc (λ y ())
tm-acc (app f a) = acc (λ { _ ◁-fun → tm-acc f })

-- the LOCAL INVERSE (the reversibility witness at work): rebuild the parent from
-- the residue argument and the function. INVERTIBLE by construction.
rcn : Tm → Tm → Tm
rcn a f = app f a

-- the step: peel to the function (atoms are values, held fixed).
nxt : Tm → Tm
nxt (atom n)  = atom n
nxt (app f a) = f

-- the value-or-step decision: atom → base; app → step carrying the RESIDUE a, the
-- reconstruction equation (refl! — the wedge is exactly invertible), and the
-- structural decrease. Contrast reduction, where the equation would NOT be refl.
prog : (s : Tm) → Progress rcn nxt (λ s' → (nxt s') ◁ s') s
prog (atom n)  = isVal (base (atom n))
prog (app f a) = stepsD a refl ◁-fun

ski-halts : HaltSystem
ski-halts = record
  { St = Tm ; Hd = Tm ; M = Tm ; R = _◁_ ; mu = λ x → x
  ; nxt = nxt ; rcn = rcn ; prog = prog }

------------------------------------------------------------------------
-- THE ℚ-SIDE BRIDGE, END TO END ON CONCRETE SKI TERMS: every term PRODUCES its
-- finite structure-trace (halts→trace, via the Acc driver), and the retraction
-- recovers it EXACTLY (halts-unit). The reversibility is REAL — carried by the
-- residue witness, not conjured from lossy reduction.
------------------------------------------------------------------------
ski-retract : (t : Tm) → Tm
ski-retract t = FUSepQHalts.halts-retract ski-halts t (tm-acc t)

ski-unit : (t : Tm) → ski-retract t ≡ t
ski-unit t = FUSepQHalts.halts-unit ski-halts t (tm-acc t)

-- concrete witness: S K I  =  app (app (atom 0) (atom 1)) (atom 2) round-trips.
_ : ski-unit (app (app (atom zero) (atom (suc zero))) (atom (suc (suc zero)))) ≡ refl
_ = refl
