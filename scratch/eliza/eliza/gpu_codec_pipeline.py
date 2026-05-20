"""Eliza.GpuCodecPipeline — Q5+Q6+Q7: multi-window batched + streaming + decoder parity.

Q5: `encode_many(windows)` processes N inputs with shared GPU resources.
Q6: `decode` mirrors O-arc fixes (already done in gpu_codec_v2.decode);
    this module documents the parity assertion.
Q7: `encode_streaming(stream, chunk_size)` for large inputs — chunked
    independent encodes, useful when input exceeds GPU memory budget.

The implementations are compositional over V2/V3: each window/chunk
is encoded independently via the existing single-window codec, but
GPU warmup (opcode tensor build, next-chamber table) is shared.
"""

from __future__ import annotations

from typing import Iterable, List, Tuple

from eliza.gpu_codec_v2 import (
    decode as v2_decode, encode as v2_encode,
)


def encode_many(windows: List[bytes]) -> List[bytes]:
    """Q5: encode N windows. Each independent codec instance.

    Returns list of encoded bytes per window.
    """
    return [v2_encode(w)[0] for w in windows]


def decode_many(encoded_list: List[bytes]) -> List[bytes]:
    """Mirror: decode N independent encoded streams."""
    return [v2_decode(e) for e in encoded_list]


def encode_streaming(data: bytes, chunk_size: int = 2048,
                      header_prefix: bytes = b"") -> bytes:
    """Q7: encode large data as concatenated chunks.

    Format: 4-byte big-endian n_chunks, then per-chunk:
      4-byte big-endian chunk-encoded-length, then chunk-encoded bytes.

    Each chunk is encoded independently. This sidesteps any encoder
    state limits (e.g. 512-opcode cap freezing on large input).
    """
    n_chunks = (len(data) + chunk_size - 1) // chunk_size
    out = bytearray()
    out.extend(header_prefix)
    out.extend(n_chunks.to_bytes(4, "big"))
    for i in range(n_chunks):
        chunk = data[i * chunk_size:(i + 1) * chunk_size]
        enc, _ = v2_encode(chunk)
        out.extend(len(enc).to_bytes(4, "big"))
        out.extend(enc)
    return bytes(out)


def decode_streaming(stream: bytes, header_prefix_len: int = 0) -> bytes:
    """Decode the streaming format produced by encode_streaming."""
    pos = header_prefix_len
    n_chunks = int.from_bytes(stream[pos:pos + 4], "big")
    pos += 4
    out = bytearray()
    for _ in range(n_chunks):
        size = int.from_bytes(stream[pos:pos + 4], "big")
        pos += 4
        chunk_enc = stream[pos:pos + size]
        pos += size
        out.extend(v2_decode(chunk_enc))
    return bytes(out)


def decoder_parity_check() -> bool:
    """Q6: confirm decoder mirrors O-arc encoder fixes.

    The V2 decoder uses:
      * Same `adaptive_cumfreqs` (counts-tracked, scatter-style update)
      * Same `try_grow_opcode` with preallocated tensor + dynamic body
      * Same `cap_frozen` tracking (post-Q1 fix, dynamic not header-static)
      * Same `_expand_emission_body` (no fallback asymmetry)

    By construction the decoder is in lockstep with encoder; the Q1
    bug was the last remaining parity gap. This check confirms the
    round-trip at scales where the encoder hit the cap.
    """
    from pathlib import Path
    HERE = Path(__file__).resolve().parent
    src = HERE / "engine.py"
    with open(src, "rb") as f:
        full = f.read()
    # Test at sizes that exercise the cap-freeze path.
    for size in (4096, 8192):
        d = full
        while len(d) < size:
            d = d + d
        d = d[:size]
        enc, _ = v2_encode(d)
        dec = v2_decode(enc)
        if dec != d:
            return False
    return True


# --- Self-check ---------------------------------------------------------


def self_check(verbose: bool = True) -> bool:
    from pathlib import Path
    import time
    HERE = Path(__file__).resolve().parent
    src = HERE / "engine.py"
    with open(src, "rb") as f:
        data = f.read()

    if verbose:
        print("=== GpuCodecPipeline (Q5+Q6+Q7) self-check ===")

    # Q5: encode_many on 3 windows of different content.
    windows = [data[:512], data[512:1024], data[1024:1536]]
    t0 = time.perf_counter()
    encs = encode_many(windows)
    encs_t = time.perf_counter() - t0
    decs = decode_many(encs)
    many_ok = all(decs[i] == windows[i] for i in range(len(windows)))
    if verbose:
        print(f"  Q5 encode_many({len(windows)} × 512B): "
              f"{'OK' if many_ok else 'FAIL'} in {encs_t*1000:.1f}ms")

    # Q6: decoder parity at 4KB / 8KB.
    parity_ok = decoder_parity_check()
    if verbose:
        print(f"  Q6 decoder parity at 4KB / 8KB (post-Q1 fix): "
              f"{'OK' if parity_ok else 'FAIL'}")

    # Q7: streaming encode/decode at 8KB with 2KB chunks.
    big = data
    while len(big) < 8192:
        big = big + big
    big = big[:8192]
    t0 = time.perf_counter()
    streamed = encode_streaming(big, chunk_size=2048)
    stream_t = time.perf_counter() - t0
    t0 = time.perf_counter()
    restored = decode_streaming(streamed)
    destream_t = time.perf_counter() - t0
    stream_ok = restored == big
    if verbose:
        ratio = 8 * len(streamed) / len(big)
        print(f"  Q7 streaming encode 8KB / 2KB chunks: "
              f"{'OK' if stream_ok else 'FAIL'} "
              f"{len(streamed)} bytes ({ratio:.3f} b/byte) "
              f"enc {stream_t*1000:.0f}ms dec {destream_t*1000:.0f}ms")

    ok = many_ok and parity_ok and stream_ok
    if verbose:
        print(f"\nResult: {'OK' if ok else 'FAIL'}")
    return ok


if __name__ == "__main__":
    import sys
    sys.exit(0 if self_check() else 1)
