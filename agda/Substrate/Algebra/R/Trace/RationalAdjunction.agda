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

open import Substrate.Foundation.Nat     using (ℕ; zero; suc; _+_; _*_)
open import Substrate.Foundation.Product using (_×_; _,_; proj₁; proj₂)
open import Substrate.Foundation.List    using (List; []; _∷_)
open import Substrate.Foundation.Eq      using (_≡_; refl; sym; trans; cong₂)

open import Substrate.Foundation.Nat.Properties.Add using (+-comm)
open import Substrate.Algebra.Nat.DivMod.Reconstruction using (div-mod-eq)

open import Substrate.Algebra.Nat.Mod          using (_mod-suc_)
open import Substrate.Algebra.Nat.DivMod.DivSuc using (_div-suc_)
open import Substrate.Algebra.R.Trace        using (RealTrace; head; tail; take; convergent; sqrt2)
open import Substrate.Algebra.R.Trace.Bisim  using (_~_)
open import Substrate.Algebra.R.Trace.Final  using (Coalg; ana; ana-head; ana-tail; ana-unique)

------------------------------------------------------------------------
-- ℚ's coalgebra structure: peel one EEA step. State = (numerator, denominator).
-- Emit the CF digit ⌊a/b⌋; the next ratio is (denominator / remainder).
------------------------------------------------------------------------

qStep : Coalg (ℕ × ℕ)        -- = (ℕ × ℕ) → ℕ × (ℕ × ℕ)
qStep (a , zero)  = a , (a , zero)                       -- terminated at the gcd: junk-pad
qStep (a , suc b) = a div-suc b , (suc b , a mod-suc b)  -- digit, then (suc b)/remainder

------------------------------------------------------------------------
-- ℚ → R : the embedding = `ana qStep`, the anamorphism into the terminal
-- coalgebra. `qToRℚ` takes the (num, den) pair directly (so `convergent`'s output
-- feeds straight back in); `qToR a d` is the rational a/(suc d).
------------------------------------------------------------------------

qToRℚ : ℕ × ℕ → RealTrace
qToRℚ = ana qStep

qToR : ℕ → ℕ → RealTrace
qToR a d = qToRℚ (a , suc d)

------------------------------------------------------------------------
-- FORCED, NOT CHOSEN — now a theorem, not prose. By `Final.ana-unique`, ANY
-- coalgebra morphism from (ℕ×ℕ, qStep) into RealTrace is bisimilar to `qToRℚ`.
-- So the embedding ℚ → R is the UNIQUE one the terminal coalgebra admits.
------------------------------------------------------------------------

qToRℚ-unique : (h : ℕ × ℕ → RealTrace)
             → (∀ s → head (h s) ≡ proj₁ (qStep s))
             → (∀ s → tail (h s) ≡ h (proj₂ (qStep s)))
             → ∀ s → h s ~ qToRℚ s
qToRℚ-unique = ana-unique qStep

------------------------------------------------------------------------
-- R → ℚ is `convergent` (in `Trace`): fold the depth-n prefix to (num, den).
--
-- Witnesses on 3/2 = [1;2]:
------------------------------------------------------------------------

-- the embedding emits 3/2's continued fraction:
emit-3/2 : take 2 (qToR 3 1) ≡ 1 ∷ 2 ∷ []
emit-3/2 = refl

-- THE ADJUNCTION UNIT  ℚ → R → ℚ = id  (at the CF depth): 3/2 reconstructs exactly.
-- (This is one INSTANCE, exact/definitional. The general unit "convergent depth ∘
-- qToR = id for every rational" is the CF-reconstruction theorem — true, shown here
-- on a witness, not yet proved ∀q.)
unit-3/2 : convergent 2 (qToR 3 1) ≡ (3 , 2)
unit-3/2 = refl

------------------------------------------------------------------------
-- FOLLOW-THROUGH on "prove the general unit". Doing so reveals the naive ∀-form is
-- FALSE, and pins exactly why: the junk-padding past the CF length DRIFTS the
-- convergent. 3/2 = [1;2] is recovered at depth 2, but at depth 3 the padding
-- digit corrupts it to 4/3 ≠ 3/2:
------------------------------------------------------------------------

unit-drift : convergent 3 (qToR 3 1) ≡ (4 , 3)
unit-drift = refl

-- So the unit is exact ONLY at the CF-length depth; the general ∀q unit needs a
-- length function AND is broken by the junk-padded embedding (the `1 + −`
-- termination R lacks — the residue we discarded by padding). The substrate-clean
-- general unit lives over EEATrace, which HAS `base` (it does not pad); that bridge
-- is the honest general theorem, NOT a coinductive freebie. (This is why the
-- "one case" was not idly hedged: the general statement is genuinely different.)

------------------------------------------------------------------------
-- What IS general and free, by the terminal-coalgebra machinery (∀ state, refl):
-- qToRℚ commutes with peeling one EEA step — the per-step unit, for every rational.
------------------------------------------------------------------------

morph-head : (s : ℕ × ℕ) → head (qToRℚ s) ≡ proj₁ (qStep s)
morph-head = ana-head qStep

morph-tail : (s : ℕ × ℕ) → tail (qToRℚ s) ≡ qToRℚ (proj₂ (qStep s))
morph-tail = ana-tail qStep

------------------------------------------------------------------------
-- THE RIGHT WAY (user): don't fold globally with `convergent n` (it runs past the
-- CF length into the padding and drifts). Invert ONE `qStep` LOCALLY via the Wedge
-- a = q·b + r (`div-mod-eq`), and recurse. `reconStep` is that local inverse: from
-- the emitted digit q and the next state (b, r), rebuild (q·b + r, b) = the state.
------------------------------------------------------------------------

reconStep : ℕ → ℕ × ℕ → ℕ × ℕ
reconStep q (b , r) = q * b + r , b

-- The LOCAL unit, GENERAL (∀ a b, not one case): reconStep inverts qStep exactly,
-- by the division equation. No convergent, no padding, no drift. This is the body
-- the full unit recurses — bottoming out at `base` (remainder 0), so it never
-- reaches the padding that drifted the global form ([[feedback_never_discard_residue]]:
-- the residue r is exactly what `reconStep` keeps, the Wedge a = q·b + r).
qStep-recon : (a b : ℕ)
            → reconStep (proj₁ (qStep (a , suc b))) (proj₂ (qStep (a , suc b))) ≡ (a , suc b)
qStep-recon a b =
  cong₂ _,_
    (trans (+-comm ((a div-suc b) * suc b) (a mod-suc b)) (sym (div-mod-eq a b)))
    refl

------------------------------------------------------------------------
-- THE COUNIT  R → ℚ → R  — a DECOMPOSITION, not identity. Take the depth-n
-- convergent (lossy: a rational) and re-embed it. It agrees with r on the PREFIX
-- (the first n CF digits — the convergent's CF IS r's truncation), and the
-- RESIDUE is r's tail beyond depth n. So `counit n` is "keep n digits, drop the
-- rest" — the finite observation, with the dropped tail as the residue
-- ([[feedback_wedge_not_projection]]: the truncation is the lossy LOOK; r is the
-- generator). Witnessed on √2 = [1;2,2,2,…]: depth-2 counit agrees with √2's prefix
-- (its convergent is 3/2 = [1;2]); the residue is the 2,2,2,… that 3/2 cannot hold.
------------------------------------------------------------------------

counit : ℕ → RealTrace → RealTrace
counit n r = qToRℚ (convergent n r)

counit-prefix-√2 : take 2 (counit 2 sqrt2) ≡ take 2 sqrt2
counit-prefix-√2 = refl
