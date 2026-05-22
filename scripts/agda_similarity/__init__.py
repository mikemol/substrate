"""agda_similarity — multi-scale similarity, template extraction, and
skeleton construction over Agda files.

Submodules:
  tokenize    — Agda-aware tokenizers + comment-stripping at four scales
                (char3, token, line, block).
  similarity  — cosine similarity per scale + geometric-mean composition.
  template    — per-scale skeleton/holes extraction + recursive variant
                (coarse-to-fine drill-down into per-file holes).
  skeleton    — parametric-template construction by substituting per-file
                residue tokens with a hole marker.
  cli         — argparse driver + mode dispatch.

Entry point: scripts/agda_similarity.py shims through to cli.main().
"""
