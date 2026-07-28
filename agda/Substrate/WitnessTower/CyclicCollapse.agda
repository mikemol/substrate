{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.WitnessTower.CyclicCollapse — ⟡cyclic-collapse (Ⓖ.cyclic-collapse, step 1 of Ⓖ.tower-basis):
-- WITNESS that the Fin iteration/order stack (σ-iterate/HasOrderPerm, now Foundation.Fin.Iterate) IS the
-- tower's cyclic-power machinery (CyclicGrounding) — i.e. that it is a structural DUPLICATE of what the
-- tower builds, hence collapsible. (It is not even F2-specific: `σ-iterate`/`HasOrderPerm`/`σ-iterate-add`
-- are over RAW `Fin n → Fin n` functions, importing only Foundation — a pure combinatorial module that WAS
-- misfiled under F2.Linear. Its true home is Foundation, NOT the tower: the tower is itself F₂-heavy — see
-- Ⓖ.tower-basis, which relocated it below both.)
--
-- The witness is the ACTION: the tower's `pow g k` (k-fold `compose` on Perm) acts as `σ-iterate k (apply g)`
-- (k-fold function iteration), via SnGroup's `apply` (= lookup). So:
--   pow-is-σ-iterate : apply (pow g k) i ≡ σ-iterate k (apply g) i          (pow IS σ-iterate under the action)
--   order-collapse   : HasOrderPerm (apply g) k → pow g k ≡ id-perm n       (their order IS the tower's order)
-- Consequently `Iterate`'s `σ-iterate-add` (additivity) and `CyclicGrounding`'s `pow-hom` are the SAME law
-- under this bridge. The duplicate is real and collapsible.
--
-- HONEST BOUNDARY (⟡H-overclaim): GROUNDED = pow-is-σ-iterate + order-collapse (the Fin iteration &
-- order ARE the tower's, via the action — the WITNESS that the stack is a build-trace). The COLLAPSE this
-- witness gated has since LANDED (Ⓖ.tower-basis, 2026-07-05): the F₂-free generator (cyclic-suc) and the
-- Fin-iterate stack were relocated BELOW F2.Linear (Algebra.Nat.CyclicSuc, Foundation.Fin.Iterate) — NOT
-- "onto the tower" (the tower is F₂-heavy), but to the F₂-free base both share.
------------------------------------------------------------------------

module Substrate.WitnessTower.CyclicCollapse where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Eq  using (_≡_; refl; sym; trans; cong)
open import Substrate.WitnessTower.Enumerate using (Perm)
open import Substrate.WitnessTower.FirstAppearance using (id-perm)
open import Substrate.WitnessTower.SnGroup using (apply; apply-compose; apply-id; apply-injective)
open import Substrate.WitnessTower.CyclicGrounding using (pow)
open import Substrate.Foundation.Fin.Iterate using (σ-iterate; HasOrderPerm)

------------------------------------------------------------------------
-- ① The bridge: the tower's `pow` ACTS AS F2.Linear's `σ-iterate`. A k-fold composition of a permutation
--    acts as the k-fold iteration of its action function — read off SnGroup's homomorphism/unit.
------------------------------------------------------------------------
pow-is-σ-iterate : {n : ℕ} (g : Perm n) (k : ℕ) (i : Fin n) →
                   apply (pow g k) i ≡ σ-iterate k (apply g) i
pow-is-σ-iterate g zero    i = apply-id i
pow-is-σ-iterate g (suc k) i =
  trans (apply-compose g (pow g k) i) (cong (apply g) (pow-is-σ-iterate g k i))

------------------------------------------------------------------------
-- ② The order collapse: F2.Linear's `HasOrderPerm` (pointwise σ^k = id) IS the tower's order (pow g k = the
--    identity permutation), by faithfulness. So the finite-order/`Zn-normalize` side of the cyclic family is
--    the tower's too — the same wrap, one construction.
------------------------------------------------------------------------
order-collapse : {n : ℕ} (g : Perm n) (k : ℕ) →
                 HasOrderPerm (apply g) k → pow g k ≡ id-perm n
order-collapse g k h =
  apply-injective (λ i → trans (pow-is-σ-iterate g k i) (trans (h i) (sym (apply-id i))))
