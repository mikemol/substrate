---
name: feedback_sparse_concrete_transparent_metadata
description: deeper frame over opacity — represent operators sparsely (eliminate blow-up) with transparent metadata + opaque-on-demand dense concrete; Dyck-boundary effect via characterizing lemmas; unifies opacity/sparse/SPPF-interning
metadata: 
  node_type: memory
  type: feedback
  originSessionId: b0f173b0-7c01-42e2-bd3c-cbed23f2d66a
---

User's PL-design frame unifying the session's opacity work. Opacity HIDES
normal-form blow-up; the deeper move ELIMINATES it via representation.

**Three ideas, by feasibility:**

1. Dyck-respecting opacity ("operation opaque, children transparent
   positionally"). NOT a language feature — Agda `opaque` is
   per-definition, not per-occurrence. BUT the characterizing-lemma
   pattern recovers the effect: `apply-linear-from-images-basis`
   (apply (lfi f) (basis i) ≡ f i) seals the dense interior while
   exposing the leaf/boundary behavior. The lemma IS the Dyck boundary;
   we build it by hand per operation.

2. SPARSE concrete = the prize. A permutation matrix is sparse (7 ones in
   49); its dense `linear-from-images` form normalizes all 49 and a power
   expands hugely before collapsing. The INDEX form (cyclic-suc : Fin n →
   Fin n ; singer : Point → Point) IS the sparse representation —
   composition stays a permutation, order is cheap refls on a finite
   type. Both session bugs (Cycle7, SingerOrder) were FAILURES TO STAY
   SPARSE: they materialized + normalized the dense matrix. The fixes
   (index-level proofs via HasOrder-from-perm / singer⁷-id +
   linear-extensionality) ARE the sparse computation. Deep fix = define
   *-Linear sparsely-by-construction; derive dense `apply` opaquely
   on demand. Substrate ALREADY has the sparse machinery (HasOrder-from-
   perm = "prove order on sparse index form, transport to dense via the
   basis lemma"); the bugs were not using it.

3. "Transparent metadata / opaque concrete" records: achievable + partly
   present. HasOrder, Commute, the "six universal-property views of ★"
   are transparent metadata about a heavy concrete map. Make it
   systematic: reason about properties without touching the concrete.

**Encoding caveat + USER CLARIFICATION:** "RLE for *" was NOT really about
a compression codec — it was about TRANSPARENT METADATA and LAZY EVALUATION.
The real point: an operator result should be a node with transparent
metadata (dims, order, is-permutation, HasOrder) over an UNFORCED concrete
core — concrete entries deferred until a coordinate is demanded. Sparse
representation is one instance; the general idea is metadata-interface +
lazy concrete. (RLE/sparse codecs are per-operation incidentals.)

KEY INSIGHT: in Agda, `opaque` IS lazy-evaluation-with-metadata-interface.
Agda's checker is EAGER (it forces concrete normal forms to decide
definitional equality — exactly why dense matrices blew up: refl forced
them). `opaque` is the lever that makes it lazy across a boundary. So "I
want lazy concrete here" and "I want this opaque" are THE SAME REQUEST in
Agda — opacity is how you buy laziness from an eager checker; the seal IS
the laziness. metadata = lemmas exported from the opaque block; lazy
concrete = the sealed body, forced only at `unfolding` sites. Interning
falls out free (unforced equal-spine thunks are shareable — why
cyclic-Linear {6} was refl-equal across modules).

ACTIONABLE DISCIPLINE (the real work): every sealed operator should export
ENOUGH metadata lemmas that no consumer needs to `unfolding` it. SingerOrder
needed the bridge only because linear-from-images exported apply-on-basis
and stopped — no "order / action-on-point" metadata. The seal is cheap;
the METADATA INTERFACE is the work, and its completeness determines whether
laziness holds or leaks (a consumer forced to unfolding = a metadata gap).

**Unification:** opacity, sparse representation, and SPPF-interning (the
earlier "build V_2 once, reference it") are ONE architecture from three
angles. Sparse concrete is interning-friendly (cyclic-suc {6} is one
definitionally-equal shared node — measured); the dense record is not.
Sparse → eliminates blow-up AND gives sharing AND gives transparent
metadata.

DEFENSIVE (done this session): opaque-by-default, seal super-linear ops
([[feedback_opacity_tracks_blowup_not_layer]]). OFFENSIVE (this frame, not
yet built): sparse-by-construction operators, dense materialized opaquely
on demand. More work; eliminates rather than contains. Related:
[[project_cyclen_opacity_fix]], [[feedback_common_substructure_recursively]].
