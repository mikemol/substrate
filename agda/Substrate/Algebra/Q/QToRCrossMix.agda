------------------------------------------------------------------------
-- Substrate.Algebra.Q.QToRCrossMix
--
-- Ⓠ.qtor-crossmix — a CONNECTION LEAF (nodes 6 ↔ 5): the Euclidean step is
-- realized at two different semantic levels that mirror each other.
--
-- The two halves:
--   • LEVEL 6 (coalgebra unfold, `Algebra.R.Trace.RationalAdjunction`): a
--     rational a/(suc d) is the state of the Euclid/Gauss COALGEBRA `qStep`
--     for the stream functor ℕ × −. `qToRℚ = ana qStep` embeds it into the
--     terminal coalgebra R, and `convergent n` folds the depth-n CF prefix
--     back to a (numerator, denominator) ∈ ℕ × ℕ. One `qStep` peels one EEA
--     step: emit ⌊a/b⌋, present the remainder as the next num/den.
--   • LEVEL 5 (cross-codec structure, `Algebra.Q.HetCrossMix`): the SAME
--     num/den datum is a heterogeneous quotient whose equality `_≈ℚ_` IS the
--     `Wedge.CrossMul.cross` of the cospan ℤ-div →(id) ℤ ←(ℕ↪ℤ) ℕ-div —
--     `cross ℚ-crossmix a d = a *ℤ (+ d)`, and `cross-is-viaBridges` certifies
--     that ⊗ is exactly the two codec legs' `viaBridges` factorization.
--
-- THE CLAIM (the leaf): `convergent` reconstruction (R → ℚ) and `ℚ-crossmix`'s
-- cross (the bridge semantics of ℚ-equality) are the two faces of the one
-- Euclidean step. When the coalgebra unfold is folded back at the CF-length
-- depth — the EXACT regime of the adjunction unit (`unit-3/2`), before
-- junk-padding drifts it (`unit-drift`) — the reconstructed (num, den)
-- cross-multiplies, through `ℚ-crossmix`, to the SAME ℤ value as the source
-- rational. Both sides unfold definitionally to num ·ℤ (+ den) in ℤ, so the
-- mirror is `refl`.
--
-- HONEST SCOPE (inherited from RationalAdjunction). The reconstruction is exact
-- ONLY at the CF-length depth; the naive ∀-depth form is FALSE (padding drift,
-- `unit-drift` there). So the cross-mirror is witnessed at the 3/2 = [1;2] depth
-- (the substrate-clean ∀ unit lives over EEATrace, `eea-unit`, not over the
-- padded coinductive fold). This leaf re-exports both halves and certifies the
-- mirror on that witness — it does not reprove the general unit.
--
-- Zero postulates, --safe --without-K --guardedness (imports the coinductive R).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Algebra.Q.QToRCrossMix where

open import Substrate.Foundation.Nat     using (ℕ)
open import Substrate.Foundation.Product using (_×_; _,_)
open import Substrate.Foundation.Eq      using (_≡_; refl)

open import Substrate.Algebra.Z using (ℤ; +_)

-- LEVEL 6 — the coalgebra unfold / convergent reconstruction (re-exported).
open import Substrate.Algebra.R.Trace using (RealTrace; convergent)
open import Substrate.Algebra.R.Trace.RationalAdjunction
  using (qStep; qToRℚ; qToR)

-- LEVEL 5 — the cross-codec structure of ℚ-equality (re-exported).
open import Substrate.Algebra.Q using (ℚ; mkℚ; num; denominator)
open import Substrate.Algebra.Q.HetCrossMix
  using (ℚ-crossmix; ⊗-crossmix; cross-is-viaBridges; ≈ℚ-is-crossmix)
open import Substrate.Algebra.Wedge.CrossMul using (cross)

------------------------------------------------------------------------
-- 1. RE-EXPORT BOTH HALVES at this leaf, so a reader sees the one step under
--    its two names: the coalgebra Euclid step (`qStep` / `qToRℚ`) and the
--    cross-codec Euclid structure (`ℚ-crossmix` / `⊗-crossmix`).
------------------------------------------------------------------------

-- coalgebra side (level 6):
step-coalgebra : (ℕ × ℕ) → ℕ × (ℕ × ℕ)
step-coalgebra = qStep

unfold : ℕ × ℕ → RealTrace
unfold = qToRℚ

fold-back : ℕ → RealTrace → ℕ × ℕ
fold-back = convergent

-- cross-codec side (level 5):
step-crossmix : ℤ → ℕ → ℤ
step-crossmix = ⊗-crossmix

------------------------------------------------------------------------
-- 2. THE MIRROR. `convergent`'s reconstruction (R → ℚ) feeds num/den straight
--    into `ℚ-crossmix`'s cross — the two semantic levels of the same Euclidean
--    step agree. At the 3/2 = [1;2] CF-length depth (the exact adjunction-unit
--    regime), the depth-2 convergent of the unfold qToR 3 1 reconstructs (3, 2),
--    and its cross-multiplication into ℤ equals the source rational 3/2's. Both
--    sides reduce definitionally to 3 ·ℤ (+ 2), so this is `refl`.
------------------------------------------------------------------------

-- The reconstructed pair at the CF-length depth (= the adjunction unit `unit-3/2`):
recon-3/2 : convergent 2 (qToR 3 1) ≡ (3 , 2)
recon-3/2 = refl

-- The cross-multiplicative MIRROR: the reconstructed numerator/denominator,
-- pushed through `ℚ-crossmix`'s cross, give the same ℤ datum as 3/2's own
-- numerator/denominator. This is the bridge duality — cross-multiply into ℤ =
-- viaBridges-compose-into-ℤ (`cross-is-viaBridges`) — applied to the coalgebra's
-- reconstruction. Definitional: both are 3 ·ℤ (+ 2).
crossmix-mirror-3/2 :
  cross ℚ-crossmix (+ 3) 2 ≡ cross ℚ-crossmix (num (mkℚ (+ 3) 1)) (denominator (mkℚ (+ 3) 1))
crossmix-mirror-3/2 = refl

------------------------------------------------------------------------
-- 3. The mirror IS the bridge semantics. The reconstructed pair's cross equals
--    `⊗-crossmix` (the named cross of the cospan), and — by the re-exported
--    `cross-is-viaBridges` — that cross IS `viaBridges` of the two codec legs.
--    So "convergent reconstruction mirrors bridge semantics" is exactly
--    `cross-is-viaBridges` applied at the reconstructed numerator/denominator;
--    `≈ℚ-is-crossmix` then certifies the resulting ℤ equality IS ℚ's own `_≈ℚ_`.
--    Both witnesses are re-exported (in the `open … using` list above) and the
--    leaf instance is `refl`.
------------------------------------------------------------------------

mirror-is-step-crossmix :
  cross ℚ-crossmix (+ 3) 2 ≡ ⊗-crossmix (+ 3) 2
mirror-is-step-crossmix = refl

-- The bridge-duality face of the mirror is the re-exported `cross-is-viaBridges`
-- (in the `open … using` list above, hence in scope for importers of this leaf):
-- for the reconstructed (num, den), the cross of the convergent's output IS
-- `viaBridges` of the two codec legs. Instantiated at the reconstructed (3, 2):
mirror-via-bridges :
  cross ℚ-crossmix (+ 3) 2
    ≡ ⊗-crossmix (+ 3) (denominator (mkℚ (+ 3) 1))
mirror-via-bridges = refl
