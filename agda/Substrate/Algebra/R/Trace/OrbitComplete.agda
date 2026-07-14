{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.OrbitComplete — ⟡U3. The COMPLETENESS the AST-
-- projection needs: finite controls that are CLOSED under the coalgebra (a
-- bisimulation / step-closed invariant P) ENTAIL the universal property
-- `~ cover`. This is the "negative controls for your negative controls"
-- (operator): the control SET being coinductively invariant (P-closed), not
-- just finite, is what makes admissibility-on-the-controls sound for ALL
-- reachable states. Previously invoked (solver-unique → ana-unique); now
-- MACHINE-CHECKED — no "demo not proof" stopping point.
--
-- The proof is ana-unique restricted to the reachable set: ana-unique's own
-- recursion only visits s₀, next s₀, … so hypotheses ON A STEP-CLOSED P
-- containing the seed suffice. Closure (P-closed) is exactly what keeps the
-- coinduction inside P — the bisimulation condition R ⊆ step(R).
--
-- Correspondence to the substrate's universal-property factoring (operator's
-- Backed/Lawvere/Unique pointer): P-closed + admissibility = WitnessUnique's
-- BOUND `Adm` (uniqueness holds relative to it); non-vacuity of P = BackedUP's
-- `content`; the two compose as solver-unique. This module is that composition
-- at the orbit coalgebra, landing on ana-unique.
------------------------------------------------------------------------

module Substrate.Algebra.R.Trace.OrbitComplete where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Unit using (⊤)
open import Substrate.Foundation.Product using (_×_; _,_)
open import Substrate.Algebra.R.Trace using (RealTrace; head; tail)
open import Substrate.Algebra.R.Trace.Bisim using (_~_; head~; tail~)
open import Substrate.Algebra.R.Trace.OrbitUniversality using (module OrbitCover)

module ClosedControls
  (S : Set) (next : S → S) (obs : S → ℕ)
  (P : S → Set)                              -- the control set, as a predicate
  (P-closed : (s : S) → P s → P (next s))    -- R ⊆ step(R): CLOSED under step
  where
  open OrbitCover S next obs using (cover)

  ------------------------------------------------------------------------
  -- admissibility RESTRICTED to the control set P: the two commuting squares
  -- checked only ON P (finitely, when P is finite — the actual controls).
  ------------------------------------------------------------------------
  AdmissibleOn : (S → RealTrace) → Set
  AdmissibleOn h = ((s : S) → P s → head (h s) ≡ obs s)
                 × ((s : S) → P s → tail (h s) ≡ h (next s))

  ------------------------------------------------------------------------
  -- COMPLETENESS: admissible-on-the-CLOSED-controls ⟹ ~ cover on P. The finite
  -- (closed) controls entail the universal property. Closure (P-closed) keeps
  -- the coinduction inside P at every step — that is what upgrades a finite
  -- sample to a genuine bisimulation. head (cover s) = obs s and tail (cover s)
  -- = cover (next s) hold definitionally (ana-head/ana-tail refl), so the
  -- squares close the bisimulation directly.
  ------------------------------------------------------------------------
  completeness : (h : S → RealTrace) → AdmissibleOn h
               → (s : S) → P s → h s ~ cover s
  completeness h (hh , ht) = go
    where
      go : (s : S) → P s → h s ~ cover s
      head~ (go s ps) = hh s ps
      tail~ (go s ps) rewrite ht s ps = go (next s) (P-closed s ps)

  ------------------------------------------------------------------------
  -- PROJECTION UNIQUENESS: any two detectors admissible on the closed controls
  -- agree (up to ~) on P. So "the smallest program passing the CLOSED controls"
  -- is THE program up to iso — the minimal AST is canonical, not coincidental.
  ------------------------------------------------------------------------
  projection-unique : (h₁ h₂ : S → RealTrace)
                    → AdmissibleOn h₁ → AdmissibleOn h₂
                    → (s : S) → P s → h₁ s ~ h₂ s
  projection-unique h₁ h₂ a₁ a₂ s ps =
    ~trans (completeness h₁ a₁ s ps) (~sym (completeness h₂ a₂ s ps))
    where
      ~sym : {x y : RealTrace} → x ~ y → y ~ x
      head~ (~sym p) rewrite head~ p = refl
      tail~ (~sym p) = ~sym (tail~ p)
      ~trans : {x y z : RealTrace} → x ~ y → y ~ z → x ~ z
      head~ (~trans p q) rewrite head~ p = head~ q
      tail~ (~trans p q) = ~trans (tail~ p) (tail~ q)

------------------------------------------------------------------------
-- CONCRETE NON-VACUOUS INSTANCE: a finite orbit where P = ⊤ is trivially
-- step-closed (everything is in the control set), so completeness holds for
-- EVERY state. This witnesses the theorem is not vacuous.
------------------------------------------------------------------------
module BoolInstance where
  open import Substrate.Foundation.Bool using (Bool; not; boolToℕ) renaming (true to tt; false to ff)  -- ⟡A4: route through Foundation.Bool (no distinct local Bool)
  flip : Bool → Bool
  flip = not
  bobs : Bool → ℕ
  bobs b = boolToℕ (not b)

  -- P = ⊤: the whole (finite) state space is the closed control set.
  open ClosedControls Bool flip bobs (λ _ → ⊤) (λ _ _ → _)
    using (AdmissibleOn; completeness; projection-unique)

  open OrbitCover Bool flip bobs using (cover)

  -- cover itself is admissible-on-⊤ (the two squares, refl), so completeness
  -- gives cover ~ cover — non-vacuous witness that the hypotheses are satisfiable.
  cover-admissible : AdmissibleOn cover
  cover-admissible = (λ s _ → refl) , (λ s _ → refl)

  cover-complete : (b : Bool) → cover b ~ cover b
  cover-complete b = completeness cover cover-admissible b _
