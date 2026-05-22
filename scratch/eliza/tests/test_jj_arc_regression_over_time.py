"""JJ follow-up: per-position predictor cost over the chain walk.

Per user 2026-05-21: 'plot the regression over time'. Track
-log₂(P(emit_k | context_k)) at each chain position k, for
multiple Sylow-subset sizes. Visualises the warmup → steady-state
transition: early positions have zero-padded probes producing
Gibbs ringing; later positions have full probe context and stable
prediction.

Output: ASCII rolling-averaged cost curve per corpus per |S|,
saved CSV of per-position cost for IDE plotting.
"""

from __future__ import annotations

import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from eliza.sylow_prime_probe import joint_sylow_context
from tests.test_hh_arc_past_chain_mi import chain_symbols
from tests.test_substrate_atlas import CORPORA


def per_position_cost(chain: np.ndarray, primes: list,
                       alpha: float = 0.5) -> np.ndarray:
    """Per-position -log₂(P(emit | context)) under adaptive predictor."""
    N = 24
    if primes:
        ctx_stream = joint_sylow_context(chain, primes)
        n_ctx = int(ctx_stream.max()) + 1 if len(ctx_stream) else 1
        counts = np.zeros((n_ctx, N), dtype=np.float64)
    else:
        ctx_stream = np.zeros(len(chain), dtype=np.int64)
        n_ctx = 1
        counts = np.zeros((1, N), dtype=np.float64)
    out = np.zeros(len(chain), dtype=np.float64)
    for k in range(len(chain)):
        emit = int(chain[k])
        ctx = int(ctx_stream[k])
        total = counts[ctx].sum() + alpha * N
        p = (counts[ctx, emit] + alpha) / total
        out[k] = -np.log2(p)
        counts[ctx, emit] += 1
    return out


def rolling_mean(x: np.ndarray, window: int = 64) -> np.ndarray:
    """Centred rolling mean, edges clipped."""
    if len(x) < window:
        return x
    cs = np.cumsum(np.insert(x, 0, 0))
    return (cs[window:] - cs[:-window]) / window


def ascii_plot(name: str, curves: dict, max_pos: int = 2000,
                 height: int = 12) -> None:
    """ASCII rolling cost curves; one row per Sylow-subset size."""
    print(f"=== {name} ===")
    # Find global y range across all curves.
    all_vals = np.concatenate([c[:max_pos] for c in curves.values()])
    y_min = float(all_vals.min())
    y_max = float(all_vals.max())
    print(f"  cost (bits) range: [{y_min:.2f} ... {y_max:.2f}]; "
          f"position 0 → {max_pos} (rolling window=64):")
    for label, curve in curves.items():
        n = min(len(curve), max_pos)
        # Sample 60 columns.
        step = max(1, n // 60)
        idxs = list(range(0, n, step))[:60]
        samples = [curve[i] for i in idxs]
        # Map to height rows.
        bars = []
        for v in samples:
            if y_max > y_min:
                norm = (v - y_min) / (y_max - y_min)
            else:
                norm = 0.5
            row = int(round(norm * (height - 1)))
            bars.append(row)
        # Print top-down.
        print(f"  {label}:")
        for r in range(height - 1, -1, -1):
            line = "    "
            for b in bars:
                line += "█" if b >= r else " "
            # Y-label at left.
            y_val = y_min + (r / (height - 1)) * (y_max - y_min)
            line = f"  {y_val:5.2f}|" + line[2:]
            print(line)
        print(f"        {'-' * 60}")
        print(f"         0{' ' * 26}→{' ' * 26}{max_pos}")
        print()


def main() -> int:
    print("JJ regression-over-time: per-position predictor cost")
    print()
    print("Per user 2026-05-21: 'plot the regression over time'.")
    print("Predicting Gibbs-ringing during warmup, settling to steady-state.")
    print()

    primes_set_1 = [2, 3]            # |S|=2
    primes_set_2 = [2, 3, 5, 7]      # |S|=4
    primes_set_3 = [2, 3, 5, 7, 11, 13]  # |S|=6

    for name, builder in CORPORA.items():
        data = builder(8192)
        chain = chain_symbols(data)

        # Baseline (no context) + three Sylow subsets.
        cost_uni = per_position_cost(chain, [])
        cost_23 = per_position_cost(chain, primes_set_1)
        cost_2357 = per_position_cost(chain, primes_set_2)
        cost_full = per_position_cost(chain, primes_set_3)

        curves = {
            "unigram":      rolling_mean(cost_uni, 64),
            "{2,3}":        rolling_mean(cost_23, 64),
            "{2,3,5,7}":    rolling_mean(cost_2357, 64),
            "{2,3,5,7,11,13}": rolling_mean(cost_full, 64),
        }

        # Print summary numbers: mean of first 100 vs last 1000.
        warmup_end = 64
        steady_start = 500
        print(f"=== {name} ===")
        print(f"  mean cost (bits) by region:")
        print(f"  {'predictor':<22} {'first 64':>10} "
              f"{'pos 500+':>10} {'last 1000':>10}")
        for label, c in [
            ("unigram", cost_uni),
            ("{2,3}", cost_23),
            ("{2,3,5,7}", cost_2357),
            ("{2,3,5,7,11,13}", cost_full),
        ]:
            if len(c) < 1064:
                continue
            r_early = float(c[:warmup_end].mean())
            r_mid = float(c[steady_start:steady_start + 1000].mean())
            r_late = float(c[-1000:].mean())
            print(f"  {label:<22} {r_early:>10.3f} {r_mid:>10.3f} "
                  f"{r_late:>10.3f}")
        print()

        # Save full per-position data to CSV for IDE plotting.
        csv_path = f"/tmp/jj_regression_{name}.csv"
        n = len(chain)
        with open(csv_path, "w") as f:
            f.write("position,unigram,S2_S3,S2to7,S2to13\n")
            for k in range(n):
                f.write(f"{k},{cost_uni[k]:.4f},{cost_23[k]:.4f},"
                        f"{cost_2357[k]:.4f},{cost_full[k]:.4f}\n")
        print(f"  CSV saved: {csv_path}")
        print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
