---
name: matrix-op-homoiconicity
description: "Codec architecture as homoiconic tensor representation: every stage (chamber walk, opcode match, isotypic projection, adaptive grammar, speculation, arithmetic coding) expressed as the same kind of tensor object, enabling end-to-end GPU pipeline with no Python control flow between stages. The roofline-driven 'port the slow stages' framing is WRONG — speedup comes from architectural homoiconicity, not bottleneck-hunting. The coalgebra IS the work (per [[coalgebraic-not-consumer-driven]]). Foundations landed (chamber walk, opcode match, isotypic projection as matrix tensors); range coder + adaptive grammar + speculation remain non-matricised; GPU env (cuBLAS loading on CUDA 13 + Python 3.14) deferred."
metadata: 
  node_type: memory
  type: project
  originSessionId: bb094a39-05c5-494d-8b01-cc34809ccae9
---

**Fact.** scratch/eliza's `matrix_ops.py` and `gpu_matrix_ops.py` re-express three codec stages as matrix-op tensors: (1) chamber walk via 16 × 24 × 24 nibble permutation matrices applied by matrix-vector product; (2) opcode match via (N_position × N_opcode) tensor of comparisons with sliding-window broadcast; (3) S₄ isotypic projection via 5 × 24 × 24 projector tensor. CPU validation passes (correctness vs sequential reference). GPU port stubbed but blocked by cuBLAS-loading issue on the CUDA 13 + Python 3.14 environment.

**Why.** User correction to the roofline framing: *"Wrong framing. It's about architectural homoiconicity. I have in mind ways to make the system incredibly fast, but they rely on being able to do everything on-GPU one way or another. Remember: The coalgebra is the work."* The previous L-arc thinking (port bottlenecks) was consumer-driven optimisation. The substrate-honest framing is: make the architecture uniformly matricisable so it can run as a fused tensor pipeline.

**How to apply.** When discussing codec performance: don't ask "which stage to GPU-port" (consumer-driven). Ask "which stages are not yet expressed as tensor ops, blocking pipeline fusion." The architectural goal is homoiconicity — everything as the same kind of object — and that's what enables the bigger speedups (no CPU↔GPU transfers, fully fused GPU dataflow, batched speculation across rotations × paths × steps).

## What "homoiconic matrix-op" means concretely

Each codec stage's state and step are tensor objects of uniform shape conventions:

| Stage | State (tensor) | Step (tensor op) |
|---|---|---|
| Chamber walk | chamber distribution (24,) or batch (B, 24) | matrix-vector M @ state |
| Opcode match | match-length tensor (N_pos, N_opc) | broadcast comparison + reduction |
| Adaptive grammar | opcode body matrix (N_opc, max_body) | tensor concat to grow |
| Spectral projection | spectral coords (5, 24) | 5×24×24 projector @ chamber |
| Speculation | (C candidates, N positions) costs | parallel encode-simulate |
| Range coder | (low, high, range) state | linear map; chunked state-update |
| Arithmetic emission | (alphabet, cumfreqs) tensor | cumulative sum + lookup |

When all stages are tensor ops of uniform shape, the pipeline becomes:

```
bytes → nibbles → walk-tensor → chamber-indices →
opcode-match-tensor → vm-emission-tensor → AC-state-tensor → encoded-bits
```

— each arrow a tensor op composable into a single GPU kernel chain.

## What landed (10 L-slices, 2026-05-20)

| Slice | Artefact | Gate |
|---|---|---|
| L1 | `nibble_to_perm_matrix()` returns (16, 24, 24) | walk via matrix-vector matches `perm_compose` reference |
| L2 | `walk_to_chamber_indices()` batched form | per-position chamber indices via matrix product |
| L3 | `longest_opcode_at_each_position()` tensor op | 5.9-9.9× faster than Python per-position loop |
| L4 | `isotypic_projector_tensor()` returns (5, 24, 24) | Σ projectors @ e_i = e_i (decomposition holds) |
| L5-L7 | GPU stubs with CuPy | cuBLAS-loading issue on CUDA 13 + Python 3.14; deferred |
| L8 | roofline analysis | **MISGUIDED FRAMING** — corrected by user |
| L9 | side-by-side codec | not done; GPU env blocked + framing corrected |
| L10 | this memo | externalised with correct framing |

## Roofline results (kept as-is, with corrected interpretation)

The roofline timing showed:
* Matrix chamber walk is SLOWER than Python on CPU (0.16-0.24× ratio) due to numpy overhead on tiny 24-dim ops.
* Tensor opcode match is 5.9-9.9× FASTER than per-position Python loop.
* Full-spec speculation dominates everything (9 sec on 256B).

**Reading under the corrected framing:**

The Python-fast chamber walk DOES NOT mean "don't port to GPU." It means the per-stage CPU-only comparison is the WRONG benchmark. The win isn't "this one stage is faster on GPU"; it's "the whole pipeline is GPU-resident with no Python control flow between stages." Even a stage that's slightly slower on GPU contributes to the overall pipeline win by avoiding transfers and enabling fusion.

The tensor opcode match's 6-10× CPU speedup is real but UNDERSELLS the gain. On GPU with all-stages-on-GPU, the win compounds because the chain stream stays GPU-resident from creation through opcode matching through emission encoding.

## What needs to happen for the architectural vision

1. **Fix cuBLAS loading** in the venv. CUDA 13 + Python 3.14 has known integration issues; either downgrade Python or work with a different CUDA/CuPy combo.
2. **Matricise the remaining stages** — range coder state, adaptive grammar (opcode growth as tensor concat), speculation (batched tensor over candidates × positions).
3. **Eliminate Python control flow between stages** — codec becomes a single tensor pipeline; control structures like "if best_opcode is None" become tensor masks.
4. **End-to-end GPU encoding** — full codec round-trip without CPU↔GPU transfers.

## The substrate connection

Per [[coalgebraic-not-consumer-driven]]: the coalgebra IS the work, not optional polish. The matrix-op formulation isn't speed optimisation OF the codec — it's the codec's coalgebraic representation. Building it serves the substrate's structural unfolding, not a downstream consumer's runtime budget.

Per [[homology-cohomology-recursion]]: the matrix-op tensors are the catalogued (cohomology) form of the observed (homology) per-position operations. The codec's homoiconic representation makes the homology/cohomology mapping uniform — every codec step is the same kind of object.

Per [[tetrative-metacircularity]]: the codec's tetrative-axis arcs (speculation, flip-opcode, stack-machine, full-speculation) become more meaningfully composable when each axis is a tensor dimension instead of a Python control-flow split. Tetrative climb in tensor space is multidimensional indexing.

## Cross-references

* [[opcode-vm-codec]] — the codec being matricised.
* [[full-speculation-codec]] — the current speculation policy; tensor speculation would batch across candidates.
* [[stack-machine-codec]] — would map to a stack-tensor with toggle = state-vector update.
* [[coalgebraic-not-consumer-driven]] — discipline corrected here: homoiconicity is the work, not optimisation.
* [[expose-generator-not-orbit]] — the generators (16 nibble perms, 5 isotypic projectors, opcodes) are tensor parameters; the orbits are tensor states.
* `eliza/matrix_ops.py` — CPU implementations of stages 1-3.
* `eliza/gpu_matrix_ops.py` — stubs for GPU implementations.
* `eliza/gpu_codec_kernel.py` — existing CUDA RawKernel for the arithmetic coder.

## Status

Externalised 2026-05-20 with the user's framing correction applied. Three codec stages (chamber walk, opcode match, isotypic projection) are now expressed as tensor operations on CPU; GPU port is environment-blocked. The architectural goal of matrix-op homoiconicity is articulated but not realised — remaining stages (range coder, adaptive grammar, speculation) need matricisation, and Python control flow between stages needs to be eliminated, to achieve the user's "incredibly fast" vision via uniform GPU-resident pipeline.

The misguided L8 roofline framing is preserved here as a substrate-honest record of the correction: the per-stage-bottleneck optimisation framing is the wrong frame for the substrate's architecture. The right frame is whole-system tensor representation enabling fused execution.
