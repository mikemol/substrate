# Eliza — Agda skeleton

A modular structural skeleton for the eliza Python script
(`scratch/eliza/17.py` and successors), formalised as type signatures
and structural claims in Agda. Mirrors the word-based decomposition
pattern of `agda/Substrate/Groups/Coxeter/Word.agda` and the cocycle
discipline of `agda/Substrate/Cocycle.agda` and
`agda/Substrate/Discipline.agda`.

The Python script has grown past the point where it can be written or
extended in single-context bursts. The Agda skeleton's job is to name
the substructures, fix the module boundaries, and state the
inter-module contracts. The Python decomposition then materialises one
module at a time, each Python file implementing one Agda module's
contract.

## Decomposition principle

The pipeline is a chain of per-symbol transducers, each operating on a
`Word α` for an alphabet α appropriate to its layer:

```
Char ──Router──► Gen ──Manifold──► Chamber ──Orbit──► Orbit
       (gauge)        (Coxeter)            (cocycle)
       │              │                     │             │
       ▼              ▼                     ▼             ▼
   Predictor    Grammar Gen          Grammar Chamber   Grammar Orbit
   (P(c|c₁c₂))  (Sequitur 3-sym)     (Sequitur 24-sym) (Sequitur 6-sym)
                                            │
                                            ▼
                                       Holonomy + Period
                                       (BC-cell, κ-band, HasOrder)
                                            │
                                            ▼
                                         Recorder
                                       (SQLite, WAL)
```

The substrate-honest payoff is at the orbit level: gauge-equivalent
text fragments (different chars, same V₄-coset trajectory) collapse to
identical grammar rules, identical surprise, identical synthesis. This
is the substrate's Cocycle Rule 5 (content-address by invariant only)
realised at runtime in the dashboard.

## Module → Python mapping

The current Python lives in one ~1400-line file. The Agda skeleton
specifies a 13-module Python decomposition:

| Agda module          | Python module (target)         | Current 17.py lines              |
|----------------------|--------------------------------|----------------------------------|
| `Eliza.Word`         | `eliza/word.py`                | (new — currently in-line)        |
| `Eliza.Transducer`   | `eliza/transducer.py`          | (new — implicit in step methods) |
| `Eliza.Alphabets`    | `eliza/alphabets.py`           | (new — `V4_PERMS`, `V4_LABELS`)  |
| `Eliza.Router`       | `eliza/router.py`              | `char_to_generator` (~5 lines)   |
| `Eliza.Manifold`     | `eliza/manifold.py`            | `SpectralManifold` (~80 lines)   |
| `Eliza.Trajectory`   | `eliza/trajectory.py`          | `Engine.detect_period`           |
| `Eliza.Orbit`        | `eliza/orbit.py`               | `SpectralManifold._compute_v4_orbits` |
| `Eliza.Holonomy`     | `eliza/holonomy.py`            | `HolonomyEngine`, `SpectralAnalytics` |
| `Eliza.Predictor`    | `eliza/predictor.py`           | `TrigramPredictor` (~120 lines)  |
| `Eliza.Sequitur`     | `eliza/sequitur.py`            | (new — proposed for 18.py)       |
| `Eliza.Synthesis`    | `eliza/synthesis.py`           | `Engine.synthesize_branches`, `_project_branched` |
| `Eliza.Recorder`     | `eliza/recorder.py`            | `Store`, `SessionRecorder` (~250 lines) |
| `Eliza.Engine`       | `eliza/engine.py`              | `Engine` (~110 lines)            |
| (UI — out of scope)  | `eliza/ui.py`                  | `_build_app` (~400 lines)        |

After this decomposition, each Python module is short (50-150 lines)
and can be written or extended in a single context burst. The UI is
intentionally outside the Agda skeleton — it has no substrate-honest
content; it's a Textual app that consumes the engine's diagnostics.

## What the skeleton enforces

1. **Module boundaries.** Each Python module implements one Agda module's
   contract; cross-module access goes through named interfaces. No
   `Engine` shortcut that bypasses (say) `Holonomy`.

2. **Gauge-vs-invariant separation.** Per Cocycle Rule 1 and Rule 5:
   semantically meaningful outputs depend only on orbits, not on chambers
   directly. The colour-coding in 17.py is the first surfacing of this;
   the orbit-level Sequitur grammar will be the deeper one.

3. **Cocycle structure of chambers.** Per V4Signature: every chamber
   decomposes as `(orbit, fiber)` with `fiber ∈ V₄`. No code may
   ADDRESS by fiber; only by orbit. (Display is fine.)

4. **Coalgebra structure of layers.** Per `Substrate.Category.Coalgebra`:
   the chamber-walker is an Endomap; the predictor is a Coalgebra; the
   recorder is a stateful accumulator. Each commits to monotonicity /
   functoriality contracts.

5. **Period as HasOrder.** Per `FiniteOrder`: the period detector
   surfaces the local `HasOrder γ k` witness — the substrate's
   torsion-element universal at runtime.

6. **BC-cell as 2-cell.** Per `BeckChevalley`: the holonomy κ is the BC
   square's structural failure cell. `ℋ-closes` is the BC condition.

## Why this is the right decomposition

The repeatable form across every layer is `Word α` — the same cons-list
spine. The composition operation is layer-chaining via `Transducer α β`.
The entailment is that gauge-equivariance composes through the chain
(per Substrate.Discipline Rule 5).

These three together — costructure, composition, entailment — license
mechanical assembly of the whole from the parts. Per the substrate's
`decomposable-by-entailment` discipline.

## How to type-check

```bash
cd scratch/eliza/agda
agda --safe --without-K Eliza.agda
```

(Requires Agda 2.6.4+; no external libraries needed — the skeleton is
self-contained via `Eliza.Prelude`.)

## Cross-references

- `agda/Substrate/Cocycle.agda` — IsomorphicCocycleStructure pattern.
- `agda/Substrate/Cocycles/V4Signature.agda` — V₄-orbit/fiber cocycle.
- `agda/Substrate/Groups/Coxeter/Word.agda` — Word α reference.
- `agda/Substrate/Category/BeckChevalley.agda` — BC-square / 2-cell.
- `agda/Substrate/Category/Coalgebra/FiniteOrder.agda` — HasOrder.
- `agda/Substrate/Discipline.agda` — Rules 1, 5, 11 of clarified
  foundation.
- `scratch/eliza/17.py` — the current monolithic Python.
- `scratch/eliza/readme-{2,4}.md` — the readmes whose framework this
  skeleton mechanises.

## Status

Skeleton: complete (13 modules + top-level Eliza.agda).
Python decomposition: not yet started; 17.py is the source.
Type-checking: not verified end-to-end (postulates are unproved; the
structural commitments are the deliverable).
