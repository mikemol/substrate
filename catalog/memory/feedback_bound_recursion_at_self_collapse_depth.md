---
name: feedback_bound_recursion_at_self_collapse_depth
description: "a graded/recursive quotient over the SPPF terminates by the domain's OWN self-collapse depth (the rig precomputes coherence to depth 3, then collapses back into the SPPF) — bound there, and never per-item-query-and-deep-recurse"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: d35bc15a-16b8-42c5-aad1-20966c9a9f8e
---

When computing a recursive/graded quotient over the SPPF (orbit keys, similarity, a fixpoint over the
def-dependency DAG), the recursion terminates by the **domain's own self-collapse depth** — do not recurse
arbitrarily deep, and do not issue a DB query per item while recursing.

**The semantic bound (the user's insight, load-bearing):** the rig category **precomputes coherence out to
depth 3**; beyond that it **collapses back into the SPPF** (the content-addressed interner). At PRIME grades
the ⊗-braidings are trivial (⟨braid⟩=Cₙ⊊Sₙ, `OrientationRigCatPermGap`); composite grades reach Sₙ via the
`blockSum` bifunctor; `PrimeFactoredGauge` is the multiplicative decomposition. So the graded orbit-key
fixpoint is bounded at **depth 3**: past it, a reference keys as its SPPF (positional, already-interned)
identity. This is not a truncation/perf-hack — it is the correct semantics (the coherence IS finite because
the tower self-collapses at the primes). `jea/metalanguage/graded_orbit.py orbit_key(depth=3)` implements it.

**The perf class it also fixes (recurring — see [[feedback_sql_declarative_over_materialized_enumeration]]):**
the first cut deep-recursed with a per-qname `unit_locus` DB query at every node → 2-minute timeout. Same
root as the pickle-cache tell: treating the DB as a per-item lookup instead of preloading + working in
memory. The fix is BOTH: (a) preload the whole index in one query (`unit_index` → {qname: (core,root_lid)}),
cache each core once; (b) bound the recursion at the self-collapse depth. A per-item-query-and-deep-recurse
loop is the tell to stop and do both.

**How to apply:** a graded/recursive SPPF computation ⇒ preload the index (one query), cache cores, and cap
the recursion at the coherence/self-collapse depth (3 for the rig orbit); deeper references collapse to
their SPPF identity. Verify it terminates fast (the distrib-family graded key went 2m→3.5s).

Relates to [[feedback_sql_declarative_over_materialized_enumeration]], [[free-universal-property]],
[[witness-tower-constructive-generator]].
