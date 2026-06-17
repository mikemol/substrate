#!/usr/bin/env python3
"""jea_limb_spec.py — the carrier is a BYTE-LIMB suspended generator, not a frozen u64.

u64 was an unjustified gauge-freeze (a convenient native word). For the suspended-generator /
unfold-on-demand carrier the principled grain is the BYTE: a value IS its little-endian byte
stream, length = exactly the significant bytes, unfolded one limb at a time; escalation = append
a byte (fine-grained, not 64->128 jumps). Two concrete wins this spec proves:

  1. PAY-FOR-WHAT-YOU-USE (charter #5, hoard bandwidth): small values carry 1 byte, not 8.
  2. UNFOLD-ON-DEMAND (the suspended generator, vs GMP eager limbs): the low k output bytes of a
     product of two ASTRONOMICAL numbers cost O(k^2) and touch only the low k limbs of each input
     -- independent of how huge the operands are. GMP ropes the whole product together; we unfold
     only the digits asked for. The value's CONSTRUCTION is the generator; digits come on demand.
"""

def to_limbs(v):                       # little-endian byte limbs; significant bytes only
    if v == 0: return [0]
    out = []
    while v: out.append(v & 0xff); v >>= 8
    return out

def from_limbs(ls): return sum(b << (8*i) for i, b in enumerate(ls))

def mul_low(a, b, k):
    """Low k byte-limbs of a*b, computed ON DEMAND: only touches a[:k], b[:k]; O(k^2).
    a,b are limb lists. Returns k limbs == (a*b) mod 256^k -- never materializes the full product."""
    out = [0]*k
    for i in range(min(k, len(a))):
        ai = a[i]
        for j in range(min(k-i, len(b))):
            out[i+j] += ai * b[j]
    c = 0                               # carry-propagate within the k-byte window
    for t in range(k):
        c += out[t]; out[t] = c & 0xff; c >>= 8
    return out


if __name__ == "__main__":
    print("byte-limb suspended-generator carrier (vs frozen u64)\n")

    # 1) pay-for-what-you-use
    print("  1. PAY-FOR-WHAT-YOU-USE (bytes carried vs u64's fixed 8):")
    for v in (0, 200, 70000, 2**63):
        print(f"     value {v:<22} -> {len(to_limbs(v))} byte-limb(s)   (u64 always carries 8)")

    # 2) unfold-on-demand: low k bytes of a product of two astronomical numbers
    import math
    a = 7**4000          # ~3380-byte number
    b = 11**4000         # ~3850-byte number
    al, bl = to_limbs(a), to_limbs(b)
    full_bytes = len((a*b).to_bytes((a*b).bit_length()+7 >> 3, "little"))
    print(f"\n  2. UNFOLD-ON-DEMAND: a=7^4000 ({len(al)} bytes), b=11^4000 ({len(bl)} bytes),")
    print(f"     full product = {full_bytes} bytes (what GMP would rope together).")
    for k in (4, 8, 16):
        got = from_limbs(mul_low(al, bl, k))
        want = (a*b) % (256**k)
        ops = k*k  # the convolution work for the low-k window (independent of operand size)
        print(f"     low {k:2d} bytes of a*b: {'MATCH' if got==want else 'WRONG'}  "
              f"(touched a[:{k}],b[:{k}], ~{ops} limb-mults; NOT the {len(al)}x{len(bl)} full product)")

    print(f"\n  the value is a byte-stream GENERATOR: small values cost 1 limb, huge values unfold one")
    print(f"  byte at a time, and you compute only the digits demanded -- never roping the whole thing")
    print(f"  together. Escalation = append a limb (8-bit grain, not 64->128). u64 was a frozen gauge.")
