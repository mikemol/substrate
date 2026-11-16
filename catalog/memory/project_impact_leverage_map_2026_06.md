---
name: project_impact_leverage_map_2026_06
description: "high-fan-in × improvement-signal leverage map; FromImages (fan-in 213, dense-transparent) is the top opacity target after Cyclic; the dense-linear-map family is the dominant cluster"
metadata: 
  node_type: memory
  type: project
  originSessionId: b0f173b0-7c01-42e2-bd3c-cbed23f2d66a
---

"High fan-in isn't just risk, it's IMPACT" (user). Leverage map = transitive
fan-in (how many modules transitively import m) × an improvement signal.
Computed read-only (/tmp/impact.py logic). Signals: dense-transparent
(defines linear-from-images / basis-permutation / L-iterate WITHOUT opaque
— the Cycle7 OOM disease), defproof (record-exporter importing a proof
module), with-in (≥4 with..in clauses), refl-heavy (≥40 refl), agdai>80k.

**Top targets (fan-in : module : signal):**
- 322  Algebra.F2 : refl-heavy (the F₂ base; refl density may be fine —
  audit, don't assume)
- 213  Algebra.F2.Linear.FromImages : dense-transparent ← TOP OPACITY TARGET
- 129  Groups.V4.Axioms : refl-heavy (64+16 cover-tuples; already minimal
  via v4×v4×v4-cover per generators-catalog — probably fine)
- 95–91 the whole FromImages.Permutation.{Iterate,Linear,IterateLift,
  Order,Involution} cluster : dense-transparent
- 52/49 Category.FreeLinearization{,.FromImages} : dense-transparent
- 42  HodgeDim4.HodgeStar, FanoPlane : dense-transparent
- 21  GL3F2.GaugeGenerators : dense-transparent

**The dominant cluster = the dense-linear-map family.** Same shape as the
Cycle7 fix ([[project_cyclen_opacity_fix.md]]), one level UP at the source:
`linear-from-images` (FromImages.agda:115) defines `apply v = sum (λ i →
lookup v i *ₛ images i)` — the dense matrix as a transparent sum. Every
consumer that normalizes through it pays the (dim)^k expansion. Sealing
`apply` behind `opaque` (exposing apply-linear-from-images-basis /
-lookup) would cut that for the WHOLE family at fan-in 213.

**Sealability of FromImages (consumer census):** 17 modules use the
lemmas (apply-linear-from-images-basis/-lookup) → safe under opacity.
9 "reducers" MENTION `apply (linear-from-images …)` — but on inspection
they are TYPE signatures / proof statements (HasOrder types in
Permutation.{Order,IterateLift,Involution}; adjunction statements in
Category.Adjunction{,/Demos}; TokiPona WithBasisAction) discharged VIA the
lemmas, not by raw reduction. So sealable, BUT delicate: 26 mention-sites
to confirm each routes through the lemma, plus opaque/unfolding placement.
Higher Impact than Cyclic, more care — NOT a charge-in.

**Prime/compound discipline (user's Sylow model,
[[project_cyclen_opacity_fix]] follow-on):** seal the PRIME (the dense
atom — linear-from-images.apply), keep COMPOUNDS transparent (reduce
through, halt at primes), use `opaque unfolding` at fiber-trace sites.
FromImages.apply IS the prime here.

**Recommended order when pursued (each: capped, make -j4, verify batch):**
1. FromImages: seal `apply` (or the record) opaque; confirm the 17 lemma
   users + 26 mention-sites green. Biggest single win (fan-in 213,
   fixes the dense family at the source — would have prevented Cycle7
   structurally).
2. Category.FreeLinearization{,.FromImages}: same pattern, fan-in 49–52.
3. Audit refl-heavy F₂ / V4.Axioms — likely already minimal (cover-tuples);
   confirm before touching.

PROGRESS:
- 48933ab — Cycle7 / cyclic-Linear opacity (the n-level instance).
- d436788 — FromImages SEALED (the source, fan-in 213). linear-from-images
  + apply-linear-from-images-{lookup,basis} wrapped in one opaque block;
  sum-F₂-basis-collapse moved above it. Verified green across 24+ consumers
  capped (Permutation.* cluster, Adjunction(+Demos), GL3F2, HodgeStar,
  FanoPlane, FreeLinearization, Generators, Coxeter.Cyclic chain, TokiPona).

MEASURED METRICS (cold, capped, like-for-like A/B by reverting the file):
- HodgeStar alloc 833 MB → 756 MB ≈ 9% (NOT 70% — an earlier number
  compared cold-pre vs warm-post, invalid; corrected). Real but MODEST.
- FromImages seal does NOTHING for Cycle7: Cycle7 routes through the
  opaque cyclic-Linear, not the dense linear-from-images path. The commit
  message's "would have prevented Cycle7" is OVERSTATED — the cyclic seal
  (48933ab) is what protects Cycle7; FromImages protects OTHER dense
  consumers (HodgeStar/Fano) modestly.
- Cycle7 itself: OOM-kill → 762 MB peak RSS, but still allocates ~2321 MB
  of churn (GC reclaims ⅔). Opacity stopped RETENTION catastrophe, not
  allocation. Heaviest file by far; cheaper-not-just-survivable is open.
HONEST VERDICT: the big metric win is Cycle7 catastrophe→finite (cyclic
seal). FromImages seal = correct + worth keeping but ~single-digit-%
allocation trims on non-cyclic dense consumers, not a sweeping reduction.
Always A/B cold-vs-cold (warm caching invalidates comparisons).
- FreeLinearization (fan-in 49–52): NO ACTION NEEDED — it holds no dense
  apply of its own; it wraps linear-from-images + apply-...-basis, both now
  sealed. The compound was fixed for free by sealing the prime. Verified
  green. (Confirms the prime/compound model: seal the prime, compounds
  inherit.)

REMAINING on the map:
- HodgeStar / FanoPlane / SelfDual / HodgeDim3.* (fan-in 26–42,
  dense-transparent): check whether they DEFINE their own dense apply or
  (like FreeLinearization) just wrap linear-from-images. If wrappers →
  already covered; if they build their own dense map → seal that.
- refl-heavy F₂ (322) / V4.Axioms (129): AUDIT — user expects real fixes
  here. V4.Axioms is cover-tuples (likely minimal); F₂ base needs a look.
- Still on the board: anchor rename (sylow {n} / Sylow-N) + CycleN
  demotion (~85 sites), separate arc.
