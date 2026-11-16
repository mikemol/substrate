---
name: feedback_cluster_means_find_apex
description: "a similarity cluster of look-alike files is evidence to GO FIND THEIR APEX, not evidence they lack one; grep for the assembly before concluding \"no general form exists\""
metadata: 
  node_type: memory
  type: feedback
  originSessionId: b0f173b0-7c01-42e2-bd3c-cbed23f2d66a
---

Twice-confirmed this session (AsFunctor cluster, then S3-on-V4 Hom cluster):
a similarity-checker cluster of N look-alike files almost always means
**they are the LEAVES of an already-built cone**, not N unextracted
duplicates. The apex lives one directory up / under a different name; the
cluster flags the leaves because that's what's textually similar.

**Cases:**
- AsFunctor cluster (20 files) → already project from Functor.AsNamed.
- S3-on-V4 Hom cluster (HomId/HomRot/HomRot²/HomSwap{AB,AG,BG}) → already
  the per-canonical-form LEAVES of an assembled cone:
  leaves → ActHomOnCanonical.act-hom-on-canonical (6-case collector,
  dispatched by Z₃/Z₂ c-pos) → ActHom.act-hom : ∀ s v₁ v₂ →
  IsHomomorphism (act s)  (the faithful general law over S₃.Carrier,
  bridged by normalize-canonical — the Coxeter canonical-form reduction).
  act-hom is LIVE (consumed by S4-Iso, S3, S4-Composed).

**The error I made:** read the leaves, concluded "no general law exists,
building it would be new mathematics," nearly built a multi-file arc that
was ALREADY IN THE TREE. The general law (act-hom) and its collector and
bridge all existed; I looked at the leaves before finding the apex.

**Discipline:** before claiming a cluster needs extraction / a general form
must be built, GREP FOR THE APEX first:
  - the cone witness (*.AsNamed, *-on-canonical collector),
  - the assembled general lemma (act-hom, *-IsHom, the ∀-quantified form),
  - whether the cluster members already `open`/project something shared.
Only if no apex exists is it genuine latent fan-in. Moderate cluster score
(~0.5–0.6) = "share a base correctly" (see
[[discipline/feedback_similarity_not_grep]] usage); the base may already be
named. Cheap check, prevents duplicating finished work.

Related: the substrate's named-categorical-structure-skeletons +
Coxeter-canonical-form machinery exist precisely so general laws over group
elements reduce to finite canonical-case analyses — when you find a cluster
of per-case files, the canonical-collector apex usually already exists.
