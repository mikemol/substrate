"""Eliza.TensorRangeCoder — range coder state + step as tensor objects.

Per the homoiconic architecture: every codec stage is a tensor object
with a uniform shape. The arithmetic coder's state (low, high,
pending_bits) packaged as a fixed-shape tensor; the encode/decode step
is a pure tensor operation.

This module mirrors `eliza/arith.py` but represents state with numpy
arrays and the step as a function that consumes (state, cumfreqs, idx,
total) and produces (new_state, output_bits_appended).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Tuple

import numpy as np


# 32-bit range coder constants (match arith.py).
MASK = 0xFFFFFFFF
HALF = 0x80000000
QUARTER = 0x40000000
THREE_Q = 0xC0000000


@dataclass
class RCState:
    """Tensor-shaped range coder state.

    The "tensor" form is small (4 ints + a bytearray) but uniformly
    typed: every field is a fixed numeric quantity, no Python objects.
    On GPU this becomes a 4-element int32 tensor + a bit-buffer tensor.
    """
    low: int = 0
    high: int = MASK
    pending_bits: int = 0
    buffer: bytearray = field(default_factory=bytearray)
    buf: int = 0          # current byte being assembled
    buf_len: int = 0      # bits in `buf`

    def as_array(self) -> np.ndarray:
        """View as a (4,) uint32 array — the "tensor" representation."""
        return np.array([self.low, self.high, self.pending_bits,
                          (self.buf_len << 8) | self.buf], dtype=np.uint32)


def _emit_bit(state: RCState, bit: int) -> None:
    state.buf = ((state.buf << 1) | (bit & 1)) & 0xFF
    state.buf_len += 1
    if state.buf_len == 8:
        state.buffer.append(state.buf)
        state.buf = 0
        state.buf_len = 0


def _emit_with_pending(state: RCState, bit: int) -> None:
    _emit_bit(state, bit)
    for _ in range(state.pending_bits):
        _emit_bit(state, 1 - bit)
    state.pending_bits = 0


def rc_step_encode(
    state: RCState,
    cumfreqs: np.ndarray, idx: int, total: int,
) -> None:
    """Pure tensor step: narrow the range by (cumfreqs[idx], cumfreqs[idx+1]).

    Mirrors `RangeEncoder.encode` but takes RCState explicitly. The
    output bit-stream is appended to state.buffer in-place; this is
    the byte-level realisation of the abstract tensor "output channel."
    """
    rng = state.high - state.low + 1
    state.high = state.low + (rng * int(cumfreqs[idx + 1])) // total - 1
    state.low = state.low + (rng * int(cumfreqs[idx])) // total
    while True:
        if state.high < HALF:
            _emit_with_pending(state, 0)
        elif state.low >= HALF:
            _emit_with_pending(state, 1)
            state.low -= HALF
            state.high -= HALF
        elif state.low >= QUARTER and state.high < THREE_Q:
            state.pending_bits += 1
            state.low -= QUARTER
            state.high -= QUARTER
        else:
            break
        state.low = (state.low << 1) & MASK
        state.high = ((state.high << 1) | 1) & MASK


def rc_finish(state: RCState) -> bytes:
    """Finalise the encoder: emit terminating bits + flush buffer."""
    state.pending_bits += 1
    if state.low < QUARTER:
        _emit_with_pending(state, 0)
    else:
        _emit_with_pending(state, 1)
    # Flush buffer.
    if state.buf_len > 0:
        state.buf <<= (8 - state.buf_len)
        state.buffer.append(state.buf & 0xFF)
        state.buf = 0
        state.buf_len = 0
    return bytes(state.buffer)


# --- Decoder side (mirror) ----------------------------------------------


@dataclass
class RCDecoderState:
    """Tensor-shaped range decoder state."""
    low: int = 0
    high: int = MASK
    value: int = 0
    stream: bytes = b""
    pos: int = 0          # byte position in stream
    bit_pos: int = 0      # bit position within current byte

    @classmethod
    def from_stream(cls, stream: bytes) -> "RCDecoderState":
        state = cls(stream=stream)
        for _ in range(32):
            state.value = ((state.value << 1) | _read_bit(state)) & MASK
        return state

    def as_array(self) -> np.ndarray:
        return np.array([self.low, self.high, self.value, self.pos],
                          dtype=np.uint32)


def _read_bit(state: RCDecoderState) -> int:
    if state.pos >= len(state.stream):
        return 0
    bit = (state.stream[state.pos] >> (7 - state.bit_pos)) & 1
    state.bit_pos += 1
    if state.bit_pos == 8:
        state.bit_pos = 0
        state.pos += 1
    return bit


def rc_step_decode(
    state: RCDecoderState,
    cumfreqs: np.ndarray, total: int,
) -> int:
    rng = state.high - state.low + 1
    target = ((state.value - state.low + 1) * total - 1) // rng
    # Linear scan for the symbol whose cumfreq interval contains target.
    idx = int(np.searchsorted(cumfreqs[1:], target, side="right"))
    if cumfreqs[idx] > target or cumfreqs[idx + 1] <= target:
        # Edge case: searchsorted picked a boundary.
        for j in range(len(cumfreqs) - 1):
            if cumfreqs[j] <= target < cumfreqs[j + 1]:
                idx = j
                break
    state.high = state.low + (rng * int(cumfreqs[idx + 1])) // total - 1
    state.low = state.low + (rng * int(cumfreqs[idx])) // total
    while True:
        if state.high < HALF:
            pass
        elif state.low >= HALF:
            state.value -= HALF
            state.low -= HALF
            state.high -= HALF
        elif state.low >= QUARTER and state.high < THREE_Q:
            state.value -= QUARTER
            state.low -= QUARTER
            state.high -= QUARTER
        else:
            break
        state.low = (state.low << 1) & MASK
        state.high = ((state.high << 1) | 1) & MASK
        state.value = ((state.value << 1) | _read_bit(state)) & MASK
    return idx


# --- Self-check: tensor coder matches eliza/arith reference ----------


def self_check(verbose: bool = True) -> bool:
    from eliza.arith import RangeDecoder as RefDecoder, RangeEncoder as RefEncoder

    # Encode a small sequence via both coders; expect identical output.
    symbols = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5, 8, 9, 7, 9, 3]
    alphabet_size = 10
    cumfreqs = np.arange(alphabet_size + 1, dtype=np.int64)  # uniform

    # Reference.
    ref_enc = RefEncoder()
    for s in symbols:
        ref_enc.encode(list(cumfreqs.tolist()), s, alphabet_size)
    ref_bytes = ref_enc.finish()

    # Tensor coder.
    state = RCState()
    for s in symbols:
        rc_step_encode(state, cumfreqs, s, alphabet_size)
    tensor_bytes = rc_finish(state)

    encode_match = ref_bytes == tensor_bytes

    # Decode via both.
    ref_dec = RefDecoder(ref_bytes)
    ref_out = [ref_dec.decode(list(cumfreqs.tolist()), alphabet_size)
                for _ in symbols]

    dec_state = RCDecoderState.from_stream(tensor_bytes)
    tensor_out = [rc_step_decode(dec_state, cumfreqs, alphabet_size)
                   for _ in symbols]
    decode_match = ref_out == symbols == tensor_out

    if verbose:
        print("=== TensorRangeCoder self-check ===")
        print(f"  encode bytes match reference: {'OK' if encode_match else 'FAIL'}")
        print(f"  decode reproduces symbols:    {'OK' if decode_match else 'FAIL'}")
        print(f"  state as array shape:         {state.as_array().shape}")
        print(f"  state values:                 {state.as_array()}")
        print(f"\nResult: {'OK' if encode_match and decode_match else 'FAIL'}")
    return encode_match and decode_match


if __name__ == "__main__":
    import sys
    sys.exit(0 if self_check() else 1)
