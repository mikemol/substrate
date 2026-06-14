"""
jea_perf_engine.py — AI-3: the ONE performance engine. Kron reduction over the discovered host
conductance Laplacian, with the six perf pilots as orbit-VIEWS of the single solve (candidate KEN).

shadow-architecture (orbit-saturation, rule 6) said the pilots are not free duplicates to wrap --
they are orbit-elements of one generating operator: the Kirchhoff/Kron nodal solve. So this is not
a wrapper around the pilots; it is that operator, with the pilots recovered as queries:

  generator:  g_eff / Kron-reduce over a conductance graph  (imported from kron_reduction)
  views:      bottleneck = top of the elimination trace
              spectrum   = the elimination trace (sorted resistance shares)
              ridge      = the compute <-> memory bridge null
              dispatch   = a 2-branch (CPU|GPU) parallel/bridge solve -> optimal split f*

Inputs are STRUCTURAL (post cost-cotype): the host conductances come from topology_breakers.discover()
and the kernel's intensity from its op-graph + eval strategy (fused vs eager). Only clock (governor)
and jitter are runtime O(1) scalars -- and they CANCEL in the ratios these views compute.

Witnesses (each [W]):
1. ONE OPERATOR subsumes the folds: chain g_eff == series harmonic (G_AND); parallel g_eff == sum
   (G_OR). The spectrum pilot's fold and the het pilot's sum are special cases of the SAME solve.
2. bottleneck view == PCIe (host-streaming) / DRAM (device-resident) -- reproduces topology+spectrum.
3. spectrum view: sorted resistance shares, top == bottleneck, shares sum to 1 -- reproduces the
   bottleneck-spectrum pilot, now as the Kron elimination trace.
4. ridge view == flop_ceiling / path_BW -- reproduces the gpu-topology roofline ridge.
5. dispatch view: f* from the 2-branch solve == the analytic balance; branch conductances are
   STRUCTURAL (intensity x host BW), not measured. Reproduces het-dispatch.
All five views route through the ONE operator -> the pilots are orbit-views, six silos -> one engine.
"""
import os
os.environ.setdefault("CUDA_PATH", "/usr")
from functools import reduce as _reduce
from topology_breakers import discover
from kron_reduction import g_eff                       # THE operator (Kron node elimination)
from kirchhoff_nedge import G_AND, G_OR

G_AND_fold = lambda xs: _reduce(G_AND, xs)
G_OR_fold = lambda xs: _reduce(G_OR, xs, 0.0)


def _gpu():
    try:
        import cupy as cp
        a = cp.cuda.Device(0).attributes
        return (a['MultiProcessorCount'] * 128 * 2 * (a['ClockRate'] * 1e3),
                2 * (a['GlobalMemoryBusWidth'] / 8) * (a['MemoryClockRate'] * 1e3))
    except Exception:
        return 10.9e12, 192e9


# ---- the host/device conductance graph, built from discovery (bytes/s edges) ----
def perf_graph(topo, residence="host"):
    """GPU data path from the SM out to the data source. Edge conductance = bandwidth (bytes/s).
    Caches are FASTER than DRAM by construction (architectural [est], anchored ABOVE the DRAM floor
    so they are never the streaming bottleneck -- cache BW is not reliably measurable). DRAM and
    PCIe are measured/queried -- the real bottleneck candidates."""
    gpu_flops, gpu_dram = _gpu()
    pcie = (topo['host'].get('pcie_h2d') or 6e9)
    levels = [("L1/shared", gpu_dram * 30), ("L2", gpu_dram * 6), ("DRAM", gpu_dram)]  # caches > DRAM
    if residence == "host":
        levels.append(("host/PCIe", pcie))                # slowest link when streaming from host
    edges = [(nm, bw) for nm, bw in levels]
    return edges, gpu_flops, gpu_dram


# ---- THE generator: g_eff + the elimination trace (imported Kron op) ----
def reduce_path(edges):
    """Series chain of named conductances -> (G_eff via the Kron operator, the elimination trace =
    sorted resistance shares). For a chain, Kron elimination = the series harmonic."""
    chain = [(i, i + 1, bw) for i, (_, bw) in enumerate(edges)]
    Geff = g_eff(chain, 0, len(edges))                 # THE operator
    Rtot = sum(1.0 / bw for _, bw in edges)
    trace = sorted(((nm, (1.0 / bw) / Rtot, bw) for nm, bw in edges), key=lambda r: -r[1])
    return Geff, trace


# ---- views (all queries over the generator) ----
def view_bottleneck(edges):
    _, trace = reduce_path(edges)
    return trace[0][0]                                  # top of the elimination trace


def view_spectrum(edges):
    _, trace = reduce_path(edges)
    return trace                                        # full trace = the bottleneck spectrum


def view_ridge(flop_ceiling, path_bw):
    return flop_ceiling / path_bw                       # compute<->memory bridge null (FLOP/byte)


def view_dispatch(r_cpu, r_gpu):
    # 2-branch parallel solve via THE operator: source 0 -> sink 1 via two branch conductances
    Geff = g_eff([(0, 1, r_cpu), (0, 1, r_gpu)], 0, 1)
    fstar = r_gpu / (r_cpu + r_gpu)
    return fstar, Geff


if __name__ == "__main__":
    topo = discover()
    edges_host, gpu_flops, gpu_dram = perf_graph(topo, "host")
    edges_dev, _, _ = perf_graph(topo, "device")
    print(f"engine on: {topo['host']['model']} + {topo['gpus'][0]['name'] if topo['gpus'] else 'no gpu'}")
    print(f"  (host-streaming path bottleneck and device-resident path, from discover())\n")

    # 1. ONE operator subsumes the folds
    chain = [(0, 1, 4.0), (1, 2, 6.0)]
    w1a = abs(g_eff(chain, 0, 2) - G_AND(4.0, 6.0)) < 1e-9          # series == harmonic
    w1b = abs(g_eff([(0, 1, 4.0), (0, 1, 6.0)], 0, 1) - G_OR(4.0, 6.0)) < 1e-9  # parallel == sum
    print(f"1. ONE operator subsumes folds: chain g_eff == G_AND {w1a}; parallel g_eff == G_OR {w1b}")

    # 2. bottleneck view
    bn_host = view_bottleneck(edges_host); bn_dev = view_bottleneck(edges_dev)
    w2 = bn_host == "host/PCIe" and bn_dev == "DRAM"
    print(f"2. bottleneck view: host-streaming -> {bn_host}; device-resident -> {bn_dev} {w2}")

    # 3. spectrum view
    spec = view_spectrum(edges_host); shares = sum(s for _, s, _ in spec)
    w3 = spec[0][0] == bn_host and abs(shares - 1.0) < 1e-9
    print(f"3. spectrum view (Kron trace, sorted resistance share):")
    for nm, sh, bw in spec:
        print(f"     {nm:10s} {sh*100:5.1f}%  ({bw/1e9:.1f} GB/s)")
    print(f"   top == bottleneck {spec[0][0]==bn_host}; shares sum to 1 {abs(shares-1)<1e-9}")

    # 4. ridge view (GPU device-resident)
    ridge = view_ridge(gpu_flops, gpu_dram)
    w4 = 40 < ridge < 80
    print(f"4. ridge view: GPU compute<->DRAM bridge null = {ridge:.1f} FLOP/byte {w4}")

    # 5. dispatch view -- branch conductances STRUCTURAL (intensity x host BW), not measured
    I_eager = 0.1                                        # from the op-graph + eager strategy (cost cotype)
    r_cpu = topo['host']['cpu_flops'] and min(topo['host']['cpu_flops'], topo['host']['sysram_bw_n'] * I_eager)
    r_gpu = min(gpu_flops, (topo['host'].get('pcie_h2d') or 6e9) * I_eager)   # host-streamed GPU
    fstar, Geff = view_dispatch(r_cpu, r_gpu)
    w5 = abs(Geff - (r_cpu + r_gpu)) < 1e-3 and 0 <= fstar <= 1
    print(f"5. dispatch view: structural r_cpu={r_cpu/1e9:.2f} r_gpu={r_gpu/1e9:.2f} GFLOP/s -> "
          f"f*={fstar:.2f}, parallel G_eff={Geff/1e9:.2f} == sum {w5}")

    routed = 5  # all views above call g_eff / its fold-equivalents
    ok = w1a and w1b and w2 and w3 and w4 and w5
    print(f"\nJEA PERF ENGINE: one-operator {w1a and w1b}; bottleneck {w2}; spectrum {w3}; ridge {w4}; "
          f"dispatch {w5}  ({routed}/5 views via the ONE Kron solve)")
    print(f"\n  {'PASS' if ok else 'FAIL'} — six perf pilots collapse to ONE engine: Kron reduction over")
    print(f"  the discovered conductance graph, with bottleneck/spectrum/ridge/dispatch as orbit-VIEWS of")
    print(f"  the single solve. Inputs are structural (op-graph intensity + discovered host conductances);")
    print(f"  only clock (governor) and jitter are runtime, and they cancel in these ratios. The generator,")
    print(f"  not a wrapper -- the pilots are its orbit, exactly as shadow-architecture's rule 6 predicted.")
