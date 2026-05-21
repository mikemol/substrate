"""tests/test_substrate_crosscodec.py — Y-arc Y8: V7 vs external codecs.

Compares V7 (with two-stage lookahead) against structure-agnostic
codecs (gzip, lzma; zstd optional) on the substrate-internal corpora
from test_substrate_atlas.

Per the Y-arc hypothesis: substrate-aligned codec V7 should hold its
own or beat structure-agnostic codecs on substrate-internal data.
Per [[negative-findings-corpus-bound]]: bounded per (corpus, codec)
cell, no overclaim from any single comparison.
"""

from __future__ import annotations

import gzip
import lzma
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))

from eliza.gpu_codec_v7 import encode as v7_encode    # noqa: E402
from eliza.adaptive_opcode_codec import encode as l0_encode    # noqa: E402
from tests.test_substrate_atlas import CORPORA    # noqa: E402

try:
    import zstandard as zstd
    HAS_ZSTD = True
except ImportError:
    HAS_ZSTD = False


def compress_v7(data: bytes) -> bytes:
    enc, _ = v7_encode(data, speculate_basis=True)
    return enc


def compress_v7_id(data: bytes) -> bytes:
    enc, _ = v7_encode(data, speculate_basis=False)
    return enc


def compress_l0(data: bytes) -> bytes:
    enc, _ = l0_encode(data)
    return enc


def compress_gzip(data: bytes) -> bytes:
    return gzip.compress(data, compresslevel=9)


def compress_lzma(data: bytes) -> bytes:
    return lzma.compress(data, preset=9 | lzma.PRESET_EXTREME)


def compress_zstd(data: bytes) -> bytes:
    if not HAS_ZSTD:
        return b""
    return zstd.ZstdCompressor(level=22).compress(data)


CODECS = [
    ("V7 identity",   compress_v7_id),
    ("V7 two-stage",  compress_v7),
    ("L0 baseline",   compress_l0),
    ("gzip -9",       compress_gzip),
    ("lzma extreme",  compress_lzma),
]
if HAS_ZSTD:
    CODECS.append(("zstd -22", compress_zstd))


def main(size: int = 4096) -> int:
    print(f"=== Cross-codec on substrate corpora — {size}B ===\n")
    header = f"{'corpus':<22}" + "".join(f"{c[0]:>15}" for c in CODECS)
    print(header)

    for corpus_name, ctor in CORPORA.items():
        data = ctor(n_bytes=size)
        actual = len(data)
        row = [f"{corpus_name:<22}"]
        for codec_name, fn in CODECS:
            try:
                out = fn(data)
                bpb = 8 * len(out) / actual if actual else 0
                row.append(f"{bpb:>14.3f} ")
            except Exception as e:
                row.append(f"{'ERR':>14} ")
        print("".join(row))

    print()
    print(f"Sizes are b/byte (lower = better). Substrate-aligned codecs")
    print(f"(V7 / L0) vs structure-agnostic (gzip / lzma{'/zstd' if HAS_ZSTD else ''}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
