---
name: project_cyclen_opacity_fix
description: Cycle7 OOM root-caused to dense matrix-power normalization in linear-from-images; fixed by opaque boundary on cyclic-Linear/cyclic-HasOrder (OOM→745MB); CycleN dense exports are unused PoCs
metadata: 
  node_type: memory
  type: project
  originSessionId: b0f173b0-7c01-42e2-bd3c-cbed23f2d66a
---

**Root cause of the All.agda / Cycle7 OOM (the "how does term algebra
inflate so much" mystery):** `Cycle7.agda` is 4 thin renamings of the
generic `Cyclic.{cyclic-Linear, cyclic-HasOrder}` at n=6. But
`cyclic-Linear = basis-permutation-Linear (cyclic-suc)` represents an
F₂-linear map as a DENSE sum-of-scaled-vectors (`linear-from-images`,
agda/Substrate/Algebra/F2/Linear/FromImages.agda: apply v = sum (λ i →
lookup v i *ₛ images i)). `cyclic-HasOrder {6}` forces `HasOrder-from-perm`
→ `L-iterate 7` (compose the dense map 7×) + `linear-extensionality`
(evaluate at all 7 basis vectors). Type-checking NORMALIZES a 7×7 matrix
raised to the 7th power in normal form ≈ super-exponential in the cyclic
order → Cycle7 (n=7) explodes while Cycle2–5 don't. The storage is term
algebra; the COST is the normaliser expanding the dense power. Not
load-bound after all — NORMALIZATION-bound, in one pathological file.

**Fix (landed, verified capped):** wrap `cyclic-Linear` + `cyclic-HasOrder`
in an `opaque` block in
agda/Substrate/Algebra/F2/Linear/FromImages/Permutation/Cyclic.agda. They
type-check ONCE generically at abstract n (cheap); a consumer instantiating
at concrete n references them as black boxes and never unfolds the dense
sum / matrix power. The proven basis-level equation
(`basis-permutation-order-k`, O(n), index-level) already sits behind
`HasOrder-from-perm`, so nothing downstream needs the dense form. Same
lesson as def/proof split, one level deeper: hand consumers the lemma, not
the unfolded construction. Verified (systemd cgroup MemoryMax=2G +
agda +RTS -M1500m, graceful): Cyclic green; Cycle7 cold 762 MB / 5 s
(WAS >1 GiB OOM-kill); Cycle3 (only instance with real dense consumers:
cycle3-Linear ×7, HasOrder-cycle3 ×4) green.

**Caveat (honest):** 745 MB warm is still high for 4 renamings — likely
the F2.Linear/Vector/Universal dependency CONE, not residual Cycle7 cost.
The opacity fixed the catastrophe (OOM→finite), not necessarily the cone
size. NOT pursued further (avoid re-OOMing the machine; see careful-
discipline). Could opaque more or the cone is just large — open.

**CycleN are PoCs (consumer census):** dense exports cycle{2,4,5,7}-Linear
and HasOrder-cycle{2,4,5,7} have ZERO external consumers; only Cycle3's do.
The cheap index names σ₂…σ₇ have all the real consumers (3–10 each) — i.e.
downstream wants the PERMUTATION, not the dense linear lift. Follow-up
(def/proof policy, [[feedback_def_proof_separation_lever]]): demote the
dense lift to .Properties / out of default build for the consumer-less
CycleN; keep lean σ_N/σ_N-HasOrderPerm as the def surface; Cycle3 keeps its
dense consumers. Generic closing lemma belongs in Cyclic.agda (it's there:
cyclic-HasOrder, now opaque).

Status: opacity fix landed + verified, NOT yet committed. PoC demotion not
done. Related: [[project_oom_load_bound_finding_2026_06]] (which this
PARTLY corrects — the dominant All.agda cost is this normalization
pathology in specific files, not uniform 40× load inflation).
