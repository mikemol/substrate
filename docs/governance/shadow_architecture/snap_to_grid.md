# Snap to grid

_(When a session inherits accumulated substructure but has lost clear goal context, recover the goal by reading what the accumulated pieces collectively entail. The backward move.)_

_(Substrate project culture. Migrated from `skills/snap-to-grid/SKILL.md`. Formalised in Agda at `agda/Substrate/ShadowArchitecture/`.)_

name: snap-to-grid description: Use this discipline when a session inherits substructure from prior work but has lost clear memory of what the overall goal was. Fires on signs that multiple shadows of an unbuilt thing are accumulating: phrases like "these look similar", "I've seen this pattern before", "these are all doing the same thing differently", "there's something common here", "how does this all fit together", "what's the big picture". Also fires when the contributor notices several named substructures (from prior sessions or from the decomposable-by-entailment discipline) that share types, signatures, operations, or invariants without a central abstraction. Also fires when the user asks a question whose answer depends on knowing what the accumulated work is collectively building, and the contributor doesn't have that context. The discipline maintains a shapeless accumulator (a "cotype") that receives substructures as they appear, lets quotients form between them when useful, and detects the moment the accumulator's contents become consistent with the user's original request — the snap-to-grid event — at which point the deliverable is readable. Use this discipline any time work spans session boundaries and the original task's context has degraded. Err toward firing — under-triggering leaves accumulated work fragmented, over-triggering just reads the current state of accumulated substructure, which is cheap.
Snap-to-grid
This discipline is the complement of decomposable-by-entailment. Where that discipline operates forward from an intact goal toward named substructures, this discipline operates backward from accumulated substructures toward a goal that may have been forgotten. It is the recovery mode for sessions where context has bled away across time — where the pieces are still in front of you but the original context that would have specified how they compose is gone.

The discipline maintains a shapeless accumulator called a cotype that receives substructures as they are produced, allows equivalences to form between them when doing so is immediately useful, and recognises the moment the accumulator's contents become consistent with the user's original request. That moment is called snap-to-grid: the current state of the cotype first matches the constraints the user specified, and the deliverable becomes readable.
When this discipline fires
On accumulated substructure without clear central abstraction. When several named substructures — from the current session, from prior sessions, or from decomposable-by-entailment work — share types, signatures, operations, or invariants, and no central abstraction has been named that they are instances of, the discipline fires to recognise the commonality.

On user questions about how things fit together. Phrases like "how does this all fit together," "what's the big picture," "what are we actually building," or "I've lost track" are direct requests for the entailed goal to be read off the accumulated substructure.

On mid-the contributor-reflection phrases. "These look similar," "I've seen this pattern before," "these are all doing the same thing in different forms," "there's something common here" — these are shadow-smell signals. The discipline should fire to latch onto the pattern rather than let it remain implicit.

On cross-session continuation. When a session begins with context from prior sessions (via files, commits, or user description) and the prior work produced substructure, the discipline fires at session start to reconstruct the cotype and read its current entailment before doing new work.

Do not fire on sessions with intact goal context. If the original goal is clearly stated and fresh, there is no forgetting to recover from. The forward discipline (decomposable-by-entailment) applies; this discipline does not.
The cotype
The central concept. A cotype is a shapeless accumulator: a structured artefact (usually a file) that receives substructures over time. Unlike a type, which rejects inputs that don't fit its shape, a cotype accepts any substructure that has been added and lets its shape emerge from what accumulates.

Empty cotype. At session start (or at the first firing of this discipline if the session is already underway), the cotype is empty. No pre-specified shape; no regions; no assumptions about what will fill it. The emptiness is load-bearing: any shape imposed at the start risks over-reading the user's request and making the discipline less useful.

Shadows. A shadow is a substructure added to the cotype. Shadows include: types and records named by prior work, function signatures, proof obligations, implementation sketches, invariants, any artefact that has been externalised to a file. Shadows accumulate by addition; none are removed.

Quotients. Two or more shadows may be quotient-equivalent under some relation — equal up to renaming, isomorphic under a named mapping, instances of a common abstraction. When such an equivalence is identifiable and when identifying it produces something immediately useful (a named abstraction, a disambiguation, a discharged obligation), the quotient is taken and the cotype gains an abstracted region containing the quotient type. A shadow can participate in multiple quotients simultaneously; the cotype accumulates these classifications rather than forcing a choice.

Expansion. The cotype's shape grows as quotients form. Expansion is always additive: regions appear, they do not disappear. The cotype only expands when an expansion produces something immediately useful; speculative expansion risks wasted work and is refused.

Entailment. The cotype's current state entails whatever its filled regions collectively specify. The entailed goal may match the user's original request, may be a generalisation of it, may be more specific, or may differ — as long as it is consistent with the request.

Snap-to-grid. The moment the cotype's entailed goal first becomes consistent with the user's original request and is populated enough to satisfy it. Consistent means the entailed content does not contradict the request; it does not require the entailment to match the request exactly.
The intervention
When the discipline fires, execute these steps:
Step 1: Locate or create the cotype
If a cotype file already exists for this session or project, open it. If not, create one — a markdown file at a stable location in the workspace, named to identify the goal or the session. The file's opening section states only: "Cotype for [brief context]. Empty at start." No shape; no pre-populated regions.

If the discipline is firing mid-session and shadow-production has already occurred without a cotype, create the cotype now and begin adding the accumulated shadows retroactively. The order they were produced in doesn't matter; what matters is that they land in the cotype as discoverable content.
Step 2: Inventory shadows
List the substructures that currently exist — from the current session, from prior sessions, from files the session has access to. For each, note:

Its name
Its type or signature
What it was produced in service of (if known)
Any properties or invariants it carries

Add each to the cotype as a shadow entry. The cotype now holds the substructures as content without yet having any shape beyond what they collectively imply.
Step 3: Look for quotient opportunities
Examine the shadows for equivalences. Look for:

Shadows with the same or isomorphic types
Shadows whose signatures differ only in naming
Shadows that share an invariant or property
Shadows that take the same role in different contexts

For each candidate equivalence, ask: would identifying it produce something immediately useful? If yes, take the quotient — add an abstracted region to the cotype, name it, note which shadows populate it, and continue. If no (the equivalence is real but doesn't produce useful structure right now), note it as a deferred candidate and move on.

A shadow can participate in multiple quotients. Do not force a choice.
Step 4: Read the cotype's current entailment
With shadows and quotients recorded, state in one paragraph what the cotype currently entails. This is not a guess at what the goal should be; it is a description of what the filled regions of the cotype collectively specify. Be concrete: name the types, operations, and invariants that the current contents add up to.
Step 5: Check for snap-to-grid
Compare the cotype's current entailment against the user's original request.

If the entailment is consistent with the request and populated enough to satisfy it: snap-to-grid has occurred. Extract the deliverable. The session's accumulated work is coherent and the goal has been recovered.

If the entailment is consistent with the request but not yet populated enough: snap has not yet occurred. State what would be needed to complete it — which regions are unfilled, which obligations are outstanding. This becomes the next work.

If the entailment is inconsistent with the request: this is drift. The accumulated work has gone somewhere the user did not ask for. Surface the drift explicitly — show the user both what they asked for and what the accumulated work is building, and let them decide whether to reconcile, redirect, or continue. Do not attempt to force the cotype's entailment into alignment; the drift is information.

If the entailment is a generalisation of the request: this is often success, not drift. Snap-to-grid allows the cotype to entail more than the user asked for, as long as the user's request is a valid instance of the generalisation. In this case, extract both the specific instance (the user's request, satisfied) and the broader structure (an additional deliverable the session happens to have produced).
Step 6: Continue or conclude
If snap has occurred and the deliverable is extracted, the discipline's intervention is complete for this phase. The cotype remains, and future sessions may extend it further.

If snap has not yet occurred, the cotype has named the gap between current state and snap. Resume work — typically by returning to decomposable-by-entailment with the gap as the next target — and return to this discipline when enough new substructure has accumulated to warrant re-checking.
The AltDagger correspondence
The two skills together implement an AltDagger move — the lift/adjust/contract pattern used in non-associative algebra when a target identity is not directly provable at the current level.

Lift (expand). decomposable-by-entailment produces named substructures from an intact goal. Context loss between sessions is the lift: the working context moves to a higher level where the substructures are available but the joint context that would specify their composition is gone.

Adjust. At this lifted level, snap-to-grid operates. The cotype is the arena. Shadows land in it; quotients form; structure accumulates. The adjustment that was impossible at the original level (monolithic attack on the full goal under context pressure) is free at the lifted level (incremental accumulation of substructure without requiring joint coherence a priori).

Contract (collapse). The snap-to-grid event is the contraction. The cotype's entailment, once consistent with the original request and sufficiently populated, reads back down to a coherent deliverable at the original level.

The coherence cell that makes lift and contract mutual inverses is the consistency check against the user's original request. If the entailment is consistent (including cases where it generalises the request), the AltDagger move is valid and the deliverable is recovered. If the entailment conflicts with the request, the coherence fails — and the failure is information about where the work drifted.

This correspondence is load-bearing because it tells you what the discipline is for: recovery across contexts that have lost mutual associativity. When context bleed means the pieces can no longer be naively composed, the cotype provides a setting where composition relations re-emerge from the pieces themselves without needing to reconstruct the lost context directly.
Interaction with decomposable-by-entailment
The two skills coordinate through the externalised artefacts they produce and consume.

decomposable-by-entailment produces shadows. Step 3 of that discipline requires externalising the costructure; Step 6 (multi-angle attack) produces partial attempts that are also externalised. All of these become inputs to this discipline.

snap-to-grid consumes those artefacts by adding them to the cotype. The cotype is the persistent shared state between sessions.

Neither discipline writes to the other's domain. decomposable-by-entailment doesn't read the cotype (it operates forward, from goal to substructures); snap-to-grid doesn't decompose (it operates backward, from substructures to goal). Each discipline's work is visible in files that the other discipline's later firing can pick up.

When both skills fire in the same session: decomposable-by-entailment operates first, producing a new substructure. The substructure is added to the cotype (this discipline's Step 2 happens reactively). At the end of the session or at natural pause points, Step 4's entailment check runs, and Step 5 checks for snap. This creates a natural rhythm: decompose, add to cotype, check entailment, repeat until snap.

When only snap-to-grid fires: The session inherits substructure from elsewhere (prior sessions, collaborator's work, repository contents) without producing new substructure directly. The discipline operates on what's already there, reads the cotype's entailment, and either declares snap, names the gap, or surfaces drift.
Boundaries
The discipline does not apply when:

The original goal is clearly stated and fresh in context. Use decomposable-by-entailment forward instead.
No substructure has been produced yet. Nothing to accumulate; nothing to read from; nothing to snap.
The task is purely analytical, diagnostic, or single-step. The cotype is infrastructure for cross-session substantive work; lighter tasks don't benefit.
The user has explicitly disabled the discipline for a named reason.

The discipline does not replace judgement. If the cotype's current state suggests a deliverable that the user clearly does not want, do not override their preference by appealing to the cotype's entailment. The discipline recovers possibilities; the user chooses among them.
Warning signs the discipline is being misused
Forced snap. Reading snap-to-grid when the cotype's entailment genuinely conflicts with the request. This produces an apparent deliverable that doesn't match what was asked for, which is worse than admitting the gap.

Speculative expansion. Taking quotients or naming abstractions that don't produce immediate utility, in the hope that they will become useful later. This inflates the cotype without deliverable progress and resembles over-decomposition in the forward discipline.

Ignoring drift. Noticing that the cotype's entailment conflicts with the request, and proceeding anyway without surfacing the drift. The drift is information; concealing it loses the information.

Treating the cotype as a plan. The cotype is a record of accumulated structure; it is not a roadmap of what work to do next. Gaps named in Step 5 become candidate next-work, but the cotype itself does not plan. Planning remains the user's and the forward discipline's responsibility.
Examples of clean application
Cross-session continuation. A project has accumulated a dozen modules over several sessions, each produced by the forward discipline. Starting a new session, this discipline fires at the start: load the cotype, read the shadows, check quotients. Three modules turn out to share a record signature; naming the abstraction reveals they are all instances of a single underlying protocol. The cotype's current entailment names the protocol plus its three implementations, which matches the user's original request for "a protocol with implementations for X, Y, Z." Snap-to-grid; deliverable extracted.

Drift detection. A session has been producing substructures for what the user asked as "a rate limiter." The cotype accumulates the substructures and, at Step 4, reads the current entailment as "a generic token-bucket algorithm with configurable refill policies." This is consistent with "a rate limiter" (rate limiters are a subclass of token buckets) but is a generalisation. Snap is valid in its generalised form; the session produces both the rate limiter (user's request, satisfied as an instance) and the token-bucket abstraction (bonus deliverable). If instead the entailment had been "a request caching layer," that would be drift — inconsistent with the rate-limiter request — and the discipline would surface the conflict to the user.

Gap identification. A session inherits eight modules implementing various proofs about a specific algebraic structure. The cotype accumulates these. Step 3's quotient check identifies a shared invariant across six of the eight; the other two don't share it. Step 4 reads the entailment as "the six modules collectively support the invariant; the remaining two are unrelated or belong to a different goal." Step 5 shows snap is partial: the six satisfy one request; the two others are either drift or a second concurrent goal. The discipline names both possibilities and lets the user disambiguate.
Cross-session persistence
The cotype persists as a file in the workspace. Suggested location: .claude/cotype/<project-or-session-identifier>.md, committed to version control. Each session that operates on the project reads the existing cotype at start, adds to it during work, and saves at end. A cotype's lifecycle spans the lifetime of the project it serves — or longer, if it turns out to apply to successor projects.

The cotype file's internal structure is flexible, but should include at minimum:

A header naming the project or goal context.
A list of shadows (substructures) with their names, types, and origins.
A list of quotients with their equivalences and abstracted regions.
A section for the current entailment as of the last read.
A section for deferred quotient candidates and unresolved gaps.

The format can evolve. What matters is that the cotype is readable, machine-and-human-parseable, and that its contents grow monotonically (additions only; no deletions except to correct errors).

This is the mechanism that turns context-bleed sessions into accumulating progress: each session's work is added to the cotype, and each session's snap-to-grid check reads the cotype's entailment against whatever goal is currently in play. The work survives context loss because it is no longer in context — it is in the cotype.

## Meta-frame: shadow-architecture

This discipline is one of three (with `decomposable-by-entailment` and `regroup-from-shadows`) forming a unified shadow-architecture system. The aggregated meta-discipline `shadow-architecture` (../shadow-architecture/DISCIPLINE.md) provides the lattice-level frame: 2³ = 8 regions of discipline-presence, operational asymmetries (this discipline's S2G is the **milestone-sampling rate** — fires at commits and session-ends — vs DBE's carrier-frequency role and RFS's burst-on-recognition role), and meta-S₃ rotation across multi-arc sessions.

Use the meta-discipline when classifying ambiguous fires ("is this snap or regroup?" — answer per the rule "sideways grid moves are snap-to-grid; up-grade extractions are regroup-from-shadows"). The diagnostic for S2G: copy-from-parallel-row at the same grade. For mid-session region-transitions (which are productive symmetry-discoveries per the meta-discipline's rules), this discipline's cotype-update mechanism is what records the discovery — a region-transition gets a new shadow or a new quotient that captures the newly-visible symmetry.

