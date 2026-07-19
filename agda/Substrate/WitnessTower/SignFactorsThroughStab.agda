------------------------------------------------------------------------
-- Substrate.WitnessTower.SignFactorsThroughStab
--
-- ⟡sign-graded-morphism-package, CORRECTED via STAB (user: "this is why you
-- need Stab — Stab fixes orientation so non-perm and perm meet").
--
-- The naive attempt "sign is a GradedDivStrMorphism out of tower-graded"
-- FAILS: tower-graded's carrier Perm = Vec (Fin n) n includes NON-permutations,
-- and the clean sign digit parity(toℕ p) only holds for genuine permutations
-- (checked: the vector [zero,zero] breaks it). So over the raw carrier the
-- digit is ill-defined and no total morphism with map-C = sign exists.
--
-- STAB is the reconciliation. Every S₄ element factors (Groups.Semidirect
-- Product.Factorisation.factorisation) as σ ≈ embed (v-for σ) · s-for σ, where
-- s-for σ FIXES the anchor axis (orientation-fixing) and v-for σ ∈ V₄. The
-- sign FACTORS THROUGH the Stab part: V₄ ⊂ A₄ is even, so it "leaves sign
-- untouched" (the substrate's own words, ReservedToBivectorCardinality), and
-- sign σ = (parity of the Stab component). The orientation-anchoring is
-- exactly what makes the sign well-defined where the raw digit was not — the
-- perm and non-perm cases MEET at the anchored Stab component, because the
-- V₄ ambiguity that broke totality is the even part that drops out.
--
-- PROVEN here TOTALLY on the codeword's domain (the 24 live = 4 V₄-axes × 6
-- Stab(D) elements): sign is V₄-axis-INDEPENDENT and equals the Stab parity.
-- (This is CodewordSignEqualsStabParity, re-read as: sign factors through
-- Stab, V₄ untouched — the orientation-anchored form.)
--
-- HONEST SCOPE: the FULLY-GENERAL sign σ = sign(s-for σ) for arbitrary
-- σ : Permutation needs sign-hom + sign(embed v)=0 as lemmas over IsPerm
-- (⟡sign-embed-v-even) — a build, since arbitrary s does not compute. What is
-- PROVEN total here is the codeword domain via the 6 concrete stabs.
--
-- --safe --without-K. Verified on Agda 2.8.0.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.SignFactorsThroughStab where

open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Vec using (Vec; tabulate)
open import Substrate.Foundation.Bool using (Bool; true; false)
open import Substrate.Foundation.Eq using (_≡_; refl; trans; sym)
open import Substrate.WitnessTower.Enumerate using (Perm)
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermSign using (sign)
open import Substrate.Axes using (Axis; D; C; S; W; v-of-axis)
open import Substrate.Axes.Punctured using (a→f; f→a)
open import Substrate.Groups.S4 using (Permutation; _·_; apply)
open import Substrate.Groups.V4-Embedding using (embed)
open import Substrate.Cocycles.V4Signature.Codeword.Live
  using (Selector; sel-fft; sel-tft; sel-ftf; sel-ttf; sel-ftt; sel-ttt)
open import Substrate.Cocycles.V4Signature.Codeword.LiveS4 using (stab-from-selector)

-- transport S4.Permutation → Perm 4 so `sign` applies.
perm4 : Permutation → Perm 4
perm4 π = tabulate (λ i → a→f (apply π (f→a i)))

-- The sign of the live codeword at (axis, stab). The axis = the V₄ part; the
-- stab = the orientation-anchored Stab(D) part.
codeword-sign : Axis → Selector → Bool
codeword-sign a sel = sign (perm4 (embed (v-of-axis a) · stab-from-selector sel))

-- The Stab parity — the orientation-anchored digit. Sign depends ONLY on this.
stab-parity : Selector → Bool
stab-parity sel-fft = false
stab-parity sel-tft = true
stab-parity sel-ftf = true
stab-parity sel-ttf = true
stab-parity sel-ftt = false
stab-parity sel-ttt = false

------------------------------------------------------------------------
-- THE STAB FACTORING (total on the codeword domain). Sign = Stab parity,
-- and is INDEPENDENT of the V₄ axis: orientation-fixing makes the sign
-- well-defined regardless of the (potentially non-perm-contributing) V₄ part.
-- This is the honest orientation-anchored morphism the raw carrier denied.
------------------------------------------------------------------------

sign-factors-through-stab :
  (a : Axis) (sel : Selector) → codeword-sign a sel ≡ stab-parity sel
sign-factors-through-stab D sel-fft = refl
sign-factors-through-stab D sel-tft = refl
sign-factors-through-stab D sel-ftf = refl
sign-factors-through-stab D sel-ttf = refl
sign-factors-through-stab D sel-ftt = refl
sign-factors-through-stab D sel-ttt = refl
sign-factors-through-stab C sel-fft = refl
sign-factors-through-stab C sel-tft = refl
sign-factors-through-stab C sel-ftf = refl
sign-factors-through-stab C sel-ttf = refl
sign-factors-through-stab C sel-ftt = refl
sign-factors-through-stab C sel-ttt = refl
sign-factors-through-stab S sel-fft = refl
sign-factors-through-stab S sel-tft = refl
sign-factors-through-stab S sel-ftf = refl
sign-factors-through-stab S sel-ttf = refl
sign-factors-through-stab S sel-ftt = refl
sign-factors-through-stab S sel-ttt = refl
sign-factors-through-stab W sel-fft = refl
sign-factors-through-stab W sel-tft = refl
sign-factors-through-stab W sel-ftf = refl
sign-factors-through-stab W sel-ttf = refl
sign-factors-through-stab W sel-ftt = refl
sign-factors-through-stab W sel-ttt = refl

-- Orientation-independence, stated directly: the sign does NOT depend on the
-- V₄ axis — only on the anchored Stab component. THIS is "perm and non-perm
-- meet": the axis (V₄) freedom is quotiented by the anchoring.
sign-orientation-independent :
  (a b : Axis) (sel : Selector) → codeword-sign a sel ≡ codeword-sign b sel
sign-orientation-independent a b sel =
  trans (sign-factors-through-stab a sel) (sym (sign-factors-through-stab b sel))
