{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.NilpotentLogExpBridge — ⟡nf-log-exp-bridge: relate the
-- ADDITIVE (log) carrier Rₖ (NilpotentDegreeK, ADD 131) to the MULTIPLICATIVE
-- (exp) carrier via gpow (ExtruderNfCrossDlog, ADD 134). gpow : ℕ → Poly is the
-- exp codec; Rₖ's addCap is the (capped) log-side operation.
--
-- THE BRIDGE IS PARTIAL, and the partiality is the POINT (grounded, not assumed):
--   • BELOW the cap: gpow intertwines addCap and *Q — gpow (addCap d i j) ≡
--     gpow i *Q gpow j. Faithful: Rₖ IS the log chart of the Poly ring here.
--   • AT the cap: they DIVERGE. Rₖ's addCap RESETS to 0 (the additive identity),
--     so gpow (addCap d i j) = gpow 0 = oneC. The Poly ring ANNIHILATES:
--     gpow i *Q gpow j = gpow (i+j) = 𝟎C. And oneC ≢ 𝟎C.
--
-- THE RESIDUE THIS SURFACES: Rₖ's gen satisfies the Nilpotent PREDICATE
-- (Σ n. powⁿ ≡ z) but is NOT a genuine ring-nilpotent — it CYCLES through z and
-- returns (pow gen 3 ≡ 0 BUT pow gen 4 ≡ 1 = gen), because z=0 is addCap's
-- IDENTITY, not absorbing. The Poly gpow IS genuine: 𝟎C is absorbing, so gpow
-- STAYS 0 (gpow 4 ≡ gpow 5 ≡ 𝟎C). The genuine multiplicative nilpotent is the
-- exp side; Rₖ is the log chart, faithful only below the cap.
------------------------------------------------------------------------

module Substrate.Algebra.Wedge.NilpotentLogExpBridge where

open import Substrate.Foundation.Eq  using (_≡_; refl; sym; trans; cong)
open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_; _<_)
open import Substrate.Foundation.Negation using (¬_)
open import Substrate.Foundation.Empty using (⊥)
open import Substrate.Foundation.Vec using (Vec; replicate)
import Substrate.Algebra.F2 as F2
open import Substrate.Algebra.F2.CommRing using (F₂-CommRing)
open import Substrate.Algebra.F2.Polynomial.Wedge.DLogHom using (module Over)
import Substrate.Algebra.Polynomial.Graded.FromCommRing as F
import Substrate.Algebra.Polynomial.Graded.Mod as M
import Substrate.Algebra.Polynomial.Graded.Quotient as Q
import Substrate.Algebra.Polynomial.Graded.Div as Div

open import Substrate.Algebra.Wedge.Mul using (pow)
open import Substrate.Algebra.Wedge.NilpotentDegreeK using (Rk; gen; addCap)
open import Substrate.Algebra.Wedge.NilpotentDegreeKGeneral using (addCap-keep; addCap-collapse)

------------------------------------------------------------------------
-- Match the regimes: Rₖ at k = 3 (cap suc 3 = 4) ↔ Poly at d = 3 (bound suc 3 = 4).
------------------------------------------------------------------------
d : ℕ
d = 3

f-lo₀ : Vec F2.F₂ (suc d)          -- zero modulus ⟹ y^(suc d) ≡ 0 (nilpotent regime)
f-lo₀ = replicate (suc d) F2.𝟘

open F.Over F₂-CommRing using (Poly)
open M.Over F₂-CommRing d f-lo₀ using (oneC)
open Q.Over F₂-CommRing d f-lo₀ using (_*Q_; 𝟎C)
open Over d f-lo₀ using (gpow; gpow-hom)

------------------------------------------------------------------------
-- ① THE BRIDGE, BELOW THE CAP: gpow intertwines Rₖ's addCap with the ring *Q.
-- For i + j below the cap, addCap is genuine addition, and gpow (addCap) =
-- gpow (i+j) = gpow i *Q gpow j. This is the faithful part: Rₖ is exactly the
-- log chart of the Poly ring here — addition of logs = multiplication of exps.
------------------------------------------------------------------------
bridge-below : (i j : ℕ) → (i + j) < suc d
             → gpow (addCap d i j) ≡ (gpow i *Q gpow j)
bridge-below i j lt =
  trans (cong gpow (addCap-keep d i j lt))    -- gpow (addCap d i j) ≡ gpow (i + j)
        (gpow-hom i j)                        -- gpow (i+j) ≡ gpow i *Q gpow j

------------------------------------------------------------------------
-- ② THE DIVERGENCE, AT THE CAP (the residue, made explicit). Rₖ's addCap RESETS
-- to 0, so gpow (addCap d i j) = gpow 0 = oneC. The ring side gives gpow (i+j),
-- which in the nilpotent regime is 𝟎C once i+j reaches the bound. The two do NOT
-- agree: oneC (Rₖ's reset) vs 𝟎C (the ring's annihilation).
------------------------------------------------------------------------
bridge-resets : (i j : ℕ) → ¬ ((i + j) < suc d)
              → gpow (addCap d i j) ≡ oneC
bridge-resets i j ¬lt = cong gpow (addCap-collapse d i j ¬lt)   -- gpow 0 = oneC (refl)

-- oneC ≢ 𝟎C: they differ at coefficient 0 (𝟙 vs 𝟘). So the reset and the
-- annihilation are genuinely different — the bridge is PARTIAL, faithful only
-- below the cap. (The obstruction to totality IS the residue.)
open import Substrate.Foundation.Vec using (lookup)
open import Substrate.Foundation.Fin renaming (zero to fz)
oneC≢𝟎C : oneC ≡ 𝟎C → ⊥
oneC≢𝟎C p = F2.𝟙≢𝟘 (cong (λ v → lookup v fz) p)

------------------------------------------------------------------------
-- ③ THE DEEP RESIDUE (grounded by computation): Rₖ's gen CYCLES through z, the
-- Poly gpow STAYS at 𝟎C. Rₖ's gen satisfies the Nilpotent predicate but is not a
-- genuine (staying) nilpotent — z=0 is addCap's identity, not absorbing.
------------------------------------------------------------------------
-- Rₖ's gen returns after hitting 0: pow gen 3 ≡ 0 but pow gen 4 ≡ 1 (= gen).
rk-gen-hits-zero : pow (Rk 3) gen 3 ≡ 0
rk-gen-hits-zero = refl
rk-gen-returns : pow (Rk 3) gen 4 ≡ 1
rk-gen-returns = refl

-- Poly's y stays: gpow 4 ≡ 𝟎C AND gpow 5 ≡ 𝟎C (𝟎C absorbing — genuine nilpotent).
poly-y-vanishes : gpow (suc d) ≡ 𝟎C
poly-y-vanishes = refl
poly-y-stays : gpow (suc (suc d)) ≡ 𝟎C
poly-y-stays = refl

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out): the log side (Rₖ, addCap) and the exp side
-- (Poly, gpow, *Q) are the two charts of ONE codec, gpow, intertwining addition
-- of logs with multiplication of exps — FAITHFULLY below the cap. They diverge
-- at the cap because they implement the modulus differently: Rₖ RESETS (monoid
-- identity), the Poly ring ANNIHILATES (absorbing zero). That divergence is not a
-- bug to hide but the residue that identifies the GENUINE nilpotent (the exp
-- side, which stays 0) versus the predicate-only one (Rₖ, which cycles). The
-- either/or "additive vs multiplicative Nf" dissolves to: one exp codec, faithful
-- on the shared below-cap domain; the cap is where the charts' modulus-handling
-- (reset vs annihilate) is the residue that names the real structure.
------------------------------------------------------------------------
