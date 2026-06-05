------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.Contextuality.Reintern
--
-- THE CARRY PROPER — the genuinely-new half (scratch/dent_system_primer.md
-- §5/§7/§10). The literature flags the obstruction and stops; we never discard
-- a residue, we REINTERN it one grade up. Here that is literal: the
-- unsatisfiable obstruction `(𝟎ⱽ, 𝟙)` at grade n, EXTENDED by a fresh
-- measurement (a witness coordinate), becomes SATISFIABLE at grade n+1 — the
-- contradiction does not dead-end, it becomes a new distinction one grade up.
--
--   * `extend b c` prepends a fresh measurement with coefficient b — the
--     grade-raising move.
--   * `reintern-obstruction-sat` : the reinterned "0 = 1" is satisfied (the new
--     witness coordinate absorbs the parity). The dead-end is dissolved by
--     ascending, not by setting H¹ to zero.
--   * `extend-𝟘-pres` : extending with coefficient 𝟘 is conservative — the
--     lower grade is preserved untouched (the new measurement is free). This is
--     the separation/recall side: reinterning disturbs nothing below.
--   * `lift-tri-global` : the TRIANGLE — contextual at grade 3 (no global
--     section, Models.tri-no-global) — acquires a global section at grade 4 once
--     its obstruction is reinterned as a shared witness coordinate. Open
--     universe made locally consistent by ascending, never by discarding.
--   * `constraint-graded` / `extend-step` : reinterning IS a graded wedge
--     (Algebra.Wedge.Graded) — carrier C n = Constraint n, residue R n = F₂
--     (the witness coefficient = the kept `rem`), recon = extend. The carry
--     lives inside the graded-wedge architecture, exactly like VecGraded and
--     the witness tower.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.Contextuality.Reintern where

open import Substrate.Foundation.Nat using (ℕ; suc)
open import Substrate.Foundation.Vec using (Vec; []; _∷_)
open import Substrate.Foundation.Eq using (_≡_; refl; cong)
open import Substrate.Foundation.Product using (_,_)
open import Substrate.Foundation.Unit using (tt)
open import Substrate.Algebra.F2 using (F₂; 𝟘; 𝟙; _+_)
open import Substrate.Algebra.F2.Vector using (Vector; 𝟎ⱽ)
open import Substrate.Algebra.Wedge.Contextuality
  using (Constraint; con; lhs; rhs; satisfies; ⟨_,_⟩; inner-zero;
         tri-c₁; tri-c₂; tri-c₃)
open import Substrate.Algebra.Wedge.Contextuality.General using (GlobalSection)
open import Substrate.Algebra.Wedge.Graded
  using (GradedDivStr; GradedWedge; recon)

------------------------------------------------------------------------
-- Slice 7. Extend by a fresh measurement; the reinterned obstruction is
--          satisfiable (the new coordinate carries the parity).
------------------------------------------------------------------------

extend : ∀ {n} → F₂ → Constraint n → Constraint (suc n)
extend b c = con (b ∷ lhs c) (rhs c)

reintern-obstruction-sat : ∀ {n} →
  satisfies (𝟙 ∷ 𝟎ⱽ {n}) (extend 𝟙 (con (𝟎ⱽ {n}) 𝟙))
reintern-obstruction-sat {n} = cong (𝟙 +_) (inner-zero (𝟎ⱽ {n}))

------------------------------------------------------------------------
-- Slice 8. Reinterning is conservative on the lower grade: a 𝟘-coefficient
--          extension leaves the new measurement free, preserving satisfaction.
------------------------------------------------------------------------

extend-𝟘-pres : ∀ {n} {s : Vector n} (w : F₂) (c : Constraint n) →
                satisfies s c → satisfies (w ∷ s) (extend 𝟘 c)
extend-𝟘-pres w c e = e

------------------------------------------------------------------------
-- Slice 9. THE PUNCHLINE: the triangle, contextual at grade 3, gains a global
--          section at grade 4 once its obstruction is reinterned as a shared
--          witness coordinate. (c₁,c₂ get coefficient 𝟘; c₃ gets 𝟙.)
------------------------------------------------------------------------

lift-tri₁ lift-tri₂ lift-tri₃ : Constraint 4
lift-tri₁ = extend 𝟘 tri-c₁
lift-tri₂ = extend 𝟘 tri-c₂
lift-tri₃ = extend 𝟙 tri-c₃

lift-tri-scenario : Vec (Constraint 4) 3
lift-tri-scenario = lift-tri₁ ∷ lift-tri₂ ∷ lift-tri₃ ∷ []

-- the assignment (witness=𝟙, x_a=x_b=x_c=𝟘) satisfies all three lifts.
lift-tri-global : GlobalSection lift-tri-scenario
lift-tri-global = (𝟙 ∷ 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ []) , (refl , refl , refl , tt)

------------------------------------------------------------------------
-- Slice 10. Reinterning IS a graded wedge: carrier C n = Constraint n,
--           residue R n = F₂ (the witness coefficient, kept as `rem`),
--           recon = extend. The carry lives in the graded-wedge architecture.
------------------------------------------------------------------------

constraint-graded : GradedDivStr
constraint-graded = record
  { C = Constraint ; R = λ _ → F₂ ; recon = λ n c b → extend b c }

extend-step : ∀ {n} (c : Constraint n) (b : F₂) →
              GradedWedge constraint-graded n (extend b c) c
extend-step c b = record { rem = b ; wedge-eq = refl }
