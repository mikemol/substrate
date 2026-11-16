---
name: feedback_suspended_generators_not_approximations
description: "A coinductive structure (RealTrace, stream) is a SUSPENDED GENERATOR, not an approximation; the finite output you force/observe (a List to a window) is an observation OF it, not the thing. Exact equalities (round-trips, adjoint equivalence) live at the generator level as coinductive BISIMULATIONS established by SPLICING generators, not by finite equality. Keep ops generator→generator."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: c1329ff9-896f-4600-8952-67ec237e5bbc
---

(user, 2026-06-12) When I called the windowed `List ℕ` output of `exp-cf`/`log-cf`
an "approximation, not an exact map," the framing was WRONG. A `RealTrace` is a
SUSPENDED GENERATOR (a coinductive process); the windowed List is what you get by
FORCING / OBSERVING it to a depth — an observation, not the object. There is no
approximation, only suspension. (My error: collapse the generator to a List, then
call the List inexact.)

**Consequence:** exact statements — the exp⊣log round-trip, the adjoint
equivalence — live at the GENERATOR level and are COINDUCTIVE BISIMULATIONS,
established by SPLICING generators (wiring one's output into another's input),
not by finite-List equality. `exp(log x) ~ x` because the spliced generator IS
observationally x — a coinduction, not a finite computation.

**How to apply:** keep operations generator→generator (`RealTrace → RealTrace`),
not generator→List. Lift via `unfold` with the window = the OUTPUT INDEX (the
k-th digit from a window growing with k) — productive (unfold of a total step),
fuel-free, structural on the index ([[feedback_finite_window_constructive_lem]]).
The List form is the observation; the generator is the real. Round-trips are then
bisimulations on the spliced generators. Exemplar:
`Algebra.R.Trace.Transcendental.{exp-real,log-real}`; B5 = the splice bisimulation.

**That bisimulation is NOT "a separate, grander objective" (user: "this is just
Lawvere").** It is the universal property of the FINAL COALGEBRA: RealTrace is the
terminal coalgebra of S(X)=ℕ×X (Lambek ⟹ its record is a fixed-point iso = the
positive `Category.Lawvere` conclusion), the codual of the Free/initial term
algebra [[project_center_free_universal_property]]. Coinduction = the uniqueness
clause; `Algebra.R.Trace.Final.ana-unique` proves ANY two coalgebra morphisms into
RealTrace agree up to `~`, generically (d2ef283). So before calling a coinductive
equality a frontier, name it terminal-coalgebra/Lawvere — it's the routine dual of
induction. ([[feedback_transcendental_value_is_a_digit_basis]] is the sibling
"don't mislabel a dual/forcing-artifact as analytic" lesson.)
