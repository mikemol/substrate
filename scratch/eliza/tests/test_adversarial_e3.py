"""tests/test_adversarial_e3.py — pathological corpora for U-arc (E3).

Each corpus is designed to bias one factor of the RuleAction algebra
A = V₄ × AffineProjection × F₂Patch × SpanCoupling.

The U-arc capstone's text/ELF/zeros sweep found that no tested mode
beat greedy on those corpora — bounded claim per
[[negative-findings-corpus-bound]]. This test asks the complementary
question: do the factors deliver on corpora SPECIFICALLY DESIGNED
to make them shine?

If the answer is YES on the targeted corpus, the factor is empirically
load-bearing somewhere — just not on standard mixed corpora.

If the answer is NO even on the targeted corpus, the factor's
implementation may have a structural issue (the chain-walk transform
might destroy the byte-level bias, or the cost-gate / heuristic
threshold may be too conservative).

Corpora:
  * phase_biased   — long template recurring with shifted start.
  * length_biased  — shared-prefix vocabulary with varying lengths.
  * patch1_biased  — template recurring with single-byte variants.
  * patchk_biased  — template recurring with k-byte variants.
  * span_biased    — interleaved portions of two templates.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))

from eliza.gpu_codec_v6 import encode, decode    # noqa: E402


# --- Corpus constructors ---------------------------------------------

def phase_biased(n_bytes: int = 1024, seed: int = 42) -> bytes:
    """Long shared template recurring at varied start offsets.

    Each instance: <random prefix 0..7 bytes> + TEMPLATE + <random suffix>.
    The TEMPLATE byte string is the same; only its position varies.
    Affine/phase factor should find TEMPLATE as a rule and use phase
    to slide into it across the random prefixes.
    """
    rng = random.Random(seed)
    template = bytes(rng.choices(range(256), k=24))
    out = bytearray()
    while len(out) < n_bytes:
        pre = bytes(rng.choices(range(256), k=rng.randint(0, 7)))
        post = bytes(rng.choices(range(256), k=rng.randint(0, 4)))
        out.extend(pre + template + post)
    return bytes(out[:n_bytes])


def length_biased(n_bytes: int = 1024, seed: int = 43) -> bytes:
    """Shared-prefix vocabulary: chunks of varying lengths sharing
    the same starting bytes.

    Encoder should grow rules for the prefixes; affine length_mask
    lets each instance take just the prefix it needs.
    """
    rng = random.Random(seed)
    base = bytes(rng.choices(range(256), k=32))
    out = bytearray()
    while len(out) < n_bytes:
        k = rng.randint(4, 32)
        out.extend(base[:k])
    return bytes(out[:n_bytes])


def patch1_biased(n_bytes: int = 1024, seed: int = 44) -> bytes:
    """Template recurring with single-byte variants.

    Each instance is TEMPLATE with exactly one byte flipped.
    Patch1 factor should encode each as (rule, patch_idx, replacement).
    """
    rng = random.Random(seed)
    template = bytes(rng.choices(range(256), k=16))
    out = bytearray()
    while len(out) < n_bytes:
        v = bytearray(template)
        idx = rng.randint(0, len(v) - 1)
        v[idx] ^= rng.randint(1, 255)
        out.extend(bytes(v))
    return bytes(out[:n_bytes])


def patchk_biased(n_bytes: int = 1024, seed: int = 45, k: int = 3) -> bytes:
    """Template recurring with k-byte variants.

    Tests the patchk factor (currently decoder-only; encoder does not
    activate). Stored as ground-truth corpus for future encoder
    activation.
    """
    rng = random.Random(seed)
    template = bytes(rng.choices(range(256), k=24))
    out = bytearray()
    while len(out) < n_bytes:
        v = bytearray(template)
        idxs = rng.sample(range(len(v)), k)
        for i in idxs:
            v[i] ^= rng.randint(1, 255)
        out.extend(bytes(v))
    return bytes(out[:n_bytes])


def span_biased(n_bytes: int = 1024, seed: int = 46) -> bytes:
    """Interleaved portions of two templates A and B.

    Each instance: alternating 4-byte chunks of A and B over 16 bytes.
    Span factor should encode the interleaving as (rule_A, rule_B,
    overlap_mask).
    """
    rng = random.Random(seed)
    A = bytes(rng.choices(range(256), k=16))
    B = bytes(rng.choices(range(256), k=16))
    out = bytearray()
    while len(out) < n_bytes:
        w = bytearray(16)
        for i in range(16):
            chunk = (i // 4) & 1
            w[i] = (A if chunk == 0 else B)[i]
        out.extend(bytes(w))
    return bytes(out[:n_bytes])


def random_baseline(n_bytes: int = 1024, seed: int = 47) -> bytes:
    """Incompressible random — control for the sweep."""
    rng = random.Random(seed)
    return bytes(rng.choices(range(256), k=n_bytes))


# --- Sweep ----------------------------------------------------------

CORPORA = {
    "phase_biased":   phase_biased,
    "length_biased":  length_biased,
    "patch1_biased":  patch1_biased,
    "patchk_biased":  patchk_biased,
    "span_biased":    span_biased,
    "random":         random_baseline,
}

MODES = [
    ("identity",     dict()),
    ("+ affine",     dict(speculate_affine=True)),
    ("+ patch1",     dict(speculate_patch1=True)),
    ("+ integrated", dict(speculate_integrated=True)),
    ("+ alias",      dict(speculate_alias=True)),
]


def main(size: int = 1024) -> int:
    print(f"=== Adversarial (E3) sweep — {size}B per corpus ===\n")
    header = (f"{'corpus':<18}{'mode':<16}{'b/byte':>9}"
              f"  {'affine':>7}{'patch1':>8}{'alias':>7}  {'ok':>5}")
    print(header)
    any_benefit = False
    for cname, ctor in CORPORA.items():
        data = ctor(n_bytes=size)
        base_bpb = None
        for mname, kw in MODES:
            try:
                enc, stats = encode(data, **kw)
                dec = decode(enc)
                ok = dec == data
                bpb = 8 * len(enc) / len(data)
            except Exception as e:
                bpb = -1.0
                ok = False
                stats = {}
            if base_bpb is None:
                base_bpb = bpb
            delta = bpb - base_bpb if base_bpb > 0 else 0.0
            verdict = (
                "B" if delta < -0.05 else
                "R" if delta > 0.05 else
                "="
            )
            if verdict == "B":
                any_benefit = True
            print(f"{cname:<18}{mname:<16}{bpb:>8.3f}{verdict}"
                  f"  {stats.get('n_affine_emissions', 0):>7}"
                  f"{stats.get('n_patch1_emissions', 0):>8}"
                  f"{stats.get('n_alias_defines', 0):>7}"
                  f"  {'OK' if ok else 'FAIL':>5}")
        print()
    print(("BENEFIT observed on at least one (corpus, mode) pair."
           if any_benefit else
           "No mode beat baseline on any tested corpus."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
