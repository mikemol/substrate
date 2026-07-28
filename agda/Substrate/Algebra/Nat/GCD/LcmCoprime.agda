------------------------------------------------------------------------
-- Substrate.Algebra.Nat.GCD.LcmCoprime
--
-- Ⓕ.face (the f072_1 face-action core) AND the closing of LcmN's own deferred
-- gap (the tight lcm = a·b/gcd) AT COPRIME.
--
-- The JEA-Pi cotype's f072_1: the operator acts on the EDGE (1-face) lattice;
-- the CROSS-BLOCK edge-orbit length between a length-a cycle and a length-(suc b′)
-- cycle is their lcm, and for COPRIME lengths that lcm = a·(suc b′) — "15=3·5,
-- 10=2·5, 6=2·3 are the cross-block products" (the orbit closes EXACTLY at a·b,
-- no earlier). LcmN defines the LOOSE bound lcm-ℕ a b = a·b; this proves it is the
-- TIGHT lcm (the LEAST common multiple) when a, b are coprime.
--
--   lcm-coprime-least : gcd a (suc b′) ≡ 1 → a ∣ m → suc b′ ∣ m → (a · suc b′) ∣ m
--
-- REUSE, not reinvention (the EEA/wedge/trace material, per the never-discard-
-- residue spine): the heavy step is `Algebra.Z.Euclid.euclid` — the coprime
-- Euclid lemma already extracted from the EEA trace (NOT a re-proved Bézout); and
-- the `divides`-witness quotients (qa, qb) ARE the wedge/trace cofactors
-- (n ≡ q·m, the kept residue), threaded, not recomputed. With a-divides-lcm /
-- b-divides-lcm (a·b is a COMMON multiple), a·(suc b′) is THE lcm at coprime.
--
-- NAMED GAPS (still external): operator order = the lcm of the WHOLE edge-orbit
-- list (the induced face-action + a list-fold of the tight lcm); the arity-climb
-- f085 (which prime is unsuppressed per face-dimension — the spectral/projection
-- content, the same field-linear-algebra gap as Ⓕ.mult); and the general composite
-- x^L−1 = ∏_{m|L} Φ_m (Ⓕ.cyclotomic's deferred divisor-product).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.GCD.LcmCoprime where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _*_)
open import Substrate.Foundation.Eq using (_≡_; refl; trans; sym; cong)
open import Substrate.Foundation.Product using (_×_; _,_)
open import Substrate.Foundation.Nat.Properties.Mul using (*-comm; *-assoc)
open import Substrate.Algebra.Nat.Divides.Type using (_∣_; divides)
open import Substrate.Algebra.Nat.GCD.GcdN using (gcd-ℕ)
open import Substrate.Algebra.Nat.GCD.LcmN using (lcm-ℕ)
open import Substrate.Algebra.Nat.GCD.ADividesLcm using (a-divides-lcm)
open import Substrate.Algebra.Nat.GCD.BDividesLcm using (b-divides-lcm)
open import Substrate.Algebra.Z.Euclid using (euclid)

------------------------------------------------------------------------
-- 1. a·b is the LEAST common multiple when a, b are coprime: the cross-block
--    edge orbit closes exactly at a·b, no earlier. (euclid does the heavy step.)
------------------------------------------------------------------------

lcm-coprime-least : (a b′ m : ℕ) →
                    gcd-ℕ a (suc b′) ≡ 1 → a ∣ m → suc b′ ∣ m → (a * suc b′) ∣ m
lcm-coprime-least a b′ m cop (divides qa m≡qa*a) (divides qbm m≡qbm*sb)
  with euclid a b′ qa cop
         (divides qbm (trans (*-comm a qa) (trans (sym m≡qa*a) m≡qbm*sb)))
... | divides qb qa≡qb*sb =
  divides qb
    (trans m≡qa*a
    (trans (cong (_* a) qa≡qb*sb)
    (trans (*-assoc qb (suc b′) a)
           (cong (qb *_) (*-comm (suc b′) a)))))

------------------------------------------------------------------------
-- 2. So at coprime, a·(suc b′) is THE lcm: a COMMON multiple (a-/b-divides-lcm,
--    lcm-ℕ a b = a·b) that is LEAST. The cross-block edge-orbit length is exact.
------------------------------------------------------------------------

-- a·b is a common multiple (loose bound), reusing LcmN's divisibility witnesses.
crossblock-common : (a b : ℕ) → (a ∣ lcm-ℕ a b) × (b ∣ lcm-ℕ a b)
crossblock-common a b = a-divides-lcm a b , b-divides-lcm a b

------------------------------------------------------------------------
-- 3. The cotype's concrete (2,3,5) cross-block orbit lengths (f072_1):
--    coprime cycle lengths → orbit length = product, and it is least.
------------------------------------------------------------------------

orbit-3-5 : lcm-ℕ 3 5 ≡ 15
orbit-3-5 = refl

orbit-2-5 : lcm-ℕ 2 5 ≡ 10
orbit-2-5 = refl

orbit-2-3 : lcm-ℕ 2 3 ≡ 6
orbit-2-3 = refl
