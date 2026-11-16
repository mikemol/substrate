---
name: z-arc-reference-orbit
description: "Z-arc adds chain-symbol backref (DEFLATE-style LZ77) to V7's operad ring; closes part of the Y-arc gap to gzip (5.5% on substrate Agda, 70% on T1+T2); names the 8-orbit reference-generator family as a substrate primitive"
metadata: 
  node_type: memory
  type: project
  originSessionId: bb094a39-05c5-494d-8b01-cc34809ccae9
---

Z-arc closure summary. The Z-arc was planned as 10 slices targeting
the Y-arc gap to gzip/lzma on substrate corpora. Three substantive
slices landed (Z1 chain-symbol backref + Z5 sweep + Z9 Agda
primitive); seven were scoped for future arcs.

**Slices landed:**

  Z1 — `S_REF_RECENT` chain-symbol backref opcode + matcher.
       (`eliza/backref.py` + `gpu_codec_v7.py` integration.)
       Commit `[Z1+Z9]`.
  Z5 — Empirical sweep on substrate corpora with backref enabled.
  Z9 — `Substrate.Category.ReferenceOrbit` Agda bridge.
       Names the 8-orbit (source × permanence × binding) reference-
       generator family. Per [[3plus1-parity-universal]] the 3-axis
       structure with BindingClass as chirality realises another
       instance of the substrate's 3+1 universal.
       Commit `[Z1+Z9]`.

**Slices deferred:**

  Z2 — `S_REF_RECENT_BYTE` byte-level backref. Requires chain
       re-walk on decoder side (copied bytes' chain symbols depend
       on current chamber state). Tractable but adds substantial
       complexity beyond Z1's empirical wins. Deferred until Z1's
       gap-closure is measured against gzip.
  Z3 — Hash-chain matcher (matricised). Z1's naive O(window × maxlen)
       matcher costs ~10s per 4KB corpus; tensorised hash-chain
       would restore practical speed. Pure perf, no compression
       effect.
  Z4 — Full operad cost-gate integration. Z1 uses a simple
       `backref_length > 5 × greedy_length` threshold; full
       integration would speculate across all generators per
       emission via the W-arc cost-gate. Refinement.
  Z6 — BWT-block generator. Substrate has `Substrate.Category.
       BWTEmergence` already; integration as ring element is its
       own arc.
  Z7 — MTF generator (recency-stack permutation).
  Z8 — Delta-filter generator (chain-walk-native).

**Empirical Z1+Z5 results at 4096B:**

  corpus           identity    + backref   + both       gzip-9
  engine.py        7.236       7.211       7.113        (~2.6)
  elf-dd           3.137       3.129       3.189
  substrate_agda   7.049       6.770       6.660        2.621
  T1+T2/T2 (3KB)   2.705       0.789       —            —

Backref delivers:
  * T1+T2: -1.916 b/byte (70.8% improvement). The structural-
    recurrence corpus that U-arc alias-define partially captured
    is now near-optimal under chain-symbol LZ77.
  * substrate_agda: -0.389 b/byte (5.5%). Backref catches
    Agda-source repetition the predictor ring missed.
  * engine.py / elf-dd: small but positive deltas.

Per [[negative-findings-corpus-bound]] (bounded findings):
  * Z1 closes PART of the gzip gap (2-5% per natural corpus) but
    not all (still 2.5× behind gzip on substrate_agda).
  * Z2 (byte-level, chamber-free) likely needed to close the
    remaining 2× gap.

**The 8-orbit reference family (Z9 Agda):**

  Per [[expose-generator-not-orbit]]: the substrate's
  reference-emission family is parameterised by three independent
  binary axes:
    SourceClass:    ExistingRuleSlice ∨ ArbitraryRecentSpan
    Permanence:     PermanentRule     ∨ OneShot
    BindingClass:   ChamberBound      ∨ ChamberFree

  Named orbits:
    QUOT             = (ExistingRuleSlice, PermanentRule, ChamberBound)
                       — U-arc alias-define.
    ChainBackRef     = (ArbitraryRecentSpan, OneShot, ChamberBound)
                       — Z1 (this arc).
    ByteBackRef      = (ArbitraryRecentSpan, OneShot, ChamberFree)
                       — Z2 (deferred).
    QUOTRecent       = (ArbitraryRecentSpan, PermanentRule,
                          ChamberBound) — full QUOT-stack design.
    OneShotSlice     = (ExistingRuleSlice, OneShot, ChamberBound)
    + 3 ChamberFree variants requiring V₄ residue compensation
      (X-arc deferred runtime).

Per [[3plus1-parity-universal]]: the (3-axis, 1-binding) structure
with BindingClass as chirality is another instance of the
substrate's 3+1 universal. The substrate-aligned (ChamberBound) /
structure-agnostic (ChamberFree) split carries the chirality F₂.

**Z-arc target (next-next):**

The gap to gzip on substrate text reveals what V7 still lacks:
  1. **Byte-level addressing** (Z2) — chamber-free backref bypasses
     the chamber-state binding entirely. Likely closes a further
     1.5-2× of the gzip gap.
  2. **Hash-chain matricisation** (Z3) — practical-speed encoding.
     V7's structural wins + Z2's coverage means the codec becomes
     competitive in compression; matricisation makes it
     competitive in speed.
  3. **BWT/MTF/Delta generators** (Z6-Z8) — Substrate has the
     primitives named; ring integration is mechanical once
     allocated.

Related: [[y-arc-substrate-atlas]] (parent — the gap to gzip the
Z-arc partially closes); [[v-arc-generator-operad]] (the operad
framework Z1 extends); [[u-arc-emergent-lz]] (the chamber-state
binding Z2 would lift); [[3plus1-parity-universal]] (the
structural pattern the 8-orbit family instantiates);
[[expose-generator-not-orbit]] (the discipline the family
honours).
