---
name: feedback_validate_outputs_not_inputs
description: "measuring your INPUTS rigorously does NOT validate your model's OUTPUTS — a model with clean inputs + internal consistency can still predict wrong; ground-truth the OUTPUT independently"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: c1329ff9-896f-4600-8952-67ec237e5bbc
---

Measuring your INPUTS rigorously (constants, rates, structural facts, BW, clock) does NOT validate
your model's OUTPUTS (its predictions). A model can have perfectly-measured inputs, clean internal
consistency, and every view agreeing with every other view — and still make WRONG predictions,
because the error lives in the derivation/assumptions, not the inputs. Validate the OUTPUT against an
INDEPENDENT ground-truth measurement (a measured OUTCOME, not derived from the model).

Recurrences (kernel-perf nedge arc, 2026-06-14):
- het-dispatch: branch rates were measured rigorously (inputs), but the "CPU-favored at low intensity"
  PREDICTION was unvalidated and WRONG — it used the sgemm rate constant, which doesn't apply to a
  memory-bound elementwise kernel. Ground truth (a real concurrent run) corrected it.
- "clock cancels in the ratio": clock and BW were measured (inputs), but the ridge-invariant
  PREDICTION was FALSIFIED by the power-arms experiment — there are TWO clock domains (core vs
  uncore), so the ridge is power-dependent. Only meeting reality exposed it.
- the whole engine was internally consistent (inputs + views agreed) but its predictions weren't
  ground-truthed until a deliberate independent check (engine_validate).

**Why:** measuring inputs FEELS like rigor and gives false confidence in the derived outputs;
internal consistency is not validation. This is the retrospective's G8 (the cross-pass blind spot)
as a standing rule: every pass that checks the model against itself shares the model's blind spots.

**How to apply:** for any predictive model, build a ground-truth witness that measures the OUTCOME
independently (not the inputs) and checks the prediction against it — like het_validate / engine_validate
/ power_arms. The independent signal must NOT be derived from the model. And beware: the ground-truth
signal ITSELF can be confounded (core-scaling was contaminated by the P/E-heterogeneity breaker) —
if a validation fails, check whether the model OR the ground-truth signal is the broken one, and
dissolve the signal's own opacity (cf [[feedback_hunt_opacity_after_green]]). Output-side twin of
hunt-opacity (input-side); same overclaim family as [[feedback_governing_law_before_special_case]],
[[feedback_negative_findings_in_corpus]], [[feedback_test_the_wall_before_declaring_it]].

**INVERTED COROLLARY (jea_pysim similarity arc, 2026-06-17):** the INPUT you treat as ground-truth is
itself a LOWER LAYER'S OUTPUT — audit it when a derived signal fails. The similarity metric (jea_pysim,
readout layer) wouldn't discriminate; I twice retuned the READOUT (denominator, then LCP) — but the
actual bug was in the INTERNER (jea_pyalg, the layer below I treated as ground-truth): it role-quotiented
distinct free globals (Fraction/GR) to one node, ERASING the carrier before the readout ever saw it. The
fix was in the assumed-correct input layer (free/bound split), not the derivation. **Rule:** when a readout
won't discriminate, AUDIT THE LAYER IT READS FROM, don't just retune the readout — a layered tool's
"ground-truth" forest is an output too. And: ground a new computation in the EXISTING primitives first
(the typehole tree WAS the similarity profile; I reinvented a metric instead of folding over it) — read,
don't reinvent.
