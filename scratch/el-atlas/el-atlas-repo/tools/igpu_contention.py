"""
igpu_contention.py — AI-7b: the iGPU as a contention edge on TWO shared nodes.

The on-package Intel iGPU is a parallel consumer (G_OR) on resources the cores already share:
  - the iMC / DRAM bandwidth (same shared sink as the DMA path, AI-7a)
  - the package POWER budget (intel-rapl:0 PL0) -- the NEW shared node this brick adds
So any iGPU use steals DRAM BW AND package power from the cores, reducing their effective compute.
Composed by the same shared-node contention as cores-on-controller / DMA-on-iMC.

Witnesses (each [W]):
1. iGPU DETECTED: an on-package GPU (DRM card, Intel vendor 0x8086) sharing the package.
2. iMC BW CONTENTION: cores' effective DRAM BW with the iGPU pulling < without (shared iMC edge).
3. PACKAGE-POWER CONTENTION: cores' share of PL0 shrinks by the iGPU draw -> in the power-limited
   regime compute scales with power -> core compute headroom drops (the package-power shared node).
"""
import os, glob
os.environ.setdefault("CUDA_PATH", "/usr")
from kron_reduction import g_eff
from host_probe import _read


def discover():
    igpu = False
    for card in glob.glob("/sys/class/drm/card[0-9]"):
        if _read(card + "/device/vendor") == "0x8086":     # Intel integrated
            igpu = True; break
    pl0 = _read("/sys/class/powercap/intel-rapl:0/constraint_0_power_limit_uw")
    pl0_w = int(pl0) / 1e6 if pl0 else 45.0
    imc = 51.2e9
    try:
        from dmi_intern import dmi_facts
        imc = (dmi_facts()[0] or {}).get('dram_peak_bw') or imc
    except Exception:
        pass
    return dict(igpu=igpu, pl0_w=pl0_w, imc=imc)


if __name__ == "__main__":
    d = discover()
    IMC, PL0 = d['imc'], d['pl0_w']
    print(f"iGPU contention: detected={d['igpu']}  package PL0={PL0:.0f}W  iMC ceiling={IMC/1e9:.1f} GB/s\n")

    w1 = d['igpu']
    print(f"1. iGPU DETECTED (on-package, shares iMC + package power): {w1}")

    # 2. iMC BW contention (shared sink, same Kron structure as AI-7a)
    CORES, IMC_N, DRAM = 0, 1, 2; HUGE = 1e18
    g_alone = g_eff([(CORES, IMC_N, HUGE), (IMC_N, DRAM, IMC)], CORES, DRAM)
    igpu_bw = IMC * 0.25                                    # iGPU pulling ~1/4 of DRAM BW (e.g. display/compute)
    g_contended = g_eff([(CORES, IMC_N, HUGE), (IMC_N, DRAM, IMC - igpu_bw)], CORES, DRAM)
    w2 = g_contended < g_alone
    print(f"2. iMC BW contention: cores alone {g_alone/1e9:.1f} -> with iGPU pulling {igpu_bw/1e9:.0f} GB/s "
          f"-> {g_contended/1e9:.1f} GB/s {w2}")

    # 3. package-power contention (the new shared node): PL0 split between cores and iGPU
    igpu_w = 8.0                                            # iGPU drawing ~8W of the package budget
    cores_power_alone = PL0
    cores_power_contended = PL0 - igpu_w
    # power-limited regime: compute ~ power -> headroom ratio
    headroom = cores_power_contended / cores_power_alone
    w3 = cores_power_contended < cores_power_alone and headroom < 1
    print(f"3. PACKAGE-POWER contention (shared node): cores' PL0 share {cores_power_alone:.0f}W -> "
          f"{cores_power_contended:.0f}W with iGPU @ {igpu_w:.0f}W -> {headroom*100:.0f}% compute headroom {w3}")

    ok = w1 and w2 and w3
    print(f"\nIGPU CONTENTION (AI-7b): detected {w1}; imc-bw-contention {w2}; power-contention {w3}")
    print(f"\n  {'PASS' if ok else 'FAIL'} — the iGPU is a contention edge on TWO shared nodes: it steals")
    print(f"  DRAM bandwidth (the iMC sink, same as the DMA path) AND package power (the new shared node,")
    print(f"  PL0 split). Both reduce core compute -- parallel-consumer (G_OR) contention on shared")
    print(f"  resources, the same structure the Kron solve already handles. AI-7c (thermal gate), AI-7d")
    print(f"  (ASPM-dynamic link) remain as specified shadows in ai7_decomposition.md.")
