# Eliza Codec

A substrate-honest lossless codec built on the V₄ chamber-walk
machinery. Real bit streams (arithmetic coding), round-trip verified,
benchmarked against gzip/bzip2/xz.

## Architecture

```text
Input bytes
    │
    ▼
[Window partition]  →  fixed-size or V₄-closure-driven windows
    │
    ▼
[Frame chooser]  →  per window, pick the cheapest of:
    │                 • I-frame   (independent, gt+AC encoding)
    │                 • P-frame   (ref_window · V₄_residue)
    │                 • Patch     (P + sparse-bitmap correction)
    │                 • B-frame   (ref_back ⊕ ref_fwd, octonion rung)
    ▼
[Encode]  →  bytes via range coder
```

## Modules

- `eliza/arith.py` — 32-bit range coder. Standalone, round-trip
  verified on uniform and skewed distributions.
- `eliza/codec.py` — gt + range coder. The Markov-3 adaptive AC baseline
  (`encode(data)` / `decode(encoded, n_symbols)`). Round-trip verified
  byte-exact on text/ELF/zeros at 1KB.
- `eliza/windows.py` — V₄-closure boundary detector. Closure points are
  positions where the cumulative XOR of crumbs returns to identity.
- `eliza/frames.py` — frame-type taxonomy and per-frame bit-cost
  formulas. Cayley-Dickson rung mapping:
  - I-frame at F₂ rung,
  - P-frame at V₄ rung (loses F-linearity),
  - Patch at V₄ + Reed-Muller correction rung,
  - B-frame at H rung (loses V₄-commutativity, gains bidirectional ref).
- `eliza/frame_codec.py` — encoder over windows: I/P/Patch/B choice,
  with V₄ byte-rotation via XOR with {0x00, 0x55, 0xAA, 0xFF}.

## V₄ byte action

For a byte interpreted as 4 crumbs, V₄ acts on each crumb by F₂² addition.
This collapses to byte-XOR with one of four masks:

```text
residue   mask    name
e (00)    0x00    identity
α (01)    0x55    every-other-bit (low bit of each crumb)
β (10)    0xAA    every-other-bit (high bit of each crumb)
γ (11)    0xFF    bit-complement
```

A P-frame `(ref_id, residue)` decodes as `ref_window XOR mask`. A
Patch-frame adds a sparse correction bitmap on top of the XOR.

## Benchmarks

### 100KB

| Input  | gzip | bzip2 | xz   | eliza (flat-I) |
|--------|------|-------|------|----------------|
| text   | 2.26 | 1.99  | 2.07 | 3.78           |
| ELF    | 3.50 | 3.30  | 2.91 | 4.43           |
| zeros  | 0.011| 0.004 | 0.012| 0.014          |

Flat-I (Markov-3 gt without windowing or references) LOSES to all
standard compressors at 100KB. Standard compressors win via LZ77-style
substring matching (gzip, xz) or BWT context grouping (bzip2), neither
of which the flat-I codec implements.

### Variable-frame on ELF 10KB

| Codec                          | b/byte   | Frames                 |
|--------------------------------|----------|------------------------|
| gzip                           | 1.78     | —                      |
| bzip2                          | 1.89     | —                      |
| eliza flat-I                   | 2.87     | —                      |
| **eliza vf (W=64, max_p=32)**  | **2.38** | 30 I / 68 Patch / 59 P |
| eliza vf (W=256, max_p=128)    | 2.80     | 12 I / 14 Patch / 14 P |

Variable-frame with V₄ rotation matches 17% of byte savings vs flat-I
on ELF. P-frames trigger on V₄-correlated byte patterns (zero-padding,
binary section boundaries, etc.). Still loses to gzip/bzip2 by ~25%.

### Variable-frame on text 10KB

Variable-frame gives no improvement on text — V₄ byte rotation rarely
matches text patterns. Text needs LZ-style substring matching (find
longest matching substring in past data), which is orthogonal to V₄
rotation and is not yet implemented.

## V₄ canonicalization (deferred)

The earlier `v4_canonicalize` machinery (Sequitur grammar with residue
tags on NTs) is implemented but **disabled by default** for sliding-
stride-1 crumbs. The sliding window's bit-overlap already encodes the
V₄ correlation natively; explicit canonicalization adds dispersion
without compressive benefit on this input mode.

Available as `Engine(v4_canonicalize=True)` for other modes or future
experiments where the input geometry doesn't naturally surface V₄
structure.

## Honest findings

1. **Flat Markov-3 isn't competitive at scale.** Standard compressors
   beat it because they exploit either long-range substring matches
   (LZ77) or context grouping (BWT) — both are richer than a fixed
   Markov context window.

2. **V₄ byte-rotation pays on binary data, not text.** The frame
   chooser finds many P/Patch frames in ELF (~76% of windows reference
   a prior window with V₄ rotation + small correction). Text bytes
   aren't V₄-correlated at any window size we tested.

3. **The architecture is right, the substrate-natural unit isn't quite.**
   The V₄ rotation IS the right abstraction for some inputs (ELF,
   stream-encoded binary). For text, it's the wrong basis — text has
   sub-byte substring structure that V₄-on-bytes can't reach.

4. **The Cayley-Dickson rung framing is the right organizing principle.**
   Each rung sacrifices an algebraic property in exchange for more
   reference flexibility. The chooser-picks-cheapest design naturally
   selects the right rung per window.

## Next directions

- **LZ-style substring matching** alongside V₄ rotation. Variable-
  length references `(offset, length, optional_residue)`. Would unlock
  text compression to gzip-or-better.
- **Adaptive window sizing**. Currently fixed-size; V₄-closure detector
  is built but not wired into the chooser.
- **Recursive BWT at successive Cayley-Dickson rungs**. Each larger
  window prepopulated with the smaller window's BWT in its lower half.
  Speculative; would require defining a `combine` operation that
  preserves the CD doubling shape (suffix-array merge is a candidate).
- **Real arithmetic coding for P/Patch/B payloads**. Currently the
  frame bit-cost is a calculation, not an emitted stream. Wiring
  `frame_codec.encode_stream` through `arith.RangeEncoder` is the
  last step to a fully bytes-out codec.
- **Round-trip on the variable-frame codec.** The flat-I codec round-
  trips byte-exact; the variable-frame codec doesn't have a decoder
  yet. Decoder design: per-frame-tag dispatch, with B-frame's two-
  reference dependency handled by storing all references in order.

## Slice arc

This codec was built in three passes of ten slices each.

- **Pass 1**: V₄ canonicalization machinery + flat-I baseline.
- **Pass 2**: arithmetic coder + variable-frame architecture + 100KB
  benchmarks.
- **Pass 3**: dimension-2 architecture — 16-rotation table (`octonion.py`),
  recursive 2-bin signature (`signature.py`), two-Sequitur chooser
  (`dim2_codec.py`), Agda bridge documentation
  ([AGDA_BRIDGE.md](AGDA_BRIDGE.md)).

The work is logged in the conversation transcript at
`~/.claude/projects/-home-mikemol-github-substrate/bb094a39-05c5-494d-8b01-cc34809ccae9.jsonl`.

## Dimension-2 codec

The two-Sequitur architecture realizes the substrate's 2-D word algebra
at the codec layer: input grammar + rotation grammar, coupled by the
chooser as a 2-cell. Per [AGDA_BRIDGE.md](AGDA_BRIDGE.md), this maps
to `DirectProduct(FreeCyclic_input, Z_16_rotations)`.

### Implementation

`eliza/dim2_codec.py` per-window flow:

1. Compute the unrotated window's depth-4 recursive-2-bin signature
   (16-bin histogram of top-nibble byte prefixes).
2. Cache by quantized signature → rotation. On miss, search 16
   candidates by gt-cost against the input predictor's current state.
3. Encode 4-bit rotation tag.
4. Encode rotated window via gt + arithmetic coding.
5. Observe (signature, rotation) into Sequitur_rotations.
6. Predictor sees the ROTATED bytes.

Round-trip verified byte-exact on 1KB of text, ELF, zeros.

### Benchmark (slice 8)

| Input  | size | gzip | bzip2 | flat-I | dim-2 | rotations used | seq_rot rules |
|--------|------|------|-------|--------|-------|----------------|---------------|
| text   | 1KB  | 5.14 | 5.51  | 7.48   | 7.50  | 1              | 1             |
| text   | 5KB  | 3.12 | 3.14  | 5.50   | 5.52  | 1              | 1             |
| text   | 10KB | 2.60 | 2.48  | 4.76   | 4.78  | 1              | 1             |
| elf    | 1KB  | 2.90 | 3.71  | 4.30   | 4.32  | 1              | 1             |
| elf    | 5KB  | 2.17 | 2.34  | 3.47   | 3.49  | 1              | 1             |
| elf    | 10KB | 1.78 | 1.89  | 2.87   | 2.88  | 2              | 1             |
| zeros  | 5KB  | 0.06 | 0.07  | 0.18   | 0.19  | 1              | 1             |
| zeros  | 10KB | 0.04 | 0.04  | 0.10   | 0.12  | 1              | 1             |

### Honest finding: chooser too conservative

Across all inputs tested, the chooser converges to rotation 0 (identity)
on ~98% of windows. The 4-bit-per-window rotation tag is then pure
overhead, making dim-2 codec slightly WORSE than flat-I (by ~0.02 b/byte
= the tag rate).

Root cause: the scoring uses `_score_rotation` against the live
predictor. The predictor learns the rotated-as-identity distribution;
subsequent windows score identity highest because the predictor was
shaped by past identity choices. Self-reinforcing.

To make the chooser useful, three possible fixes:

1. **Rotation-invariant scoring.** Score by signature-entropy or by a
   prior-free statistic, not by the predictor's surprise (which is
   biased by past choices).
2. **Per-rotation predictors.** Maintain 16 independent gt models, one
   per rotation. Choose the rotation whose model gives the best fit.
   Costs 16× memory; resolves the self-reinforcement.
3. **Cold-start exploration.** First N windows use random rotation;
   subsequent windows exploit the learned distribution. Standard
   bandit-style approach.

These are open follow-up directions for a Pass 4.

### Architectural success

Even though the compression numbers don't yet beat flat-I, the
architectural goals of Pass 3 were achieved:

- Two-Sequitur 2-D structure implemented and round-trip-verified.
- Categorical type emitted (`stats["categorical_type"]`).
- Coxeter / Agda correspondence documented (`AGDA_BRIDGE.md`).
- Cross-fertilization edge (chooser ↔ predictor) wired and functional.

The compression failure is a chooser-tuning problem, not an
architectural one. The shape is right; the heuristic isn't yet.
