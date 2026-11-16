---
name: codec-as-pfg-witness
description: "The scratch/eliza codec is the substrate's third runtime-bearing PrimeFactoredGauge instance (alongside AtlasCatalogue's GL(3,F₂) and HodgeDim4 GaugeTorsor), at S₄ = V₄ ⋊ S₃ ≅ Z₂² ⋊ Z₃. Chambers ARE the workspace (W) axis; rotation IS the workspace operation. The atlas decomposes the gauge element via Sylow-chain (per MultiRouteEquivariance.agda), NOT a scalar combiner — the prior Bezout-of-scalars framing was RETRACTED (see retraction note)."
metadata: 
  node_type: memory
  type: project
  originSessionId: bb094a39-05c5-494d-8b01-cc34809ccae9
---

**Fact.** scratch/eliza's `eliza/walk_carrier.py` + `gauge_element.py` + `sylow_chain.py` + `chain_chooser.py` realise a runtime-bearing PrimeFactoredGauge at S₄. The carrier is the workspace state (chamber walk's end-S₄-element); the gauge element extractor returns `g = ref · walk_r⁻¹`; the Sylow chain decomposes g via V₄ ⋊ S₃ uniquely; the chain chooser picks rotation by chain-norm. All 24 chains round-trip; all 576 gauge-element existence cases pass; chain decomposition is unique by construction.

**Why.** The T0-T8 arc plan ([[prime-factored-gauge-arc]]) names PrimeFactoredGauge as the unifying costructure and queues three instance retrofits: GL(3,F₂) (smallest, formal, landed via AtlasCatalogue.agda), HodgeDim4 (original site, formal, landed via GaugeTorsor + named orbit points), and Monster (largest, conjectural). The codec is a fourth instance — and the **first runtime-bearing one with empirical measurement gates**. The chain decomposition output matches `Substrate.Category.PrimeFactoredGauge.MultiRouteEquivariance::multi-route-equivariance`'s signature: `(x, y) → (g, sylow-chain g)`, where the chain witnesses `InGenerated(⋃ Sylow)`.

**How to apply.** When discussing the codec as a PrimeFactoredGauge instance, the substrate-honest output is the Sylow chain, NOT a scalar score. When citing the W-axis: chambers are workspace cells, rotation is the workspace operation, the chain IS the equivariance-transmitting carrier-level decomposition.

## Retraction note (2026-05-20)

The prior version of this memo claimed a Bezout-of-scalars combiner `multi_chart_join` as the codec's PFG composition. That framing was **structurally wrong**: it collapsed two per-Sylow chart scores into a single S₄-invariant scalar, which is rotation-blind by construction (different rotations produce statistically equivalent walks ⇒ identical joint-score in the asymptote). The substrate template (`MultiRouteEquivariance.agda`) wants the **chain itself**, not a scalar projection.

**Retracted artefacts:**
- `eliza/atlas_join.py` — DELETED
- `eliza/spectral_window_tagger.py` — DELETED (dominance-magnitude tag was Bezout-residue)
- `eliza/spectral_atlas.py` — DELETED (chart_score and ChartScorer were Bezout-targets)
- old `tests/test_galois_adjunction.py` — REPLACED with chain-level version
- old `tests/test_compressibility_peer.py` — REPLACED with chain-chooser version

**Preserved artefact:** `eliza/spectral_characters.py` remains as background-diagnostic isotypic partition (S₄ irrep blocks), but no longer wired as an oracle. Eigenspace structure documents the algebra; chain decomposition extracts the substrate-honest gauge content.

The retraction was triggered by the user's correction:
1. *"The 24 bins are not supposed to be ignorant to rotation. They are, in fact, supposed to be derived from rotation."* — pointing at the W axis from `cotype-free-self-extending-grammar.md` § M27.
2. *"We're supposed to chain charts to transmit equivariance over nontrivial carrier."* — pointing at `MetricGauge.agda`'s `congruence-act-4` and `MultiRouteEquivariance.agda`'s chain witness.

## The W-axis reading (M27 of cotype-free-self-extending-grammar.md)

> "That fourth axis is your 'scratch' axis that lets you play Freecell while you rotate your problem space and trade between data, compute and space without losing coherence."

- The 24 chambers = workspace cells.
- Rotation r ∈ 0..15 = workspace allocation operation.
- A walk through chambers = workspace usage trace.
- The walk's end-S₄-element = workspace state after the trace.
- Chain decomposition = substrate-honest gauge content extracted from the workspace state.

Per M8 (cocycle invariance): coherence is invariant under workspace usage. Per M27: realizability depends on workspace allocation. The Bezout collapse read only the coherence coordinate; the chain reads the realizability coordinate.

## What landed (chain redesign, 2026-05-20)

| Slice | Artefact | Gate |
|---|---|---|
| C1 | `eliza/walk_carrier.py` | WalkCarrier identity + fold + walk-to-S₄ folding |
| C2 | `eliza/gauge_element.py` | `act(g, x) = y` for all 576 (x, y) pairs |
| C3 | `sylow_chain.py::semidirect_decompose` | unique V₄ ⋊ S₃ section, all 24 round-trip |
| C4 | `sylow_chain.py::build_chain` | every g ∈ S₄ gets a chain (24/24) |
| C5 | `sylow_chain.py::ChainEquivarianceWitness` | algebraic: round-trip 0/24, coverage 24/24, unique 24/24, word-length dist {0:1, 1:4, 2:7, 3:7, 4:4, 5:1} |
| C6 | `eliza/chain_chooser.py::ChainNormChooser` + Adaptive variant | argmin consistency; 3 distinct norms on text input |
| C7 | DELETE retracted artefacts | clean removal; spectral_characters.py preserved as diagnostic |
| C8 | `tests/test_galois_adjunction.py` (chain) | **per-component agreement** decomposes rotation-level delta into V₄ / Sylow-3 / Sylow-2 contributions (e.g. 53%/47%/68% on a mixed corpus) |
| C9 | `tests/test_compressibility_peer.py` (chain) | gt 5.85 b/byte; chain-static 6.95 b/byte (+18.9%); chain-adaptive 6.93 b/byte (+18.6%); rotation entropy chain 3.0-3.2 vs gt 1.58 |
| C10 | this memo + W-axis externalisation | retraction documented; cross-links to MultiRouteEquivariance, MetricGauge, M27 |

## The diagnostic value of the chain-level report

The chain decomposition exposes a strictly more informative signal than the scalar combiner:

* **Per-Sylow agreement breakdown**: rotation-level 21% / V₄ 53% / Sylow-3 47% / S₃-Sylow-2 68% on engine.py mixed corpus.
* **Chain-shape distributions**: gt's chain lengths spread {0:1, 1:8, 2:6, 3:3, 4:1}; chain chooser concentrates at {0:12, 1:7}. gt samples Sylow-3 uniformly; chain chooser commits to Sylow-3-identity.
* **Sylow-3 distribution split**: gt {(e):8, (123):7, (132):4}; chain {(e):18, (123):1, (132):0} — gt explores Sylow-3 space; chain commits to the Sylow-3 identity coset.

These are substrate-honest measurements of the Galois adjunction's non-trivial component at the chain level — strictly finer than the prior scalar Δ-rate.

## Workspace-axis is the load-bearing reading

Per the M27 framing: gauge freedom IS the W-axis. Per MultiRouteEquivariance.agda's T5: the chain IS the atlas-of-charts decomposition. Per MetricGauge.agda's `congruence-act-4`: charts chain over a nontrivial carrier (the symmetric form there; the S₄ workspace state here). Per the codec instance:

* x = walk under candidate rotation r (workspace state at end of trace)
* y = reference (canonical workspace state)
* g = gauge element connecting them
* Sylow chain = (v ∈ V₄, s3 ∈ Sylow-3, s2 ∈ {e, (12)})
* chooser = picks r minimising chain norm

This is the substrate-honest realisation. The prior Bezout-of-scalars framing read only the coherence-coordinate (S₄-invariant residue); the chain reads the full W-axis structure.

## Cross-references

* [[prime-factored-gauge-arc]] — the unifying primitive; runtime-bearing third instance.
* [[multi-route-equivariance-recovery]] — atlas-of-charts reframing; GL(3,F₂) substrate-side template (`AtlasCatalogue.agda`).
* `Substrate.Category.PrimeFactoredGauge.MultiRouteEquivariance` — T5 theorem signature this codec mirrors.
* `Substrate.Algebra.F2.HodgeDim4.MetricGauge` — the carrier-chain template (`congruence-act-4` on `SymBilinForm-4`).
* `cotype-free-self-extending-grammar.md` § M27 (lines 2868-2942) — the W-axis reading.
* [[choice-rigidification-in-substrate]] — the discipline corrected here; gt is a peer, not an oracle.
* [[coalgebraic-not-consumer-driven]] — chain correctness is algebraic-from-its-own-structure.
* [[expose-generator-not-orbit]] — Sylow generators are the exposing axis; chain word is the orbit-element-enumeration *with explicit generators*.

## Status

Retraction externalised 2026-05-20. The Bezout claim is retired; the chain decomposition is the substrate-honest output. All 10 C-slices passed their gates. The codec is the runtime-bearing third leg of the T0-T8 arc, mirroring the T5 chain decomposition with measurable per-Sylow components.
