---
name: u-arc-emergent-lz
description: "U-arc (10 slices) lands the RuleAction algebraic-action abstraction over the GPU codec; structure ships, per-slice (E3) empirically NEUTRAL/REGRESSES on text — beneficiary corpora deferred to W-arc"
metadata: 
  node_type: memory
  type: project
  originSessionId: bb094a39-05c5-494d-8b01-cc34809ccae9
---

U-arc closure summary. The codec gains a unified algebraic-action
abstraction at the substrate level; the empirical case for each
factor remains to be demonstrated on factor-biased corpora.

**Structure delivered (E1+E2 across all slices, lossless round-trip):**

  * U1: `RuleAction = (residue, start_phase, length_mask, f2_patch,
    span_coupling)` type in `eliza/rule_action.py`; V6 codec at
    `eliza/gpu_codec_v6.py` reproduces V5 byte-exactly at
    identity-only.
  * U2: + start_phase factor (S_PHASE inline control).
  * U3: + length_mask completing AffineProjection (S_AFFINE inline);
    LZ77 emerges as an A-orbit point (rule + (phase, length) slice).
  * U4: + F₂Patch k=1 via FLIP-OPCODE paradigm (S_FLIP_PATCH1) —
    after U3 inline-control regressed +0.078 b/byte the user pushed
    back to "this is why we have the flag toggling paradigm";
    subsequent factors use flip-opcodes.
  * U5: F₂Patch k≤K (S_FLIP_PATCHK) — decoder dispatch landed.
  * U6+U7: SpanCoupling (S_FLIP_SPAN) with full F₂ overlap mask;
    H-rung non-commutativity (left/right rule order matters).
  * U8: cost-aware gate — `_affine_beats_greedy` compares
    symbols-per-walk-chain; integrated mode commits to affine only
    when it beats greedy.
  * U9: `agda/Substrate/Category/RuleAction.agda` — monoid acting
    on rule expansions; --safe --without-K; action laws stated as
    proof obligations (not yet inhabited).

**Empirical (E3) findings across text/ELF/zeros at 1KB** (added after
U10 capstone — initial U10 only tested text, user pointed out the gap;
testing ELF exposed two correctness bugs in U3 decoder, fixed in
commit 3634056):

  corpus           identity  + affine     + patch1     + integrated
  text engine.py   8.172     8.250 (R)    15.906 (R)   8.172 (=)
  elf  /bin/dd     5.438     5.672 (R)     9.500 (R)   5.438 (=)
  zeros            0.148     0.148 (=)     0.148 (=)   0.148 (=)

All three standard corpora: factor activation regresses or is
neutral; the U8 cost-gate correctly degrades to identity. Bounded
claim: **on the tested corpora (text/ELF/zeros) with the tested
modes (affine / patch1 / integrated), none of the other modes
outperformed greedy.** The claim does NOT generalise to "greedy is
the local optimum" — that would be a negation-overclaim from
absence on three corpora to a structural property. Untested factor-
biased corpora (W-arc) may still surface modes that beat greedy.

The cost-aware gate is structurally correct: it identifies that on
engine.py text, no factor's bit-cost beats greedy. The honest
finding is "greedy IS the local optimum on code corpora; factor
benefit awaits factor-biased corpora."

**Why factors didn't earn their bits on this corpus:**

  * `start_phase` — engine.py code has tight bytewise local structure;
    long rules don't have phase-shifted re-occurrences.
  * `length_mask` — same root cause; truncation only helps when
    longer body matches exist.
  * `f2_patch` — code has too few one-character-different near-
    matches at chain level; near-matches at the BYTE level don't
    show up as near-matches at the CHAIN level after S₄ chamber
    walk transformation.
  * `span_coupling` — not exercised by encoder (decoder-only).

**Architectural milestone:** the codec is now a unified
`(rule_id, action ∈ A) → chain-symbols` machine; LZ77, B-frames,
fuzzy match are A-orbit-element catalogues, not separate algorithms.
The flip-opcode paradigm amortises per-emission control cost so each
factor can be activated only when it pays.

**W-arc target candidates (deferred):**

  1. **Adversarial / factor-biased corpora.** Construct text streams
     where each A-factor's specific structure earns visible bits:
     shifted-start substrings (phase), near-duplicates (affine), 
     single-character variations (patch1), compound words (span).
     Validates (E3) BENEFITS where the structure predicts it should.
  2. **Substrate self-application.** Run V6 on Agda source files
     and decomposition-graph data — the codec's algebraic alignment
     with substrate structure should yield greater compression on
     substrate-internal data than on text/elf.
  3. **Adaptive weight on cost-gate.** Currently
     `_affine_beats_greedy` uses fixed 4-symbol assumption. Online
     adaptation of per-factor weights (per [[multi-route-equivariance-
     recovery]] — a per-window gauge) could activate factors
     selectively even on mixed corpora.
  4. **GPU matricisation of factor search.** The naïve CPU loops in
     `_try_affine_match` / `_try_patch1_match` cost ~7-9 seconds per
     1KB. Vectorising over the body-tensor would restore the
     V5-class encode times.

Related memory: [[project-qarc-closure]] (V2 GPU/L0 crossover);
[[project-rarc-lambda-vm-recognition]] (R-arc — opcode-VM as CCC);
[[project-sarc-active-speculation]] (S-arc active-speculation policy);
[[flip-opcode-speculation]] (the paradigm U4 adopted after U3's
regression); [[expose-generator-not-orbit]] (action algebra A IS the
generator behind the per-emission opcode orbit);
[[categorical-name-first]] (RuleAction's name is "monoid action on
rule expansions" — standard category theory).
