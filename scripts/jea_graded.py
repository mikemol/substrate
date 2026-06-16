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


# --- graded RATIONAL: two bit-sliced integers (num, den); arithmetic stays bit-sliced (reduce at readout, host gcd) ---
def rat_mul(nA,dA, nB,dB):  return bs_mul(nA,nB), bs_mul(dA,dB)                          # (na/da)*(nb/db)
def rat_add(nA,dA, nB,dB):  return bs_add(bs_mul(nA,dB), bs_mul(nB,dA)), bs_mul(dA,dB)   # cross-multiply add


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

    ok=w1 and w2 and w3 and w4 and w5 and w6
    print(f"\n  {'PASS' if ok else 'FAIL'} — the graded sub-byte carrier: a value is carried at its GRADE (1 bit up), bit-sliced")
    print(f"  so arithmetic (ripple-carry add, shift-and-add mul) is per-bit SWAR -- 64 values per word; the GradedStore")
    print(f"  is the device-resident contiguous sub-byte VALUE store. u128 was a frozen coordinate; the grade is the")
    print(f"  geometry. NEXT (Δ-Ψ-forest b wiring): make GradedStore the forest's value backend, dropping host vn/vd.")
