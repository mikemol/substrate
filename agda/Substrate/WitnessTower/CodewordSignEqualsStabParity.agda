------------------------------------------------------------------------
-- Substrate.WitnessTower.CodewordSignEqualsStabParity
--
-- ⟡codeword-sign-equals-perm-sign — RESOLVED, with a CORRECTED conclusion.
-- The tie sought was "codeword selector bit b₂ ≡ sign of its permutation".
-- Computing the actual grid (4 axes × 6 selectors) shows:
--
--   (1) sign (perm4 (embed (v-of-axis a) · stab-from-selector sel)) is
--       AXIS-INDEPENDENT — the V₄ factor contributes NO sign. This IS the
--       V₄ ⊂ A₄ fact (Klein four = even permutations), holding definitionally.
--
--   (2) the sign equals the STABILISER PARITY of the selector, NOT b₂:
--         selector : fft  tft  ftf  ttf  ftt  ttt
--         stab     : id   sw   cs   cw   csw  cws
--         sign     :  F    T    T    T    F    F     (id & 3-cycles even; the
--                                                     three transpositions odd)
--         b₂       :  F    T    F    T    F    T     (DIFFERS at ftf,ttf,ttt)
--
-- So the honest theorem is sign = stab-parity, and b₂ ≠ sign in general
-- (b₂ is the "ordering selector", a DIFFERENT bit, exactly as the catalog
-- states: "b₂ | reserved: sign; live: ordering selector"). My earlier
-- assumption b₂ = sign was WRONG; the computation corrected it.
--
-- This file proves BOTH facts by the computation that established them:
-- axis-independence (all four axes agree) and the six sign values.
--
-- --safe --without-K. Verified on Agda 2.8.0.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.CodewordSignEqualsStabParity where

open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Vec using (Vec; tabulate; _∷_; [])
open import Substrate.Foundation.Bool using (Bool; true; false)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.WitnessTower.Enumerate using (Perm)
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermSign using (sign)
open import Substrate.Axes using (Axis; D; C; S; W; v-of-axis)
open import Substrate.Axes.Punctured using (a→f; f→a)
open import Substrate.Groups.S4 using (Permutation; _·_; apply)
open import Substrate.Groups.V4-Embedding using (embed)
open import Substrate.Cocycles.V4Signature.Codeword.Live
  using (Selector; sel-fft; sel-tft; sel-ftf; sel-ttf; sel-ftt; sel-ttt)
open import Substrate.Cocycles.V4Signature.Codeword.LiveS4 using (stab-from-selector)

-- Transport an Axis-permutation to Perm 4 (= Vec (Fin 4) 4) so `sign` applies.
perm4 : Permutation → Perm 4
perm4 π = tabulate (λ i → a→f (apply π (f→a i)))

-- The sign of the live codeword's permutation (axis a, selector sel).
codeword-sign : Axis → Selector → Bool
codeword-sign a sel = sign (perm4 (embed (v-of-axis a) · stab-from-selector sel))

------------------------------------------------------------------------
-- (1) V₄ ⊂ A₄: the sign is AXIS-INDEPENDENT (the V₄ factor is even).
--     All four axes give the same sign, for every selector.
------------------------------------------------------------------------

axis-independent-DC : (sel : Selector) → codeword-sign D sel ≡ codeword-sign C sel
axis-independent-DC sel-fft = refl
axis-independent-DC sel-tft = refl
axis-independent-DC sel-ftf = refl
axis-independent-DC sel-ttf = refl
axis-independent-DC sel-ftt = refl
axis-independent-DC sel-ttt = refl

axis-independent-DS : (sel : Selector) → codeword-sign D sel ≡ codeword-sign S sel
axis-independent-DS sel-fft = refl
axis-independent-DS sel-tft = refl
axis-independent-DS sel-ftf = refl
axis-independent-DS sel-ttf = refl
axis-independent-DS sel-ftt = refl
axis-independent-DS sel-ttt = refl

axis-independent-DW : (sel : Selector) → codeword-sign D sel ≡ codeword-sign W sel
axis-independent-DW sel-fft = refl
axis-independent-DW sel-tft = refl
axis-independent-DW sel-ftf = refl
axis-independent-DW sel-ttf = refl
axis-independent-DW sel-ftt = refl
axis-independent-DW sel-ttt = refl

------------------------------------------------------------------------
-- (2) The sign equals the STABILISER PARITY of the selector:
--     id & the two 3-cycles are even (false); the three transpositions
--     (sw, cs, cw) are odd (true). This is the honest content — the
--     codeword's sign is the S₃-stabiliser parity.
------------------------------------------------------------------------

-- stab-parity : the parity of each selector's Stab(D) element.
stab-parity : Selector → Bool
stab-parity sel-fft = false  -- id       (even)
stab-parity sel-tft = true   -- sw       (transposition, odd)
stab-parity sel-ftf = true   -- cs       (transposition, odd)
stab-parity sel-ttf = true   -- cw       (transposition, odd)
stab-parity sel-ftt = false  -- csw      (3-cycle, even)
stab-parity sel-ttt = false  -- cws      (3-cycle, even)

codeword-sign-is-stab-parity :
  (a : Axis) (sel : Selector) → codeword-sign a sel ≡ stab-parity sel
-- axis D:
codeword-sign-is-stab-parity D sel-fft = refl
codeword-sign-is-stab-parity D sel-tft = refl
codeword-sign-is-stab-parity D sel-ftf = refl
codeword-sign-is-stab-parity D sel-ttf = refl
codeword-sign-is-stab-parity D sel-ftt = refl
codeword-sign-is-stab-parity D sel-ttt = refl
-- other axes: reduce to D by axis-independence (V₄ even). Proven case-wise.
codeword-sign-is-stab-parity C sel-fft = refl
codeword-sign-is-stab-parity C sel-tft = refl
codeword-sign-is-stab-parity C sel-ftf = refl
codeword-sign-is-stab-parity C sel-ttf = refl
codeword-sign-is-stab-parity C sel-ftt = refl
codeword-sign-is-stab-parity C sel-ttt = refl
codeword-sign-is-stab-parity S sel-fft = refl
codeword-sign-is-stab-parity S sel-tft = refl
codeword-sign-is-stab-parity S sel-ftf = refl
codeword-sign-is-stab-parity S sel-ttf = refl
codeword-sign-is-stab-parity S sel-ftt = refl
codeword-sign-is-stab-parity S sel-ttt = refl
codeword-sign-is-stab-parity W sel-fft = refl
codeword-sign-is-stab-parity W sel-tft = refl
codeword-sign-is-stab-parity W sel-ftf = refl
codeword-sign-is-stab-parity W sel-ttf = refl
codeword-sign-is-stab-parity W sel-ftt = refl
codeword-sign-is-stab-parity W sel-ttt = refl
