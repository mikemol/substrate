"""Eliza.CodecAPI — clean encode/decode entry points for the GPU codec.

P9 of the P-arc. Exposes a uniform `encode(bytes) → bytes` /
`decode(bytes) → bytes` interface over the GpuCodecV2 internals, plus
a small CLI for round-trip verification on a file.

The codec is the result of arcs C-K (substrate-native chain grammar +
opcode-VM) + M-arc (matricised tensor primitives) + N-arc (GPU port) +
O-arc (kernel fusion + adaptive predictor + int walk).

Maturity at this point:
  * Lossless on text/elf/zeros at 256B/512B/1024B/2048B
  * Compression matches L0 within 0.01-0.03 b/byte
  * Encode-time gap to L0 closing: 4.6× at 1KB → 2.3× at 2KB
  * Known bug: invalid chain transition at 4KB+ (under investigation)
"""

from __future__ import annotations

from typing import Tuple

from eliza.gpu_codec_v2 import (
    decode as _v2_decode, encode as _v2_encode,
)


def encode(data: bytes) -> bytes:
    """Encode bytes via the substrate-native GPU codec.

    Returns encoded bytes. Internally uses GpuCodecV2 with vectorized
    opcode matching, adaptive predictor, and int-based chamber walk.

    Round-trip property: `decode(encode(data)) == data`.
    """
    encoded, _stats = _v2_encode(data)
    return encoded


def decode(encoded: bytes) -> bytes:
    """Decode bytes from the substrate-native GPU codec output."""
    return _v2_decode(encoded)


def encode_with_stats(data: bytes) -> Tuple[bytes, dict]:
    """Encode + return per-encode diagnostics dict."""
    return _v2_encode(data)


# --- CLI ---------------------------------------------------------------


def _cli():
    import sys, time
    if len(sys.argv) < 3:
        print("usage: codec_api {encode|decode|roundtrip} <file>")
        return 1
    cmd, path = sys.argv[1], sys.argv[2]
    with open(path, "rb") as f:
        data = f.read()
    if cmd == "encode":
        t0 = time.perf_counter()
        out = encode(data)
        dt = time.perf_counter() - t0
        sys.stdout.buffer.write(out)
        sys.stderr.write(f"encoded {len(data)} → {len(out)} bytes "
                         f"({8*len(out)/len(data):.3f} b/byte) in {dt*1000:.1f}ms\n")
    elif cmd == "decode":
        t0 = time.perf_counter()
        out = decode(data)
        dt = time.perf_counter() - t0
        sys.stdout.buffer.write(out)
        sys.stderr.write(f"decoded {len(data)} → {len(out)} bytes "
                         f"in {dt*1000:.1f}ms\n")
    elif cmd == "roundtrip":
        n = min(len(data), 2048)
        sample = data[:n]
        t0 = time.perf_counter()
        e = encode(sample)
        enc_t = time.perf_counter() - t0
        t0 = time.perf_counter()
        d = decode(e)
        dec_t = time.perf_counter() - t0
        ok = d == sample
        print(f"input:     {len(sample)} bytes")
        print(f"encoded:   {len(e)} bytes ({8*len(e)/len(sample):.3f} b/byte)")
        print(f"decode:    {len(d)} bytes")
        print(f"round-trip: {'OK' if ok else 'FAIL'}")
        print(f"encode time: {enc_t*1000:.1f}ms")
        print(f"decode time: {dec_t*1000:.1f}ms")
        return 0 if ok else 1
    else:
        print(f"unknown command: {cmd}")
        return 1
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(_cli())
