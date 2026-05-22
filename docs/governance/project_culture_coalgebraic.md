# Project culture: coalgebraic, not consumer-driven

_(Substrate governance policy. Migrated from `memory/discipline/feedback_coalgebraic_not_consumer_driven.md`.)_

**Rule.** When deferring work from a slice, justify the deferral by **slice-scope discipline** (= "this slice's coalgebraic unfolding covers X; Y is a separate unfolding"), not by hypothetical consumer demand (= "if downstream consumers need it, do Y later"). The substrate is being built coalgebraically; consumers come second.

**Why:** Coalgebraic vs algebraic framings produce different work orderings:
- **Algebraic** (build from primitives toward consumer goals): you build only what's needed; gauge structure is implicit and risks rigidification.
- **Coalgebraic** (unfold the structure that's there): you expose all the gauge choices, orbit relationships, and structural symmetries; the substrate becomes self-describing at multiple meta-levels (see [[project_tetrative_metacircularity]]).

The substrate's central commitments (gauge-honesty, multi-reading-ambient discipline, fractal recurrence at meta-levels, resistance to rigidification) ARE the coalgebraic move. "If consumers need it" framing slides toward algebraic thinking — toward fixing gauges prematurely because no consumer has surfaced the alternatives yet.

**How to apply:**

- **In DBE plans' "out of scope" sections:** justify deferrals by "this slice's scope is concrete-witness rather than abstract-completeness" or "the full orbit-coverage is a natural coalgebraic-unfolding follow-on." NOT by "deferred unless a consumer needs it."

- **When sizing slices:** a slice's "successful completion" is structural — does it expose the gauge cleanly, surface alternatives, name the orbit? — not consumer-driven (does X have callers).

- **When refactoring:** if existing code rigidifies a gauge choice, surface the alternatives (formalize a few, document the orbit) regardless of whether anything else in the codebase needs them. The coalgebraic substrate's value IS this surface.

- **When evaluating progress:** progress is measured by structural completeness of the unfolding, not by what's downstream-callable.

**Connection to other discipline:**

This is the dual of [[feedback_choice_rigidification_in_substrate]] (don't fix gauges) and [[feedback_ordering_is_chirality_choice]] (gauges have gauge-of-gauges). Both rules say "surface the gauge"; this rule says "the surfacing is the WORK, not an optional add-on for consumers."

It also reinforces [[feedback_composable_primitives_over_flat_enumeration]] (composable structure over flat enumeration) by clarifying WHY composable structure matters: it's coalgebraic unfolding, not algebraic build-to-spec.

**Anti-pattern flagged in my prior DBE plans:**

Phrases like "deferred unless a consumer needs it," "out of scope until downstream requires it," "follow-on slice if needed" — these slip into algebraic framing. Replace with: "this slice's coalgebraic scope covers X; the full structural unfolding (Y, Z, ...) is a separate slice," or just "deferred to a follow-on slice (M-x.y.z) for [structural reason]." Coalgebra is the work, not the optional polish.

**Cross-references:** [[project_tetrative_metacircularity]], [[feedback_choice_rigidification_in_substrate]], [[feedback_ordering_is_chirality_choice]], [[feedback_multi_reading_ambient_discipline]], [[feedback_composable_primitives_over_flat_enumeration]].
