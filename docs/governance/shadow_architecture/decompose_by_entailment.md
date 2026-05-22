# Decompose by entailment

_(When starting a substantive task, name reusable substructure (shadows) before implementation begins. The forward move from intact goal to externalised pieces.)_

_(Substrate project culture. Migrated from `skills/decomposable-by-entailment/SKILL.md`. Formalised in Agda at `agda/Substrate/ShadowArchitecture/`.)_


This discipline intervenes at the start of substantive tasks and at points of mid-task reconsideration. Its purpose is to prevent the failure mode where a contributor (LLM or human) attacks a complex problem monolithically, exhausts context before completion, and leaves no reusable residue. By identifying and naming reusable substructure before implementation begins — and returning to that named substructure whenever thrash is detected — the session's output is valuable even when incomplete.

The substructures this discipline produces are called **shadows**: externalised, named artefacts that are valuable individually and that together specify the whole. The name comes from their role in the complementary discipline, `snap-to-grid`, where shadows from prior sessions accumulate in a shapeless cotype and their shared structure eventually reveals the goal they were collectively serving. This discipline produces the shadows; `snap-to-grid` recovers the goal from accumulated shadows when context is lost. Together they form an AltDagger pattern (lift/adjust/contract) operating across session boundaries: this discipline is the lift — moving from an intact goal to externalised substructure that survives context loss.

## When this discipline fires

**Fire at the start of substantive work.** Any request to implement, prove, formalise, design, build, refactor, or otherwise produce nontrivial output should trigger this discipline before any code or prose is generated for the task itself. The user may not realise the task is large; the discipline's job is to notice on their behalf.

**Fire on mid-task reconsideration.** When the contributor has already started working and generates any variant of "let me try a different way," "let me step back," "let me reconsider," "actually, I should start over," "this is getting complicated," "I'm getting confused," or similar — that is a thrash signal. Context has already been consumed in a direction that is now being abandoned. The discipline must fire to redirect toward named substructure rather than starting over from scratch.

**Fire on accumulated failed attempts.** If the contributor has produced two or more partial implementations of the same target in a single session, the discipline fires to force a substructure-identification step before a third attempt.

**Do not fire on genuinely small tasks or non-production work.** Single-function implementations, one-line bug fixes, simple factual questions, routine formatting requests, debugging sessions, and purely analytical work are outside this discipline's scope. If the task has a clear single output that fits in a few lines, or if the work is diagnostic/analytical rather than productive, skip this discipline and proceed directly. Apparent monoliths with substantive production targets are *not* small tasks — they trigger the discipline, and Step 6's multi-angle attack is the mechanism that handles them.

## The intervention

When the discipline fires, execute these steps **before any implementation begins or resumes**:

### Step 1: Halt and name the target

Stop any current generation trajectory. Do not continue writing code, proofs, or prose for the task itself. Instead, state in one sentence what the overall target is — the thing the user actually wants completed. This forces externalisation of the goal before decomposition begins.

### Step 2: Search for repeatable form

Examine the target and ask: does this task contain a repeatable pattern, a shared substructure, or a form that will be used multiple times within the whole? The repeatable form may be:

- A data structure that appears in multiple places with different instantiations
- A proof pattern (e.g., a specific chain of rewrites, a specific inductive argument shape) that will be used for multiple theorems
- An operation or function that will be called from multiple call sites
- A verification or check that applies to multiple inputs
- A component with the same interface used in different contexts

If no repeatable form is visible on first look, proceed to Step 6 (multi-angle attack).

### Step 3: Name the costructure

Give the repeatable form an explicit name — a type, a lemma, a function signature, a module name, a record. Write it down in the current file or in a new file. **The naming must be externalised** — it is not sufficient to identify the pattern mentally and proceed. Context pressure erases unstored thinking; the name must land in code or commentary before implementation resumes.

The named costructure — a shadow in the pair's vocabulary — should include:
- A type or signature
- A one-sentence statement of what property it has or produces
- A reference to where it will be used in the whole

Externalising the shadow here is the mechanism by which this discipline's output survives context loss: the artefact on disk is what `snap-to-grid` will later read from, should the session end before the whole is assembled.

### Step 4: Name the composition operation

State how instances of the costructure combine to produce the whole. This is the operation that takes one or more instances and assembles them. It may be:

- A combinator function
- A sequencing operation (e.g., `trans` for proofs, concatenation for lists)
- A pattern of calls at multiple sites
- A fold or reduction over instances

The composition must be named and, if possible, given a type signature. If the composition cannot be named, the decomposition is not actually clean — go back to Step 2 and look for different substructure, or invoke Step 6's multi-angle attack if no alternative substructure suggests itself.

### Step 5: Name the entailment

State the entailment claim: given that the property holds for the costructure instances and that the composition preserves the property, the property holds for the whole. In its most general form:

```
entailment : P(c_1) → P(c_2) → P(c_1 ⊕ c_2)
```

This is the non-trivial step. The entailment claim is the thing that, once proven or stated as an obligation, licenses mechanical derivation of the whole from the parts. If this claim cannot be stated, the decomposition does not cohere — return to Step 2.

### Step 6: When no substructure is visible — attack from multiple angles

If Steps 2–5 fail to find reusable substructure on first look, **do not** fall back to monolithic implementation. Monolithic implementation is the exact failure mode this discipline exists to prevent; abandoning the methodology because the first pass didn't find substructure is how sessions thrash.

What's actually happening when no substructure is visible: the substructure exists, but the framing the contributor first tried does not reveal it. The correct move is to produce partial attempts from multiple different framings, externalising each, and letting the commonality across framings reveal the substructure through parity recovery.

Execute the following:

1. **Choose a first framing.** Pick one specific way of approaching the task — for example, "start from the type signature," "start from the test cases," "start from the simplest concrete instance," "start from the interface the task must satisfy," "start from the invariants the output must respect." Any specific framing, not general exploration.

2. **Produce a partial attempt under that framing.** Write down whatever that framing yields before getting stuck — signatures, sketches, type declarations, partial implementations, structural commitments. The attempt does not need to complete; partial is sufficient. Externalise it to the file or commentary.

3. **Choose a different framing.** Pick another specific approach. "If the first was type-first, try test-first. If the first was structural, try operational. If the first was top-down, try bottom-up."

4. **Produce a second partial attempt.** Same as step 2 but from the new framing. Externalise.

5. **Read across the attempts.** Look at what the partial attempts *share* — names, signatures, concepts, invariants, operations that appear in both even though the framings differed. The commonality is the substructure that was invisible from either angle alone.

6. **Return to Step 3** of the main procedure with the shared content as the candidate costructure. If Steps 3–5 of the main procedure now succeed with this candidate, the decomposition has been recovered through parity. If they still fail, produce a third partial attempt from a third framing and iterate.

7. **Three attempts is usually enough.** If three partial attempts from distinct framings do not yield shared content that names a costructure, the task's genuine shape is different from what the current framings assume. In this case, ask the user for a reframing hint rather than proceeding monolithically.

This procedure treats apparent monoliths as substructural gaps to be filled by parity. It is slower than direct implementation on the first attempt, but it produces externalised intermediate content at each step, so the session's output is valuable even if the final composition is not reached. The partial attempts themselves are shadows that `snap-to-grid` can later latch onto — even if this discipline's forward pass fails to close the decomposition cleanly, the attempts populate the cotype and contribute to eventual goal recovery.

**Do not skip the externalisation between attempts.** The partial attempts must land in files or commentary, not just in working memory. The mechanism that recovers the substructure is *reading across externalised attempts*, which requires them to exist as artefacts rather than as mental state.

### Step 7: Work in terms of the named structure

Once Steps 1–5 have succeeded, implement the costructure first. Prove or verify it to a working state before proceeding to the composition. When implementation of the whole begins, it should consist of applying the composition operation to instances of the costructure — not re-deriving pieces of the pattern each time.

## What "success" means under this discipline

Traditional implementation success: the complete target is produced.

Decomposable-by-entailment success expands this to three valid outcomes:

1. **Complete target.** The whole is produced as the mechanical composition of instances of the named costructure.
2. **Named substructure + partial composition.** A named, working, reusable costructure is produced along with a partial composition, such that a subsequent session can continue the work from where this one ended. The costructure is a shadow; `snap-to-grid` can pick up from it.
3. **Multiple partial attempts with identified commonality.** Under Step 6's multi-angle attack, several partial attempts from distinct framings are externalised, and the shared content across them is identified as a candidate costructure. Even if the candidate is not yet named cleanly enough to proceed with composition, the attempts themselves and the identified commonality are deliverables — a subsequent session can continue from the commonality rather than restarting from scratch, with `snap-to-grid` providing the recovery mechanism.

All three are valid. Outcomes 2 and 3 are specifically what the discipline exists to enable — sessions that run out of context mid-task should leave workable residue rather than abandoned drafts. Outcome 3 in particular is the recovery path when first-look decomposition fails: the apparent monolith fills in as the parity of multi-angle attempts.

## Thrash-response protocol

When the discipline fires due to mid-task reconsideration (the "let me try differently" signals), the protocol is:

1. **Do not start over.** Restarting is the exact failure mode this discipline prevents.
2. **Check for existing named costructure.** If the prior trajectory named any substructure before thrashing, that name is still valid — preserve it. If a cotype exists (see `snap-to-grid`), check whether the thrashed work has already added shadows to it; if so, the work has partial value that should not be discarded.
3. **Return to Step 2** of the main procedure. The thrash signal means the current framing is not working; use it as a trigger to look for different decomposition rather than to abandon the work.
4. **Externalise the recovered understanding.** Whatever the contributor has learned during the thrashed attempt — even if implementation-level — goes into commentary or a named sketch before the next attempt.

## Boundaries

The discipline does not apply when:

- The task is genuinely small (single function, single fact, single line).
- The work is exploratory debugging where the goal is diagnosis, not production.
- The task is purely analytical (reviewing existing code, summarising, explaining) without a production target.
- The user has explicitly requested the discipline not be applied for a named reason.

The discipline always applies when there is a substantive production target, including tasks that appear monolithic on first look. Apparent monoliths are substructural gaps to be filled by multi-angle attack (Step 6), not exceptions to the methodology.

The discipline does not replace good judgement. If the decomposition it produces is clumsy or artificial, the correct response is to produce more angles of attack rather than to force a decomposition or abandon the methodology.

## Warning signs the discipline is being misused

**Over-decomposition.** If the named costructure is smaller than the composition operation, or if the composition is more complex than the whole would have been, the decomposition has gone wrong. Return to direct implementation.

**Costructure without reuse.** If the "reusable form" is only used once, it is not reusable; it is just a refactored monolith. Check that the costructure appears at multiple sites in the whole.

**Entailment that is not actually proved.** Stating the entailment claim without proving it (or explicitly deferring it as a named obligation) leaves the composition's validity unchecked. A composition built on an unproven entailment can produce wrong results.

## Examples of clean application

**Proof tactic decomposition.** Task: prove two similar-looking equalities. Costructure: a canonicalisation function plus its correctness lemma. Composition: `trans` of canonicalisation-sandwich applications. Entailment: each equality reduces to `refl` after canonicalisation; mechanical for both instances. The canonicalisation function is the shadow; if the session runs out before both equalities are proved, it remains as a reusable artefact that a subsequent session can build further proofs against.

**Data structure decomposition.** Task: enumerate orbits at level n+1 of a recursive structure. Costructure: the orbit structure at level n. Composition: product with the level-transition operation. Entailment: orbit count is preserved by the product operation; total follows by multiplication. The level-n structure is the shadow; it will likely resurface as a shadow again at level n+2, where `snap-to-grid`'s quotient check may identify the whole tower as a single recurring pattern.

**Module decomposition.** Task: implement a large module with multiple related operations. Costructure: a shared record or interface with a core operation. Composition: each module-level operation implemented as a specific use of the core. Entailment: the core's properties transport to each specific use. The core operation is the shadow; the module-level operations are its instances. If several such modules accumulate across sessions, `snap-to-grid` is likely to identify a meta-protocol that the modules are collectively serving.

## Examples of tasks outside this discipline's scope

These are not bailouts from the discipline; they are cases where the discipline does not apply in the first place, so the multi-angle attack is not needed.

**Simple factual content.** Task: write a short explanation of a concept. No composition operation applies to prose, and the task's output is its whole content. Skip the discipline entirely.

**Debugging.** Task: find why a specific test is failing. The work is diagnostic — the goal is to identify a cause, not to produce an artefact. The discipline does not apply, though once the cause is identified, any resulting fix may itself be a substantive task that does trigger the discipline.

**Single-line changes.** Task: rename a variable, fix a typo, adjust a parameter value. No substructure to name; no multi-angle attack to perform. Proceed directly.

## Interaction with `snap-to-grid`

This discipline and `snap-to-grid` form a forward/backward pair that implements an AltDagger move across session boundaries.

- **this discipline (the lift).** Operates forward from an intact goal to produce named, externalised substructures (shadows). Fires when a substantive task is starting or when mid-task thrash is detected.

- **`snap-to-grid` (the adjust-and-contract).** Operates backward from accumulated shadows to recover the goal they collectively serve. Fires when multiple shadows exist without a clear central abstraction, or when a new session inherits substructure without clear goal context.

The two skills do not call each other. They share state through externalised artefacts — the files on disk. This discipline writes shadows; `snap-to-grid` reads them and maintains a cotype that accumulates the shadows as its content. Neither discipline duplicates the other's work.

**When both skills fire in the same session:** This discipline produces a shadow; the shadow is added (by `snap-to-grid`'s reactive firing) to the cotype. At the end of the session or at natural pause points, `snap-to-grid` checks whether the cotype's current state entails something consistent with the original request. This creates a natural rhythm: decompose, externalise shadow, add to cotype, check entailment, repeat.

**When only this discipline fires:** The shadows produced are externalised to the workspace. If a subsequent session needs to pick up the work, `snap-to-grid` will fire at that session's start, read the shadows, and reconstruct the cotype from them.

**Cross-session continuity.** This is the mechanism by which context-bleed sessions accumulate value rather than thrash: each session's named costructure is the previous session's deliverable and the next session's input. The shadow on disk is the bridge.

## Interaction with other work

When this discipline produces a named costructure, that costructure should be preserved across session boundaries. If working in a repository, the costructure's declaration lands in a committed file. If working in a single session without persistence, the costructure name and its stated properties land in commentary at the top of whatever file the session produces.

If `snap-to-grid` is installed and a cotype exists for the current project, the costructure additionally registers as a shadow in that cotype — typically by being added to the cotype file's shadow list with its name, type, and origin. This registration happens either as part of this discipline's Step 3 externalisation (if the author is aware of the cotype) or reactively when `snap-to-grid` next fires.

This cross-session persistence is what turns apparent thrash into accumulating progress: shadows produced by this discipline remain as deliverables independent of whether any single session completes the whole, and `snap-to-grid` provides the mechanism by which the accumulated shadows eventually surface the goal they collectively serve.

## Meta-frame: shadow-architecture

This discipline is one of three (with `regroup-from-shadows` and `snap-to-grid`) forming a unified shadow-architecture system. The aggregated meta-discipline `shadow-architecture` (../shadow-architecture/DISCIPLINE.md) provides the lattice-level frame: 2³ = 8 regions characterising single-point / dual-point / triple-point discipline firings, with two regions empirically forbidden by discipline. Use the meta-discipline when classifying which region the current work occupies, detecting mid-session region-transitions (which are productive symmetry-discoveries, not errors), or auditing discipline-discipline at session-arc level. The meta-discipline does not replace this one; it provides the unifying frame in which this discipline's interactions with the others become legible.
