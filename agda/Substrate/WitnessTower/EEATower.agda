------------------------------------------------------------------------
-- Substrate.WitnessTower.EEATower  (Ⓣ₂ — ℚ is BUILT OF the witnessing step,
-- and ℝ is the SAME step productive: induction↔coinduction on the tower)
--
-- The second tower-reduction. `WitnessTower.Core` is the bare witness path
-- (`start`, `_witnesses_`). The EUCLIDEAN trace `EEATrace a b g` is that path
-- DECORATED with a Wedge at each rung — the Euclidean division a = q·b + r
-- (quotient = the continued-fraction digit, remainder = the residual sub-
-- problem) — terminating at `base` when the gcd is reached.
--
--   Core.witnessing : WSimplex k → WSimplex (suc k)        -- the bare step
--   EEATrace.step   : Wedge a (suc b) → EEATrace (suc b) r g → EEATrace a (suc b) g
--                                                           -- step + its Wedge
--   toPath          : EEATrace a b g → Path (cf-length t)   -- forget the Wedge,
--                                                              keep the Core spine
--
-- So one Euclid step IS Core's witnessing step decorated by its CF digit.
-- Two readings of the SAME finite path, both already proved elsewhere and
-- imported here (Ⓒ / never-discard-residue — not rebuilt):
--   • ℚ-reduction: `eea-unit` (RationalAdjunction) — folding the Wedges back
--     (`reconstruct`) rebuilds exactly the (a,b) the trace started from. So a
--     rational IS built of its n witnessing steps (the ℚ-analog of Ⓣ₁'s
--     `decode-encode`), bottoming out at `base`.
--   • The COINDUCTIVE dual: `qToRℚ = ana qStep` (RationalAdjunction) is the
--     SAME Wedge step run as a terminal-coalgebra unfold. A finite trace HITS
--     `base` ⇒ ℚ; the productive unfold never does ⇒ ℝ.
--
-- The new theorem here, `digit-agreement`, LANDS that duality on the tower:
-- the inductive finite walk's digits (`digits-of-EEA`) are exactly the first
-- `cf-length` digits the coinductive walk emits (`take … (qToRℚ …)`). Same
-- step, observed two ways; they agree on every rung the finite one reaches.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.WitnessTower.EEATower where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_; _*_; _<_)
open import Substrate.Foundation.List using (List; []; _∷_)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong; cong₂)
open import Substrate.Foundation.Product using (_×_; _,_; proj₁; proj₂)
open import Substrate.Foundation.Nat.Properties.Add using (+-comm)

open import Substrate.Algebra.Nat.DivMod.DivSuc using (_div-suc_)
open import Substrate.Algebra.Nat.Mod using (_mod-suc_; mod-suc-bound)
open import Substrate.Algebra.Nat.DivMod.Reconstruction using (div-mod-eq)
open import Substrate.Algebra.Nat.DivMod.Unique using (divmod-unique)
-- only the Wedge PROJECTIONS (the type `Wedge` is the ambiguous bare name —
-- two shape-nodes ⟦b7e6a995⟧/⟦478f66a6⟧ — and is unused here, so not imported).
open import Substrate.Algebra.Nat.GCD.Wedge using (quotient; remainder; wedge-eq; r<b)
open import Substrate.Algebra.Nat.GCD.EEATrace using (EEATrace; base; step)
open import Substrate.Algebra.R.Trace using (RealTrace; take; digits-of-EEA)
open import Substrate.Algebra.R.Trace.RationalAdjunction using (qToRℚ; reconstruct; eea-unit)

open import Substrate.WitnessTower.Core using (Path; start; _witnesses_; top; steps)

------------------------------------------------------------------------
-- 1. The Core spine of an EEA trace: forget the Wedge decoration, keep the
--    chain of witnessing steps. Its length is the continued-fraction length,
--    and the spine has exactly that many witnessing steps (Core.steps).
------------------------------------------------------------------------

cf-length : ∀ {a b g} → EEATrace a b g → ℕ
cf-length (base _)       = zero
cf-length (step _ _ rest) = suc (cf-length rest)

toPath : ∀ {a b g} (t : EEATrace a b g) → Path (cf-length t)
toPath (base _)        = start
toPath (step _ _ rest) = toPath rest witnesses top (toPath rest)

toPath-steps : ∀ {a b g} (t : EEATrace a b g) → steps (toPath t) ≡ cf-length t
toPath-steps (base _)        = refl
toPath-steps (step _ _ rest) = cong suc (toPath-steps rest)

------------------------------------------------------------------------
-- 2. The ℚ-reduction (imported, not rebuilt): the rational IS built of its
--    witnessing steps — folding the Wedges back rebuilds the (a,b) the trace
--    started from. (= RationalAdjunction.eea-unit, restated as the tower's
--    decode-encode; the ℚ-analog of Ⓣ₁.)
------------------------------------------------------------------------

tower-reconstructs : ∀ {a b g} (t : EEATrace a b g) → reconstruct t ≡ (a , b)
tower-reconstructs = eea-unit

------------------------------------------------------------------------
-- 3. (Ⓣ₂ headline) induction↔coinduction on the tower: the inductive finite
--    walk's CF digits ARE the first `cf-length` digits the coinductive walk
--    (`qToRℚ = ana qStep`) emits. The Wedge quotient at each `step` equals the
--    coalgebra's emitted digit `a div-suc b` (divmod-unique on `wedge-eq`), and
--    the residuals line up the same way — so the two observations of the one
--    Wedge step agree on every rung the finite trace reaches.
------------------------------------------------------------------------

digit-agreement :
  ∀ {a b g} (t : EEATrace a b g) →
  digits-of-EEA t ≡ take (cf-length t) (qToRℚ (a , b))
digit-agreement (base a)            = refl
digit-agreement {a} (step b w rest) =
  cong₂ _∷_ (sym (proj₁ du))
            (trans (digit-agreement rest)
                   (cong (λ r → take (cf-length rest) (qToRℚ (suc b , r)))
                         (sym (proj₂ du))))
  where
    du : (a div-suc b ≡ quotient w) × (a mod-suc b ≡ remainder w)
    du = divmod-unique (a div-suc b) (quotient w) (a mod-suc b) (remainder w) b
                       (mod-suc-bound a b) (r<b w)
                       (trans (+-comm ((a div-suc b) * suc b) (a mod-suc b))
                              (trans (sym (div-mod-eq a b)) (wedge-eq w)))
