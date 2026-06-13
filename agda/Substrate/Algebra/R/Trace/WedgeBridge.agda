------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.WedgeBridge
--
-- THE UP HOOKUP I had been neglecting (user, 2026-06-13): "we may already HAVE that
-- unlock latent… we've been running independent of the category-theory machinery…
-- neglected to provide the universal-property hookups." Correct. The whole R-arc
-- coalgebra/adjunction story (`RationalAdjunction`, `Final`) is a ℕ/coinductive
-- REDISCOVERY of the general wedge machinery in `Algebra.Wedge.*`. This module wires
-- it in — typechecked, not narrated.
--
-- THE CORRESPONDENCE (each is a hookup, not a coincidence):
--   reconStep q (b,r)         ≡  (recon ℕ-div q b r , b)   -- `recon-bridge`, refl below.
--      i.e. my "local inverse" IS the general FORGETFUL `eval = recon`
--      (`Algebra.Wedge.Adjunction.eval`); the second component just carries b.
--   qStep                      ↔  `Wedge.Coalgebra.WedgeCoalg.divide` over ℕ-div
--      (the unfold step, dual to recon).
--   qStep-recon / eea-unit     ↔  `Wedge.Adjunction.eval-eq` / `triangle`
--      (the Free⊣Forgetful hom-iso `Wedge ≅ Term` and its witness `a = recon q b r`),
--      iterated over `fromEEATrace`.
--   qStep∘reconStep (r < b)    ↔  the `to (from t) ≡ t` direction `Wedge.Adjunction`
--      left OPEN ("needs the divisor pinned"), and the `rem < b` UNIQUENESS
--      certificate `Algebra.Wedge` only FLAGGED ("the certified, natural wedge").
--      I proved it (via divmod-unique) — so the bounded ℕ wedge has the FULL iso.
--   RealTrace / Final          ↔  the COINDUCTIVE trace of `WedgeCoalg` (the
--      non-halting `run`); rational = halt at z, irrational = never halts.
--   the residue r              ↔  `Category.Lawvere`: "the adjoint defect, the r in
--      a = recon q b r — inverse up to residue." The off-(r<b) failure of the step
--      iso IS that defect.
--
-- So the "primary object" the user asked for already exists: the wedge
-- (Free⊣Forgetful, `Algebra.Wedge.Adjunction`), and ℚ/R/CF are its derived views —
-- ℚ the finite (halting) trace, R the coinductive one, CF the digit readout.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Algebra.R.Trace.WedgeBridge where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Product using (_×_; _,_)
open import Substrate.Foundation.Eq using (_≡_; refl)

open import Substrate.Algebra.Wedge            using (DivStr; C; recon; ℕ-div)
open import Substrate.Algebra.Wedge.Adjunction using (eval)
open import Substrate.Algebra.R.Trace.RationalAdjunction using (reconStep)

------------------------------------------------------------------------
-- THE HOOKUP, typechecked: the R-arc's `reconStep` is the general wedge Forgetful
-- `eval = recon` over ℕ-div, paired with the divisor. `recon ℕ-div q b r = q*b+r`
-- is definitionally `reconStep`'s first component, so this is `refl`.
------------------------------------------------------------------------

reconStep≡recon : (q b r : ℕ) → reconStep q (b , r) ≡ (recon ℕ-div q b r , b)
reconStep≡recon q b r = refl

-- …and `eval` (the named Forgetful functor in Wedge.Adjunction) IS `recon`, so the
-- same `refl` exhibits reconStep as the Forgetful applied at ℕ-div:
reconStep≡eval : (q b r : ℕ) → reconStep q (b , r) ≡ (eval ℕ-div q b r , b)
reconStep≡eval q b r = refl
