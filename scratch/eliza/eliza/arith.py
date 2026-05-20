"""Eliza.Arith — range coder for real bit streams.

A standard 32-bit-state range coder. The Eliza compression pipeline
produces per-symbol probability distributions (via gt over the grammar);
this module turns those into actual bytes.

Encoder/decoder API: both take cumulative-frequency arrays per symbol
emission. The caller is responsible for building the cumfreqs from the
predictor's per-symbol probability, and for keeping encoder and decoder
in lockstep through the same Sequitur+gt model state.

Round-trip property: `RangeDecoder(RangeEncoder.encode(syms)).decode(...)
== syms` provided both sides receive the same `cumfreqs` at each step.
"""

from __future__ import annotations

from typing import List


# 32-bit state.
TOP = 0x100000000  # 2^32
HALF = TOP // 2     # 0x80000000
QUARTER = TOP // 4  # 0x40000000
THREE_Q = 3 * QUARTER  # 0xC0000000
MASK = TOP - 1      # 0xFFFFFFFF


class RangeEncoder:
    def __init__(self) -> None:
        self.low = 0
        self.high = MASK
        self.pending_bits = 0
        self._buf = 0
        self._buf_len = 0
        self._out = bytearray()

    def encode(self, cumfreqs: List[int], idx: int, total: int) -> None:
        """Encode the symbol at position `idx` given cumulative frequencies.
        cumfreqs[i] is the cumulative freq up to symbol i (cumfreqs[0]=0,
        cumfreqs[n]=total). The symbol's range is [cumfreqs[idx], cumfreqs[idx+1])."""
        rng = self.high - self.low + 1
        self.high = self.low + (rng * cumfreqs[idx + 1]) // total - 1
        self.low = self.low + (rng * cumfreqs[idx]) // total
        while True:
            if self.high < HALF:
                self._emit(0)
            elif self.low >= HALF:
                self._emit(1)
                self.low -= HALF
                self.high -= HALF
            elif self.low >= QUARTER and self.high < THREE_Q:
                self.pending_bits += 1
                self.low -= QUARTER
                self.high -= QUARTER
            else:
                return
            self.low = (self.low << 1) & MASK
            self.high = ((self.high << 1) | 1) & MASK

    def _emit(self, bit: int) -> None:
        self._push_bit(bit)
        opp = 1 - bit
        for _ in range(self.pending_bits):
            self._push_bit(opp)
        self.pending_bits = 0

    def _push_bit(self, bit: int) -> None:
        self._buf = (self._buf << 1) | bit
        self._buf_len += 1
        if self._buf_len == 8:
            self._out.append(self._buf)
            self._buf = 0
            self._buf_len = 0

    def finish(self) -> bytes:
        self.pending_bits += 1
        if self.low < QUARTER:
            self._emit(0)
        else:
            self._emit(1)
        # Pad to byte boundary.
        if self._buf_len > 0:
            self._buf <<= (8 - self._buf_len)
            self._out.append(self._buf)
            self._buf = 0
            self._buf_len = 0
        return bytes(self._out)


class RangeDecoder:
    def __init__(self, stream: bytes) -> None:
        self._stream = stream
        self._pos = 0
        self._buf = 0
        self._buf_len = 0
        self.low = 0
        self.high = MASK
        self.code = 0
        for _ in range(32):
            self.code = (self.code << 1) | self._read_bit()

    def _read_bit(self) -> int:
        if self._buf_len == 0:
            if self._pos < len(self._stream):
                self._buf = self._stream[self._pos]
                self._pos += 1
                self._buf_len = 8
            else:
                return 0
        bit = (self._buf >> 7) & 1
        self._buf = (self._buf << 1) & 0xFF
        self._buf_len -= 1
        return bit

    def decode(self, cumfreqs: List[int], total: int) -> int:
        """Determine and return the symbol index at the current code position,
        then narrow the interval. Caller passes the same cumfreqs/total as
        the encoder used at this step."""
        rng = self.high - self.low + 1
        value = ((self.code - self.low + 1) * total - 1) // rng
        # Binary-search for the symbol.
        lo, hi = 0, len(cumfreqs) - 2
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if cumfreqs[mid] <= value:
                lo = mid
            else:
                hi = mid - 1
        idx = lo
        self.high = self.low + (rng * cumfreqs[idx + 1]) // total - 1
        self.low = self.low + (rng * cumfreqs[idx]) // total
        while True:
            if self.high < HALF:
                pass
            elif self.low >= HALF:
                self.low -= HALF
                self.high -= HALF
                self.code -= HALF
            elif self.low >= QUARTER and self.high < THREE_Q:
                self.low -= QUARTER
                self.high -= QUARTER
                self.code -= QUARTER
            else:
                return idx
            self.low = (self.low << 1) & MASK
            self.high = ((self.high << 1) | 1) & MASK
            self.code = ((self.code << 1) | self._read_bit()) & MASK
