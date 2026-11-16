------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationRigCatPermCoxeterBraid.TpBraid
--
-- Defines: tp-braid
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.Wedge.OrientationRigCatPermCoxeterBraid; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationRigCatPermCoxeterBraid.TpBraid where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermSign
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermCoxeterGeneral
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Cong



------------------------------------------------------------------------
-- 2. THE TWO PURE-Fin LEMMAS on the index transposition tp (cong-suc inductions,
--    all bases refl — the whole combinatorial content lives here).
------------------------------------------------------------------------

-- the braid identity on indices (6 clauses: 4 concrete at i=zero, 2 at i=suc).
tp-braid : {n : ℕ} (i : Fin n) (x : Fin (suc (suc n))) →
           tp (inj1 i) (tp (suc i) (tp (inj1 i) x))
           ≡ tp (suc i) (tp (inj1 i) (tp (suc i) x))
tp-braid zero    zero                = refl
tp-braid zero    (suc zero)          = refl
tp-braid zero    (suc (suc zero))    = refl
tp-braid zero    (suc (suc (suc x))) = refl
tp-braid (suc i) zero                = refl
tp-braid (suc i) (suc x)             = cong suc (tp-braid i x)
