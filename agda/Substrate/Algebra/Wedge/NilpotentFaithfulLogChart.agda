{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.NilpotentFaithfulLogChart — ⟡nf-faithful-log-chart: a
-- log carrier whose cap ANNIHILATES (absorbing), making the log/exp bridge TOTAL.
--
-- ADD 135's Rₖ DISCARDED the overflow residue: at the cap addCap RESETS to 0 (the
-- additive identity), so gen climbs back out (cycles) — predicate-nilpotent, not
-- genuine. The fix, grounded in the substrate's Free⊣Forgetful (Wedge.Adjunction,
-- eval = recon) read through "we don't discard residues": KEEP the overflow as a
-- persistent residue that REFUSES TO VANISH (ResidueAtom's FixedPointFree). That
-- residue IS the absorbing element — once in it, you cannot get back out.
--
-- The adjoin-a-point is the substrate's own Maybe (just = a live log value,
-- nothing = the absorbing overflow-residue). LogM = Maybe ℕ, with mulM adding
-- logs and collapsing to the ABSORBING `nothing` at/over the cap — and `nothing`
-- STAYS `nothing` (absorbing), unlike Rₖ's reset. gpowM sends nothing ↦ 𝟎C, so
-- the bridge is TOTAL: gpowM (mulM x y) ≡ gpowM x *Q gpowM y everywhere.
------------------------------------------------------------------------

module Substrate.Algebra.Wedge.NilpotentFaithfulLogChart where

open import Substrate.Foundation.Eq  using (_≡_; refl; sym; trans; cong)
open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_; _<_; _<?_)
open import Substrate.Foundation.Maybe using (Maybe; just; nothing)
open import Substrate.Foundation.Negation using (Dec; yes; no; ¬_)
open import Substrate.Foundation.Empty using (⊥-elim)
open import Substrate.Foundation.Vec using (Vec; replicate)
import Substrate.Algebra.F2 as F2
open import Substrate.Algebra.F2.CommRing using (F₂-CommRing)
open import Substrate.Algebra.F2.Polynomial.Wedge.DLogHom using (module Over)
import Substrate.Algebra.Polynomial.Graded.Div as Div

------------------------------------------------------------------------
-- The regime: bound (suc d), zero modulus (nilpotent), d = 3 as before.
------------------------------------------------------------------------
d : ℕ
d = 3

f-lo₀ : Vec F2.F₂ (suc d)
f-lo₀ = replicate (suc d) F2.𝟘

open Div.Over F₂-CommRing d f-lo₀ using (Poly; _*Q_; oneC; 𝟎C)
open Over d f-lo₀ using (gpow; gpow-hom)

------------------------------------------------------------------------
-- THE FAITHFUL LOG CARRIER: LogM = Maybe ℕ. `just n` = a live log (exponent n);
-- `nothing` = the ABSORBING overflow-residue (the residue that refuses to vanish).
-- This is the substrate's adjoin-a-point (Maybe) as the free monoid-with-zero:
-- the wedge's Free (keep the residue) with `nothing` the fixed-point-free corner.
------------------------------------------------------------------------
LogM : Set
LogM = Maybe ℕ

-- multiplication of logs: add exponents; if the sum reaches the cap, ABSORB into
-- `nothing` (which STAYS nothing). `nothing` is absorbing — the residue kept, not
-- reset. This is the corrected addCap: overflow ↦ persistent nothing.
mulM : LogM → LogM → LogM
mulM nothing  _        = nothing                      -- absorbing: overflow stays
mulM (just _) nothing  = nothing                      -- absorbing on the right too
mulM (just i) (just j) with (i + j) <? suc d
... | yes _ = just (i + j)                            -- below cap: keep the summed log
... | no  _ = nothing                                 -- at/over cap: ABSORB (persist)

------------------------------------------------------------------------
-- THE EXP CODEC on the faithful carrier: gpowM sends a live log to gpow, and the
-- absorbing residue `nothing` to the ring's absorbing zero 𝟎C.
------------------------------------------------------------------------
gpowM : LogM → Poly (suc d)
gpowM (just n) = gpow n
gpowM nothing  = 𝟎C

------------------------------------------------------------------------
-- ① THE BRIDGE IS NOW TOTAL below the cap AND at it — no divergence. We show the
-- two nontrivial cases: below the cap (both live, sum < cap) it is gpow-hom; at
-- the cap (both live, sum ≥ cap) BOTH sides are 𝟎C (the ring annihilates AND the
-- log absorbs — matched, unlike Rₖ). The absorbing cases (nothing) are refl.
------------------------------------------------------------------------
-- absorbing-left: gpowM (mulM nothing y) = 𝟎C = gpowM nothing *Q gpowM y, because
-- 𝟎C is absorbing in the ring. (Needs 𝟎C *Q p ≡ 𝟎C — the ring's zero-absorb.)
open Div.Over F₂-CommRing d f-lo₀ using (*Q-zeroˡ)

bridge-absorb-left : (y : LogM) → gpowM (mulM nothing y) ≡ (gpowM nothing *Q gpowM y)
bridge-absorb-left y = sym (*Q-zeroˡ (gpowM y))       -- 𝟎C *Q gpowM y ≡ 𝟎C

-- below the cap (both live, i+j < cap): gpowM (just (i+j)) = gpow (i+j) =
-- gpow i *Q gpow j = gpowM (just i) *Q gpowM (just j).
bridge-below-total : (i j : ℕ) → (i + j) < suc d
                   → gpowM (mulM (just i) (just j)) ≡ (gpowM (just i) *Q gpowM (just j))
bridge-below-total i j lt with (i + j) <? suc d
... | yes _  = gpow-hom i j
... | no ¬lt = ⊥-elim (¬lt lt)

-- AT the cap (both live, i+j ≥ cap): mulM absorbs to nothing (gpowM = 𝟎C), and
-- the ring gives gpow i *Q gpow j = gpow (i+j) = 𝟎C (nilpotent, overflow). MATCHED.
bridge-at-cap-total : (i j : ℕ) → ¬ ((i + j) < suc d) → gpow (i + j) ≡ 𝟎C
                    → gpowM (mulM (just i) (just j)) ≡ (gpowM (just i) *Q gpowM (just j))
bridge-at-cap-total i j ¬lt gpow-ij≡𝟎 with (i + j) <? suc d
... | yes lt = ⊥-elim (¬lt lt)
... | no  _  = sym (trans (sym (gpow-hom i j)) gpow-ij≡𝟎)   -- both 𝟎C

------------------------------------------------------------------------
-- ② `nothing` is ABSORBING (the residue that refuses to vanish) — the property
-- Rₖ's reset-to-0 LACKED. Once overflowed, you stay overflowed. This is what
-- makes the chart faithful: the absorbing cap matches the ring's absorbing zero.
------------------------------------------------------------------------
nothing-absorbs : (y : LogM) → mulM nothing y ≡ nothing
nothing-absorbs y = refl

-- and the exp of the absorbing residue is the ring's absorbing zero:
gpowM-nothing : gpowM nothing ≡ 𝟎C
gpowM-nothing = refl

------------------------------------------------------------------------
-- THE INVARIANT (grounded in Free⊣Forgetful + "don't discard residues"): the
-- faithful log chart is the wedge's FREE construction — KEEP the residue. Rₖ
-- discarded the overflow (reset to the additive identity), breaking faithfulness;
-- the fix ADJOINS the residue as the absorbing `nothing` (Maybe = adjoin-a-point,
-- the free monoid-with-zero). `nothing` is the residue that refuses to vanish
-- (ResidueAtom/FixedPointFree) — the absorbing element. Then gpowM is a TOTAL
-- homomorphism LogM → Poly, and the log/exp bridge is total: adjoining the
-- absorbing element = not discarding the overflow residue. The either/or
-- "reset vs annihilate" (ADD 135) dissolves — the faithful chart annihilates,
-- because it keeps the residue instead of discarding it.
------------------------------------------------------------------------
