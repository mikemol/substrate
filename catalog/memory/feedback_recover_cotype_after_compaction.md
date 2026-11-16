---
name: feedback_recover_cotype_after_compaction
description: "after a context compaction (esp. one that landed BETWEEN planning and executing), recover the plan + last commits + persistent cotype BEFORE executing — the summary is lossy and you will re-derive badly"
metadata:
  node_type: feedback
  type: feedback
  originSessionId: d35bc15a-16b8-42c5-aad1-20966c9a9f8e
---

A context compaction produces a LOSSY summary. If one lands between constructing a plan and executing it, the
executing self runs on the summary and **re-derives — badly — machinery the plan/commits/cotype already
specified.** 2026-07-13: post-compaction I re-derived a broken (full-inlining) version of the graded-orbit
key whose correct **handle/relative-address design was already written** in the cotype
(`scratch/pyast_rigcat_dissolution.md:1099-1103` "points reference level-(k-1) orbit-points … a choice of
lower-orbit-point") and the Phase-B commit prose ("keys as its content-addressed qname"). The user had to
stop me: *"review the previous plan, and the last dozen commits, and progress along the persistent cotype;
you had a compaction between constructing the plan and executing it, so you lost a lot of context without
realizing it."*

**How to apply — on resuming after any compaction, BEFORE the first substantive move:**
1. Read the **plan file** in full (not just the summary's gloss of it).
2. `git log --oneline -~15` + `git show` the commits of the current arc — the design intent often lives in
   commit prose / code comments the summary dropped.
3. Recall the **persistent cotype**: `scratch/<arc>.md` + the memory mesh apexes for this arc. Confirm
   load-bearing claims against the LIVE code (memories carry staleness).
4. Only then execute. Treat a plan step as "verify the design that already exists," not "invent it."

The tell you skipped this: you find yourself DESIGNING something the arc clearly already built, or a user
says "we chased this exact thing days ago." Two Explore agents (commits+code; cotype+specs+memories) recover
it fast. Relates to [[feedback_reference_is_a_handle_not_inlined]],
[[feedback_reuse_search_before_feasibility_conclusions]], [[handoff-blind-spot]].

⚑ 2026-07-22 RECURRENCE (fired via the USER again, not self — confirming the ceiling: a memory is
skippable). Post-compaction I ran the summary's gloss ("everything compiled except gen-v; restore the
wall module + fix gen-v") and (a) restored a module that is a WALL-WITNESS (cannot compile — its local
`≈⟨_⟩_` combinator walls universally under eta), (b) reached to hand-pin then codemod the proof — when the
durable cotype (`scratch/jac_rosetta_stone.md`) already encoded the OPERATIONAL LAW (`cong φ bridge`), the
extractor (`decode_core`), and the finding (the wall is INFERENCE; the machinery SUPPLIES the endpoints).
User: *"Re-read the rosetta stone; it feels like you've lost a lot of context."* Reading it recovered the
whole method (the free-algebra UP lift). Re-read the arc's cotype BEFORE the first substantive move.
