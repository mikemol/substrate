------------------------------------------------------------------------
-- Substrate.Groups.Actions.S3-on-V4.Generators.IterPowIsHom
--
-- If a generator g is a V₄-homomorphism, so is `iter-pow g w` for ANY
-- word w (induction on w; each step is one g, a hom, composed with the
-- IH via ∘-IsHom). Hence rot-pow = iter-pow rotate and swap-pow =
-- iter-pow swap-αβ are homomorphisms at every word — no per-canonical
-- table. This is the generic engine of the structural collapse.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.S3-on-V4.Generators.IterPowIsHom where

open import Substrate.Groups.V4 using (V₄)
open import Substrate.Groups.Coxeter.Word using (Word; []; _∷_)
open import Substrate.Groups.V4.IsHomomorphism using (IsHomomorphism)
open import Substrate.Groups.V4.IsHomomorphism.Compose using (id-IsHom; ∘-IsHom)
open import Substrate.Groups.Actions.S3-on-V4.Generators.IterPow using (iter-pow)

iter-pow-IsHom :
  {Gen : Set} {g : V₄ → V₄} → IsHomomorphism g →
  (w : Word Gen) → IsHomomorphism (iter-pow g w)
iter-pow-IsHom g-hom []      = id-IsHom
iter-pow-IsHom {g = g} g-hom (_ ∷ w) =
  ∘-IsHom {f = g} {g = iter-pow g w} g-hom (iter-pow-IsHom g-hom w)
