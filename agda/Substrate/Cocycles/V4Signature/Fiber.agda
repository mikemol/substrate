------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.Fiber
--
-- The CY-5 fiber: every orbit has V₄ as its torsor carrier. The
-- constant function `λ _ → V₄` over OrbitKey, paired with the
-- per-orbit torsor witness.
--
-- In the strong-discipline formulation this captures that every
-- orbit has the same internal structure (V₄-torsor) — orbit_key
-- distinguishes WHICH orbit; within an orbit, the elements form a
-- V₄-torsor with no canonical baseline.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.Fiber where

open import Substrate.Cocycle using (IsTorsor)
open import Substrate.Groups.V4 using (V₄)
open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.Cocycles.V4Signature.OrbitKey.Type using (OrbitKey)
open import Substrate.Cocycles.V4Signature.V4GroupSetoid using (V₄-Group-Setoid)
open import Substrate.Cocycles.V4Signature.V4IsTorsor    using (V4-is-torsor)

Fiber : OrbitKey → Set
Fiber _ = V₄

fiber-torsor : (i : OrbitKey) → IsTorsor V₄ _≡_ V₄-Group-Setoid (Fiber i)
fiber-torsor _ = V4-is-torsor
