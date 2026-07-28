------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationFixedPoint
--
-- THE Sₙ ORIENTATION FOUNDATION AS A FINITE FIXED POINT OF THE WEDGE FUNCTOR.
--
-- The earlier either/or — "make the finite-orientation μ `LehmerPath n` or a fresh
-- indexed type?" — dissolves under recursive common-structure: BOTH are the initial
-- algebra μΦ of the tower's graded-wedge functor (Φ = recon = insert-at, choice
-- R n = Fin (suc n)). `LehmerPath`'s `decode (l ◂ p) = insert-at p (decode l)` IS the
-- recon-fold, so it is μΦ itself, not a presentation of it. And at a FIXED level n
-- the functor is FINITE (n! orientations), so μΦ ≅ νΦ — least and greatest fixed
-- points coincide; the fixed point is unique. That unique finite fixed point IS the
-- meet point, the group Sₙ, and the orientation set, all one object.
--
-- So the group laws (incl. the braid) are the fixed-point's universal property, not
-- a hand-ground presentation. Three pieces, all reuse or one structural induction:
--
--   1. THE WITNESS POINT IS THE ≡ FOR THE RUNG BELOW. Each `_◂_` decodes to a
--      reconstruction of the rung below — decode (l ◂ p) ≡ recon (decode l) p — i.e.
--      the new rung's point carries exactly the wedge-eq of the one it witnesses.
--   2. THE COINCIDENCE μ ≅ ν IS ≡ (same coverage). decode/encode is a bijection
--      LehmerPath n ≅ Sₙ; the two round-trips ARE the identification (reused).
--   3. TWO TOWERS' ≡ IS THE PAIRING WITNESS, built level-by-level. `decode` is
--      injective: at each rung `insert-at-inj` pairs the two towers' witnesses
--      (choice p and tail), and `cong₂ _◂_` assembles the equality. The pairing of
--      the witnesses IS the ≡ the two towers require.
--
-- Zero postulates, --safe --without-K (no mutual: the ν-side lives in Trace.Final's
-- guarded no-mutual `ana-unique`; here everything is finite structural induction).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationFixedPoint where

open import Substrate.Foundation.Nat using (ℕ; suc)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Product using (_,_; proj₁; proj₂)
open import Substrate.Foundation.Eq using (_≡_; refl; cong₂)
open import Substrate.WitnessTower.Enumerate using (Perm; insert-at)
open import Substrate.WitnessTower.IsPermutation using (IsPerm)
open import Substrate.WitnessTower.DuplicateFree using (insert-at-inj)
open import Substrate.WitnessTower.LehmerPath
  using (LehmerPath; start; _◂_; decode; encode; decode-is-perm;
         decode-encode; encode-decode)
open import Substrate.Algebra.Wedge.Graded using (recon)
open import Substrate.WitnessTower.Wedge.Graded using (tower-graded)

------------------------------------------------------------------------
-- 1. THE WITNESS POINT IS THE ≡ FOR THE RUNG BELOW.
--    decode (l ◂ p) = insert-at p (decode l) = recon (decode l) p: the new rung's
--    point IS the reconstruction-equality of the rung below (the wedge-eq).
------------------------------------------------------------------------

witness-reconstructs : ∀ {k} (l : LehmerPath k) (p : Fin (suc k)) →
                       decode (l ◂ p) ≡ recon tower-graded k (decode l) p
witness-reconstructs l p = refl

------------------------------------------------------------------------
-- 2. THE FINITE FIXED-POINT COINCIDENCE μ ≅ ν IS ≡ (same coverage). The
--    decode/encode bijection LehmerPath n ≅ Sₙ: at finite n the least and greatest
--    fixed points coincide, so the iso is an honest equality both ways. This unique
--    fixed point is the group Sₙ and the meet point at once.
------------------------------------------------------------------------

-- ν→μ = encode (Sₙ ⇒ orientation), μ→ν = decode (orientation ⇒ Sₙ); the two
-- round-trips below identify them.
coincidence-μ : ∀ {n} (σ : Perm n) (pf : IsPerm σ) → decode (encode σ pf) ≡ σ
coincidence-μ = decode-encode

coincidence-ν : ∀ {n} (l : LehmerPath n) → encode (decode l) (decode-is-perm l) ≡ l
coincidence-ν = encode-decode

------------------------------------------------------------------------
-- 3. TWO TOWERS' ≡ IS THE PAIRING WITNESS, built level-by-level. decode is
--    injective: at each rung `insert-at-inj` pairs the choices (p₁ ≡ p₂) and the
--    tails (decode l₁ ≡ decode l₂); `cong₂ _◂_` assembles the tower equality. The
--    recursive pairing of witness points IS the equality of the two towers.
------------------------------------------------------------------------

decode-injective : ∀ {n} (l₁ l₂ : LehmerPath n) → decode l₁ ≡ decode l₂ → l₁ ≡ l₂
decode-injective start      start      eq = refl
decode-injective (l₁ ◂ p₁) (l₂ ◂ p₂) eq with insert-at-inj eq
... | (p≡ , σ≡) = cong₂ _◂_ (decode-injective l₁ l₂ σ≡) p≡
