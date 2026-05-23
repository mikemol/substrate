------------------------------------------------------------------------
-- Substrate.ShadowArchitecture.Raven.PhaseTransition.StanzaIndices
--
-- s1 .. s18 : named Fin 18 indices into the 18-stanza Raven vector.
--
-- Each sₖ is built as suc^(k-1) zero — explicit because `sₖ₊₁ = suc sₖ`
-- would make `sₖ₊₁ : Fin 19` rather than `Fin 18`.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.ShadowArchitecture.Raven.PhaseTransition.StanzaIndices where

open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Fin.Literals using (₁; ₂; ₃; ₄; ₅; ₆; ₇; ₈; ₉; ₁₀; ₁₁; ₁₂; ₁₃; ₁₄; ₁₅; ₁₆)

s1  : Fin 18 ; s1  = zero
s2  : Fin 18 ; s2  = suc zero
s3  : Fin 18 ; s3  = suc ₁
s4  : Fin 18 ; s4  = suc ₂
s5  : Fin 18 ; s5  = suc ₃
s6  : Fin 18 ; s6  = suc ₄
s7  : Fin 18 ; s7  = suc ₅
s8  : Fin 18 ; s8  = suc ₆
s9  : Fin 18 ; s9  = suc ₇
s10 : Fin 18 ; s10 = suc ₈
s11 : Fin 18 ; s11 = suc ₉
s12 : Fin 18 ; s12 = suc ₁₀
s13 : Fin 18 ; s13 = suc ₁₁
s14 : Fin 18 ; s14 = suc ₁₂
s15 : Fin 18 ; s15 = suc ₁₃
s16 : Fin 18 ; s16 = suc ₁₄
s17 : Fin 18 ; s17 = suc ₁₅
s18 : Fin 18 ; s18 = suc ₁₆
