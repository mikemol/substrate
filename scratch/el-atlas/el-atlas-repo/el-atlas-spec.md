# The EL-Atlas

**A paraconsistent evidence logic over exp/log charts, without probability**

Specification — draft 18 (CHIP-(N+1), deliberately non-closed)

---

## 0. Status, charter, and reading discipline

This document is the first self-contained witness of a structure previously
derived across working sessions. It is written under two disciplines:

**The realizability charter.** If a distinction is real, it must be
constructible; if constructible, behaviorally reachable; if reachable,
observable; if observable, coverable. A claim this document cannot construct
internally is not a claim of this document. Existence claims are
witness-bearing (BHK / intuitionistic): to assert a thing, exhibit it. A
claim with no witness is neither asserted nor denied — it is registered as
**undetermined** in the obligation register (§15).

**Deliberate non-closure.** This specification does not pretend to be a
disk. Its notion graph has one genuine loop (H₁ rank 1, see §7), centered
on the carrier's numeric range, which is committed here as a **free
parameter with a stated constraint contract** rather than a fixed value.
The document tracks its own residue: each open item in §15 is recorded as
an (evidence-for, evidence-against) pair — the spec applies its own logic
to itself. Full closure is not a goal; tracked openness is.

**Notation is introduced before use.** Claims marked **[W]** are witnessed
(derived and confirmed in the source record). Claims marked **[S]** are
synthesis: faithful assembly of witnessed pieces into one statement, where
the assembly itself is new. Claims marked **[C]** are conjectures with
proposed tests. Nothing else is asserted.

---


**Remark 0.x (the indexed-verdict discipline is a truth-definition
discipline).** Every verdict in this document is indexed to a declared
space ("unseparated-in-S_…"; ∀-over-declared-spaces; never closes). This
is Convention-T-shaped practice: a truth predicate is only ever defined
relative to a named metalanguage, and the harness's space manifest IS
that metalanguage, declared rather than presupposed. The scrutiny strata
(knob values → knob set → test semantics → claim formalization) form the
object/meta tower; "no unindexed verdicts" is Tarskian relativization
adopted as policy. The deflationary boundary is respected in both
directions: verdicts are decidable because they are syntactic facts
about declared spaces, and nothing in this document claims a truth
predicate for the language it is itself written in. (theory-threads §1;
instrument provenance in the run headers.) **[S]**
## 1. The carrier: two independent accumulators

**Definition 1.1 (evidence increments and totals).** Distinguish two types:

- An **increment** ε ≥ 0: one finding, for or against.
- A **total** E ≥ 0: an accumulated quantity of increments.

The accumulation operation has signature `increment × total → total`.
Increments and totals are not interchangeable; an English sentence that
says "evidence" must resolve to one or the other. **[W]** (forced by the
place-structure cross-check; "evidence" is mass-noun ambiguous and the
spec is not).

**Definition 1.2 (the carrier).** The carrier of the logic is a pair

> **(E⁺, E⁻)**

of totals: E⁺ accumulates evidence-for, E⁻ accumulates evidence-against.
Also written (t, f) in earlier derivations. The pair lives in the quadrant
[0, ∞]². **[W]**

**Law 1.3 (independence).** E⁺ and E⁻ are two *independent additive
accumulators*. Each pin accumulates by summing its own increments. They are
not the numerator and denominator of anything. No operation of the logic
reads one pin while writing the other. **[W]**

**Law 1.4 (accumulation is sum; the sum is a choice of operation).**
Accumulation on a pin is additive in whatever carrier presentation is in
use. "Logspace sum" versus "semiring sum" (ordinary +, or a semiring ⊕
such as max or logsumexp) is a *choice of which sum* — both constructible,
neither canonical. There is no underlying multiplication being linearized;
the log is one constructible view, not a forced bridge. **[W]** (this
corrects an earlier error; see Provenance, P-2).

**Interpretive regions** (regions, not posited labels — see §4, §9):

- E⁺ high, E⁻ low: supported.
- E⁺ low, E⁻ high: refuted.
- both high: active disagreement — high instability, highly curved local
  space (§8).
- both low: lack of knowledge.

**[W]**

---

## 2. The atlas: one value space, two charts

The one-parameter value space underlying each pin — and underlying the
pre-split logic — has two presentations related by exp/log. This is the
atlas the title names.

**Definition 2.1 (additive chart 𝔸).** The extended real line
x ∈ [−∞, +∞], with:

- +∞ = truth, −∞ = falsity,
- neutral point **0** = maximal ignorance / balance,
- negation **not(x) = −x**: reflection through 0,
- truth-degree = signed distance from the origin,
- evidence accumulates **additively**. **[W]**

**Definition 2.2 (multiplicative chart 𝕄).** The semiring [0, +∞] with
multiplicative ideal at 1:

- +∞ = truth, 0 = falsity,
- neutral point **1** (the image of 0 under exp),
- negation **not(y) = 1/y**: reflection through 1,
- evidence accumulates **multiplicatively**. **[W]**

**Definition 2.3 (the transition map).** exp : 𝔸 → 𝕄 and log : 𝕄 → 𝔸
are the chart transitions. The two charts present *the same object*; no
statement of this logic is chart-essential. **[W]**

**Lemma 2.4 (negation is chart-local and conjugate).** Negation is
reflection through *each chart's own* neutral point. The two charts carry
**two genuinely different involutions, each appropriate to its own
algebraic structure**, and exp/log conjugate them:

- **Additive chart 𝔸 = [−∞, +∞] (the signed line):** not_𝔸(u) = −u, sign
  negation, reflection through **0**, fixed point {0}. This is the
  involution that acts on signed quantities, because 𝔸 is where signed
  quantities live.
- **Multiplicative chart 𝕄 = [0, ∞] (a semiring, *not* a ring):**
  not_𝕄(y) = 1/y, reflection through **1**, fixed point {1}. The
  reciprocal is the **semiring** negation; the carrier has no negative
  numbers, so 1/y is defined and involutive on all of [0, ∞] (with
  1/0 = ∞, 1/∞ = 0).

> not_𝕄(y) = 1/y = exp(−log y), i.e. not_𝕄 = exp ∘ not_𝔸 ∘ log.

The flip −log y ↦ +log y in 𝔸 *is* y ↦ 1/y in 𝕄. **[W]**

*Proof.* Direct computation: exp(−log y) = y⁻¹; the neutral points
correspond (0 ↦ 1) and each is the unique fixed point of its chart's
involution. ∎

**Caveat 2.4a (do not put 1/y on a ring).** The reciprocal involution is
the negation **of the semiring [0, ∞]**, not a reciprocal on a field. It
must not be extended to negative or complex arguments: the signed
quantities of this logic live in the *additive* chart (via log, which
maps the semiring [0, ∞] onto the whole signed line [−∞, +∞]), where the
appropriate involution is sign negation. Asking for "the fixed points of
1/y on ℂ" is a category error — it imposes a field structure 𝕄 does not
have. There is one semiring involution (1/y, fixed point 1) and one
signed-line involution (−u, fixed point 0); they are conjugate, and
neither is "1/x on a ring." **[W]** (records the correction that retired
the OB-9 complexification run; see OB-9.)

**Remark 2.5 (transport).** Lemma 2.4 is the pattern for every law of the
logic: prove in one chart, conjugate by exp/log, obtain the other chart's
form. The "same object, two charts" claim is a transport-along-equivalence
statement (see §10, Martin-Löf entry). **[S]**

**Lemma 2.5b (the chart adjunction — exp ⊣ log).** The two charts are
related by the adjoint pair **exp : 𝔸 → 𝕄** and **log : 𝕄 → 𝔸**, with
unit and counit log ∘ exp = id_𝔸 and exp ∘ log = id_𝕄. On the relevant
domains this is an **adjoint equivalence** (both round-trips are
identities), which is the precise content of "the same object in two
charts." **[W]** (round-trips verified).

On the (mass, bias) basis the adjunction acts **losslessly on both
coordinates at once**:

> bias b = u₊ − u₋  ⟼  E₊/E₋ = exp(b)   (the **ratio** is the
> multiplicative-chart *image* of bias)
> mass m = u₊ + u₋  ⟼  E₊·E₋ = exp(m)   (the **product** is the image
> of mass)

Both coordinates cross; neither is discarded; log brings both back. **[W]**

**Remark 2.5c (ratio-as-collapse vs ratio-as-chart-image — the keystone
distinction, stated explicitly).** The expression E₊/E₋ appears in two
roles that must never be conflated:

- **As a value (forbidden, §3):** reducing the pair *to* the ratio,
  discarding the orthogonal mass coordinate. This is lossy, one-way, and
  cannot distinguish both-high from both-low (Lemma 3.2). *Collapse =
  project and forget.*
- **As a chart image (fine, Lemma 2.5b):** E₊/E₋ = exp(b) is the
  multiplicative-chart presentation of the *bias* coordinate, with mass
  simultaneously present as the product axis E₊·E₋ = exp(m). Nothing is
  discarded; the map is invertible. *Chart-cross = transport and keep.*

The difference is not the formula — it is identical in both — but
**whether the orthogonal axis survives the operation.** The prohibition
of §3 forbids the first role and is silent on the second. A ratio that is
one half of an invertible (mass, bias) ↔ (product, ratio) chart map is not
a collapse; it is the adjunction acting. **[W]** (This corrects a
conflation that is easy to commit precisely because the surface syntax is
the same; see §11.3 / OB-5, where the Wheatstone galvanometer reads the
*chart-image* ratio, not the *collapse* ratio.)

**Lemma 2.6 (the locked locus).** The one-parameter value space embeds in
the carrier plane as the **inverse-locked locus**: pairs of the form
(u, −u) in additive presentation, equivalently (y, 1/y) in multiplicative
presentation. On this locus — and only there — negating one pin coincides
with swapping the pins:

> on (u, −u): u ↦ −u  ≡  (u, −u) ↦ (−u, u).

Off the locus, negate-a-pin and pin-swap are distinct involutions. **[S]**
(assembled from the witnessed derivation that negate-a-pin ≡ pin-swap
*requires* inverse-locked pins, plus Law 1.3 that the general pins are
independent.)

The paraconsistent move of §1 is precisely the passage from the locked
line to the full plane: the ideal of the second term is *not* of the first
term's ideal, and then the lock is released. **[W]**

---

## 3. The prohibition: no quotient, no odds, no probability

This is the load-bearing constraint of the entire construction. It is
stated as a hard law, with its justification as a lemma.

**Law 3.1 (no-collapse).** The pair (E⁺, E⁻) is never quotiented to a
ratio, an odds, a normalized probability, or any single decision
coordinate, by any operation *of the logic*. Forming E⁺/E⁻, or normalizing
by E⁺+E⁻, is a **forced Boolean resolution under a probability measure
over a field of interpretations** — it collapses the field to a point on
an odds line or [0,1]. Odds space is where one goes *to decide*; it is not
where the logic lives. Probability may be *recovered* from the carrier by
an explicit, external, named collapse — it is never the semantics. **[W]**

**Lemma 3.2 (ratio blindness).** The quotient q(E⁺, E⁻) = E⁺/E⁻ cannot
distinguish "both high" from "both low": q(a, a) = 1 for every a. Its
fibers are rays through the origin; the quotient kills exactly the mass
coordinate m = E⁺ + E⁻ (§4). Since "both high" (active disagreement) and
"both low" (ignorance) are distinct interpretive regions of Definition
1.2, any collapsed representation that identifies them is unsound for this
logic. **[W]** *Proof.* Immediate from q's homogeneity of degree 0. ∎

**Definition 3.3 (balance is a non-operation).** "Balance of evidence" —
the phrase used informally for this logic's stance — does **not** name an
operator. There is no balance function. Balance is the *state of declining
to compute* the quotient of Law 3.1: both accumulators held live,
unreconciled. (Formal renderings of the spec contain no balance relation;
the English word marks a refusal, and this definition makes the refusal
explicit so the word cannot be re-read as arithmetic.) **[W]**

**Remark 3.4 (the slogan and its status).** The informal gloss is
"quantum superposition without collapse": always a balance of evidence,
never a likelihood of outcome. The literal commitments of the slogan are
exactly Laws 1.3 and 3.1 plus the unnormalized-pair reading of §8. Whether
the quantum framing is *normative* (amplitudes that genuinely interfere,
requiring a phase-composition law) or *illustrative* is undetermined —
obligation OB-2, §15. **[W]** for the slogan; status open.

**Remark 3.5 (projection plurality).** The corpus consolidation (App. A,
D-1) sharpens Law 3.1 from one prohibition into a discipline: there is
**no single privileged projection down to real**. At least four distinct
scalar shadows of the carrier exist — total commitment (mass), differential
tilt (bias), unsigned decisiveness, equivalent single-conductor collapse —
and the bridge adds a fifth, the ratio/null-test shadow. Each is a
legitimate *external, named* projection; conflating them, or treating any
one as "the" value of the pair, is the collapse Law 3.1 forbids. The
prohibition is not "never project" but "every projection is plural,
external, and named." **[W]** (corpus-witnessed, D-1 §C4.)

**Remark 3.6 (annihilation is a collapse; the resolution is
representational).** The corpus's zero-divisor design move — *"zero-divisors
can be resolved through representation-as-rationals (the number becomes
structured)"* — is this section's prohibition stated at the multiplicative
level. Annihilation (a · b = 0 with a, b ≠ 0) destroys the factors'
structure exactly as the quotient destroys the pair's; the resolution in
both cases is to **upgrade the representation so the operation's input
structure remains addressable**: keep the formal pair instead of
evaluating. The carrier's refusal of E⁺/E⁻ and the zero-divisor
resolution by formal quotient are one design principle — when an
operation would lose information, do not perform it; encode it. **[S]**
*(Deployed instance: the Nedge G-Value Calculus is exactly this
arithmetic with the quotient taken — §5.7e, lift theorem.)*

---

## 4. The crossbar: mass/bias change of basis

**Definition 4.1 (mass and bias).** In the additive (log-carrier)
presentation of the pins, define the change of basis

> **m = E⁺ + E⁻** (mass: total evidence, presence-of-evidence)
> **b = E⁺ − E⁻** (bias: net judgement)

**[W]**

**Law 4.2 (b is not a log-odds).** The bias coordinate b = t − f must not
be read as a log-odds. Reading it as one discards the mass axis (the
diagonal), which Lemma 3.2 shows is exactly the information the
construction exists to keep. b is net judgement *within* an uncollapsed
pair, not a disposition over outcomes. **[W]**

**Proposition 4.3 (the four regions are the crossbar's corners).** The
classical four values arrive as *derived regions*, not posited labels:

- T (supported) and F (refuted): the two ends of the **bias axis**.
- B (conflict) and N (absence): the two ends of the **mass axis** — both
  have b ≈ 0 and differ only in m. Conflict is high-mass-zero-bias;
  absence is low-mass-zero-bias.

The crossbar (b, m) = (judgement, total evidence) is primary; the four
points are corners of a geometry. This is the deliberate departure from
Belnap–Dunn, which takes the four points as primary (§9, §10). Flat
labels erase precisely the low-information-balance vs
high-information-balance distinction that the mass axis carries. **[W]**

---

## 5. The involutions: V₄ and De Morgan as pin-swap

**Definition 5.1 (the two generating involutions).** On the carrier:

- **negate-a-pin**: x ↦ −x on one coordinate (additive presentation);
  one C₂.
- **pin-swap**: (E⁺, E⁻) ↦ (E⁻, E⁺); a different C₂. On the bias
  coordinate, swap acts as b ↦ −b.

Their product is the diagonal involution; the two together generate the
Klein four-group **V₄**. **[W]**

**Theorem 5.2 (De Morgan is the swap).** The pin-swap *is* De Morgan —
the involution that exchanges ∧ and ∨. NOT, read on the pair, is the swap;
read on the locked locus (Lemma 2.6), it is the group inverse x ↦ x⁻¹
(equivalently u ↦ −u). De Morgan being one of the crossbar's two
generating involutions is why it sits as a C₂ inside V₄. **[W]**

**Theorem 5.3 (the carrier condition).** NOT(AND) ≡ OR holds **iff both**
of the following hold; each alone fails:

1. **Inverse-locked pins** (on the locus where negate-a-pin must equal
   pin-swap): pins of the form (x, 1/x) / (u, −u). Without the lock, the
   two involutions are simply different maps and the identity is false.
2. **Two log-linked operations** (a semiring carrier, §6). With only one
   operation and pure inversion, define OR(a,b) := 1/((1/a)(1/b)) = a·b:
   the product is **self-dual** under inversion, AND = OR collapse, and
   there is nothing for De Morgan to exchange.

**[W]** (both failure directions were exhibited in the source
derivation; the collapse in (2) was caught mid-derivation and is recorded
as Provenance P-3.)

---

**Theorem 5.4 (representation-dependence of V₄ — a corrected bug).** The
abstract V₄ of this section is exact, but *which concrete involutions
generate it depends on the representation*, and one of this spec's earlier
claims was false:

- **On the full pin plane**, single-pin-negate N and pin-swap S do **not**
  commute: ⟨N, S⟩ ≅ **D₄** (order 8), N·S is a 90° rotation of order 4, and
  the earlier claim "their product is the diagonal involution" is **false**
  there. **[W]** (the error was caught by an external computation quoted by
  the user; verified.) However: [N, S] = −id (negate-both), which is
  **central, order 2, and reversible** — so N and S commute *up to* the
  central twist, giving the central extension
  **1 → Z₂ → D₄ → V₄ → 1**, with V₄ surviving as the quotient. The exact
  V₄ inside the plane is the **diagonal subgroup {id, N₊, N₋, −id}** (the
  two single-pin negations, negate-both, identity), which commutes on the
  nose. **[W]**
- **On the four-corner (tetrahedron) representation** — the crossbar's four
  corners as the four vertices — the diagonal subgroup acts as exactly the
  three double-transpositions + id: the **normal V₄ of S₄**, commuting
  exactly, with the antipode −id = (Q₁Q₃)(Q₂Q₄) exchanging opposite
  corners. Pin-swap S acts there as a **single transposition** — a frame
  element, outside the content V₄. Conjugation of S₄ on this V₄ has image
  the **full S₃ = Aut(V₄)** (transitively permuting the three involutions)
  and kernel V₄ itself: **S₄ = V₄ ⋊ S₃ = Hol(V₄)**, the holomorph. **[W]**
- **The linear obstruction (why the pin chart cannot see the frame).** Any
  invertible linear map of the pin plane satisfies M(−v) = −M(v), so its
  induced corner permutation commutes with the antipode; the centralizer of
  the antipode in S₄ is exactly D₄. Hence the pin chart can linearly
  realize **only** D₄ — the braid-thickened V₄ — and the axis-mixing
  3-cycles of the S₃ frame are **not realizable by any linear map of the
  plane**. The full frame exists only on the corner representation. **[W]**

**Remark 5.5 (the braid reading — the verdict the computation invites and
must refuse).** "⟨N, S⟩ = D₄, not V₄" is computationally correct and
judgmentally a collapse: it discards (i) the central twist's
*reversibility* — N·S = (−id)·S·N is a crossing sign (the anticommutation
of Pauli X and Z; a symmetric-with-sign braiding), not an obstruction;
(ii) the quotient V₄, intact as D₄/center; (iii) the
representation-dependence — on the tetrahedron representation V₄ and its
full S₃ frame are exact. Forgetting the crossing sign is the braid →
permutation projection; the sign is *remembered, reversible* structure
riding on top of V₄, not a refutation of it. On the inverse-locked locus
(Lemma 2.6) the twist degenerates and V₄ is exact even in the pin chart —
which is precisely why Theorem 5.3 demands the inverse-lock. **[W]**

### 5.6 The pin-scenario catalog — what "the pin plane" was

Theorem 5.4 used "the pin plane" informally, and the phrase smuggled in a
scenario. Stated precisely: **a single pin read in isolation is one linear
axis of information**, readable in two charts — as the semiring 𝕄 = [0,∞]
(magnitudes, positive values only) and as the signed line 𝔸 = [−∞,+∞]
(positive and negative values), with **exp/ln as the magnitude mapping
between the two structures**. The atlas of §2 is *per-pin* structure. Two
pins are then either **independent** (Law 1.3: no cross-read) or have
**meaning composed** — a conjugatively-encoded interdependency between
both pins that is realized on reading. Which operations exist, and which
symmetry is visible, is a function of this **reading relation**, not of
the pins themselves. The catalog (each row's symmetry claim **[W]**,
verified):

| scenario | pins | interrelation | supported readings | frames presented | visible symmetry |
|---|---|---|---|---|---|
| **P1** | 1 | — | accumulate (write); **balance read** (net judgement, identity-anchored) in either codec: 𝕄 magnitude or 𝔸 signed via ln | the per-pin atlas (exp ⊣ ln) | **C₂** (the chart involution 1/y ↔ −u). Cannot express conflict vs ignorance (§5.7) |
| **P2-I** | 2 | independent (Law 1.3) | per-pin P1 reads only; cross-reads (mass, bias) exist only as *named external projections* (Remark 3.5, mode 2) and exit this scenario | two per-pin atlases | **V₄ exact** = {id, N₊, N₋, −id}: the diagonal sign maps, the *only* linear maps respecting no-cross-read. No swap (swap is a cross-read); **no braid possible** — the braid requires the cross-read independence forbids |
| **P2-C** | 2 | meaning composed; joint linear reads | joint linear functionals: (mass, bias); modes (d, c); the swap (an operation on the *encoding*); mode transport | crossbar; differential-mode frame | **D₄** = V₄ braided by the central twist; [N, S] = −id = **the conjugate-encoding interdependency surfacing on reading** — the phase bit / extension class (Theorem 5.4). Sub-case *inverse-lock* (u, −u): one meaning over two pins; twist degenerates; V₄ exact (Lemma 2.6) |
| **P2-G** | 2 | composed + **gated** read (sign-pattern extraction, mode 3 — the first nonlinearity) | which-corner reads; perspective anchoring (the 3+1) | the four corners (Belnap as crossbar corners); the tetrahedron | **S₄ = V₄ ⋊ S₃ = Hol(V₄)**: normal V₄ exact (double-transpositions) plus the S₃ = Aut(V₄) frame. The 3-cycles are realizable at the gate level and at *no* linear level |
| **P2ⁿ** | 2ⁿ | composed pairs of composed pairs, recursively | Walsh-mode reads (RM(1,m) linear layer); wire-swap conjugation; bridge readouts (4 pins = two composed pairs: the mass/bias instrument, §11.3–11.4) | doubling tree; mode hierarchy | per-level P2-C structure iterated; overlay across towers climbs RM degree (§13.2) |

**The ladder law (the catalog's content).** Visible symmetry is purchased
by the reading relation:

> independence → **V₄** (exact, commuting, no swap)
> composition + linear joint reads → **D₄** (braided V₄; phase = the
> encoding interdependency)
> composition + gated reads → **S₄ = Hol(V₄)** (the frame unlocks)

and the consumption-mode grading (§13.1) *predicts* this ladder: degree-1
(linear) reads cap the visible symmetry at D₄; the gate — the first
nonlinearity, Mode 3 — is exactly what unlocks the corner frame and its
S₃. The frame was never missing; it was priced in a currency (nonlinear
reads) that the linear scenarios do not spend. **[W]**

**Re-scoping Theorem 5.4.** "The pin plane" = scenario **P2-C**: the joint
signed-chart read of two *meaning-composed* pins. The D₄ result is a
theorem about that reading relation. The spec's §5 V₄ lives in **P2-I**
(generators {N₊, N₋}, diagonal — the bug fix lands here: the correct
independent-scenario generator pair was never {negate-one, swap}) and in
**P2-C on the locus**; the holomorph lives in **P2-G**. All three are
correct *in their scenario*; draft 13's error was scoping, and the quoted
"D₄ not V₄" verdict was a scenario-conflation in the other direction.
**[W]**

### 5.7 The balance channel and the differential encoding (the catalog's semantics)

**A single pin is the balance channel.** Reading the real component of a
single pin holds **the balance of the evidence** — net judgement, read
*relative to the identity element of its declared frame* — and cannot
express internal conflict. The expressivity limit of P1 is now exact: the
single pin says how far for-vs-against nets out; it cannot say whether a
given net came from pure refutation or from refutation amid heavy
conflict, nor distinguish ignorance from deadlocked conflict (both net to
the identity). **[W]** (witnessed: (0,5) and (5,10) have the same balance
−5; (0,0) and (7,7) both balance to 0; the pairs separate only on the
gained axis.)

**The chart is a codec, and balance is identity-anchored.** The real
component can be encoded to the ring (logspace, identity 0, negatives
licensed) or the semiring (exp-space, identity 1, positives only) — *it
does not matter which, so long as the encoding matches the decoding for
the normal operations* (the ones the exp/ln conjugation transports:
accumulate, negate, compare-to-identity). The valid (stored sign ×
declared frame) cells are exactly three: negative+log, positive+log,
positive+semiring; **negative+semiring is ill-typed** (the semiring has
no negatives — Caveat 2.4a, stated on the value side). Frame mismatch is
*silent corruption of balance*: a semiring-stored "against" (value below
1) decoded in the log frame reads as "for" (a positive number). The
identity element is the anchor; remembering the frame *is* remembering
where balance sits. **[W]**

**Codec family extension (corpus import).** The consolidation report's C3
adds a third valid encoding family: the **shifted log**, e ↦ ln(1 + e/κ)
(equivalently the shifted embedding e ↦ 1 + e/κ before the log), with
identity image 0 and **κ as a headroom/scale parameter** — joining ℛ and
Maslov h on OB-1's axis (§5.8g). The anchor discipline extends unchanged:
every codec family must declare its identity image. **[S]**

**The projection inventory (corpus C4: "these must not be conflated").**
There is no single privileged scalar shadow of the pair. The corpus names
five: **total commitment** (mass m), **differential tilt** (balance b),
**unsigned decisiveness** (|b| — gate-adjacent, mode 3), **single-conductor
collapse** (read one pin), and the bridge's **ratio/null-test** shadow
(level 2). The worked-rails result locates exactly where they coincide:
at the saturated rails, and only there — in the interior they diverge,
which is why conflating them is the C4 error. **[S]**

**A pair of pins: two channels, or one channel differentially encoded.**
The real components of a pair either hold **two channels' balances
independently** (P2-I: two propositions, diagonal operations only), or
hold **one channel's data as a differential encoding** (P2-C) — and the
differential encoding is not a mere re-housing: it **gains access to
measuring conflict and ignorance**, not just balancing positive against
negative. The differential mode d = u₊ − u₋ carries exactly what the
single pin held (the balance); the common mode c = u₊ + u₋ is the
*gained* axis (mass), separating pure-refutation from
refutation-amid-conflict and ignorance from deadlocked conflict. **The
carrier (E⁺, E⁻) is therefore, in encoding terms, the differential
encoding of the balance channel** — §1's pair restated as a codec: one
proposition, two pins, with the encoding purchasing the mass axis. **[W]**

**The recursion.** Each composition level repeats the purchase: composing
two encoded channels re-expresses their balances as the next level's
differential modes and *gains* a new common mode (§11.10's "what a level
cannot read as signal is re-encoded as the next level's channel"). Four
pins as two composed pairs is the Wheatstone instrument: the
pair-of-pairs' differential is the galvanometer (bias), its common mode
the supply (mass) — the bridge is the level-2 instance of the same gain.
**[S]**

**The worked rails, re-grounded.** The four presentations of
refutation-false (single pin −∞ signed; single pin 0 semiring; pair
(−∞, +∞) signed; pair (0, +∞) semiring) are one semantic point under
(chart × pin-count): the chart pairs are codec transports (lossless;
ln 0 = −∞); the pin-count pairs are the balance channel vs its
differential encoding. The single-pin reading −∞ is a *genuine* balance
refutation ("infinitely against"), not an empty accumulator; what it
cannot certify is the **mass** behind the net — "refutation false" in
full (zero support *and* saturated counter-evidence, F = (0, ∞), the
bottom endpoint of the inverse-locked locus) is expressible only in the
differential encoding. At the rails the natural projections coincide
(which is why the single-pin read feels unambiguous there); in the
interior they diverge. Classical truth values are the locus rails;
locus-constrained NOT exchanges them (F → T); *independent* single-pin
negation at the F rail leaves the locus and lands on conflict, B — the
classical NOT is the composed one (Theorem 5.3's inverse-lock as rail
dynamics). **[W]**

### 5.7e Famous instance: the Nedge G-Value Calculus (the quotient shadow, lifted)

The corpus's own Nedge program (Appendix B.0; N-series decomposition,
`nedge-decomposition.md`) carries a quantitative semantic engine — the
**G-Value Calculus** — whose Master Specification defines: a scalar
G(P) ∈ [0,∞] ("evidence strength"; rails 0 and ∞); G_NOT(G) = 1/G;
G_AND(G₁,G₂) = G₁G₂/(G₁+G₂) (series conductance); G_OR = Σ (parallel);
DeMorgan exact; non-idempotent (AND(G,G) = G/2, OR(G,G) = 2G);
non-distributive; an "L-space" L = ln G with L_NOT = −L, L_OR = LogSumExp,
L_AND = −LogSumExp(−·), idempotence failure ±ln 2 read via Landauer;
residuated implication G_res(P⇒Q) = G(P)G(Q)/(G(P)−G(Q)) when
G(P) > G(Q), else ∞; conditional G(Q|P) = G(Q)/(G(P)+G(Q)); local
consistency G(P)·G(¬P) = 1; least-fixed-point network equilibrium; and a
confidence chart Conf(G) = G/(G+1). **[O]** (Artifact B, Sections IV–IX.)

**Declared reading (ladder law).** The source oscillates between *cost*
and *strength* labels for its rails; this import takes the **strength**
reading: G large = strong net support, G = ∞ the ⊤ rail, G = 0 the ⊥
rail, so L = ln G is the balance coordinate in standard orientation. The
cost reading is the orientation-reversed import (L ↦ −L) and changes
nothing structural; what matters is that one is declared before any
identification is made. **[S]**

The identifications, in increasing depth:

1. **The codec identification.** L-space ≅ 𝔸 and G-space ≅ 𝕄, and the
   spec's "L-space isomorphism" is Lemma 2.5b's exp ⊣ log codec formula
   for formula, identity images included (G = 1 ↔ L = 0). **[S, near-W]**

2. **The quotient shadow.** G is the odds — the ratio §3 refuses.
   G(P)·G(¬P) = 1 is the antipode constraint of a balance channel with
   **no mass axis**: G = 1 cannot distinguish massive conflict from total
   ignorance — a Lemma 3.2 instance inside Nedge's own Layer 2, while its
   Layer-3 four-valued logic (confidence × consistency) demands exactly
   the information the scalar destroys. **[S]**

3. **The lift theorem.** On formal-quotient pairs (n, d) with class n/d:
   G_OR is fraction addition, G_NOT is the swap, G_AND is swap-conjugated
   fraction addition, and DeMorgan exactness is the swap distributing.
   Non-idempotence is the **mass-growth shadow**:
   (n,d) ⊕ (n,d) = (2nd, d²) ~ 2n/d — the calculus's "resource
   sensitivity" is the quotient remembering the extruded magnitude axis
   in distorted form. **The entire G-Value Calculus is ⟨fraction-⊕, swap⟩
   on formal-quotient pairs.** **[W]** (Pilot, 2000 trials; instrumented
   as claim NGL, S_fd5ddbe7ac57. The instrument further finds {NGL, V4I}
   to be one structure: identical precondition support ⟨pair, involution,
   char 0⟩, diverging only in *kind* at characteristic 2 — the exact V₄
   is falsified there, the lift merely de-stated.)
   *Cross-reference, Remark 3.6:* representation-as-rationals is this
   lift made policy. Three positions on one move: Nedge takes the
   quotient; the corpus's rationals move works pre-quotient; the atlas
   refuses the quotient entirely.

4. **The differential reading.** G_res is a resistance **difference**:
   1/G_res = 1/G(Q) − 1/G(P), residuation adjointness exact —
   implication as a differential taken in the swap-dual chart. **[S]**

5. **The c-pinning instance.** G(Q|P) = G(Q)/(G(P)+G(Q)) is the
   L1-normalization of the pair (G(P), G(Q)) — conditional belief is a
   simplex projection; Conf(G) = sigmoid(L) is the same chart one level
   down. **[S]**

6. **The two-gate theorem (machine-found).** Nedge's four-valued gate
   (confidence × consistency = mass × conflict) and the Belnap chart
   (bias-sign × rail) are distinct four-cell gates on one carrier, and
   **either magnitude pinning degenerates the Nedge gate**: the c-pin
   (§3, §5.8a) kills the mass axis exactly; the r-pin (§5.9, PR2) leaves
   one dimension on which mass and conflict are monotonically locked. A
   four-valued logic needs the **unpinned pair** — both prohibitions bite
   it. **[W]** (Claim NVL, S_fd5ddbe7ac57: F under both pinnings, P only
   on the free carrier; separated from PUR by the r-pin slice, 3072
   truth-separators.)

**Lineage consequence** (sharpens Appendix B.0): the atlas is the
**pre-quotient of Nedge's own Layer-2 semantic engine.** Open in the
source itself: the ∨E (proof-by-cases) G-value transformation, flagged
there as "a key area for precise axiomatic definition" — the carrier
treatment is the natural candidate (the pair keeps the case-mass the
scalar loses); queued as N-series work. **[C]**

**Answered (S8, author construction; instrument v3.5a).** The flag above
is retained per the supersession-as-alias rule (S9); the answer: ∨E is
the **single/double pin split/join carrier expansion**, witnessed by the
**Wheatstone bridge**. The split is a section choice the scalar quotient
erases — splits (3,7) and (5,5) of joined G = 10 conflate in the
parallel join yet read as equal-and-opposite bridge currents (∓0.043478
against reference (2,3)). The high-impedance bridge reading is exactly
the difference of two L1-normalized conditionals (identification 5
stitched to identification 4), nulling on equal odds at any mass — the
bridge is itself a shadow-level instrument: galvanometer = bias read,
source current = mass read, the crossbar as a circuit. Classical ∨E
lives on the balance manifold, where case identity is invisible. Three
layers, one answer: packed node (storage) / split-join (arithmetic) /
bridge (measurement); the n-ary form is a lattice of exactly n−1
partition readings plus the mass channel (pack tomography — necessity
and sufficiency both pilot-witnessed). **[W]** (Claim NVE,
S_2738ddb8c926: P wherever statable; separated from NVL by 6,144
truth-separators; guards pins ≥ 2, neg, linear ops, real coefficients.
Pilots: nve-bridge, nve-alias-delta.)

### 5.8 What the codec view clarifies (a sweep)

The §5.7 semantics re-derives structure the spec previously stipulated.
Each item below is pilot-verified unless graded otherwise.

**(a) The prohibition becomes a type theorem.** Collapse = decoding a
two-mode encoding with a one-mode decoder (arity mismatch). And
**probability is the c-pinned slice of the evidence space**: normalization
does not hide mass, it *constrains the purchased axis to a constant* —
(7,7) and (0.1,0.1) both normalize to (½,½) — after which only balance
remains free, which is *why* probability is balance-only. The simplex is a
level set of c; Lemma 3.2 restates as "same d once c is pinned." §3's law
is the codec contract's theorem. **[W]**

**(b) Classical logic is the zero-mass section.** The inverse-locked locus
(u, −u) is exactly **c ≡ 0**: the single-pin balance channel embedded in
the pair — the differential encoding with the purchased axis switched off.
This *explains* (rather than stipulates): Lemma 2.6 (negate = swap on the
locus: one axis, one flip), Theorem 5.3's inverse-lock (classical De
Morgan holds exactly when c is off), and the Belnap split — **T/F are
channel-level facts** (visible to one pin) while **B/N are encoding-level
facts** (rails of the purchased axis). FDE = classical logic + the bought
axis's rails. **[W]**

**(c) Phase has a support theorem.** The D₄ twist degenerates exactly *on*
the c = 0 section (−id coincides with the swap there) and is nontrivial
exactly *off* it: **the extension class is supported precisely where mass
capacity exists. A single pin has no phase**; the classical section is
phase-free by construction. This sharpens §5.6/§8.5: phase = the encoding
interdependency, *with support = the purchased axis*. **[W]**

**(d) The read/write error taxonomy completes.** Three distinct failures:
**arity mismatch** (collapse: decode fewer modes than encoded — loses c);
**frame mismatch** (right arity, wrong identity anchor — silently flips
balance, §5.7); **range violation** (write outside the declared codec —
negative + semiring, Caveat 2.4a). These are the only failure modes the
codec contract admits, and the spec's named errors each instantiate one.
**[W]**

**(e) The instruments simplify.** Common-mode rejection acquires a
legitimacy *condition*: d-only decoding is correct iff c is declared
noise; the epistemic error is applying it where c is data — the
prohibition *is* the declaration that in evidence, c is data (sharpest
form of the §11.10 novelty seed). The §11.4 two-readout repair = restoring
decoder arity. The repeater (Witness 7.5) = a deliberate rail re-encode.
**[S]**

**(f) OB-11 sharpened to a concrete proposal.** LET_F's ○ (classicality)
= the **c-degenerate region** (the locus ∪ the rails: where the classical
section holds or the gate has committed); ● = the c-live region. The
discharge path is now a specific region-definition to test against the
LET_F axioms, not an open search. **[C]** (proposal, untested.)

**(g) OB-1 as codec headroom.** The range parameter ℛ / Maslov h reads as
the encoding's analog headroom between the rails: h → 0 = tropical
saturation = rails-only = the classical limit. The graded interior is what
finite headroom buys; OB-1's openness = the headroom is a model parameter.
**[S]**

**(h) The sweep gains a parsing column.** Goodman semiring parsing is
projection plurality for parsing: one chart, pluggable semiring, and the
semiring choice IS the quotient choice. Boolean = the classical section;
inside (probability) = the positive-rail slice; Viterbi = the idempotent
argmax pinning; the carrier semiring keeps what each discards (root mass
= the SPPF's packed multiplicity; the equal-G/different-mass conflation
is POINTWISE — at every span, not just the root). Inside × outside is
the decategorified zipper, exact precisely because context-free means
the filling family is constant over contexts. Maslov dequantization
makes the column a one-parameter family — (ℝ₊,+,×) → (ℝ,max,+) as
ħ → 0 — so Viterbi is the classical limit of inside, APSP/geodesics the
(min,+) member, and the multiplicity the idempotent member discards is
recoverable from the ħ-correction (k = exp(−(F−min)/ħ), exact for
equal-cost geodesics). **[W]** (Claim SWP, S_2738ddb8c926; pilots:
swp-carrier-parsing, bdp-inside-outside, pit-zipper, apsp-tropical,
act-stationary.) The column splits along the order axis (v3.6): the
ORDER-FREE face — counting, inside, inside×outside, conflation — extends
verbatim over ℂ (claim SWF, S_9a577e722039: the first stance flipped by
its own named breaker rather than by assumption; the extension is
reading-robust, touching only the ring structure of ℂ), while the
ORDERED face (Viterbi) is undefinable without an order — the idempotent
member of the Maslov family needs the (max,+) order that ℂ lacks.

**(i) Third codec sighting.** GALAXY's W ↔ ASPF's F is exp_α ⊣ log_α
verbatim — exact on the rank-sum quotient, and the quotient genuinely
collides (rank-sets {1,4} and {2,3}: equal α-shadow, distinct prime
carrier): GALAXY is a one-mode decode of the ASPF carrier, the corpus's
own probability : carrier instance. Sightings now three: Nedge L ↔ G;
the atlas 𝔸 ↔ 𝕄; GALAXY ↔ ASPF. **[W]** (Claim GCX, S_2738ddb8c926;
separated from CDC by 27,648 truth-separators — a sighting, not a
restatement.)

### 5.9 The doubling interface and the radial chart (corpus imports, H-series)

**The interface (correcting a name).** The recursion of §5.7 and the tree of
§13.2 are instances of one type: a **binary tree with a conjugation
operator** — (A, σ) ↦ (A², σ′), with the level conjugation's eigenspaces
giving the modes (d, c) and the composition rule twisted by a per-level
cochain. Cayley–Dickson is only the most famous pinning, not the type:
**cocycle = 0** pins the untwisted tree — the Walsh/Hadamard/RM layer (the
characters of (ℤ/2)ⁿ are the Walsh functions); **cocycle = the CD
sign-twist** pins ℝ→ℂ→ℍ→𝕆 with its per-level property sacrifices. The
twist class at a level is that level's **phase** — at n = 2 the cocycle
classes are exactly the central extensions of V₄ (Theorem 5.4's D₄, and
Q₈ as the other Arf class). **[S]**

**Theorem (char-2 collapse). [W]** Over GF(2) the twist dies: conjugation
trivializes (−b = b) and CD multiplication at dims 2, 4, 8, 16 is
bit-identical to XOR-indexed convolution, the group algebra GF(2)[(ℤ/2)ⁿ]
— commutative and associative even at octonion/sedenion levels (verified,
200 random triples per dim). The sign-twisted and untwisted towers are
**one tree differing only in a cocycle that characteristic 2 cannot see**;
the corpus's CD-over-GF(2) addressing scheme (XOR norms, conjugate-bit
flips) is this collapse used as engineering. (Filed as a *rhyme* with the
phase support theorem — coefficient characteristic vs section degeneracy
are different invisibility mechanisms — not an identity. **[C]**)

**The radial entailment (a caution that is also a purchase).** The CD
pinning implies **accessibility of a radial coordinate space**: the
conjugation yields a quadratic norm N(x) = x x̄ (a sum of squares), hence
a radius and a **polar chart** (magnitude × direction) at every level —
structure the untwisted pinning provably lacks (its "norm" degenerates to
the XOR-sum). Two disciplines attach: (i) the radius is **quadratic
magnitude, not the crossbar's linear mass** — do not conflate ‖·‖₂ with
m = E⁺+E⁻; (ii) the radius's compatibility with the product is
rung-limited: N(xy) = N(x)N(y) holds exactly through 𝕆 (Hurwitz;
composition algebras at dims 1, 2, 4, 8) and fails at sedenions (zero
divisors) — radial multiplicativity is itself a rung of the sacrifice
ladder. **[S]** The payoff: there are **two magnitude-pinnings**, and they
are the two normalizations — pinning the linear mass c gives the simplex
(probability, §5.8a); pinning the quadratic radius gives the sphere
(amplitude normalization, the natural home of §8's amplitude reading).
The prohibition's arity argument applies to both: each is a one-mode
decode of a two-mode encoding, differing only in which magnitude it pins.
**[C]**

**The bundle reading (n = 1 geometry).** The pair is the **double cover**
of the single channel; the pin-swap is the **deck transformation**; the
twist is **ℤ/2 monodromy** — the Möbius picture from the corpus
(one base traversal swaps the fiber; the cover's cylinder has the swap as
its sheet-exchange). The band's lack of a global sheet-distinguishing
section is the bundle-level face of the frame-invisibility obstruction
(Theorem 5.4). **[C]**

**The breakdown locus is geography (Z-series corpus import).** The radial
caution above has a corpus-quantified continuation: when radial
multiplicativity fails (sedenions and beyond), the failure locus is not
scattered pathology but **enumerated, oriented structure** — the corpus's
conservation-law program ("zero divisors aren't a problem, they're
orienting features" once their number and placement are predictable).
Externally anchored there: Moreno's characterization — a sedenion pair
(v₁, v₂) is a zero divisor **iff ‖v₁‖ = ‖v₂‖ and ⟨v₁, v₂⟩ = 0**; the
normalized zero-divisor pairs form G₂ = Aut(𝕆); dim ZD(Aₙ) = 2ⁿ − 5
(Moreno; Biss–Dugger–Isaksen), filling the ambient space as n → ∞ while
the law-release schedule exhausts at n = 4 ("the information suppressed by
each trivial law is exactly the information that becomes expressible when
it is released" — a law being *trivial* when it holds without witness
structure, the charter's own vocabulary). **[S]** Two atlas readings:
(i) **the conservation principle is the algebraic dual of the §11.10
recursion** — residue-at-level-n becomes structure-at-level-(n+1) on the
signal side (common mode → next channel) and on the algebra side
(released law → zero-divisor geography); what the radial codec cannot
multiplicatively transport is re-encoded as the next level's terrain.
**[S]** (ii) Moreno's condition read in atlas coordinates: equal norm =
**balance on the radial channel**; orthogonality = maximal directional
opposition — the zero-divisor locus is the radial chart's *conflict
corner*, and annihilation (v(ab) = ∞, the product at the bottom rail) is
what conflict does at the multiplicative level. **[C]** (candidate
reading, not identity). Register consequence: the high-rung tropical
limit (OB-1) requires a **zero-divisor-indexed valuation** — the corpus
program's "index the valuation relative to the ZD locus and let the locus
do the geometric work" names exactly the blocker its open-problems ledger
records for standard tropicalization. **[S]**

**The lock schedule (S25; instrument v3.6a, S_9a577e722039).** One
certificate rides the whole tower: det L_x, the determinant of the
left-multiplication operator. Through the octonions it is **locked to
the radial chart** — det L_x = N(x)^(d/2) exactly (sampled ratio
1.000000 at d = 2, 4, 8): one invariant, two charts, a codec; because
det is a function of the norm alone, the kernel is empty and there are
no left zero divisors. At the sedenions the lock breaks (ratio spread
≈ [0.03, 0.76]) — **not a failure of the certificate but the purchase
of an axis**: det becomes an independent coordinate, and the pair
(N, det) carries strictly more than either. The two witness modes of
the rung-16 boundary are the two readings of the unlocked pair:
norm-failure (the N-reading) and kernel (the det-reading), the kernel
mode strictly contained in the norm-failure mode (claims RDW/ZDW,
Π-formalized: fiber-contentful at every rung, the witness being the
section over rungs — a 1-path, displayed in verdict geometry as
cdlevel-inertness). The annihilator of a zero divisor is **compiled,
not searched**: it is ker L_x (a 4-plane for the exhibit
(e₁+e₁₀)(e₄−e₁₅) = 0), the alignment system's coefficients being
octonion multiplication data — the last locked rung parameterizes the
first unlocked one, EEA's final-vector-just-prior structurally. The
determinant variety {det L_x = 0} is measure-zero: sampling never
lands on it; riding the certificate is the only access. Verdict-level
consequence, recorded against the spec's own instrument: the five
claims {GCX, RAD, RDW, ZDG, ZDW} share ONE verdict map in
S_9a577e722039 and differ only at the witness stratum — five
statements, five witness structures, one P/F/V profile: the verdict
lattice undercounts content, and witness-valued verdicts (the
2nd-order breaker/joiner program) are the registered remedy. **[W]**
(Pilots: det-lock, radzdg-witness, hyperplane-ride, second-order-zd.)
## 6. The semiring: two operations, log-linked

**Definition 6.1 (the two operations).** The carrier of the connectives is
a semiring with two operations related through the log:

- **AND ~ sum-of-logs** (log-product): the multiplicative-dominant
  operation; the (+, ×) face.
- **OR ~ log-sum-exp** (soft max): the additive-dominant operation; the
  (max, +) tropical limit.

NOT negates the log carrier (u ↦ −u) = inverts (y ↦ 1/y) = swaps pins.
Under NOT, log-sum-exp and log-product exchange — which *is* De Morgan:
negating the log axis turns the product (sum of logs) into the dual
co-product (inverse-weighted sum). **[W]**

**Remark 6.2 (why two operations are forced).** By Theorem 5.3(2): a
single operation under inversion is self-dual and collapses the
∧/∨ distinction. The semiring is not a flourish; it is the minimum
structure under which NOT has something to exchange. **[W]**

**Remark 6.3 (which semiring is open).** The *shape* — log-sum-exp /
(+, ×) duality — is forced by "additive accumulation + inverse-locked
locus + involutive NOT." The *specific* semiring instance (which precise
⊕, and the numeric window it acts on) is part of the range contract, §7.
**[W]**

**Remark 6.4 (the physical instance).** The two operations have a
realized physical instance in resistor networks: series combination adds
resistances; parallel combination adds conductances (1/R = 1/R₁ + 1/R₂).
See §11.1 — the conductor square is this section's semiring duality as
hardware, with De Morgan as the law-preserving diagonal. **[W]**

---

## 7. The range parameter ℛ — the document's named loop

This section fills the specification's single H₁ generator *as a
parameter contract*, and deliberately does not fill it as a value.

**Definition 7.1 (the parameter).** **ℛ** is the numeric range / saturation
behavior of each pin's carrier: unbounded log-carrier, or
bounded/saturating window, or a specific numeric window. ℛ is a **free
parameter of this specification.** An instance of the EL-Atlas is the
structure of §§1–6 together with a choice of ℛ.

**Contract 7.2 (constraints on ℛ, from both routes).** The two routes that
reach ℛ in the notion graph impose:

- **Route via the involution structure (§5):** *no constraint.* The
  log-odds-shaped carrier is forced, but nothing in the V₄ / inverse-lock
  structure fixes boundedness or a window. **[W]**
- **Route via the semiring (§6) and dynamics:** *saturation desiderata.*
  A bounded/saturating range is what makes a repeater stable
  (fade-resistance); choosing ℛ is simultaneously choosing the saturation
  regime of accumulation. **[W]** (flagged repeatedly in the source
  record as a design consideration, never derived.)

**Named instance candidates (corpus).** The corpus consolidation (App. A,
D-1 §C3) records concrete admissible instances of ℛ without privileging
one: the raw zero-based carrier **[0, ∞]²** (0 = no evidence) as default;
**[1, ∞]²** for purely positive multiplicative coordinates before logs;
and the **shifted embedding e ↦ 1 + e/κ** with l-space as an extended or
shifted log. Both raw and exponentiated carriers are allowed; the choice
is an instance declaration per Contract 7.2, not a resolution of it.
**[W]** (corpus-witnessed.)

**Coherence 7.3.** The two routes are consistent: ∅ (route one) is
compatible with any desiderata set (route two). The loop is thereby
*coherent as a contract* — both routes agree that ℛ is free and that
fade-resistance is the live design pressure — while remaining *open as a
value*. This is the intended permanent state: the framework is
paraconsistent precisely so that an open obligation can be carried without
infecting the rest of the structure. **[S]**

**Observation 7.4 (range as domain structure).** Choosing ℛ is choosing a
Scott-domain structure on the pin carrier: a saturating range gives
accumulation chains least upper bounds; an unbounded range does not. This
reframes the open parameter as a continuity/limit decision rather than a
mere interval pick. **[C]** — candidate observation from the
correspondence probe (§10), not derived in the source record.

**Witness 7.5 (saturation dynamics on the one-parameter chart;
re-scoped).** A range spec was worked on the multiplicative chart 𝕄 with
neutral 1 and rails 0 / +∞: NOT swaps the rails (1/0 = ∞, the
inverse-locked certainties); the rails are **absorbing** while the
neutral is **unstable** — consistent accumulation drives to a rail and
the rail pins the decision. Fade-resistance = drive to saturation; the
bounded-at-rails range is exactly what makes a decision hold (the
repeater mechanism). **[W]** for the dynamics — with a mandatory scope
restriction: in the source record this was first read on the odds axis
x = E⁺/E⁻ and then superseded by the no-collapse correction (Provenance
P-1); a single such axis sees bias only and collapses B and N to the same
point. The witnessed dynamics therefore attach to the **one-parameter
chart / the external decision projection**, not to the carrier pair. They
constrain ℛ's saturation regime without fixing the per-pin accumulator
range; the specific potential, measure, and critical drive remain the
user's design (OB-1). **[S]** for the re-scoping.

---

## 8. The amplitude reading: norm, phase, curvature, holonomy

The geometric/sheaf-theoretic reading of the carrier, for use as a
coefficient system on graphs and complexes.

**Definition 8.1 (the coefficient object).** The carrier is read as a
**two-component, non-normalized, amplitude-valued coefficient**: the
components are E⁺ and E⁻ (equivalently t, f), kept separate, never
divided into a disposition. The coefficient is *not* a probability — there
is no normalization, ever (Law 3.1). **[W]**

**Definition 8.2 (the dictionary).** On the crossbar of §4:

- **Modal grading / filtration** = total norm **m = t + f**. Not a
  probability: one never divides by it.
- **Connection / phase** = the relative balance of the two unreconciled
  components, carried on the bias axis **b = t − f** — *relative phase
  between two amplitudes that remain uncollapsed*, not a log-odds
  (Law 4.2).
- **Curvature** = contradiction degree, peaking where *both* components
  are large — the interference-dominated region. A collapsed (odds)
  representation must report that region as flat (ratio ≈ 1); the
  amplitude reading reports it as maximally curved. This is the whole
  difference between a geometry that can carry holonomy and one that
  cannot.

**[W]**

**Conjecture 8.3 (holonomy = enclosed contradiction).** On a complex
carrying this coefficient system — connection the net-truth phase,
curvature the contradiction degree, filtration m — the holonomy
accumulated around a loop equals the contradiction it encloses.
**[C]** Proposed test (from the source record, never run): build the
enriched complex with coefficients in the two-term log-semiring and check
"holonomy = enclosed contradiction" under the same d∘d = 0 gate and
vacuity discipline as the existing harness. Obligation OB-3.

**Remark 8.4 (the discipline, stated once).** The same forbidden move
recurs at every level: don't collapse the fiber, don't normalize the
amplitude, don't take the odds. Keep the components live until something
*forces* collapse — and the obstruction to ever being forced is the
holonomy. **[W]**

---

### 8.5 The phase socket — what OB-2/OB-3/OB-9 jointly are (V₄-valued)

OB-2 (phase composition), OB-3 (holonomy = contradiction), and OB-9 (phase
origin) are **one hole, three gradings**, not three obligations. The hole is
characterized here by its boundary conditions (what the rest of the spec forces
about anything filling it), and its value group is then forced. This is the
*characterization*, not the fill; the fill is parked (user-direction pending).

**The socket (six boundary conditions, each from a committed part):**

- **C1 — lives on edges, not nodes.** The carrier at rest is 2-dimensional
  (mass, bias) and §8 fixes the coefficient as the unnormalized *pair*; phase is
  therefore not a third axis on a value at rest but a structure on *comparisons
  between* values — a connection.
- **C2 — typed as a connection.** §8's dictionary already types it: relative
  phase = connection (1-cochain), curvature = contradiction (2-cochain),
  holonomy = enclosed contradiction. The d∘d=0 object of OB-3.
- **C3 — partly occupied.** The OB-3 run witnessed **bias-holonomy** (net bias
  around an unfilled loop, H¹=1). Anything filling the socket must restrict to
  bias-holonomy as its abelian/real shadow on the bias axis.
- **C4 — non-flat (corrected).** The Noether charges (squeeze/dilation) live in
  (ℝ,+)², which is flat; the socket needs *nonzero curvature* for nonzero
  holonomy. (An earlier draft wrote "non-abelian"; that was an error — flat means
  zero *curvature*, not abelian *group*. An abelian group carries nonzero
  holonomy: the Z₂ orientation/Möbius sign is the prototype. The real requirement
  is two **independent involutions**, see the value group.)
- **C5 — not a complexified value.** Caveat 2.4a forbids the field route: phase is
  not arg() of a complexified semiring. It comes from composition structure, not
  from enriching a value at rest.
- **C6 — sourced from overlay non-commutativity.** The overlay (§13.2) is
  composition; transport around a loop composes overlays; **phase is the failure
  of overlays to commute around the loop.** This meets C1 (edges), C2
  (connection), C5 (composition not field), and supplies the curvature C4 needs.

**The value group is forced to be V₄.** The connection must independently record,
around a loop, **two** order-2 bits: (i) the bias-sign flip (the witnessed
bias-holonomy, one Z₂) and (ii) which of the two **distinct** involutions —
negate-a-pin vs pin-swap, kept distinct by Theorem 5.3 — was transported (a
second, independent Z₂). Two required independent order-2 generators is exactly
**Z₂ × Z₂ = V₄**. Smaller groups each fail a named condition: the trivial group
kills holonomy (C2/C3); Z₂ has one bit and conflates De Morgan with bias-flip
(kills Theorem 5.3); Z₃ has no order-2 element and cannot hold even one involution.
V₄ is therefore **forced, not merely minimal** — and it is V₄ (all non-identity
elements order 2), not Z₄. The d∘d=0 gate closes identically with V₄ = (Z₂)²
coefficients, since the cochain complex is then over GF(2) — the *same* ground
field as the Reed–Muller / Walsh structure of §13.1 (the coding substrate and the
phase structure share GF(2); likely not a coincidence). **[W]** for the socket
characterization and the forcing of V₄; **[C]** for any specific fill.

### 8.6 Phase as a dependent type — the V4 interface and its pinnings

The apparent remaining hole ("which loops realize a nonzero class, by evidence")
is an artifact of one framing. It dissolves the same way "unreachable" did: refuse
the either/or, find the common structure. Here the either/or is **carrier vs
action** — does the system *carry* a V4 action (evidence picks each edge's
transport; holonomy is a measurement you survey) or *is* it a V4-torsor (topology
fixes the transport; holonomy = H1(complex; V4), a theorem)? The resolution is
neither: the system is a **dependent type with a fixed V4 interface**, and carrier
and action are two **pinnings** of that interface to a model.

**The interface (fixed; the invariant).**
```
V4Interface:
  transport  : Edge -> V4        -- every edge carries a group element
  holonomy   : Loop -> V4        -- = sum of edge transports
  biasShadow : V4 -> Z2          -- projects to the witnessed bias-holonomy (C3)
Phase : (pin : V4Interface |- Model) -> Type
```
The V4 structure (§5, §8.5) is invariant; what varies per model is the **witness**
supplying `transport` — the pinning.

**The two pinnings (both retained, neither lost).**

- **Carrier pinning (A):** `transport(e) := classify(evidence_at(e))`. Evidence
  picks the V4 element per edge; holonomy *responds to data* — you can ask what the
  evidence does around a loop. Holonomy is a **measurement**.
- **Action pinning (B):** `transport(e) :=` the structural V4 element (torsor);
  topology fixes the elements; holonomy = H1(complex; V4), **determined**, no
  survey. Holonomy is a **theorem**.

**The rich carrier holds both at once.** Because both pinnings implement the *same*
interface, both witnesses can sit on one complex; their **V4-difference is itself a
1-cochain** — the *evidence-relative-to-structure* field. So the carrier holds
three things simultaneously: structural holonomy (what topology forces, B),
evidential holonomy (what the data shows, A), and their difference (where data
departs from structure). The pinning chooses which is read as *primary*; the type
holds all three. Nothing is lost in either direction. **[W]** (worked on a triangle:
B-holonomy and A-holonomy distinct, difference = the data's departure, all three
V4-valued and simultaneously present.)

**C3 holds in both pinnings** because `biasShadow` is in the *interface*, not a
witness — the bias-holonomy is recoverable however you pin.

**Status change.** Phase is therefore **resolved as a type**, not parked: it is a
group-action-carrier with a fixed V4 interface and a pinning-dependent realization.
The pinning is a declared *model parameter* (upstream, like R in OB-1), not a hole
in the logic. The typethy layer is correspondingly re-typed from "open domain-hole"
to **a dependent type, pinning-parametric** — derived once a model supplies its
pinning, exactly as the DAG made the coverage cells derived-by-construction.
OB-2/OB-3/OB-9 consolidate and move from *open* to *resolved-as-type* (the remaining
freedom is the pinning, a modeling choice, not an open obligation of the logic).
**[W]** for the type and the two-pinning structure; the *choice* of pinning per
application is model data, not a spec obligation.

**Addendum (draft 13) — the pinnings are the two representations, and phase
is the extension class.** Theorem 5.4 supplies the consistency check §8.6
predicted. The **action pinning (B)** is the corner/tetrahedron
representation: V₄ exact (the normal double-transpositions), frame
S₃ = Aut(V₄) permuting the three involutions, total symmetry of the
pinning space **S₄ = V₄ ⋊ S₃ = Hol(V₄)** — re-pinnings compose as S₃,
resolving the holomorph candidate (witnessed: image full S₃, kernel V₄).
The **carrier pinning (A)** is the pin-plane representation: only the
antipode-centralizer **D₄** is linearly realizable, i.e. V₄ braided by the
central twist [N,S] = −id; the phase bit of §8.5 is realized internally as
**the extension class of 1 → Z₂ → D₄ → V₄ → 1** — the two De Morgan
generators already fail to commute by exactly one reversible central sign
(Pauli X/Z anticommutation), so phase was never an external add-on: it is
what the carrier pinning *sees* of the structure the action pinning holds
exactly. The §8.6 difference-cochain between the pinnings is this class.
The axis-mixing S₃ frame is linearly invisible to the pin chart
(Theorem 5.4), which is why perspective shifts felt external to the
carrier: they are not in any single chart; they live on the corners. **[W]**

## 9. Counterexamples and boundaries

Structures the EL-Atlas is *not*, and moves it forbids. Each is a real
failure, not a rhetorical bound.

**CX-1 (odds / probability).** Any reading of the carrier as odds or
normalized probability fails by Lemma 3.2: it identifies active
disagreement with ignorance. This includes "innocent" readings of b as
log-odds (Law 4.2). The collapse is admissible only as an explicit,
external decision step — never inside the logic.

**CX-2 (Belnap–Dunn as four labels).** The adjacent construction most
likely to be confused with this one. Belnap's FOUR posits four points;
here the four values are corners of a geometry whose primary structure is
the crossbar (Proposition 4.3). The label lattice cannot express *degrees*
of mass or bias, and erases low-mass-balance vs high-mass-balance except
as the single B/N distinction.

**CX-3 (one chart alone).** Working only in 𝔸 or only in 𝕄 loses the
content of the atlas: that the *same* accumulation is additive in one
presentation and multiplicative in the other, with negation conjugate
across (Lemma 2.4). Laws proven chart-essentially are not laws of this
logic.

**CX-4 (one operation alone).** A single connective operation under
inversion is self-dual (Theorem 5.3(2)): AND = OR, De Morgan vacuous. The
two-operation semiring is a hard requirement.

**CX-5 (locked pins everywhere).** Treating the inverse-lock (u, −u) as
holding on the whole carrier re-collapses the plane to the line and
silently restores a one-parameter (hence collapse-equivalent) logic. The
lock holds only on the embedded locus (Lemma 2.6); the general pins are
independent (Law 1.3).

---

## 10. Correspondences (related structures, classified)

Per the probe discipline: **nothing here is claimed Present** — no
internal witness in the source derivation *names* a canon correspondence.
All entries are Implicit (witness-functor sketched) or Candidate (sharp
test available). These are the spec's test surface.

**Implicit:**

- **Dialectica (de Paiva).** F maps (E⁺, E⁻) to Dialectica-style objects
  of (proofs, challenges); the for/against pair has exactly the
  two-sided object shape. Test: does pin-swap match Dialectica
  dualization on composites? This cleaves "evidence algebra" from
  "decision algebra."
- **Chu.** F maps the carrier to a Chu object with NOT as the Chu duality
  involution; pin-swap = dualization. Test: NOT∘NOT = id and De Morgan
  via Chu duality, checked mechanically.
- **Martin-Löf (transport).** F: charts ↦ types, exp/log ↦ equivalence;
  "same object, two charts" ↦ transport along the equivalence
  (Remark 2.5). Test: prove a law in 𝔸, transport, verify the 𝕄 form —
  Lemma 2.4 is the first instance.
- **Girard (polarities).** F: pins ↦ polarized formulas; the no-collapse
  law as refusal of contraction on the pair. Test: which structural rules
  survive on each pin separately vs on the pair.
- **Kleisli (writer).** F: each pin ↦ a writer monad over its additive
  monoid; accumulation = bind. Test: associativity/unit of accumulation
  as monad laws, per pin, guarding against cross-pin leakage (Law 1.3).

**Candidate:**

- **Scott (domains).** Choosing ℛ = choosing the domain structure on the
  pin carrier (Observation 7.4). Highest-yield candidate: it cleaves
  exactly along the document's open loop.

---

## 11. Circuit and network witnesses

The logic has a realized electrical instance. The honest grade (draft 7,
tightened against external review) is **functorial-shape correspondence**,
not literal identity: there is a structure-preserving map between the
logic's connective algebra and the network's combination algebra that
preserves the V₄ and its De Morgan diagonal, witnessed at the level of
*form* (the values are the chart, the form is the invariant). Where this
section formerly said "the same algebraic object," read "the same algebra
*up to the explicit functor named in each item*" — following the
Baez–Fong decorated-cospan template (App. B, S-G), which is how a
network↔semantics correspondence is stated rigorously. Claims of literal
identity beyond the witnessed functor are downgraded to **[C]**. Each
item below is a witness for a section above.

### 11.1 The conductor square (witness for §5–§6)

Series combination adds resistances (R = R₁ + R₂); parallel combination
adds conductances (1/R = 1/R₁ + 1/R₂). Series/parallel are dual under
R ↔ G = 1/R — the same swap as AND ↔ OR under ¬. The square
{series, parallel} × {R, G} is a V₄: series/parallel is the AND/OR axis,
R/G is the negation axis, and their product — the diagonal — is
**De Morgan as the unique law-preserving move** of the square. **[W]**

Precision the algebra forced: De Morgan maps the law-*form*
(X₁ + X₂ ↦ Y₁ + Y₂, same shape, dual quantities), not the value —
series-R-read-as-conductance is not numerically equal to parallel-G; they
are different circuits. De Morgan is a duality of forms, and the square is
its Cayley graph. **[W]**

With this, De Morgan is witnessed from **three independent directions**
landing on the same V₄ diagonal: gate composition ({IDENT, AND, NOT,
XOR}), the differential rail-swap (the pin-swap of §5), and the
conductor-square diagonal. **[W]**

### 11.2 The flat-binding theorem (witness for §5; closes a fork)

Binding De Morgan's V₄ to any other V₄ is choosing one of the 6
isomorphisms (Aut(V₄) = S₃). Of these, **2 preserve the De Morgan
diagonal (flat; they form the C₂ stabilizer of the diagonal) and 4 move
it (twisted)**. Flat-vs-twisted is therefore a property of the *binding*,
not of any circuit or network — decidable, intrinsic, no external data.
Every V₄ in the construction — the gate, the Belnap/crossbar (§4), the
shape-frame, the conductor square (11.1), the constraint plane — was
built with De Morgan as its diagonal, so all these bindings are **flat by
construction**. A twist could only enter by binding to a V₄ that places
De Morgan off-diagonal, or by binding to a non-V₄ and manufacturing the
structure (which smuggles in the placing choice). **[W]**

### 11.3 The Wheatstone bridge: the crossbar as instrument (witness for §4)

The bridge's two sense corners are E⁺ and E⁻. The **galvanometer reads
their difference — bias b**; the **supply reads their sum — mass m**.
The Wheatstone bridge is the physical instrument of the (mass, bias)
basis of §4. **Balance is the null of the difference — the pin-swap
fixpoint**: a balanced bridge is one where swapping the two sense arms
changes nothing, i.e. the De Morgan involution at its fixed point. The
galvanometer reads this null in the *multiplicative chart* (a ratio
E₊/E₋=1), the pin-swap fixes it in the *additive chart* (a difference
b=0), and the two are the same locus across the exp ⊣ log adjunction
(Lemma 2.5b) — the **chart-image** ratio, not the forbidden **collapse**
ratio (Remark 2.5c). The
B/N axis (zero bias) is the balanced condition: one can be balanced at
high supply (B, conflict) or low supply (N, absence) — the mass axis,
orthogonal to what the galvanometer reads. Drive and sense occupy
orthogonal diagonals; the galvanometer reading is the deviation from that
orthogonality. **[W]** (the structural correspondence; see OB-5 for the
strong form.) The corpus consolidation adds the categorical grade of this
object: the bridge is a **higher-order lift — a pair-of-pairs** that
compares two local readings of the carrier (differential/common vs
normalized divider/resource); not merely another gate but a
**comparison-of-comparisons**. **[W]** (corpus-witnessed, App. A D-1.)

### 11.4 The two-readout instrument (witness for Lemma 3.2)

A galvanometer alone is ratio-blind in exactly the sense of Lemma 3.2: at
null it cannot tell B from N. A **differential pair under the bridge**
fixes this: the galvanometer reads bias; the **common-mode output reads
mass**. High common-mode at null = conflict (both arms strongly driven,
opposed); low common-mode = ignorance (both quiet). A two-readout
instrument recovers **both** carrier coordinates that the odds-line
collapse destroys — the full carrier, measured. Lemma 3.2's
impossibility, and its repair, both have hardware. **[W]**

**External grounding (recovered from corpus T1129/T1130, web-verified
there).** The corner-representation half of Theorem 5.4 and this section's
W-axis have published anchors: S₄ = V₄ ⋊ S₃ is standard (the normal
Klein four of double transpositions; quotient S₃); the **tetrahedron
algebra** g_⊠ ≅ sl₂ ⊗ A (arXiv math/0604218, Elduque / Hartwig–Terwilliger)
realizes the S₄ action as exactly *Klein-four automorphisms plus an S₃
action* — published Lie theory for the holomorph structure; and the
dimension-4 **Hodge star** gives Λ¹ ↔ Λ³ (the witness↔triangle duality)
with Λ² (dim 6) splitting 3 + 3 self-dual/anti-self-dual — the W-axis's
form-theoretic home. **[S]** Inherited residue: the binding of the tetrad
(source, sink, witness, apex) to the tetrahedron algebra's four sl₂-points
is cited in the corpus but not yet constructed.

### 11.5 Conflict as stored potential (dynamics for §1's regions)

In a static label system, B is just a label. In the circuit realization,
**conflict is the metastable loaded state**. Minimal witnessed model:
d(bias)/dt = drive·bias − bias³. Above critical drive, bias = 0 is an
**unstable** fixed point — high potential, poised, flipping to a rail
(±) under any perturbation: conflict = stored potential energy waiting to
resolve an either/or, with the flip as its release. Below critical drive,
bias = 0 is **stable** — ignorance, nothing poised. T/F are energy
flowing/dissipating to a rail. **[W]** (minimal model run in the source
record.) With reactive components (C, L), energy is stored rather than
dissipated and the system has a **lattice of fixed points; take the
least** (Knaster–Tarski) — the carrier's dynamics bottom out at the same
fixed-point theorem as the framework's operating principle. **[W]**
The exact reactive network, potential, and critical drive are design
parameters (folds into OB-1's contract). **[W]** as flagged-open.

### 11.6 The square reduces; the triangle doesn't (scope theorem)

Tracing actual resistance *values* (not law-forms) across network
embeddings exposed the boundary of the entire V₄ picture:

- Series/parallel-reducible networks are the V₄ square's territory — the
  **reducible half** of network space.
- The Wheatstone **crossbar R₅** behaves as the sign-object: **at
  balance it vanishes** from the terminal resistance entirely
  (R_terminal = (R₁+R₃)‖(R₂+R₄), R₅ absent — its marginal contribution
  is exactly 0); **off balance it obstructs** — the network becomes
  irreducible by series/parallel and requires the **Y-Δ (star-mesh)
  transform**, which has no series/parallel analog. The irreducible
  3-cycle (the triangle) is structure the square's vocabulary cannot
  represent. **[W]** (sympy-witnessed in the source record.)

The lesson, recorded as method: when a structure comes out *too* clean,
suspect it is the reducible fragment, and go looking for the irreducible
cycle it cannot see (Provenance P-4). The unsigned content of this logic
is a square; the signed content is a triangle. In circuit form:
**affine = bridge balanced = crossbar vanishes = reducible; non-affine =
unbalanced = genuine Y-Δ triangle.** **[W]** for the circuit statement;
the identification with the sign-cocycle computation is OB-5.

### 11.7 Prior electrical formalisms (lineage, classified)

Two earlier constructions in the source record realize this logic's
shape in circuit terms and are recorded as lineage, not as witnesses:

- **CHL-E.** NOT as reciprocal inversion (R = 1/G) — the §2 multiplicative
  negation as a component law; **contradiction as a high-resistance
  state** rather than an explosive one (paraconsistency from circuit
  topology); a **two-rail architecture** (the pins as rails) with
  **harmonic-mean AND and additive OR** — which is exactly the
  parallel/series pair of 11.1. Whether the architecture satisfies the
  paraconsistent axioms (Priest/Belnap literature) was flagged and never
  checked: OB-6. **[W]** as a recorded proposal; unverified as a logic.
- **G-Calculus.** A proposition's state as a six-signal vector:
  (q, r) evidence for/against — the carrier pair; (x₁, x₂)
  capacitive/inductive bias — the reactive predisposition of 11.5;
  (q̇, ṙ) momentum of belief/disbelief — dissonance as velocity. Three
  simultaneous equilibrium laws (op-amp, Wheatstone phase rotator,
  differential tension buffer); the fixed point is the settled state,
  qualified by remaining dissonance. The EL-Atlas carrier is the
  (q, r) plane of this system; the G-Calculus is a candidate *dynamics*
  over the EL-Atlas *statics*. **[W]** as a recorded system; the
  identification of its laws with §§4–6 is **[S]**.

### 11.8 Conservation and equivalence: Kirchhoff, Noether, Thévenin

**Kirchhoff.** The two laws are the dual spine of energy redistribution
over a closed network: KCL — current conservation at nodes; KVL —
voltage sum zero around loops. **[W]** (source record). The corpus
axiomatizes them as named formal axioms (OhmsLawName,
KirchhoffCurrentName, KirchhoffVoltageName in a Level4_Physics module,
App. A D-8), and grounds series composition in global charge
conservation with voltage division as a KVL consequence (D-12). The
atlas identifications, graded:

- **KCL ↔ per-pin bookkeeping.** Conservation at a node is the
  accumulation law of Definition 1.1 read as flow: increments in,
  total maintained, nothing leaks between pins (Law 1.3). **[S]**
- **KVL homogeneous ↔ the d∘d = 0 gate.** "Sum around a loop is zero"
  is exactly the closure condition Conjecture 8.3's harness gates on.
  **[S]**
- **KVL inhomogeneous (Faraday form) ↔ Conjecture 8.3.** A loop sum
  that is *not* zero equals the enclosed source — which is precisely
  "holonomy = enclosed contradiction" in circuit form. The conjecture
  is KVL-with-curl. **[S]** — this gives OB-3 a second, physical
  statement of its test.
- In the purely resistive (dissipative) regime, settlement is the
  unique Thomson minimum; reactive components replace it with the
  least-fixed-point lattice of 11.5. **[W]**

**Noether.** The corpus contains the schema applied to this material's
algebraic spine: D-10 derives a "Law of Conservation of Ontological
Content" from the symmetries of categorical duality, explicitly on the
symmetry → conservation analogy, traced along the Cayley–Dickson
property-degradation ladder (ordering, commutativity, associativity lost
stepwise; content conserved). **[W]** (corpus-witnessed). The
atlas-internal Noether-shaped fact is immediate and checkable:

> **Under the De Morgan involution (pin-swap), mass is conserved and
> bias is negated:** (E⁺, E⁻) ↦ (E⁻, E⁺) gives m ↦ m, b ↦ −b.
> The symmetry of §5 pairs with the invariant of §4 — and the
> galvanometer (11.3) reads exactly the coordinate the symmetry does
> *not* conserve, while the supply reads the one it does. **[S]**
> (one-line computation; stated here, not yet developed.)

Noether proper requires a *continuous* symmetry. The atlas has a
candidate: the exp/log transition makes translation in 𝔸 the same
one-parameter flow as scaling in 𝕄 — a continuous chart symmetry whose
conserved quantity is unidentified. Promoting the discrete pairing above
and the corpus's categorical analogy to an actual Noether statement for
the carrier is **OB-7**.

**Thévenin.** Stated under the charter: **no corpus document names
Thévenin or Norton.** The *move*, however, appears twice, unnamed:
D-1's fourth scalar shadow — "equivalent single-conductor collapse" —
is the Thévenin operation (replace a whole network, seen from a port,
by one equivalent element); and the Sys framework's **Star-Mesh
Transform** (D-13) generalizes it as a reversible level-move,
instantiating conservation across abstraction levels — the n-ary
extension of §11.6's Y-Δ. The atlas reading: **Thévenin equivalence is
a named external projection in the sense of Remark 3.5** — the port
abstraction of an evidence network. It is legal as an instrument
(summarize a subnetwork's contribution at a boundary) and forbidden as
semantics (the equivalent element erases the internal mass/bias
distribution, exactly the ratio-blindness of Lemma 3.2 applied to a
whole subnetwork). Norton/Thévenin source duality
(voltage-source-in-series ↔ current-source-in-parallel) is itself a
De Morgan-shaped swap, unverified here. **[C]** — OB-8.

### 11.9 The simulation stack: verification, tooling, application

The corpus organizes the "what is it for" layer in three tiers, each
with documents in hand (App. A, D-11, D-14–D-16):

- **Verification.** An empirical G-Calculus study implements the
  5D_State vector with G_AND/G_OR composition and an RK4 solver,
  demonstrating existence and uniqueness of equilibrium via the
  contraction property (trajectories from disparate initial conditions
  converge to the same fixed point) and a functorial equivalence to
  Hopfield networks (D-11). This is the empirical counterpart of
  11.5's fixed-point claims: the dynamics over the carrier are not
  only stated but simulated, with convergence witnessed numerically.
  **[W]** as corpus record; binding its 5D_State to this spec's
  carrier+reactive coordinates is unverified.
- **Tooling.** The XSPICE mixed-signal framework analysis (D-14) and
  the LTspice/B2 Spice comparative evaluation (D-15) supply the
  instrument bench. The mixed-signal frame is apt, not incidental: the
  carrier is mixed-signal by construction — continuous accumulation
  (analog pins) punctuated by discrete decisions (external collapses,
  Remark 3.5). A simulated instance of the EL-Atlas is a SPICE-class
  deliverable: pick an ℛ instance (§7), wire the bridge of 11.3–11.4,
  and the two-readout instrument is runnable. **[S]** as a proposed
  application path.
- **Application.** Recorded domains where the carrier-with-dynamics is
  deployed as an interpretation: System Pi — language as a physical
  system under conservation laws, modeled by impedance and circuit
  dynamics (D-16); hyperparameter self-regulation — cognitive-state
  modulation of learning dynamics through a bridge architecture, the
  RLC/optimizer identification (D-17); RCA — computation as
  restoration of equilibrium under conservation laws, "algebraic
  physics of meaning" (D-18); and the Sys framework's conductance
  hierarchy with Star-Mesh as the level-conserving Process (D-13).
  **[W]** as corpus records; each is an interpretation of the atlas,
  none yet a verified model of it.

### 11.10 Communication, interfacing, and signal processing

The carrier has a channel form, and the corpus treats it as one. Five
threads, graded:

**Differential signaling is the carrier's transmission form.** Sent as
a differential pair, the pins put **bias on the differential mode and
mass on the common mode**. Standard communication practice applies
common-mode rejection — read the difference, discard the sum as noise.
Under Remark 3.5 that is a *named projection*, and the atlas inverts
the engineering default: **mass is data** (it is the B/N distinction),
so CMR-as-semantics is exactly the collapse Lemma 3.2 forbids, and the
two-readout instrument of §11.4 is the channel architecture that
refuses it. **[S]** (assembly of witnessed pieces; the engineering
definitions are corpus-cited in D-1 §C2.)

**The phantom hierarchy: nothing is noise all the way up.** D-1's
quad-star reading (Poulton's phantom/ghost/wraith hierarchy) gives a
physical recursion in which **common-mode structure at one level
becomes the signal-bearing differential structure of the next level**.
**[W]** (corpus-witnessed). Read against §11.6's doubling: the
phantom tower is a communication stack — what a level cannot read as
signal is re-encoded as the next level's channel. This is the
no-collapse discipline (Remark 8.4) as a transmission architecture: the
quotient is never taken; the residue is promoted. **[S]**
(Corpus locus: the Evidence–Differential consolidation report tags this
source [E4]; the hierarchy is the named external anchor of this section's
recursion.)

**Pilot result (OB-12, witnessed) — and a frame correction.** The
structure here is, in its own right, a **recursive binary tree with a
conjugation**: the iterated (sum, diff) splitting, i.e. the
Walsh–Hadamard recursion H₂ⁿ = H₂ ⊗ H₂ⁿ⁻¹, with a per-level involution
acting on the modes as (d, c) ↦ (−d, c) — exactly the pin-swap (a swap
of the underlying conductor pair sends d ↦ −d, c ↦ c). This is the
**Hadamard doubling tree**: the orthogonal mode decomposition of a
2ⁿ-conductor bundle (modes orthonormal at ideal balance, witnessed
levels 1–3). It is a complete, well-behaved object on its own and owes
nothing to any algebra.

The history of this object being called "Cayley–Dickson" is a
**frame-collapse worth recording as a caveat**, because it is the
forbidden quotient (Remark 3.5) committed one layer down. "Recursive
binary tree + conjugation" is a two-axis description: a *doubling
functor* (one axis) that may or may not carry a *bilinear product* (the
other axis). CD is the famous landmark sharing the first axis, so a
nearest-name reading collapses both axes onto it and asserts the
product — which this construction never contained. The pilot confirms
the collapse: **no channel multiplication is exhibited**, so the staged
loss of algebraic identities (commutativity, then associativity) that
*characterises* CD cannot occur — there is no product for them to be
lost from. (The numerical degradation that does occur — mode-isolation
leakage under conductor imbalance — is analytic robustness; it shrinks
per level under √-normalisation rather than growing, so it is not the
staged algebraic loss either.)

The accurate framing therefore puts the tree first and CD second, not
the reverse: **this is a Hadamard doubling tree with swap-conjugation;
Cayley–Dickson would be one possible *completion* of it — the one
obtained by bolting on a specific bilinear product — and nothing in the
construction calls for that product.** Whether a natural channel product
exists at all is the open residue (OB-12); if none is natural, the
full-CD framing is retracted and only the doubling-tree statement
stands. **[W]** for the doubling tree + involution; **[C]** for any
claim that requires a product (CD or otherwise).

**Repeater and regeneration.** Witness 7.5's fade-resistance content is,
in channel terms, a **repeater specification**: saturating rails
regenerate the signal, and choosing ℛ is choosing the regeneration
regime of the link. The communication reading adds a requirement the
logic reading didn't surface: a repeater for *this* carrier must
regenerate **both modes** — a bias-only repeater (standard practice)
silently erases the mass channel at every hop. **[S]**

**The spectral layer (Laplace / s-plane).** The corpus already
generalizes the carrier to AC: D-3's formalization extends to the
complex s-plane ℂₛ, and D-17 carries Total Semantic Impedance
**Z = R + jX** — dissipative and reactive components, i.e. §11.5's
resistive settlement and stored-potential coordinates as the real and
imaginary parts of one complex quantity. **[W]** as corpus records. The
candidate that follows: **complexifying the atlas** — on ℂ, log splits
into magnitude + phase, so the §8 dictionary (norm/phase) would become
*literal* rather than borrowed, and filtering/spectral analysis of
evidence streams becomes available. Whether NOT, the locked locus, and
De Morgan survive complexification is unworked: **OB-9.**

**Sparse signaling and the cost of ignorance.** D-20 frames the
"Problem of Vacuum Density": the thermodynamic cost of encoding
non-events can exceed the information content of the signal. In carrier
terms: **N (low mass) is the expensive-to-transmit state** — absence of
evidence still costs channel. The same document family carries an
explicit structural critique of Bayesian-probability foundations —
independent corpus support for Law 3.1's stance, from the
information-physics direction. **[W]** (corpus-witnessed).

**Interfacing as the register's own theory.** D-23 redefines axioms as
**solvable interfaces equipped with theorem-generating structures**
(triangulation, homological auditing, representable local generators)
rather than terminal postulates. This is the discipline §13 already
practices: each obligation is an interface — a stated contract with a
named discharge path — not an assumed truth and not a defect. The
corpus thereby supplies the standardization story for the spec's own
non-closure: **an open obligation is a port, and ports are how systems
compose.** SYSTEM Π's self-hosted upgrade artifact (D-16 family) is the
packaging precedent at the protocol level. **[S]**

---

## 12. The overlay principle

Committed to a document here for the first time. The principle is
user-origin and is the generative move behind §2, §11.2, §11.3, and the
rung-coupling result in the source record; until this draft it existed
only as practice.

**Principle 12.1 (overlay).** **[W]** (user-origin statement, this
draft):

1. Construct a **pair of networks** N₁, N₂ such that both contain a
   **common structure** S — a span of embeddings N₁ ↩ S ↪ N₂.
2. **Characterize the topology of the reasoning space** of each network
   separately.
3. **Overlay** the networks so the shared structure is a common
   **instance** — not two isomorphic copies but one object: the gluing
   N₁ ⊔_S N₂ (the pushout along the span).
4. Then **computations in one network manifest in the other network,
   characterized by the common structure.**

The force of step 3 is the difference between isomorphism and identity:
two copies of S related by an isomorphism transmit nothing by
themselves; *identifying* them creates the channel. The choice of
identification is itself structure (§11.2: six choices for V₄, two
flat, four twisted) — the "forced correspondence," and its structure
modulates the transmission.

**Candidate Law 12.2 (the manifestation law).** **[S]** — synthesis,
stated for verification, not assumed: on the overlay, the transmission
of computation has the shape of **Mayer–Vietoris**. What can manifest
across the gluing is exactly what restricts nontrivially to S; the
connecting homomorphism through S *is* the transmission channel; the
topology of S bounds the transmissible classes — H(S) as the channel
capacity of the correspondence. Contrapositive, which is the testable
edge: **a deformation whose restriction to S vanishes is invisible to
the other network.** The galvanometer (§11.3) is this law as hardware —
it reads precisely the mismatch of the two arm-networks' restrictions
to the shared crossbar, and reads zero when they agree on S.

**Instances 12.3, regraded under the principle.**

- **Instance zero: the atlas itself (§2).** Charts 𝔸 and 𝕄 are two
  networks containing the same value space; exp/log performs the
  overlay (the value space as common *instance*, not two copies);
  Lemma 2.4 / Remark 2.5 transport is the manifestation. The
  construction this document specifies is the principle's first
  application to itself. **[S]**
- **The flat-binding theorem (§11.2).** S = V₄. The identification
  choice is the modulation structure: flat identifications (De Morgan
  preserved) transmit without twist; the other four transmit a twist.
  **[W]** as restated.
- **The Wheatstone bridge (§11.3, §11.6).** S = the crossbar. The two
  arm-networks overlay on it; deflection is the S-mismatch; balance is
  the two networks agreeing on S — at which point S vanishes from the
  conserved quantity entirely (§11.6), the channel carrying nothing.
  **[W]** as restated.
- **The rung-coupling theorem (source record, June 6; not previously
  in this spec).** Adjacent rungs of the generator tower are each
  intrinsically contractible — every simplex cone fills its own holes;
  **degeneracy is never intrinsic to a rung and appears only when two
  rungs couple.** The coupling form is S; its Pfaffian vanishes on a
  real locus (the forbidden corner at every rung). Direct coupling
  transmits deformation as a ripple tracking the Pfaffian exactly;
  **factoring the identification through Sylow-prime mediators
  modulates the transmission spectrally** — mediate every prime of the
  symmetry order and the residual is zero (constant velocity); drop a
  prime and that prime's frequency transmits as residual ripple. A new
  irreducible mediator is forced exactly when n+1 is prime. **[W]**
  (numerically witnessed in the source record) — the fullest worked
  example of step 4's modulation clause.
- **The phantom hierarchy (§11.10).** Adjacent levels overlay on the
  common-mode structure; what level n cannot read transmits to level
  n+1 through exactly that shared structure. **[S]**
- **Interfaces (§11.10, D-23).** An obligation-as-port is a
  *designated S awaiting its second network*: the register's open
  items are pre-positioned overlay sites. **[S]**

**Remark 12.4 (the Σ → Π path).** The source record's honesty flag
stands: the instances above share a pattern but live in different
categories — three instances, not one theorem (Σ, not Π). The overlay
principle names what a Π-promotion requires: construct the category of
(network, S-marking) pairs in which each instance is a pushout along
its S, and the pattern becomes one theorem with §11.2, §11.3, and the
rung result as corollaries. Until that category is constructed and
Candidate Law 12.2 is verified or corrected on it, the Σ grade is the
honest one: **OB-10.**

---

## 13. Consumption modes — how data is taken in and acted on

The atlas distinguishes five ways a value is *consumed*. They were
enumerated piecewise across §§1–12; collected here they expose a grading
that resolves OB-12. The organising fact, stated by the user: **getting
additive is logic in circuit clothing** — accumulation is not a
distinguishing axis, because every mode is some accumulation. What
distinguishes the modes is *what order of form they consume* and *whether
they preserve, project, or build the carrier.*

**Mode 1 — Accumulate (write).** Definition 1.1: increment × total →
total, on a single pin, no cross-read (Law 1.3). The only *write* mode;
the rest are reads. Consumes a **degree-1** quantity (a running sum).
**[W]**

**Mode 2 — Project to a named scalar (read-down, lossy).** Remark 3.5's
five shadows: mass, bias, unsigned decisiveness, single-conductor
collapse, ratio/null. Each discards everything orthogonal to the chosen
axis. Common-mode rejection is this mode used to discard mass. Consumes a
**degree-1** linear functional of the pins. **[W]**

**Mode 3 — Gate / threshold (consume-by-committing).** Witness 7.5: drive
to a saturating rail; the value is consumed by being *absorbed* into a
decision (the repeater). Unlike Mode 2 it does not read the value, it
*ends* it. This is the **first nonlinearity** — a saturating rail is not
a linear functional of the pins — so it is the first mode that leaves the
linear layer. **[W]**

**Mode 4 — Transport (lossless read-across).** Lemma 2.4 / Remark 2.5:
consume in one chart, conjugate by exp/log, act in the other. The only
mode that preserves *all* structure. The atlas is instance zero of it.
**[W]**

**Mode 5 — Overlay / glue (build-up).** §12: consume across a shared
instance S; computation in one network manifests in another, modulated by
S (Candidate Law 12.2). Unlike every other mode, this one *builds* rather
than reads or writes — it is a **bilinear pairing** of two reasoning
spaces. **[W]** for the mode; the manifestation law is **[C]**.

### 13.1 The Reed–Muller grading of the consumption modes

Under the identification of §11.10 — the doubling tree is the
Sylvester–Hadamard matrix, whose rows are the Walsh characters
(−1)^⟨a,x⟩, and **RM(1, m) is exactly the Hadamard code** under
x ↦ (−1)ˣ, with the Walsh–Hadamard transform as its fast decoder
(classical: MacWilliams–Sloane) — the modes grade by Reed–Muller degree:

- **Modes 1, 2, 4 consume degree-1 forms.** Accumulation, the mass/bias
  projections, and chart transport are all linear in the pins; they live
  entirely in **RM(1, m)**. This is the precise content of "additive is
  logic in circuit clothing": the whole linear layer — accumulate,
  project, transport — *is* the first-order Reed–Muller / Walsh layer,
  and nothing in a single tower climbs past it. **[W]**
- **Mode 3 (gating) is the first departure from RM(1).** The threshold
  nonlinearity is where degree can begin to climb; a decided rail is not
  a first-order form. **[W]**
- **Mode 5 (overlay) is the product that builds the degree filtration.**
  Gluing two networks along S is a **pairing** — and the pointwise
  product of two degree-1 reads (one from each tower) at the shared
  instance is a **degree-2** RM codeword (witnessed: the product of two
  linear forms is generically not in RM(1, m)). So the higher-order
  Reed–Muller layers RM(r, m) for r > 1 are reached by the **overlay
  pairing**, not by the doubling recursion. **[W]**

### 13.2 Resolution of OB-12 (the channel product)

The pilot (§11.10) found no product in the doubling tower and left open
where a product could come from. §13.1 answers it: **the product was never
supposed to be in the tower.** A single tower is a consumption mode
(accumulate/transport — Modes 1 and 4), and consumption modes are linear:
they stay in RM(1, m) **by design**. The bilinear product — the operation
that climbs to RM(r > 1) — is **Mode 5, the overlay**: the pairing of two
towers at a shared instance. The Cayley–Dickson search looked for the
product *inside the doubling recursion*; it is not there because it lives
on a different axis — the overlay (e₂/e₃ in §12's terms), not the doubling
(the tree's own recursion). **OB-12 is therefore resolved, not deferred:**
the doubling tree is RM(1, m) and correctly carries no product; the
product is the overlay pairing, and "climbing the RM degree filtration" =
"composing more overlays." The phantom hierarchy is the linear transport
layer; multiplication is what happens when two such layers are glued.
**[W]**

### 13.3 The no-collapse discipline, in code terms

The five modes give the prohibition (§3) a coding-theoretic statement:

- **Accumulate and transport are lossless** — they retain the full
  evaluation vector (all of RM(m, m), the whole transform). Mode 4 is the
  structure-preserving representation; nothing is discarded.
- **Project and gate are the named lossy consumptions** — decoding to a
  subcode (Mode 2 reads one RM(1) coordinate; Mode 3 hard-decides). Every
  lossy read is exactly a Remark 3.5 named projection.
- **Overlay is the one constructive consumption** — it builds *up* the
  degree filtration rather than reading *down* it.

So "never collapse the pair" reads, for codes, as **"never silently
project to a subcode; keep the full transform, and name every decoder."**
The Walsh–Hadamard transform is the lossless representation; every
standard decoder is a named lossy projection of it. **[S]**

---

## 14. Provenance (committed residue)

The prohibitions of this spec were each paid for by a caught error. The
history is the inoculation; flattening it away would invite re-deriving
the errors. Three corrections, committed:

**P-1 (the odds anchor).** An entire derivation pass was built on
x = E⁺/E⁻ before the correction: *"I don't (ever) default to thinking in
odds; it's always a balance of evidence, not a likelihood of outcome.
Quantum superposition without collapse."* The ratio is itself the error —
a forced Boolean resolution under a probability measure over a field of
interpretations. Became Law 3.1 and Definition 3.3.

**P-2 (the smuggled log-bridge).** "Evidence combines multiplicatively,
therefore take logs to get additive" was a default smuggled in, not a
derivation. Accumulation is natively additive per pin; logspace-sum vs
semiring-sum is a choice of operation, both constructible; the log is one
constructible view, not the canonical home. Became Law 1.4 and demoted
the multiplicative chart from "origin" to "chart."

**P-3 (the caught collapse).** Mid-derivation, defining OR by pure
inversion produced OR(a,b) = a·b: product self-dual, AND = OR. The
collapse forced the two-operation semiring as a hard condition. Became
Theorem 5.3(2) and CX-4.

**P-4 (the too-clean square).** The circuit V₄ came out clean enough to
trigger the diagnostic "so clean you're certain you screwed something
up." The error was scope, not content: the square is the
series/parallel-*reducible* half of network space, and the half it omits
is exactly the irreducible triangle (Y-Δ) where the sign lives. Became
§11.6 and the recorded method-heuristic: excessive cleanness signals a
reducible fragment posing as the whole.

---

## 15. Obligation register (the spec's own evidence pairs)

Open items, each carried as an (evidence-for, evidence-against) pair in
this spec's own idiom — held live, not resolved by fiat. Both-low items
are honest ignorance; any future both-high item is a flagged
contradiction, not an explosion.

**OB-1 — the value of ℛ.**
For: the contract is coherent (7.3); instances are definable today; the
saturation dynamics are now witnessed on the one-parameter chart
(Witness 7.5: absorbing rails, unstable neutral, fade-resistance = drive
to saturation); the circuit realization adds the metastability picture
(§11.5); and the corpus contains a five-validator survey of exactly this
fork — bounded structures vs unbounded resource algebras (D-22) — plus
the repeater requirement that any instance regenerate both modes
(§11.10).
Against: the witnessed dynamics attach to the decision projection, not
the carrier pair; the per-pin accumulator range, the specific potential
and measure, and the critical drive remain explicitly the user's design.
*Status: open by design — the permanent loop, now with a tighter
contract. Discharge path: a chosen instance per application, each
recorded as an instance, never back-ported as "the" range.*

**OB-2 — status of the quantum framing.**
For: the literal commitments (unnormalized pair, no quotient, interference
region) are all witnessed.
Against: no phase-composition law is specified; "amplitude" beyond the
dictionary of 8.2 is so far analogy. *Discharge path: either specify how
phases compose (normative) or mark 8.2 as the full literal content
(illustrative).*

**OB-3 — Conjecture 8.3 (holonomy = enclosed contradiction).**
For: the dictionary makes the statement well-typed; a test harness with
the d∘d = 0 gate exists; **and the discharge path now has a proven
sibling** — Abramsky–Brandenburger sheaf-theoretic contextuality
(App. B, S-F) already establishes contradiction/contextuality as a
non-vanishing Čech cohomology obstruction to gluing, with δ∘δ = 0 built
in. *Discharge path (upgraded): construct the comparison functor from
the EL-Atlas coefficient system to AB-contextuality; if it lands,
Conjecture 8.3 inherits a proof-shape rather than starting bare.*
*Boundary clause (Carù): the cohomological obstruction is not a complete
invariant of strong contextuality, so the identification can be sound but
cannot be made complete — 8.3 must be stated as "non-vanishing holonomy ⇒
enclosed contradiction," not an iff.* **Harness-framing correction
(recorded run):** the d∘d=0 gate was first set on a *filled* triangle,
which is contractible (H¹=0) and can carry no holonomy — there is nothing
enclosed, so the test was structurally incapable of exhibiting the
phenomenon. On the triangle *boundary* (an unfilled 1-cycle) H¹=1 and a
**bias-holonomy genuinely exists** (= net bias accumulated around the
loop). So the conjecture must be tested on complexes with real 1-cycles,
not filled simplices. Status after the run: bias-holonomy around a hole is
**witnessed**; the identification of that holonomy with *contradiction*
(mass / both-high) is still unrun, and the AB comparison functor is still
unbuilt. The d∘d=0 gate itself passes (it always will — it is the cochain
axiom); the content is the H¹ class, which requires a hole to be nonzero.

**OB-4 — formal verification of the correspondence tests (§10).**
For: five witness functors are sketched with concrete tests.
Against: none executed; all entries remain Implicit/Candidate, none
Present. *Discharge path: execute per test; promote to Present only with
a witness.*

**OB-5 — the strong Wheatstone identification. WITNESSED (via the chart adjunction).**
The galvanometer-null and the pin-swap fixpoint are the **same balance
locus read in the two charts** (Lemma 2.5b): the pin-swap fixpoint is
bias b = E₊−E₋ = 0 in the additive chart, and the galvanometer balances
at the ratio E₊/E₋ = 1 in the multiplicative chart — and exp(b)=ratio
maps one to the other losslessly, mass preserved as the product axis. A
run initially mis-flagged this as a chart conflation (a forbidden ratio);
that was itself the error — crossing charts is the exp ⊣ log adjunction
(invertible, structure-preserving), not the §3 collapse (lossy,
one-way). See Remark 2.5c for the distinction. The galvanometer reads the
**chart-image** ratio, not the **collapse** ratio. *Status: the weak and
strong structural identifications stand as witnessed; the remaining open
piece is only the further claim that galvanometer *deflection magnitude*
equals the sign-cocycle's value (the affineness/R12 identification),
which is a separate quantitative claim untouched by this correction.*

**OB-6 — CHL-E axiom check.**
For: the two-rail / harmonic-mean-AND / additive-OR architecture matches
the conductor square (11.1), and contradiction-as-high-resistance matches
non-explosive ⊤-localization; **a machine-checked formalization exists**
(EvidenceAsElectronics.agda and its CHL extension, App. A D-3) covering
the ℝ⁺ operations of chart 𝕄 and an ℂₛ s-plane AC generalization.
Against: whether the architecture satisfies the paraconsistent axioms
against the Priest/Belnap literature was flagged at review time and never
checked; the Agda modules postulate the foundational types rather than
deriving them. *Discharge path: check the axioms; the Agda modules give
the statements machine-visible form. If they hold, 11.7's lineage entry
promotes to a witness for §§5–6.*

**OB-7 — the Noether statement for the carrier. RESOLVED (clean two-pairing).**
A run initially called this inconsistent (the proposed continuous flow
conserved bias while the discrete pin-swap conserves mass); that was a
single-chart artifact — the wrong continuous partner was chosen. Corrected
under the adjunction (Lemma 2.5b), the structure is clean and complete:
there are **two one-parameter symmetry subgroups, each pairing an
involution with a continuous flow conserving the same axis:**

| involution | continuous partner | Noether charge | chart picture |
|---|---|---|---|
| pin-swap | squeeze (E₊,E₋)↦(eᵗE₊, e⁻ᵗE₋) | **mass** = E₊·E₋ | hyperbolic rotation |
| negate-a-pin | common translation (u₊,u₋)↦(u₊+t,u₋+t) | **bias** = E₊/E₋ | dilation |

Mass and bias are the two Noether charges of the two subgroups of
(ℝ⁺,×)² ≅ (ℝ,+)²; the squeeze fixes the dilation charge and vice versa.
The pin-swap (mass-conserving involution) pairs with the squeeze
(mass-conserving flow) — same axis, witnessed. *Status: resolved as a
clean pairing. The discrete pairing extends to a genuine continuous
(Noether) statement; the earlier "inconsistency" was a flow-choice error,
not a structural one.* **[W]**

**OB-8 — Thévenin/Norton as named external collapse.**
For: the move exists twice in the corpus unnamed (D-1's
equivalent-single-conductor shadow; D-13's Star-Mesh as reversible
level-conservation); Remark 3.5 supplies the governing discipline
(legal as instrument, forbidden as semantics); §11.6's Y-Δ is the
special case already witnessed.
Against: no corpus document derives the port abstraction for an
*evidence* network; the claim that Norton/Thévenin source duality is a
De Morgan-shaped swap is unverified; the relation between Star-Mesh
reversibility and the irreversibility of single-element collapse
(Lemma 3.2 at network scale) is unworked. *Discharge path: define the
port abstraction of an evidence network; verify what it conserves
(mass? bias? neither?) and bind it to the Star-Mesh transform.* **Machinery
(draft 7):** the Baez–Fong black-box functor (App. B, S-G) is exactly
"named external collapse as a functor" — Thévenin/black-boxing of an open
network to its port behaviour, proven functorial. Bind the evidence-port
abstraction to it rather than constructing from scratch.

**OB-9 — phase: where does it come from? (fully open; complexification retracted).**
For: the corpus works in ℂₛ (D-3) and carries complex semantic impedance
Z = R + jX (D-17); §11.5's dissipative/reactive split is suggestive of a
real/imaginary decomposition; §8's amplitude reading wants a phase.
Against: the obvious route — complexify the multiplicative chart — is a
**category error** (Caveat 2.4a): 1/y is the *semiring* involution, not a
field reciprocal, and signed quantities live in the additive chart, not
in an extension of 𝕄 to ℂ. So the "complexified atlas" framing is
withdrawn; phase has *no established origin* in the current structure.
OB-9 and OB-2 (phase composition) are both open and coupled. *Discharge path: construct the complex charts, check the
three structures, and state the phase-composition law or its
obstruction.* **Run RETRACTED as ill-posed (Caveat 2.4a).**
A first run complexified 𝕄 and reported a "second fixed point y=−1" and a
"unit-circle balance," concluding phase was the new DOF. That was a
category error: 1/y is the involution of the **semiring** [0, ∞], not a
reciprocal on a ring/field, and must not be extended to negative or
complex arguments — the signed quantities already live in the additive
chart (sign negation, fixed point 0), reached by log, not by
complexifying the semiring. There is no second fixed point and no
ambiguous neutral; the unit-circle result was an artifact of imposing a
field structure 𝕄 does not have. **Phase is therefore reopened as fully
open:** the spec makes *no* claim about where phase comes from. It is not
"the DOF exposed by complexification" (that scaffolding is withdrawn); if
phase enters at all it is a separate enrichment whose origin is
undetermined. Coupled to OB-2, which is likewise open. **Consolidated and resolved-as-type in §8.5–8.6:**
OB-2/OB-3/OB-9 are one object (the phase connection), three gradings; its value
group is **forced to be V4**, and it is **resolved as a dependent type** with a
fixed V4 interface and two pinnings (carrier/measurement and action/theorem), both
retained. The remaining freedom is the *pinning* — a declared model parameter
(upstream, like R), not an open obligation of the logic. Status: resolved-as-type;
no evaluation debt. Draft 13: the two pinnings identified as the two
representations (corner = exact V₄ + S₃ frame, Hol(V₄) = S₄ total; pin
plane = D₄ central extension, phase = extension class); the holomorph
candidate (re-pinnings compose as Aut(V₄) = S₃) is RESOLVED-WITNESSED.*

**OB-10 — the overlay theorem (Σ → Π promotion).**
For: the principle is stated and committed (12.1, user-origin); five
instances plus instance zero are enumerated with their S identified
(12.3); a candidate manifestation law exists (12.2, Mayer–Vietoris
shape) with hardware semantics (the galvanometer as the S-mismatch
reader) and a numerically witnessed modulation example (Sylow
factoring of the rung coupling).
Against: the category of (network, S-marking) pairs is not
constructed; the reasoning-space topologies have not been given the
complex structure Mayer–Vietoris requires (the cohomology theory is
unfixed); the source record's Σ-flag explicitly withholds the
identification of the instances as one object. *Discharge path: fix
the cohomology theory of a reasoning space; construct the overlay
category; verify or correct Law 12.2 on it; re-derive §11.2, §11.3,
and the rung theorem as corollaries of one pushout statement.*
**Machinery (draft 7, App. B, S-G):** the category need not be built from
nothing — **decorated cospans (Fong 2015; Baez–Fong 2018)** already give
networks-glued-along-shared-boundary as pushout, with functorial
semantics; **Hansen–Ghrist cellular-sheaf spectral theory (2019)** already
proves the manifestation law's shape — the sheaf-Laplacian kernel is the
global sections, and data vanishing on the relevant restriction maps is
not transmitted, which is precisely Candidate Law 12.2 including its
"vanishes on S ⇒ invisible" clause. Reframed task: define the
**evidence-sheaf** decoration on a cospan/cell complex, then 12.2 becomes
"verify the sheaf-Laplacian statement under this decoration," and the
genuinely original content localises to the *decorations and the instance
menagerie* (V₄ bindings, Sylow mediators), not the gluing machinery.

**OB-11 — the ○/● operators as carrier gates.**
For: the closest kin, LET_F (Rodrigues–Bueno-Soler–Carnielli, App. B,
S-B), supplies classicality (○) and non-classicality (●) operators the
EL-Atlas carrier lacks as named gates; the carrier has natural candidate
regions (○ ≈ the saturated-bias rails of Witness 7.5, where the state is
decided/classical; ● ≈ the high-mass-low-|bias| region of §4, where
conflict is live).
Against: the identification of ○/● with carrier regions is proposed, not
checked; the LET_F axioms for ○/● have not been verified against the
carrier semantics. *Discharge path (sharpened, §5.8f): define ○ = the c-degenerate
region (the inverse-locked locus ∪ the saturation rails) and ● = the
c-live region; check the LET_F axioms against these; if they hold,
position the spec as "LET_F's geometry" and import LET_F's completeness
results.*

**OB-12 — the channel product. RESOLVED (§13.2).**
The product is not in the doubling tower and was never supposed to be: a
single tower is a linear consumption mode (RM(1, m) by design, §13.1).
The bilinear product is **Mode 5, the overlay** — the pairing of two
towers at a shared instance, which produces degree-2 RM codewords
(witnessed). Climbing the Reed–Muller degree filtration = composing
overlays, not climbing the doubling recursion. The Cayley–Dickson search
looked on the wrong axis (the tree's recursion instead of the overlay).
*Status: resolved. Residual sub-question (optional, demoted): whether the
overlay pairing, iterated, reproduces a specific named algebra — but the
spec no longer needs it to, since the product has a home (§12).*

---

## Appendix A. Corpus cross-reference (Google Drive)

Documents in the corpus matching **two or more** atlas terms, with the
sections they touch. **Status correction (draft 7):** this corpus is
largely AI-co-generated across the same workstream. It is therefore a
**provenance and shadow record — the workstream's own externalised
notes-to-self — not external validation.** Corpus convergence measures
internal coherence across sessions (which is its purpose); it carries
**zero weight** as evidence of external novelty or correctness. External
support lives only in Appendix B's import/export edges. Where a corpus
document *adds* content, the addition is integrated above with an
"(App. A, D-n)" tag; where it merely restates, it is listed here only.

**D-1. Evidence–Differential–Cayley–Dickson Construction** (3 doc
copies + 2 PDFs; the densest match — effectively a parallel
consolidation). Terms: the (e⁺, e⁻) carrier with 0 = no evidence (§1);
Belnap–Dunn / De Morgan / bilattice with channels as independent
supports, not complements (§1, §4, §9 CX-2); two-rail conductance with
series/parallel connectives (§11.1); l-space as **additive hull that
enriches, not replaces, the raw semiring** — independent corroboration
of Law 1.4; bridge as pair-of-pairs (→ §11.3); projection plurality
(→ Remark 3.5); carrier-range instances (→ §7); Cayley–Dickson
conjugation involution as structural operator (§11.6 lineage, OB-5);
explicit literalness corrections C1/C6 matching this spec's [W]/[S]
discipline.

**D-2. CHL-E Monograph** (2 copies: "The Curry-Howard-Lambek-Electronics
(CHL-E) Isomorphism"; "Paraconsistent Logic and Isomorphisms"). Terms:
paraconsistency via circuit dynamics, explosion-of-contradiction as
motivating crisis, CCC structure. Touches §11.7, OB-6.

**D-3. EvidenceAsElectronics.agda / EvidenceAsElectronics_CHL.agda +
"Formalizing Evidence-Electronics Correspondence" (exegesis).** Terms:
machine-checked evidence/electronics isomorphism; ℝ⁺ with R+/R÷ and unit
1 (the chart-𝕄 operations of §2); ℂₛ s-plane AC generalization (reactive
direction of §11.5); HoTT identity paths. Touches §2, §11.7, OB-6
(discharge infrastructure).

**D-4. "The Isomorphisms of De Morgan Duality" monograph.** Terms: De
Morgan duality as instance of broader duality; paraconsistent physical
logic; G-Value Calculus. Touches §5, §11.1, §11.7.

**D-5. Nedge G-Value Calculus analyses** ("Researcher 3" + Theme-4
expansion). Terms: G-values as multi-dimensional truth degrees beyond
bivalent/fuzzy (§1's regions); contradiction as a measurable,
information-rich physical state, dialetheism (§3, §11.5). Touches §1,
§3, §11.5, §11.7.

**D-6. "Formalizing Document Interrelationships."** Terms: categorical
pushout of D-3's Agda module with the SPPF exegesis — the corpus's own
record that the evidence-electronics thread and the
no-collapse-the-fiber thread (§8's discipline) compose. Touches §8,
§11.7. Meta-document.

**D-7. Agda Formalization of Wheatstone Bridge** (multiple copies + a
"Physical Domain Formalization" folder). Terms: formal proofs of
balanced null-comparator vs unbalanced differential-sensor states —
exactly the §11.3/§11.6 dichotomy in type-theoretic form; Kelvin and
Carey Foster topological extensions. Touches §11.3, §11.6, OB-5
(discharge infrastructure).

**D-8. "Comprehensively reformalize…" (MetaCategory extension).** Terms:
Wheatstone as a Theory in a monoidal category of resistive networks;
Ohm/KCL/KVL as named axioms; **the null state formalized as
commutativity** — a categorical restatement of balance = pin-swap
fixpoint (§11.3). Touches §11.3, OB-5.

**D-9. PGZ Constructive Proof Machine.** Terms: Belnap four-valued logic
enforced in a verified micro-architecture; Lojban predicate semantics as
the specification language — the same three-formalism witness discipline
this spec was checked under. Touches §4, §9 CX-2.

**D-10. "Categorical Duality and Information Conservation."** Terms:
conservation law from categorical-duality symmetry (the Noether schema,
explicitly analogized); Cayley–Dickson property-degradation ladder with
content conserved. Touches §11.8 (Noether), §11.6 lineage, OB-7.

**D-11. "G-Calculus Simulation and Verification."** Terms: RK4 dynamics
over the 5D_State; G_AND/G_OR composition; equilibrium existence and
uniqueness via contraction; functorial equivalence to Hopfield networks.
Touches §11.5, §11.9 (verification tier), OB-3's harness ecosystem.

**D-12. "Circuit Theory and Differential Algebra" + "Kirchhoff's Laws
Application" reports.** Terms: series/parallel composition algebra; KCL
as global charge conservation; KVL voltage division; series →
series-parallel transition analysis. Touches §11.1, §11.8 (Kirchhoff).

**D-13. "A Coconstructed Universe: the Sys Framework."** Terms: S₀ = a
real-valued conductance line; Sₙ₊₁ = Sₙ × Sₙ as differential pairs (the
recursive doubling-tree as hardware recursion — same operator as D-1;
labelled Cayley–Dickson in the corpus, but see §11.10: the doubling is
real, the product is not exhibited);
**Star-Mesh Transform as the Process facet: reversible, conservation
across abstraction levels** (the n-ary Y-Δ of §11.6, and the unnamed
Thévenin-shaped move of §11.8). Touches §11.6, §11.8, OB-8.

**D-14. "Exploring XSPICE Mixed-Signal Simulation."** Terms:
analog/digital (continuous/discrete) simulation dichotomy; MNA. Touches
§11.9 (tooling tier).

**D-15. "Spice Simulators: LTspice vs. B2."** Terms: hypothesis-driven
comparison of simulation platforms. Touches §11.9 (tooling tier).

**D-16. "System Pi: Physics-Based Linguistic Parser."** Terms: language
as a physical system under conservation laws; impedance + category
theory + circuit dynamics as the semantics. Touches §11.9 (application
tier).

**D-17. "G-Calculus Hyperparameter Bridge Circuits" +
"G-Calculus Curry-Howard Modelings" + "g-calculus WIP."** Terms:
RLC/optimizer identifications (momentum = inductance, learning rate =
conductance); "logics-as-circuits" correspondence table; Total Semantic
Impedance Z = R + jX. Touches §11.5, §11.7, §11.9 (application tier).

**D-18. "Relational Construct Algebra (RCA) Encyclopedic Reference."**
Terms: computation as equilibrium restoration under physical
conservation laws ("algebraic physics of meaning"). Touches §11.8,
§11.9 (application tier).

**D-19. "Branch, Resistor, and Isomorphism Analysis."** Terms:
branch ↔ resistor isomorphism (logical derivation / syntactic
dependency / decision path ↔ network element); Boolean structures made
dynamic under Kirchhoff + Ohm; R/G duality as the logical engine.
Touches §11.1, §11.8, §11.9 (application tier), §11.10.

**D-20. "Nedge Concepts: Tension, Conductance, Reactance"
(Nedge–Sigma Unification).** Terms: paraconsistent information physics;
tension/conductance/reactance vocabulary (§11.5's coordinates); the
Vacuum Density problem (cost of encoding non-events); structural
critique of Bayesian-probability foundations — independent support for
Law 3.1. Touches §3, §11.5, §11.10.

**D-21. "G-Value Calculus Deep Analysis."** Terms: G-Values as positive
reals G > 0; negation as reciprocal (chart 𝕄's not(y) = 1/y, §2);
conjunction as sum of reciprocals (parallel/harmonic AND, §6, §11.1);
the domain constraint as singularity-avoidance. Touches §2, §6, §11.1.

**D-22. "Cross-model Nedge G-Value Calculus Analysis."** Terms: five
independent formal validations compared; divergence spectrum from
bounded algebraic structures to continuous unbounded resource algebras
— the ℛ fork (§7, OB-1) surveyed across five validators. Touches §7,
OB-1.

**D-23. "Axioms as Solvable Interfaces" (2 copies).** Terms: axioms as
solvable interfaces with theorem-generating structures; triangulated
coherence; homological auditing. The standardization theory of this
spec's obligation register (§11.10, §13). Touches §0, §11.10, §15.

**D-24. "Deep Structural Coherence Protocol" + SYSTEM Π v2.22
artifact.** Terms: grand unification of CLT / SymNum / CHIP / System Pi
as fibered components of one total category; self-hosted versioned
upgrade artifact as protocol packaging. Touches §11.9, §11.10;
meta-documents for the CHIP workstream this spec runs under.

Corpus note: D-1's provenance discipline ([E] external / [U] user-origin
/ [I] internal synthesis) is the same three-way grading as this spec's
[W]/[S]/[C]; the two documents can be cross-keyed if merged.

---

## Appendix B. The prior-art adjacency map (external literature as overlay instances)

**B.0 Lineage (corpus-internal, recovered by the H-series re-sweep).** The
atlas formalizes a program the corpus already named: **BK4VL**, the user's
local term for a *resource-aware extension of the Belnap–Dunn / B4 /
bilattice family*, consolidated in the March 2026
"Evidence–Differential" construction cluster — which contains the carrier
verbatim ((e⁺, e⁻), 0 = no evidence), the l-space additive hull
("enriches, not replaces" the semiring), the bridge as
comparison-of-comparisons, the doubling tower with conjugation (§5.9's
interface, there under its famous instance-name), the Poulton phantom
hierarchy as [E4], and its own [E]/[U]/[I] provenance discipline. The
atlas's relationship to that cluster: same program, rigorized — with the
locus-closure caution (its C1) and the projection plurality (its C4) now
theorems and inventories rather than warnings. **[S]** Sharpened by the
N-series (N2/N3): the relationship is not adjacency but **quotient** —
the atlas is the pre-quotient of Nedge's own Layer-2 semantic engine;
the G-Value Calculus is the carrier modulo the diagonal (§5.7e lift
theorem, claim NGL), and Nedge's Layer-3 four-valued logic demands
exactly the axis that quotient removes (§5.7e two-gate theorem, claim
NVL, S_fd5ddbe7ac57). **[S/W]**

This is the generative reading of the external review. Each mature
literature the atlas touches is a **second network** sharing a common
structure S with the atlas; the review's "prior art" findings are the
**import edges** (theorems the atlas inherits through S) and the atlas's
content is the **export edges** (what it carries back that the neighbour
lacks). A novelty verdict is the *bias-only* projection of this map and
is forbidden (Remark 3.5, §3): the map's **mass** — the density of these
edges — is the actual situation, and dense connection to mature fields is
the both-high state, not the both-low one. The neighbour is identified;
S is named; the manifestation runs both ways. This is §12 applied to the
spec's own scholarship.

**S-A — Bilattices / twist-structures.** *S:* pair-with-swap-negation;
two orders on one carrier. Kalman (1958) ¬(a,b) = (b,a) **is** pin-swap;
Ginsberg/Fitting knowledge-vs-truth orders **are** mass/bias as orders.
*Import:* ~60 years of representation theorems, Cignoli functoriality,
the N4 connection — §4/§5 inherit proofs instead of owing them.
*Export:* the continuous geometry (mass/bias as coordinates, not just
orders), the exp/log charts, the §11 instrument layer — none of which
twist-structures carry. *Position:* the atlas **specialises** this
family. *Generates:* check the bilattice interlacing axioms on [0,∞]²
(new-lemma candidate).

**S-B — Carnielli–Rodrigues (LET_F) / Smets TBM / Jøsang / annotated
logics.** *S:* independent non-complementary evidence pair; sum > 1 =
conflict, sum < 1 = ignorance; normalization refused as principle
(Smets retains m(∅) > 0); probability recovered as special case
(P(○α) → 1). *Import:* the ○/● operators (named carrier gates the atlas
lacks → OB-11); rigorous probabilistic semantics; PAL2v's
certainty/contradiction Cartesian axes **already fielded in EE
monitoring** — a deployed cousin of the crossbar. *Export:* the charts,
the V₄/De Morgan instrumentation, the circuit witnesses, the overlay
machinery — LET_F has no geometry. *Position:* **closest kin; the atlas
extends, does not discover.** Honest framing: "LET_F's geometry."

**S-C — Decision neuroscience (LCA; absolute-vs-relative evidence) +
Good/Turing weight of evidence.** *S:* two competing accumulators;
sum/difference dissociation. *Import:* **empirical confirmation that the
mass axis is physically real** — the sum (absolute evidence) and
difference (relative evidence) are behaviourally dissociable; DDM
(difference-only) is the *collapsed* model, LCA the uncollapsed one.
*Export:* the algebraic skeleton these implement numerically; the
prohibition (§3) as a *theoretical explanation* of why DDM fails where
LCA succeeds. *Position:* **independent witness, not a novelty defect**
(this is the review's sharpest mis-grade, corrected). See B.1 below.

**S-D — Tropical / idempotent analysis; t-norm/t-conorm duality; MALL.**
*S:* log-sum-exp ↔ (max, +); two-operations-plus-involution duality.
*Import:* the Maslov dequantization parameter h — which **is OB-1's range
parameter ℛ, independently re-derived**: the external probe found the
document's own H₁ generator and named its deformation family (h → 0 =
tropical saturation). *Export:* the evidence interpretation; the circuit
realisation of the duality. *Position:* the atlas **specialises** the
log-semiring. *Generates:* restate Contract 7.2 with h as the Maslov
coordinate; ℛ instances = points on the dequantization family.

**S-E — Shannon (1938); network duality; Y-Δ / Epifanov; Cano-Jorge
(2025).** *S:* series/parallel = AND/OR; R↔G duality; star-mesh.
*Import:* the full classical reduction theory; Epifanov as the formal
backbone of §11.6. *Export:* graded values, the evidence pair, the mass
readout, paraconsistency — Shannon is the **Boolean single-rail shadow**
of §11. *Position:* the atlas **generalises** switching algebra to a
graded two-rail logic. *Generates:* cite Shannon in §11.1; engage
Cano-Jorge 2025 (concurrent — priority matters); the functor-statement
softening (§11 intro) is the rigorous form of the binding.

**S-F — Abramsky–Brandenburger sheaf contextuality; AMB cohomology;
Carù.** *S:* contradiction as obstruction-to-gluing; δ∘δ = 0. *Import:*
**a proven older sibling of Conjecture 8.3** — contextuality as
non-vanishing Čech cohomology. OB-3's discharge upgrades from "run the
harness" to "build the comparison functor," and Carù's incompleteness
becomes 8.3's boundary clause (sound, not complete). *Export:* the
two-component unnormalized coefficient system — a *different coefficient
choice* than AB's possibilistic/probabilistic one, hence a candidate new
coefficient system **for** their framework. *Position:* **serves**;
defer to the proven version, inherit its proof-shape.

**S-G — Compositional network theory (Fong decorated cospans 2015;
Baez–Fong 2018) + Farmer little theories + Hansen–Ghrist cellular sheaves
2019.** *S:* pushout-gluing along shared boundary; theorem transport;
sheaf-modulated transmission. *Import:* **OB-10's requested category
already exists** (decorated cospans); the manifestation law has a
theorem-template (Hansen–Ghrist: sheaf-Laplacian kernel = global
sections; data vanishing on restrictions does not transmit — Candidate
12.2 including its "vanishes on S ⇒ invisible" clause); the black-box
functor is OB-8's Thévenin discipline, proven. *Export:* the
decorations (evidence-valued) and the instance menagerie (V₄ bindings,
Sylow mediators) — decorations Baez–Fong never chose. *Position:*
**serves**; the Overlay Principle is repositioned as an
*instance-discovery program over known gluing machinery*, with the
candidate-novel content in the decorations.

**S-H — Phantom circuits (Jacob 1882; Carty 1886; AT&T 1910s);
differential signaling.** *S:* common/differential mode hierarchy.
*Import:* 140 years of practice and the historical record. *Export
(the two standing novelty candidates):* (1) **CMR-as-semantics is the
forbidden epistemic collapse** — mass is data, so rejecting common mode
discards the conflict-vs-ignorance datum (no prior art found for this
reinterpretation); (2) **phantom hierarchy = a Hadamard
doubling tree with swap-conjugation** (recursive (sum,diff) splitting +
pin-swap involution) — witnessed by the OB-12 pilot; the recurring
"Cayley–Dickson" label was a nearest-name frame-collapse asserting a
bilinear product the construction never contained. The doubling tree is
the actual object; CD is an optional completion nothing here requires. *Position:*
**serves; the publishable seeds live here.**

### B.1 Convergent witnesses (the both-high reading)

The mass/bias distinction — the one thing the atlas most insists on not
collapsing — is **independently forced in three mature fields that did
not borrow it from each other**:

- **Logic:** LET_F's sum > 1 (conflict) vs sum < 1 (ignorance), with the
  two evidence measures independent (S-B).
- **Engineering:** the Wheatstone two-readout instrument — galvanometer
  (bias) and supply/common-mode (mass) — recovering both coordinates the
  odds-line destroys (§11.4, S-H).
- **Neuroscience:** absolute (sum) vs relative (difference) evidence,
  behaviourally dissociable, with DDM collapsing what LCA keeps (S-C).

Three independent derivations of the same distinction is the **strong**
form of support. The review read this convergence as "the insight is not
novel"; in the atlas's own grading it is the opposite — a both-high mass
reading that a bias-only (novelty) projection cannot see (Lemma 3.2,
applied to the assessment). The honest claim is therefore not "we
discovered mass/bias" but **"we re-derive, in a logical/algebraic
setting with an explicit exp/log chart structure and a circuit
instrument, a distinction independently established in evidence theory
and decision neuroscience — and we supply the geometry and the
no-collapse discipline that those settings leave implicit."**

### B.2 What the external review contributes, kept intact

The review's **bias-axis content is good and is retained**: the reading
list (S-A…S-H authors, correctly prioritised); the three falsifiable
tests (run d∘d = 0; one worked overlay as a decorated-cospan pushout with
sheaf transmission computed; the phantom staged-loss check — **the third
is now done**, §11.10/OB-12); the discipline of explicit functor
statements over "same object"; and the warning that the most quotable
claims ("same object," "holonomy = contradiction") are the least
supported. What the review got wrong was the *projection* — collapsing a
two-axis map to a novelty scalar — not the *edges*, which are accurate
and are the substance of this appendix.

---

*End of draft 18. CHIP state: OPEN CHIP-(N+1), gated on OB-1. Draft 18
imports the Z-series (zero-divisor) corpus thread: the breakdown locus of
radial multiplicativity as enumerated, G₂-oriented geography
(dim ZD = 2ⁿ − 5; Moreno's equal-norm-and-orthogonal characterization,
read as the radial chart's conflict corner [C]); the conservation
principle as the algebraic dual of the §11.10 recursion — residue at
level n is structure at level n + 1 on both the signal and algebra
sides; the OB-1 consequence that high-rung tropical limits need a
zero-divisor-indexed valuation; and Remark 3.6, joining the corpus's
representation-as-rationals zero-divisor resolution to the prohibition
as one design principle: when an operation would lose information,
encode it instead of performing it. Non-closure remains the design,
not the defect.*
