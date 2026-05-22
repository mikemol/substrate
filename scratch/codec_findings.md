# Codec empirical findings

Consolidated measurements from the codec arcs (P/Q/M/N/O/U/V/W/X), migrated
from individual memory entries. Each section names the structural fact
discovered + the corpora/measurements that support it. Per
[[reject-lem-in-substrate]]: measurements are data, not pass/fail verdicts.

------------------------------------------------------------------------

## cap-doubling-eliminates-freeze

`try_grow_opcode` in `eliza/gpu_codec_v2.py` now doubles `max_opcodes`
(and `max_body`) when full, rather than freezing. Power-of-2 alignment
with the rest of the codec is preserved iff the initial cap is a power
of 2.

**Why.** Per [[project-parc-speculation-packaging]] and
[[project-qarc-closure]] the cap-natural phase-change peak (16KB
cap=2048 → 1773 µs/step pathology) was caused by every observed digram
triggering growth + match-tensor reshape exactly at the cap boundary.
User's framing: "we just double the capacity. The prior-existing
grammar slots in at the start."

**How to apply.** Initial cap is now purely an allocation hint;
compression no longer depends on it (V2/L0 ratio = 1.000 across
cap ∈ {128, 256, 512, 1024, 2048, 4096, 8192} at sizes 4K/8K/16K).
`try_grow_opcode` returns a 6-tuple including the (possibly doubled)
`max_opcodes`; all callers in V2/V3/V4/V5 unpack this. Small initial
caps (e.g. 128) pay amortised-O(1) per growth across log₂(N)
doublings; cap=512 is reasonable default; cap=1024+ avoids most
copies on text-class inputs.

------------------------------------------------------------------------

## chain-grammar-compression-findings

The chain-Sequitur arc's compression value is **structural**, not
raw bits-per-byte. Concrete measurements across (text / elf / zeros)
× (4K / 16K / 64K):

| Corpus | gt-baseline | hybrid | chain-only | byte-only | +V4-cond | +chain-cond | ml-grammar |
|--------|------------:|-------:|-----------:|----------:|---------:|------------:|-----------:|
| text   |       3.565 |  3.611 |      0.018 |     3.593 |    4.601 |       5.796 |      0.018 |
| elf    |       3.771 |  3.852 |      0.015 |     3.837 |    4.088 |       4.352 |      0.014 |
| zeros  |       0.036 |  0.329 |      0.001 |     0.328 |    0.021 |       0.021 |      0.001 |

**Key findings.**

1. **Chain stream is nearly free** — 0.018 b/byte for text (~ log₂(24)/256).
2. **Chain conditioning fails at standard granularity** — 24× more
   contexts without 24× more data. Text 64KB: byte-only 3.593 →
   +chain-cond 5.796 (+2.2 b/byte).
3. **Chain conditioning helps degenerate inputs** — zeros 64KB:
   byte-only 0.328 → +chain-cond 0.021. Sharp prior on conditioned
   context.
4. **gt-baseline's rotation chooser pays for itself** — beats byte-only
   by 0.03–0.3 b/byte on text/elf.
5. **Multi-level grammar marginally cheapens the chain stream** —
   0.014–0.018 b/byte; absolute chain cost already negligible.

**What this means.** The chain machinery's PRIMARY value is structural
(per-Sylow agreement breakdown, recursive grammar inference,
substrate-native rewrite step — per [[homology-cohomology-recursion]]).
SECONDARY value (byte-level compression) is marginal at standard window
sizes, NEGATIVE when used as predictor context with insufficient data.

Future directions where chain context might help: corpora ≥10MB,
hierarchical conditioning, chain context for the rotation chooser
rather than the byte predictor.

Harness: `tests/test_compression_panout.py`.

------------------------------------------------------------------------

## full-speculation-codec

Replace K-step beam search with full-remainder speculation: at each
decision point, encode the entire rest of the stream under each
candidate prefix; commit the winner. Validates the stack-machine
architecture:

* full-spec gives EXACTLY L0's result (0 toggles, 9.688 b/byte = L0
  on text 256B);
* the K-step beam was the bad heuristic, not the architecture.

Cost: O(N²) per encoding (~9s on 256B, ~34s on 512B). BWT-emergence
diagnostic across the rotation axis pending.

------------------------------------------------------------------------

## sppf-as-free-markov-codec

The SPPF (shared packed parse forest) over the chain-Sequitur rules
is structurally a free Markov model — codec = SPPF + start-rule body.
The grammar metadata cost is non-trivial on low-redundancy data
(loses to gt-baseline on text/elf); the codec dominates on highly
repetitive data (zeros 16KB: 3× better at 0.027 b/byte).

------------------------------------------------------------------------

## stack-machine-codec

Generalised flip-opcode to sticky-mode toggle-opcodes via a bounded
stack of (rewrite, observe) entries. Round-trip is lossless;
architecturally the correct primitive per "transformations as flags
+ opcodes manipulate stack." Empirically worse than L0 with K-step
beam (heuristic problem, not architecture; full-speculation fixes —
see full-speculation-codec above).

------------------------------------------------------------------------

## tetrative-speculation-axis

Exploration of L0/L1/L2/... where each level exposes a previously-
automatic codec decision as explicit speculation. Empirical:
per-emission-flag implementation adds ~1.5 b/byte control-bit
overhead per level (L0 7.23 → L1 9.17 → L2 10.84). FIXED by
flip-opcode redesign (see flip-opcode-speculation below).

------------------------------------------------------------------------

## flip-opcode-speculation

Flip-opcode (special command word in joint alphabet) + K-step beam
lookahead eliminates per-emission control-bit overhead. L1-flip /
L2-flip MATCH L0 baseline (text 2KB: 7.73 / 7.82 vs L0 7.72; old
L1-flag was 9.29). Flip rate ≈ 0 on text/elf/zeros; L0 default IS
near-optimal on these corpora. Speculation primitive
ARCHITECTURALLY available at zero cost; "expose generator not orbit"
applied to control bits.

------------------------------------------------------------------------

## gpu-matricised-codec

N-arc closure: cuBLAS env fixed (`apt install libcublas-dev-13-1`);
all four codec stages ported to CuPy with CPU fallback via `xp()`.
End-to-end pipeline round-trips lossless. Two rounds of review-driven
fixes applied; remaining bottleneck is per-step GPU launch overhead.
BWT-emergence positively signalled at 128B (top-3 rotations cover
100% of windows).

------------------------------------------------------------------------

## matricised-codec-pipeline

M-arc completion: every codec stage as a tensor object on CPU (range
coder, opcode set, digram index, stack-machine, speculation batch).
`tensor_codec.py` composes end-to-end with lossless round-trip at
10.09 b/byte on 256B.

------------------------------------------------------------------------

## opcode-vm-codec

Substrate-native codec: each rule = opcode, pre-populated with
V₄/Sylow-3 generators, speculative-commit = exploding-bitmap,
adaptive opcode growth, rule-utility checking REMOVED. Adaptive
opcode-VM: text 4KB 7.23 b/byte (35% better than SPPF), elf 4.75,
zeros 0.04 b/byte (5× better than gt-baseline). Competitive with
gt on text/elf, dominates on zeros.

------------------------------------------------------------------------

## quot-stack-associativity-scope

User-guided refinement to U-arc; reification-cost was the codomain
binding; alias-define subset achieves first (E3) BENEFITS (8.5% on
structurally-designed corpus); full QUOT-stack design (separate stack
from R-arc lambda-VM, associativity scope, references by stack
position) recorded for future slice.

------------------------------------------------------------------------

## substrate-native-recursive-grammar

ChainSequitur over per-window walk chains with S₄-product rule lift;
6 levels demonstrated; chain product preserved across all levels;
rule occurrences correspond to byte-window spans; substrate-honest
realisation of [[homology-cohomology-recursion]] at runtime.

------------------------------------------------------------------------

## Cross-references

* [[project-codec-as-pfg-witness]] — Codec realises PrimeFactoredGauge
  at S₄ = V₄ ⋊ S₃; chain-of-charts decomposition per
  `MultiRouteEquivariance.agda` T5.
* [[project-rarc-lambda-vm-recognition]] — Codec's machinery IS a
  lambda-VM in a CCC; the R-arc adds 14 control opcodes +
  `Substrate.Category.OpcodeAlgebra` Agda formalisation.
* [[homology-cohomology-recursion]] — observed = homology, cataloged
  = cohomology, recursive at every level.
