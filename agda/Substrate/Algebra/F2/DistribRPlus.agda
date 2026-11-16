------------------------------------------------------------------------
-- Substrate.Algebra.F2.DistribRPlus
--
-- Defines: ·-distribʳ-+
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.F2; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.DistribRPlus where

open import Substrate.Foundation.Empty.Bot
open import Substrate.Foundation.Empty.BotElim
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.PlusF
open import Substrate.Algebra.F2.Op
open import Substrate.Algebra.F2.Comm
open import Substrate.Algebra.F2.DistribLPlus



·-distribʳ-+ : (x y z : F₂) → ((y +F z) · x) ≡ ((y · x) +F (z · x))
·-distribʳ-+ x y z =
  trans (·-comm (y +F z) x)
        (trans (·-distribˡ-+ x y z)
               (cong₂ _+F_ (·-comm x y) (·-comm x z)))
