------------------------------------------------------------------------
-- Substrate.Logic.Evidence.ElAtlas.CenterIsStarAntisym  (Ξ★.aⁿ)
--
-- The UNIVERSAL self-annihilation (POINT_CLOUD §6.1): vᵀB₃v ≡ 0 for ALL v —
-- "self-annihilation is the defining property, everywhere", i.e. the
-- antisymmetry of the rung-3 cycle-space form B₃ (Ξ★.1 gave it only for the
-- specific vectors e₁, w; here it is every v). Unlike the F₂ Antisymmetric
-- tensor (where 2 = 0 makes it trivial), over ℤ this is a genuine ring identity
-- — NOT `refl`: the form `2xy + 2xz − 2xy + 2yz − 2xz − 2yz` vanishes by
-- PAIRWISE cancellation of the antisymmetric off-diagonal pairs.
--
-- Structure of the proof:
--   * pcancel       — an antisymmetric pair vanishes: a·(c·b) + b·((−c)·a) ≡ 0
--                     (the cross product commutes; the signs cancel, +ℤ-inverseʳ).
--   * sum6-cancel   — the six row-grouped terms regroup into the three cancelling
--                     pairs, via the MEDIAL law (Algebra.Medial) at ℤ's +ℤ —
--                     reusing Ⓜ for the commutative-monoid 4-term exchange.
--   * row0/1/2      — kill each diagonal 0·v term (*ℤ-zeroˡ + identity) and
--                     distribute, turning x·(B₃ row) into its two off-diagonal terms.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Logic.Evidence.ElAtlas.CenterIsStarAntisym where

open import Substrate.Foundation.Vec using (_∷_; [])
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong; cong₂)
open import Substrate.Algebra.Z using (ℤ; +_; -ℤ_; 0ℤ)
open import Substrate.Algebra.Z.Arithmetic using (_+ℤ_; _*ℤ_)
open import Substrate.Algebra.Z.Properties.Mul using (*ℤ-comm; neg-*-left)
open import Substrate.Algebra.Z.Properties.MulFull
  using (neg-*-right; *ℤ-assoc; *ℤ-zeroˡ; *ℤ-distribˡ-+)
open import Substrate.Algebra.Z.Properties.Add
  using (+ℤ-comm; +ℤ-assoc; +ℤ-identityˡ; +ℤ-identityʳ; +ℤ-inverseʳ)
open import Substrate.Algebra.Medial using (medial)
open import Substrate.Logic.Evidence.ElAtlas.CenterWitness using (dot; apply-B₃)

------------------------------------------------------------------------
-- ℤ's medial law (the 4-term middle exchange), an instance of Ⓜ.
------------------------------------------------------------------------

medialℤ : (w x y z : ℤ) → (w +ℤ x) +ℤ (y +ℤ z) ≡ (w +ℤ y) +ℤ (x +ℤ z)
medialℤ = medial _+ℤ_ +ℤ-assoc +ℤ-comm

------------------------------------------------------------------------
-- a ·ℤ (c ·ℤ b) ≡ c ·ℤ (a ·ℤ b) — pull the coefficient out front.
------------------------------------------------------------------------

reassoc : (c a b : ℤ) → a *ℤ (c *ℤ b) ≡ c *ℤ (a *ℤ b)
reassoc c a b =
  trans (sym (*ℤ-assoc a c b))
  (trans (cong (_*ℤ b) (*ℤ-comm a c)) (*ℤ-assoc c a b))

------------------------------------------------------------------------
-- The antisymmetric pair cancels: a·(c·b) + b·((−c)·a) ≡ 0.
------------------------------------------------------------------------

pcancel : (c a b : ℤ) → (a *ℤ (c *ℤ b)) +ℤ (b *ℤ ((-ℤ c) *ℤ a)) ≡ 0ℤ
pcancel c a b =
  trans (cong₂ _+ℤ_ (reassoc c a b) snd≡)
        (+ℤ-inverseʳ (c *ℤ (a *ℤ b)))
  where
    snd≡ : (b *ℤ ((-ℤ c) *ℤ a)) ≡ -ℤ (c *ℤ (a *ℤ b))
    snd≡ =
      trans (cong (b *ℤ_) (neg-*-left c a))
      (trans (neg-*-right b (c *ℤ a))
      (trans (cong -ℤ_ (reassoc c b a))
             (cong (λ t → -ℤ (c *ℤ t)) (*ℤ-comm b a))))

------------------------------------------------------------------------
-- The six row-grouped terms regroup into the three cancelling pairs.
------------------------------------------------------------------------

sum6-cancel :
  (a b c d e f : ℤ) →
  (a +ℤ c ≡ 0ℤ) → (b +ℤ e ≡ 0ℤ) → (d +ℤ f ≡ 0ℤ) →
  ((a +ℤ b) +ℤ ((c +ℤ d) +ℤ (e +ℤ f))) ≡ 0ℤ
sum6-cancel a b c d e f h₁ h₂ h₃ =
  trans (medialℤ a b (c +ℤ d) (e +ℤ f))
  (trans (cong₂ _+ℤ_ (sym (+ℤ-assoc a c d)) (sym (+ℤ-assoc b e f)))
  (trans (medialℤ (a +ℤ c) d (b +ℤ e) f)
  (trans (cong₂ _+ℤ_ (cong₂ _+ℤ_ h₁ h₂) h₃)
  (trans (+ℤ-identityʳ (0ℤ +ℤ 0ℤ)) (+ℤ-identityˡ 0ℤ)))))

------------------------------------------------------------------------
-- THE UNIVERSAL SELF-ANNIHILATION: vᵀB₃v ≡ 0 for every v = (x,y,z).
------------------------------------------------------------------------

self-annihilation :
  (x y z : ℤ) →
  dot (x ∷ y ∷ z ∷ []) (apply-B₃ (x ∷ y ∷ z ∷ [])) ≡ + 0
self-annihilation x y z =
  trans (cong₂ _+ℤ_ row0 (cong₂ _+ℤ_ row1 row2))
        (sum6-cancel (x *ℤ ((+ 2) *ℤ y)) (x *ℤ ((+ 2) *ℤ z))
                     (y *ℤ ((-ℤ (+ 2)) *ℤ x)) (y *ℤ ((+ 2) *ℤ z))
                     (z *ℤ ((-ℤ (+ 2)) *ℤ x)) (z *ℤ ((-ℤ (+ 2)) *ℤ y))
                     (pcancel (+ 2) x y) (pcancel (+ 2) x z) (pcancel (+ 2) y z))
  where
    -- row 0: x · ((0·x) + ((2·y)+(2·z)))  ≡  x·(2·y) + x·(2·z)
    row0 : (x *ℤ (((+ 0) *ℤ x) +ℤ (((+ 2) *ℤ y) +ℤ ((+ 2) *ℤ z))))
           ≡ ((x *ℤ ((+ 2) *ℤ y)) +ℤ (x *ℤ ((+ 2) *ℤ z)))
    row0 =
      trans (cong (λ t → x *ℤ (t +ℤ (((+ 2) *ℤ y) +ℤ ((+ 2) *ℤ z)))) (*ℤ-zeroˡ x))
      (trans (cong (x *ℤ_) (+ℤ-identityˡ (((+ 2) *ℤ y) +ℤ ((+ 2) *ℤ z))))
             (*ℤ-distribˡ-+ x ((+ 2) *ℤ y) ((+ 2) *ℤ z)))
    -- row 1: y · ((−2·x) + ((0·y)+(2·z)))  ≡  y·(−2·x) + y·(2·z)
    row1 : (y *ℤ (((-ℤ (+ 2)) *ℤ x) +ℤ (((+ 0) *ℤ y) +ℤ ((+ 2) *ℤ z))))
           ≡ ((y *ℤ ((-ℤ (+ 2)) *ℤ x)) +ℤ (y *ℤ ((+ 2) *ℤ z)))
    row1 =
      trans (cong (λ t → y *ℤ (((-ℤ (+ 2)) *ℤ x) +ℤ t))
                  (trans (cong (_+ℤ ((+ 2) *ℤ z)) (*ℤ-zeroˡ y))
                         (+ℤ-identityˡ ((+ 2) *ℤ z))))
            (*ℤ-distribˡ-+ y ((-ℤ (+ 2)) *ℤ x) ((+ 2) *ℤ z))
    -- row 2: z · ((−2·x) + ((−2·y)+(0·z)))  ≡  z·(−2·x) + z·(−2·y)
    row2 : (z *ℤ (((-ℤ (+ 2)) *ℤ x) +ℤ (((-ℤ (+ 2)) *ℤ y) +ℤ ((+ 0) *ℤ z))))
           ≡ ((z *ℤ ((-ℤ (+ 2)) *ℤ x)) +ℤ (z *ℤ ((-ℤ (+ 2)) *ℤ y)))
    row2 =
      trans (cong (λ t → z *ℤ (((-ℤ (+ 2)) *ℤ x) +ℤ t))
                  (trans (cong (((-ℤ (+ 2)) *ℤ y) +ℤ_) (*ℤ-zeroˡ z))
                         (+ℤ-identityʳ ((-ℤ (+ 2)) *ℤ y))))
            (*ℤ-distribˡ-+ z ((-ℤ (+ 2)) *ℤ x) ((-ℤ (+ 2)) *ℤ y))
