# The EL-Atlas, Structured Edition

*Mechanically derived by `tools/el-atlas-structured-gen.py` from the v3.1 harness.*
*All verdicts indexed: space **S_703c582017c8** (663552 models, exhaustive); manifest below.*
*Hand-written content: claim metadata sentences and spec pointers only.*

**Space manifest S_703c582017c8:** pins ∈ {1, 2, 3}; adj ∈ {True, False}; ident ∈ {True, False}; neg ∈ {True, False}; ops ∈ {diagonal, linear}; lock ∈ {available, unavailable, wrong, clipped, affine, noisy, partial, forced}; norm ∈ {free, pinned, pinned_l2}; two_ops ∈ {True, False}; basis_def ∈ {ok, singular}; coeff ∈ {real, gf2, complex}; cdlevel ∈ {2, 4, 8, 16}; probe ∈ {full, depth1, mention}; extclass ∈ {d4, q8, z4xz2, split}.
*Why this space: no knob is a-priori — each was admitted by a named correction*
*event (KNOB_PROVENANCE in the harness); knobs are monotonic. Intrinsic verdicts*
*below carry a frontier: what a separator would require, and at which scrutiny*
*stratum the residual openness lives.*

**Legend:** P = visible/true from that vantage; F = false there; U = observable but
undecided; V = not statable there. Dependence edges arise from F and V only —
undecided is not destroyed. Circle verdicts carry their space index and ledger.

**Proof tier:** EMPTY — reserved: the Agda rung. [W]-by-sample != [W]-by-proof (external evaluator fork, verified); lineage: the source's KernelProver / parse-as-constructive-proof (proc1).

Every claim below carries its fiber certificate, executed at generation time: the edition is proof-carrying (B2) — no witness-stratum IOU survives to this artifact; the proof tier is the registered empty.

## Table of Contents

**Part 1 — Layer 0 (foundations)**
- [The chart adjunction (exp ⊣ log)](#the-chart-adjunction-exp--log)
- [The braided V₄ (D₄)](#the-braided-v4-d4) *(characteristic-break coincidence; separated in-space)*
- [The third codec sighting ≡ The radial schedule ≡ The radial witness mode ≡ The zero-divisor schedule ≡ The zero-divisor witness mode](#the-third-codec-sighting) *(one structure — expressibility-intrinsic)*
- [The G-value lift ≡ The exact V₄](#the-g-value-lift) *(one structure — expressibility-intrinsic)*
- [The Noether pairings](#the-noether-pairings) *(characteristic-break coincidence; separated in-space)*
- [The ∨E bridge](#the-∨e-bridge) *(characteristic-break coincidence; separated in-space)*
- [Order-free semiring parsing](#order-free-semiring-parsing) *(characteristic-break coincidence; separated in-space)*
- [Semiring-weighted parsing](#semiring-weighted-parsing) *(characteristic-break coincidence; separated in-space)*
- [The twist](#the-twist) *(characteristic-break coincidence; separated in-space)*
- [The identity-collapse schedule](#the-identity-collapse-schedule)

**Part 2 — Layer 1**
- [The balance channel](#the-balance-channel) *(characteristic-break coincidence; separated in-space)*
- [The codec contract](#the-codec-contract) *(characteristic-break coincidence; separated in-space)*
- [The crossbar](#the-crossbar)
- [The two-gate theorem](#the-two-gate-theorem) *(characteristic-break coincidence; separated in-space)*
- [The sphere prohibition](#the-sphere-prohibition) *(characteristic-break coincidence; separated in-space)*
- [The prohibition ≡ The differential purchase](#the-prohibition) *(one structure — expressibility-intrinsic)*
- [The involution coincidence ≡ The classical section](#the-involution-coincidence) *(one structure — truth-intrinsic)*
- [The classical rails](#the-classical-rails) *(characteristic-break coincidence; separated in-space)*

**Part 3 — Layer 2**
- [The De Morgan requirements](#the-de-morgan-requirements)
- [The phase support theorem](#the-phase-support-theorem)


---


# Part 1 — Layer 0 (foundations)


## The chart adjunction (exp ⊣ log)

**ADJ — The chart adjunction (exp ⊣ log)** (§2, Lemma 2.5b). The two per-pin charts — semiring magnitudes and the signed line — form an adjoint equivalence; the codec pair whose round-trips are identities.

*Certificate (guard)*


*Perspective visibility — ADJ (executed, S_703c582017c8 configs):*

| FULL | P1 | P2-I | CLASSICAL | PROB | NO-CODEC | NO-ANCHOR | ONE-OP | NO-NEG | SING-BASIS | NOISY-LOCK | CHAR-2 | SEDENION | SPHERE | MENTION | COMPLEX |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P | P | P | P | P | F | P | P | P | P | P | P | P | P | P | P |

*Cross-reference — ADJ:* depends on —; required by ['BAL']; independent of 25 claims (CDC, CRS, PUR, PRO, LOC…).


## The braided V₄ (D₄)

**D4C — The braided V₄ (D₄)** (Theorem 5.4, Remark 5.5). Composed reading licenses the swap; ⟨negate-one, swap⟩ = D₄, the central extension of V₄ by the reversible twist [N,S] = −id.

*Certificate (guard)*

*Characteristic-break coincidence with ['GCX', 'NGL', 'NOE', 'NVE', 'RAD', 'RDW', 'SWF', 'SWP', 'TWN', 'V4I', 'ZDG', 'ZDW'] (shared break in the dep digraph); separated in-space — see ledger.*

*Separation ledger D4C–TWN:* separated-in-S_703c582017c8 (18432 truth-separators); unseparated, co-movement 1.00 (partly by construction) @ S_94763a8b62ea (v3.3); unseparated 1.00 (partly by construction) @ S_fd5ddbe7ac57 (v3.4a); 0/0 truth circle; rung-2 strict containment computed in-run — the admission's correction event @ S_d0ede8d60ddb (165888, v3.9.0 pre-admission).


*Perspective visibility — D4C (executed, S_703c582017c8 configs):*

| FULL | P1 | P2-I | CLASSICAL | PROB | NO-CODEC | NO-ANCHOR | ONE-OP | NO-NEG | SING-BASIS | NOISY-LOCK | CHAR-2 | SEDENION | SPHERE | MENTION | COMPLEX |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P | V | V | P | P | P | P | P | V | P | P | F | P | P | P | V |

*Cross-reference — D4C:* depends on ['GCX', 'NGL', 'NOE', 'NVE', 'RAD', 'RDW', 'SWF', 'SWP', 'TWN', 'V4I', 'ZDG', 'ZDW']; required by ['NVE', 'NVL', 'PHS', 'PR2', 'PRO', 'PUR', 'TWN']; independent of 9 claims (ADJ, BAL, CDC, CRS, LOC…).


## The third codec sighting ≡ The radial schedule ≡ The radial witness mode ≡ The zero-divisor schedule ≡ The zero-divisor witness mode — one structure

**GCX — The third codec sighting** (corpus-sweep §6 (S4); §5.8). GALAXY's W ↔ ASPF's log-decode: the exponential codec is exact on the rank-sum quotient, and the quotient genuinely collides — GALAXY is a one-mode decode of the ASPF carrier.

*Certificate (mixed: sampled(500) identities + exact collision witness)*: collision computed live: alpha-shadow 0.168070 == 0.168070; prime carrier 2*7=14 != 3*5=15

**RAD — The radial schedule** (§5.9). The CD pinning's quadratic norm is multiplicative exactly through the octonion rung (Hurwitz); radial multiplicativity is a sacrifice-ladder rung.

*Certificate (sampled(40) — _rad_mult_ok, self-declared '(sampled)')*

**RDW — The radial witness mode** (§5.9; theory-threads §14 (T2)). Pi-form: the excess-mode schedule — norm-failure-beyond-the-kernel is empty through the octonions, inhabited from the sedenions; the witness is the section over rungs (a 1-path), displayed as cdlevel-inertness.

*Certificate (sampled(60+60+30) across fibers)*

**ZDG — The zero-divisor schedule** (§5.9 (Z-series)). Zero divisors first appear at the sedenion rung and are enumerated, oriented geography (dim 2ⁿ−5, G₂); in characteristic 2 they appear at every rung — the schedule is a char-0 fact.

*Certificate (cited-theorem(dim<16: composition algebras) + witness-search(dim 16))*

**ZDW — The zero-divisor witness mode** (§5.9; theory-threads §14 (T2)). Pi-form: the kernel-mode schedule — det L_x locked to N^(d/2) through the octonions (kernel empty), unlocked at the sedenions (kernel inhabited, contained in norm-failure); the lock schedule IS the content.

*Certificate (mixed: exact witness (N(xy)=0.0) + sampled(30) lock)*: (e1+e10)(e4-e15): N(xy) = 0.0 exactly, N(x)N(y) = 4

*Verdict (S_703c582017c8, exhaustive): EXPRESSIBILITY-INTRINSIC — zero separators; co-movement 442368/442368 = 1.00; but GCX, RAD, RDW, ZDW is never F anywhere in the space: a theorem, truth-stable wherever statable. Mutual constitution at the statability level, one-way at the truth level: interventions de-state the theorem rather than falsify it. ∀-over-declared-spaces; open-by-design.*

*Separation ledger GCX–SWP:* separated-in-S_703c582017c8 (0 truth-separators); unseparated in truth, 0/18432; kind counts carry the blanket-guard semantics @ S_f117b7f53a8e (165888, v3.5 first form — central complex V-guard overrode declared knob support; Break-2 coeff rows artifactual; retrospective R-V35); unseparated in truth 0/18432; theorem-cluster member @ S_2738ddb8c926 (165888, v3.5a corrected).


*Perspective visibility — GCX (executed, S_703c582017c8 configs):*

| FULL | P1 | P2-I | CLASSICAL | PROB | NO-CODEC | NO-ANCHOR | ONE-OP | NO-NEG | SING-BASIS | NOISY-LOCK | CHAR-2 | SEDENION | SPHERE | MENTION | COMPLEX |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P | P | P | P | P | P | P | P | P | P | P | V | P | P | P | V |

*Perspective visibility — RAD (executed, S_703c582017c8 configs):*

| FULL | P1 | P2-I | CLASSICAL | PROB | NO-CODEC | NO-ANCHOR | ONE-OP | NO-NEG | SING-BASIS | NOISY-LOCK | CHAR-2 | SEDENION | SPHERE | MENTION | COMPLEX |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P | P | P | P | P | P | P | P | P | P | P | V | P | P | P | V |

*Perspective visibility — RDW (executed, S_703c582017c8 configs):*

| FULL | P1 | P2-I | CLASSICAL | PROB | NO-CODEC | NO-ANCHOR | ONE-OP | NO-NEG | SING-BASIS | NOISY-LOCK | CHAR-2 | SEDENION | SPHERE | MENTION | COMPLEX |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P | P | P | P | P | P | P | P | P | P | P | V | P | P | P | V |

*Perspective visibility — ZDG (executed, S_703c582017c8 configs):*

| FULL | P1 | P2-I | CLASSICAL | PROB | NO-CODEC | NO-ANCHOR | ONE-OP | NO-NEG | SING-BASIS | NOISY-LOCK | CHAR-2 | SEDENION | SPHERE | MENTION | COMPLEX |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P | P | P | P | P | P | P | P | P | P | P | F | P | P | P | V |

*Perspective visibility — ZDW (executed, S_703c582017c8 configs):*

| FULL | P1 | P2-I | CLASSICAL | PROB | NO-CODEC | NO-ANCHOR | ONE-OP | NO-NEG | SING-BASIS | NOISY-LOCK | CHAR-2 | SEDENION | SPHERE | MENTION | COMPLEX |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P | P | P | P | P | P | P | P | P | P | P | V | P | P | P | V |

*Cross-reference — GCX:* depends on ['NGL', 'SWF', 'TWN']; required by ['D4C', 'NGL', 'NVE', 'NVL', 'PHS', 'RLS', 'SWF', 'SWP', 'T53', 'TWN', 'V4I']; independent of 11 claims (ADJ, BAL, CDC, CRS, PUR…).

*Cross-reference — RAD:* depends on ['NGL', 'SWF', 'TWN']; required by ['D4C', 'NGL', 'NVE', 'NVL', 'PHS', 'RLS', 'SWF', 'SWP', 'T53', 'TWN', 'V4I']; independent of 11 claims (ADJ, BAL, CDC, CRS, PUR…).

*Cross-reference — RDW:* depends on ['NGL', 'SWF', 'TWN']; required by ['D4C', 'NGL', 'NVE', 'NVL', 'PHS', 'RLS', 'SWF', 'SWP', 'T53', 'TWN', 'V4I']; independent of 11 claims (ADJ, BAL, CDC, CRS, PUR…).

*Cross-reference — ZDG:* depends on ['NGL', 'SWF', 'TWN']; required by ['D4C', 'NGL', 'NVE', 'NVL', 'PHS', 'RLS', 'SWF', 'SWP', 'T53', 'TWN', 'V4I']; independent of 11 claims (ADJ, BAL, CDC, CRS, PUR…).

*Cross-reference — ZDW:* depends on ['NGL', 'SWF', 'TWN']; required by ['D4C', 'NGL', 'NVE', 'NVL', 'PHS', 'RLS', 'SWF', 'SWP', 'T53', 'TWN', 'V4I']; independent of 11 claims (ADJ, BAL, CDC, CRS, PUR…).


## The G-value lift ≡ The exact V₄ — one structure

**NGL — The G-value lift** (§5.7e, nedge-decomposition §6). Nedge's G-Value Calculus is ⟨fraction-addition, swap⟩ on formal-quotient pairs — the carrier quotiented by the diagonal; non-idempotence is the mass-growth shadow; resource sensitivity is the quotient remembering the extruded axis.

*Certificate (sampled(200) identities)*: lift instance: cl(p (+) q) = 1.380952 == cl(p)+cl(q) = 1.380952

**V4I — The exact V₄** (§5, Theorem 5.4, §5.6 P2-I). Under independence, the only admissible linear maps are diagonal; their sign-involutions form the Klein four-group exactly — no swap, no braid.

*Certificate (guard)*

*Verdict (S_703c582017c8, exhaustive): EXPRESSIBILITY-INTRINSIC — zero separators; co-movement 589824/589824 = 1.00; but NGL is never F anywhere in the space: a theorem, truth-stable wherever statable. Mutual constitution at the statability level, one-way at the truth level: interventions de-state the theorem rather than falsify it. ∀-over-declared-spaces; open-by-design.*


*Perspective visibility — NGL (executed, S_703c582017c8 configs):*

| FULL | P1 | P2-I | CLASSICAL | PROB | NO-CODEC | NO-ANCHOR | ONE-OP | NO-NEG | SING-BASIS | NOISY-LOCK | CHAR-2 | SEDENION | SPHERE | MENTION | COMPLEX |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P | V | P | P | P | P | P | P | V | P | P | V | P | P | P | V |

*Perspective visibility — V4I (executed, S_703c582017c8 configs):*

| FULL | P1 | P2-I | CLASSICAL | PROB | NO-CODEC | NO-ANCHOR | ONE-OP | NO-NEG | SING-BASIS | NOISY-LOCK | CHAR-2 | SEDENION | SPHERE | MENTION | COMPLEX |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P | V | P | P | P | P | P | P | V | P | P | F | P | P | P | V |

*Cross-reference — NGL:* depends on ['GCX', 'NOE', 'RAD', 'RDW', 'SWF', 'SWP', 'TWN', 'ZDG', 'ZDW']; required by ['D4C', 'GCX', 'NVE', 'NVL', 'PHS', 'RAD', 'RDW', 'RLS', 'SWF', 'SWP', 'T53', 'TWN', 'ZDG', 'ZDW']; independent of 10 claims (ADJ, BAL, CDC, CRS, PUR…).

*Cross-reference — V4I:* depends on ['GCX', 'NOE', 'RAD', 'RDW', 'SWF', 'SWP', 'TWN', 'ZDG', 'ZDW']; required by ['D4C', 'NVE', 'NVL', 'PHS', 'RLS', 'T53', 'TWN']; independent of 10 claims (ADJ, BAL, CDC, CRS, PUR…).


## The Noether pairings

**NOE — The Noether pairings** (§11.8, OB-7). The squeeze conserves mass; the common translation conserves bias — the two charges of the pair's symmetry flows.

*Certificate (exact (Lie-level in-run + variational/moment-map, pilot exact: noe-variational-pilot) — B6+OB-7 discharged)*: Lie-level invariants exact over integer grid: squeeze conserves a+b, translation conserves a-b -> True

*Characteristic-break coincidence with ['D4C', 'GCX', 'NGL', 'NVE', 'RAD', 'RDW', 'SWF', 'SWP', 'TWN', 'V4I', 'ZDG', 'ZDW'] (shared break in the dep digraph); separated in-space — see ledger.*


*Perspective visibility — NOE (executed, S_703c582017c8 configs):*

| FULL | P1 | P2-I | CLASSICAL | PROB | NO-CODEC | NO-ANCHOR | ONE-OP | NO-NEG | SING-BASIS | NOISY-LOCK | CHAR-2 | SEDENION | SPHERE | MENTION | COMPLEX |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P | V | P | P | P | P | P | P | P | P | P | P | P | P | P | P |

*Cross-reference — NOE:* depends on ['SWP']; required by ['CRS', 'D4C', 'L26', 'LOC', 'NGL', 'NVE', 'NVL', 'PHS', 'PR2', 'PRO', 'PUR', 'RLS', 'SWF', 'SWP', 'T53', 'TWN', 'V4I']; independent of 9 claims (ADJ, BAL, CDC, RAD, ZDG…).


## The ∨E bridge

**NVE — The ∨E bridge** (§5.7e; nedge-decomposition §8 (S8/S9)). Proof-by-cases is the single/double pin split/join expansion; the Wheatstone bridge reads the case-bias the join forgets; classical ∨E lives on the balance manifold.

*Certificate (mixed: sampled(800/400) + constructed nulls + exact conflation)*: constructed null bridge(3,7,6,14) = 0.00e+00; conflation splits (3,7)/(5,5): currents -0.043478 / +0.043478

*Characteristic-break coincidence with ['D4C', 'GCX', 'NGL', 'NOE', 'RAD', 'RDW', 'SWF', 'SWP', 'TWN', 'V4I', 'ZDG', 'ZDW'] (shared break in the dep digraph); separated in-space — see ledger.*

*Separation ledger NVE–NVL:* separated-in-S_703c582017c8 (6144 truth-separators); separated, 6144 truth @ S_f117b7f53a8e (v3.5 first form, same caveat); separated, 6144 truth @ S_2738ddb8c926 (v3.5a).


*Perspective visibility — NVE (executed, S_703c582017c8 configs):*

| FULL | P1 | P2-I | CLASSICAL | PROB | NO-CODEC | NO-ANCHOR | ONE-OP | NO-NEG | SING-BASIS | NOISY-LOCK | CHAR-2 | SEDENION | SPHERE | MENTION | COMPLEX |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P | V | V | P | P | P | P | P | V | P | P | V | P | P | P | V |

*Cross-reference — NVE:* depends on ['D4C', 'GCX', 'NGL', 'NOE', 'RAD', 'RDW', 'SWF', 'SWP', 'TWN', 'V4I', 'ZDG', 'ZDW']; required by ['D4C', 'NVL', 'PHS', 'PR2', 'PRO', 'PUR', 'TWN']; independent of 9 claims (ADJ, BAL, CDC, CRS, LOC…).


## Order-free semiring parsing

**SWF — Order-free semiring parsing** (theory-threads §8; retrospective R-V35). The order-free face of SWP (counting, inside, inside×outside, conflation): extends verbatim over ℂ — the first EXTENDS stance, earned by its named breaker.

*Certificate (exact (both fields; the complex run IS the breaker))*

*Characteristic-break coincidence with ['D4C', 'GCX', 'NGL', 'NOE', 'NVE', 'RAD', 'RDW', 'SWP', 'TWN', 'V4I', 'ZDG', 'ZDW'] (shared break in the dep digraph); separated in-space — see ledger.*

*Separation ledger SWF–SWP:* separated-in-S_703c582017c8 (0 truth-separators); 0 truth / 36864 kind — exactly the statable complex region: the EXTENDS breaker's footprint as a separator count @ S_3ed20b0e9c22 (v3.6); 0 truth / 36864 kind — the EXTENDS footprint, stable across v3.6/v3.6a @ S_9a577e722039 (v3.6a).


*Perspective visibility — SWF (executed, S_703c582017c8 configs):*

| FULL | P1 | P2-I | CLASSICAL | PROB | NO-CODEC | NO-ANCHOR | ONE-OP | NO-NEG | SING-BASIS | NOISY-LOCK | CHAR-2 | SEDENION | SPHERE | MENTION | COMPLEX |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P | V | P | P | P | P | P | P | P | P | P | V | P | P | P | P |

*Cross-reference — SWF:* depends on ['GCX', 'NGL', 'NOE', 'RAD', 'RDW', 'SWP', 'TWN', 'ZDG', 'ZDW']; required by ['D4C', 'GCX', 'NGL', 'NVE', 'NVL', 'PHS', 'RAD', 'RDW', 'RLS', 'SWP', 'T53', 'TWN', 'V4I', 'ZDG', 'ZDW']; independent of 10 claims (ADJ, BAL, CDC, CRS, PUR…).


## Semiring-weighted parsing

**SWP — Semiring-weighted parsing** (theory-threads §2/§8/§9 (S7/S12/S13)). One chart, pluggable semiring: the carrier semiring carries the SPPF's packed multiplicity; probability is the positive-rail section, Viterbi the idempotent pinning; inside×outside is the zipper product.

*Certificate (exact (CKY + exhaustive containment))*: exact: 'aaaa' under S->SS|'a' has 5 derivations; inside = 5*p^3*q^4 verified symbol-for-symbol; inside x outside = containment at every span

*Characteristic-break coincidence with ['D4C', 'GCX', 'NGL', 'NOE', 'NVE', 'RAD', 'RDW', 'SWF', 'TWN', 'V4I', 'ZDG', 'ZDW'] (shared break in the dep digraph); separated in-space — see ledger.*


*Perspective visibility — SWP (executed, S_703c582017c8 configs):*

| FULL | P1 | P2-I | CLASSICAL | PROB | NO-CODEC | NO-ANCHOR | ONE-OP | NO-NEG | SING-BASIS | NOISY-LOCK | CHAR-2 | SEDENION | SPHERE | MENTION | COMPLEX |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P | V | P | P | P | P | P | P | P | P | P | V | P | P | P | V |

*Cross-reference — SWP:* depends on ['GCX', 'NGL', 'NOE', 'RAD', 'RDW', 'SWF', 'TWN', 'ZDG', 'ZDW']; required by ['CRS', 'D4C', 'L26', 'LOC', 'NGL', 'NOE', 'NVE', 'NVL', 'PHS', 'PR2', 'PRO', 'PUR', 'RLS', 'SWF', 'T53', 'TWN', 'V4I']; independent of 4 claims (ADJ, BAL, CDC, IDC).


## The twist

**TWN — The twist** (§5.9, Theorem 5.4). The level conjugation pair anticommutes by a central, reversible sign — the cocycle of the doubling interface; trivial in characteristic 2.

*Certificate (guard)*

*Characteristic-break coincidence with ['D4C', 'GCX', 'NGL', 'NOE', 'NVE', 'RAD', 'RDW', 'SWF', 'SWP', 'V4I', 'ZDG', 'ZDW'] (shared break in the dep digraph); separated in-space — see ledger.*


*Perspective visibility — TWN (executed, S_703c582017c8 configs):*

| FULL | P1 | P2-I | CLASSICAL | PROB | NO-CODEC | NO-ANCHOR | ONE-OP | NO-NEG | SING-BASIS | NOISY-LOCK | CHAR-2 | SEDENION | SPHERE | MENTION | COMPLEX |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P | V | V | P | P | P | P | P | V | P | P | F | P | P | P | V |

*Cross-reference — TWN:* depends on ['D4C', 'GCX', 'NGL', 'NOE', 'NVE', 'RAD', 'RDW', 'SWF', 'SWP', 'V4I', 'ZDG', 'ZDW']; required by ['D4C', 'GCX', 'NGL', 'NVE', 'NVL', 'PHS', 'RAD', 'RDW', 'RLS', 'SWF', 'SWP', 'T53', 'V4I', 'ZDG', 'ZDW']; independent of 10 claims (ADJ, BAL, CDC, CRS, PUR…).


## The identity-collapse schedule

**IDC — The identity-collapse schedule** (nedge-decomposition §2 (N-series)). Bare nodes collapse; minimally-stabilized twins still collapse; distinct participation separates — identity is unseparated-in-probe-space, and differentiation is probe-space extension.

*Certificate (exact (WL signatures on declared exhibits; probe-indexed rounds) — audited S45)*


*Perspective visibility — IDC (executed, S_703c582017c8 configs):*

| FULL | P1 | P2-I | CLASSICAL | PROB | NO-CODEC | NO-ANCHOR | ONE-OP | NO-NEG | SING-BASIS | NOISY-LOCK | CHAR-2 | SEDENION | SPHERE | MENTION | COMPLEX |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P | P | P | P | P | P | P | P | P | P | P | P | P | P | F | P |

*Cross-reference — IDC:* depends on —; required by —; independent of 26 claims (ADJ, BAL, CDC, CRS, PUR…).


# Part 2 — Layer 1


## The balance channel

**BAL — The balance channel** (§5.7). A single pin's real component holds the balance of the evidence, read relative to its frame's identity element; conflict is inexpressible.

*Certificate (analytic-points (s=-0.2))*

*Characteristic-break coincidence with ['CDC'] (shared break in the dep digraph); separated in-space — see ledger.*

*Separation ledger BAL–CDC:* separated-in-S_703c582017c8 (165888 truth-separators); separated (adj; identical-frames) @ S_v2 (characteristic-break basis).


*Perspective visibility — BAL (executed, S_703c582017c8 configs):*

| FULL | P1 | P2-I | CLASSICAL | PROB | NO-CODEC | NO-ANCHOR | ONE-OP | NO-NEG | SING-BASIS | NOISY-LOCK | CHAR-2 | SEDENION | SPHERE | MENTION | COMPLEX |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P | P | P | P | P | F | F | P | P | P | P | P | P | P | P | P |

*Cross-reference — BAL:* depends on ['ADJ', 'CDC']; required by ['CDC']; independent of 24 claims (CRS, PUR, PRO, LOC, L26…).


## The codec contract

**CDC — The codec contract** (§5.7, Caveat 2.4a). Ring or semiring encoding is indifferent iff encode matches decode; frame mismatch silently flips balance; negative+semiring is ill-typed.

*Certificate (analytic-point (codec range at s=-0.2) + guard(ident) — audited S45)*

*Characteristic-break coincidence with ['BAL'] (shared break in the dep digraph); separated in-space — see ledger.*

*Separation ledger CDC–GCX:* separated-in-S_703c582017c8 (110592 truth-separators); separated, 27648 truth — the sighting is not a restatement @ S_f117b7f53a8e (v3.5 first form, same caveat); separated, 27648 truth @ S_2738ddb8c926 (v3.5a).


*Perspective visibility — CDC (executed, S_703c582017c8 configs):*

| FULL | P1 | P2-I | CLASSICAL | PROB | NO-CODEC | NO-ANCHOR | ONE-OP | NO-NEG | SING-BASIS | NOISY-LOCK | CHAR-2 | SEDENION | SPHERE | MENTION | COMPLEX |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P | P | P | P | P | P | F | P | P | P | P | P | P | P | P | P |

*Cross-reference — CDC:* depends on ['BAL']; required by ['BAL']; independent of 25 claims (ADJ, CRS, PUR, PRO, LOC…).


## The crossbar

**CRS — The crossbar** (§4). (mass, bias) = (E⁺+E⁻, E⁺−E⁻) is an invertible change of basis on the pair.

*Certificate (guard)*

*Separation ledger CRS–NOE:* separated-in-S_703c582017c8 (221184 truth-separators); unseparated-in-S_v3 @ S_v3 (9 knobs, no basis_def); separated (basis_def='singular') @ S_v2 (characteristic-break basis + basis_def probe).


*Perspective visibility — CRS (executed, S_703c582017c8 configs):*

| FULL | P1 | P2-I | CLASSICAL | PROB | NO-CODEC | NO-ANCHOR | ONE-OP | NO-NEG | SING-BASIS | NOISY-LOCK | CHAR-2 | SEDENION | SPHERE | MENTION | COMPLEX |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P | V | P | P | P | P | P | P | P | F | P | P | P | P | P | P |

*Cross-reference — CRS:* depends on ['NOE', 'SWP']; required by —; independent of 24 claims (ADJ, BAL, CDC, PUR, PRO…).


## The two-gate theorem

**NVL — The two-gate theorem** (§4, §5.7e, nedge-decomposition §2/§6). Nedge's 4VL (confidence × consistency) and Belnap's chart (bias-sign × rail) are distinct four-cell gates on one carrier; either magnitude pinning degenerates the gate — a four-valued logic needs the unpinned pair.

*Certificate (exact-exhaustive (declared 24-point grid, adaptive bits))*

*Characteristic-break coincidence with ['PR2', 'PRO', 'PUR'] (shared break in the dep digraph); separated in-space — see ledger.*

*Separation ledger NVL–PUR:* separated-in-S_703c582017c8 (12288 truth-separators); 6144 truth, HALF ARTIFACTUAL: NVL spuriously P on the L1 slice (adaptive bit split float noise around mass==1); corrected same-day, fingerprint widened to full module source @ S_8fecfdc135c8 (v3.4 FIRST run — FP-noise artifact in _nvl_two_gates, helper outside the then-fingerprint).


*Perspective visibility — NVL (executed, S_703c582017c8 configs):*

| FULL | P1 | P2-I | CLASSICAL | PROB | NO-CODEC | NO-ANCHOR | ONE-OP | NO-NEG | SING-BASIS | NOISY-LOCK | CHAR-2 | SEDENION | SPHERE | MENTION | COMPLEX |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P | V | V | P | F | P | P | P | V | P | P | V | P | F | P | V |

*Cross-reference — NVL:* depends on ['D4C', 'GCX', 'NGL', 'NOE', 'NVE', 'PR2', 'PRO', 'PUR', 'RAD', 'RDW', 'SWF', 'SWP', 'TWN', 'V4I', 'ZDG', 'ZDW']; required by ['PR2', 'PRO', 'PUR']; independent of 10 claims (ADJ, BAL, CDC, CRS, LOC…).


## The sphere prohibition

**PR2 — The sphere prohibition** (§5.9). Pinning the quadratic radius (L2 normalization) is also a one-mode decode: it conflates states differing only in radius — the prohibition's arity argument, second magnitude instance.

*Certificate (witness (constructed exact collision: (3,4)~(6,8) under r-pinning) — audited S45)*

*Characteristic-break coincidence with ['NVL', 'PRO', 'PUR'] (shared break in the dep digraph); separated in-space — see ledger.*

*Separation ledger PR2–PRO:* separated-in-S_703c582017c8 (0 truth-separators); 0 truth-separators; 4096 kind-separators (PRO's guard keys on L1) @ S_94763a8b62ea (v3.3).


*Perspective visibility — PR2 (executed, S_703c582017c8 configs):*

| FULL | P1 | P2-I | CLASSICAL | PROB | NO-CODEC | NO-ANCHOR | ONE-OP | NO-NEG | SING-BASIS | NOISY-LOCK | CHAR-2 | SEDENION | SPHERE | MENTION | COMPLEX |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P | V | V | P | V | P | P | P | P | P | P | P | P | V | P | P |

*Cross-reference — PR2:* depends on ['D4C', 'NOE', 'NVE', 'NVL', 'PRO', 'PUR', 'SWP']; required by ['NVL']; independent of 19 claims (ADJ, BAL, CDC, CRS, LOC…).


## The prohibition ≡ The differential purchase — one structure

**PRO — The prohibition** (§3, §5.8a). Pinning the purchased axis (normalization) conflates conflict with ignorance; collapse is an arity-mismatched decode; probability is the c-pinned slice.

*Certificate (guard (truth-stable by arithmetic; see spec 5.8a))*

**PUR — The differential purchase** (§5.7). Encoding one channel over two pins gains the conflict/ignorance axis: d carries the balance, c is the purchased mass axis.

*Certificate (guard)*

*Verdict (S_703c582017c8, exhaustive): EXPRESSIBILITY-INTRINSIC — zero separators; co-movement 516096/516096 = 1.00; but PRO is never F anywhere in the space: a theorem, truth-stable wherever statable. Mutual constitution at the statability level, one-way at the truth level: interventions de-state the theorem rather than falsify it. ∀-over-declared-spaces; open-by-design.*

*Frontier: a separator would require a pinning that fails to conflate equal-d states, or a model where PRO is statable yet false — excluded by arithmetic; residual openness at the TEST-FORMALIZATION stratum.*


*Perspective visibility — PRO (executed, S_703c582017c8 configs):*

| FULL | P1 | P2-I | CLASSICAL | PROB | NO-CODEC | NO-ANCHOR | ONE-OP | NO-NEG | SING-BASIS | NOISY-LOCK | CHAR-2 | SEDENION | SPHERE | MENTION | COMPLEX |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P | V | V | P | V | P | P | P | P | P | P | P | P | P | P | P |

*Perspective visibility — PUR (executed, S_703c582017c8 configs):*

| FULL | P1 | P2-I | CLASSICAL | PROB | NO-CODEC | NO-ANCHOR | ONE-OP | NO-NEG | SING-BASIS | NOISY-LOCK | CHAR-2 | SEDENION | SPHERE | MENTION | COMPLEX |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P | V | V | P | F | P | P | P | P | P | P | P | P | P | P | P |

*Cross-reference — PRO:* depends on ['D4C', 'NOE', 'NVE', 'NVL', 'SWP']; required by ['NVL', 'PR2']; independent of 19 claims (ADJ, BAL, CDC, CRS, LOC…).

*Cross-reference — PUR:* depends on ['D4C', 'NOE', 'NVE', 'NVL', 'SWP']; required by ['NVL', 'PR2']; independent of 19 claims (ADJ, BAL, CDC, CRS, LOC…).


## The involution coincidence ≡ The classical section — one structure

**L26 — The involution coincidence** (Lemma 2.6). On the classical section, constrained negation equals the pin-swap — they coincide iff the section is exactly f = −id.

*Certificate (analytic-points)*

**LOC — The classical section** (Lemma 2.6, §5.8b). The inverse-locked locus (u, −u) is exactly c ≡ 0: the balance channel embedded in the pair; classical logic with the purchased axis off.

*Certificate (analytic-points (3 probe values) + U-kinds)*

*Verdict (S_703c582017c8, exhaustive): TRUTH-INTRINSIC — zero separators of any kind; co-movement 497664/497664 = 1.00. Closure-under-break: every perturbation breaks the loop coherently, with kind-structure inside the co-movement (e.g. noisy lock: U vs F). ∀-over-declared-spaces; strengthens with each space survived; never closes.*

*Frontier: a separator would require a model with f != -id yet c == 0 on it, or f == -id with swap != constrained-negation — both excluded by the shared arithmetic of the current test semantics; residual openness lives at the TEST-FORMALIZATION stratum, not the knob-value stratum.*


*Perspective visibility — L26 (executed, S_703c582017c8 configs):*

| FULL | P1 | P2-I | CLASSICAL | PROB | NO-CODEC | NO-ANCHOR | ONE-OP | NO-NEG | SING-BASIS | NOISY-LOCK | CHAR-2 | SEDENION | SPHERE | MENTION | COMPLEX |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P | V | P | P | P | P | P | P | P | P | F | P | P | P | P | P |

*Perspective visibility — LOC (executed, S_703c582017c8 configs):*

| FULL | P1 | P2-I | CLASSICAL | PROB | NO-CODEC | NO-ANCHOR | ONE-OP | NO-NEG | SING-BASIS | NOISY-LOCK | CHAR-2 | SEDENION | SPHERE | MENTION | COMPLEX |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P | V | P | P | P | P | P | P | P | P | U | P | P | P | P | P |

*Cross-reference — L26:* depends on ['NOE', 'RLS', 'SWP']; required by ['PHS', 'RLS', 'T53']; independent of 20 claims (ADJ, BAL, CDC, CRS, PUR…).

*Cross-reference — LOC:* depends on ['NOE', 'RLS', 'SWP']; required by ['PHS', 'RLS', 'T53']; independent of 20 claims (ADJ, BAL, CDC, CRS, PUR…).


## The classical rails

**RLS — The classical rails** (§5.7 worked rails). The locus endpoints are T and F; composed NOT exchanges them; independent negation at a rail lands on conflict. The rails are a compactification fact, detachable from the section.

*Certificate (analytic-rails (B=1e9 endpoints))*

*Characteristic-break coincidence with ['L26', 'LOC'] (shared break in the dep digraph); separated in-space — see ledger.*


*Perspective visibility — RLS (executed, S_703c582017c8 configs):*

| FULL | P1 | P2-I | CLASSICAL | PROB | NO-CODEC | NO-ANCHOR | ONE-OP | NO-NEG | SING-BASIS | NOISY-LOCK | CHAR-2 | SEDENION | SPHERE | MENTION | COMPLEX |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P | V | P | P | P | P | P | P | V | P | U | F | P | P | P | V |

*Cross-reference — RLS:* depends on ['GCX', 'L26', 'LOC', 'NGL', 'NOE', 'RAD', 'RDW', 'SWF', 'SWP', 'TWN', 'V4I', 'ZDG', 'ZDW']; required by ['L26', 'LOC', 'PHS', 'T53']; independent of 11 claims (ADJ, BAL, CDC, CRS, PUR…).


# Part 3 — Layer 2


## The De Morgan requirements

**T53 — The De Morgan requirements** (Theorem 5.3). NOT(AND) ≡ OR requires two operations (one collapses OR into AND) and the inverse-lock (the classical section).

*Certificate (guard + delegate(L26))*


*Perspective visibility — T53 (executed, S_703c582017c8 configs):*

| FULL | P1 | P2-I | CLASSICAL | PROB | NO-CODEC | NO-ANCHOR | ONE-OP | NO-NEG | SING-BASIS | NOISY-LOCK | CHAR-2 | SEDENION | SPHERE | MENTION | COMPLEX |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P | V | P | P | P | P | P | F | V | P | F | V | P | P | P | V |

*Cross-reference — T53:* depends on ['GCX', 'L26', 'LOC', 'NGL', 'NOE', 'RAD', 'RDW', 'RLS', 'SWF', 'SWP', 'TWN', 'V4I', 'ZDG', 'ZDW']; required by —; independent of 12 claims (ADJ, BAL, CDC, CRS, PUR…).


## The phase support theorem

**PHS — The phase support theorem** (§5.8c, §8.5–8.6). The extension class (the phase bit) is trivial exactly on the classical section and nontrivial exactly off it; a single pin has no phase.

*Certificate (analytic-points (on/off locus, numpy exact))*

*Separation ledger PHS–TWN:* separated-in-S_703c582017c8 (4608 truth-separators); SEPARATED: 768 truth-separators (the phase is the twist AS SEEN AGAINST the section) @ S_94763a8b62ea (v3.3).


*Perspective visibility — PHS (executed, S_703c582017c8 configs):*

| FULL | P1 | P2-I | CLASSICAL | PROB | NO-CODEC | NO-ANCHOR | ONE-OP | NO-NEG | SING-BASIS | NOISY-LOCK | CHAR-2 | SEDENION | SPHERE | MENTION | COMPLEX |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P | V | V | V | P | P | P | P | V | P | U | V | P | P | P | V |

*Cross-reference — PHS:* depends on ['D4C', 'GCX', 'L26', 'LOC', 'NGL', 'NOE', 'NVE', 'RAD', 'RDW', 'RLS', 'SWF', 'SWP', 'TWN', 'V4I', 'ZDG', 'ZDW']; required by —; independent of 10 claims (ADJ, BAL, CDC, CRS, PUR…).


---

# Glossary (computed)

**Order-free semiring parsing** [SWF] — The order-free face of SWP (counting, inside, inside×outside, conflation): extends verbatim over ℂ — the first EXTENDS stance, earned by its named breaker. *(Layer 0; theory-threads §8; retrospective R-V35)*

**Semiring-weighted parsing** [SWP] — One chart, pluggable semiring: the carrier semiring carries the SPPF's packed multiplicity; probability is the positive-rail section, Viterbi the idempotent pinning; inside×outside is the zipper product. *(Layer 0; theory-threads §2/§8/§9 (S7/S12/S13))*

**The De Morgan requirements** [T53] — NOT(AND) ≡ OR requires two operations (one collapses OR into AND) and the inverse-lock (the classical section). *(Layer 2; Theorem 5.3)*

**The G-value lift** [NGL] — Nedge's G-Value Calculus is ⟨fraction-addition, swap⟩ on formal-quotient pairs — the carrier quotiented by the diagonal; non-idempotence is the mass-growth shadow; resource sensitivity is the quotient remembering the extruded axis. *(Layer 0; §5.7e, nedge-decomposition §6; expr-intrinsic circle member)*

**The Noether pairings** [NOE] — The squeeze conserves mass; the common translation conserves bias — the two charges of the pair's symmetry flows. *(Layer 0; §11.8, OB-7)*

**The balance channel** [BAL] — A single pin's real component holds the balance of the evidence, read relative to its frame's identity element; conflict is inexpressible. *(Layer 1; §5.7)*

**The braided V₄ (D₄)** [D4C] — Composed reading licenses the swap; ⟨negate-one, swap⟩ = D₄, the central extension of V₄ by the reversible twist [N,S] = −id. *(Layer 0; Theorem 5.4, Remark 5.5)*

**The chart adjunction (exp ⊣ log)** [ADJ] — The two per-pin charts — semiring magnitudes and the signed line — form an adjoint equivalence; the codec pair whose round-trips are identities. *(Layer 0; §2, Lemma 2.5b)*

**The classical rails** [RLS] — The locus endpoints are T and F; composed NOT exchanges them; independent negation at a rail lands on conflict. The rails are a compactification fact, detachable from the section. *(Layer 1; §5.7 worked rails)*

**The classical section** [LOC] — The inverse-locked locus (u, −u) is exactly c ≡ 0: the balance channel embedded in the pair; classical logic with the purchased axis off. *(Layer 1; Lemma 2.6, §5.8b; truth-intrinsic circle member)*

**The codec contract** [CDC] — Ring or semiring encoding is indifferent iff encode matches decode; frame mismatch silently flips balance; negative+semiring is ill-typed. *(Layer 1; §5.7, Caveat 2.4a)*

**The crossbar** [CRS] — (mass, bias) = (E⁺+E⁻, E⁺−E⁻) is an invertible change of basis on the pair. *(Layer 1; §4)*

**The differential purchase** [PUR] — Encoding one channel over two pins gains the conflict/ignorance axis: d carries the balance, c is the purchased mass axis. *(Layer 1; §5.7; expr-intrinsic circle member)*

**The exact V₄** [V4I] — Under independence, the only admissible linear maps are diagonal; their sign-involutions form the Klein four-group exactly — no swap, no braid. *(Layer 0; §5, Theorem 5.4, §5.6 P2-I; expr-intrinsic circle member)*

**The identity-collapse schedule** [IDC] — Bare nodes collapse; minimally-stabilized twins still collapse; distinct participation separates — identity is unseparated-in-probe-space, and differentiation is probe-space extension. *(Layer 0; nedge-decomposition §2 (N-series))*

**The involution coincidence** [L26] — On the classical section, constrained negation equals the pin-swap — they coincide iff the section is exactly f = −id. *(Layer 1; Lemma 2.6; truth-intrinsic circle member)*

**The phase support theorem** [PHS] — The extension class (the phase bit) is trivial exactly on the classical section and nontrivial exactly off it; a single pin has no phase. *(Layer 2; §5.8c, §8.5–8.6)*

**The prohibition** [PRO] — Pinning the purchased axis (normalization) conflates conflict with ignorance; collapse is an arity-mismatched decode; probability is the c-pinned slice. *(Layer 1; §3, §5.8a; expr-intrinsic circle member)*

**The radial schedule** [RAD] — The CD pinning's quadratic norm is multiplicative exactly through the octonion rung (Hurwitz); radial multiplicativity is a sacrifice-ladder rung. *(Layer 0; §5.9; expr-intrinsic circle member)*

**The radial witness mode** [RDW] — Pi-form: the excess-mode schedule — norm-failure-beyond-the-kernel is empty through the octonions, inhabited from the sedenions; the witness is the section over rungs (a 1-path), displayed as cdlevel-inertness. *(Layer 0; §5.9; theory-threads §14 (T2); expr-intrinsic circle member)*

**The sphere prohibition** [PR2] — Pinning the quadratic radius (L2 normalization) is also a one-mode decode: it conflates states differing only in radius — the prohibition's arity argument, second magnitude instance. *(Layer 1; §5.9)*

**The third codec sighting** [GCX] — GALAXY's W ↔ ASPF's log-decode: the exponential codec is exact on the rank-sum quotient, and the quotient genuinely collides — GALAXY is a one-mode decode of the ASPF carrier. *(Layer 0; corpus-sweep §6 (S4); §5.8; expr-intrinsic circle member)*

**The twist** [TWN] — The level conjugation pair anticommutes by a central, reversible sign — the cocycle of the doubling interface; trivial in characteristic 2. *(Layer 0; §5.9, Theorem 5.4)*

**The two-gate theorem** [NVL] — Nedge's 4VL (confidence × consistency) and Belnap's chart (bias-sign × rail) are distinct four-cell gates on one carrier; either magnitude pinning degenerates the gate — a four-valued logic needs the unpinned pair. *(Layer 1; §4, §5.7e, nedge-decomposition §2/§6)*

**The zero-divisor schedule** [ZDG] — Zero divisors first appear at the sedenion rung and are enumerated, oriented geography (dim 2ⁿ−5, G₂); in characteristic 2 they appear at every rung — the schedule is a char-0 fact. *(Layer 0; §5.9 (Z-series); expr-intrinsic circle member)*

**The zero-divisor witness mode** [ZDW] — Pi-form: the kernel-mode schedule — det L_x locked to N^(d/2) through the octonions (kernel empty), unlocked at the sedenions (kernel inhabited, contained in norm-failure); the lock schedule IS the content. *(Layer 0; §5.9; theory-threads §14 (T2); expr-intrinsic circle member)*

**The ∨E bridge** [NVE] — Proof-by-cases is the single/double pin split/join expansion; the Wheatstone bridge reads the case-bias the join forgets; classical ∨E lives on the balance manifold. *(Layer 0; §5.7e; nedge-decomposition §8 (S8/S9))*


# Cross-Reference Index (computed)

| claim | layer | depends on | required by | circle |
|---|---|---|---|---|
| ADJ | 0 | — | BAL | — |
| BAL | 1 | ADJ, CDC | CDC | — |
| CDC | 1 | BAL | BAL | — |
| CRS | 1 | NOE, SWP | — | — |
| PUR | 1 | D4C, NOE, NVE, NVL, PRO, SWP | NVL, PR2, PRO | PRO ≡ PUR |
| PRO | 1 | D4C, NOE, NVE, NVL, PUR, SWP | NVL, PR2, PUR | PRO ≡ PUR |
| LOC | 1 | L26, NOE, RLS, SWP | L26, PHS, RLS, T53 | L26 ≡ LOC |
| L26 | 1 | LOC, NOE, RLS, SWP | LOC, PHS, RLS, T53 | L26 ≡ LOC |
| T53 | 2 | GCX, L26, LOC, NGL, NOE, RAD, RDW, RLS, SWF, SWP, TWN, V4I, ZDG, ZDW | — | — |
| V4I | 0 | GCX, NGL, NOE, RAD, RDW, SWF, SWP, TWN, ZDG, ZDW | D4C, NGL, NVE, NVL, PHS, RLS, T53, TWN | NGL ≡ V4I |
| D4C | 0 | GCX, NGL, NOE, NVE, RAD, RDW, SWF, SWP, TWN, V4I, ZDG, ZDW | NVE, NVL, PHS, PR2, PRO, PUR, TWN | — |
| PHS | 2 | D4C, GCX, L26, LOC, NGL, NOE, NVE, RAD, RDW, RLS, SWF, SWP, TWN, V4I, ZDG, ZDW | — | — |
| RLS | 1 | GCX, L26, LOC, NGL, NOE, RAD, RDW, SWF, SWP, TWN, V4I, ZDG, ZDW | L26, LOC, PHS, T53 | — |
| NOE | 0 | SWP | CRS, D4C, L26, LOC, NGL, NVE, NVL, PHS, PR2, PRO, PUR, RLS, SWF, SWP, T53, TWN, V4I | — |
| TWN | 0 | D4C, GCX, NGL, NOE, NVE, RAD, RDW, SWF, SWP, V4I, ZDG, ZDW | D4C, GCX, NGL, NVE, NVL, PHS, RAD, RDW, RLS, SWF, SWP, T53, V4I, ZDG, ZDW | — |
| RAD | 0 | GCX, NGL, RDW, SWF, TWN, ZDG, ZDW | D4C, GCX, NGL, NVE, NVL, PHS, RDW, RLS, SWF, SWP, T53, TWN, V4I, ZDG, ZDW | GCX ≡ RAD ≡ RDW ≡ ZDG ≡ ZDW |
| ZDG | 0 | GCX, NGL, RAD, RDW, SWF, TWN, ZDW | D4C, GCX, NGL, NVE, NVL, PHS, RAD, RDW, RLS, SWF, SWP, T53, TWN, V4I, ZDW | GCX ≡ RAD ≡ RDW ≡ ZDG ≡ ZDW |
| PR2 | 1 | D4C, NOE, NVE, NVL, PRO, PUR, SWP | NVL | — |
| NGL | 0 | GCX, NOE, RAD, RDW, SWF, SWP, TWN, V4I, ZDG, ZDW | D4C, GCX, NVE, NVL, PHS, RAD, RDW, RLS, SWF, SWP, T53, TWN, V4I, ZDG, ZDW | NGL ≡ V4I |
| NVL | 1 | D4C, GCX, NGL, NOE, NVE, PR2, PRO, PUR, RAD, RDW, SWF, SWP, TWN, V4I, ZDG, ZDW | PR2, PRO, PUR | — |
| IDC | 0 | — | — | — |
| GCX | 0 | NGL, RAD, RDW, SWF, TWN, ZDG, ZDW | D4C, NGL, NVE, NVL, PHS, RAD, RDW, RLS, SWF, SWP, T53, TWN, V4I, ZDG, ZDW | GCX ≡ RAD ≡ RDW ≡ ZDG ≡ ZDW |
| SWP | 0 | GCX, NGL, NOE, RAD, RDW, SWF, TWN, ZDG, ZDW | CRS, D4C, L26, LOC, NGL, NOE, NVE, NVL, PHS, PR2, PRO, PUR, RLS, SWF, T53, TWN, V4I | — |
| NVE | 0 | D4C, GCX, NGL, NOE, RAD, RDW, SWF, SWP, TWN, V4I, ZDG, ZDW | D4C, NVL, PHS, PR2, PRO, PUR, TWN | — |
| RDW | 0 | GCX, NGL, RAD, SWF, TWN, ZDG, ZDW | D4C, GCX, NGL, NVE, NVL, PHS, RAD, RLS, SWF, SWP, T53, TWN, V4I, ZDG, ZDW | GCX ≡ RAD ≡ RDW ≡ ZDG ≡ ZDW |
| ZDW | 0 | GCX, NGL, RAD, RDW, SWF, TWN, ZDG | D4C, GCX, NGL, NVE, NVL, PHS, RAD, RDW, RLS, SWF, SWP, T53, TWN, V4I, ZDG | GCX ≡ RAD ≡ RDW ≡ ZDG ≡ ZDW |
| SWF | 0 | GCX, NGL, NOE, RAD, RDW, SWP, TWN, ZDG, ZDW | D4C, GCX, NGL, NVE, NVL, PHS, RAD, RDW, RLS, SWP, T53, TWN, V4I, ZDG, ZDW | — |

*Independence count: 195 of 351 pairs carry no dependence in either direction (S_703c582017c8).*