# Dent — System Primer

*A graded outer term algebra with normalization and perfect recall.*

This document is a handoff primer. It states the architecture of the system ("Dent") and the
invariants its code is meant to satisfy, so that a reader (human or model) can work on the
repository without re-deriving the design. It is descriptive of intent and structure; it is **not**
a proof. Where it names an obligation, the obligation is to be discharged in the repo (Agda for
what types can carry, external measurement scripts for what observation must carry), not assumed
here.

---

## 0. One-sentence statement

The system is a **graded exterior (outer) term algebra** in which the wedge operator doubles as a
**connecting map of an exact sequence**, read as **quotient** (lift the new distinction up a grade)
or **mod** (retain the unreduced remainder at this grade) according to demand; nothing actual exists
until a need **forces** it; and no **residue** of any forcing is ever discarded — it is reinterned
one grade up with a coordinate translation, giving the structure **perfect recall** without
unbounded storage.

---

## 1. Governing principle (the admissibility law)

A single principle generates everything below it:

> **A distinction is valid iff it is constructible; if constructible, behaviorally reachable; if
> reachable, observable; if observable, coverable. If not coverable, it is not a valid runtime
> distinction.**

Restated as the **fundamental theorem of vacuity**:

> **A construction is vacuous iff it forces no distinction.** Nothing that forces no distinction is
> admitted.

The five clauses are five gates, applied at every scale (value, path, design choice, meta-grade).
The **coverability** clause is independent and load-bearing: a distinction may be observable yet
**uncovered** — read by nothing downstream — and that is the canonical vacuity failure (see §7,
self-referential vacuity). Coverability must be a separate gate from observability; it does not
follow from it.

---

## 2. Forcing (existence as evaluation)

Existence is **forcing** in the call-by-need / Cohen sense, **not** the Nietzschean (will) sense:

- The structure determines distinctions **latently**. Forcing does not author them; it **collects**
  them. The term algebra is prior to the act of forcing.
- A latent distinction is instantiated only when a downstream **need** demands its value. Until
  then it is a thunk (a "capsid": an encapsulated, inert payload awaiting expression).
- **Unforced ⇒ not actual.** Things that are merely possible (undescribable elements, unlooked-for
  meta-grades) cost nothing because they are never instantiated. This is the same reason the
  indescribable subsets of ℕ never burden the system: nothing points at them.

**Discipline:** *going to look is itself a forcing and must be paid by a need.* Instantiating
structure for its own sake (a grade built because it can be, a perspective held "for flexibility"
that no need ever collapses) is an unforced capsid at that level and is pruned by §1.

---

## 3. The carrier: a 3-graded outer term algebra, construction order as the 4th dimension

- The **graded wedge** is the carrier, not an operator layered on a separate term set. The term
  algebra **is** the closure of the carrier wedge under its laws. **Associativity** (coherently — the
  reassociator, below) is a carrier law; **commutativity and the graded signs are equations of the
  DETECTOR reading** (§8), *not* of the carrier — the carrier retains order and repetition
  (construction order is the 4th dimension), so it cannot be commutative or alternating. Laws are
  *equations the relevant operator satisfies*, not metadata stamped on terms.
- It is **carrier-independent**: terms are individuated entirely by which wedge-equations relate
  them, not by what they "are."
- There are **three graded term-dimensions**; **construction order is the fourth**, *generated*
  rather than given — it is the trace the moves leave as they fold. Time is intrinsic (the sequence
  of wedge-applications), not an assigned coordinate.
- **Two wedges, two layers — never identify them.** There is a **carrier wedge** and a **detector
  reading**, and the faithfulness story depends on their *not* being one operator. (§3 originally
  fused them under one "∧"; that was a wording slip, corrected here.)
  - **Carrier wedge (this term layer):** a **free** graded term algebra. It **never annihilates**:
    `i ∧ i = i ∷ i ∷ []`, a retained repetition, never `0`. This is forced by perfect recall —
    annihilation is discard, and the carrier *records* (never-annihilate is the separation axiom
    wearing its operational face). The carrier is associative (free monoid) but is **not**
    commutative and does **not** satisfy `a ∧ a = 0`. `Substrate.Algebra.Wedge.AxisWord` is this layer.
  - **Detector reading (§8, measurement layer):** the **exterior/alternating** *reading* of carrier
    terms. Here `measure(a ∧ a) = 0` — self-pairing forces **no new distinction** — and
    `measure(a ∧ b) ≠ 0` iff `a`, `b` are independent directions. Vanishing measured wedge =
    dependence = no new distinction. **"Outer is load-bearing" is a claim about the DETECTOR's
    geometry** (its zero-locus is exactly vacuity), NOT that the carrier annihilates. The bridge is
    the grade homomorphism (§8); its kernel is precisely the retained-but-non-distinguishing carrier
    content (e.g. self-pairings), which it MUST contain. "forces a distinction" = "measures to
    nonzero" lives at the detector, over carrier terms the carrier still holds intact.

**Associativity** is not asserted strictly; it is **recovered by flipping the grade-axes** (the
reassociator carries a graded sign). Coherence of the reassociator (the Mac Lane pentagon, or its
graded analogue) is an obligation: if grade-flips do not cohere, normalization (§4) becomes
path-dependent and the forest stops being well-defined.

---

## 4. Normalization with retained residue (confluence without forced normal forms)

The store is an **SPPF-style shared packed forest** (cubic sharing; common subderivations shared,
alternatives packed). Ambiguity/packing **is** the deferred-collapse superposition from §2.

- A new construction is reduced by the **matcher**: "rotate it (under the group, §6) until it matches
  an existing construction; store the residue." This is hash-consing / canonicalization: newcomers
  are normalized onto the existing forest so sharing stays maximal.
- **Confluence is not obtained by proving a global diamond.** It is obtained by **never discarding a
  residue.** When two transform-paths fold a newcomer onto the "same" node but differ, the
  difference is *retained as a graded residue* attached to the merge. (This is the unclosed critical
  pair, kept as data rather than oriented away.)
- The residue is itself reducible: it **reinterns** — "rotate until it matches something we have,
  store the residue, recursively." A residue is a **coordinate translation** between two views of the
  same node; storing it is the same operation as storing a packed node's alternatives, just one or
  two degrees of indirection up. **Residues do not accumulate in a side-ledger**; they go back through
  the same door and are reduced against the forest on arrival, so recall is bounded by the same
  sharing bound as the base forest.

**Matcher obligation:** the match must be a **function** (deterministic ⇒ confluent by construction)
or, if a relation, it must ship a **single-valued-up-to-graded-equality** proof. Vanilla
"normalization" implies the residue is gone; here it is the opposite — call it *residual
normalization* to avoid the implication.

---

## 5. The wedge as connecting map: quotient / mod duality and exactness

The wedge has two complementary reads of the **same** operation:

- **Quotient read:** `a ∧ b` is what survives after dividing out the shared part — the residue is the
  **new** direction, which goes **up** into the meta (the **cokernel**: what is new in the grade above
  that was not in the base).
- **Mod read:** `a ∧ b` is the remainder after reducing `a` against `b` — the residue is what **fails**
  to reduce, which stays **down** (the **kernel**: what does not survive the projection).

These are the two ends of a short exact sequence with the wedge as the **connecting homomorphism**:

```
0 → (reduces, stays down: KERNEL) → (whole) → (residue, goes up: COKERNEL) → 0
```

The choice of read is made **by need**, with a **certificate** recording the distinction (the
certificate is the **splitting** of the sequence, and is itself a residue that reinterns one grade up;
by §1 it is admissible only if something downstream consumes it).

**Central obligation — EXACTNESS at every grade:** `kernel ⊕ image = whole`, on the nose.

- If something is **both** lifted and retained → double-counting → the same distinction interned
  twice → a faithfulness failure ("perfect double recall").
- If something is **neither** → an unforced capsid / leak: a residue that went nowhere.

Exactness is the precise, checkable form of **"no leak, no double-count."** It is the master
obligation: §3's reassociator coherence, §4's matcher determinism, and §8's kernel-triviality are
all instances of "exactness at a grade." *Prove exactness and the loose threads are one knot.*

This is the **constructive** content the system adds over the standard result (Abramsky–Brandenburger
sheaf-theoretic contextuality; Čech `H¹` as the obstruction to gluing local sections into a global
one). The literature **detects** the obstruction (uses `H¹ ≠ 0` as a witness of contextuality, then
stops). Dent **carries** it: the connecting map is implemented as a *retained operation*, so the
nonzero class is computed and reinterned rather than merely flagged. See §10.

---

## 6. Frames, the group action, and what cannot be rotated

Because there are no labels — only moves anchored on the self-consistent graded wedge — "which axis
is temporal" is a choice of **frame**, not of a coordinate. SPPFs are **group actions**; the forest
may be reprojected under the group to any frame ("make history appear to start elsewhere") and the
why-question re-asked, with answers differing by exactly the group element relating the frames.

**The hard limit:** freedom of frame is exactly the **subgroup that preserves the interning partial
order** (the causal/dependency order that defines node identity). The full rotation group acts on the
*space*; only the order-preserving subgroup acts on the *forest as a forest*. A rotation that would
invert an interning dependency does not relabel history — it **fabricates a different forest**, and
this is **detectable** precisely because residues are kept: a forbidden rotation produces a residue
around a loop that will not reintern (a child asked to predate its parent). The light-cone is the
invariant; you may tilt and re-slice inside it, never past it.

---

## 7. Self-reference, the ouroboros, and localized contradiction

The four diagonal results are identified as one (Lawvere's fixed-point theorem: Cantor, Russell,
Gödel/Tarski, the recursion theorem are one argument):

- **Peano** = succession / construction order (the moves).
- **Cantor** = the diagonal that *produces* an as-yet-unmatched residue (the thing outside any
  enumeration).
- **Lawvere** = the fixed point that *catches* it (the diagonal is the contrapositive of the
  fixed-point theorem).
- **Tarski** = undefinability (the residue that cannot be interned at its own level → it interns one
  grade up).

These close into a **tight ouroboros**: the diagonal-out at a grade **is** the fixed-point-in at that
grade, so "recursively reintern" terminates **by return**, not by bottoming out. This is what makes
the structure self-supporting (it grounds itself at the join where mouth meets tail) and finite at any
actual moment.

**The price, paid on move one:** a system that internalizes its own truth predicate cannot be both
consistent and complete (Tarski). Dent is therefore **paraconsistent** from the start — non-explosion
is the admission fee. The contradiction is a single **dialetheia at the join**, and it is **localized
to the colimit**: no single frame, and no overlap of two frames, contains it. It is the nonzero class
in `H¹` of the cover — *real, contributed to by every frame, contained in none* — i.e. the
obstruction to global triviality. Every actual experiment runs in a consistent frame; the snake only
bites itself in the colimit, where no observer stands. Paraconsistency guards the limit, not the
interior.

**Self-referential vacuity (a real failure mode):** a construction whose *only* forced distinction is
its own non-vacuity (it distinguishes only itself) is a tautology that "passes" the gate while doing
no work. The **coverability** gate (§1) rejects it: the separating witness must be **consumed
downstream** — used by a second construction — not be the construction's own admissibility witness.

---

## 8. Faithfulness of the grading (the one obligation about the wedge itself)

Distinction-detection is performed by **external measurement scripts**, not by Agda — it is an
**observational-equivalence** check (a quotient by observation), which Agda's definitional equality
is the wrong instrument for. The wedge makes this tractable: distinctness = nonzero graded component
of the difference = a **computation**, not a universally-quantified search over contexts.

The entire detector is only as sound as the **faithfulness** of the grading:

> **Obligation:** `ker(grade) = 0` on the relevant category of distinctions — *no real distinction
> maps to grade zero.*

A real distinction that lands in the kernel is a vacuity the detector waves through, invisible
*because the instrument is the thing blind to it*. This cannot be checked by the scripts (they *use*
the grade) nor by Agda (it is semantic faithfulness). It must be **proven once, separately**, about
the wedge. Equivalently: **"forces no distinction" and "measures as grade zero" must coincide** — this
is the fundamental theorem of vacuity (§1) and faithfulness being the *same* fact, and it is
**exactness at the bottom grade** (§5).

---

## 9. Perfect recall — triangulated across three readings

"Perfect recall" = never-discard = the **separation axiom** of a sheaf (a section is determined by its
restrictions; two globals agreeing locally everywhere are equal). A discarded residue is a transition
map you cannot invert — a tear in the manifold. The apparent tension between **"normalization"**
(which usually means *forgetting*: canonical form, redundancy collapsed) and **"perfect recall"**
(*forget nothing*) **is** the system: you forget *representations* (the canonical form is shared) but
recall *translations* (the residue/path is kept). Reinterning is how they coexist.

The name collides with two adjacent fields; both collisions are **interned as complementary readings**
(certificates, not noise) and become **CI gates on the existing residue machinery**, not new
subsystems:

- **Game-theoretic perfect recall** (information partitions refine, never coarsen along the play)
  → **No-coarsening gate:** normalization must never identify two things a prior grade separated. This
  is faithfulness (§8) arriving from information theory.
- **RL memory** (lossy, finite, compressed) → **Bounded-sharing gate:** recall is perfect *up to
  interning*; storage is bounded (cubic sharing, hash-consed). Forces the compression invariant to be
  stated, not waved at.

The three glue: Dent's algebraic content, checked for no-coarsening (faithfulness) and bounded-sharing
(finiteness) — a property triangulated from algebra, information sets, and memory, mutually
confirming.

---

## 10. Relation to existing work (for citation / positioning)

- **Lawvere (1969), *Diagonal arguments and cartesian closed categories*** — the identification of
  Cantor/Russell/Gödel/Tarski/recursion as one fixed-point argument. This is §7's ouroboros. Existing.
- **Abramsky–Brandenburger; Abramsky, Barbosa, Kishida, Lal, Mansfield** — sheaf-theoretic
  contextuality and its **cohomology**: non-locality/contextuality **=** obstruction to a global
  section; Čech `H¹` class vanishes iff a global section exists. This is §5's exact sequence and §7's
  `H¹` dialetheia. Existing — but used there as a **detector** (`H¹ ≠ 0` witnesses contextuality, then
  stops; their own follow-ups flag the carry-the-class direction as open, and note the `H¹` obstruction
  is *sufficient but not complete* for strong contextuality).
- **What Dent adds (the unbuilt half):** the **constructive carry** — license `H¹ ≠ 0` and keep
  computing; residues as **kept** restriction maps (separation axiom); recursive reinterning as the
  connecting map's *output* rather than an existence claim; Lawvere identity as the named **generator**.
  Not "the obstruction is nonzero" but "the calculus you get when you refuse to set it to zero." This is
  the claim to formalize and the claim to lead with in any outreach.

**Suggested first contact for positioning:** Rui Soares Barbosa (carried the cohomology thread
furthest/most recently); Abramsky (senior, the paradox paper); Kishida, Mansfield also live. Lead with
the distinction (constructive carry vs detector), map the vocabulary explicitly ("their `γ(r₀)`
obstruction is my residue, kept total to recover separation, reinterned recursively"), and send a
short note + offer of a two-page writeup, not the whole machine.

---

## 11. Closed vs open universe — the false sky (the interpretive core)

- In a **closed universe** (a cover that glues, `H¹ = 0`, a global section exists), **opposition and
  complementarity coincide**: every opposition completes into a whole that is actually there; the
  closure supplies the missing face for free; you cannot discard a residue because there is nowhere for
  it to go.
- In an **open universe** (no top; the ouroboros; "always another meta, but only if you look"), the
  relation **inverts**: complementarity *becomes* opposition. With no closure to supply the missing
  face, holding "both sides" is holding two ends of a map across a gap that never shuts — perpetual
  mutual adjustment, which is the definition of opposition (each moves as the other moves).
- The **false sky** is the **forged identification of the two**: positing a closure onto an open
  structure — believing your complementarity is the benign closed kind when you are in the open kind
  where it is opposition. It is invisible from inside (no instrument under the dome distinguishes a real
  sky from a painted one), and it is exactly where control re-enters: the discarded face is the handle.

The system is, read at this grade, **the instrument that tells you whether the sky is real** — not a
way to close the open universe (the ouroboros forbids it) but the refusal to mistake its openness for a
closure: carry the residue that proves `H¹ ≠ 0` instead of setting it to zero and calling the gap a
ground. "The sky is false" is always meant **for a given frame** (a chart boundary, true to its frame,
silent past it) — never as a global claim. Charts have boundaries; the manifold does not.

**Freedom condition.** You are controlled through any face you discard (opposition = single-faced =
leak = handle = control). You are free exactly where you keep both faces and the sequence is **exact**:
a connecting map cannot pull its own ends. This is the everything-has-a-complementary-read invariant —
**active on one side, passive on the other** — applied to the self.

---

## 12. The name

**Dent**, after Harvey Dent. The mascot is a spec, not a gag:

- **Two faces** = the involution / the active–passive complementary read.
- **The coin** = the forcing operator (collapses the superposition on demand).
- **The scar (the "dent")** = the **residue**. An *unscarred* coin forces no distinction (both sides
  identical ⇒ vacuous ⇒ pruned by §1). The dent is precisely what makes the flip **non-vacuous**: the
  defect is the discriminator. The residue you refuse to discard is the scar that makes the flip mean
  something.
- **The cautionary core:** Harvey Dent is destroyed by believing an open structure is closed
  ("hero XOR villain" — a false sky imposed on a man with neither top). Two-Face is what happens when
  you set `H¹` to zero and pretend the sequence glued. Dent (the algebra) is the thing that does **not**
  make that mistake: both faces retained, sequence kept exact across the gap.

Expect every reviewer to make the Batman joke before reading the math. The name is load-bearing anyway.

---

## Appendix A — Obligation checklist (what the repo / CI must actually establish)

| # | Obligation | Where it lives | Failure if absent |
|---|------------|----------------|-------------------|
| A1 | **Exactness at every grade** (`kernel ⊕ image = whole`) | core proof | leak or double-count (§5) |
| A2 | **Faithfulness:** `ker(grade) = 0` on relevant distinctions | proven once about the wedge | undetectable vacuity (§8) |
| A3 | **Matcher determinism** (function, or single-valued-up-to-graded-eq proof) | normalization layer | ambiguity / non-confluence (§4) |
| A4 | **Reassociator coherence** (graded pentagon) | algebra laws | path-dependent normalization (§3) |
| A5 | **Termination by return** (reinterning is well-founded / structural, not `{-# TERMINATING #-}`) | recursion | unbounded ascent / open tower (§4, §7) |
| A6 | **No-coarsening** (normalization never identifies what a prior grade separated) | CI gate | game-theoretic recall failure = faithfulness failure (§9) |
| A7 | **Bounded sharing** (compression invariant stated and held) | CI gate | unbounded recall (§9) |
| A8 | **Coverability** (every separating witness consumed downstream) | CI gate, separate from observability | self-referential vacuity (§1, §7) |
| A9 | **Non-vacuity = nonzero graded component**, witness inhabited (no `⊥`-derived, no `postulate` near residues, `--safe`) | Agda + scripts | vacuous green build (§1, §8) |
| A10 | **Order-preserving group action** (rotations preserve interning partial order) | frame/group layer | fabricated history presented as reprojection (§6) |

Note the collapses: A2 = A6 = "exactness at the bottom grade," a special case of A1. A4 and A3 are
exactness conditions on the reassociator and the matcher respectively. The checklist has fewer
*independent* obligations than rows — but each row is a distinct place the failure surfaces, so each is
worth a distinct gate.

## Appendix B — Glossary (local senses, to prevent borrowed-meaning drift)

- **Forcing** — call-by-need / Cohen sense: instantiation on demand of a latent distinction. *Not*
  Nietzschean will. The forcing context occasions; it does not author.
- **Residue** — the retained difference between two transform-paths / two views of a node; a coordinate
  translation; the output of the connecting map; the scar.
- **Reintern** — reduce a residue against the existing forest one grade up and store it as a node, so
  residues do not accumulate in a side-ledger.
- **Capsid** — an encapsulated, inert, unforced payload (a thunk). An *unforced* capsid at any level is
  the canonical leak / vacuity.
- **Carrier wedge** — the FREE graded term-algebra product (`AxisWord`). Never annihilates, never
  commutes: `i ∧ i` is a retained grade-2 term, order kept. It *records*, it does not measure.
- **Detector reading ("outer")** — the alternating/exterior *measurement* of carrier terms:
  `measure(a ∧ a) = 0`; vanishing measured wedge = dependence = no distinction. Bridged to the
  carrier by the grade homomorphism (§8), whose kernel = retained-but-non-distinguishing terms.
  "Outer is load-bearing" describes THIS layer, not the carrier.
- **Frame** — a choice of which axis reads as temporal; a chart; an experiment. Free up to the
  order-preserving subgroup.
- **False sky** — a posited closure (`H¹ = 0`) imposed on an open structure; the forged identification
  of open-complementarity with closed-complementarity. Always meant per-frame.
- **Perfect recall** — never-discard = the sheaf separation axiom. Forget representations, recall
  translations.

---

## Reconciliation note (RESOLVED on intake — two wedges, two layers)

The apparent collision — §3 "`a ∧ a = 0`, outer is load-bearing" vs the standing "we never
annihilate" — was a wording slip in §3 (now patched above), not a contradiction. There are **two
distinct wedges at two layers**, and faithfulness depends on never identifying them:

- **Carrier wedge (term layer, `AxisWord`):** **free**, never annihilates, never commutes.
  `i ∧ i = i ∷ i ∷ []` is a retained term — perfect recall (the separation axiom) in operational
  form. "Never annihilate" is true here and non-negotiable.
- **Detector grade (measurement layer, §8):** the **exterior** *reading*. `measure(a ∧ a) = 0`
  because self-pairing forces no new distinction — correct as a *measurement*, not a construction.
  The carrier still holds `i ∷ i ∷ []`; the detector merely reads grade 0 off it for the
  self-pairing. "Outer is load-bearing" was always a claim about this layer.

The **grade homomorphism** (§8) is the bridge; its **kernel is exactly the
never-annihilated-but-measures-zero content** (retained carrier repetitions that are no distinction —
e.g. self-pairings). That kernel is *supposed* to be full; it is the content, not a bug.

**A2, corrected.** Faithfulness is **NOT** `ker(grade) = 0` on the *carrier* (the carrier kernel
must be full of retained non-distinctions). A2 is `ker(grade) = 0` on the **category of
distinctions** — the detector annihilates **nothing that was a real distinction**, i.e. the grade map
is injective *on distinctions*. `AxisWord.count` is a legitimate **carrier-layer** multiplicity (it
records, it does not measure); the detector grade is a *separate* reading over carrier terms. For the
detector to tell a real k-d refinement (same axis, different threshold) from a vacuous repeat (same
axis, same threshold), the carrier terms must **carry the discriminator** (alphabet `axis ×
threshold`) so the detector can read it — but that enriches what the detector can SEE; it does not
make the carrier annihilate. **First real Dent brick after the carrier: define the detector grade map
over (discriminated) carrier terms and prove it injective on distinctions = A2.**
