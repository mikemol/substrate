---
name: feedback_opacity_tracks_blowup_not_layer
description: "opaque boundary belongs at operations whose normal form grows super-linearly (×, ^, tetration) — NOT addition; refines opaque-by-default to track blow-up rate, not module layer"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: b0f173b0-7c01-42e2-bd3c-cbed23f2d66a
---

User refinement to the opaque-by-default direction: opacity should track
NORMAL-FORM BLOW-UP RATE, not module layer.

- `_+_` : linear; `2+3 ⇝ 5` cheap; thousands of idiomatic refls depend on
  it reducing. KEEP TRANSPARENT. (User: "I don't know that _+_ should be
  opaque.")
- `_*_` (quadratic), `_^_` (exponential), tetration (non-elementary):
  a single concrete instance explodes the normal form. SEAL THESE. (User:
  "multiplication, powers and tetration probably should.")

**Why this is the right line:** both OOM/regression bugs this session were
POWERS being normalized — Cycle7 (matrix^7 via cyclic-HasOrder) and
SingerOrder (HasOrder-singer = iterate 7 = singer-Linear^7 by refl). The
boundary belongs at the super-linear operation, at its source, so concrete
instances reference it instead of grinding the power. Addition is the
computational floor; multiply-and-up is sealed.

**Relation to opaque-by-default** ([[project_cyclen_opacity_fix]] /
the dense-matrix seals): the cut is NOT "Foundation transparent / derived
opaque" (my earlier framing) — it's "linear transparent / super-linear
sealed." More principled: it predicts exactly which definitions blow up.
Needs the usual `unfolding`-on-demand escape for the rare site that
genuinely needs e.g. 2*3 ⇝ 6 in a refl.

Open: a linter could flag a transparent definition whose body applies
_*_/_^_ to a recursively-built argument (the blow-up shape). Not built.
Related: [[feedback_def_proof_separation_lever]], [[feedback_common_substructure_recursively]].
