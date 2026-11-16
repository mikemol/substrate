------------------------------------------------------------------------
-- Substrate.WitnessTower.SignZ2Coordinates.GMult
--
-- Defines: G-mult
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.SignZ2Coordinates; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.WitnessTower.SignZ2Coordinates.GMult where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Vec
open import Substrate.Foundation.Fin.Punctured
open import Substrate.WitnessTower.Enumerate
open import Substrate.WitnessTower.FirstAppearance
open import Substrate.WitnessTower.SnGroup
open import Substrate.WitnessTower.CyclicGrounding
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermSign
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermCoxeterGeneral
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermSignChirality
open import Substrate.WitnessTower.InsertionParity
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Cong
open import Substrate.WitnessTower.SignZ2Coordinates.G
open import Substrate.WitnessTower.SignZ2Coordinates.GSwap



-- G invariant under right-composition by ANY Coxeter word (a permutation).
G-mult : {m : ℕ} (p : Fin (suc m)) (v : Perm m) {τ : Perm m} →
         CoxGen τ → G p (compose v τ) ≡ G p v
G-mult p v cox-id      = cong (G p) (compose-id-right v)
G-mult p v (cox-s j)   = trans (cong (G p) (bridge v j)) (G-swap p j v)
G-mult p v (cox-∘ {σ = σ'} {τ = τ'} g h) =
  trans (cong (G p) (sym (compose-assoc v σ' τ')))
        (trans (G-mult p (compose v σ') h) (G-mult p v g))
