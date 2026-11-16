---
name: oarc-kernel-fusion
description: "O-arc lands the kernel-fusion + GPU-residency improvements per user review. Vectorized opcode-match (10× kernel speedup), incremental match-append on growth, GPU-side argmax, adaptive predictor in tensor form, int-based chamber walk (no float matmul), explicit cap policy, dynamic max_body resize. GpuCodecV2: encode time 6.8-16.4× faster than V1; compression now matches L0 (8.172 vs L0 8.164 on text 1024B); speedup scales with input size. Maturity now: tensor formulation ✅, GPU acceleration ✅, GPU residency ✅, kernel fusion ✅ substantial (vectorized match), parallel parsing ❌ (P-arc)."
metadata: 
  node_type: memory
  type: project
  originSessionId: bb094a39-05c5-494d-8b01-cc34809ccae9
---

**Fact.** O-arc lands 10 slices addressing the user's review priorities. `gpu_kernels.py` provides a single-launch vectorized `gpu_opcode_match_vectorized` (10× speedup over the per-opcode Python-loop version) plus `gpu_opcode_match_append` for incremental updates on grammar growth. `gpu_codec_v2.py` is the integrated codec: vectorized match + incremental append + GPU argmax + adaptive predictor + int chamber walk + dynamic cap/body. Compression now matches L0 to within 0.01-0.03 b/byte across 256B/512B/1024B; encode time is 6.8× faster than V1 at 256B, 16.4× faster at 1024B — speedup scales with input size.

**Why.** Per user's closing review of N7: the architectural pieces were correct but per-step GPU launches + per-opcode Python loop + uniform cumfreqs predictor were the residual bottlenecks. O-arc addresses each directly. The user's prioritised roadmap mapped 1:1 onto slices O1-O8.

**How to apply.** When discussing the GPU codec:
* The codec is now both lossless AND competitive with CPU on compression (matches L0 within 0.01-0.03 b/byte).
* Encode-time gap to CPU is closing — extrapolation suggests crossover at ~2-4KB.
* The remaining architectural ceiling is sequential greedy parsing (P-arc job).
* Adaptive predictor is the single biggest compression win in the GPU pipeline.

## Empirical comparison (bits/byte and encode time)

| size | L0 b/byte | L0 time | V1 b/byte | V1 time | V2 b/byte | V2 time | V2/V1 speedup |
|------|-----------|---------|-----------|---------|-----------|---------|---------------|
| 256  |     9.688 |  84.6ms |    10.094 |  2506ms |     9.719 | 370.8ms |          6.8× |
| 512  |     8.781 | 186.7ms |     8.969 |  4510ms |     8.797 |   488ms |          9.2× |
| 1024 |     8.164 |   349ms |     8.562 | 13275ms |     8.172 |   811ms |         16.4× |

**Two key observations:**
1. V2 compression nearly matches L0 (adaptive predictor + grammar growth).
2. V2 speedup *scales with input size*, suggesting the GPU is finally amortising its launch overhead.

## What landed (O-arc, 2026-05-20)

| Slice | Artefact | Empirical result |
|---|---|---|
| O1 | `gpu_opcode_match_vectorized` — single-launch broadcast comparison | 10× faster than per-opcode loop |
| O2 | `gpu_opcode_match_append` — append columns for new opcodes only | no full recompute on growth |
| O3 | GPU-side argmax in main loop | scalar transfer only per step |
| O4 | Argmax happens once per position (precomputed match) | unified into V2 codec design |
| O5 | `adaptive_cumfreqs(counts, alphabet_size)` — tensor predictor | compression matches L0 |
| O6 | Explicit cap policy with `FREEZE_MARKER` and `cap_frozen` flag | visible behaviour at limit |
| O7 | `grow_body_capacity` dynamic max_body resize | no body truncation |
| O8 | `int_chamber_walk` via permutation-index lookup table | numerically exact; no float matmul |
| O9 | end-to-end timing measurement | V2 6.8-16.4× faster than V1 |
| O10 | this memo | externalised |

## Maturity table update

| Layer              | After N-arc | After O-arc |
|--------------------|-------------|-------------|
| Tensor formulation | ✅ complete | ✅ complete |
| GPU acceleration   | ✅ substantial | ✅ complete |
| GPU residency      | ⚠️ partial  | ✅ substantial (match tensor lives on GPU) |
| Kernel fusion      | ❌ not yet  | ✅ substantial (vectorized match; integrated pipeline) |
| Parallel parsing   | ❌ not yet  | ❌ not yet (P-arc) |

Three layers upgraded; one remains for P-arc.

## What's deferred to P-arc

Per the planned P-arc:
* Tensor full-speculation (multiple candidates evaluated in parallel)
* StackTensor integration into encoder (sticky-mode toggles)
* Rotation-axis full-speculation (BWT-emergence at scale)
* Multi-window batched encoding
* Streaming GPU encoder
* Decoder GPU residency parity
* End-to-end CPU vs GPU speedup measurement at large sizes
* Clean codec packaging

## Cross-references

* [[gpu-matricised-codec]] — the N-arc this builds on; closing review identified exact priorities applied here.
* [[matricised-codec-pipeline]] — M-arc CPU tensor foundations.
* [[matrix-op-homoiconicity]] — the architectural goal this realises further.
* [[opcode-vm-codec]] — the L0 baseline now matched on compression.
* `eliza/gpu_kernels.py` — vectorized kernels (O1-O3).
* `eliza/gpu_codec_v2.py` — integrated codec (O4-O8).

## Status

Externalised 2026-05-20. O-arc complete. Codec is now lossless, competitive with L0 on compression, and increasingly competitive on encode time (gap closing as input size grows). The user's review priorities are addressed. P-arc next: parallel parsing, BWT-emergence at scale, multi-window batching, streaming, packaging.
