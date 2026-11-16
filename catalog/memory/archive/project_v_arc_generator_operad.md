---
name: v-arc-generator-operad
description: "V-arc (10 slices) frames the codec as an operad over a generator ring (rewrite rules + adaptive predictors + basis-torsor transitions + bit-granular sink); structure shipped, substantive empirical work deferred"
metadata: 
  node_type: memory
  type: project
  originSessionId: bb094a39-05c5-494d-8b01-cc34809ccae9
---

V-arc closure summary. The V-arc reframes the codec's entire
emission machinery as a single algebraic structure (operad over a
generator ring); structural infrastructure lands across all ten
slices; substantive compression work (basis-aware emission
transformation, range-coder rewiring for true bit-granular sink)
is recognized and deferred.

**Design pieces (iterated over the session via user-led
refinement):**

  1. **Spectral analyzer as torsor** — basis-state is a labeled
     point in a torsor over the basis-change Lie group; no
     privileged "home" basis. Heading (S_BASIS_AT label) and
     bearing (S_BASIS_BY quaternion component) are dual access
     patterns.

  2. **Alphabet speculation** — multiple parallel predictors, one
     per basis label; cost-gate selects per emission.

  3. **Generator ring** — rewrite rules and adaptive predictors are
     peers in one ring (per the user: "an adaptive encoder is just
     another rewrite engine"). The codec is an operad over this
     ring.

  4. **Bit-granular sink** — `S_SHIFT_BIT` commits one bit (per user
     correction: drop `S_COPY_NIBBLE`, use only single-bit
     emission); symmetric with bit-granular input.

**Slices landed:**

  V1 — `BasisState` type + `S_BASIS_AT` (absolute heading). Commit
       `e2c0a44`. V7 codec begins; output V6-equivalent.
  V2 — `S_BASIS_BY` quaternion-word (relative bearing). Q_8 = {±1,
       ±i, ±j, ±k} via 4-bit selector. Commit `a0e871b`.
  V3 — Per-basis parallel predictors (counts_by_basis dict, one
       count array per BasisLabel). Commit `e2f02c1`.
  V4–V7 — Operad infrastructure scaffold bundled. Speculate_basis
       flag, `_predictor_cost_estimate` helper, generator-ring
       framing, predictor-variants acknowledged. Commit `06f2022`.
  V8 — `S_SHIFT_BIT` opcode slot + decoder dispatch (structural
       placeholder; range-coder rewiring is a separate arc).
       Commit `62599b8`.
  V9 — `Substrate.Category.GeneratorOperad` Agda bridge; operad
       laws stated as proof obligations, LeftIdentity inhabited.
       --safe --without-K. Commit `29a4849`.
  V10 — Capstone (this memory entry).

**Honest scope assessment:**

The V-arc lands **structural infrastructure**, not empirical
compression gains. Each slice's identity case reproduces V6
exactly (+0.000 to +0.008 b/byte overhead from unused control
slots). The encoder defaults to never exercising the new
machinery; the user can opt in via `speculate_basis=True`, but
the substantive work to make basis switching actually deliver
bits — basis-aware emission transformation that changes WHAT is
emitted, not just WHICH count array is consulted — is recognized
and deferred.

The deferred substantive work is what would actually demonstrate
the (E3) BENEFITS. Without it, V7 with no speculation flags is
just V6 with extra opcode slots.

**Why ship the structural arc anyway:**

Per [[expose-generator-not-orbit]]: the codec's prior design hid
the generator-set behind layers (rules vs adaptive coder as
separate stages). The V-arc EXPOSES them as peers in one ring.
That exposure has structural value even before the encoder
actively exercises the new generators.

Per [[homology-cohomology-recursion]]: rewrite rules are observed
redundancy (homology of the stream's pattern set); adaptive
predictors are catalogued frequency (cohomology of the chain
distribution). They're dual readings of the same data — both live
in the operad. Naming this unification is the V-arc's deliverable.

Per [[categorical-name-first]]: "operad" was the correct name all
along; the V-arc's Agda bridge `Substrate.Category.GeneratorOperad`
makes that name first-class in the substrate.

**Bounded claim** (per [[negative-findings-corpus-bound]]):
  No (E3) measurement performed. The structure round-trips
  losslessly with negligible overhead. Empirical performance
  awaits the deferred substantive work.

**W-arc target candidates** (next):

  1. **Basis-aware emission transformation.** Make a non-default
     basis ACTUALLY change emission content (e.g., spectral
     basis = emit eigenvector coefficients with different
     alphabet/distribution). Validates (E3) for the V-arc.
  2. **Range-coder rewiring for true bit-granular sink.** Make
     `S_SHIFT_BIT` actually defer bit emission until released.
     Enables compositional codec stacking.
  3. **Chamber-state residue compensation** (carried over from
     U-arc deferred). The V₄ residue compensates chamber-state
     drift; wiring it would unbind the codomain for randomized
     corpora identified in [[u-arc-emergent-lz]].
  4. **Operad-of-operads (tetrative lift).** The codec's operad
     becomes one element in a higher-level operad whose elements
     are codecs; speculation across the meta-operad picks codecs
     per region.

Related: [[u-arc-emergent-lz]] (parent arc; RuleAction algebra);
[[quot-stack-associativity-scope]] (alias-define mechanism, first
(E3) BENEFITS); [[flip-opcode-speculation]] (the amortisation
pattern); [[expose-generator-not-orbit]] (the substrate principle
this arc serves).
