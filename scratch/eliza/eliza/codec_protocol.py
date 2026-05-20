"""Eliza.CodecProtocol — T5+T6+T9 portable opcode-stream protocol.

T5: header metadata captures codec version + opcode-set version so
    streams encoded by V2/V4/V5 are decodable by version-aware
    consumers.
T6: streaming + multi-window combined — encode a corpus as a
    sequence of independent chunks, each chunk batchable.
T9: clean encode/decode/CLI API.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Tuple

from eliza.gpu_codec_v2 import decode as v2_decode, encode as v2_encode
from eliza.gpu_codec_v4 import decode as v4_decode, encode as v4_encode
from eliza.gpu_codec_v5 import decode as v5_decode, encode as v5_encode


# --- T5: stream header (portable across codec versions) -------------


MAGIC = b"ELIZA"

# Codec version codes.
CODEC_V2 = 2
CODEC_V4 = 4
CODEC_V5 = 5

# Opcode-set version (the substrate-native + control-opcode set).
# Bumped when the initial opcode set changes incompatibly.
OPCODE_SET_VERSION = 1


@dataclass
class StreamHeader:
    """Top-level header for portable codec streams.

    Layout: MAGIC (5 bytes) + codec_version (1 byte) +
    opcode_set_version (1 byte) + n_chunks (4 bytes).
    """
    codec_version: int
    opcode_set_version: int
    n_chunks: int

    def to_bytes(self) -> bytes:
        out = bytearray()
        out.extend(MAGIC)
        out.append(self.codec_version & 0xFF)
        out.append(self.opcode_set_version & 0xFF)
        out.extend(self.n_chunks.to_bytes(4, "big"))
        return bytes(out)

    @classmethod
    def from_bytes(cls, data: bytes, pos: int = 0) -> Tuple["StreamHeader", int]:
        if data[pos:pos + len(MAGIC)] != MAGIC:
            raise ValueError("not an Eliza codec stream (magic mismatch)")
        pos += len(MAGIC)
        codec_v = data[pos]; pos += 1
        opc_v = data[pos]; pos += 1
        n_chunks = int.from_bytes(data[pos:pos + 4], "big"); pos += 4
        return cls(codec_v, opc_v, n_chunks), pos


# --- T6: combined streaming + multi-window encode -------------------


def _select_encoder(codec_version: int):
    if codec_version == CODEC_V2:
        return v2_encode, v2_decode
    if codec_version == CODEC_V4:
        return v4_encode, v4_decode
    if codec_version == CODEC_V5:
        return v5_encode, v5_decode
    raise ValueError(f"unknown codec version {codec_version}")


def encode(data: bytes, chunk_size: int = 2048,
            codec_version: int = CODEC_V2) -> bytes:
    """Encode `data` into a portable stream.

    Each chunk is encoded independently via the chosen codec version.
    The chunks are framed with per-chunk size prefixes.
    """
    encode_fn, _ = _select_encoder(codec_version)
    chunks = []
    for start in range(0, len(data), chunk_size):
        chunk = data[start:start + chunk_size]
        enc, _ = encode_fn(chunk)
        chunks.append(enc)

    header = StreamHeader(
        codec_version=codec_version,
        opcode_set_version=OPCODE_SET_VERSION,
        n_chunks=len(chunks),
    )
    out = bytearray()
    out.extend(header.to_bytes())
    for c in chunks:
        out.extend(len(c).to_bytes(4, "big"))
        out.extend(c)
    return bytes(out)


def decode(stream: bytes) -> bytes:
    """Decode an Eliza codec stream, version-aware."""
    header, pos = StreamHeader.from_bytes(stream)
    if header.opcode_set_version != OPCODE_SET_VERSION:
        raise ValueError(
            f"opcode-set version mismatch: stream has "
            f"{header.opcode_set_version}, codec expects "
            f"{OPCODE_SET_VERSION}"
        )
    _, decode_fn = _select_encoder(header.codec_version)
    out = bytearray()
    for _ in range(header.n_chunks):
        size = int.from_bytes(stream[pos:pos + 4], "big"); pos += 4
        chunk_enc = stream[pos:pos + size]; pos += size
        out.extend(decode_fn(chunk_enc))
    return bytes(out)


# --- Self-check ---------------------------------------------------------


def self_check(verbose: bool = True) -> bool:
    from pathlib import Path
    HERE = Path(__file__).resolve().parent
    src = HERE / "engine.py"
    with open(src, "rb") as f:
        data = f.read()[:4096]

    if verbose:
        print("=== CodecProtocol (T5+T6+T9) self-check ===")
    all_ok = True
    for cv in [CODEC_V2, CODEC_V4, CODEC_V5]:
        enc = encode(data, chunk_size=2048, codec_version=cv)
        dec = decode(enc)
        ok = dec == data
        all_ok = all_ok and ok
        if verbose:
            ratio = 8 * len(enc) / len(data)
            print(f"  codec_v{cv}: {len(enc)} bytes ({ratio:.3f} b/byte)  "
                  f"round-trip {'OK' if ok else 'FAIL'}")

    if verbose:
        print(f"\nResult: {'OK' if all_ok else 'FAIL'}")
    return all_ok


if __name__ == "__main__":
    import sys
    sys.exit(0 if self_check() else 1)
