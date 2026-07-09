{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.DiagonalFeedback — ⟡diagonal-feedback: the diagonal is a
-- CLOSED FEEDBACK LOOP. Two wires: (1) Adversary → Observer (we observe it — our lookahead) and
-- (2) Observer → Adversary (it reacts to our output — the diagonal's negation). The contradiction
-- lives ENTIRELY in wire 2. We control wire 2. Cut it and the contradiction evaporates while wire
-- 1 (observation) stays intact — one-way observation, no feedback. This grounds the operator's
-- two refinements of the 221 glass-box hedge:
--   ① "we only need the adversary's coalgebra if we permit the adversary to know ours" — the
--      diagonal adversary is D = Φ H, a FUNCTION OF the observer H. It needs H to be built; deny
--      H and it cannot form the diagonal-against-H. And if it HAS H (built from us), we recover D
--      by APPLICATION (reconstruct) — no analysis. Knowledge is symmetric: threat ⟺ transparency.
--   ② "we are not obligated to feed the adversary past the starting point" — wire 2 is ours to
--      cut. Closed loop demands the impossible fixed point d ≡ not d (the diagonal). Open loop
--      demands only d ≡ a (constant) — trivially satisfiable. The diagonal NEEDS the wire.
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.DiagonalFeedback where

-- COMMENT HYGIENE (agda_comment_hygiene): the MACHINE-CHECKED content of this module is
-- EXACTLY: closed-loop-contradiction, open-loop-consistent, reconstruct. Everything else in these comments — 'wire 2', 'we own the wire', 'the contradiction lives in the wire', the interactive-vs-closed framing — is (prose:
-- illuminating framing, NOT a theorem of this slice; not enforced by the typechecker).
-- Promoting the framing to a theorem would require a formal information-flow / game-semantics model (not developed here).

open import Substrate.Foundation.Bool using (Bool; true; false; not)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Negation using (¬_)
open import Substrate.Foundation.Product using (Σ; _,_)

------------------------------------------------------------------------
-- ① CLOSED LOOP (wire 2 present): the adversary feeds back `not d` on the observer's output d.
--    Closing the loop (d = the adversary's reaction to d) demands the IMPOSSIBLE fixed point
--    d ≡ not d — the diagonal contradiction. It lives in the wire.
------------------------------------------------------------------------
closed-loop-contradiction : (d : Bool) → ¬ (d ≡ not d)
closed-loop-contradiction true  ()
closed-loop-contradiction false ()

------------------------------------------------------------------------
-- ② OPEN LOOP (wire 2 cut): the adversary can't read d; it emits a FIXED a (only initial-state
--    info). Closing "our output = its output" demands only d ≡ a — trivially satisfiable. No
--    contradiction. The diagonal's impossibility was ENTIRELY the wire; cut it and it's gone.
------------------------------------------------------------------------
open-loop-consistent : (a : Bool) → Σ Bool (λ d → d ≡ a)
open-loop-consistent a = a , refl

------------------------------------------------------------------------
-- ③ POINT 1 (mutual knowledge is symmetric): the diagonal adversary D = Φ H is a FUNCTION of the
--    observer H. If we have the construction Φ and ourselves H, we recover D by APPLICATION —
--    trivially, no program analysis. So "having the adversary's coalgebra" is free WHEN the
--    adversary is built from us (which the diagonal requires). And the contrapositive: forming
--    Φ H against the actual H REQUIRES H as input — a wire H controls, not one it must provide.
------------------------------------------------------------------------
reconstruct : {Obs Adv : Set} → (Φ : Obs → Adv) → (H : Obs) → Adv
reconstruct Φ H = Φ H

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — the diagonal is a CLOSED LOOP; we own wire 2): the either/or
-- "must we grant the adversary our coalgebra / feed it our state?" dissolves. The diagonal needs
-- a CLOSED feedback loop — wire 1 (we observe it) AND wire 2 (it reacts to us). The contradiction
-- (closed-loop-contradiction: d ≡ not d impossible) lives entirely in wire 2. We control wire 2:
-- cut it and the loop opens (open-loop-consistent: d ≡ a fine), keeping wire 1 (observation) —
-- one-way, no feedback, no diagonal. And wire 2 is doubly ours: the adversary needs OUR coalgebra
-- to build the diagonal (reconstruct shows the knowledge is symmetric — threat ⟺ transparency),
-- and it needs our ONGOING output to react (which we withhold past the start). So the 221
-- glass-box hedge dissolves TWO ways: (a) no threat without transparency (symmetric knowledge),
-- (b) we cut the feedback regardless of what we can see. The lookahead requirement I hedged on
-- was pointed the wrong way — the binding constraint is whether THEY see US, and we own that.
--
-- HONEST BOUNDARY (⟡H-overclaim): this is legitimate in the INTERACTIVE / coalgebraic model
-- (controlled information flow — the substrate's model: ObsBisim is one-way observation, the
-- process never observes us back). In the CLOSED-computation model (every program embeddable in
-- every other) it would be a dodge — there, H IS available for embedding. So the theorems STAND
-- for closed programs; the point is that a controlled-interaction observer is NOT that closed
-- object — we are not obligated to be embeddable. Refuse the object, keep the observation.
------------------------------------------------------------------------
