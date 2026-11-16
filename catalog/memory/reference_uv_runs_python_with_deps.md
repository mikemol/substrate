---
name: reference-uv-runs-python-with-deps
description: "the box has no pip in the .venv, but `uv` runs Python with deps injected on the fly — `uv run --with <pkg> python3 …` (e.g. protobuf / the OTLP exporter); don't hand-roll or fall back when a lib is 'missing'"
metadata:
  node_type: memory
  type: reference
  originSessionId: d35bc15a-16b8-42c5-aad1-20966c9a9f8e
  modified: 2026-07-23T20:19:05.524Z
---

The project `.venv` python has **NO pip** (`No module named 'pip'`), so `python3 -c "import X"` fails for
anything not already vendored (protobuf, opentelemetry, numpy-if-not-in-venv, …). **Do not conclude "the lib
is unavailable" and hand-roll a fragile substitute or route around it** — that was my mistake once (I proposed
hand-encoding OTLP protobuf / a native-import fallback because "no pip, no protobuf lib").

**`uv` (0.11.12+) runs Python with deps fetched on the fly, cached:**
```sh
uv run --with opentelemetry-sdk --with opentelemetry-exporter-otlp-proto-http python3 <script.py>
uv run --with protobuf python3 -c "import google.protobuf; print(google.protobuf.__version__)"
```
`--with <pkg>` (repeatable) installs into an ephemeral env for that run (14 packages in ~21ms when cached).
So the OTLP proto-http exporter, protobuf, and any PyPI dep are one flag away. This IS the
[[feedback_fix_infra_not_route_around]] move for "missing" Python deps: reach the proper library via `uv`,
don't build a shim. Tell: I'm about to write "the lib isn't installed, so I'll hand-encode / use a simpler
path" — instead try `uv run --with <lib>` first.
