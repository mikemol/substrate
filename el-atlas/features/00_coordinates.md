# EL-Atlas — AWGT coordinate classification

Axis set (fixed): `layer ∈ {topos, governance, ladder, bootstrap, typethy, groupoid, testing, meta}`,
`role ∈ {local, invariant, cross-cutting}`, `depth = 1 + max(prereq depth)` (base 0).

Mapping of the eight layers onto this spec's structure (cited, not asserted):
- **bootstrap** — the primitive carrier and charts (§1, §2): the base objects everything else is built from.
- **governance** — the prohibition and its discipline (§3): governs admissibility of every read/projection.
- **groupoid** — the involutions and the adjunction (§2 Lemma 2.4/2.5b, §5): invertible structure, V₄, exp⊣log.
- **ladder** — the basis change, semiring, range, consumption modes (§4, §6, §7, §13): the graded build-up.
- **typethy** — the amplitude/coefficient reading (§8): the coefficient-system typing.
- **topos** — the overlay principle (§12): gluing/pushout, the sheaf-theoretic layer.
- **testing** — the circuit witnesses and instrument (§11): the witnessed/runnable correspondences.
- **meta** — the obligation register and provenance (§14, §15): claims about the spec's own claims.

| coordinate | concept (one sentence) | layer match criterion | role | depth (computation) | prerequisites | file |
|---|---|---|---|---|---|---|
| `bootstrap_local_0_carrier` | The carrier is an independent (E⁺,E⁻) pair of additive accumulators, never cross-read. | base objects of §1; nothing precedes them | local | 0 (no prereq) | — | `bootstrap_local_0_carrier.feature` |
| `bootstrap_invariant_1_atlas` | The two charts are one object related by exp⊣log; negation is chart-local (−u on 𝔸, 1/y on the semiring 𝕄). | §2 builds on the carrier; an equivalence preserved across charts | invariant | 1 = 1+max(0) | carrier | `bootstrap_invariant_1_atlas.feature` |
| `governance_cross-cutting_2_prohibition` | No quotient to a ratio/odds; every projection is named & external; collapse ≠ chart-image. | §3 governs admissibility of all reads across all layers | cross-cutting | 2 = 1+max(1) | atlas | `governance_crosscutting_2_prohibition.feature` |
| `ladder_local_2_crossbar` | (mass,bias)=(E⁺+E⁻, E⁺−E⁻); B/N are the mass-axis ends, T/F the bias-axis ends. | §4 change of basis on the carrier | local | 2 = 1+max(1) | atlas | `ladder_local_2_crossbar.feature` |
| `groupoid_invariant_3_involutions` | V₄ = {negate-pin, pin-swap}; pin-swap = De Morgan; NOT(AND)≡OR needs inverse-lock + two ops. | §5 invertible involution group; preserved structure | invariant | 3 = 1+max(2) | crossbar | `groupoid_invariant_3_involutions.feature` |
| `testing_invariant_3_wheatstone` | Galvanometer-null = pin-swap fixpoint, same locus across the adjunction (chart-image ratio, not collapse). | §11.3 witnessed instrument; an invariant of the balance locus | invariant | 3 = 1+max(2,2) | crossbar, prohibition | `testing_invariant_3_wheatstone.feature` |
| `groupoid_invariant_3_noether` | Pin-swap⊣squeeze conserve mass; negate-pin⊣translation conserve bias (the two Noether charges). | §11.8/OB-7 symmetry↔invariant pairing | invariant | 3 = 1+max(2) | crossbar | `groupoid_invariant_3_noether.feature` |
| `ladder_cross-cutting_3_consumption` | Five consumption modes graded by RM degree; accumulate/transport lossless, project/gate lossy, overlay constructive. | §13 spans all layers (how any value is consumed) | cross-cutting | 3 = 1+max(2) | prohibition | `ladder_crosscutting_3_consumption.feature` |
| `topos_cross-cutting_4_overlay` | Glue two networks on shared S; computation transmits modulated by S; the overlay is the bilinear product (climbs RM). | §12 pushout/sheaf layer; affects multiple layers | cross-cutting | 4 = 1+max(3) | consumption | `topos_crosscutting_4_overlay.feature` |
| `meta_invariant_1_register` | Each obligation is an (evidence-for, evidence-against) pair held live; resolved/open/retracted are tracked states. | §14/§15 claims about the spec's own claims | invariant | 1 = 1+max(0) | carrier | `meta_invariant_1_register.feature` |

Notes:
- `bootstrap_invariant_1_atlas` carries the draft-10 correction (two involutions on two algebras) and the adjunction (Lemma 2.5b) — both are faces of the same atlas obligation.
- `governance_cross-cutting_2_prohibition` is the keystone; Lemma 3.2 (ratio-blindness) and Remark 2.5c (collapse vs chart-image) are its declared faces.
- Open obligations (OB-1 range, OB-2/OB-9 phase, OB-3 contradiction-link) appear as **`@open` / `@undetermined`-tagged scenarios**, not omitted — a scenario whose status the spec marks open is a real cell, per the obligation-register discipline.
