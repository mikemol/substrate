"""CLI entry point for the cleanroom eliza pipeline.

Modes:
  python run.py                            # smoke (pangram 4×)
  python run.py path/to/file.txt           # text file → CLI summary
  python run.py path/to/file.txt --ui      # text file → dashboard
  python run.py path/to/file.bin --binary  # binary file
  python run.py --stdin --binary           # raw bytes from stdin (e.g. ffmpeg pipe)
  python run.py path --compress            # CLI compression-rate report

Persists to scratch/eliza/state/state.db by default; override with
ELIZA_STATE_DIR.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

# Allow running as `python run.py` from scratch/eliza/.
sys.path.insert(0, str(Path(__file__).parent))

from eliza.engine import Engine
from eliza.manifold import word_str
from eliza.recorder import DEFAULT_DB, Store


def _open_input(args):
    """Return an iterator yielding 1-char strings.

    Modes:
      * Default: read characters from text file or stdin.
      * --binary: read bytes; each byte → chr(byte) (1-char string).
      * --bits:   read bytes; each byte → 8 bit-chars ('0' or '1', MSB first).
                  This is the substrate-honest F₂-native mode for bitstreams.
    """
    if args.bits:
        if args.stdin:
            raw = sys.stdin.buffer
        else:
            raw = open(args.path, "rb")
        def gen():
            while True:
                b = raw.read(4096)
                if not b:
                    if not args.stdin:
                        raw.close()
                    return
                for byte in b:
                    for i in range(8):
                        yield "1" if (byte >> (7 - i)) & 1 else "0"
        return gen()
    if args.nibbles:
        if args.stdin:
            raw = sys.stdin.buffer
        else:
            raw = open(args.path, "rb")
        def gen():
            while True:
                b = raw.read(4096)
                if not b:
                    if not args.stdin:
                        raw.close()
                    return
                for byte in b:
                    yield chr((byte >> 4) & 0xF)   # high nibble first
                    yield chr(byte & 0xF)          # low nibble
        return gen()
    if args.crumbs:
        if args.stdin:
            raw = sys.stdin.buffer
        else:
            raw = open(args.path, "rb")
        # Sliding window stride 1: every bit slides one bit further, emitting
        # a 2-bit crumb (last bit, new bit). N input bits → N-1 crumbs, each
        # sharing 1 bit with its neighbour. This protects tile edges — any
        # 2-bit pattern at any bit-offset becomes a crumb, regardless of
        # byte alignment. The grammar lifts 4-bit (stride 2 implicit) by
        # absorbing pairs of consecutive overlapping crumbs.
        def gen():
            prev_bit = None
            while True:
                b = raw.read(4096)
                if not b:
                    if not args.stdin:
                        raw.close()
                    return
                for byte in b:
                    for i in range(8):  # MSB first
                        bit = (byte >> (7 - i)) & 1
                        if prev_bit is not None:
                            yield chr((prev_bit << 1) | bit)
                        prev_bit = bit
        return gen()
    if args.stdin:
        if args.binary:
            def gen():
                while True:
                    b = sys.stdin.buffer.read(1)
                    if not b:
                        return
                    yield chr(b[0])
            return gen()
        return iter(lambda: sys.stdin.read(1), "")
    if args.binary:
        f = open(args.path, "rb")
        def gen():
            while True:
                b = f.read(1)
                if not b:
                    f.close()
                    return
                yield chr(b[0])
        return gen()
    f = open(args.path, "r", encoding="utf-8", errors="replace")
    return iter(lambda: f.read(1), "")


def _compress_mode(engine: Engine, source, *, report_every: int = 50_000) -> None:
    """Stream the source, print compression stats every report_every bytes."""
    import time

    start = time.time()
    last_report = 0
    n = 0
    for ch in source:
        engine.step(ch)
        n += 1
        if n - last_report >= report_every:
            stats = engine.compression_stats()
            elapsed = time.time() - start
            rate = n / elapsed if elapsed > 0 else 0
            cycle = stats['orbit_cycling_rate']
            cycle_bar = "█" * int(cycle * 10)
            print(
                f"[{n:>10,} sym]  "
                f"tri {stats['ratio']:.2f}×  "
                f"gt {stats['gt_ratio']:.2f}×  "
                f"gt6 {stats['gt6_ratio']:.2f}×  "
                f"v4a {stats['gtV4a_ratio']:.2f}×  "
                f"v4d {stats['gtV4d_ratio']:.2f}×  "
                f"coa {stats['coalg_slot_ratio']:.2f}×* "
                f"geo {stats['geo_ratio']:.2f}×  "
                f"cyc {cycle:.2f} {cycle_bar:<8} "
                f"rules={stats['grammar_n_rules']:>4} "
                f"({rate:,.0f}/s)"
            )
            last_report = n
    stats = engine.compression_stats()
    print(
        f"\nfinal: {n:,} symbols  raw={stats['raw_bits_per_symbol']:.1f} bits/sym\n"
        f"  trigram (raw alphabet, 2-symbol context):\n"
        f"    {stats['compressed_bits']:,.0f} bits "
        f"({stats['bits_per_symbol']:.3f} b/s, ratio {stats['ratio']:.2f}×)\n"
        f"  grammar (sum of rule body sizes × log₂(alphabet + n_rules)):\n"
        f"    {stats['grammar_total_bits']:,.0f} bits "
        f"({stats['grammar_bits_per_symbol']:.3f} b/s, "
        f"ratio {stats['grammar_ratio']:.2f}×, "
        f"{stats['grammar_n_rules']} rules)\n"
        f"  grammar-trigram (Markov over production rules):\n"
        f"    {stats['gt_total_bits']:,.0f} bits "
        f"({stats['gt_bits_per_symbol']:.3f} b/s, ratio {stats['gt_ratio']:.2f}×)\n"
        f"  orbit-indexed gram-tri (S₃ orientation: gt + current orbit):\n"
        f"    {stats['gt6_total_bits']:,.0f} bits "
        f"({stats['gt6_bits_per_symbol']:.3f} b/s, ratio {stats['gt6_ratio']:.2f}×)\n"
        f"  V₄-tetrad gram-tri, absolute (slot = orbit_now · V₄[i mod 4]):\n"
        f"    {stats['gtV4a_total_bits']:,.0f} bits "
        f"({stats['gtV4a_bits_per_symbol']:.3f} b/s, ratio {stats['gtV4a_ratio']:.2f}×)\n"
        f"  V₄-tetrad gram-tri, delta (slot = orbit_now·frame⁻¹ · V₄[i mod 4]):\n"
        f"    {stats['gtV4d_total_bits']:,.0f} bits "
        f"({stats['gtV4d_bits_per_symbol']:.3f} b/s, ratio {stats['gtV4d_ratio']:.2f}×)\n"
        f"  coalgebraic codec (gt over V₄ slot stream — LOSSY projection):\n"
        f"    {stats['coalg_total_bits']:,.0f} bits "
        f"({stats['coalg_bits_per_slot']:.3f} b/slot, "
        f"slot-ratio {stats['coalg_slot_ratio']:.2f}×, "
        f"{stats['coalg_n_contexts']} contexts)\n"
        f"    (compresses slot stream only; lossless input encoding needs\n"
        f"     a residual codec for (input_symbol | slot), not yet built)\n"
        f"  orbit cycling rate (power-weighted, top-rule-item scale):\n"
        f"    {stats['orbit_cycling_rate']:.3f} "
        f"(per-char cycling is structurally 1.0; item-scale shows grammar absorption)\n"
        f"  huffman (marginal, no context):\n"
        f"    {stats['huffman_total_bits']:,.0f} bits "
        f"({stats['huffman_bits_per_symbol']:.3f} b/s, "
        f"ratio {stats['huffman_ratio']:.2f}×)\n"
        f"  orbit-huffman (SPPF rotated per V₄-coset; orbit-hot codes shallow):\n"
        f"    {stats['orbit_huffman_total_bits']:,.0f} bits "
        f"({stats['orbit_huffman_bits_per_symbol']:.3f} b/s, "
        f"ratio {stats['orbit_huffman_ratio']:.2f}×)\n"
        f"    per-orbit bits: "
        + "  ".join(
            f"{o}={b}" for o, b in
            sorted(stats['orbit_huffman_per_orbit'].items(), key=lambda kv: -kv[1])
        ) + "\n"
        f"  geo-sppf (Walsh-Hadamard cells, 4-bit address + within-cell bits):\n"
        f"    {stats['geo_total_bits']:,.0f} bits "
        f"({stats['geo_bits_per_symbol']:.3f} b/s, "
        f"ratio {stats['geo_ratio']:.2f}×, "
        f"{stats['geo_n_rules']} rules)\n"
        f"    cell population: "
        + "  ".join(
            f"{c:04b}={n}" for c, n in
            sorted(stats['geo_cell_population'].items(), key=lambda kv: -kv[1])
            if n > 0
        )
    )


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="?", help="Text/binary file to stream (omit for smoke)")
    parser.add_argument("--no-persist", action="store_true")
    parser.add_argument("--quiet", action="store_true")
    parser.add_argument(
        "--grammar-every",
        type=int,
        default=1,
        help="Feed every N-th symbol into the Sequitur grammars. 0 disables.",
    )
    parser.add_argument(
        "--binary",
        action="store_true",
        help="Treat input as raw bytes (vocab=256). Each byte → chr(byte).",
    )
    parser.add_argument(
        "--bits",
        action="store_true",
        help="Treat input as a bitstream (vocab=2, F₂-native). Each byte "
             "expands to 8 bit-chars '0'/'1'. The substrate-honest mode "
             "for binary compression analysis.",
    )
    parser.add_argument(
        "--nibbles",
        action="store_true",
        help="Read input as 4-bit nibbles (vocab=16). Each byte → two "
             "chr(nibble) (high then low). Each nibble drives a "
             "quaternion-shaped chamber step (V₄ × S₃-involution); the "
             "chamber walks the full S₄, not the S₃ subgroup --bits "
             "is restricted to.",
    )
    parser.add_argument(
        "--crumbs",
        action="store_true",
        help="Read input as 2-bit SLIDING window crumbs (vocab=4, V₄ ≅ F₂²; "
             "stride 1, overlap 1 bit). N input bits → N-1 crumbs, each "
             "sharing 1 bit with neighbour. Protects tile edges: any "
             "2-bit pattern at any bit-offset becomes a crumb regardless "
             "of byte alignment. Each crumb drives a pure V₄ chamber "
             "step; higher-order structure is discovered by the grammar "
             "bottom-up. The substrate-natural primitive.",
    )
    parser.add_argument(
        "--stdin",
        action="store_true",
        help="Read from stdin instead of a file. Pair with --binary for pipes.",
    )
    parser.add_argument(
        "--compress",
        action="store_true",
        help="CLI compression-rate report mode (no UI, no per-symbol output).",
    )
    parser.add_argument(
        "--ui",
        action="store_true",
        help="Launch the Textual dashboard.",
    )
    parser.add_argument(
        "--rate",
        type=float,
        default=20.0,
        help="Chars/sec when streaming a file under --ui.",
    )
    args = parser.parse_args(argv)

    # Compress mode drops SQLite (irrelevant to compression) but KEEPS the
    # grammar — the SPPF's accumulated structure IS the long-range capture
    # the trigram alone can't do. User can pass --grammar-every 0 to disable.
    no_persist = args.no_persist or args.compress
    grammar_every = args.grammar_every
    state_dir = Path(os.environ.get(
        "ELIZA_STATE_DIR", Path(__file__).parent / "state"
    ))
    store = None if no_persist else Store(state_dir / DEFAULT_DB)
    if args.crumbs:
        vocab_size = 4
    elif args.nibbles:
        vocab_size = 16
    elif args.bits:
        vocab_size = 2
    elif args.binary:
        vocab_size = 256
    else:
        vocab_size = 128
    if args.crumbs:
        from eliza.router import crumb as crumb_router
        # v4_canonicalize on sliding-stride-1 crumbs is structurally
        # redundant with the sliding window's bit-overlap (slice-8 finding):
        # the window already correlates consecutive crumbs through V₄, so
        # explicit canonicalization just adds dispersion. Available via
        # the Engine flag for other modes / future experiments.
        engine = Engine(
            store=store,
            router=crumb_router,
            grammar_every=grammar_every,
            vocab_size=vocab_size,
            v4_canonicalize=False,
        )
    elif args.nibbles:
        from eliza.router import nibble as nibble_router
        engine = Engine(
            store=store,
            router=nibble_router,
            grammar_every=grammar_every,
            vocab_size=vocab_size,
        )
    else:
        engine = Engine(
            store=store,
            grammar_every=grammar_every,
            vocab_size=vocab_size,
        )

    try:
        # Smoke mode: no path and no stdin.
        if args.path is None and not args.stdin:
            text = "the quick brown fox jumps over the lazy dog. " * 4
            for ch in text:
                engine.step(ch)
            here = engine.current_chamber
            info = engine.cocycle.info(here)
            stats = engine.compression_stats()
            print(
                f"final chamber: {word_str(engine.manifold.shortlex_word(here))} "
                f"({info.chirality.name}, fiber {info.fiber_label})"
            )
            print(
                f"trigram contexts={engine.predictor.n_contexts()} "
                f"obs={engine.predictor.n_observations()}"
            )
            print(
                f"compression: {stats['bits_per_symbol']:.2f} bits/sym, "
                f"ratio {stats['ratio']:.2f}× vs raw "
                f"{stats['raw_bits_per_symbol']:.1f}"
            )
            print(f"char-grammar: {engine.grammar_char.n_rules()} rules")
            print(f"orbit-grammar: {engine.grammar_orbit.n_rules()} rules")
            return

        if args.ui:
            from eliza.ui import build_app
            # UI keeps its own ticker loop; pass a file source if given.
            source_file = (
                open(args.path, "rb" if args.binary else "r",
                     **({} if args.binary else {"encoding": "utf-8", "errors": "replace"}))
                if args.path else None
            )
            # For binary UI: wrap source to yield 1-char strings via chr().
            if args.binary and source_file is not None:
                class _BinAdapter:
                    def __init__(self, f): self.f = f
                    def read(self, n):
                        b = self.f.read(n)
                        return "".join(chr(x) for x in b) if b else ""
                    def close(self): self.f.close()
                source = _BinAdapter(source_file)
            else:
                source = source_file
            app = build_app(engine, source=source, rate=args.rate)
            try:
                app.run()
            finally:
                if source is not None:
                    source.close()
            return

        # CLI mode: stream + print.
        source = _open_input(args)
        if args.compress:
            _compress_mode(engine, source)
            return

        # Per-symbol verbose CLI.
        for ch in source:
            r = engine.step(ch)
            if not args.quiet:
                surp = f"  surp={r.surprise:.2f}" if r.surprise is not None else ""
                print(
                    f"[{r.orbit_to:>14}] {r.char!r} -> {r.chamber_to_word}  "
                    f"κ={r.holonomy.curvature:.3f}{surp}"
                )
        stats = engine.compression_stats()
        print(
            f"\nfinal chamber: "
            f"{word_str(engine.manifold.shortlex_word(engine.current_chamber))}"
        )
        print(
            f"compression: {stats['bits_per_symbol']:.2f} bits/sym, "
            f"ratio {stats['ratio']:.2f}× vs raw "
            f"{stats['raw_bits_per_symbol']:.1f}"
        )
        print(f"char-grammar: {engine.grammar_char.n_rules()} rules")
        print(f"orbit-grammar: {engine.grammar_orbit.n_rules()} rules")
    finally:
        engine.end()


if __name__ == "__main__":
    main(sys.argv[1:])
