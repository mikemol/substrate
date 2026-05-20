"""Eliza — cleanroom instantiation of agda/Eliza/ contracts in Python.

Each Python module here implements exactly one Agda module's contract.
Cross-module access goes through published interfaces only; no module
reaches into another's internals.

Agda module          → Python module
─────────────────────────────────────
Eliza.Prelude        → (Python built-ins; no module needed)
Eliza.Word           → Python list  (lists ARE Word α; no module needed)
Eliza.Transducer     → eliza.transducer
Eliza.Alphabets      → eliza.alphabets
Eliza.Router         → eliza.router
Eliza.Manifold       → eliza.manifold
Eliza.Trajectory     → eliza.trajectory
Eliza.Orbit          → eliza.orbit
Eliza.Holonomy       → eliza.holonomy
Eliza.Predictor      → eliza.predictor
Eliza.Sequitur       → eliza.sequitur
Eliza.Synthesis      → eliza.synthesis
Eliza.Recorder       → eliza.recorder
Eliza.Engine         → eliza.engine
"""

from eliza.alphabets import Gen, Chamber, Orbit, V4_PERMS, V4_LABELS
from eliza.engine import Engine

__all__ = ["Gen", "Chamber", "Orbit", "V4_PERMS", "V4_LABELS", "Engine"]
