"""tests/test_substrate_atlas.py — Y-arc substrate self-application.

Each cell is one (corpus × mode) measurement of V7. The matrix
aggregates into the Substrate Compression Atlas: empirical evidence
of how well V7's predictor ring aligns with substrate-internal
structural data.

Per the DBE pass on the Y-arc:
  costructure: MeasurementCell = (corpus_constructor, predictor_binding,
                                    identity_bpb, speculate_bpb,
                                    n_switches, ok).
  composition: aggregate cells into per-corpus table; reveal which
               structural classes V7's predictors capture.
  entailment:  cells with speculate < identity witness structural
               axes the substrate's predictor ring captures on that
               corpus.

Per [[homology-cohomology-recursion]] and [[tetrative-metacircularity]]:
substrate-internal data SHOULD compress better than random data under
V7 because the codec's predictor ring is built from substrate-native
primitives.

Per [[negative-findings-corpus-bound]]: each cell is a bounded
measurement; no overclaim from absence to structural property.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))

from eliza.gpu_codec_v7 import encode, decode    # noqa: E402


SUBSTRATE_ROOT = Path("/home/mikemol/github/substrate")
MEMORY_ROOT = Path(
    "/home/mikemol/.claude/projects/-home-mikemol-github-substrate/memory"
)


# --- Corpus constructors ------------------------------------------------


def substrate_agda(n_bytes: int = 4096) -> bytes:
    """Y2: concatenated Agda source from agda/Substrate/**/*.agda.

    Deterministic order (sorted paths). Truncated to n_bytes.
    """
    files = sorted((SUBSTRATE_ROOT / "agda" / "Substrate").rglob("*.agda"))
    out = bytearray()
    for f in files:
        if len(out) >= n_bytes:
            break
        try:
            out.extend(f.read_bytes())
        except OSError:
            continue
    return bytes(out[:n_bytes])


def substrate_memory(n_bytes: int = 4096) -> bytes:
    """Y3: concatenated memory entries (excluding MEMORY.md which would
    self-reference).
    """
    files = sorted(p for p in MEMORY_ROOT.glob("*.md") if p.name != "MEMORY.md")
    out = bytearray()
    for f in files:
        if len(out) >= n_bytes:
            break
        try:
            out.extend(f.read_bytes())
        except OSError:
            continue
    return bytes(out[:n_bytes])


def substrate_opcodes(n_bytes: int = 4096) -> bytes:
    """Y4: substrate's initial opcode-body table serialised as bytes.

    Codec compressing its own opcode-source = recursive-coupling test
    per [[tetrative-metacircularity]]. The bodies are V₄ × S₃
    permutations — pure substrate structure, no extraneous content.
    """
    from eliza.opcode_set import build_full_opcode_set
    from eliza.matrix_ops import _manifold_index

    _, idx_map = _manifold_index()
    ops = build_full_opcode_set()
    out = bytearray()
    for op in ops:
        for cs in op.body:
            out.append(idx_map[cs.to_s4()] & 0xFF)
    # Repeat the seed until reaching n_bytes (the opcode set is small).
    while len(out) < n_bytes:
        out.extend(out)
    return bytes(out[:n_bytes])


CORPORA = {
    "substrate_agda":     substrate_agda,
    "substrate_memory":   substrate_memory,
    "substrate_opcodes":  substrate_opcodes,
}


# --- Measurement cell ---------------------------------------------------


@dataclass
class MeasurementCell:
    corpus: str
    mode: str
    bpb: float
    n_switches: int
    ok: bool
    delta_vs_identity: float = 0.0
    encode_ms: float = 0.0


MODES = [
    ("identity",   False),
    ("two-stage",  True),
]


def measure(corpus_name: str, corpus_data: bytes) -> List[MeasurementCell]:
    """Run V7 identity + two-stage on a single corpus; return cells."""
    import time
    cells: List[MeasurementCell] = []
    base_bpb = None
    for mode_name, flag in MODES:
        t0 = time.perf_counter()
        try:
            enc, stats = encode(corpus_data, speculate_basis=flag)
            elapsed_ms = (time.perf_counter() - t0) * 1000
            dec = decode(enc)
            ok = dec == corpus_data
            bpb = 8 * len(enc) / len(corpus_data)
        except Exception:
            elapsed_ms = (time.perf_counter() - t0) * 1000
            ok = False
            bpb = -1.0
            stats = {"n_basis_at": 0}
        if base_bpb is None:
            base_bpb = bpb
        delta = bpb - base_bpb if base_bpb > 0 else 0.0
        cells.append(MeasurementCell(
            corpus=corpus_name, mode=mode_name, bpb=bpb,
            n_switches=stats.get("n_basis_at", 0), ok=ok,
            delta_vs_identity=delta, encode_ms=elapsed_ms,
        ))
    return cells


# --- Atlas sweep --------------------------------------------------------


def main(size: int = 4096) -> int:
    print(f"=== Substrate Compression Atlas — {size}B per corpus ===\n")
    print(f"{'corpus':<22}{'mode':<14}{'b/byte':>9}  {'Δ':>7}  "
          f"{'switches':>9}  {'encode ms':>10}  {'ok':>5}")

    all_cells: List[MeasurementCell] = []
    for name, ctor in CORPORA.items():
        data = ctor(n_bytes=size)
        actual_size = len(data)
        for cell in measure(name, data):
            v = ("B" if cell.delta_vs_identity < -0.01 else
                 "R" if cell.delta_vs_identity > 0.01 else "=")
            print(f"{name:<22}{cell.mode:<14}{cell.bpb:>8.3f}{v}  "
                  f"{cell.delta_vs_identity:>+7.3f}  "
                  f"{cell.n_switches:>9}  {cell.encode_ms:>9.0f}ms  "
                  f"{'OK' if cell.ok else 'FAIL':>5}")
            all_cells.append(cell)
        print()

    wins = [c for c in all_cells if c.delta_vs_identity < -0.01]
    print(f"BENEFITS observed: {len(wins)} cells "
          f"out of {len(all_cells)} total.")
    for c in wins:
        print(f"  {c.corpus} / {c.mode}: "
              f"{c.delta_vs_identity:+.3f} b/byte")
    return 0


if __name__ == "__main__":
    sys.exit(main())
