---
name: feedback_enumerate_dont_proxy_filter
description: "when the full structural space is available (the interned SPPF), ENUMERATE it — don't impose thresholds/filters or reason from proxy measurements"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: d35bc15a-16b8-42c5-aad1-20966c9a9f8e
---

When the full structural search space is already built — the agglomerated SPPF interned from every
`.agdai` core (the full-build discipline exists precisely to produce it) — **enumerate it directly**.
Do NOT impose interpretive filters (min-size, max-fanin, "noise vs signal", "vocabulary") or reason from
a PROXY measurement and then editorialize a conclusion.

Corrected repeatedly in one session (2026-07-13, ⟡reuse-sweep):
- I filtered out high-fanin subtrees as "shared vocabulary, not dups" — WRONG: **fanin IS duplication =
  the consolidation win** (N instances of one pattern → parameterize it; X-is-an-instance-of-Y is the
  point of the research program, not a warning). [[coxeter-word-is-combine-generators]] [[feedback_no_bespoke_sum_or_subtypes]]
- I concluded "SnRig shares only primitives / sits at rung 0" — WRONG: that was an artifact of a
  `min_size 6` filter I imposed. Enumerating fully (`min_size 2`) showed SnRig richly participates in the
  `replay-*` family, the decode-density family (`on-iso₂`), and the RigAlgebra field patterns.

**Why:** the interner is bottom-up-complete — the shared canonical nodes ARE the structure, at every
depth. Any threshold I add HIDES real structure and substitutes my guess about what matters. Proxy
reasoning ("rung 0 ⇒ shallow") compounds the error.

**How to apply:** default to enumerating the whole thing (rank by impact for DISPLAY, e.g. `--top`, but
never DROP rows by an assumed-meaning filter). Present the raw enumeration; let the data speak. Reserve
thresholds for performance only, and say so. Think Sequitur, recursively: repeated structure → a rule →
recurse ([[reuse-search-before-feasibility-conclusions]]).
