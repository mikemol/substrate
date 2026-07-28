------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.V4flipmorph
--
-- Defines: v4-flip-morph
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.V4flipmorph where

open import Substrate.Foundation.Nat
open import Substrate.Foundation.Eq
open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.Wedge.Graded
open import Substrate.Algebra.R.Trace.Bisim
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitMonad ℕ
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitViaTrace using (coemit-trace) renaming (coalg to coemit-coalg)
open import Substrate.Foundation.Product
open import Substrate.Foundation.Eq using () renaming (trans to ≡-trans)
open import Substrate.Category.Allegory.Refinement using (Refinement) renaming (iterate to Riterate)
open import Substrate.Category.Allegory.Refinement using () renaming (chain to Rchain; _⊑ᶠ_ to _R⊑ᶠ_)
open import Substrate.Algebra.R.Trace.Bisim using (~-trans) renaming (head~ to bhead~; tail~ to btail~)
open import Substrate.Foundation.Eq using (sym; cong) renaming (trans to ≡tr)
open import Substrate.Category.UniversalProperty.ExtrudeBisimUpTo
open import Substrate.Algebra.Wedge.Mul
open import Substrate.Algebra.R.Trace.Bisim using (~-refl) renaming (_~_ to _~ᵗ_)
open import Substrate.Foundation.Empty using () renaming (⊥ to Bot)
open import Substrate.Algebra.R.Trace.Bisim using (~-sym) renaming (~-refl to ~-refl')
open import Substrate.Algebra.R.Trace.Final using (ana; ana-unique; into) renaming (out to trace-out)
open import Substrate.Groups.V4.Bijection
import Substrate.Algebra.R.Trace.V4FullCocycle as V4
open import Substrate.Algebra.F2
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Axes.Axis
open import Substrate.Algebra.F2 using () renaming (_+_ to _⊕₂_)
open import Substrate.Algebra.F2 using () renaming (_+_ to _+F_)
open import Substrate.WitnessTower.FaceSet
open import Substrate.Algebra.Setoid
open import Substrate.Foundation.Hedberg
open import Substrate.Category.Lawvere
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Bar


------------------------------------------------------------------------
-- (3) OPERATOR CORRECTION: "We don't use Set₁. We use LAWVERE instead."
-- My hand-rolled `record SetoidStarDivStr : Set₁ { carrier : Set ; ... }` bumped the universe by FIELDING the
-- carrier. The house style is Substrate.Category.Lawvere: **carrier-GENERIC atoms, PARAMETERIZED by V : Set**,
-- so the record itself lives in Set. Lawvere's diagonal (fixed-point) theorem is "the carrier-generic atom behind
-- Cantor, Gödel, Tarski, Turing, and the substrate's wedge residue"; its atoms are FixedPointFree, InvolutiveResidue,
-- TorsorAtom, and — exactly what I was reinventing — **CommutingInvolutions**:
--
--     record CommutingInvolutions (V : Set) : Set where
--       field δ₁ δ₂  : V → V
--             δ₁-inv : (v : V) → δ₁ (δ₁ v) ≡ v
--             δ₂-inv : (v : V) → δ₂ (δ₂ v) ≡ v
--             commute : (v : V) → δ₂ (δ₁ v) ≡ δ₁ (δ₂ v)
--
-- That IS StarV4's V₄ = ⟨†, bar⟩ (two commuting involutions), carrier-generic, in Set — and `commute` is the very
-- V₄-square 353 could only scope at endpoints. PREFLIGHT MISS: I searched reuse-index for "StarDivStr/Setoid" and
-- not for "involution" — the atom was indexed under Lawvere all along ("the carrier-generic atom behind …").
--
-- WHERE IT FITS (verified, D-record-demands-its-equality): CommutingInvolutions demands INTENSIONAL ≡ involutions.
-- On RealTrace, bar (bar r) ~ r (not ≡) ⇒ the atom does NOT take the trace carrier. It takes **V4Full** — the F₂×F₂
-- coords where V₄'s two generators ARE ≡-involutive and DO commute (342: rowSwap-invol, recip-invol, gens-commute).
------------------------------------------------------------------------

-- V4Full is (morph, obj) : F₂ × F₂ with (v4 a b) · (v4 c d) = v4 (a ⊕ c) (b ⊕ d) (348). So right-multiplication
-- by a fixed generator is componentwise ⊕ by a constant — an involution, since F₂ has x ⊕ x = 𝟘 and 𝟘 is the unit.
-- δ₁ = flip the morph bit (rowSwap side) ; δ₂ = flip the obj bit (recip side). They act on DISJOINT components,
-- hence they COMMUTE — the V₄-not-dihedral condition (StarV4's recip-bar), here by componentwise computation.
-- (pattern-match on the `v4` constructor: V4Full's field accessors are opened non-publicly upstream)
v4-flip-morph : V4.V4Full → V4.V4Full
v4-flip-morph (V4.v4 a b) = V4.v4 (𝟙 ⊕₂ a) b
