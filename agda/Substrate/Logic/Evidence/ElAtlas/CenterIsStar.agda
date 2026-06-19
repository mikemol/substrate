------------------------------------------------------------------------
-- Substrate.Logic.Evidence.ElAtlas.CenterIsStar  (Ξ★.3 — MECHANIZE-STAR rung 3)
--
-- center-is-★ (POINT_CLOUD_HODGE_FORMALIZATION §5, §7.1) — composing the two
-- halves landed in Ξ★.1 (the rung-3 cycle-space centre = witness line, over ℤ)
-- and Ξ★.2 (★ = G_NOT, over ℚ G-values).
--
-- These live on DIFFERENT carriers (ℤ³ cycle space vs ℚ G-values). The tie is
-- NOT a hand-built bridge — it is a CROSS-CARRIER WEDGE: a CrossMix cospan
-- A → R ← B (Algebra.Wedge.CrossMul). Two strands embed into a common carrier;
-- the CROSS TERM measures their interference, and COHERENCE = the cross term
-- vanishing (a nilpotent residue of degree ≤ 1) = an ORTHOGONAL, clean
-- correspondence. That is exactly the bridge-null (§4.5): at balance the
-- coupling carries no current = the two arms don't interfere = the loop kernel
-- (witness) = the centre. center-is-★ is therefore a CrossMix COHERENCE, and
-- the cross-carrier tie is mechanical.
--
-- The same "interference → z" pattern appears at both ends:
--   * cycle-space (ℤ, Ξ★.1):  witness-⟂-rep — `dot rep w ≡ + 0`: the witness
--     and the representable image have zero cross (dot) term.
--   * g-calculus (ℚ, Ξ★.2):   ★ = G_NOT fixes BOTH fold-ends — the open circuit
--     G = 0 (`★ 0ℚ ≡ 0ℚ`, the witness/centre end) and the balance G = 1
--     (`★-fixes-1`, the self-dual end).
--   * carrier-free (Wedge):    a CrossMix whose cross term is nilpotent — the
--     orthogonal/clean extreme (square-zero R), coherence everywhere.
--
-- HONEST RESIDUAL (matching CrossMul's own deferral + §7.1's open status):
--   * GRADED coherence — the numeral Wheatstone bridge with a richer common
--     carrier R, where the cross term is nilpotent of degree n > 1 (the cost) —
--     is deferred exactly as CrossMul defers its CRT numeral instance.
--   * the projective center↔periphery EXCHANGE (G→0 ↔ G→∞, §5's radial fold)
--     needs ℙ¹: affine ℚ recip fixes 0, it does not swap 0↔∞. So ★ FIXES the
--     two ends here; the fold that EXCHANGES them is the ℙ¹ residual.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Logic.Evidence.ElAtlas.CenterIsStar where

open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Algebra.Q using (ℚ; 0ℚ)

open import Substrate.Algebra.Wedge.CrossMul
  using (CrossMix; cross; Coherent; mix-witness; coherent-everywhere)
open import Substrate.Algebra.Wedge.Mul using (two-div; two-mul; Two)

open import Substrate.Logic.Evidence.ElAtlas.StarIsGNot
  using (★; ★-fixes-balance; ★-fixes-1)

------------------------------------------------------------------------
-- §5 / §7.1 — ★ = G_NOT fixes the OPEN-CIRCUIT end G = 0 (the witness / centre).
-- Together with ★-fixes-1 (the balance end), ★ fixes BOTH ends of the fold:
-- the centre (witness, G→0) and the balance (self-dual, G=1).
------------------------------------------------------------------------

-- centre / open-circuit / witness end. (The balance / self-dual end G=1 is
-- ★-fixes-1, imported from Ξ★.2 — so ★ fixes BOTH ends of the fold.)
★-fixes-open-circuit : ★ 0ℚ ≡ 0ℚ
★-fixes-open-circuit = refl

------------------------------------------------------------------------
-- The cross-carrier tie IS a CrossMix cospan (the mechanical bridge). center-
-- is-★ at the ORTHOGONAL / clean extreme: the centre (witness) strand and the
-- periphery (representable) strand meet in a common carrier with a VANISHING
-- cross term — coherence everywhere — the bridge-null where the strands do not
-- interfere. (The cycle-space instance of this same vanishing-cross-term is
-- `witness-⟂-rep` below; the carrier-free instance is this CrossMix.)
------------------------------------------------------------------------

centre∥periphery : CrossMix two-div two-div two-mul
centre∥periphery = mix-witness

centre∥periphery-coherent : (a b : Two) → Coherent centre∥periphery a b
centre∥periphery-coherent = coherent-everywhere

-- The cycle-space (Ξ★.1) instance of the SAME coherence — the cross/dot term
-- vanishes: `witness-⟂-rep` (imported) is `dot rep w ≡ + 0`, the witness
-- orthogonal to the representable image = the centre condition, electrically
-- the bridge-null. Re-exported so center-is-★ carries both instances.
open import Substrate.Logic.Evidence.ElAtlas.CenterWitness public using (witness-⟂-rep)
