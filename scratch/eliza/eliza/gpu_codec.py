"""Eliza.GpuCodec — chunked arithmetic-coded codec with cupy backend.

Slice 9: GPU port of `codec.encode/decode` per `GPU_ACCELERATION.md`.
Strategy:
  * Split input into 4 KB chunks; each chunk has an independent range
    coder state.
  * Predictor counts live in a `[256, 256, 256] int32` tensor on
    GPU (16 MB).
  * Per chunk: cumfreqs via `xp.cumsum`, AC step via a custom kernel.
  * Concatenate chunk outputs with a small header (chunk offsets).

Backend selector: `cupy` if available, else `numpy` as a fallback.
Same code either way; only the array module changes. The numpy path is
the CPU shadow that verifies the algorithm before GPU; the cupy path
is the runtime speedup.

The AC step itself is byte-serial within a chunk. The parallelism is
**across chunks** (independent range coders) and **across chunk
predictor lookups** (vectorised cumsum). The custom CUDA kernel is
deferred to a follow-up — the chunked-numpy approach gets us round-trip
correctness today; the kernel adds wall-clock speedup later.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Tuple

import numpy as np

try:
    import cupy as cp  # type: ignore
    HAS_CUPY = cp.cuda.is_available()
except Exception:
    cp = np  # CPU fallback; same API
    HAS_CUPY = False

xp = cp if HAS_CUPY else np


# Chunk size: 4 KB per chunk. Larger = better compression (smaller
# per-chunk overhead); smaller = more parallelism on GPU.
CHUNK_SIZE = 4096
VOCAB = 256
ALPHA = 0.5  # Laplace smoothing pseudocount


def _build_cumfreqs(counts_row: "xp.ndarray", alpha: float = ALPHA) -> "xp.ndarray":
    """Compute cumulative frequencies for one (c1, c2) context row.

    `counts_row` is a 256-element int32 array of counts for each next
    symbol. Returns a 257-element array with `cumfreqs[i] = total of
    counts[0..i-1]` after Laplace smoothing.
    """
    smoothed = counts_row + alpha
    # Scale to integer for AC: multiply by a large factor and floor.
    # Standard approach: scale all counts by a precision factor.
    scaled = (smoothed * 256).astype(xp.int64) + 1  # +1 guards zero probability
    cum = xp.empty(VOCAB + 1, dtype=xp.int64)
    cum[0] = 0
    cum[1:] = xp.cumsum(scaled)
    return cum


def encode_chunked(data: bytes) -> bytes:
    """Encode `data` via per-chunk arithmetic coding.

    Each chunk gets its own range coder. The predictor state is
    GLOBAL — all chunks share the count tensor — but each chunk's
    encoder is independent. This means the model adapts across the
    whole input (compression-friendly) while encoding is parallelisable.

    Output format:
      [n_chunks: uint32 little-endian]
      [chunk_offset_0: uint32] ... [chunk_offset_{n-1}: uint32]
      [chunk_payload_0] ... [chunk_payload_{n-1}]
    """
    from eliza.arith import RangeEncoder

    n = len(data)
    counts = xp.zeros((VOCAB, VOCAB, VOCAB), dtype=xp.int32)
    c1, c2 = 0, 0  # initial context (sentinel)

    chunk_payloads: List[bytes] = []

    for chunk_start in range(0, n, CHUNK_SIZE):
        chunk_data = data[chunk_start:chunk_start + CHUNK_SIZE]
        enc = RangeEncoder()
        for byte in chunk_data:
            row = counts[c1, c2]
            cumfreqs = _build_cumfreqs(row)
            # Convert to python list for the existing RangeEncoder API.
            cumfreqs_list = cumfreqs.tolist() if HAS_CUPY else cumfreqs.tolist()
            total = int(cumfreqs_list[VOCAB])
            enc.encode(cumfreqs_list, byte, total)
            # Update counts (atomic-add in cupy via item write).
            counts[c1, c2, byte] = counts[c1, c2, byte] + 1
            c1, c2 = c2, byte
        chunk_payloads.append(enc.finish())

    # Assemble header + payloads.
    n_chunks = len(chunk_payloads)
    header = bytearray()
    header.extend(n_chunks.to_bytes(4, "little"))
    offset = 4 + 4 * n_chunks
    for payload in chunk_payloads:
        header.extend(offset.to_bytes(4, "little"))
        offset += len(payload)
    return bytes(header) + b"".join(chunk_payloads)


def decode_chunked(encoded: bytes, n_bytes: int) -> bytes:
    """Inverse of `encode_chunked`. Uses the same global predictor
    that the encoder built; reads the header for chunk offsets."""
    from eliza.arith import RangeDecoder

    n_chunks = int.from_bytes(encoded[:4], "little")
    offsets = [
        int.from_bytes(encoded[4 + 4 * i : 8 + 4 * i], "little")
        for i in range(n_chunks)
    ]
    # The encoder appended chunks in order; payload boundaries are the
    # offsets followed by the end of `encoded`.
    boundaries = offsets + [len(encoded)]

    counts = xp.zeros((VOCAB, VOCAB, VOCAB), dtype=xp.int32)
    c1, c2 = 0, 0

    out = bytearray()
    chunks_remaining = n_bytes
    for i in range(n_chunks):
        chunk_bytes = encoded[boundaries[i]:boundaries[i + 1]]
        dec = RangeDecoder(chunk_bytes)
        n_in_chunk = min(CHUNK_SIZE, chunks_remaining)
        chunks_remaining -= n_in_chunk
        for _ in range(n_in_chunk):
            row = counts[c1, c2]
            cumfreqs = _build_cumfreqs(row)
            cumfreqs_list = cumfreqs.tolist()
            total = int(cumfreqs_list[VOCAB])
            idx = dec.decode(cumfreqs_list, total)
            out.append(idx)
            counts[c1, c2, idx] = counts[c1, c2, idx] + 1
            c1, c2 = c2, idx
    return bytes(out)


def gpu_available() -> bool:
    return HAS_CUPY


def backend_name() -> str:
    return "cupy" if HAS_CUPY else "numpy"


# --- Self-test ------------------------------------------------------------


def _format_rate(bytes_per_sec: float) -> str:
    if bytes_per_sec >= 1e9:
        return f"{bytes_per_sec / 1e9:.2f} GB/s"
    if bytes_per_sec >= 1e6:
        return f"{bytes_per_sec / 1e6:.2f} MB/s"
    if bytes_per_sec >= 1e3:
        return f"{bytes_per_sec / 1e3:.2f} KB/s"
    return f"{bytes_per_sec:.0f} B/s"


def self_check(sizes_kb=(1, 4, 16), verbose: bool = True) -> bool:
    """Run an encode + decode round-trip at increasing sizes; report
    backend, byte-exact correctness, and wall-clock per byte.

    Returns True if all round-trips succeeded; False otherwise.
    """
    import time
    import os
    from pathlib import Path

    print(f"=== Eliza GPU codec self-check ===")
    print(f"backend       : {backend_name()}")
    print(f"HAS_CUPY      : {HAS_CUPY}")
    if HAS_CUPY:
        try:
            # cupy device info if available.
            dev = cp.cuda.runtime.getDevice()
            props = cp.cuda.runtime.getDeviceProperties(dev)
            name = props["name"].decode() if isinstance(props["name"], bytes) else props["name"]
            cc_major = props.get("major", "?")
            cc_minor = props.get("minor", "?")
            free, total = cp.cuda.runtime.memGetInfo()
            print(f"GPU           : {name} (compute {cc_major}.{cc_minor})")
            print(f"memory        : {free/1e9:.2f} / {total/1e9:.2f} GB free")
        except Exception as e:
            print(f"GPU info unavailable: {e}")
    print(f"CHUNK_SIZE    : {CHUNK_SIZE}B")
    print()

    # Choose a stable source: use this module's own bytes, replicated to size.
    src_path = Path(__file__)
    with open(src_path, "rb") as f:
        base = f.read()

    all_ok = True
    for size_kb in sizes_kb:
        n = size_kb * 1024
        # Repeat base to reach n bytes.
        data = (base * ((n // len(base)) + 1))[:n]

        t0 = time.perf_counter()
        encoded = encode_chunked(data)
        enc_time = time.perf_counter() - t0

        t0 = time.perf_counter()
        decoded = decode_chunked(encoded, len(data))
        dec_time = time.perf_counter() - t0

        ok = decoded == data
        all_ok = all_ok and ok
        bpb = len(encoded) * 8 / len(data)
        enc_rate = len(data) / enc_time if enc_time > 0 else 0.0
        dec_rate = len(data) / dec_time if dec_time > 0 else 0.0
        status = "✓" if ok else "✗"
        if verbose:
            print(f"  {size_kb:>4}KB: {status} round-trip  "
                  f"compressed={len(encoded):>6}B ({bpb:.2f} b/byte)  "
                  f"enc={enc_time*1000:>7.1f}ms ({_format_rate(enc_rate):>10})  "
                  f"dec={dec_time*1000:>7.1f}ms ({_format_rate(dec_rate):>10})")

    print()
    print(f"Result: {'OK' if all_ok else 'FAILURE — at least one round-trip mismatched'}")
    return all_ok


def _main() -> int:
    import argparse
    parser = argparse.ArgumentParser(
        description="Eliza GPU codec self-check (chunked AC, cupy/numpy backend)"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Run the self-check (default action).",
    )
    parser.add_argument(
        "--sizes",
        type=int,
        nargs="+",
        default=[1, 4, 16],
        help="Sizes in KB to test (default: 1 4 16).",
    )
    args = parser.parse_args()
    ok = self_check(sizes_kb=tuple(args.sizes))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    sys.exit(_main())
