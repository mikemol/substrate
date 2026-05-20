# Codec architecture flow — post-Q-arc

Post-60-slice arc (C through Q). Current production codec is **GpuCodecV2**; V3 wires speculation on top.

## Encoder dataflow

```mermaid
flowchart TB
    subgraph CPU["CPU side (control + range coder)"]
        bytes[("bytes")]
        rc["RCState<br/>(tensor: low/high/pending/buf)"]
        counts["counts: (alphabet_size,) np.int64<br/>(adaptive predictor)"]
        encoded[("encoded bytes")]
    end

    subgraph GPU["GPU side (tensor pipeline)"]
        walk["int_chamber_walk<br/>via next_chamber_table (24×16)<br/>O8 numerically exact"]
        chain[/"chain stream<br/>(N,) int64 chamber indices"/]
        opcodes[("opcode_tensor<br/>(max_opcodes, max_body)<br/>preallocated O6/O7")]
        match["gpu_opcode_match_vectorized<br/>O1: single CuPy launch<br/>(N_pos × N_opc) match-length"]
        match_t[/"match_tensor<br/>(N_pos, n_used) int64"/]
        argmax["xp.argmax(row[pos])<br/>O3 on-device"]
        spec{{"V3: speculation<br/>(StackTensor toggle)<br/>Q3+Q4"}}
        digram["digram_index dict<br/>(prev, this) → rule_id"]
        grow["try_grow_opcode<br/>+ gpu_opcode_match_append<br/>O2 incremental"]
    end

    bytes --> walk
    walk --> chain
    chain --> match
    opcodes --> match
    match --> match_t
    match_t --> argmax
    argmax --> spec
    spec -->|emit_idx| counts
    counts -->|cumfreqs via cumsum| rc
    rc --> encoded

    spec -->|digram event| digram
    digram -->|seen twice| grow
    grow -.->|append column<br/>(no full recompute)| match_t
    grow -.->|append body| opcodes

    classDef gpu fill:#e0f7fa,stroke:#00838f
    classDef cpu fill:#fff3e0,stroke:#e65100
    classDef bridge fill:#f3e5f5,stroke:#6a1b9a
    class walk,chain,opcodes,match,match_t,argmax,spec,digram,grow gpu
    class bytes,rc,counts,encoded cpu
```

## Decoder dataflow (mirror)

```mermaid
flowchart TB
    encoded[("encoded bytes")]
    rc_dec["RCDecoderState<br/>(low/high/value/pos)"]
    counts["counts<br/>(mirrors encoder)"]
    digram["digram_index<br/>(mirrors encoder)"]
    opcodes["opcode_tensor<br/>(grown in lockstep)"]
    cap["cap_frozen flag<br/>Q1: tracked dynamically<br/>(NOT from header)"]
    emit[/"emit_idx stream"/]
    unfold["expand emit_idx:<br/>chain index OR opcode body"]
    chain_term[/"chain_terminals<br/>(M,) int64"/]
    inverse["nibble_from_transition<br/>per-step inverse lookup"]
    bytes_out[("bytes")]

    encoded --> rc_dec
    rc_dec -->|searchsorted on cumfreqs| emit
    counts -->|cumfreqs| rc_dec
    emit -->|< 24| chain_term
    emit -->|>= 24| unfold
    opcodes --> unfold
    unfold --> chain_term
    emit --> digram
    digram -->|seen twice| opcodes
    cap -.->|gates growth| opcodes
    chain_term --> inverse
    inverse --> bytes_out
```

## Tensor I/O shapes (homoiconic representation)

```
chamber walk:       (N_chain,) int64                           -- O8 int lookup
opcode bodies:      (max_opcodes, max_body) int64              -- O7 dynamic
opcode lengths:     (max_opcodes,) int64
match tensor:       (N_chain, n_used) int64                    -- O1 vectorized
RC state:           (4,) uint32                                -- M1+M2
adaptive counts:    (alphabet_size,) int64                     -- O5
stack state:        (C, max_depth, 2) int8                     -- M6
speculation batch:  (C, max_steps) int64                       -- M7
```

## Sub-arc layering

```mermaid
flowchart LR
    L0["L0 adaptive opcode-VM<br/>(C-K arcs)"] --> M["M-arc: tensor primitives<br/>(CPU homoiconic)"]
    M --> N["N-arc: CuPy port<br/>cuBLAS env fix"]
    N --> O["O-arc: kernel fusion<br/>10× match speedup<br/>adaptive predictor"]
    O --> P["P-arc: BWT-at-scale<br/>+ packaging<br/>(P1,P2,P5,P6,P7 deferred)"]
    P --> Q["Q-arc: bug fix + crossover<br/>+ substrate bridge<br/>(60-slice arc closes)"]

    classDef done fill:#c8e6c9,stroke:#2e7d32
    class L0,M,N,O,P,Q done
```

## Substrate-side bridge (Q8+Q9)

```mermaid
flowchart TB
    subgraph Codec["scratch/eliza (Python runtime)"]
        py_chain["sylow_chain.py<br/>SylowChain (v, s3, s2)<br/>build_chain : S₄ → ChainSymbol"]
        py_bwt["gpu_rotation_speculation.py<br/>full-spec across 16 rotations<br/>EmergentConcentration measure"]
    end

    subgraph Substrate["agda/Substrate/Category (Agda formal)"]
        agda_sylow["SylowDecomposition<br/>(T0)"]
        agda_pfg["PrimeFactoredGauge<br/>(T1)"]
        agda_mre["MultiRouteEquivariance<br/>(T5)"]
        agda_chain["ChainDecomposition<br/>(Q8, NEW)<br/>Vec G n + reconstruct"]
        agda_bwt["BWTEmergence<br/>(Q9, NEW)<br/>RotationCommitMap<br/>+ EmergentConcentration"]
    end

    py_chain -.->|empirically instances| agda_chain
    py_bwt -.->|empirically instances| agda_bwt
    agda_sylow --> agda_pfg
    agda_pfg --> agda_mre
    agda_pfg --> agda_chain
    agda_chain --> agda_bwt

    classDef code fill:#fff9c4,stroke:#f9a825
    classDef agda fill:#e8eaf6,stroke:#3949ab
    class py_chain,py_bwt code
    class agda_sylow,agda_pfg,agda_mre,agda_chain,agda_bwt agda
```

## Module dependencies (Python side, post-Q-arc)

```mermaid
flowchart BT
    alphabets["alphabets.py<br/>(Chamber, NIBBLE_TO_PERM)"]
    manifold["manifold.py<br/>(24-chamber Cayley graph)"]
    chain_symbol["chain_symbol.py"]
    sylow_chain["sylow_chain.py"]
    walk_carrier["walk_carrier.py"]
    gauge["gauge_element.py"]
    per_nibble["per_nibble_chain.py"]
    matrix_ops["matrix_ops.py<br/>(L1-L4)"]
    tensor_rc["tensor_range_coder.py<br/>(M1-M2)"]
    tensor_grammar["tensor_grammar.py<br/>(M3-M5)"]
    tensor_spec["tensor_speculation.py<br/>(M6-M8)"]
    gpu_stages["gpu_codec_stages.py<br/>(N2-N6)"]
    gpu_kernels["gpu_kernels.py<br/>(O1-O3)"]
    opcode_set["opcode_set.py"]
    v2["gpu_codec_v2.py<br/>(O-arc + Q1 fix)"]
    v3["gpu_codec_v3.py<br/>(Q3+Q4)"]
    pipeline["gpu_codec_pipeline.py<br/>(Q5-Q7)"]
    codec_api["codec_api.py<br/>(P9)"]

    chain_symbol --> sylow_chain
    alphabets --> manifold
    manifold --> matrix_ops
    matrix_ops --> gpu_stages
    matrix_ops --> gpu_kernels
    gpu_kernels --> v2
    gpu_stages --> v2
    tensor_rc --> v2
    tensor_grammar --> v2
    opcode_set --> v2
    walk_carrier --> per_nibble
    per_nibble --> v2
    v2 --> v3
    tensor_spec --> v3
    v2 --> pipeline
    v2 --> codec_api
    sylow_chain --> chain_symbol
    gauge --> walk_carrier
```

## Performance summary (post-Q-arc)

| size | L0 b/byte | L0 time | V2 b/byte | V2 time | ratio |
|------|-----------|---------|-----------|---------|-------|
| 1024 | 8.164 | 327ms | 8.164 | 1294ms | 3.96× slower |
| 2048 | 7.723 | 981ms | 7.723 | 1720ms | 1.75× slower |
| 4096 | 7.232 | 2553ms | 7.307 | 2738ms | 1.07× slower |
| **8192** | **6.644** | **6880ms** | **6.938** | **4065ms** | **0.59× — V2 FASTER** |

V2 crosses over L0 between 4KB and 8KB. At 8KB V2 GPU is 1.7× faster than L0 CPU; compression cost 0.3 b/byte from cap-freeze at 512 opcodes (Q7 streaming sidesteps via chunking).

## Cross-references

- `[[qarc-closure]]` — Q-arc completion memo
- `[[oarc-kernel-fusion]]` — O-arc vectorisation
- `[[gpu-matricised-codec]]` — N-arc GPU port
- `[[matricised-codec-pipeline]]` — M-arc CPU primitives
- `[[opcode-vm-codec]]` — L0 baseline
- `[[substrate-primitives-index]]` — substrate's categorical-primitive registry; Q8+Q9 land here
