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
