------------------------------------------------------------------------
-- Σ-SEAM-GLUE / Ξ8 — the FULL ¬(A₄×ℤ₂ ≅ S₄), via order-transport.
--
-- ΞB3 gave the distinguishing invariant (S₄ has the order-4 element fc;
-- A₄×ℤ₂'s no-order-4 forbids it). Ξ8 turns that into a machine-checked
-- NON-ISOMORPHISM: an iso would carry fc to an order-4 element of A4Z2,
-- contradicting no-order-4.
--
-- `A4Z2≅SymV4` records exactly the iso's ORDER-RELEVANT structure — a
-- homomorphism into Sym(V₄) (the faithful action on the four masks) that
-- preserves the identity, is injective, and hits fc. EVERY group iso
-- A₄×ℤ₂ ≅ S₄ supplies these (S₄ = Sym(V₄); to = the iso; to-hom/to-ι from
-- the homomorphism; to-inj from injectivity; fc-hit from surjectivity). So
-- `no-iso : A4Z2≅SymV4 → ⊥` refutes any such iso: A₄×ℤ₂ is GENUINELY ≠ S₄.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.M40NoIso where

import Substrate.Groups.V4.Operations as V4
open import Substrate.Groups.V4.Bijection using (V₄; e)
open import Substrate.Foundation.Eq using (_≡_; refl; trans; sym; cong)
open import Substrate.Foundation.Empty using (⊥)
open import Substrate.Foundation.Product using (Σ; _,_; proj₁; proj₂)
open import Substrate.WitnessTower.M40Closure using (A4Z2; compose; ι; sq; no-order-4)
open import Substrate.WitnessTower.M40Contrast using (fc; fc-order-4; fc-not-order-2)

-- the order-relevant structure of an iso A₄×ℤ₂ ≅ S₄ = Sym(V₄).
record A4Z2≅SymV4 : Set where
  field
    to     : A4Z2 → (V₄ → V₄)
    to-hom : (g h : A4Z2) (x : V₄) → to (compose g h) x ≡ to g (to h x)
    to-ι   : (x : V₄) → to ι x ≡ x
    to-inj : (g h : A4Z2) → ((x : V₄) → to g x ≡ to h x) → g ≡ h
    fc-hit : Σ A4Z2 (λ g → (x : V₄) → to g x ≡ fc x)


open A4Z2≅SymV4
no-iso : A4Z2≅SymV4 → ⊥
no-iso iso = fc-not-order-2 fc²e≡e
  where
    T = to iso
    g = proj₁ (fc-hit iso)
    hit = proj₂ (fc-hit iso)                       -- hit : (x) → T g x ≡ fc x

    -- T(g²) acts as fc² (transport the hit through the homomorphism)
    to-g-sq : (x : V₄) → T (sq g) x ≡ fc (fc x)
    to-g-sq x = trans (to-hom iso g g x) (trans (hit (T g x)) (cong fc (hit x)))

    -- T(g⁴) acts as fc⁴ = id
    to-g-4 : (x : V₄) → T (sq (sq g)) x ≡ x
    to-g-4 x = trans (to-hom iso (sq g) (sq g) x)
                     (trans (to-g-sq (T (sq g) x))
                            (trans (cong (λ y → fc (fc y)) (to-g-sq x)) (fc-order-4 x)))

    -- so g⁴ = ι (injectivity), hence g² = ι (no-order-4) ...
    sqsq-ι : sq (sq g) ≡ ι
    sqsq-ι = to-inj iso (sq (sq g)) ι (λ x → trans (to-g-4 x) (sym (to-ι iso x)))

    sqg-ι : sq g ≡ ι
    sqg-ι = no-order-4 g sqsq-ι

    -- ... but then fc² = id (T(g²) = T(ι) = id while T(g²) = fc²), contradicting
    -- fc-not-order-2: fc² moves e.
    fc²e≡e : fc (fc e) ≡ e
    fc²e≡e = trans (sym (to-g-sq e)) (trans (cong (λ z → T z e) sqg-ι) (to-ι iso e))
