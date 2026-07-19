---
name: tightening-loop
description: Turn a hand-built result into repo-integrated, fully-reified structure via one recurring three-phase loop — co-apex (bridge the result to the pre-existing term it should meet), reify-audit (catch where a tie was asserted in prose but no term was wired), and cover (build a higher construction that cross-links a cluster of co-apexes and unifies threads). Use whenever a proof, lemma, definition, or claim has just been built by hand and might duplicate or connect to existing machinery; whenever a result is stated as a prose pointer ("these ARE the same", "this corresponds to", "cites X") without a checkable term; whenever several bridges have accumulated and want a unifying apex; or whenever an either/or has been dissolved to a "common structure" that still lives only in prose. Fires on phrases like "this is just X", "same as the existing Y", "wire this to", "does this already exist", "tighten this", "is this a pointer or a term", "cover these", "what unifies these". Distinct from the discipline-cluster (which prevents under-scoping the toolkit); this is the constructive method for what you DO once a result is in hand — integrate it, reify it, unify it. Do NOT fire on a result that is already a checkable term meeting existing machinery, or on pure exploration with nothing yet built.
---

# The Tightening Loop

A hand-built result is not done when it typechecks. It is done when it is **integrated** (meets the pre-existing machinery it should meet), **reified** (every claimed tie is a checkable term, not prose), and **covered** (a cluster of such results is unified by a construction that cross-links them). These are not three habits — they are **three phases of one loop**, and the loop's output feeds its own input: a cover produces new siblings that become the next round's co-apexes.

This skill is the constructive counterpart to a defensive discipline. Where a toolkit-scan keeps you from *stopping short* (recording a false blocker, missing an available tool), the tightening loop is **what you do when you don't stop short**: it takes the result you built and drives it down from a standalone artifact to repo-integrated, fully-reified, unified structure. One keeps you moving; the other is the move.

**The anti-pointer principle.** A prose tie — "these three parities *are* the coordinate iso," "this *corresponds to* the existing bijection," "cites the co-apex" — feels like integration and is its opposite: it has the texture of a bridge with none of the load-bearing. It relocates a *checkable identification* into an *unverifiable assertion*, and it commits to nothing a future reader can run. If you catch yourself asserting a tie in prose, that is the reify-audit firing: stop and either wire the term or name the pointer honestly as open. The prose assertion is the failure mode this loop's middle phase exists to replace — exactly as free-floating self-criticism is the failure mode the retrospective ritual replaces.

## When to run it

Trigger on **any just-built result that could connect to existing structure** — a proof, a lemma, a definition, a claim, or a dissolved either/or. Not only on completions: a mid-build "wait, doesn't this already exist?" is the co-apex phase asking to fire. Scale depth to stakes — a one-line co-apex citation for a small lemma, the full three-phase loop with a covering for a cluster — but never fake a phase. Skip a phase by *declaring it out of scope* (e.g. "no sibling cluster yet, cover deferred"), never by asserting its output without the term.

**Do not fire** on a result that already meets its machinery as a checkable term (nothing to tighten), or on pure exploration with nothing built yet (nothing to integrate). The loop needs an artifact in hand.

## The three phases

Run them in order per result; the loop closes when a cover's new siblings re-enter as co-apexes.

### P1 — CO-APEX (bridge the result to its pre-existing term)

For the result just built, find the **pre-existing repo term it should meet** and wire a named lemma plus a checkable identification (ideally `refl`) between them. The rediscovery becomes a bridge, not waste; the hand-proof becomes discoverable from the existing machinery and vice versa.

- **Gate:** the co-apex must name a *specific existing term* and state the *identification as a checkable claim*. "This relates to the sign machinery" is not a co-apex; "`signF σ ≡ bool→F₂ (sign σ)` by `refl`, meeting `TowerCocycleGraded.signF`" is. If no pre-existing home exists, that is a valid finding — record "no repo home; standalone" honestly (the honest non-co-apex), which becomes a candidate for a future covering.
- The co-apex has two grades: **tight** (a `refl`/definitional identification — the term meets the machinery) and **pointer** (a named-but-prose correspondence — "these are the same," not yet a term). A pointer is not a failure; it is an *honestly-named half-built co-apex*. But it must be labeled as a pointer, which is what P2 enforces.

### P2 — REIFY-AUDIT (catch the prose pointer, wire the term or name it open)

Audit the co-apex just built: **did you wire a term, or assert a tie in prose?** This is the load-bearing middle phase — the one that most often catches itself.

- **Gate:** every claimed identification is either a *checkable term* or *explicitly marked as a prose pointer with an open action item to reify it*. A tie asserted in prose and banked as "done" is theater — the precise thing this phase exists to eliminate. If you wrote "these ARE the coordinate iso" but wired no `V₄ → Bool × Bool` term with roundtrips, the audit *fails* and the finding is: reify-term open, not integration done.
- **The one-line test:** for the identification, ask *could a future reader run it?* If yes, it is reified. If it is a sentence they must take on trust, it is a pointer — file it as open (`◆tighten-<name>`), do not smooth it into "done."
- Reify-audit also runs *across* the accumulated co-apexes as a standing sweep: "which of my bridges are still prose pointers?" This is the audit you run when asked "any open co-apexes?" — it enumerates the un-reified ties.

### P3 — COVER (build the higher construction over a cluster of co-apexes)

When several co-apexes accumulate, build **a covering construction over them** — one apex that cross-links the siblings and, when it works, *unifies threads that were separate*. This is the higher-closure phase.

- **Gate:** a covering must *cite the flagship terms of its siblings*, not merely re-state them or cite early/pre-flagship witnesses. A cover that names the roles but wires in stale witnesses is a *pointer-cover* — P2 applies to the cover itself: reify it against the flagships or mark it open (`◆wire-<cover>`).
- **The generative signal.** A covering is worth building precisely when it is *not* mere bookkeeping. The diagnostic: if wiring the cover *unifies two threads that were tracked separately* (an N-sweep audit with a sign arc; three parity-facts with one coordinate iso), it is generative and load-bearing. If it only files existing bridges under one heading, it is a filing exercise — still valid, but do not expect surprise. Watch for the surprise; it is the sign the cluster shared a common structure you had not named.
- **The loop closes here.** A covering's cross-links are *new results* — they are themselves co-apexes (the covering meets each sibling's term). So P3's output re-enters at P1: the covering's siblings-as-met become the next round's bridges, and a covering-of-coverings becomes reachable. This is why it is a loop, not a pipeline.

## The loop as one move

The phases interlock; a single arc usually fires all three:

```
build result → P1 co-apex (bridge to existing term)
             → P2 reify-audit (term? or prose pointer → open ◆tighten)
             → [cluster accumulates]
             → P3 cover (unify siblings; cite flagships)
             → cover's cross-links are new co-apexes → P1 …
```

The canonical trace: you build a coordinate apex (P1), it comes out as a prose pointer — "these three parities are the coord iso" — the reify-audit catches it (P2), tightening wires the `V₄ → Bool × Bool` term with roundtrips, and that tight iso becomes a sibling in a covering over the grade-role flagships (P3), whose cross-links are the next co-apexes.

## Relation to the recursive-common-structure rule

The tightening loop is *why* "at an either/or, find the common structure recursively" bottoms out in **terms rather than prose**. Each recursive dissolution, left alone, is a prose pointer ("sign and coord are two coordinates of one decomposition"). The loop forces that pointer down: P1 bridges it to an existing term, P2 refuses to bank it as prose, P3 covers the dissolved siblings. Without the loop, the recursion produces elegant prose gestures; with it, the recursion produces `refl`-identifications against the repo's actual machinery. The deepest dissolutions in a session — where a hand-gesture meets an already-reified pattern in the corpus — are the loop running to completion: the prose "these rhyme" pushed until it *is* the existing named structure.

## Registering to the cotype

Each phase writes to the cotype (working-memory tightening is erased by context pressure and does not persist). The entry records:

- **phase** — P1 co-apex / P2 reify-audit / P3 cover.
- **the result** and **the term it meets** (or "no home; standalone").
- **grade** — tight (`refl`/term) or pointer (prose, with the open `◆tighten`/`◆wire` item).
- **for covers:** which sibling flagships it cites, and whether wiring it unified separate threads (the generative signal) or filed existing ones.

An open pointer is a first-class, honestly-named state — *not* a defect to hide. The cotype should show the pointer co-apexes and pointer-covers explicitly, each with its reify action item, so a future session tightens them rather than re-discovering they were never terms.

## The one-line test for whether you actually ran it

For each phase, ask: **did it produce a checkable term, or did I narrate a tie?** If P1 named a specific existing term, P2 either wired the identification or filed an honest `◆tighten`, and P3 cited flagships (or declared no-cluster-yet) — the loop ran. If any phase banked a prose pointer as done, that phase failed, and the honest move is to name the pointer open, not to smooth it into integration.
