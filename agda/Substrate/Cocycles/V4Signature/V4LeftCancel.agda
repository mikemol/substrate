------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.V4LeftCancel
--
-- Left cancellation in V₄: g · h ≡ h ⟹ g ≡ e. The freeness witness
-- for V₄-acting-on-itself, established by exhaustive case analysis
-- over the 4×4 multiplication table.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.V4LeftCancel where

open import Substrate.Foundation.Eq using (_≡_; refl; sym)
open import Substrate.Groups.V4 as V4 using (V₄; e; α; β; γ)

V4-left-cancel : (g h : V₄) → g V4.· h ≡ h → g ≡ e
V4-left-cancel e h _ = refl
V4-left-cancel α e p = p
V4-left-cancel α α p = sym p
V4-left-cancel α β ()
V4-left-cancel α γ ()
V4-left-cancel β e p = p
V4-left-cancel β α ()
V4-left-cancel β β p = sym p
V4-left-cancel β γ ()
V4-left-cancel γ e p = p
V4-left-cancel γ α ()
V4-left-cancel γ β ()
V4-left-cancel γ γ p = sym p
