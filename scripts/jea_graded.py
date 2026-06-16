#!/usr/bin/env python3
"""jea_graded.py — the GRADED, SUB-BYTE value carrier (bit-sliced). A value is carried at its GRADE (bit-length),
not a frozen fixed width. u128 (two u64 lanes, 256 bits/rational regardless of content) was a frozen coordinate
[[feedback_judgement_is_demechanization]]: the grade is ALREADY known (predict_per_node / the kernel's bln,bld), so
pinning the carrier to 128 pads and discards that residue [[feedback_wedge_not_projection]]. coordinate->geometry:
the carrier WIDTH is the grade, mechanized down to a single bit.

SUB-BYTE arithmetic = BIT-SLICED / SWAR. The N values are stored as G bit-PLANES: plane[b] is a bitmask holding bit
b of every value (64 values per uint64 word). One bitwise op on a plane operates on 64 values at once; a grade-g
value uses exactly g planes -- 1..7-bit values pack BELOW a byte, the strongest packing. Arithmetic is built from
AND/XOR across planes (ripple-carry add; shift-and-add multiply) -- genuinely below byte granularity. This is the
F2-dataflow carrier the charter (M1) points at; a rational is two graded integers (num,den), each bit-sliced.

Witnesses ([W], __main__):
1. PACK/UNPACK round-trips exact (the bit-sliced rep is lossless at the grade).
2. SUB-BYTE ADD: bit-sliced ripple-carry add == Python, for N values in parallel (incl. sub-byte grades).
3. SUB-BYTE MUL: bit-sliced shift-and-add multiply == Python.
4. GRADED RATIONAL: rational *,+ via the carrier (num/den each graded) == Fraction, exact.
5. [numbers] PACKING: sub-byte grade-packing bits vs the u128 fixed lane -- the density the graded carrier buys.
"""
import os, sys
os.environ.setdefault("CUDA_PATH", "/usr")
import numpy as np, cupy as cp
from fractions import Fraction


def grade(v): return max(1, int(v).bit_length())                         # the GRADE of a value = its bit-length (>=1)


def to_bitsliced(vals):
    """Pack nonneg ints -> bit-sliced planes (G, W) uint64: plane[b] bit (i&63) of word (i>>6) = bit b of vals[i].
    G = max grade (sub-byte when small). The host bit-extraction is O(N*G); the arithmetic below is device SWAR."""
    vals=[int(v) for v in vals]; N=len(vals); G=max(1, max((grade(v) for v in vals), default=1)); W=(N+63)//64
    host=np.zeros((G,W), np.uint64)
    for i,v in enumerate(vals):
        w=i>>6; one=np.uint64(1)<<np.uint64(i&63); b=0
        while v:
            if v&1: host[b,w]|=one
            v>>=1; b+=1
    return cp.asarray(host), N


def from_bitsliced(planes, N):
    host=cp.asnumpy(planes); G=host.shape[0]; out=[0]*N
    for i in range(N):
        w=i>>6; bit=np.uint64(i&63); v=0
        for b in range(G):
            if (host[b,w]>>bit)&np.uint64(1): v|=(1<<b)
        out[i]=v
    return out


def _pad(A, G):
    return A if A.shape[0]>=G else cp.concatenate([A, cp.zeros((G-A.shape[0], A.shape[1]), cp.uint64)])


def bs_add(A, B):
    """Bit-sliced ripple-carry add (SWAR): A,B planes -> (max(Ga,Gb)+1, W). G bitwise steps process all 64*W values."""
    G=max(A.shape[0], B.shape[0]); W=A.shape[1]; A=_pad(A,G); B=_pad(B,G)
    out=cp.zeros((G+1,W), cp.uint64); carry=cp.zeros(W, cp.uint64)
    for b in range(G):
        a=A[b]; bb=B[b]; out[b]=a^bb^carry; carry=(a&bb)|(carry&(a^bb))   # sum bit + carry-out, per bit-plane
    out[G]=carry
    return out


def bs_mul(A, B):
    """Bit-sliced shift-and-add multiply: A (Ga) x B (Gb) -> (Ga+Gb, W). For each bit-plane c of B, add the per-value
    masked A shifted up by c planes (multiply by 2^c). Product of grades Ga,Gb fits Ga+Gb planes."""
    Ga,W=A.shape; Gb=B.shape[0]; acc=cp.zeros((Ga+Gb,W), cp.uint64)
    for c in range(Gb):
        masked=A & B[c][None,:]                                          # keep A only where B's bit c is set (per value)
        partial=cp.zeros((Ga+Gb,W), cp.uint64); partial[c:c+Ga]=masked   # placed at planes [c, c+Ga) = A * 2^c
        acc=bs_add(acc, partial)[:Ga+Gb]                                 # accumulate (product fits Ga+Gb planes)
    return acc


_F64 = cp.uint64(0xFFFFFFFFFFFFFFFF)
def bs_sub(A, B):
    """Bit-sliced ripple-BORROW subtract: (A - B mod 2^G, per-value borrow_out) -- borrow=1 iff A<B. The complement
    of bs_add; a full-subtractor over bit-planes (diff=a^b^bin; bout=(~a&b)|(~(a^b)&bin)), branch-free SWAR."""
    G=max(A.shape[0],B.shape[0]); W=A.shape[1]; A=_pad(A,G); B=_pad(B,G)
    out=cp.zeros((G,W),cp.uint64); bor=cp.zeros(W,cp.uint64)
    for b in range(G):
        a=A[b]; bb=B[b]; out[b]=a^bb^bor; bor=((a^_F64)&bb)|(((a^bb)^_F64)&bor)
    return out, bor

def q_sub(a, b):
    """Rational a - b for a >= b (result >= 0) via the carrier -- the conductance/throughput domain (differences of
    MONOTONE quantities). a-b = (a.n·b.d - b.n·a.d)/(a.d·b.d): cross-products via bs_mul, the non-negative numerator
    difference via bs_sub, all on the carrier. The carrier stays UNSIGNED (the GF(2)/F2-home form); SIGN is a
    NORMALIZATION/readout gauge, never carried -- bs_sub returns the borrow (the would-be sign bit) so a caller with a
    possibly-negative result can normalize at the boundary (bias / orient + an F2 bit), not in the carrier."""
    an,_=to_bitsliced([a.numerator]); ad,_=to_bitsliced([a.denominator])
    bn,_=to_bitsliced([b.numerator]); bd,_=to_bitsliced([b.denominator])
    diff, _ = bs_sub(bs_mul(an, bd), bs_mul(bn, ad))                 # (a.n·b.d) - (b.n·a.d), unsigned (a>=b -> borrow 0)
    return Fraction(from_bitsliced(diff, 1)[0], from_bitsliced(bs_mul(ad, bd), 1)[0])


# --- graded RATIONAL: two bit-sliced integers (num, den); arithmetic stays bit-sliced (reduce at readout, host gcd) ---
def rat_mul(nA,dA, nB,dB):  return bs_mul(nA,nB), bs_mul(dA,dB)                          # (na/da)*(nb/db)
def rat_add(nA,dA, nB,dB):  return bs_add(bs_mul(nA,dB), bs_mul(nB,dA)), bs_mul(dA,dB)   # cross-multiply add


def combine_batch(op, nL, dL, nR, dR):
    """Δ-Ψ-forest (c): evaluate a BATCH of N independent same-op rational combines in ONE bit-sliced SWAR pass (the
    eval-path use of the graded carrier). op: 1=multiply, 0=add. The N pairs are bit-sliced (64 per word), combined
    by per-bit-plane AND/XOR (no per-node loop), reduced at readout (host gcd). The independent same-op BATCH is the
    SWAR unit that reconciles bit-slicing with the per-node drain -- a forest level / op-class is exactly such a batch."""
    pnL,_=to_bitsliced(nL); pdL,_=to_bitsliced(dL); pnR,_=to_bitsliced(nR); pdR,_=to_bitsliced(dR)
    rn,rd = (rat_mul if op==1 else rat_add)(pnL,pdL, pnR,pdR)             # ONE bit-sliced op for all N combines
    N=len(nL); RN=from_bitsliced(rn,N); RD=from_bitsliced(rd,N)
    return [ (lambda f:(f.numerator,f.denominator))(Fraction(RN[i],RD[i])) for i in range(N) ]   # reduce at readout


# --- graded RATIONAL as DEVICE-RESIDENT plane-tuples (num_planes, den_planes): thread bit-sliced planes THROUGH a
#     computation without host Fraction reconstruction between ops; reciprocal = SWAP (the ℚ field quotient, free).
#     Used for the on-device operating-point solve (Δ-Ω-onegraph brick 4): values never leave the device mid-solve. ---
def gr_lift(f):  n,_=to_bitsliced([f.numerator]); d,_=to_bitsliced([f.denominator]); return (n, d)   # Fraction -> device planes
def gr_mul(A, B): return (bs_mul(A[0], B[0]), bs_mul(A[1], B[1]))                     # (na/da)·(nb/db) -- device, no readout
def gr_add(A, B): return (bs_add(bs_mul(A[0], B[1]), bs_mul(B[0], A[1])), bs_mul(A[1], B[1]))   # cross-mul add -- device
def gr_recip(A):  return (A[1], A[0])                                                # SWAP num<->den planes = ℚ wedge quotient (free)
def gr_read(A):   return Fraction(from_bitsliced(A[0], 1)[0], from_bitsliced(A[1], 1)[0])  # reduce ONCE at readout (host gcd)


_W = np.uint64(0xFFFFFFFFFFFFFFFF)
def _extract(buf, off, width):
    """Read `width` bits at bit-offset `off` from a device uint64 bit-buffer -> Python int (only at query/readout)."""
    if width==0: return 0
    w0=off>>6; b0=off&63; nw=((off+width-1)>>6)-w0+1
    acc=0
    for j,wd in enumerate(int(x) for x in buf[w0:w0+nw].get()): acc|=wd<<(64*j)
    return (acc>>b0)&((1<<width)-1)


class GradedStore:
    """Device-resident, SUB-BYTE, contiguous bit-packed value store. Each value is packed to EXACTLY its grade bits
    (1 bit up) in a device uint64 bit-buffer; per-id (offset,grade) is the small host index. Replaces host Python-int
    value lists -- the graded RESIDENCY for the forest (Δ-Ψ-forest b): the heavy arbitrary-magnitude VALUES live on
    the device packed to grade (no u128 padding, no 8-bit-limb floor); the offset/grade index is host (like op/lch)."""
    def __init__(self):
        self.nbuf=cp.zeros(64,cp.uint64); self.dbuf=cp.zeros(64,cp.uint64); self._nb=0; self._db=0
        self.noff=[]; self.ngr=[]; self.doff=[]; self.dgr=[]              # per-id num/den bit-offset + grade (host index)

    def _grow(self, buf, words):
        if buf.size>=words: return buf
        cap=buf.size
        while cap<words: cap*=2
        nb=cp.zeros(cap,cp.uint64); nb[:buf.size]=buf; return nb

    def _put(self, buf, bits, v, g):
        o=bits; w0=o>>6; b0=o&63; buf=self._grow(buf, ((o+g-1)>>6)+1); span=((g+b0+63)>>6)
        cur=[int(x) for x in buf[w0:w0+span].get()]; val=(int(v)<<b0)
        for j in range(span): cur[j]|=(val>>(64*j))&int(_W)                # OR the value's bits in (merge the partial word)
        buf[w0:w0+span]=cp.asarray(cur,cp.uint64); return buf, o+g

    def append(self, num, den):
        num=int(num); den=int(den); gn=grade(num); gd=grade(den)
        self.noff.append(self._nb); self.ngr.append(gn); self.nbuf,self._nb=self._put(self.nbuf,self._nb,num,gn)
        self.doff.append(self._db); self.dgr.append(gd); self.dbuf,self._db=self._put(self.dbuf,self._db,den,gd)
        return len(self.noff)-1

    def value(self, sid):
        return Fraction(_extract(self.nbuf,self.noff[sid],self.ngr[sid]), _extract(self.dbuf,self.doff[sid],self.dgr[sid]))
    def is_crown(self, sid): return self.ngr[sid]>128 or self.dgr[sid]>128   # >u128 -> needs the byte-limb deliver path
    def size(self): return len(self.noff)
    def bits(self): return self._nb+self._db                             # total VALUE bits resident (sub-byte packed)


if __name__ == "__main__":
    print("jea_graded: the GRADED, SUB-BYTE (bit-sliced) value carrier -- carrier width = grade, packs below a byte\n")
    rng=np.random.default_rng(11)
    # a mix of grades: many SUB-BYTE (1..7 bit) + some larger, to exercise packing + carry across grades
    grades=[int(g) for g in rng.integers(1,8,size=140)]+[int(g) for g in rng.integers(8,40,size=60)]
    A=[int(rng.integers(0,1<<g)) for g in grades]; B=[int(rng.integers(0,1<<g)) for g in grades]; N=len(A)

    pA,_=to_bitsliced(A); pB,_=to_bitsliced(B)
    w1 = (from_bitsliced(pA,N)==A) and (from_bitsliced(pB,N)==B)
    print(f"  W1  PACK/UNPACK round-trip exact ({N} values, grades {min(grades)}..{max(grades)}): {w1}")

    addr=from_bitsliced(bs_add(pA,pB), N); w2 = addr==[a+b for a,b in zip(A,B)]
    print(f"  W2  SUB-BYTE ADD (bit-sliced ripple-carry, {N} adds in parallel) == Python: {w2}")

    mulr=from_bitsliced(bs_mul(pA,pB), N); w3 = mulr==[a*b for a,b in zip(A,B)]
    print(f"  W3  SUB-BYTE MUL (bit-sliced shift-and-add) == Python: {w3}")

    # W4: graded RATIONAL arithmetic via the carrier (num/den each bit-sliced); reduce at readout (host gcd)
    nums=[int(rng.integers(1,1<<5)) for _ in range(N)]; dens=[int(rng.integers(1,1<<5)) for _ in range(N)]
    nums2=[int(rng.integers(1,1<<5)) for _ in range(N)]; dens2=[int(rng.integers(1,1<<5)) for _ in range(N)]
    nA,_=to_bitsliced(nums); dA,_=to_bitsliced(dens); nB,_=to_bitsliced(nums2); dB,_=to_bitsliced(dens2)
    mn,md=rat_mul(nA,dA,nB,dB); an,ad=rat_add(nA,dA,nB,dB)
    MN=from_bitsliced(mn,N); MD=from_bitsliced(md,N); AN=from_bitsliced(an,N); AD=from_bitsliced(ad,N)
    rmul_ok=all(Fraction(MN[i],MD[i])==Fraction(nums[i],dens[i])*Fraction(nums2[i],dens2[i]) for i in range(N))
    radd_ok=all(Fraction(AN[i],AD[i])==Fraction(nums[i],dens[i])+Fraction(nums2[i],dens2[i]) for i in range(N))
    w4 = rmul_ok and radd_ok
    print(f"  W4  GRADED RATIONAL (num/den each bit-sliced): rational * and + via the carrier == Fraction (reduce at readout): {w4}")

    # W5 [numbers]: packing density -- sub-byte grade-packing vs the u128 fixed lane (256 bits/rational)
    packed_bits=sum(grades)                                              # contiguous grade-packing: exactly Sigma grade
    fixed_bits=N*128                                                     # the frozen u128 lane (per integer)
    subbyte=sum(1 for g in grades if g<8)
    w5 = packed_bits < fixed_bits
    print(f"\n  W5  [numbers] PACKING ({N} integers): grade-packed = {packed_bits} bits  vs  u128 fixed lane = {fixed_bits} bits"
          f"  ({fixed_bits/packed_bits:.1f}x denser); {subbyte}/{N} values are SUB-BYTE (grade<8, impossible to pack in the 8-bit limb)")

    # W6: GradedStore -- the resident contiguous sub-byte value store (Δ-Ψ-forest b). Append varied-grade rationals,
    # value() round-trips exact; the resident bits = Sigma grade (sub-byte), vs the u128 fixed lane.
    GS=GradedStore(); rats=[(int(rng.integers(0,1<<g)), int(rng.integers(1,1<<g))) for g in grades]
    for n,d in rats: GS.append(n,d)
    rt=all(GS.value(i)==Fraction(rats[i][0],rats[i][1]) for i in range(len(rats)))
    store_bits=GS.bits(); fixed=len(rats)*256                            # u128 num + u128 den per rational = 256 bits
    w6 = rt and (store_bits < fixed)
    print(f"\n  W6  GradedStore (Δ-Ψ-forest b): {len(rats)} rationals append+value round-trip exact: {rt}; resident value")
    print(f"      bits = {store_bits} (sub-byte packed, Sigma grade) vs u128 lanes {fixed} ({fixed/store_bits:.1f}x denser)")

    # W7: combine_batch (Δ-Ψ-forest c) -- a BATCH of N independent same-op rational combines in ONE bit-sliced SWAR pass
    M=128; lN=[int(rng.integers(0,1<<6)) for _ in range(M)]; lD=[int(rng.integers(1,1<<6)) for _ in range(M)]
    rN=[int(rng.integers(0,1<<6)) for _ in range(M)]; rD=[int(rng.integers(1,1<<6)) for _ in range(M)]
    mul=combine_batch(1, lN,lD,rN,rD); add=combine_batch(0, lN,lD,rN,rD)
    mul_ok=all(Fraction(*mul[i])==Fraction(lN[i],lD[i])*Fraction(rN[i],rD[i]) for i in range(M))
    add_ok=all(Fraction(*add[i])==Fraction(lN[i],lD[i])+Fraction(rN[i],rD[i]) for i in range(M))
    w7 = mul_ok and add_ok
    print(f"\n  W7  combine_batch (Δ-Ψ-forest c): {M} independent rational combines in ONE bit-sliced SWAR pass --")
    print(f"      mul-batch == Fraction: {mul_ok}; add-batch == Fraction: {add_ok} (per-bit-plane, no per-node loop): {w7}")

    # W8: UNSIGNED subtraction on the carrier (the carrier stays unsigned; sign is a normalization/readout gauge, NOT
    # carried -- the conductance/throughput domain's differences are monotone, results >= 0). bs_sub + q_sub, exact.
    hi=[max(a,b) for a,b in zip([int(rng.integers(0,1<<g)) for g in grades], [int(rng.integers(0,1<<g)) for g in grades])]
    lo=[int(rng.integers(0,h+1)) for h in hi]                            # lo <= hi (a>=b: the monotone-difference domain)
    pa,_=to_bitsliced(hi); pb,_=to_bitsliced(lo); diff,bor=bs_sub(pa,pb); D=from_bitsliced(diff,N)
    sub_ok = all(D[i]==hi[i]-lo[i] for i in range(N)) and int(bor.sum())==0   # a>=b -> exact, borrow 0 (no sign needed)
    pr=[int(rng.integers(0,1<<6)) for _ in range(40)]; dr=[int(rng.integers(1,1<<6)) for _ in range(40)]
    rats=[ (Fraction(pr[i],dr[i]), Fraction(int(rng.integers(0,pr[i]+1)), dr[i])) for i in range(40) ]   # a>=b
    rat_ok=all(q_sub(a,b)==a-b for a,b in rats)
    w8 = sub_ok and rat_ok
    print(f"\n  W8  UNSIGNED subtract on the carrier (sign = normalization/readout, NOT carried): bs_sub == a-b for a>=b "
          f"(borrow 0): {sub_ok}; q_sub (rational a-b via the carrier) == Fraction: {rat_ok} -- ÷ is native (swap), so -")
    print(f"      is the only added additive-inverse (no sign-magnitude): {w8}")

    # W9: graded RATIONAL threaded as DEVICE plane-tuples (gr_*) -- a multi-op computation with NO host Fraction
    # between ops (recip = plane swap), == Fraction; the on-device-resident solve form (Δ-Ω-onegraph brick 4).
    fa, fb, fc = Fraction(3,7), Fraction(5,11), Fraction(2,9)
    dev = gr_read(gr_mul(gr_lift(fb), gr_recip(gr_add(gr_lift(fa), gr_lift(fc)))))    # fb / (fa+fc), device-resident
    w9 = dev == fb / (fa + fc)
    print(f"\n  W9  graded RATIONAL as device planes (gr_add/gr_mul/gr_recip=swap, no host Fraction between ops) == "
          f"Fraction: {dev} == {fb/(fa+fc)}: {w9}")

    ok=w1 and w2 and w3 and w4 and w5 and w6 and w7 and w8 and w9
    print(f"\n  {'PASS' if ok else 'FAIL'} — the graded sub-byte carrier: a value is carried at its GRADE (1 bit up), bit-sliced")
    print(f"  so arithmetic (ripple-carry add, ripple-borrow SUB, shift-and-add mul, combine_batch) is per-bit SWAR -- 64")
    print(f"  values/word; GradedStore = the device sub-byte VALUE store. u128 was a frozen coordinate; the grade is the")
    print(f"  geometry. UNSIGNED (sign normalizes away); ÷ native (swap). WIRED: GradedStore=forest(b); combine_batch=eval(c); q_sub=onegraph diffs.")
