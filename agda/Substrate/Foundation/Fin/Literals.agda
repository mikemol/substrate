------------------------------------------------------------------------
-- Substrate.Foundation.Fin.Literals
--
-- Subscript-digit pattern synonyms for small Fin values.
--
-- Replaces hand-written `suc ₂` chains with the
-- equivalent `₃` — readable in both expression AND pattern positions.
--
-- Per [[project_cpos_migration_arc]]'s lesson and the user's
-- "delegate to the term algebra" framing applied to Nat indices:
-- substrate already has `n-refls` and `copies` which absorb arity-
-- specific tuple construction via numeric literals. These Fin
-- patterns absorb the analogous arity-specific INDEX construction.
--
-- Each ₍digit₎ is polymorphic in the implicit Fin size, so e.g.
-- ₃ : Fin (suc (suc (suc (suc m)))) for any m ≥ 0; concrete uses
-- like `apply T ₃` infer m from context.
--
-- Naming convention matches substrate's heavy use of subscripts
-- elsewhere (Z₂, Z₃, V₄, e₀, …); the ₍digit₎ form is the natural
-- extension to position indices.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Fin.Literals where

open import Substrate.Foundation.Fin using (Fin; zero; suc)

pattern ₀ = zero
pattern ₁ = suc ₀
pattern ₂ = suc ₁
pattern ₃ = suc ₂
pattern ₄ = suc ₃
pattern ₅ = suc ₄
pattern ₆ = suc ₅
pattern ₇ = suc ₆
pattern ₈ = suc ₇
pattern ₉ = suc ₈
pattern ₁₀ = suc ₉
pattern ₁₁ = suc ₁₀
pattern ₁₂ = suc ₁₁
pattern ₁₃ = suc ₁₂
pattern ₁₄ = suc ₁₃
pattern ₁₅ = suc ₁₄
pattern ₁₆ = suc ₁₅
pattern ₁₇ = suc ₁₆
pattern ₁₈ = suc ₁₇
pattern ₁₉ = suc ₁₈
pattern ₂₀ = suc ₁₉
pattern ₂₁ = suc ₂₀
pattern ₂₂ = suc ₂₁
pattern ₂₃ = suc ₂₂
pattern ₂₄ = suc ₂₃
pattern ₂₅ = suc ₂₄
pattern ₂₆ = suc ₂₅
pattern ₂₇ = suc ₂₆
pattern ₂₈ = suc ₂₇
pattern ₂₉ = suc ₂₈
pattern ₃₀ = suc ₂₉
pattern ₃₁ = suc ₃₀
pattern ₃₂ = suc ₃₁
