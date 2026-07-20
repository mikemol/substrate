------------------------------------------------------------------------
-- Substrate.WitnessTower.AbelBetaCollapse
--
-- ◆ip-abel-β-cap — THE COLLAPSE LEMMA: an adjacent generator is recovered by
-- conjugating its neighbour through the braid,
--
--   sᵢ₊₁ ≡ (sᵢ sᵢ₊₁) · sᵢ · (sᵢ₊₁ sᵢ)
--
-- at grade `suc (suc n)`, where (per the Braid module's index convention) the
-- position-i / position-(i+1) generators are `sadj (suc n) (inj1 i)` and
-- `sadj (suc n) (suc i)` for `i : Fin n`.
--
-- THIS IS THE ONE-BIT COLLAPSE IN CONCRETE FORM. Route C
-- (`SnAbelianizationZ2`) derives `Sₙ^ab ≅ Z/2` SYNTACTICALLY: in an abelian
-- quotient, braid + involution force h(sᵢ) = h(sᵢ₊₁), so all generators carry
-- ONE bit. This lemma is that same collapse read on the CONCRETE `Perm`
-- carrier: sᵢ₊₁ is a conjugate of sᵢ (by `sᵢsᵢ₊₁`), so any class function —
-- in particular any abelian character — cannot separate them. It is the
-- concrete companion of the presented collapse, not a second proof of it.
--
-- It is PURE COVERAGE over already-proven anchors: braid (`cox-braid`),
-- involution (`sadj-involution`), associativity (`compose-assoc`) and the
-- left unit (`compose-id-left`). No new combinatorial content.
--
-- The 8-step chain (a = sᵢ, b = sᵢ₊₁; the goal is (ab)(a(ba)) ≡ b):
--   1  braid on the right factor          (ab)(a(ba)) ≡ (ab)(b(ab))
--   2  reassociate                                    ≡ a(b(b(ab)))
--   3  reassociate inward (sym)                       ≡ a((bb)(ab))
--   4  involution at b                                ≡ a(id(ab))
--   5  left unit                                      ≡ a(ab)
--   6  reassociate outward (sym)                      ≡ (aa)b
--   7  involution at a                                ≡ id·b
--   8  left unit                                      ≡ b
--
-- ⚑ ANCHOR NOTE: `compose-assoc` is the Perm one from `CyclicGrounding`; a
-- DIFFERENT `compose-assoc` (on A4Z2) lives in `M40Group` — do not import it.
--
-- --safe --without-K, no postulates/holes.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.AbelBetaCollapse where

open import Substrate.Foundation.Nat using (ℕ; suc)
open import Substrate.Foundation.Fin using (Fin; suc)
open import Substrate.Foundation.Eq using (_≡_; trans; sym; cong)
open import Substrate.WitnessTower.FirstAppearance using (compose)
open import Substrate.WitnessTower.CyclicGrounding using (compose-assoc)
open import Substrate.WitnessTower.SnGroup using (compose-id-left)
open import Substrate.WitnessTower.SignAbelianization using (sadj-involution)
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermCoxeterGeneral
  using (sadj; inj1)
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermCoxeterBraid
  using (cox-braid)

------------------------------------------------------------------------
-- ◆ip-abel-β-cap — the collapse: sᵢ₊₁ = (sᵢsᵢ₊₁) sᵢ (sᵢ₊₁sᵢ).
------------------------------------------------------------------------

abel-β-collapse : {n : ℕ} (i : Fin n) →
  compose (compose (sadj (suc n) (inj1 i)) (sadj (suc n) (suc i)))
          (compose (sadj (suc n) (inj1 i))
                   (compose (sadj (suc n) (suc i)) (sadj (suc n) (inj1 i))))
  ≡ sadj (suc n) (suc i)
abel-β-collapse {n} i =
  trans (cong (compose (compose a b)) (cox-braid i))
  (trans (compose-assoc a b (compose b (compose a b)))
  (trans (cong (compose a) (sym (compose-assoc b b (compose a b))))
  (trans (cong (compose a) (cong (λ z → compose z (compose a b))
                                 (sadj-involution (suc i))))
  (trans (cong (compose a) (compose-id-left (compose a b)))
  (trans (sym (compose-assoc a a b))
  (trans (cong (λ z → compose z b) (sadj-involution (inj1 i)))
         (compose-id-left b)))))))
  where
    a = sadj (suc n) (inj1 i)
    b = sadj (suc n) (suc i)
