------------------------------------------------------------------------
-- Substrate.WitnessTower.CyclicCharacter
--
-- ℤ/n's CHARACTER, DERIVED FROM THE TOWER — not merely agreeing with it.
--
-- `Algebra.PontryaginDual.Sites.ZnCharacter` defines χ_k (j) = (j·k) mod (suc n)
-- and proves `χ-hom` by mod arithmetic.  That proof is self-contained and says
-- nothing about where the character COMES FROM.  This module derives the same
-- law from the tower's build, in the direction the substrate is meant to grow:
-- the tower constructs ℕ, ℕ gives ℤ/n, and the cyclic character is the tower's
-- own iteration read through the action.
--
-- ⚑ THE DERIVATION CHAIN, EVERY LINK ALREADY PROVED ELSEWHERE:
--
--   pow g k                     the tower's k-fold `compose`   [CyclicGrounding]
--     ≡ σ-iterate k (apply g)   under the action               [CyclicCollapse.pow-is-σ-iterate]
--     ≡ (· + k) mod-suc n       at the cyclic generator        [CyclicSuc.σ-iterate-toℕ]
--
-- and the homomorphism law is `pow-hom : pow g (a + b) ≡ compose (pow g a)
-- (pow g b)` — the monoid hom (ℕ, +, 0) → (⟨g⟩, compose, id) — transported
-- along that chain.  Nothing new is PROVED here; the content is the composite,
-- which is exactly the "an attribute IS its build-trace" method
-- (`CyclicGrounding`'s own framing) applied to the character.
--
-- ⚑ WHY THE DERIVATION LIVES HERE AND NOT IN `ZnCharacter`.
-- The obvious move — have `ZnCharacter` import the tower and define χ as a
-- `pow` — INVERTS THE LAYER DIRECTION.  `CyclicSuc`'s header is explicit that
-- neither the tower *nor* F2.Linear is the basis for the cyclic chain: the
-- F₂-free mod-suc arithmetic is, and Ⓖ.tower-basis deliberately relocated the
-- shared stack BELOW both rather than "onto the tower" (the tower is itself
-- F₂-heavy).  `CyclicCollapse` records the same boundary.  So an `Algebra.*`
-- module must not depend on `WitnessTower.*`; the derivation is stated from
-- the tower side, pointing DOWN at the arithmetic definition, which is the
-- only direction that respects both layers.
--
-- ⚑ SO WHAT THIS BUYS, STATED WITHOUT INFLATION.  `ZnCharacter.χ-hom` remains
-- the primitive law by which ℤ/n's character is proved a homomorphism; this
-- module shows that law is not an accident of mod arithmetic but the shadow of
-- the tower's `pow-hom` — the same law, one construction, two readings.  It
-- does NOT make `ZnCharacter` a consumer of the tower, and it does NOT supply
-- the uniqueness theorem (the cyclic analogue of
-- `SignUniqueCharacter.sign-unique-◂-character` is still open).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.CyclicCharacter where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Properties.Add.PlusAssoc
open import Substrate.Foundation.Nat.Properties.Add.PlusComm
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.To
open import Substrate.Foundation.Fin.Iterate using (σ-iterate)
open import Substrate.Foundation.Nat.Nat.ModSuc
open import Substrate.Algebra.Nat.Mod.ModSucBound
open import Substrate.Algebra.Nat.Mod.ModSucId
open import Substrate.Algebra.Nat.Mod.ModSucPeriodic
open import Substrate.Algebra.Nat.Mod.ModSucSuc
open import Substrate.Algebra.Nat.Mod.SucModSucLt
open import Substrate.Algebra.Nat.Mod.SucModSucSelf
open import Substrate.Algebra.Nat.Mod.Homomorphism using (mod-+-left)
open import Substrate.Algebra.Nat.CyclicSuc using (cyclic-suc; σ-iterate-toℕ)
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong

------------------------------------------------------------------------
-- 1. THE CHARACTER AS A BUILD-TRACE.
--
-- χ^tower_k (j) = iterate the cyclic generator k times, starting from j.  This
-- is `pow g k` read through the action (`CyclicCollapse.pow-is-σ-iterate`),
-- specialised to the canonical generator `cyclic-suc` — the F₂-free n-cycle
-- that `CyclicSuc` exposes ("expose-generator-not-orbit").
------------------------------------------------------------------------

χ-tower : (n : ℕ) → ℕ → Fin (suc n) → Fin (suc n)
χ-tower n k j = σ-iterate k (cyclic-suc {n}) j

------------------------------------------------------------------------
-- 2. THE TOWER'S ITERATION IS THE MOD-REDUCED EXPONENT.
--
-- `σ-iterate-toℕ` verbatim: the build-trace's index is (j + k) reduced.  This
-- is the link that lands the tower's construction on ℤ/n's arithmetic.
------------------------------------------------------------------------

χ-tower-toℕ : (n : ℕ) (k : ℕ) (j : Fin (suc n)) →
              toℕ (χ-tower n k j) ≡ (toℕ j ℕ+ k) mod-suc n
χ-tower-toℕ n k j = σ-iterate-toℕ k j

------------------------------------------------------------------------
-- 3. THE HOMOMORPHISM LAW, DERIVED.
--
-- Iterating (a + b) times IS iterating a then b — the additivity that
-- `CyclicGrounding.pow-hom` proves at the `compose` level and
-- `Foundation.Fin.Iterate.σ-iterate-add` proves at the action level.  Read
-- through §2 this is the character law: exponents add.
--
-- Proved here by the index reading rather than by importing σ-iterate-add, so
-- the statement is about the CHARACTER (a Fin-valued equation) rather than
-- about iteration, and the two sides are visibly the same mod-reduction.
------------------------------------------------------------------------

χ-tower-add : (n : ℕ) (a b : ℕ) (j : Fin (suc n)) →
              toℕ (χ-tower n (a ℕ+ b) j) ≡ toℕ (χ-tower n a (χ-tower n b j))
χ-tower-add n a b j =
  trans (χ-tower-toℕ n (a ℕ+ b) j)
  (trans (cong (λ m → (toℕ j ℕ+ m) mod-suc n) (+ℕ-comm a b))
  (trans (cong (_mod-suc n) (sym (+ℕ-assoc (toℕ j) b a)))
  (trans (sym (mod-+-left (toℕ j ℕ+ b) a n))
  (trans (cong (λ m → (m ℕ+ a) mod-suc n) (sym (χ-tower-toℕ n b j)))
         (sym (χ-tower-toℕ n a (χ-tower n b j)))))))
