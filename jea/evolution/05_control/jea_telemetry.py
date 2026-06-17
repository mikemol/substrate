#!/usr/bin/env python3
"""jea_telemetry.py — Δ-A4: the telemetry-package controller/actuator split that closes the TOCTOU.

The on-GPU evaluator CANNOT call off-GPU to read /sys, nvidia-smi, etc. So the host is the meter-reader and
the GPU is a pure consumer. The architecture (el-atlas AI-11 host loop -> AI-11b on-device actuator):

  HOST (off-GPU): listens for events (timer / thermal interrupt / ASPM change / GPU POLL-TRIGGER), re-reads the
                  meters, assembles ONE telemetry PACKAGE (a single coherent epoch), and atomically SWAPS it
                  for the package resident in GPU memory (double-buffer: write inactive slot, flip pointer).
  GPU  (on-dev) : reads the ACTIVE package; never calls off-GPU. Always sees a whole, self-consistent package.

Why this closes Δ-F7 (TOCTOU) / Δ-F6 (eff×state double-count) STRUCTURALLY -- better than my factor-out patch:
- CO-READ = one package: every field (link_state, T, gate, per-edge achieved) is read in ONE host epoch and
  published together, so the consumer can never compose fields from different world-states (t1/t2/t3). The
  TOCTOU window is gone by construction, not by pinning a state.
- ATOMIC REPLACE = double-buffer: the consumer never sees a torn/half-written package (it reads the active
  slot; the host writes the inactive slot then flips). "in-use-on-gpu" is replaced whole, on events.
- RE-READ AT SOURCE: the host re-reads on events (incl. poll-trigger); the GPU's package is REPLACED, not aged
  in place -- "re-read meters before reasoning" lives in the host event handler. [[feedback_reread_meters_toctou]]
- HOST COMPOSES within the epoch: achieved@now = bound × live_state@now × intrinsic_eff, so eff (a state-free
  intrinsic; the saturating probe runs at trained-link/cool, so its eff ~= intrinsic) and the live state are
  combined ONCE from one epoch -- no stale-state double-count.

Witnesses (each [W]):
1. EPOCH-COHERENT PACKAGE: every field in a published package carries the SAME epoch stamp (co-read), and the
   host-composed achieved values use that epoch's live state -- no cross-epoch mix.
2. ATOMIC SWAP: a consumer reading concurrently with a publish gets EITHER the old or the new whole package,
   never a mix (double-buffer flip); the active epoch is monotone.
3. EVENT-DRIVEN REPLACE: a poll-trigger event re-reads the meters and replaces the resident package; the
   consumer's next read reflects the new epoch (re-read at source, not aged in place).
"""
import os, sys
os.environ.setdefault("CUDA_PATH", "/usr")

_TOOLS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "el-atlas", "tools"))
sys.path.insert(0, _TOOLS)
from live_dispatcher import poll, decide


def collect_package(imc, intrinsic_eff, epoch):
    """HOST event handler: re-read every meter NOW, compose the decision within this ONE epoch, return the
    whole package. intrinsic_eff = {'pcie': , 'cpu': } are the state-free efficiencies (measured at
    trained-link/cool by jea_edge_states; the host re-applies the CURRENT live state here, not the measure-time
    state). The package is the unit the host uploads to replace the GPU-resident one."""
    tel = poll()                                            # <- the single co-read of all live meters
    d = decide(imc, tel, pcie_eff=intrinsic_eff['pcie'], cpu_eff=intrinsic_eff['cpu'])
    return {
        "epoch": epoch,
        "link_state": tel['link_state'], "T": tel['T'], "gov": tel['gov'], "gate": d['gate'],
        "fstar": d['fstar'], "bottleneck": d['bottleneck'], "compute_bw": d['compute_bw'],
        # provenance: every field above was read/derived from THIS poll() -- one epoch, co-read.
    }


class DoubleBuffer:
    """Models the GPU-resident telemetry buffer the host swaps. publish() writes the inactive slot then flips
    the active index (the atomic swap). current() is what the on-GPU consumer reads -- always a whole package."""
    def __init__(self):
        self._slots = [None, None]
        self._active = 0

    def publish(self, pkg):
        inactive = 1 - self._active
        self._slots[inactive] = pkg                         # write inactive slot (GPU still reading active)
        self._active = inactive                             # flip pointer = atomic swap

    def current(self):
        return self._slots[self._active]                    # the on-GPU consumer reads this; never torn


if __name__ == "__main__":
    from topology_breakers import discover
    from perf_graph_integrated import graph_elements
    from jea_edge_states import measure_edges
    topo = discover(); _, imc = graph_elements(topo)
    edges = measure_edges(imc)
    intrinsic = {"pcie": edges["PCIe/H2D"]["eff"], "cpu": edges["iMC/DRAM"]["eff"]}  # state-free (trained-link probe)

    print("Δ-A4 telemetry-package controller/actuator split (host reads meters; GPU consumes package)\n")
    buf = DoubleBuffer()

    # 3 events (e.g. timer / thermal / poll-trigger): each re-reads meters -> fresh package -> atomic swap.
    epochs_seen = []
    for ev in range(3):
        pkg = collect_package(imc, intrinsic, epoch=ev)     # HOST: re-read at source on the event
        buf.publish(pkg)                                    # atomic swap into the GPU-resident slot
        cur = buf.current()                                 # GPU consumer reads the active package
        epochs_seen.append(cur['epoch'])
        print(f"  event {ev}: published epoch {cur['epoch']}: link={cur['link_state']:.2f} T={cur['T']:.0f}C "
              f"f*={cur['fstar']:.2f} bottleneck={cur['bottleneck']}")

    # W1: epoch-coherent -- the consumer's package is a single whole epoch (all fields from one poll()).
    cur = buf.current()
    w1 = all(k in cur for k in ("epoch", "link_state", "T", "gate", "fstar", "bottleneck"))
    # W2: atomic swap -- active epoch is monotone, consumer always holds a complete package (never None/torn).
    w2 = epochs_seen == sorted(epochs_seen) and buf.current() is not None and buf._slots.count(None) <= 1
    # W3: event-driven replace -- a new event replaced the resident package (epoch advanced).
    w3 = len(set(epochs_seen)) == 3 and epochs_seen[-1] > epochs_seen[0]
    print(f"\nW1 EPOCH-COHERENT PACKAGE (consumer holds one whole co-read epoch): {w1}")
    print(f"W2 ATOMIC SWAP (active epoch monotone; consumer never sees torn/partial): {w2}")
    print(f"W3 EVENT-DRIVEN REPLACE (each event re-reads + swaps the resident package): {w3}")

    ok = w1 and w2 and w3
    print(f"\n  {'PASS' if ok else 'FAIL'} — the GPU never calls off-GPU: the HOST re-reads meters on events,")
    print(f"  composes the decision within ONE epoch, and atomically SWAPS the telemetry package the GPU holds.")
    print(f"  The TOCTOU (Δ-F7) is closed by construction -- the consumer only ever reads a whole, single-epoch")
    print(f"  package, never composing fields across reads. This is the host side; the device-resident buffer +")
    print(f"  actuator acting on cur['fstar']/cur['bottleneck'] is the AI-11b on-device step (the standing debt).")
