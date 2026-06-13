------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.RationalAdjunction
--
-- ℚ ⊣ R, FOR FREE — because of how R was architected (user, 2026-06-12): "we can
-- establish a strict adjunction between R and Q; Q just happens to peel a step of
-- the EEA trace and present it as numerator/denominator."
--
-- The pieces line up exactly:
--   • R = RealTrace is the TERMINAL COALGEBRA of the stream functor ℕ × − (proved
--     in `Final`: Lambek iso + `ana-unique`).
--   • ℚ carries the EUCLID/GAUSS COALGEBRA `qStep` for the SAME functor: from
--     (numerator, denominator) peel one EEA step — emit the CF digit ⌊a/b⌋ and
--     present the remainder as the next num/den. That is ℚ's coalgebra structure.
--   • Hence the embedding ℚ → R is `ana qStep` — the UNIQUE coalgebra morphism
--     into the terminal coalgebra (`Final.ana-unique`). It is FORCED by
--     terminality, not chosen; that is the "strict" in strict adjunction.
--   • R → ℚ is `convergent` (already in `Trace`): fold the depth-n CF prefix back
--     to a numerator/denominator — literally "present the node as num/den".
--
-- This is the inductive/coinductive duality the arc opened with
-- ([[project_substrate_real_arc]]): ℚ = a finite EEA trace that HITS `base` at the
-- gcd; R = the coinductive trace that never terminates. The unit ℚ → R → ℚ = id
-- (a rational reconstructs from its CF prefix — `unit-3/2` below, by refl).
--
-- HONEST SCOPE. `qStep` is a coalgebra for ℕ × − (always continues), but ℚ's CF is
-- FINITE — so once the remainder hits 0 (the gcd / `base`), `qStep` junk-pads
-- (emits the leftover and holds). Only the PREFIX up to the CF length is the
-- rational; `convergent` at that depth recovers it exactly, and the padding is the
-- terminated tail (ℚ is really a coalgebra for ℕ × (1 + −); the `1` is the
-- termination R lacks). The unit (this brick) is proved on the prefix; the counit
-- R → ℚ → R (the truncation, with residue = the tail beyond depth) and the
-- triangle identities are the next brick.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Algebra.R.Trace.RationalAdjunction where

open import Substrate.Foundation.Nat     using (ℕ; zero; suc)
open import Substrate.Foundation.Product using (_×_; _,_)
open import Substrate.Foundation.List    using (List; []; _∷_)
open import Substrate.Foundation.Eq      using (_≡_; refl)

open import Substrate.Algebra.Nat.Mod          using (_mod-suc_)
open import Substrate.Algebra.Nat.DivMod.DivSuc using (_div-suc_)
open import Substrate.Algebra.R.Trace        using (RealTrace; take; convergent)
open import Substrate.Algebra.R.Trace.Unfold using (unfold)

------------------------------------------------------------------------
-- ℚ's coalgebra structure: peel one EEA step. State = (numerator, denominator).
-- Emit the CF digit ⌊a/b⌋; the next ratio is (denominator / remainder).
------------------------------------------------------------------------

qStep : ℕ × ℕ → ℕ × (ℕ × ℕ)
qStep (a , zero)  = a , (a , zero)                       -- terminated at the gcd: junk-pad
qStep (a , suc b) = a div-suc b , (suc b , a mod-suc b)  -- digit, then (suc b)/remainder

------------------------------------------------------------------------
-- ℚ → R : the embedding = `ana qStep` (= unfold). The unique coalgebra morphism
-- into the terminal coalgebra RealTrace (`Final.ana-unique`) — forced, not chosen.
-- (a , d) is the rational a/(suc d).
------------------------------------------------------------------------

qToR : ℕ → ℕ → RealTrace
qToR a d = unfold qStep (a , suc d)

------------------------------------------------------------------------
-- R → ℚ is `convergent` (in `Trace`): fold the depth-n prefix to (num, den).
--
-- Witnesses on 3/2 = [1;2]:
------------------------------------------------------------------------

-- the embedding emits 3/2's continued fraction:
emit-3/2 : take 2 (qToR 3 1) ≡ 1 ∷ 2 ∷ []
emit-3/2 = refl

-- THE ADJUNCTION UNIT  ℚ → R → ℚ = id  (at the CF depth): 3/2 reconstructs exactly.
unit-3/2 : convergent 2 (qToR 3 1) ≡ (3 , 2)
unit-3/2 = refl
