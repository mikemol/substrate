"""tests/test_baseline.py — the regression gate.

Captures current `compression_stats` numbers under all input modes on
fixed corpora. Any refactor that changes these numbers (or fails to
reproduce them) reveals a brick-port that lost information.

Used by the 20-slice plan as the verification gate after every port.

Run via:
    cd scratch/eliza && python -m tests.test_baseline
or:
    cd scratch/eliza && python -m pytest tests/test_baseline.py
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

# Ensure scratch/eliza/ is on path for `import eliza`.
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))

from eliza.engine import Engine  # noqa: E402
from eliza.router import crumb, nibble  # noqa: E402

# --- Fixtures --------------------------------------------------------------

# Use the project's own source as a stable text corpus (deterministic
# byte sequence regardless of which machine runs the test).
TEXT_SOURCE = ROOT / "eliza" / "engine.py"
ELF_SOURCE = "/bin/true"
ZEROS_SIZE = 5000


def text_bytes(n: int) -> bytes:
    """N bytes of stable text from the project's engine.py source."""
    with open(TEXT_SOURCE, "rb") as f:
        data = f.read()
    # Repeat if necessary to reach n bytes.
    while len(data) < n:
        data = data + data
    return data[:n]


def elf_bytes(n: int) -> bytes:
    with open(ELF_SOURCE, "rb") as f:
        return f.read(n)


def zeros_bytes(n: int) -> bytes:
    return b"\x00" * n


# --- Modes -----------------------------------------------------------------

MODES = {
    "bits": dict(vocab_size=2, router=None),
    "crumbs": dict(vocab_size=4, router=crumb),
    "nibbles": dict(vocab_size=16, router=nibble),
    "binary": dict(vocab_size=256, router=None),
}


def bits_iter(data: bytes):
    for byte in data:
        for i in range(8):
            yield "1" if (byte >> (7 - i)) & 1 else "0"


def crumb_iter(data: bytes):
    prev = None
    for byte in data:
        for i in range(8):
            bit = (byte >> (7 - i)) & 1
            if prev is not None:
                yield chr((prev << 1) | bit)
            prev = bit


def nibble_iter(data: bytes):
    for byte in data:
        yield chr((byte >> 4) & 0xF)
        yield chr(byte & 0xF)


def binary_iter(data: bytes):
    for byte in data:
        yield chr(byte)


SYM_ITERS = {
    "bits": bits_iter,
    "crumbs": crumb_iter,
    "nibbles": nibble_iter,
    "binary": binary_iter,
}


# --- Baseline capture ------------------------------------------------------


def run_engine(data: bytes, mode: str) -> dict:
    """Run the engine over the data in the given mode; return stats."""
    cfg = MODES[mode]
    kwargs = dict(grammar_every=1, vocab_size=cfg["vocab_size"])
    if cfg["router"] is not None:
        kwargs["router"] = cfg["router"]
    eng = Engine(**kwargs)
    for ch in SYM_ITERS[mode](data):
        eng.step(ch)
    return eng.compression_stats()


# Keys we expect every mode to surface. Used to verify the dict shape
# after refactoring. Refactors should NEVER remove these keys.
EXPECTED_KEYS = {
    "symbols",
    "raw_bits_per_symbol",
    "bits_per_symbol",            # trigram
    "compressed_bits",
    "ratio",
    "grammar_bits_per_symbol",
    "grammar_total_bits",
    "grammar_ratio",
    "grammar_n_rules",
    "gt_bits_per_symbol",
    "gt_total_bits",
    "gt_ratio",
    "gt6_bits_per_symbol",
    "gt6_total_bits",
    "gt6_ratio",
    "gtV4a_total_bits",
    "gtV4d_total_bits",
    "orbit_cycling_rate",
    "huffman_total_bits",
    "huffman_ratio",
    "orbit_huffman_total_bits",
    "orbit_huffman_ratio",
    "geo_total_bits",
    "geo_ratio",
    "geo_n_rules",
    "coalg_total_bits",
    "coalg_bits_per_slot",
    "coalg_slot_ratio",
    "coalg_n_contexts",
}


def dict_signature(d: dict) -> str:
    """Stable hash of a stats dict (rounds floats; sorts keys)."""

    def normalise(v):
        if isinstance(v, float):
            # Round to 6 sig figs to absorb arithmetic-coding noise.
            return f"{v:.6g}"
        if isinstance(v, dict):
            return {k: normalise(v[k]) for k in sorted(v)}
        if isinstance(v, (list, tuple)):
            return [normalise(x) for x in v]
        return repr(v)

    payload = json.dumps({k: normalise(d[k]) for k in sorted(d)}, sort_keys=True)
    return hashlib.sha256(payload.encode()).hexdigest()[:16]


# --- Main ------------------------------------------------------------------


def capture_baseline(size: int = 5000) -> dict:
    """Capture stats for every (corpus, mode) at the given size."""
    corpora = {
        "text": text_bytes(size),
        "elf": elf_bytes(size),
        "zeros": zeros_bytes(size),
    }
    out = {}
    for corpus_name, data in corpora.items():
        for mode in MODES:
            stats = run_engine(data, mode)
            key = f"{corpus_name}-{mode}-{size}B"
            # Filter to expected keys for the regression check; ignore
            # extra keys that may appear (e.g., per-orbit dicts).
            filtered = {k: stats[k] for k in EXPECTED_KEYS if k in stats}
            out[key] = {
                "n_keys_present": len(filtered),
                "signature": dict_signature(filtered),
                "selected_floats": {
                    k: filtered[k] for k in (
                        "gt_total_bits",
                        "grammar_n_rules",
                        "coalg_total_bits",
                        "ratio",
                    ) if k in filtered
                },
            }
    return out


if __name__ == "__main__":
    print("Capturing baseline at 5KB across (text/elf/zeros) × (bits/crumbs/nibbles/binary)...")
    baseline = capture_baseline(size=5000)
    # Write to file for the gate to read on later runs.
    out_path = HERE / "baseline_5KB.json"
    with open(out_path, "w") as f:
        json.dump(baseline, f, indent=2)
    print(f"Wrote {out_path}")
    for k, v in baseline.items():
        print(f"  {k}: sig={v['signature']}  keys={v['n_keys_present']}  "
              f"gt={v['selected_floats'].get('gt_total_bits', '?'):.0f}  "
              f"rules={v['selected_floats'].get('grammar_n_rules', '?')}")
