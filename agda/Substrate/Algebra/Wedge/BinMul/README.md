# `BinMul` — multiplication, and the width law

⟡nat-fin-rebase N1, milestone 2.

    mul : Bin m → Bin n → Bin (m + n)          -- widths ADD

## The width law is the signature

A machine-word carrier has to compute the result width, assert it fits, and
escalate the carrier when it does not. Here the same law is the `_+_` in the
return type: `m + n` is not a fact to check, it is where the answer lives. The
sibling implementation's rule for its bit-sliced multiply — operand grades
Ga, Gb produce an output of grade Ga+Gb — is this signature, read at runtime.

## Shift-and-add, on bare bits

The recursion is the schoolbook one, read LSB-first so it matches `AddU`'s
direction and `Bin`'s own convention:

    (a ∷ as) · bs  =  (a AND bs)  +  2·(as · bs)

`Sel` is the broadcast-and-mask a hardware multiplier performs, not a
conditional; `2·x` is a `false` cons, because doubling in an LSB-first numeral
IS the constructor. Both operands of the inner add are plain `Bin`s and the
add is `BinArith.AddBits`, so nothing here is a reified per-step record: the
computation is structural recursion on bare bits, exactly as the constraint
requires ("so long as they're not reified _records_, [these] are structural
reductions"). The certificate is a separate theorem over the same bits, never
a field of the data.

## The one transport

See `ShiftFits`. The partial product has the MULTIPLICAND's width; the answer
has the sum width; they differ by nothing but commutativity, and the index
convention `m + n` confines that to a single `subst` on one operand.

## Honest debts

Both are recorded on `MulU` itself: the carry-out provably vanishes (the
product always fits the predicted width) but that is NOT proved here, and
`value (mulU as bs) ≡ value as * value bs` is not built. General `divide` is
not here either.
