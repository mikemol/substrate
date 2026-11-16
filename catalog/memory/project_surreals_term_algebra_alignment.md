---
name: project-surreals-term-algebra-alignment
description: "Conway's surreal numbers ({L | R} recursive definition) align very naturally with the substrate's existing term-algebra infrastructure (Coxeter Word, R-arc lambda-VM CCC, ChainSequitur); user-flagged as eventual arc."
metadata: 
  node_type: memory
  type: project
  originSessionId: 20608575-0873-42b7-b664-8addeb8207d9
---

User-noted future arc seed (2026-05-20, during Toki Pona arc): Conway's **surreal numbers** are a very natural alignment with the substrate's existing term algebra.

**The alignment**: Surreals are defined recursively as `{L | R}` where L and R are themselves sets of (already-constructed) surreals. The substrate already has multiple recursively-defined term-algebra primitives that match this shape:
- [[feedback-prefer-coxeter-backed]] — Coxeter Word: `[] | g ∷ Word`
- [[project-rarc-lambda-vm-recognition]] — opcode lambda-VM in CCC with NT references as application
- [[project-substrate-native-recursive-grammar]] — ChainSequitur recursive grammar over per-window walk chains
- [[project-opcode-vm-codec]] — the codec's runtime is a recursive term-algebra evaluator

A surreal arc could share substantial machinery: the recursive `{L | R}` constructor + the comparison / order relation + the surreal-arithmetic operations as term-algebra reductions, all sitting in the substrate's CCC + term-algebra infrastructure.

**Why it matters**: Surreals are the deepest recursive-decision-structure number system, containing ℚ, ℝ, infinitesimals, ordinals, and dyadic rationals — the universal numeric carrier in some sense. Combined with [[feedback-q-over-r-constructive]] (ℚ preferred over ℝ for decision structure), surreals offer a numeric carrier that's even richer than ℚ while still preserving the construction tree — recursion built into the carrier definition itself, matching [[project-tetrative-metacircularity]] at the numeric layer.

**How to apply**:
- When the substrate's numeric needs grow beyond F₂ and the user wants more than ℚ, surreals are the substrate-honest target.
- Eventual arc plan: surreals as recursive term algebra in the CCC, with comparison + arithmetic as opcode-style reductions.
- Connection to existing primitives: surreal `{L | R}` is structurally a Cone (apex = the surreal; legs = the L/R bounds) — see [[project-3plus1-is-cone-instance]] for the cone framework.
- Deferred per [[feedback-coalgebraic-not-consumer-driven]] — surfaces when a consumer (a richer numeric arc) forces it.

Related: [[project-continuous-limit-lift-framework]] (discrete-to-continuous topological lifts; surreals are the categorical home for that lift's destination); [[feedback-continuous-via-discrete-inference-rules]] (surreals ARE the discrete inference rules constructing continuous limits).
