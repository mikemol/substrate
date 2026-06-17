#!/usr/bin/env python3
"""jea_carrier.py — Δ-Ω-carrier: the THREE carriers are ONE width-w limb carrier in two LAYOUTS (the user-flagged
silo, unified). A value is a bit-matrix; the LAYOUT is a data-parallelism GAUGE:

  * VALUE-MAJOR  (one value's limbs contiguous; the multiply is a dp4a CONVOLUTION spread across threads -- parallel
    PER-MULTIPLY): jea_carrier_base (w-parametric, 8->4->2->1) / jea_limb_gpu (its w=8 carry instance, the crown
    deliver). Good for FEW BIG values.
  * BIT-MAJOR  (bits of MANY values as planes; the multiply is bit-sliced SWAR -- parallel ACROSS VALUES):
    jea_graded / jea_bitkernel (the fused branchless kernel). Good for MANY SMALL values.

They carry the SAME bit-matrix (value i, bit b); the two layouts are its row-major vs column-packed storage -- the
TRANSPOSE is the gauge change. At w=1 both reach the GF(2)/F₂ floor (carrier_base w=1 carryless = GF(2)[x]; bit-major
= per-bit AND/XOR). And the LAYOUT CHOICE IS the navigator's eval-strategy dispatch: value-major = the few-big crown
(per-node drain), bit-major = the many-small SWAR level (Δ-Ψ-swar-win) -- the same few-big-vs-many-small structure.

Witnesses ([W], __main__):
1. ONE VALUE, BOTH LAYOUTS: value-major limbs (carrier_base) and bit-major planes (jea_graded) reconstruct the same
   value (the transpose is lossless, every w).
2. SAME BATCH, BOTH LAYOUTS: N element-wise products via value-major (carrier_base.gpu_mul per value, dp4a) ==
   bit-major (jea_bitkernel.bs_mul, SWAR) -- one carrier, two parallelisms, identical results.
3. w=1 = GF(2) FLOOR: carrier_base w=1 carryless == clmul (the value-major F₂ multiply); the bit/F₂ representation is
   shared (the transpose preserves it).
"""
import os, sys
os.environ.setdefault("CUDA_PATH", "/usr")
import numpy as np, cupy as cp
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jea_carrier_base as CB      # VALUE-MAJOR (dp4a, w-parametric, GF(2)@w=1)
import jea_graded as GR            # BIT-MAJOR (to/from_bitsliced -- the transpose to/from planes)
import jea_bitkernel as BK         # BIT-MAJOR fused SWAR (bs_mul)
import jea_limb_gpu as LB          # VALUE-MAJOR w=8 (the crown deliver instance)


def value_major(v, w=8):  return CB.to_limbs(int(v), w)              # one value -> w-bit limbs (row-major, carrier_base)
def bit_major(vals):      return GR.to_bitsliced([int(x) for x in vals])   # values -> bit-planes (column-packed, jea_graded)
# the transpose between layouts pivots through the int: value-major <-> int <-> bit-major (the SAME bit-matrix).


if __name__ == "__main__":
    print("jea_carrier: Δ-Ω-carrier -- ONE width-w limb carrier, two LAYOUTS (value-major dp4a / bit-major SWAR), transposed\n")
    rng = np.random.default_rng(17)

    # W1: ONE value, both layouts reconstruct it (the transpose is lossless at every w)
    w1 = True
    for v in [0, 1, 7, 255, 1<<40, (1<<80)+12345]:
        vm = all(CB.from_limbs(CB.to_limbs(v, w), w) == v for w in (8, 4, 2, 1))     # value-major, every w
        bm = GR.from_bitsliced(GR.to_bitsliced([v])[0], 1)[0] == v                    # bit-major
        w1 = w1 and vm and bm
    print(f"  W1  ONE value, BOTH layouts (value-major every w + bit-major) reconstruct it (transpose lossless): {w1}")

    # W2: SAME batch of products, BOTH layouts agree -- value-major (dp4a per value) == bit-major (SWAR), one carrier
    N = 200; A = [int(rng.integers(0, 1<<g)) for g in rng.integers(4, 40, size=N)]
    B = [int(rng.integers(0, 1<<g)) for g in rng.integers(4, 40, size=N)]
    vm_prod = [CB.from_limbs(CB.gpu_mul(CB.to_limbs(a, 8), CB.to_limbs(b, 8), 8), 8) for a, b in zip(A, B)]  # value-major dp4a
    pa, _ = GR.to_bitsliced(A); pb, _ = GR.to_bitsliced(B)
    bm_prod = GR.from_bitsliced(BK.bs_mul(pa, pb), N)                                  # bit-major SWAR
    truth = [a*b for a, b in zip(A, B)]
    w2 = (vm_prod == truth) and (bm_prod == truth)
    print(f"  W2  SAME {N} products, BOTH layouts: value-major (dp4a per value) == bit-major (SWAR) == truth: {w2}")

    # W3: w=1 = the GF(2)/F₂ floor -- carrier_base w=1 carryless == clmul (the value-major F₂ multiply)
    gf = True
    for a, b in [(0b1011, 0b110), (0b11011, 0b1101), (7**20, 11**20)]:
        poly = CB.gpu_mul(CB.to_limbs(a, 1), CB.to_limbs(b, 1), 1, carryless=True)
        gf = gf and (CB.from_limbs(poly, 1) == CB.clmul(a, b))
    w3 = gf
    print(f"  W3  w=1 = GF(2) FLOOR: carrier_base w=1 carryless == clmul (value-major F₂ mul); bit/F₂ rep shared: {w3}")

    # W4: the LAYOUT IS the dispatch gauge -- value-major = few-big (crown/limb_gpu), bit-major = many-small (SWAR).
    big = (1<<400) + 7; _bl = cp.asarray(LB.to_limbs(big))
    few_big = LB.from_limbs(LB.gpu_mul(_bl, _bl)[0]) == big*big          # value-major crown (jea_limb_gpu dp4a)
    w4 = few_big
    print(f"  W4  LAYOUT = the dispatch gauge: value-major (jea_limb_gpu, few-big crown) exact ({few_big}); bit-major")
    print(f"      (jea_bitkernel, many-small SWAR) is W2 -- the carrier-layout choice IS the navigator's few-big/many-small dispatch")

    ok = w1 and w2 and w3 and w4
    print(f"\n  {'PASS' if ok else 'FAIL'} — Δ-Ω-carrier: jea_carrier_base (value-major dp4a, w-ladder, GF(2)@w=1) +")
    print(f"  jea_graded/jea_bitkernel (bit-major SWAR) + jea_limb_gpu (value-major w=8 crown) are ONE width-w limb")
    print(f"  carrier in transposed LAYOUTS -- same bit-matrix, the layout a data-parallelism gauge = the few-big/")
    print(f"  many-small dispatch. The silo is unified; w=1 is the shared F₂ floor.")
