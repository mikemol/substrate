---
name: sarc-active-speculation
description: "S-arc activates control-opcode emission via speculation. V5 codec emits S_DEFER_GROW when a simple heuristic predicts growth is harmful. Round-trips lossless. Empirically: V5 1024B 8.227 b/byte vs V4 8.195 (defer emissions don't save bits with this heuristic). Consistent with I-arc finding: automatic-rewrite is default-optimal on typical inputs. Architecture-wise the active-speculation primitive is wired; the heuristic refinement is future work."
metadata: 
  node_type: memory
  type: project
  originSessionId: bb094a39-05c5-494d-8b01-cc34809ccae9
---

**Fact.** S-arc lands the active-speculation primitive. `gpu_codec_v5.py` emits `S_DEFER_GROW` control opcodes when a body-length heuristic predicts growing the current digram is harmful. Round-trips lossless at 1KB-4KB. Empirically the defers cost more than they save on tested inputs (V5 1024B 8.227 b/byte vs V4 8.195), consistent with the I-arc finding that automatic-rewrite is default-optimal on standard corpora.

**Why.** Per R-arc recognition, V4 has the control opcodes in alphabet but never emits them. S-arc tests whether ACTIVE emission via speculation can buy bits. The substrate-honest finding: a simple body-length heuristic doesn't, and matches the I-arc pattern. Better heuristics (e.g., true K-step lookahead with cost evaluation under both paths) might find wins; not pursued here.

**How to apply.** When discussing the V5 codec:
* It's architecturally complete: control opcodes are EMITTED, not just reserved in alphabet.
* Active speculation requires a smart heuristic; the body-length heuristic isn't smart enough on typical inputs.
* Per the H/I/J/K-arc series: this is the same pattern. Per-emission control overhead exceeds the savings of selective deferral on standard text.
* The architecture remains AVAILABLE for inputs / policies where speculation does win (e.g., degenerate inputs, future smarter heuristics, downstream cross-codec exchange).

## What landed (S-arc, 2026-05-20)

| Slice | Artefact | Result |
|---|---|---|
| S1-S6 | `gpu_codec_v5.py` | encoder emits `S_DEFER_GROW` via `_should_defer_grow` heuristic |
| S7 | round-trip at 1KB-4KB | lossless |
| S8 | V2 vs V4 vs V5 comparison | V5 ≈ V4 ≈ V2 within 0.03-0.06 b/byte |
| S9 | burstiness probe | V5 doesn't fire defers on bursty input; same compression as V2 |
| S10 | this memo | externalised |

## Empirical numbers

| size | V2 b/byte | V4 b/byte | V5 b/byte | V5 defers |
|------|-----------|-----------|-----------|-----------|
| 1024 | 8.164     | 8.195     | 8.227     | 3         |
| 2048 | 7.723     | 7.746     | 7.746     | 0         |
| 4096 | 7.307     | 7.316     | 7.316     | 0         |

Bursty input (zeros+text alternating, 1024B):
* V2: 4.711 b/byte
* V5: 4.742 b/byte (0 defers — heuristic missed potential wins)

## Substrate-honest reading

This matches the H/I/J/K-arc pattern:
* H-arc: per-emission flag → +20-27% overhead (always pays)
* I-arc: flip-opcode → matches L0 (zero overhead when default-optimal)
* J-arc: stack-machine + K-step beam → mis-toggles (-15-50%)
* K-arc: full-speculation → matches L0 exactly (0 toggles on real inputs)
* **S-arc: active heuristic emission → matches V4 within 0.03 b/byte (defers don't save)**

Each speculation arc confirms: automatic-rewrite is default-optimal on typical inputs. The architectural ability to EMIT control opcodes is now in place at V5; finding inputs where active emission wins remains future work.

## Cross-references

* [[rarc-lambda-vm-recognition]] — R-arc named the control opcodes; S-arc emits them.
* [[full-speculation-codec]] — K-arc full-spec; same pattern, different mechanism.
* [[flip-opcode-speculation]] — I-arc same finding via different primitive.
* [[opcode-vm-codec]] — L0 baseline.
* `eliza/gpu_codec_v5.py` — V5 codec.

## Status

Externalised 2026-05-20. S-arc complete. V5 actively speculates over control-opcode emission; round-trips lossless; compression matches V4 within 0.03 b/byte. Substrate-honest: automatic-rewrite is default-optimal; active emission primitive is wired and ready for smarter heuristics or non-standard inputs.
