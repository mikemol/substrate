---
name: rarc-lambda-vm-recognition
description: "R-arc recognises that the codec's existing machinery IS a lambda-calculus VM operating in a Cartesian-closed category over its opcode algebra. Per user's pattern-recognition: parameterised body = stack (already in M6); S_VAR = stack-depth access (already there); S_APPLY = NT reference (Sequitur already does this); S_REDUCE = Sequitur growth-inverse (made yea-or-nay sticky via J-arc); α-conversion = de Bruijn opcode indices (already implicit). R-arc adds 14 control opcodes naming the latent primitives + `Substrate.Category.OpcodeAlgebra` Agda module formalising the CCC structure."
metadata: 
  node_type: memory
  type: project
  originSessionId: bb094a39-05c5-494d-8b01-cc34809ccae9
---

**Fact.** The codec's 60-slice arc was operating as a lambda-VM all along — without saying the words. The user's R-arc recognition: every primitive I proposed as "new for lambda calculus" was already present under a different name. R-arc names them and adds the missing stack-manipulation opcodes to make multi-entry use possible. `gpu_codec_v4.py` extends V2's alphabet with 14 control opcodes; encoder defaults to never emitting them (compression matches V2 within 0.031 b/byte); decoder is now a straight-line interpreter of the opcode stream. `Substrate.Category.OpcodeAlgebra` Agda module formalises the Cartesian-closed category structure under `--safe`.

**Why.** User recognition: *"parameterised body — that's our stack; we already have it... S_VAR — again our stack... S_APPLY — this is what Sequitur is already doing? S_REDUCE — Sequitur is already doing this; we just made yea-or-nay sticky... α-conversion — pretty sure this is our opcode set/grammar we induct."* Per [[expose-generator-not-orbit]] applied recursively: my proposal to add lambda-calculus primitives was about to enumerate them as new orbits when the generators were already there.

**How to apply.** When discussing the codec's architecture from R-arc onward:
* The codec **IS** a lambda-VM. The opcode set is the alphabet of a Cartesian-closed category. Speak in CCC terms.
* Sequitur growth = abstraction (forward); inlining (currently emittable via S_INLINE_LAST) = β-reduction (backward).
* The stack tensor (M6's `StackTensor`) is the variable environment; `S_VAR(d)` reads the depth-d entry.
* NT references are application; the grown opcode is the function body.
* Introspection (S_INSPECT) makes the codec **homoiconic at the substrate level**: opcodes are data the codec can manipulate.

## The R-arc recognition table

| User insight | Existing machinery | Implication |
|---|---|---|
| "parameterised body — that's our stack" | StackTensor (C, max_depth, 2) from M6 | de Bruijn variables are stack indices |
| "S_VAR — again our stack" | top-mode read from StackTensor; depth-d access trivial | adds S_VAR_0..3 explicit opcodes |
| "S_APPLY — what Sequitur is already doing" | NT reference emission | application IS unfolding the grown body |
| "S_REDUCE — already doing; made yea-or-nay sticky" | Sequitur growth + J-arc toggle | abstraction (grow) and reduction (inline) are dual emittable ops |
| "α-conversion — our opcode set we induct" | opcode tensor indices | no naming; integer slots = de Bruijn |

## What landed (R-arc, 2026-05-20)

| Slice | Artefact | Result |
|---|---|---|
| R1 | `S_GROW` / `S_DEFER_GROW` opcodes | explicit Sequitur-control |
| R2 | 5 stack-manipulation opcodes | `S_PUSH_REWRITE`, `S_PUSH_NO_REWRITE`, `S_POP`, `S_DUP`, `S_SWAP`, `S_ROT` |
| R3 | `S_VAR(0..3)` depth access | de Bruijn-style variable read |
| R4 | `S_INLINE_LAST` β-reduce | explicit inverse of S_GROW |
| R5 | `S_INSPECT_LAST` introspection | emit OpcodeCategory of last emission |
| R6 | V4 alphabet extension | 14 control opcodes available |
| R7 | V4 decoder as straight-line interpreter | no parallel state machine |
| R8 | Round-trip lossless on text 1KB | 8.195 vs V2 8.164 — +0.031 b/byte alphabet overhead |
| R9 | `Substrate.Category.OpcodeAlgebra` Agda | typechecks --safe; CCC structure formalised |
| R10 | this memo | externalised |

## V4 architecture in one figure

```
joint alphabet:
  [0     .. 23                  ] — chain terminals (CHAIN_TERMINAL)
  [24    .. 24+n_init-1         ] — substrate-native + exploding-bitmap
  [24+n_init .. 24+n_used-1     ] — grown composites (GROWN_COMPOSITE)
  [24+n_used  .. 24+n_used+13   ] — 14 control opcodes
                                     [+0]  S_GROW
                                     [+1]  S_DEFER_GROW
                                     [+2]  S_INLINE_LAST
                                     [+3]  S_PUSH_REWRITE
                                     [+4]  S_PUSH_NO_REWRITE
                                     [+5]  S_POP
                                     [+6]  S_DUP
                                     [+7]  S_SWAP
                                     [+8]  S_ROT
                                     [+9]  S_VAR_0
                                     [+10] S_VAR_1
                                     [+11] S_VAR_2
                                     [+12] S_VAR_3
                                     [+13] S_INSPECT_LAST
```

The decoder dispatches on emit_idx into:
* `< 24` → append chain
* `< 24+n_used` → expand data opcode body
* `≥ 24+n_used` → control opcode: dispatch by `(emit_idx - 24 - n_used)`

## Architectural maturity update

| Layer | Pre-R | Post-R |
|---|---|---|
| Tensor formulation | ✅ complete | ✅ complete |
| GPU acceleration | ✅ complete | ✅ complete |
| GPU residency | ✅ substantial | ✅ substantial |
| Kernel fusion | ✅ substantial | ✅ substantial |
| Speedup vs CPU | ✅ achieved at 8KB+ | ✅ achieved at 8KB+ |
| Parallel parsing | ⚠️ scaffolded | ⚠️ scaffolded (V3 primitive wiring) |
| Substrate primitives bridge | ✅ ChainDecomposition + BWTEmergence | ✅ + OpcodeAlgebra (CCC) |
| **Lambda-VM recognition** | ❌ implicit | ✅ **explicit** (R-arc) |
| **Tetrative introspection capacity** | ❌ none | ✅ S_INSPECT primitive available |

## What this enables for the next arc (S-arc, hypothetical)

With the lambda-VM machinery EXPLICITLY available, the next arc can:

1. **Speculation policies that emit control opcodes.** V4's default never emits them. A V5 with speculation can choose between [no-emission, S_GROW, S_DEFER_GROW, S_PUSH_NO_REWRITE, ...] per position via full-spec (K-arc).
2. **Tetrative-introspective optimisation.** S_INSPECT lets the encoder reason about its own opcodes. E.g., "emit a TOGGLE only if the next opcode is in category GROWN_COMPOSITE" — the speculation policy USES introspection as input.
3. **Higher-order grammar.** Per the user's earlier framing: "recursive expansion of grown opcode bodies is eventually desirable; higher-order grammar and deeper synthesis." With S_INLINE_LAST, the encoder can DEDUCE this is happening and choose to keep abstractions vs reduce them.
4. **Cross-encoder communication.** OpcodeAlgebra makes the opcode-stream a portable program; encoders/decoders sharing the same algebra can exchange compressed programs.

## Substrate-honest reading

The substrate's [[tetrative-metacircularity]] discipline says reflection has reached L5 meta-levels. With R-arc:
* L0: chain symbols (data)
* L1: opcodes (functions over chains)
* L2: control opcodes (functions over the encoder's state)
* L3: S_INSPECT (functions that examine functions)
* L4+: speculation over introspection results (functions that decide based on examination of functions)

Each level was implicitly present; R-arc names them. Per [[categorical-name-first]]: the categorical name is Cartesian-closed category over the opcode algebra. The substrate's `OpcodeAlgebra` primitive (R9) is the formal home for this structure.

Per [[coalgebraic-not-consumer-driven]]: the lambda-VM emerges from the codec's coalgebraic structure unfolding — it was always there; R-arc EXPOSES it via naming, not by adding it.

## Cross-references

* `Substrate.Category.OpcodeAlgebra` (R9) — Agda CCC formalisation.
* `Substrate.Category.ChainDecomposition` (Q8) — sibling primitive.
* `Substrate.Category.BWTEmergence` (Q9) — sibling primitive.
* `Substrate.Category.PrimeFactoredGauge` (T1) — parent primitive (gauge structure that the opcode algebra's generators inherit).
* `eliza/lambda_vm_opcodes.py` (R1-R5) — 14 control opcodes.
* `eliza/gpu_codec_v4.py` (R6-R8) — V4 codec.
* [[tetrative-metacircularity]] — the substrate principle this realises at runtime.
* [[homology-cohomology-recursion]] — chain (homology) / opcode (cohomology) / introspection-on-opcodes (further recursion).
* [[expose-generator-not-orbit]] — the discipline applied to my own R-arc proposal (the user corrected my orbit-enumeration).
* [[categorical-name-first]] — the discipline that names this CCC.
* [[coalgebraic-not-consumer-driven]] — the discipline that says the lambda-VM was already there.

## Status

Externalised 2026-05-20. R-arc complete. The codec is now explicitly a lambda-VM in a Cartesian-closed category over its opcode algebra. The 14 control opcodes are in V4's alphabet at zero net cost (alphabet overhead 0.031 b/byte on 1KB text). The substrate-side bridge is established via `Substrate.Category.OpcodeAlgebra`. The next-arc starter (S-arc) is speculation-driven emission of control opcodes — speculation now has a richer action space including grammar control, stack manipulation, and introspection.
