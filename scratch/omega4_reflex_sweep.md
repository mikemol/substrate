# Ω4 — the reflex sweep (analytic/transcendental/limit scope-outs → formal structure)

The G9-general reflex sweep: audit the codebase for things labelled **analytic / transcendental / "in
the limit" / out-of-reach / needs-ℝ / only-classical** that are actually FORMAL structure (the
structure-vs-value confusion), and apply the corrected lesson retroactively. Standing triggers:
[[feedback_trace_inversion_vs_transcendental_limit]], [[feedback_transcendental_value_is_a_digit_basis]],
[[feedback_transcendental_phase_is_loop_fact]].

## Method (mechanical, grep over `agda/Substrate/**.agda` comments)

Markers swept: `analytic`, `transcendental`, `in the limit`, `out of scope/reach`, `needs/requires ℝ`,
`real-valued`, `not constructive/representable/provable`, `can't be proved/represented`, `only …
classical / classically holds`, `deferred … (real|analytic|limit|continuous)`, `irreducibly`,
`continuous … (limit|approx)`. Plus the convertible-mislabel shape `X only holds classically / by LEM`.

## Verdict: the reflex is already PURGED — zero uncorrected mislabels.

Every hit falls into one of three classes; NONE is an uncorrected "analytic excuse for a formal fact":

| class | meaning | representative hits |
|------|---------|---------------------|
| **(a) already corrected** | the comment explicitly states it is NOT analytic / NOT "in the limit" and cites the lesson | `Algebra/R/Trace/{Cancel,Bisim,SeriesCancel,Exp,Transcendental}` (exp⊣log = a coinductive BISIMULATION, exact per order, NOT a limit); `Algebra/R/Circle` (e^{iπ}=−1 is a LOOP fact, π=½ turn rational, the antipode = `negBoth`); `Algebra/R/TranscendentalDigits` (π,i,e ARE the digit basis); `Logic/Evidence/GValueAsQ`,`GValueLSpace` (the codec is a monoid hom, NOT an analytic ln-value) |
| **(b) principled scope** | the continuum/topology is correctly *parameterised* or *reduced*, not avoided | `Category/FieldContinuum`,`S1-Lift`,`S2-Lift` (substrate formalises the discrete→continuum CONSTRUCTOR / inference rule; the continuum target is a supplied parameter); `Algebra/TopologicalGroup` (discrete ⟹ continuity collapses to the group law); `Algebra/PontryaginDual` (finite case PROVED by CRT; the continuous LCA case is the named general concept); `feedback_scoped_classical_hypotheses` instances (LEM enters only as a module parameter → P) |
| **(c) genuine deferral** | a real, heavy build — bounded by EFFORT, not impossibility; NOT an analytic mislabel | GL3F2 168-element enumeration & PSL(2,7) simplicity (`Algebra/GL3F2*`); `OR ~ log-sum-exp` lift (`Logic/Evidence/{Atlas,Verdict}`, `GValueLSpace`) = the **Ω3-L-primes** item (needs the free-abelian-on-primes "log", `ℚ₊ ≅ ⊕ℤ`) |

The convertible shape "X only holds classically / by LEM" (a formal fact hidden behind a classical
excuse) is **ABSENT** from the tree — the one place "classically" appears as a scope-claim is the
`Cancel.agda` CORRECTION that rejects it.

## Conclusion

Ω4 finds nothing left to convert: the prior arcs (Algebra.R bisimulation, Circle loop-fact,
TranscendentalDigits, GValue codec, continuous-via-discrete constructor, finite-Pontryagin-by-CRT,
discrete-topology-collapse, scoped-classical-hypotheses) already applied the lesson pervasively. The
"analytic/transcendental/impossible" reflex is purged. What remains under "out of scope" is **(c)
genuine effort-deferrals** — chiefly the **Ω3-L-primes** build (the only one that is itself a clean
formal fold, queued separately) and the GL3F2 finite enumerations/PSL simplicity (heavy, not analytic).

This report is the Ω4 artifact: the audit is DONE (sweep run, classification recorded). Re-run the
marker grep above to refresh; the genuine deferrals (c) are tracked as their own scoped items.
