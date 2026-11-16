---
name: feedback-2d-first-then-conform
description: "For parametric 2D glyph/decal geometry engraved onto 3D figures, verify the flat 2D construction before mapping; conform decals to the surface and extrude along the local normal."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 49bbd55e-7a45-4904-a48a-ed08e8709e13
---

When building parametric 2D marks (glyphs, decals, inscriptions) that get engraved
onto curved 3D geometry (e.g. Blender figures under scratch/figures), the user's
discipline:

**Verify the flat 2D geometry first** (matplotlib, with the construction guide
overlaid) BEFORE mapping into 3D. This decouples geometry-correctness from
mapping-correctness — every "glyph looks wrong" bug we chased turned out to be in
the 3D mapping, never the construction. Test 2D, then map.

**To engrave on a curved surface, conform the 2D decal to it** — do NOT cut with a
single flat slab positioned for one radius (it floats off inward-curving caps and
the mark never engraves). Instead: parametrize the surface (for a capsule, meridian
arc-length s along the axis, folding over the endcaps; arc-length u around), map
each 2D point to (surface point, surface normal), and **extrude along the LOCAL
surface normal** to build the cutter prism.

**Why / supporting rules learned:**
- Select recess floors via the shape's **SDF** (e.g. capsule = dist-to-axis-segment
  − r), not a global facing direction — the global-normal test fails on caps.
- Carve **one decal at a time** as separate sequential booleans. Overlapping cutters
  (forced on short/stubby hosts) self-intersect and invert the EXACT solid, deleting
  the whole host mesh. A single decal cutter is fine; the union of overlapping ones
  is not.
- Keep decal extent clear of parametrization **singularities** (ring radius → 0 at
  capsule poles) — degenerate cutters there also corrupt the boolean.

Relates to [[feedback_section_then_lemma_for_parametric]] (verify the small unit
before composing) and the prototype-before-figure habit.
