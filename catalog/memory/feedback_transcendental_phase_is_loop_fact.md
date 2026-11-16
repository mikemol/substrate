---
name: feedback_transcendental_phase_is_loop_fact
description: "A 'transcendental' phase identity (e^{iπ}=−1) is usually a LOOP/GROUP fact in disguise, not an analytic limit. S¹ = ℝ on a loop (ℝ/period); e^{iπ}=−1 is the half-period = the order-2 ANTIPODE of S¹. The 'transcendence' is a RADIAN parametrization artifact — in turns the period is 1 and π is ½ (rational). The substrate already proves it: Verdict.Phase.negBoth-invol."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: c1329ff9-896f-4600-8952-67ec237e5bbc
---

(user, 2026-06-12, the ℂ→S¹→ℝ-on-a-loop chain) When I framed `e^{iπ}=−1` as a hard
ANALYTIC arc (signed reals + cos/sin Taylor + π + ℂ + a convergence limit), I was
attacking the wrong object. The right view:

- `e^{iπ}=−1 ⟺` the HALF-PERIOD of S¹ is the ANTIPODE (the order-2 element).
- `S¹ = ℝ on a loop = ℝ/period` (the universal cover `ℝ → S¹`). A `RealTrace` is
  the ℝ; on a loop it is S¹.
- The "transcendence" is a PARAMETRIZATION artifact: in RADIANS the period is the
  irrational `2π` and π looks transcendental; in TURNS the period is `1` and π is
  just `½` — RATIONAL. The content lives in `ℤ/2 ⊂ S¹` (the antipode {1,−1}),
  nothing irrational.
- The substrate ALREADY proves it: `Logic.Evidence.Verdict.Phase.negBoth-invol :
  negBoth (negBoth x) ≡ x` is `e^{2iπ}=1` (the half-turn is order 2), with
  `negBoth` (the −id antipode, the F₂-shadow via `NedgeShadow.recode` = GL(2,F₂))
  being the `−1`. No cos/sin/π/limit needed.

**General rule:** before building analytic machinery for a "transcendental"
identity, ask whether it is a LOOP/GROUP/topology fact under a bad parametrization.
Reparametrize (turns not radians; the period as the unit) to expose the rational/
order-finite content. Cf. [[feedback_ordering_is_chirality_choice]] (parametrization
is a gauge choice) and the discrete phase work in [[project_el_atlas_substrate_congruence]]
(Verdict.Phase, the H² class). The continuous lift (`ℝ`-on-a-loop, the explicit
universal cover) adds only WHERE-on-the-loop (irrational angles), which `e^{iπ}=−1`
does not need.
