---
name: y-arc-substrate-atlas
description: "Y-arc applies V7 to substrate-internal corpora; honest finding — gzip/lzma beat V7 by 2-3× on substrate text and even on pure opcode data; V7's structural advantage on hand-crafted patterns doesn't generalise to natural text compression"
metadata: 
  node_type: memory
  type: project
  originSessionId: bb094a39-05c5-494d-8b01-cc34809ccae9
---

Y-arc closure summary. The Y-arc was planned as 10 slices testing
V7 on the substrate's own data and benchmarking against
structure-agnostic codecs. Seven slices landed; Y6+Y7 (more
predictor variants) deferred as unlikely to close the empirical
gap revealed by Y8.

**Slices landed:**

  Y1 — MeasurementCell harness + atlas sweep driver.
       (`tests/test_substrate_atlas.py`).
  Y2 — `substrate_agda` corpus (concat Agda source).
  Y3 — `substrate_memory` corpus (concat memory entries).
  Y4 — `substrate_opcodes` corpus (codec's own opcode table
       serialised — recursive-coupling test).
  Y5 — V7 sweep across substrate corpora. Commit `[Y1-Y5+Y8]`.
  Y8 — Cross-codec comparison V7 vs L0 vs gzip vs lzma.
       (`tests/test_substrate_crosscodec.py`).
  Y9 — `Substrate.Category.CompressionAtlas` Agda bridge. Commit
       `5889e7b`. Also materialised the ad-hoc `t1t2_handcrafted`
       corpus per user feedback.
  Y10 — This memory entry.

**Slices deferred:**

  Y6 — LexicalTokenPredictor. Cross-layer (byte vs chain) plumbing
       required; unlikely to close the 3× gap to gzip on text.
  Y7 — CoxeterWordPredictor. Largely redundant with the existing
       QuaternionContextPredictor (W-arc). Deferred until a corpus
       distinguishes them.

**Empirical Y5 results (4KB per corpus):**

  corpus              identity   two-stage   Δ
  substrate_agda      7.047      7.119       +0.072 (R)
  substrate_memory    7.051      7.211       +0.160 (R)
  substrate_opcodes   0.566      0.529       -0.037 (B)

Recursive-coupling case (codec compressing its own opcode source)
BENEFITS — small but positive, per [[tetrative-metacircularity]].
Substrate-documentation TEXT (Agda source, memory entries) regresses
— V7's predictor ring doesn't capture natural-text structure on
substrate documentation.

**Empirical Y8 cross-codec (4KB per corpus):**

  corpus              V7 id   V7 spec   L0     gzip-9   lzma-ex
  substrate_agda      7.047   7.119     7.045  2.621    2.719
  substrate_memory    7.051   7.211     7.049  3.801    3.938
  substrate_opcodes   0.566   0.529     0.564  0.172    0.258

**Bounded findings per [[negative-findings-corpus-bound]]:**

On the 3 tested substrate corpora at 4KB:
  * V7 b/byte > gzip b/byte by 2.7× to 4× on text corpora.
  * V7 b/byte > gzip b/byte by 3.1× on the opcode corpus.
  * V7 STRUCTURAL wins on T1+T2-style hand-crafted patterns
    (commits a016442, b8871a6: 10.5%) do not generalise to beating
    LZ77-style codecs on natural text or pure-structural data
    at this scale.

**Diagnostic interpretation:**

V7 is a STRUCTURE-REVEALING codec — its (E3) BENEFITS pattern
provides empirical evidence of substrate-aligned structural
captures. It is NOT yet a gzip-competitive general-purpose
codec. The 3× gap to gzip is the deferred structural work:

  1. Range-coder rewiring (X-arc deferred) — V7's chain-walk +
     arithmetic-coding overhead dominates. Replacing/augmenting
     with LZ77-style matching might close the gap.
  2. Chamber-state residue compensation (X-arc deferred) — extends
     match coverage across chamber-state-different positions.
  3. Lookahead matricisation (W5 deferred) — performance, not
     compression.

**Categorical naming:**

`Substrate.Category.CompressionAtlas` (commit `5889e7b`) names
the empirical measurements as a substrate primitive. Per the
DBE pass: the atlas IS a functor from (CorpusCategory ×
PredictorRing) into ordered (b/byte, ≤). Where the functor
shows REGRESSES, the predictor ring is missing a generator for
that corpus class per [[expose-generator-not-orbit]].

**Z-arc target candidates** (next):

  1. **Honest pivot**: integrate an LZ77-style matcher alongside
     the V7 predictor ring. The structural codec captures
     long-range substrate alignment; LZ77 captures byte-level
     repetition. Both produce emissions; the generator ring's
     operad (per [[v-arc-generator-operad]]) speculates between
     them.
  2. **Substrate-only validation**: extend t1t2_handcrafted to
     a family of substrate-designed corpora that V7 SHOULD win on
     by construction (not text-like). Validates V7's
     structural-codec claim on its natural target class.
  3. **Performance arc**: matricise V7's lookahead + finalise the
     range-coder. Closes the practical-usability gap.
  4. **Substrate Agda extraction**: extract V7's Python into Agda
     under the cubical extraction discipline ([[agda-cubical-extraction-discipline]]).

Related: [[w-arc-predictor-ring]] (parent — the predictor side
the atlas measures); [[v-arc-generator-operad]] (the operad
structure the atlas instantiates); [[tetrative-metacircularity]]
(the recursive-coupling reading of substrate_opcodes);
[[negative-findings-corpus-bound]] (the discipline guarding this
arc's honest negative findings against overclaim);
[[homology-cohomology-recursion]] (BENEFITS / REGRESSES cells
read as homology / cohomology evidence).
