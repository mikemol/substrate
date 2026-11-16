---
name: feedback_governing_law_before_special_case
description: "model a domain via its GOVERNING LAW first; the algebra you'd reinvent is a special-case reduction of it, and its \"limits\" are theorems not empirical discoveries"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: c1329ff9-896f-4600-8952-67ec237e5bbc
---

When modeling a domain, reach for the established LAW that governs it (the physics/math —
Kirchhoff for conductance networks, KCL/Noether conservation, the universal property) BEFORE
building empirical special-case witnesses. The operation you'd otherwise take as primitive
(e.g. G_OR=ΣG, G_AND=harmonic) is usually a special-case REDUCTION of that law; once you start
from the law, the operation's domain-of-validity and "limits" are THEOREMS, derivable a priori,
not things to rediscover by experiment.

This session (kernel-perf nedge arc, 2026-06-14): I took G_OR/G_AND as primitive and
empirically DISCOVERED "parallel-sum breaks under a shared resource" (branch-independence pilot,
after hitting the 512² L2→shared-L3 confound by trial-and-error). The user flagged it: "should
have been a given — evaluating G_OR properly requires Kirchhoff and Noether." It was: G_OR/G_AND
are the parallel/series reductions of the nodal solve; the shared-resource cap = G_AND(k·g,c) is a
KCL theorem; "all graphs reduce, in the right order" (Kron/Schur node elimination, order = cost
gauge / answer invariant). Built in kirchhoff_nedge.py + kron_reduction.py AFTER correction.

**Why:** foundation-first makes the special cases fall out by construction AND catches confounds a
priori — the breaker auto-survey would have flagged the 512² spill before I ran it. The recurring
failure is bottom-up (special→general, corrected late) when the principled path is top-down
(law→special cases). Sibling of [[feedback_universal_property_discipline]],
[[feedback_categorical_name_first]], [[feedback_expose_generator_not_orbit]],
[[feedback_cluster_means_find_apex]] — same apex/generator-first family, generalized from
category theory to physical/mathematical governing laws.

**How to apply:** before building a domain model, ask "what established law GOVERNS this, of which
my proposed operation is a special case?" Build the law (the solver / the universal property);
derive the ops as its reductions. If you find yourself empirically discovering an operation's
limits, stop — the limit is almost certainly a theorem of a law you skipped.
