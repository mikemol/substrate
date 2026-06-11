# The EL-Atlas, Structured Edition

*Mechanically derived by `tools/el-atlas-structured-gen.py` from the v3.1 harness.*
*All verdicts indexed: space **S_666bf26b7779** (3072 models, exhaustive); manifest below.*
*Hand-written content: claim metadata sentences and spec pointers only.*

**Space manifest S_666bf26b7779:** pins ∈ {1, 2, 3}; adj ∈ {True, False}; ident ∈ {True, False}; neg ∈ {True, False}; ops ∈ {diagonal, linear}; lock ∈ {available, unavailable, wrong, clipped, affine, noisy, partial, forced}; norm ∈ {free, pinned}; two_ops ∈ {True, False}; basis_def ∈ {ok, singular}.

**Legend:** P = visible/true from that vantage; F = false there; U = observable but
undecided; V = not statable there. Dependence edges arise from F and V only —
undecided is not destroyed. Circle verdicts carry their space index and ledger.

## Table of Contents

**Part 1 — Layer 0 (foundations)**
- [The chart adjunction (exp ⊣ log)](#the-chart-adjunction-exp--log)
- [The Noether pairings](#the-noether-pairings)

**Part 2 — Layer 1**
- [The balance channel](#the-balance-channel) *(characteristic-break coincidence; separated in-space)*
- [The codec contract](#the-codec-contract) *(characteristic-break coincidence; separated in-space)*
- [The crossbar](#the-crossbar)
- [The exact V₄](#the-exact-v4)

**Part 3 — Layer 2**
- [The involution coincidence ≡ The classical section](#the-involution-coincidence) *(one structure — truth-intrinsic)*
- [The classical rails](#the-classical-rails) *(characteristic-break coincidence; separated in-space)*
- [The braided V₄ (D₄)](#the-braided-v4-d4)

**Part 4 — Layer 3**
- [The prohibition ≡ The differential purchase](#the-prohibition) *(one structure — expressibility-intrinsic)*
- [The De Morgan requirements](#the-de-morgan-requirements)
- [The phase support theorem](#the-phase-support-theorem)


---


# Part 1 — Layer 0 (foundations)


## The chart adjunction (exp ⊣ log)

**ADJ — The chart adjunction (exp ⊣ log)** (§2, Lemma 2.5b). The two per-pin charts — semiring magnitudes and the signed line — form an adjoint equivalence; the codec pair whose round-trips are identities.


*Perspective visibility — ADJ (executed, S_666bf26b7779 configs):*

| FULL | P1 | P2-I | CLASSICAL | PROB | NO-CODEC | NO-ANCHOR | ONE-OP | NO-NEG | SING-BASIS | NOISY-LOCK |
|---|---|---|---|---|---|---|---|---|---|---|
| P | P | P | P | P | F | P | P | P | P | P |

*Cross-reference — ADJ:* depends on —; required by ['BAL']; independent of 12 claims (CDC, CRS, PUR, PRO, LOC…).


## The Noether pairings

**NOE — The Noether pairings** (§11.8, OB-7). The squeeze conserves mass; the common translation conserves bias — the two charges of the pair's symmetry flows.


*Perspective visibility — NOE (executed, S_666bf26b7779 configs):*

| FULL | P1 | P2-I | CLASSICAL | PROB | NO-CODEC | NO-ANCHOR | ONE-OP | NO-NEG | SING-BASIS | NOISY-LOCK |
|---|---|---|---|---|---|---|---|---|---|---|
| P | V | P | P | P | P | P | P | P | P | P |

*Cross-reference — NOE:* depends on —; required by ['CRS', 'D4C', 'L26', 'LOC', 'PHS', 'PRO', 'PUR', 'RLS', 'T53', 'V4I']; independent of 3 claims (ADJ, BAL, CDC).


# Part 2 — Layer 1


## The balance channel

**BAL — The balance channel** (§5.7). A single pin's real component holds the balance of the evidence, read relative to its frame's identity element; conflict is inexpressible.

*Characteristic-break coincidence with ['CDC'] (shared break in the dep digraph); separated in-space — see ledger.*

*Separation ledger BAL–CDC:* separated-in-S_666bf26b7779 (768 truth-separators); separated (adj; identical-frames) @ S_v2 (characteristic-break basis).


*Perspective visibility — BAL (executed, S_666bf26b7779 configs):*

| FULL | P1 | P2-I | CLASSICAL | PROB | NO-CODEC | NO-ANCHOR | ONE-OP | NO-NEG | SING-BASIS | NOISY-LOCK |
|---|---|---|---|---|---|---|---|---|---|---|
| P | P | P | P | P | F | F | P | P | P | P |

*Cross-reference — BAL:* depends on ['ADJ', 'CDC']; required by ['CDC']; independent of 11 claims (CRS, PUR, PRO, LOC, L26…).


## The codec contract

**CDC — The codec contract** (§5.7, Caveat 2.4a). Ring or semiring encoding is indifferent iff encode matches decode; frame mismatch silently flips balance; negative+semiring is ill-typed.

*Characteristic-break coincidence with ['BAL'] (shared break in the dep digraph); separated in-space — see ledger.*


*Perspective visibility — CDC (executed, S_666bf26b7779 configs):*

| FULL | P1 | P2-I | CLASSICAL | PROB | NO-CODEC | NO-ANCHOR | ONE-OP | NO-NEG | SING-BASIS | NOISY-LOCK |
|---|---|---|---|---|---|---|---|---|---|---|
| P | P | P | P | P | P | F | P | P | P | P |

*Cross-reference — CDC:* depends on ['BAL']; required by ['BAL']; independent of 12 claims (ADJ, CRS, PUR, PRO, LOC…).


## The crossbar

**CRS — The crossbar** (§4). (mass, bias) = (E⁺+E⁻, E⁺−E⁻) is an invertible change of basis on the pair.

*Separation ledger CRS–NOE:* separated-in-S_666bf26b7779 (1024 truth-separators); unseparated-in-S_v3 @ S_v3 (9 knobs, no basis_def); separated (basis_def='singular') @ S_v2 (characteristic-break basis + basis_def probe).


*Perspective visibility — CRS (executed, S_666bf26b7779 configs):*

| FULL | P1 | P2-I | CLASSICAL | PROB | NO-CODEC | NO-ANCHOR | ONE-OP | NO-NEG | SING-BASIS | NOISY-LOCK |
|---|---|---|---|---|---|---|---|---|---|---|
| P | V | P | P | P | P | P | P | P | F | P |

*Cross-reference — CRS:* depends on ['NOE']; required by —; independent of 12 claims (ADJ, BAL, CDC, PUR, PRO…).


## The exact V₄

**V4I — The exact V₄** (§5, Theorem 5.4, §5.6 P2-I). Under independence, the only admissible linear maps are diagonal; their sign-involutions form the Klein four-group exactly — no swap, no braid.


*Perspective visibility — V4I (executed, S_666bf26b7779 configs):*

| FULL | P1 | P2-I | CLASSICAL | PROB | NO-CODEC | NO-ANCHOR | ONE-OP | NO-NEG | SING-BASIS | NOISY-LOCK |
|---|---|---|---|---|---|---|---|---|---|---|
| P | V | P | P | P | P | P | P | V | P | P |

*Cross-reference — V4I:* depends on ['NOE']; required by ['D4C', 'PHS', 'RLS', 'T53']; independent of 8 claims (ADJ, BAL, CDC, CRS, PUR…).


# Part 3 — Layer 2


## The involution coincidence ≡ The classical section — one structure

**L26 — The involution coincidence** (Lemma 2.6). On the classical section, constrained negation equals the pin-swap — they coincide iff the section is exactly f = −id.

**LOC — The classical section** (Lemma 2.6, §5.8b). The inverse-locked locus (u, −u) is exactly c ≡ 0: the balance channel embedded in the pair; classical logic with the purchased axis off.

*Verdict (S_666bf26b7779, exhaustive): TRUTH-INTRINSIC — zero separators of any kind; co-movement 2304/2304 = 1.00. Closure-under-break: every perturbation breaks the loop coherently, with kind-structure inside the co-movement (e.g. noisy lock: U vs F). ∀-over-declared-spaces; strengthens with each space survived; never closes.*


*Perspective visibility — L26 (executed, S_666bf26b7779 configs):*

| FULL | P1 | P2-I | CLASSICAL | PROB | NO-CODEC | NO-ANCHOR | ONE-OP | NO-NEG | SING-BASIS | NOISY-LOCK |
|---|---|---|---|---|---|---|---|---|---|---|
| P | V | P | P | P | P | P | P | P | P | F |

*Perspective visibility — LOC (executed, S_666bf26b7779 configs):*

| FULL | P1 | P2-I | CLASSICAL | PROB | NO-CODEC | NO-ANCHOR | ONE-OP | NO-NEG | SING-BASIS | NOISY-LOCK |
|---|---|---|---|---|---|---|---|---|---|---|
| P | V | P | P | P | P | P | P | P | P | U |

*Cross-reference — L26:* depends on ['NOE', 'RLS']; required by ['PHS', 'RLS', 'T53']; independent of 8 claims (ADJ, BAL, CDC, CRS, PUR…).

*Cross-reference — LOC:* depends on ['NOE', 'RLS']; required by ['PHS', 'RLS', 'T53']; independent of 8 claims (ADJ, BAL, CDC, CRS, PUR…).


## The classical rails

**RLS — The classical rails** (§5.7 worked rails). The locus endpoints are T and F; composed NOT exchanges them; independent negation at a rail lands on conflict. The rails are a compactification fact, detachable from the section.

*Characteristic-break coincidence with ['L26', 'LOC'] (shared break in the dep digraph); separated in-space — see ledger.*


*Perspective visibility — RLS (executed, S_666bf26b7779 configs):*

| FULL | P1 | P2-I | CLASSICAL | PROB | NO-CODEC | NO-ANCHOR | ONE-OP | NO-NEG | SING-BASIS | NOISY-LOCK |
|---|---|---|---|---|---|---|---|---|---|---|
| P | V | P | P | P | P | P | P | V | P | U |

*Cross-reference — RLS:* depends on ['L26', 'LOC', 'NOE', 'V4I']; required by ['L26', 'LOC', 'PHS', 'T53']; independent of 7 claims (ADJ, BAL, CDC, CRS, PUR…).


## The braided V₄ (D₄)

**D4C — The braided V₄ (D₄)** (Theorem 5.4, Remark 5.5). Composed reading licenses the swap; ⟨negate-one, swap⟩ = D₄, the central extension of V₄ by the reversible twist [N,S] = −id.


*Perspective visibility — D4C (executed, S_666bf26b7779 configs):*

| FULL | P1 | P2-I | CLASSICAL | PROB | NO-CODEC | NO-ANCHOR | ONE-OP | NO-NEG | SING-BASIS | NOISY-LOCK |
|---|---|---|---|---|---|---|---|---|---|---|
| P | V | V | P | P | P | P | P | V | P | P |

*Cross-reference — D4C:* depends on ['NOE', 'V4I']; required by ['PHS', 'PRO', 'PUR']; independent of 8 claims (ADJ, BAL, CDC, CRS, LOC…).


# Part 4 — Layer 3


## The prohibition ≡ The differential purchase — one structure

**PRO — The prohibition** (§3, §5.8a). Pinning the purchased axis (normalization) conflates conflict with ignorance; collapse is an arity-mismatched decode; probability is the c-pinned slice.

**PUR — The differential purchase** (§5.7). Encoding one channel over two pins gains the conflict/ignorance axis: d carries the balance, c is the purchased mass axis.

*Verdict (S_666bf26b7779, exhaustive): EXPRESSIBILITY-INTRINSIC — zero separators; co-movement 2560/2560 = 1.00; but PRO is never F anywhere in the space: a theorem, truth-stable wherever statable. Mutual constitution at the statability level, one-way at the truth level: interventions de-state the theorem rather than falsify it. ∀-over-declared-spaces; open-by-design.*


*Perspective visibility — PRO (executed, S_666bf26b7779 configs):*

| FULL | P1 | P2-I | CLASSICAL | PROB | NO-CODEC | NO-ANCHOR | ONE-OP | NO-NEG | SING-BASIS | NOISY-LOCK |
|---|---|---|---|---|---|---|---|---|---|---|
| P | V | V | P | V | P | P | P | P | P | P |

*Perspective visibility — PUR (executed, S_666bf26b7779 configs):*

| FULL | P1 | P2-I | CLASSICAL | PROB | NO-CODEC | NO-ANCHOR | ONE-OP | NO-NEG | SING-BASIS | NOISY-LOCK |
|---|---|---|---|---|---|---|---|---|---|---|
| P | V | V | P | F | P | P | P | P | P | P |

*Cross-reference — PRO:* depends on ['D4C', 'NOE']; required by —; independent of 10 claims (ADJ, BAL, CDC, CRS, LOC…).

*Cross-reference — PUR:* depends on ['D4C', 'NOE']; required by —; independent of 10 claims (ADJ, BAL, CDC, CRS, LOC…).


## The De Morgan requirements

**T53 — The De Morgan requirements** (Theorem 5.3). NOT(AND) ≡ OR requires two operations (one collapses OR into AND) and the inverse-lock (the classical section).


*Perspective visibility — T53 (executed, S_666bf26b7779 configs):*

| FULL | P1 | P2-I | CLASSICAL | PROB | NO-CODEC | NO-ANCHOR | ONE-OP | NO-NEG | SING-BASIS | NOISY-LOCK |
|---|---|---|---|---|---|---|---|---|---|---|
| P | V | P | P | P | P | P | F | V | P | F |

*Cross-reference — T53:* depends on ['L26', 'LOC', 'NOE', 'RLS', 'V4I']; required by —; independent of 8 claims (ADJ, BAL, CDC, CRS, PUR…).


## The phase support theorem

**PHS — The phase support theorem** (§5.8c, §8.5–8.6). The extension class (the phase bit) is trivial exactly on the classical section and nontrivial exactly off it; a single pin has no phase.


*Perspective visibility — PHS (executed, S_666bf26b7779 configs):*

| FULL | P1 | P2-I | CLASSICAL | PROB | NO-CODEC | NO-ANCHOR | ONE-OP | NO-NEG | SING-BASIS | NOISY-LOCK |
|---|---|---|---|---|---|---|---|---|---|---|
| P | V | V | V | P | P | P | P | V | P | U |

*Cross-reference — PHS:* depends on ['D4C', 'L26', 'LOC', 'NOE', 'RLS', 'V4I']; required by —; independent of 7 claims (ADJ, BAL, CDC, CRS, PUR…).


---

# Glossary (computed)

**The De Morgan requirements** [T53] — NOT(AND) ≡ OR requires two operations (one collapses OR into AND) and the inverse-lock (the classical section). *(Layer 3; Theorem 5.3)*

**The Noether pairings** [NOE] — The squeeze conserves mass; the common translation conserves bias — the two charges of the pair's symmetry flows. *(Layer 0; §11.8, OB-7)*

**The balance channel** [BAL] — A single pin's real component holds the balance of the evidence, read relative to its frame's identity element; conflict is inexpressible. *(Layer 1; §5.7)*

**The braided V₄ (D₄)** [D4C] — Composed reading licenses the swap; ⟨negate-one, swap⟩ = D₄, the central extension of V₄ by the reversible twist [N,S] = −id. *(Layer 2; Theorem 5.4, Remark 5.5)*

**The chart adjunction (exp ⊣ log)** [ADJ] — The two per-pin charts — semiring magnitudes and the signed line — form an adjoint equivalence; the codec pair whose round-trips are identities. *(Layer 0; §2, Lemma 2.5b)*

**The classical rails** [RLS] — The locus endpoints are T and F; composed NOT exchanges them; independent negation at a rail lands on conflict. The rails are a compactification fact, detachable from the section. *(Layer 2; §5.7 worked rails)*

**The classical section** [LOC] — The inverse-locked locus (u, −u) is exactly c ≡ 0: the balance channel embedded in the pair; classical logic with the purchased axis off. *(Layer 2; Lemma 2.6, §5.8b; truth-intrinsic circle member)*

**The codec contract** [CDC] — Ring or semiring encoding is indifferent iff encode matches decode; frame mismatch silently flips balance; negative+semiring is ill-typed. *(Layer 1; §5.7, Caveat 2.4a)*

**The crossbar** [CRS] — (mass, bias) = (E⁺+E⁻, E⁺−E⁻) is an invertible change of basis on the pair. *(Layer 1; §4)*

**The differential purchase** [PUR] — Encoding one channel over two pins gains the conflict/ignorance axis: d carries the balance, c is the purchased mass axis. *(Layer 3; §5.7; expr-intrinsic circle member)*

**The exact V₄** [V4I] — Under independence, the only admissible linear maps are diagonal; their sign-involutions form the Klein four-group exactly — no swap, no braid. *(Layer 1; §5, Theorem 5.4, §5.6 P2-I)*

**The involution coincidence** [L26] — On the classical section, constrained negation equals the pin-swap — they coincide iff the section is exactly f = −id. *(Layer 2; Lemma 2.6; truth-intrinsic circle member)*

**The phase support theorem** [PHS] — The extension class (the phase bit) is trivial exactly on the classical section and nontrivial exactly off it; a single pin has no phase. *(Layer 3; §5.8c, §8.5–8.6)*

**The prohibition** [PRO] — Pinning the purchased axis (normalization) conflates conflict with ignorance; collapse is an arity-mismatched decode; probability is the c-pinned slice. *(Layer 3; §3, §5.8a; expr-intrinsic circle member)*


# Cross-Reference Index (computed)

| claim | layer | depends on | required by | circle |
|---|---|---|---|---|
| ADJ | 0 | — | BAL | — |
| BAL | 1 | ADJ, CDC | CDC | — |
| CDC | 1 | BAL | BAL | — |
| CRS | 1 | NOE | — | — |
| PUR | 3 | D4C, NOE, PRO | PRO | PRO ≡ PUR |
| PRO | 3 | D4C, NOE, PUR | PUR | PRO ≡ PUR |
| LOC | 2 | L26, NOE, RLS | L26, PHS, RLS, T53 | L26 ≡ LOC |
| L26 | 2 | LOC, NOE, RLS | LOC, PHS, RLS, T53 | L26 ≡ LOC |
| T53 | 3 | L26, LOC, NOE, RLS, V4I | — | — |
| V4I | 1 | NOE | D4C, PHS, RLS, T53 | — |
| D4C | 2 | NOE, V4I | PHS, PRO, PUR | — |
| PHS | 3 | D4C, L26, LOC, NOE, RLS, V4I | — | — |
| RLS | 2 | L26, LOC, NOE, V4I | L26, LOC, PHS, T53 | — |
| NOE | 0 | — | CRS, D4C, L26, LOC, PHS, PRO, PUR, RLS, T53, V4I | — |

*Independence count: 62 of 91 pairs carry no dependence in either direction (S_666bf26b7779).*