---
name: feedback_one_level_off_is_graded
description: "'one level off' is the tell for a GRADED operation, not a level to pick; index over the grading and keep the residue
metadata:
  type: feedback
---

USER, verbatim (2026-07-21): *"Usually, 'one level off' as a suspicion is a screaming red hot indicator that what
you're looking at needs to be thought of as a graded operation (or an operation indexed over grading), rather than
something that exists at a single 'level'. There's a reason the repo has so much machinery around indexing across
gradings."* And: *"There's no such thing as a demotion if the origin can be constructed or generalized from it."*

**Why:** posing "which level is this at — X or Y?" presupposes a single level, and the answer is almost always an
operation INDEXED OVER a grading of which both X and Y are instances (usually the grade-0 shadow). Seven forks in
one session dissolved this way: is Route A worth building (no — a coordinate, not a competitor) · is the cover
demoted to a face (no — "demote" is a ranking = a cleaver) · which apex, ExpLogCodec or Semiring (neither — both
are ungraded shadows of `GradedDivStrMorphism`/`GradedHomOver`) · one apex pole or three route poles (at grade 0
there is one; graded, `map-R` carries a residue per rung) · 1831 file edits or a cmdline flag (neither — the
`.agda-lib` `flags:` field) · site `--guardedness` at Shape or Shape/Double (neither — global dissolves the
boundary). The either/or trap, the realizability-charter's CLEAVER (collapsing a comparison to a bit instead of
keeping `(common_mode, residue)`), and the ungraded shadow are ONE failure — and the fix is one move, which IS the
wedge `a = recon q b r`.

**How to apply:** when you catch yourself asking which level something belongs at, or ranking two candidates, or
proposing to delete one because another is "preferred" — STOP and look for the grading. Reach for the repo's
indexing machinery first: `GradedDivStr`/`recon` (`Algebra/Wedge/Graded.agda`), `GradedDivStrMorphism`
(`map-C`/`map-R`/`respects-recon` — note it HARDCODES `≡`), `GradedProductOver`/`GradedHomOver`
(`OrientationBimonoidal.agda` — the latter PARAMETERIZES the target equality, and a target valued in an
unnormalized carrier like ℚ FORCES it), `LehmerAlgebra`/`fold`/`fold-unique`. A "target" is cheap — a
`GradedDivStr` is just a `recon`, one line. Worked precedent: `SignZ2Coordinates` already runs a whole A/B route
arc + content-cover in graded form, retaining the route-distinction as residue.

Relates to [[set1-is-grade-collapse]], [[never-discard-residue]],
[[collapse-keeps-the-orientation-residue]], [[feedback_reuse_search_carrier_shape]],
[[feedback_route_through_witness_tower]].
