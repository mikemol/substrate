# `BinArith` — binary arithmetic WITH CARRY, and its correctness

⟡nat-fin-rebase N1, milestone 1. N0 established that the carrier, the graded
wedge, the analysis direction and the VALUE all already existed, so nothing
was owed there. What the tree genuinely lacked is arithmetic that COMPUTES on
the bit carrier: a reuse-search for `carry|full-?add|half-?add|ripple|addBits`
finds only `AxisWord.PackedTree`'s "carry", which is GRADE OVERFLOW in a
packed tower — a different notion entirely. So the ripple adder here is built,
not cited, and its correctness is the first real theorem of the migration.

## The shape — an unfold, not two recursions

`Bin n` is LSB-first, so the head is the least significant bit and the carry
propagates head→tail. That is exactly the substrate's bounded-unfold idiom: at
each step take the cheapest decidable OBSERVATION and BLEED THE RESIDUE
forward. Two homes state it:

- `ExtrudeBisimRun.take-obs` — `take-obs (suc k) s = obs s ∷ take-obs k (more s)`
- `Wedge.Coalgebra.run` — `… = quot w ∷ proj₁ r , proj₂ r`, whose header reads
  *"the residue (remainder) IS the coalgebra's next state."*

For an adder: **the carry IS the residue**, the sum bit IS the per-step
observation, and the vector length IS the fuel. `AddU` emits the n result bits
AND returns the terminal residue in ONE traversal; `AddBits` and `CarryOut`
are PROJECTIONS of that single traversal, never a second walk of the spine.

⚑ A first draft got this wrong and the correction is worth recording. It split
the job into two structurally-recursive functions justified as keeping the
proof free of `with` — but both walked the same spine and each RECOMPUTED THE
WHOLE CARRY CHAIN, precisely the anti-pattern this migration exists to remove
("a division primitive on a carrier that recomputed its residue at every
step").

⚑ Deliberately NOT `WedgeCoalg`/`run` itself: those seek a CYCLE
(`seen?`/`eq?`, the halt/loop/stop outcome of a CF expansion). A ripple carry
is a BOUNDED prefix with no cycle test — the `take-obs` shape, not the `run`
shape. The idiom is instantiated; the cycle-seeking machinery is not.

## Scope

This is ADDITION. Multiplication lives in `BinMul`; general division is not
built and is not claimed. The archive's twice-recorded correction still binds:
assemble a certificate from per-step definitional reconstructions, never a
monolithic `wedge-eq` induction over the bits.
