------------------------------------------------------------------------
-- Substrate.Logic.Evidence.ElAtlas.TowerResidueNumeral
--
-- Ⓕ.tower-crossmul-residue — the residue-carrying CrossMix, CONNECTED (not
-- rebuilt: the reuse-before-build rule). The cyclotomic tower's F₂↔ℚ
-- characteristic clash (SpectralCrossCoherent: doubling is 0 over F₂, invertible
-- over ℚ) is the PRIME-2 phenomenon, and its residue-carrying CrossMix already
-- exists — it is Ξ★.num's `numeral-mix` over R = ℤ/2³ (CenterIsStarNumeral),
-- the deferred CRT numeral example.
--
-- The not-locally-resolvable meaning (the prime 2 — quotiented to 0 in F₂,
-- inverted in ℚ) is held BETWEEN those limits as a NONZERO graded nilpotent in
-- ℤ/2³, carried by the CrossMix as the cross-term obstruction `2·2 = 4` and
-- RESOLVED by embedding up the 2-adic tower (it vanishes: 2³ ≡ 0). This is the
-- paraconsistency made numeral — the contradiction localised as a graded
-- residue, not exploded. Its grade across the tower:
--     mod 2 (F₂):    2 ≡ 0          — the residue VANISHES (char-2 limit)
--     mod 4 (ℤ/4):   2 ≢ 0 (= 2)    — the residue is ALIVE, nonzero
--     in ℤ/2³:       2 nilpotent, degree 3 (2³ ≡ 0) — carried + resolved
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Logic.Evidence.ElAtlas.TowerResidueNumeral where

open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Algebra.Nat.Mod using (_mod-suc_)
open import Substrate.Algebra.Wedge.Mul using (Nilpotent)
open import Substrate.Algebra.Wedge.CrossMul using (cross; Coherent)
open import Substrate.Logic.Evidence.ElAtlas.CenterIsStarNumeral
  using (ℤ8-mul; numeral-mix; obstruction-cross; graded-obstruction; 2-degree-3; clean-cross)

------------------------------------------------------------------------
-- 1. The residue-carrying CrossMix IS numeral-mix; the tower's prime-2 residue
--    is its cross-term, carried as a graded nilpotent and resolved by embedding.
------------------------------------------------------------------------

tower-prime2-residue : Nilpotent ℤ8-mul 2            -- 2³ ≡ 0 : the residue, degree 3
tower-prime2-residue = 2-degree-3

tower-residue-carried : Coherent numeral-mix 2 2     -- the cross-term obstruction is carried
tower-residue-carried = graded-obstruction

tower-residue-value : cross numeral-mix 2 2 ≡ 4      -- the NONZERO residue value (2·2 mod 8)
tower-residue-value = obstruction-cross

tower-residue-resolved : cross numeral-mix 2 4 ≡ 0   -- resolved (null) one rung up
tower-residue-resolved = clean-cross

------------------------------------------------------------------------
-- 2. The grade of the residue across the 2-adic tower — the two field limits
--    of SpectralCrossCoherent (F₂: 2≡0; ℚ: 2 invertible) bracket ℤ/2ⁿ, where
--    the residue is held nonzero-nilpotently.
------------------------------------------------------------------------

residue-vanishes-mod-2 : (2 mod-suc 1) ≡ 0           -- F₂ limit: the residue collapses to 0
residue-vanishes-mod-2 = refl

residue-alive-mod-4 : (2 mod-suc 3) ≡ 2              -- ℤ/4: the residue is nonzero (alive)
residue-alive-mod-4 = refl
