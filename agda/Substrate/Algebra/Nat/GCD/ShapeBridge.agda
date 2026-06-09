------------------------------------------------------------------------
-- Substrate.Algebra.Nat.GCD.ShapeBridge
--
-- The convergence bridge between the INTERIOR (EEATrace structural) and
-- EXTERIOR (compute-trace) views of the continued-fraction shape.
--
--   trace-shape-det   : any two traces of the SAME (a,b,g) have the same shape
--                       (= shape-value-invariance at the refl cross-equation —
--                        the determinism corollary, named so the bridge is
--                        navigable rather than implicit).
--   shape-canonical   : the exterior compute-trace shape = ANY interior trace's
--                       shape for the same (a,b). This de-orphans cf-step: the
--                       exterior recurrence and the interior keystone induction
--                       are now provably about the SAME shape object.
--
-- "Convergence without loss of demonstrable fluency": two routes to the shape
-- (structural induction; the Acc-recursion's exterior readout), one agreement.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.GCD.ShapeBridge where

open import Substrate.Foundation.Nat using (ℕ; suc; _<_)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Algebra.Nat.GCD.EEATrace using (EEATrace)
open import Substrate.Algebra.Nat.GCD.GcdN using (gcd-ℕ)
open import Substrate.Algebra.Nat.GCD.GcdTrace using (gcd-trace)
open import Substrate.Algebra.Nat.GCD.GcdPos using (gcd-suc-pos)
open import Substrate.Algebra.Nat.GCD.CFInvariance using (shape-value-invariance)
open import Substrate.Algebra.Wedge.Shape using (ℕ-shape)

-- Same value (here: literally the same a,b) ⟹ same shape — the keystone at refl.
trace-shape-det : {a b g : ℕ} (t₁ t₂ : EEATrace a b g) →
                  0 < g → ℕ-shape t₁ ≡ ℕ-shape t₂
trace-shape-det t₁ t₂ pos = shape-value-invariance t₁ t₂ pos pos refl

-- The exterior compute-trace shape agrees with any interior trace's shape.
shape-canonical : (a b : ℕ) (t : EEATrace a b (gcd-ℕ a b)) →
                  0 < gcd-ℕ a b → ℕ-shape (gcd-trace a b) ≡ ℕ-shape t
shape-canonical a b t pos = trace-shape-det (gcd-trace a b) t pos

-- Positive-denominator specialisation (no positivity obligation on the caller).
shape-canonical-suc : (a b : ℕ) (t : EEATrace a (suc b) (gcd-ℕ a (suc b))) →
                      ℕ-shape (gcd-trace a (suc b)) ≡ ℕ-shape t
shape-canonical-suc a b t = shape-canonical a (suc b) t (gcd-suc-pos a b)
