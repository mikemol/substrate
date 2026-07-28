------------------------------------------------------------------------
-- Σ-SEAM-GLUE / ΞB1 — the REALIZED generator actions, not the model.
--
-- v2's load-bearing obligation (Scenario B1): the REAL carrier actions
-- {spectral_translation, z3_cycle, chirality_flip} (scratch/spectral_view.py)
-- close to the A4Z2 model. The trap v2 names is proving the MODEL is a
-- direct product (a tautology). This file instead proves facts about the
-- ACTIONS on a carrier:
--
--   * `act-hom`  : `act` (the a4z2_act action) is a HOMOMORPHISM —
--                  act (compose g h) ≗ act g ∘ act h. FALSIFIABLE: if
--                  a4z2_compose were the wrong law this would not hold.
--   * `T-gen/Z-gen/chi-gen` : the three REAL actions equal `act` of the
--                  model generators (even,m,z0)/(even,e,z1)/(odd,e,z0).
--
-- Together: the real generators ARE act-images and compose per the model
-- law — the closure of the real actions reproduces the A4Z2 model.
--
-- PENDING (NOT proved here — honest scope of ΞB1's remainder):
--   * that the three model generators GENERATE all of A4Z2 (closure = act(A4Z2));
--   * `act` injective on a faithful carrier (closure ≅ A4Z2 — the full iso).
-- These complete B1; this file is its homomorphism+generator core.
--
-- Carrier convention (from the Python): spectral_translation F k = F (k·m);
-- z3_cycle = pullback by c⁻¹ = rotate²  (verified: returns F[0],F[3],F[1],F[2]
-- ⇒ index map rotate²); chirality_flip = pointwise neg. a4z2_act applies
-- cycleʲ then translate then chir, so act(s,m,j) F k = sgnˢ (F (c⁻ʲ (k·m))).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.M40Action where

import Substrate.Groups.V4.Operations as V4
open import Substrate.Groups.V4.Bijection using (V₄; e)
open import Substrate.Groups.V4.Operations using (_·_)
open import Substrate.Groups.V4.Axioms.Assoc using (·-assoc)
open import Substrate.Groups.V4.Axioms.EpsilonIdentity using (ε-identity)
open import Substrate.Groups.Actions.S3-on-V4.Generators.Rotate using (rotate)
open import Substrate.Groups.Actions.S3-on-V4.Generators.RotateIsHom using (rotate-IsHom)
open import Substrate.Groups.Actions.S3-on-V4.Generators.RotateCubeId using (rotate³-id)
open import Substrate.Foundation.Eq using (_≡_; refl; trans; sym; cong)
open import Substrate.Foundation.Product using (proj₂)
open import Substrate.WitnessTower.M40Closure
  using (Chir; even; odd; _*c_; Z3; z0; z1; z2; _+₃_; σ; A4Z2; mk; compose)
open A4Z2

ε-right : (x : V₄) → (x · e) ≡ x
ε-right = proj₂ ε-identity

------------------------------------------------------------------------
-- c⁻ʲ : the inverse cycle power on V₄ (c = rotate; c⁻¹ = rotate², c⁻² = rotate).
------------------------------------------------------------------------

cinv : Z3 → V₄ → V₄
cinv z0 v = v
cinv z1 v = rotate (rotate v)
cinv z2 v = rotate v

-- c⁻ʲ is a V₄-homomorphism (rotate-IsHom, composed for z1).
cinv-hom : (j : Z3) (a b : V₄) → cinv j (a · b) ≡ cinv j a · cinv j b
cinv-hom z0 a b = refl
cinv-hom z1 a b = trans (cong rotate (rotate-IsHom a b)) (rotate-IsHom (rotate a) (rotate b))
cinv-hom z2 a b = rotate-IsHom a b

-- c⁻ʲ²∘c⁻ʲ¹ = c⁻⁽ʲ¹⁺ʲ²⁾  (uses rotate³-id at the wraparound cases).
cinv-add : (j₁ j₂ : Z3) (a : V₄) → cinv j₂ (cinv j₁ a) ≡ cinv (j₁ +₃ j₂) a
cinv-add z0 z0 a = refl
cinv-add z0 z1 a = refl
cinv-add z0 z2 a = refl
cinv-add z1 z0 a = refl
cinv-add z1 z1 a = rotate³-id (rotate a)
cinv-add z1 z2 a = rotate³-id a
cinv-add z2 z0 a = refl
cinv-add z2 z1 a = rotate³-id a
cinv-add z2 z2 a = refl

-- c⁻ʲ ∘ cʲ = id  (the cycle and its inverse cancel; σ = cʲ forward).
cinv-σ-cancel : (j : Z3) (a : V₄) → cinv j (σ j a) ≡ a
cinv-σ-cancel z0 a = refl
cinv-σ-cancel z1 a = rotate³-id a
cinv-σ-cancel z2 a = rotate³-id a

------------------------------------------------------------------------
-- The carrier action, parametrized over any sign-carrier (𝕍, neg, neg²=id).
------------------------------------------------------------------------

module Action (𝕍 : Set) (neg : 𝕍 → 𝕍) (neg-neg : (x : 𝕍) → neg (neg x) ≡ x) where

  C : Set
  C = V₄ → 𝕍

  sgn : Chir → 𝕍 → 𝕍
  sgn even x = x
  sgn odd  x = neg x

  sgn-hom : (s t : Chir) (x : 𝕍) → sgn (s *c t) x ≡ sgn s (sgn t x)
  sgn-hom even t    x = refl
  sgn-hom odd  even x = refl
  sgn-hom odd  odd  x = sym (neg-neg x)

  -- act(s,m,j) F k = sgnˢ (F (c⁻ʲ (k · m)))  — exactly a4z2_act.
  act : A4Z2 → C → C
  act g F k = sgn (chir g) (F (cinv (zee g) (k · mask g)))

  -- THE load-bearing fact: act is a homomorphism (the model law computes
  -- the composition of the real actions). Pointwise — no funext needed.
  act-hom : (g h : A4Z2) (F : C) (k : V₄) → act (compose g h) F k ≡ act g (act h F) k
  act-hom g h F k =
    trans (sgn-hom (chir g) (chir h) (F idxL))
          (cong (λ z → sgn (chir g) (sgn (chir h) z)) (cong F idx-eq))
    where
      jg jh : Z3
      jg = zee g ; jh = zee h
      mg mh : V₄
      mg = mask g ; mh = mask h
      A B C₁ C₂ : V₄
      A  = cinv (jg +₃ jh) k
      B  = cinv (jg +₃ jh) mg
      C₁ = cinv (jg +₃ jh) (σ jg mh)
      C₂ = cinv jh mh
      idxL idxR : V₄
      idxL = cinv (jg +₃ jh) (k · (mg · σ jg mh))
      idxR = cinv jh (cinv jg (k · mg) · mh)
      C₁≡C₂ : C₁ ≡ C₂
      C₁≡C₂ = trans (sym (cinv-add jg jh (σ jg mh)))
                    (cong (cinv jh) (cinv-σ-cancel jg mh))
      idx-eq : idxL ≡ idxR
      idx-eq =
        trans (cinv-hom (jg +₃ jh) k (mg · σ jg mh))
        (trans (cong (A ·_) (cinv-hom (jg +₃ jh) mg (σ jg mh)))
        (trans (sym (·-assoc A B C₁))
        (trans (cong ((A · B) ·_) C₁≡C₂)
        (trans (cong (_· C₂) (sym (cinv-hom (jg +₃ jh) k mg)))
        (trans (cong (_· C₂) (sym (cinv-add jg jh (k · mg))))
               (sym (cinv-hom jh (cinv jg (k · mg)) mh)))))))

  ------------------------------------------------------------------------
  -- The three REAL carrier actions (faithful to spectral_view.py), and the
  -- proof each EQUALS act of the corresponding model generator.
  ------------------------------------------------------------------------

  -- spectral_translation by mask m:  F'[k] = F[k · m].
  transl : V₄ → C → C
  transl m F k = F (k · m)

  -- z3_cycle: pullback by c⁻¹ = rotate²  (F[0],F[3],F[1],F[2]).
  zcycle : C → C
  zcycle F k = F (rotate (rotate k))

  -- chirality_flip:  F ↦ neg ∘ F.
  chiflip : C → C
  chiflip F k = neg (F k)

  -- the real generators are act of the model generators:
  T-gen   : (m : V₄) (F : C) (k : V₄) → transl m F k ≡ act (mk even m z0) F k
  T-gen m F k = refl                               -- sgn even = id, c⁻ᶻ⁰ = id

  Z-gen   : (F : C) (k : V₄) → zcycle F k ≡ act (mk even e z1) F k
  Z-gen F k = cong (λ x → F (rotate (rotate x))) (sym (ε-right k))

  chi-gen : (F : C) (k : V₄) → chiflip F k ≡ act (mk odd e z0) F k
  chi-gen F k = cong (λ x → neg (F x)) (sym (ε-right k))
