---
name: feedback_dedup_preserve_crossdomain_bridges
description: "Deduping interned parallel material must WITNESS cross-domain bridges (transport maps), never silently collapse — the parallel code IS explicit inter-subsystem wiring."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: a96a1d8c-75ae-47e6-807c-c4988d800d8f
---

When deduping duplicates that jea_pysim (or collapse-check) surfaces, distinguish **within-domain**
dups from **cross-domain** ones. A within-domain dup (three copies of `length`, a local `≤-up` = the
Foundation order lemma) is safe to collapse — the shared import still documents the dependency. A
**cross-domain** dup is NOT a redundancy to delete: it is a **bridge** the interned material made
explicit, and collapsing one side destroys the transport.

**Why.** Much of the z47 / hand-interned parallel material's VALUE is that it makes explicit wiring
between substrate subsystems that were not cleanly connected before — S5Matrix's 2×2 state ↔ the CF
convergent matrix (CFMatrixBridge), S5RealConv's conv-go/twos/sqrt2 ↔ the coinductive reals (Trace.Real),
S5EEA's DivStr instance ↔ Algebra.Wedge, S5TorsorWireV4's KleinV4 ↔ Groups.V4. Each apparent "duplicate
def" (`state`, `_·_`, `twos`, `shape`, `KleinV4`) is a **bridge point**. Collapse it and you lose the
Level-1 relationship (this ≅ that across domains) AND the Level-2 **relationships-of-relationships**: the
consistent pattern across all the bridges — the "S5 is a metacircular reflection of the substrate" story
the corpus tells only when every bridge is preserved as a witnessed transport.

**How to apply.** Model on the `KleinV4 ≅ Groups.V4.V₄` iso (S5TorsorWireV4, commit cdb8be2): keep BOTH
sides, add the witnessed transport (bijection/iso/homomorphism, or at minimum a `refl`-witnessed equality
naming the two domains). The load-bearing-chart check is part of this — if the local side computes
differently (KleinV4's direct Cayley `_·_` is refl-reducible; Groups.V4's is Coxeter-routed), it is
load-bearing and MUST be kept, related-not-replaced (see [[project_z47_migration_cotype]], the v4-unify
lesson). Only collapse when BOTH sides are the same concept in the SAME domain with no bridge crossed —
and even then, let the shared import make the dependency visible. "Demonstrate definitional equality"
(the RIdx≡PIdx witnesses) is the same move at the trivial end: witness, don't silently erase. Related:
[[similarity-not-grep]] (use jea_pysim to FIND them), [[feedback_reuse_search_before_feasibility_conclusions]].

**jea_pysim clusters are CANDIDATES-requiring-audit, NOT auto-collapse targets.** Corroborated by auditing the 4
pre-existing Trace-tree "dups" it flagged: ALL FOUR were false-positives-for-collapse — (a) `bezout-combo≡det4`
was an ALREADY-WITNESSED cross-domain bridge (CFBezoutPrev proves it: Bézout=determinant); (b) `Cancel.bump` vs
`Ops.addℕ` were GENUINELY DIFFERENT (add-to-all vs add-to-head — the non-IDENTICAL score with a hole flagged the
real distinction); (c/d) the two `cover` pairs were ONE shared `cover=ana orbit-coalg` from OrbitCover, `open`ed in
three modules — already factored. Collapsing any would have destroyed a bridge, a distinction, or a shared factoring.
So: read the cluster's IDENTICAL-vs-STRONG score AND the actual defs before acting — an IDENTICAL hit is often an
already-shared/re-exported def (check for `open`/`import`), and a true byte-collapse is the exception.

**A STRONG-orbit-with-hole hit is a PARAMETRIC FAMILY → LIFT it (do NOT dismiss as "genuinely different").** jea_pysim
literally labels these "one parametric concept"; the hole is the parameter. Correcting my own earlier miscall: I saw
Cancel.bump / Cancel.unbump / Ops.addℕ (88%, one hole @ the tail) as "different functions, leave them" — WRONG. They
share `head (F f x) = f (head x)` and differ only in the tail (recurse vs stop). The right move (the user's
find-the-common-structure-recursively reflex) is to lift: `bump=mapT(k+_)`, `unbump=mapT(_∸k)`, `addℕ=onHead(k+_)`,
extracting the generic stream map (Substrate.Algebra.R.Trace.StreamMap) that was genuinely ABSENT (each op reinvented
it). CAVEAT: the hole may not be a clean FUNCTION parameter — coinductive guardedness REJECTS corecursion-through-a-
function (tested: TerminationIssue), so recurse-vs-stop becomes a choice between two guarded copattern generics, but
the shared parameter (the head-function) is still lifted. TEST the parameterization in a scratch module before
concluding it can't be done. "Behaviorally different" ≠ "not liftable" — the shared skeleton is the lift.
