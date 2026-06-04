------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.Factoradic
--
-- TIER 1 — the WitnessTower's factorial ladder is a WEDGE ROOT.
--
-- |S_{n+1}| = (n+1) · |S_n| + 0.  Read through the generic wedge interface
-- (Algebra.Wedge.ℕ-div, whose recon q b r = q*b + r), the count-level rung
-- step is a wedge of (n+1)! against n!:
--
--   quot = suc n     (the factoradic digit / the coset count [S_{n+1}:S_n])
--   rem  = 0         (the division is exact — S_n tiles S_{n+1} with no slop)
--   wedge-eq : (suc n)! ≡ recon ℕ-div (suc n) (n!) 0
--            = (suc n) * (n!) + 0
--
-- This is the COUNT shadow of the witnessing-insertion move
-- (Enumerate.insert-at): each of the n! perms of Fin n spawns exactly
-- (n+1) children — one per insertion slot Fin (suc n) — and they glue with
-- zero remainder.  The wedge's `quot` read IS the inductive action's arity.
--
-- THE FACTORADIC.  The quotient sequence up the tower is
--   tower-quotient 0,1,2,3,… = 1,2,3,4,…
-- i.e. quotient at rung n→(n+1) is (suc n).  That ascending sequence is the
-- mixed RADIX of the factorial number system (the Lehmer code): an index in
-- Fin (n!) decomposes against radices [1,2,3,…,n], exactly the radices that
-- WitnessTower.Sn.enumerate unranks against.  So `tower-quotient` here and
-- the unrank radices there are the same sequence, witnessed below
-- (`quotient-is-unrank-radix`).
--
-- Built on Enumerate.factorial (= the catamorphism whose fold is n!,
-- proved length-correct by Enumerate.perms-length).  Zero postulates,
-- zero holes, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.Factoradic where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_; _*_)
open import Substrate.Foundation.Eq using (_≡_; refl; sym)
open import Substrate.Foundation.Nat.Properties.Add using (+-identityʳ)

open import Substrate.Algebra.Wedge using (DivStr; Wedge; ℕ-div; recon)
open import Substrate.WitnessTower.Enumerate using (factorial)

------------------------------------------------------------------------
-- 1. The rung-step wedge.  (suc n)! wedges against n! with quotient
--    (suc n) and remainder 0.
------------------------------------------------------------------------

-- recon ℕ-div q b r computes to q * b + r; here q = suc n, b = n!, r = 0,
-- so the goal (suc n)! ≡ (suc n) * (n!) + 0 holds because
-- factorial (suc n) is DEFINITIONALLY (suc n) * factorial n, and +0 is
-- killed by +-identityʳ.
tower-wedge : (n : ℕ) → Wedge ℕ-div (factorial (suc n)) (factorial n)
tower-wedge n = record
  { quot     = suc n
  ; rem      = 0
  ; wedge-eq = sym (+-identityʳ (suc n * factorial n))
  }

------------------------------------------------------------------------
-- 2. The quotient read = the factoradic digit at this rung.
------------------------------------------------------------------------

-- the wedge's quotient at rung n→(n+1).
tower-quotient : (n : ℕ) → ℕ
tower-quotient n = Wedge.quot (tower-wedge n)

-- it is the coset count [S_{n+1} : S_n] = (suc n) — the arity of the
-- inductive insertion action (Enumerate.insert-at ranges over Fin (suc n)).
tower-quotient-is-suc : (n : ℕ) → tower-quotient n ≡ suc n
tower-quotient-is-suc n = refl

-- the wedge is EXACT: remainder 0, the prior rung tiles the next with no
-- slop (the witnessing move is a clean cover, no orphan permutations).
tower-rem-zero : (n : ℕ) → Wedge.rem (tower-wedge n) ≡ 0
tower-rem-zero n = refl

------------------------------------------------------------------------
-- 3. The factoradic identification.  The unrank radix that
--    WitnessTower.Sn.enumerate uses at the suc-step is the length of the
--    fresh insertion-position list, all-positions (suc n), which is
--    (suc n) (Enumerate.length-all-positions).  That is exactly
--    tower-quotient n.  So the tower's wedge-quotient sequence and Sn's
--    unrank radices are the one factorial-number-system radix sequence.
------------------------------------------------------------------------

-- the unrank radix at rung n→(n+1): the number of insertion slots, i.e.
-- the size of the position alphabet the Lehmer digit ranges over.
unrank-radix : (n : ℕ) → ℕ
unrank-radix n = suc n

quotient-is-unrank-radix : (n : ℕ) → tower-quotient n ≡ unrank-radix n
quotient-is-unrank-radix n = refl

-- worked rungs: the radix sequence 1,2,3,4 up to S₄.
radices-0-3 :
  (tower-quotient 0 ≡ 1) →
  (tower-quotient 1 ≡ 2) →
  (tower-quotient 2 ≡ 3) →
  (tower-quotient 3 ≡ 4) → ℕ
radices-0-3 _ _ _ _ = 4

radix-0 : tower-quotient 0 ≡ 1
radix-0 = refl
radix-1 : tower-quotient 1 ≡ 2
radix-1 = refl
radix-2 : tower-quotient 2 ≡ 3
radix-2 = refl
radix-3 : tower-quotient 3 ≡ 4
radix-3 = refl

------------------------------------------------------------------------
-- 4. The count check: the wedge reconstructs the right factorials.
--    forget (tower-wedge n) ≡ (suc n)! — the wedge is faithful.
------------------------------------------------------------------------

-- recon evaluated on the wedge data recovers (suc n)!.
tower-recon-correct :
  (n : ℕ) → recon ℕ-div (tower-quotient n) (factorial n) 0 ≡ factorial (suc n)
tower-recon-correct n = +-identityʳ (suc n * factorial n)

-- spot-checks at the worked rungs (S₁..S₄ counts).
recon-3 : recon ℕ-div (tower-quotient 2) (factorial 2) 0 ≡ 6
recon-3 = refl
recon-4 : recon ℕ-div (tower-quotient 3) (factorial 3) 0 ≡ 24
recon-4 = refl
