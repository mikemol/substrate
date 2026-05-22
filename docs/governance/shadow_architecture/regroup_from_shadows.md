# Regroup from shadows

_(When refactoring existing working artefacts, extract reusable substructures (shadows) and recompose from them. The sideways move.)_

_(Substrate project culture. Migrated from `skills/regroup-from-shadows/SKILL.md`. Formalised in Agda at `agda/Substrate/ShadowArchitecture/`.)_


This discipline takes an existing working artefact — code that runs, a proof that typechecks, a module that behaves correctly, a document that covers its material — and extracts its reusable substructures as named shadows, abstracts them where possible, and recomposes the artefact using the abstractions. The recomposition preserves behaviour while making the artefact's internal structure explicit and available to other work.

The discipline is the third member of a trio alongside `decomposable-by-entailment` (the forward move: intact goal → shadows) and `snap-to-grid` (the backward move: accumulated shadows → goal). `regroup-from-shadows` is the sideways move: existing artefact → shadows plus recomposition. Together the three cover all the directions substantive work can arrive in and depart from.

## When this discipline fires

**Fire on explicit refactoring requests.** User phrasings like "refactor this," "clean this up," "this works but it's ugly," "make this more maintainable," "extract the abstraction," "what's the underlying pattern here" are direct requests for this discipline.

**Fire on "we have multiple similar X" observations.** When the user identifies duplication across existing artefacts — "we have three similar modules," "these functions all do the same thing differently" — the discipline fires to extract the common shadow.

**Fire automatically when blocking duplication is detected.** If, during work on a new task, the contributor is about to write code that duplicates logic already present in the codebase, the discipline fires to extract the existing logic into a shadow before the duplication is created. This is the only automatic-firing condition; the discipline does not fire on incidental duplication the user hasn't asked about.

**Fire when the cotype suggests an existing-code opportunity.** If `snap-to-grid` is installed and its cotype contains shadows that suggest an abstraction, and existing code in the project is a candidate instance of that abstraction without being explicitly recognised as one, the discipline fires to bring the existing code into structural alignment.

**Do not fire on new work without existing artefacts.** If there is no working code or proof to operate on, this discipline does not apply. Use `decomposable-by-entailment` forward instead.

**Do not fire on artefacts the user has explicitly marked as off-limits for refactoring.** Some code is deliberately kept as-is for historical, reliability, or scope reasons. Respect those markers.

## The intervention

When the discipline fires, execute these steps:

### Step 1: Inventory the existing artefact

Identify what the artefact is and what external commitments it has. The external commitments are the behaviours, interfaces, types, or properties that *must* be preserved by the recomposition. These include:

- Public APIs and their documented contracts
- Test-covered behaviours
- Type signatures visible to external consumers
- Performance characteristics if specified
- Any named invariants the artefact is known to satisfy

Write these down explicitly. They are the fixed points of the refactoring; the recomposition must hit every one of them.

### Step 2: Identify candidate shadows

Examine the artefact's internal structure and list substructures that look like candidate shadows. A candidate shadow is a substructure that:

- Has a coherent name that could be given to it in isolation
- Appears at multiple sites within the artefact, OR implements a recognisable pattern that exists in other artefacts in the codebase
- Has a clear boundary: its inputs, outputs, and invariants can be stated without reference to the full artefact's internals
- Would be independently useful — the shadow could potentially serve code outside this specific artefact

Helper functions called once are not shadows; they are internal implementation details. A function called three times at different sites *is* a candidate shadow. A pattern repeated across several modules — even if not currently factored into a function — is a stronger candidate because its extraction produces reuse across module boundaries.

List the candidates. Do not extract anything yet.

### Step 3: Attempt abstraction across candidates

Examine the candidate shadows collectively. Can any of them be grouped under a common abstraction? This is the quotient-taking move: two or more candidates that differ only in specific ways might be instances of a more general pattern.

For each group of quotient-equivalent candidates, name the abstraction they are instances of. The abstraction is a new shadow at a higher level of generality than the individual candidates.

A candidate that does not quotient with any other remains a single shadow at its own level. That is fine; not every shadow has siblings.

If `snap-to-grid` is installed and a cotype exists, check whether any of the candidate shadows quotient with shadows already in the cotype from other origins. Cross-origin quotients are high-value — they reveal commonality that was invisible from any single work direction.

### Step 4: Design the recomposition

Before extracting anything, plan how the artefact will be rebuilt using the abstractions from Step 3.

For each external commitment from Step 1, trace how the recomposition will preserve it. If any commitment cannot be preserved under the proposed abstraction set, the abstraction set is wrong — return to Step 3 and reconsider.

The recomposition plan should include:

- Which shadows are extracted as independent artefacts
- How the original artefact's external interface is rebuilt using calls to the shadows
- Where the composition operation applies the shadows to reconstruct each piece of the original's behaviour

The plan is written down before any extraction begins. Context pressure erases plans held only in working memory.

### Step 5: Extract the shadows

Create the shadows as independent artefacts in the workspace. Each shadow gets its own file (or its own clearly-named section in a shared file), with:

- A type or signature
- A behavioural specification or docstring
- A minimal set of tests or verifications
- Any invariants it carries

The extracted shadow must be self-contained: if someone were to copy only this shadow out of the project and into another, it should still be meaningful.

If a cotype exists, register each extracted shadow as an entry in the cotype's shadow list.

### Step 6: Rebuild the original artefact using the shadows

Replace the original artefact's internals with calls to and compositions of the extracted shadows. The rebuilt artefact is typically smaller than the original — sometimes dramatically so — because the shared logic now lives in the shadows.

### Step 7: Verify behaviour preservation

Run every check that existed before the refactoring: tests, type-checks, proofs, integration scenarios. Every external commitment from Step 1 must still hold.

If any check fails, diagnose whether the failure is in:

- **The shadow extraction** (the shadow doesn't capture the behaviour it was supposed to),
- **The abstraction** (the abstraction is too general and loses information the original had),
- **The recomposition** (the recomposition plan missed a piece of the original's behaviour).

Fix at the level of the failure, not by special-casing at the recomposition level. Special-casing defeats the purpose of the extraction.

### Step 8: Close by externalising the structural change

Document what was extracted and why. This is typically a commit message, a changelog entry, or a comment at the top of the rebuilt artefact. The documentation should name:

- The shadows that were extracted (by name and location)
- The abstraction(s) they were grouped under, if any
- The external commitments that were preserved

This externalisation is the bridge to future work: subsequent sessions or collaborators should be able to read the structural story of the refactoring without reconstructing it from the code diff.

## When extraction should iterate

A single pass through Steps 1–8 extracts the most obvious shadows. After the first pass, new shadows may become visible that were obscured by the original monolithic structure. Strip-for-parts can iterate:

1. Complete a first pass. Verify behaviour preservation.
2. Re-examine the rebuilt artefact. Are there further shadows visible now?
3. If yes, iterate. If no, the refactoring has converged for this artefact.

Termination: when a full pass through Steps 1–8 reveals no new candidate shadows, the artefact is in a stable refactored state for its current scope. Further refactoring, if wanted, would require changing the artefact's external commitments (widening its scope) rather than extracting further shadows from its current content.

## What "success" means under this discipline

Three valid outcomes:

1. **Full recomposition.** The artefact is fully rebuilt from shadows and abstractions, behaviour-preserving, and the refactoring has iterated to convergence. The cotype (if present) has accumulated new shadows that may participate in future quotients.

2. **Partial extraction with working recomposition.** Some shadows were extracted and the artefact rebuilt around them, but other candidate shadows were identified and deferred because extracting them would have required more work than the current session could complete. The artefact is in a better state than before, and the deferred candidates are documented for future sessions.

3. **Shadow identification without recomposition.** The shadows were identified and documented, but the recomposition was not completed in this session. The shadow documentation becomes input to a later session that completes the rebuild.

All three are valid. The third outcome specifically handles the case where context runs out mid-extraction: the shadows identified are valuable even without the rebuild, and a subsequent session (potentially with `snap-to-grid` maintaining the cotype) can pick up from the documented shadows.

## Boundaries

The discipline does not apply when:

- The artefact is small enough that refactoring wouldn't produce independently valuable shadows.
- The artefact is marked as off-limits for refactoring (legacy, deprecated, frozen, or explicitly user-protected).
- The user wants only a minor tweak to the artefact without structural change.
- The work is exploratory or diagnostic rather than productive.

The discipline does not apply to *creating* new artefacts. That is `decomposable-by-entailment`'s domain. This discipline only operates on artefacts that already exist and work.

## Warning signs the discipline is being misused

**Extracting non-shadows.** If a "shadow" is only used once within the artefact, it is not a shadow — it is a renamed internal helper. Extracting it produces bureaucracy without structural value.

**Extracting orbit-elements as a wrapper.** If the ≥3 instances triggering the C7 threshold are **orbit-elements under a generating symmetry** rather than free duplicates, the standard "extract a universal record" move produces a wrapper-of-an-operator (the operator already serves as the universal). This is the C7-misfire case identified by the orbit-saturation refinement (see `shadow-architecture` discipline, discipline rule 6). Diagnostic: if the 3+ instances all have the form `<existing-operator> <args₁>`, `<existing-operator> <args₂>`, `<existing-operator> <args₃>` — and `<existing-operator>` is already the universal at the carrier-axis — the regroup is orbit-element-cataloguing, not record-extraction. Lattice classification: **S2G** (catalogue orbit position), not **RFS** (extract universal record).

**Forcing abstractions that don't quotient cleanly.** Candidates that differ in ways that can't be cleanly parameterised shouldn't be grouped under a shared abstraction. The result is an abstraction full of special cases, which is worse than leaving the candidates as distinct shadows.

**Behaviour drift.** If any external commitment fails after recomposition and the fix is a special case at the recomposition level rather than a correction to the shadow or abstraction, the refactoring has silently changed the artefact's behaviour. Revert the special case and fix at the structural level or at the shadow level.

**Extraction paralysis.** Identifying candidates without ever extracting them. The discipline must produce externalised shadows, not just a list of potential ones. If the session runs out before extraction, the candidate list is Outcome 3 (valid partial success) — but only if it has been documented externally, not kept in working memory.

**Over-extraction.** Pulling every possible pattern into a shadow produces a codebase of tiny pieces with complex composition. Extract shadows that have genuine reuse value; leave singleton patterns as internal helpers.

## Examples of clean application

**Duplicated logic across three modules.** Task: three modules each contain similar data-validation routines with slight differences. Step 2 identifies the validation routines as candidate shadows. Step 3 groups them under a single abstracted `validate` function parameterised over the differences. Step 5 extracts the validation into its own module. Step 6 rebuilds each of the three modules to call the extracted function. Step 7 confirms all prior tests pass. Result: three modules with less code, one new module with shared validation, the validation shadow registered in the cotype for potential reuse elsewhere.

**Monolithic proof with reusable tactic.** Task: a long proof in a formalisation repository uses a specific rewrite sequence at multiple points. Step 2 identifies the rewrite sequence as a candidate shadow. Step 3 recognises it could be abstracted as a named tactic or lemma. Step 5 extracts it as a standalone lemma with its own proof. Step 6 rebuilds the original proof using the extracted lemma at each site. Step 7 confirms the proof still typechecks. The extracted lemma is now available for other proofs in the repository that may need the same rewrite.

**Blocking duplication during new work.** the contributor is implementing a new feature that would require writing logic nearly identical to logic already present in another module. The discipline fires automatically. Step 2 identifies the existing logic as the candidate shadow. Step 3–6 extract it into a shared location and rebuild the original module. The new feature then calls the shared shadow rather than duplicating the logic. The refactoring is pre-emptive: it happens before the duplication would have been created.

**Cross-module cotype quotient.** A cotype from `snap-to-grid` contains several shadows from forward work, and examination suggests they quotient under a pattern. Existing code in the project implements a related pattern without being recognised as an instance. The discipline fires to bring the existing code into alignment: Step 2 identifies the existing implementation as a candidate shadow, Step 3 recognises it as an instance of the pattern the cotype suggests, Step 5 extracts and Step 6 rebuilds, and the now-aligned code participates in the cotype's abstraction.

## Interaction with the other skills

The three skills — `decomposable-by-entailment`, `snap-to-grid`, and `regroup-from-shadows` — form a complete set of shadow-architecture moves:

- **`decomposable-by-entailment`** operates forward: intact goal → shadows. Fires before substantive work begins.
- **`snap-to-grid`** operates backward: accumulated shadows → goal. Fires when shadows exist without clear central abstraction.
- **`regroup-from-shadows`** operates sideways: existing artefact → shadows + recomposition. Fires on refactoring opportunities or blocking duplication.

The three share state through externalised artefacts and through the cotype (when `snap-to-grid` is installed). Each discipline's shadows feed the others:

- Shadows produced forward by `decomposable-by-entailment` go into the cotype, where `snap-to-grid` reads them.
- Shadows extracted sideways by `regroup-from-shadows` also go into the cotype, where `snap-to-grid` may recognise them as quotient-equivalent to shadows from other origins.
- `snap-to-grid`'s cotype analysis may identify opportunities for `regroup-from-shadows` to fire on existing code.

**When all three skills are installed:** the system has bidirectional-plus-sideways shadow flow. New work produces shadows forward; those shadows accumulate in the cotype; existing artefacts get stripped to contribute their shadows; the cotype's quotients reveal patterns that cross directions; snap-to-grid events recover goals from the accumulated structure. This is the prompt-level instance of a decomposition-by-entailment architecture operating across the full lifecycle of substantive work.

**When this discipline operates without `snap-to-grid`:** it still works. Shadows extracted from existing artefacts are externalised to files in the workspace as standalone artefacts. They do not participate in a cotype, so cross-origin quotient recognition is not available, but the refactoring itself still produces the named shadows and behaviour-preserving recomposition.

**When this discipline operates without `decomposable-by-entailment`:** also fine. This discipline operates on existing artefacts, which may have been produced by any means. The absence of the forward discipline just means new work is more likely to need this discipline later.

## Cross-session persistence

Shadows extracted by this discipline persist as standard artefacts in the workspace — typically as new files or as clearly-named sections in shared files. If `snap-to-grid` is installed, they additionally register in the cotype.

The key persistence consideration: the *reason* for the extraction should be documented. Step 8's externalisation is where this happens. A shadow extracted without its rationale is a shadow that future sessions will be tempted to re-inline, losing the structural progress this discipline made. The rationale is part of the shadow's definition, not decoration.

## Meta-frame: shadow-architecture

This discipline is one of three (with `decomposable-by-entailment` and `snap-to-grid`) forming a unified shadow-architecture system. The aggregated meta-discipline `shadow-architecture` (../shadow-architecture/DISCIPLINE.md) provides the lattice-level frame: 2³ = 8 regions of discipline-presence, with discipline-induced asymmetries (this discipline's RFS is the **burst** signal — fires when shadow-recognition triggers, otherwise silent — vs DBE's carrier-frequency role and S2G's milestone-sampling role).

Use the meta-discipline when classifying ambiguous fires ("is this regroup or snap?" — answer per the rule "sideways grid moves are snap-to-grid; up-grade extractions are regroup-from-shadows"). The diagnostic: ≥3 same-grade instances → universal record above them = RFS (this discipline). Same-grade copy-from-parallel-row = S2G. Forward entailment chain = DBE.

