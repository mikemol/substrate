# `BinBridge` — the ℕ↔Bin bridge

⟡nat-fin-rebase N1. The direction that walks the unary spine, and the
retraction that says the bit carrier has no junk.

## Why this folder is the missing piece

N0 and N1-milestone-1 built the carrier and its arithmetic and never built the
encoder — a real gap a user correction exposed: *"adding 4 to 7 IS the run
shape … counting to 4 or counting to 7 is the run shape (the conversion of a
decimal to a bitvec)."* The ADDER is a bounded prefix — n bits in, n bits out,
the `take-obs` shape. The CONVERSION is not: `ToBin` must consume a ℕ by
HALVING until it reaches zero, and that halt condition is the `run` shape. So
this is where the unary cost actually lives, and it is exactly the boundary
the migration has to cross ONCE so that everything above it can stop crossing
it at all.

## The ℕ-side radix-2 wedge, and why it is a co-apex

`Bin.BinDivmod2` gives `a = 2·q + r` on the BIT carrier, where it is
`vec-uncons` and holds by `refl` — dividing by the radix is free because the
radix IS the constructor. `Divmod2` here is the SAME equation on ℕ:

    boolToℕ (odd n) + (half n + half n) ≡ n

and it is NOT free: it costs a three-case induction plus four `+-suc`
transports. That asymmetry is the migration's whole thesis in one pair of
theorems. Radix-2 analysis on a numeral born as bits is a pattern match; on a
numeral born as a unary spine it is a proof. `ToBin` is the map between the two
readings, and it pays that cost once.

## Reuse, and the one deliberate non-import

`odd`/`half` do not exist in the tree (searched: no `half`, no `div2`, no
`even`). `oddB : ℕ → Bool` DOES exist — `WitnessTower/InsertionParity.agda:87`
— but in its ONE-STEP form (`oddB (suc n) = not (oddB n)`) and inside the
permutation-sign cone. Importing it would drag Perm/CoxGen/sign into the
numeral carrier, which is precisely the closure this arc exists to stop
paying, and the one-step form is the wrong recursion anyway: `odd` and `half`
must step TOGETHER, two at a time, or `Divmod2` is not a three-case induction.
So the pair is local and the sibling is cited rather than imported — an honest
cost, not an oversight. (`Algebra.N-to-F2-Parity.parity : ℕ → F₂` is the other
sibling; it is lighter but F₂-valued and still gives no `half`.)

## What is proved here, precisely

- `ToBinSection` — `toBin w (value b) ≡ b`, for EVERY `b : Bin w`. The encoder
  is a RETRACTION: every n-bit numeral is the encoding of its own value, so
  the carrier has no junk. `ValueInjective` follows in two lines.
- `ToBinValue` — `value (toBin w n) ≡ n` whenever `n < 2ʷ`. The other
  direction, and it needs the bound: `toBin` TRUNCATES, so above 2ʷ the high
  bits are dropped. That bound is the honest statement of the predicted width,
  and `BinTrim.Trim` is what reads back how much of it was actually used.

Together: `Bin w ≅ { n : ℕ ∣ n < 2ʷ }`.
