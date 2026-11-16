# `Curve` — the Morton / Hilbert curve-crossover, as a tropical (cost) instance

⊙.c8. The loosest commuting-sphere conjecture (#8, a framing): a space-filling
curve linearizes the F₂ⁿ index; Morton (Z-order) is the plain index rank,
Hilbert is a locality-preserving reordering, and WHICH to use crosses over at a
grade boundary CHOSEN BY THE COST (tropical) instance.

This grounds the framing without reinventing a curve (none existed in the tree):

- `Morton` is the Z-order linearization (index → rank), reusing `Grade.bit`.
- The crossover IS the tropical min ⊓ (`NatInf` — the same cost gauge ⊙.c6's
  `Contraction` reads): of two curves' costs, take the cheaper; the chosen
  curve is the argmin, and the crossover BOUNDARY is the grade where the argmin
  flips.
- `Gray` is the binary-reflected Gray code — the 1D Hilbert curve (each step a
  single quadrant reflection). `GrayRoundtrip` proves it bijective, hence a
  faithful linearization like `Morton`. The full 2D Hilbert (quadrant ROTATION)
  is a refinement.
- `MortonJump` / `GrayJump` supply the crossover's REAL costs as popcount
  jumps, so `CrossoverGrayWins` is no longer hand-picked.

The full Hilbert construction is a separate build; only the SELECTION mechanism
— a tropical argmin — is C8's content.
