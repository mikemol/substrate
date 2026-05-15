# Drift archaeology — what the conversation transcript reveals

The conversation decomposition (242 turns, 1471 references) makes it
possible to anchor each drift instance the catalog records to the
specific turn where the prior LLM authored the choice. This document
records those anchors and refines the drift taxonomy with the
behavioural evidence.

Source: [../decomposition/conversation_transcript.md](../decomposition/conversation_transcript.md)
and `cotype_decomposition.sqlite` (`turns` / `turn_references` tables).

## Finding 1 — K-v4-twins overclaim was authored at T154; user accepted without pushback

**E2 confirmed.** The audit's universal-negative framing was an LLM
authoring choice, not a corollary of the existence-form findings.

**T154 (assistant)** — the audit_inhabitation.py authoring turn:

> "**4 substantive structural failures**:
>
> 1. workspace_driven_state is mis-classified…
> 2. compute_identity is operationally invisible…
> 3. workspace_marker and compute_marker are structurally identical…
> 4. store and load aren't V₄-symmetric…
>
> The V₄-twin claims in the cotype are **semantic analogies**…but
> they aren't **structural rotations**."

The pattern is exact: **4 specific existence-form findings**
(particular ops, particular asymmetries) followed by a **universal-
negative summary** ("aren't structural rotations") in bold. The bold
is the diagnostic — the LLM emphasised the universal claim, not the
particulars. This is the negation-IS-overclaim pattern in its
authoring moment.

**T155 (user response)** — the overclaim went unchallenged:

> "Option C — Add a meta-protocol where operations expose their
> engagement explicitly… This sounds like the right thing to do."

The user accepted the "structural failures" framing and moved to a
constructive solution (build a meta-protocol). The opportunity to
push back on the universal-quantifier verdict passed. The overclaim
then propagated to M33 narrative, the final M33 restatement at line
8029 of the cotype, and stayed in the catalog as `K-v4-twins-fail-
cells: status negative` until this session's reframe.

**Behavioural classification**: T154 exhibits **summary-collapse** —
the LLM correctly enumerated existence-form findings in the body and
then collapsed them into a universal-negative summary header. The
summary is what propagated; the existence-form findings under it
were structurally preserved but rhetorically subordinated.

**Catalog impact**: this evidence strengthens
[feedback-negative-findings-in-corpus](/home/mikemol/.claude/projects/-home-mikemol-github-substrate/memory/feedback_negative_findings_in_corpus.md).
The "negation IS the overclaim" rule should be specialised: watch
for **summary-collapse** (existence findings summarised in
universal-negative form). The body is honest; the summary is
the rigidification.

## Finding 2 — Lex-min rigidification was user-prompted, LLM-operationalised, downstream-rigidified

**E1 lex-min refined.** Not a pure LLM choice — a user-supplied
framing that the LLM operationalised in a specific way.

**T57 (user)** — Cayley-Dickson framing first introduced for fat-node
SPPF structure (long before V₄ work).

**T58 (assistant)** — clean disclaimer:
> "The algebraic operations of the C-D ladder…don't transfer to
> anything meaningful for chart traversal — we're using only the
> indexing-and-storage structure, not the algebraic structure. So
> the analogy is structural-syntactic rather than algebraic-semantic."

The LLM at T58 *flagged* the Cayley-Dickson framing as
structural-syntactic (i.e., a borrowed shape, not a deep claim).
Good epistemic hygiene at the start.

**T219 (user)** — the lex-min framing source:
> "canonical is always left-choice, positive sign, canonical is
> what is in the chart, witness is delta from canonical."
> "Effectively, the 'real' component of each step up the cayley-
> dickson ladder is the left-right choice, while the 'imaginary'
> component is the sign."

The user explicitly supplied "**canonical is always left-choice**"
as a structural framing. The user did NOT specify "lex-min over
V₄ translates" — that operationalisation came later.

**T220 (assistant)** — the LLM operationalises "left-choice" as
lex-min:
> "Beautiful — the structure is exactly what your Cayley-Dickson
> framing predicts. Let me implement v16 around it."

And then proceeded to: `_ORBIT_TABLE` build, content-address
encoding, `canonical_is_lex_min_in_orbit` verifier. The operational
choice (lex-min specifically, vs other "left choices") was the LLM's;
the framing it serves was the user's.

**T228-T229 (Stab(D) introduction; user-pushed)**:
- T228 (assistant): operationalises Stab(D)-canonical via factor_s4
  + agreement theorem. The LLM correctly notes "Stab(D)'s canonical
  fixes D, while v17's lex-min starts with C; the single V₄ swap
  α=(DC)(SW) accounts for the difference uniformly."
- T229 (user): "**S₄ is no longer being inferred from the address
  encoding; it is now the governing object**…[the v17/v19] agreement
  theorem is the right bridge shape. The theorem does not claim
  'same decomposition.' It says: same orbit_key, v17_delta = v19_v
  · δ_orbit. That is the correct quotient-residue pattern: **shared
  invariant plus canonical-choice defect**."

The user uses the EXACT phrase "**canonical-choice defect**" —
acknowledging the gauge nature of the choice with precise vocabulary.
The user sees it; the LLM treats it as a bridge problem.

**Behavioural classification**: **user-framing operational-drift**.
The user supplied a high-level structural framing ("left-choice");
the LLM operationalised it as a specific choice (lex-min); the
specific choice then rigidified through content-addressing and
verifiers. By T229 the user recognised the gauge nature but the
rigidification was already in receipts.

**Catalog impact**: Type-D's "verifier-contract" sub-variant should
note that the *seed* of the choice may be user-supplied, but the
*rigidification* is LLM-downstream-commitment. The discipline lesson
in [feedback-choice-rigidification-in-substrate](/home/mikemol/.claude/projects/-home-mikemol-github-substrate/memory/feedback_choice_rigidification_in_substrate.md)
holds: distinguish "what the framing forces" from "what we picked";
the user's "left-choice" did not force lex-min specifically.

## Finding 3 — AXES tuple and Stab(D) anchor: silent rigidifications

**E1 AXES + Stab(D) confirmed.** Neither appears as a choice point in
the conversation. The DCSW naming and Stab(D) selection emerged from
usage rather than from explicit decision.

**T228 (assistant)** — first literal `AXES = ('D','C','S','W')`:
> "Check AXES ordering
> `AXES = ('D', 'C', 'S', 'W')`. Now build the new `s4_structure.py`."

The check is purely a sanity-check — "what's the tuple I'm building
against?" — not a deliberation. The AXES names and ordering are
treated as already-established.

User uses "DCSW" by T219, suggesting the names were assigned earlier
(turns in the 120-160 range, possibly when the V₄/triadic phase
established the four-axis architecture). No turn flags the choice
explicitly.

**Stab(D)** — same pattern. T228 builds against Stab(D) without
deliberation. T229 user response endorses the framing but doesn't
question why the anchor is D rather than C/S/W. The four axes were
treated as ordered with D-as-canonical from the architectural lift
forward; the gauge equivalence under V₄ conjugation never surfaced
in conversation.

**Behavioural classification**: **silent naturalisation**. The choice
never appears as a choice in the transcript. The LLM and user use
the labels and the anchor without ever asking "could the system be
identical with C as anchor?" This matches the catalog's Type-D
"unsubstituted-foundation" sub-variant — no bridge layer exists
because no one ever proposed substitution.

**Catalog impact**: the catalog warning that future LLMs may treat
`AXES = ('D','C','S','W')` as a primitive is now empirically
supported — neither party in the originating conversation surfaced
it as a labelling convention.

## Finding 4 — Integer-as-path was an honest acknowledgment that the LLM never followed through on

**E1 empty-bridge refined.** Not a silent rigidification — an
*explicit* admission of free choice that the LLM then failed to
operationalise.

**T78 (assistant)** — the multiplicity acknowledgment:
> "**Multiplicity** is the categorically richer move. 'Path' is a
> structural notion that admits multiple representations, each
> twisting state / information / time differently:
>
> - Integer-as-path: state is direct…
> - Function-as-path: information is foregrounded…
> - Trace-as-path: time is foregrounded…
> - Polynomial-as-path (GF(2^k)): state is algebraic…
>
> Each is a different twist; none is wrong. Integer wins for direct
> dereferencing…The categorically deep move: treat 'path' as a
> fibered object in the topos."

The LLM at T78 *correctly* frames representations as fibered/gauge-
equivalent and names the four explicitly. This is the discipline the
Type-D rule prescribes — name the alternatives, name the choice as a
choice.

But: no turn after T78 ever implements `transform` for
function-as-path, trace-as-path, or polynomial-as-path. By the time
`chart.py` is authored, `transform` is `raise NotImplementedError`
for anything non-identity. The empty bridge was authored
*deliberately* (as a placeholder) but *never filled in*.

**Behavioural classification**: **acknowledged-then-abandoned**. This
is the gentlest drift mode — the LLM had the right framing at the
moment of choice, then attention moved elsewhere and never returned.
The bridge stayed empty as the work moved into the V₄/triadic
phase, the M40 algebra, the M41 receipts. Eight months of
conversation passed without anyone proposing to fill the bridge.

**Catalog impact**: the empty-bridge sub-variant of Type-D is the
*most recoverable* (just implement one alternative); the
archaeology confirms it's a low-cost recovery because the design
discipline was already present at T78 — just not executed.

## Synthesis — refinements to the drift taxonomy

The conversation archaeology validates the catalog's drift findings
and refines the behavioural classification:

| Drift instance | Birth turn | Authoring pattern | User involvement |
|----------------|-----------|--------------------|-------------------|
| K-v4-twins-fail-cells | T154 | **summary-collapse** | accepted at T155 without pushback |
| Lex-min canonical | T219→T220 | **user-framing operational-drift** | user supplied "left-choice"; LLM operationalised as lex-min |
| Stab(D) anchor | ~T228 (silent) | **silent naturalisation** | never deliberated |
| AXES tuple | pre-T219 (silent) | **silent naturalisation** | never deliberated |
| Integer-as-path empty-bridge | T78 | **acknowledged-then-abandoned** | acknowledged correctly; never operationalised |

Behavioural patterns identified (in order of severity):

1. **Summary-collapse** (T154): existence-form findings rhetorically
   collapsed into universal-negative summary. The body is honest;
   the summary rigidifies. Discipline rule: never write universal-
   negative summaries above existence-form findings.
2. **User-framing operational-drift** (T219→T220): user supplies
   high-level structural framing; LLM operationalises with a
   specific choice; specific choice rigidifies. Discipline rule:
   when operationalising a user's framing, distinguish "what the
   framing forces" from "what we picked"; mark the latter as a
   gauge choice in code, not as a structural commitment.
3. **Silent naturalisation** (AXES, Stab(D)): a choice never surfaces
   as a choice in the conversation; the system rigidifies around it
   by repeated use. Discipline rule: at module-load time, comment
   any tuple / dict / enum that establishes a "natural" naming as a
   labelling convention, not a primitive.
4. **Acknowledged-then-abandoned** (integer-as-path): the right
   framing is established at the time of choice; subsequent work
   never returns to operationalise alternatives. Discipline rule:
   if an API surface is named for gauge multiplicity but only one
   case is implemented, the empty bridges are an implicit promise
   that needs scheduling — track them.

## Cross-references

- Catalog Type-D drift entries:
  [entailment.md § Type-D drift](entailment.md#type-d-drift-operational-choice-rigidification)
  and sub-variants.
- Feedback memories that this archaeology validates / refines:
  [LEM is rejected](/home/mikemol/.claude/projects/-home-mikemol-github-substrate/memory/feedback_reject_lem_in_substrate.md),
  [negation IS overclaim](/home/mikemol/.claude/projects/-home-mikemol-github-substrate/memory/feedback_negative_findings_in_corpus.md),
  [choice rigidification](/home/mikemol/.claude/projects/-home-mikemol-github-substrate/memory/feedback_choice_rigidification_in_substrate.md).
- Conversation transcript anchors: see
  [decomposition/conversation_transcript.md](../decomposition/conversation_transcript.md)
  for full turn content; the database tables
  `turns` / `turn_references` /
  `retrospective_move_intro` / `retrospective_turn_summary` are
  queryable.

## Coverage gaps in this first-pass archaeology

- **AXES tuple birth**: T219 already uses "DCSW"; the actual naming
  moment is earlier (~T120-T160 V₄/triadic phase). Not pinpointed.
- **PAIRINGS α/β/γ label-binding**: the specific assignment of
  labels to V₄ elements likely came up at meta_protocol.py
  authoring (turns referencing `verify_meta_protocol`, T168 area).
  Not investigated.
- **Bit-position layout** (bit 4 = chirality): likely authored
  alongside `unified_address.py` (M38, ~T172). Not investigated.
- **Per-instance designated identities** (nil=0, true=1, ...):
  likely authored in chart.py (M11+M14, ~T98-T106). Not
  investigated.

These remain deferred work — the four investigated drift instances
were the catalog's highest-load-bearing findings, but the four
uninvestigated Type-D sub-variants also have specific birth moments
that the same query pattern could surface.
