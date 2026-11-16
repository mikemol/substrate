---
name: feedback_never_discard_residue
description: "core substrate principle — never discard residue; the quotient/remainder/cofactor is always kept and reused, never re-derived"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: b0f173b0-7c01-42e2-bd3c-cbed23f2d66a
---

**We never discard residue.** Division/recursion ALWAYS retains the
quotient AND remainder; downstream work reuses that kept residue rather than
recomputing or re-dividing.

**Why:** it's the design spine of the Wedge/Trace/EEA stack and the balanced
SPPF — `Wedge` keeps (quot, rem, reconstruction proof); `Trace`/`EEATrace` keep
the full Wedge chain; divisibility witnesses `_∣_ = divides q (n ≡ q*m)` keep the
cofactor `q`; the SPPF keeps everything via perfect-recall + no-double-count.
Different folds read the SAME residue-keeping trace for different targets
(gcd-fold, bezout-ℤ, CRT).

**How to apply:** when something looks like it "needs a new division" (e.g. ℚ
`reduce` dividing num/den by their gcd), the cofactor is ALREADY a kept residue —
`gcd-divides-left/right` return `a ≡ q·g`, so `q = a/g` is in hand. Project from
the witness; do not introduce a fresh ℤ÷ℕ/NonZero division. The
"deferred — needs division" framing is usually a residue that was forgotten, not
a missing algorithm. See [[project_sppf_eea_unification]],
[[project_realizability_charter_arc]] (THE RESIDUE IS NEVER DROPPED appears in
Wedge.Product.Laws too).

**REFINEMENT — retention is the FOREST's job, NOT the READOUT's** (BEZOUT_READOUT.md,
jea/metalanguage, 2026-06-17; verified: jea_pyalg.trace is eager). "Retain all
intermediates" describes the STORED structure (the interned SPPF — shared, hash-consed,
why nothing is a digest); it says NOTHING about how you TRAVERSE it. The naive inference
"since everything is retained, the readout may hold it all" is exactly backwards: the read
must keep NOTHING — O(1) streaming, holding only the current step. This is EEA restated:
the forest is the retained division chain; back-substitution STREAMS over it (one step at a
time). Conflating them is a materialization bug (a "SPPF→ABNF" readout that builds a grammar
dict + eager trace() + descend-then-compose trace_fold = a TRIPLE copy of a 50GiB forest,
where zero are needed). The fix: drive the single-step primitive (`wedge`) in a loop and
`yield` (`stream_rhs`); never build an intermediate dict/materialized-Trace/fold-accumulator.
EVERY readout is this backward walk (emit_octave/project_cuda/project_unified/stream_rhs =
"different reads of the same kept trace"); every forward op is obligation-discharge. The one
core change this motivates: **Σ-TRACE-LAZY** — make jea_pyalg.trace/trace_fold lazy
(generator, yield one wedge step) so streaming is the default. Dual of
[[feedback_suspended_generators_not_approximations]] (the generator IS the object; the
forced window is an observation): retention=generator-level, frugality=observation-level.

**THE FRAMING SLIP — "residue is what an external SUPPLIES" (projection) vs "the kept COFACTOR"
(retraction)** (Ⓤ.byte arc, jea_extrude_ir, 2026-06-20). Building the IR→Python unparser I framed
the round-trip's lost data (literal values, field-tags, bound spellings, trivia) as "RESIDUE = what a
byte-grade plugin must SUPPLY" — i.e. external, gone, someone else's job. That is the PROJECTION
framing, and it silently violates this spine. The user caught it: "the residue should be usable for
SOMETHING." Reframed: the residue is the kept COFACTOR; replayed, it lifts the lossy projection into a
lossless **RETRACTION** — `recon(skeleton, residue) == original` = the split-idempotent apex
([[project_split_idempotent_apex]]). The "byte-grade is structurally impossible" verdict was the wrong
frame: the truth is a **GRADE LADDER** of recoveries, each adding a residue layer — skeleton
(projection) ⊕ structural-residue → AST (lossless structure) ⊕ trivia → bytes (lossless layout, trivia
= pure gauge). The recurring tell: a flag about *whether something converges/is faithful/is possible*
is usually "is the residue retained?" — and "lost/needs-a-plugin/can't-recover" is a forgotten cofactor.
Sibling of the "deferred — needs division" slip above; same reflex, framing scale.

**METHOD COROLLARY — validate residue-replay at SCALE on REAL code, not synthetic.** A fail-loud
alignment invariant (the `_pop` tag-assert: capture/replay streams must agree by tag) only BITES when
the diverging records have *different* tags. Synthetic snippets masked an IfExp field-order scramble
(all-Name branches → same 'name' tag → cancelled); a real f-string-in-ifexp exposed it. The whole-tree
run (133 real modules) caught three more (asname collapse, Ellipsis repr, numpy `a[:, l]` slice) that
hand-written cases missed. Pair a fail-loud invariant with a DIVERSE real corpus; synthetic tests
under-sample the tag-space. Twin of [[feedback_validate_outputs_not_inputs]].
