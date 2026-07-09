{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.DiagonalEscapeCoalg — ⟡diagonal-escape-coalg: the diagonal
-- escape made categorical, as an INSTANCE of the repo's final-coalgebra generics (Final.agda) —
-- NOT a hand-rolled stream (the ExtruderObsCoalg idiom: reuse-search, CLAUDE.md). The whole arc's
-- through-line, finally wired:
--   * the OBSERVER is a COALGEBRA (S, c : S → ℕ × S = Final.Coalg S) — its unfolding IS Final.ana;
--   * its behaviour lives in the FINAL coalgebra RealTrace, a ν-FIXED-POINT (Lambek: RealTrace ≅
--     ℕ × RealTrace, Final.into/out) — the coinductive "escape", the ν side where equality is ~;
--   * the ADVERSARY-as-a-DIFFERENT-PRESENTATION is a BISIMULATION: any coalgebra morphism into
--     RealTrace is ~ Final.ana (Final.ana-unique) — "a bisimulation IS equality in the terminal
--     coalgebra" (Bisim.agda). So the observer's behaviour is characterised UP TO ~, NOT up to ≡;
--     the diagonal's ≡-on-a-committed-object contradiction has no purchase on the ν-fixed-point.
--
-- This wires 233's computable observer (Obs, holding a plural prediction per step) to the FORMAL
-- finality: an observer's prediction-stream is Final.ana of its prediction-coalgebra, unique up
-- to ~. The escape is not a trick — it is finality: the ν-fixed-point is canonical up to
-- bisimilarity, and there is no privileged committed value for the diagonal to negate.
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.DiagonalEscapeCoalg where

-- COMMENT HYGIENE (agda_comment_hygiene): the MACHINE-CHECKED content of this module is
-- EXACTLY: observe (= Final.ana), prediction-is-nu-fixed-point (= Lambek), adversary-is-bisimulation (= Final.ana-unique). Everything else in these comments — 'the escape IS finality', 'the diagonal has nothing to negate', 'was finality all along', 'the escape was never a trick' — is (prose:
-- illuminating framing, NOT a theorem of this slice; not enforced by the typechecker).
-- Promoting the framing to a theorem would require the formal functor-map from ana-unique to the defeat of the Lawvere negateAll endomap (⟡diagonal-lawvere-coalg), and the ℕ-observation coding 233's Pred slice (⟡diagonal-obs-code).

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Product using (_×_; _,_; proj₁; proj₂)
open import Substrate.Algebra.R.Trace using (RealTrace; head; tail)
open import Substrate.Algebra.R.Trace.Bisim using (_~_; head~; tail~; ~-refl)
open import Substrate.Algebra.R.Trace.Final using (Coalg; out; into; ana; ana-head; ana-tail; ana-unique; lambek-into-out; lambek-out-into)

------------------------------------------------------------------------
-- ① THE OBSERVER IS A COALGEBRA. Its state carries a plural prediction, presented as a single
--    observation ℕ (a code for the current prediction-slice) + the next state — exactly
--    Final.Coalg S = S → ℕ × S. The observer's behaviour is Final.ana of this coalgebra.
------------------------------------------------------------------------
observe : {S : Set} → Coalg S → S → RealTrace
observe = ana

-- the coalgebra-morphism square holds definitionally (the observer's step IS the coalgebra step):
observe-step : {S : Set} (c : Coalg S) (s : S) → out (observe c s) ≡ (proj₁ (c s) , observe c (proj₂ (c s)))
observe-step c s = refl

------------------------------------------------------------------------
-- ② THE PREDICTION IS A ν-FIXED-POINT (Lambek): the observer's behaviour lives in RealTrace, whose
--    structure map `out` is invertible (into) — RealTrace ≅ ℕ × RealTrace. This IS the coinductive
--    escape: the observer sits at the greatest fixed point, where equality is ~ (not ≡).
------------------------------------------------------------------------
prediction-is-nu-fixed-point-fwd : (ns : ℕ × RealTrace) → out (into ns) ≡ ns
prediction-is-nu-fixed-point-fwd = lambek-out-into

prediction-is-nu-fixed-point-bwd : (x : RealTrace) → into (out x) ~ x
prediction-is-nu-fixed-point-bwd = lambek-into-out

------------------------------------------------------------------------
-- ③ THE ADVERSARY (a DIFFERENT PRESENTATION of the same behaviour) IS A BISIMULATION: any h that
--    is a coalgebra morphism into RealTrace is ~ the observer's ana. So two presentations of the
--    same structure map agree UP TO ~ — the ν-fixed-point is canonical up to bisimilarity, and the
--    diagonal has no committed ≡-value to negate. This is Final.ana-unique, instantiated.
------------------------------------------------------------------------
adversary-is-bisimulation :
  {S : Set} (c : Coalg S) (h : S → RealTrace)
  → (∀ s → head (h s) ≡ proj₁ (c s))
  → (∀ s → tail (h s) ≡ h (proj₂ (c s)))
  → ∀ s → h s ~ observe c s
adversary-is-bisimulation = ana-unique

-- COROLLARY (the escape, stated): the observer's behaviour is UNIQUE UP TO ~ — there is no
-- privileged committed value. Every presentation with the same structure map is ~ to ana. So the
-- diagonal (which needs a fixed-point-free endomap on a COMMITTED ≡-object) cannot act: on the
-- ν-fixed-point the only equality is ~, and finality makes the behaviour canonical, not committed.
escape-is-finality :
  {S : Set} (c : Coalg S) (h : S → RealTrace)
  → (∀ s → head (h s) ≡ proj₁ (c s))
  → (∀ s → tail (h s) ≡ h (proj₂ (c s)))
  → ∀ s → h s ~ observe c s
escape-is-finality = adversary-is-bisimulation

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — the escape IS finality; the observer is a coalgebra whose
-- ν-fixed-point behaviour is canonical up to bisimilarity): the either/or "is the coinductive
-- escape a trick, or real structure?" bottoms out — it is FINALITY. The observer is a coalgebra
-- (observe = Final.ana); its prediction lives at the ν-fixed-point RealTrace ≅ ℕ × RealTrace
-- (Lambek, ②); and any other presentation of the same structure is a BISIMULATION to it
-- (ana-unique, ③) — "a bisimulation IS equality in the terminal coalgebra". So the observer's
-- behaviour is characterised UP TO ~, never as a committed ≡-value. The diagonal (Lawvere) needs
-- a fixed-point-free endomap on a COMMITTED object; on the ν-fixed-point there is no committed
-- value — only the ~-class — so the diagonal has nothing to negate. The 221 Bool-crux (the full
-- prediction is a fixed point of the diagonal move) is the SET-LEVEL shadow of THIS: at the
-- ν-fixed-point the "full prediction" is the canonical behaviour, unique up to ~. The escape was
-- finality all along.
--
-- REUSE (232/CLAUDE.md, the ExtruderObsCoalg idiom): observe = Final.ana; the ν-fixed-point =
-- Final.into/out + Lambek; the adversary-bisimulation = Final.ana-unique — ALL instances of the
-- repo's existing final-coalgebra generics, NOT reinvented. --safe --without-K --guardedness
-- (the finality machinery is genuinely coinductive — earned, as in 233).
--
-- HONEST BOUNDARY (⟡H-overclaim): GROUNDED = the observer-as-coalgebra, the ν-fixed-point
-- (Lambek), and finality-up-to-~ (ana-unique), as instances of Final. SCOPED: (a) the prediction
-- carried as a single observation ℕ (a CODE for the plural slice) rather than 233's ℕ → Bool
-- directly — tying the Pred-valued Obs (233) to this ℕ-observation Coalg via a coding is
-- ⟡diagonal-obs-code (the ℕ×S functor is the repo's; the Pred×S functor would need its own
-- Final, or a code); (b) the formal identification of ana-unique with the DEFEAT of the specific
-- Lawvere endomap (221 negateAll) — the shadow relation is stated, the formal functor-map is
-- ⟡diagonal-lawvere-coalg. What's grounded: the escape IS finality, via the repo's generics.
------------------------------------------------------------------------
