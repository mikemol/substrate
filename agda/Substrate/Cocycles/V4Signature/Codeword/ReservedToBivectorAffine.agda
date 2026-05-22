------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.Codeword.ReservedToBivectorAffine
--
-- ONE concrete sacrifice on the V₄-equivariance ladder (per memory
-- `project_reserved_selfdual_bijection_gauge`): a Reserved → SelfDual
-- bijection that's F₂-AFFINE (not F₂-linear) and V₄-equivariant.
--
-- File-per-lemma decomposition:
--
--   ReservedToBivectorAffine.V4               — V₄ = F₂² + _+V₄_
--   ReservedToBivectorAffine.XorSelf          — xor-self helper
--   ReservedToBivectorAffine.ActReserved      — V₄ action on Reserved
--   ReservedToBivectorAffine.Shift            — V₄ → Bivector map
--   ReservedToBivectorAffine.ShiftSelfDual    — shift targets are self-dual
--   ReservedToBivectorAffine.ShiftHom         — shift is a group hom (16 cases)
--   ReservedToBivectorAffine.ActSelfDual      — V₄ action on SelfDual
--   ReservedToBivectorAffine.BaseBivector     — sign-dependent offset + sd-witness
--   ReservedToBivectorAffine.AffineBijection  — reserved-to-selfdual-affine
--   ReservedToBivectorAffine.BivectorEquivariance — bivector-level identity
--   ReservedToBivectorAffine.V4EquivarianceProj   — proj₁-level equivariance
--   ReservedToBivectorAffine.SelfDualPredIrr      — Hedberg-based irrelevance
--   ReservedToBivectorAffine.V4Equivariance       — Σ-level equivariance
--
-- The sacrifice: F₂-linearity. The recovery: V₄-equivariance under a
-- specific V₄ subgroup of Aff(3, F₂). The Cayley-Dickson analogue
-- would be "sacrifice commutativity to gain quaternion structure."
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.Codeword.ReservedToBivectorAffine where

open import Substrate.Cocycles.V4Signature.Codeword.ReservedToBivectorAffine.V4                  public
open import Substrate.Cocycles.V4Signature.Codeword.ReservedToBivectorAffine.XorSelf             public
open import Substrate.Cocycles.V4Signature.Codeword.ReservedToBivectorAffine.ActReserved         public
open import Substrate.Cocycles.V4Signature.Codeword.ReservedToBivectorAffine.Shift               public
open import Substrate.Cocycles.V4Signature.Codeword.ReservedToBivectorAffine.ShiftSelfDual       public
open import Substrate.Cocycles.V4Signature.Codeword.ReservedToBivectorAffine.ShiftHom            public
open import Substrate.Cocycles.V4Signature.Codeword.ReservedToBivectorAffine.ActSelfDual         public
open import Substrate.Cocycles.V4Signature.Codeword.ReservedToBivectorAffine.BaseBivector        public
open import Substrate.Cocycles.V4Signature.Codeword.ReservedToBivectorAffine.AffineBijection     public
open import Substrate.Cocycles.V4Signature.Codeword.ReservedToBivectorAffine.BivectorEquivariance public
open import Substrate.Cocycles.V4Signature.Codeword.ReservedToBivectorAffine.V4EquivarianceProj  public
open import Substrate.Cocycles.V4Signature.Codeword.ReservedToBivectorAffine.SelfDualPredIrr     public
open import Substrate.Cocycles.V4Signature.Codeword.ReservedToBivectorAffine.V4Equivariance      public
