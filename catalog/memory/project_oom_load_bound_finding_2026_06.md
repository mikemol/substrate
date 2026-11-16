---
name: project_oom_load_bound_finding_2026_06
description: "CONFINED All.agda probe proves the OOM is LOAD-bound (deserializing cached interfaces), not check-bound; distribution is FLAT not power-law; lever is closure-size/import-graph, not per-module proof cost"
metadata: 
  node_type: memory
  type: project
  originSessionId: b0f173b0-7c01-42e2-bd3c-cbed23f2d66a
---

Ran All.agda under hard cgroup caps (systemd-run --user --scope -p
MemoryMax=… -p MemorySwapMax=0, plus agda +RTS -M… inner guard). SAFE
way to probe the OOM: it dies cleanly at the cap, machine never pages.
agda honors +RTS -M (graceful heap-exhausted exit). Reusable harness.

**DECISIVE FINDING — the OOM is LOAD-bound, not check-bound:**
- At 256 MB cap: All.agda dies with ZERO "Checking" lines — OOMs purely
  DESERIALIZING cached .agdai interfaces, before checking any module.
- At 1024 MB cap: only ~20 "Checking" lines, all shallow; the rest of the
  GB is loaded interfaces.
- Inflation ratio ≈ 40×: 26.2 MB of serialized .agdai (1219 interfaces)
  → 1 GB+ resident. Standalone, PrimitiveInstances (384 KB .agdai) needs
  317 MB peak RSS alone. In-memory term representation is ~40× the
  serialized form, per module, and All.agda forces the whole closure
  co-resident.

**REFUTES earlier framing (mine):** the cost is NOT a power law with a fat
head, and NOT dominated by per-module proof complexity. Distribution is
FLAT: mean 22 KB, median 16 KB, top-20 only 8.8%, top-200 41.4% of the
26 MB closure. It is ~1219 modules × ~22 KB, all co-resident. So the
Stab-S3-Extend β-migration (933→531 MB alloc) was a real per-module win
but is NOT the dominant OOM lever — the lever is CLOSURE SIZE × per-module
inflation, i.e. the import graph.

**Reconciliation with [[project_oom_memory_profile_2026_06]]:** that
profile (case-count drives per-module ALLOCATION) stands — it's about
checking-time allocation. This finding is about RESIDENT memory at
aggregate-load time. Two different costs: β-laws cut allocation (faster,
less GC churn) AND shrink .agdai (less to deserialize), so the lever still
helps — but the FIRST-ORDER OOM driver is "All.agda co-loads 1219
interfaces at ~40× inflation."

**Actionable levers, in power-law order (biggest first):**
1. DON'T co-resident the whole closure. All.agda is the problem by
   construction; a partitioned/sharded build (check subtrees separately,
   never one process) avoids the 40× × 1219 product. This is the dominant
   fix and needs no proof edits. [[feedback_never_build_all_agda]] already
   says never build it locally; this explains WHY mechanically.
2. Shrink the closure: 1213 .agda files, 1081 imported by ≥1 other. Prune
   redundant transitive imports; many Capstone/Manifest aggregators may
   pull modules that are already transitively present.
3. Per-module .agdai shrink (β-laws over enumeration, generators over
   bespoke): second-order — helps deserialization linearly, and the
   enumeration family (Coxeter/Stab/S4Iso/GL3F2/Hodge) is ~39.5% of the
   closure, so it's worth ~10 MB of the 26 MB if fully collapsed. Good,
   but smaller than (1).

**Antipattern census (per-module shrink targets, by .agdai KB):**
PrimitiveInstances 385, V4-Coxeter 148, Charter 141 (MINE — cube), Generators
120, Manifest 110, PrimitivesAll 107, ConjugationCoalgebra/Simplicity 105
(untracked, not mine), Z3-Coxeter 103, CoxeterFin 101, Zn-Coxeter-Fin ~88×5.
with-in clause hogs: Stab-S3-Hom 12, OrbitKey-S3/SFinRoundTrip 7,
S4Iso/Cases 6. refl-tuple hogs: V4/Axioms 105 refls, Stab-S3-Hom 74.
