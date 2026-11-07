# Changes in this copy

1. **Heap-buffer-overflow fixed** (`VocalProcessor::processInterleaved`): scratch buffers hold 65,536 frames and were
   indexed with no bound, so any interleaved block of 65,537+ frames wrote past the end (confirmed with AddressSanitizer).
   It now processes in 65,536-frame chunks.
2. **Soft clipper discontinuity fixed**: `0.9*tanh(x/0.9)` above |x| > 0.9 made the output jump from 0.9 to 0.685 at the
   threshold (about -30 dBc of non-harmonic splatter once the stage engages). Now `0.9 + 0.1*tanh((|x|-0.9)/0.1)`,
   continuous with matching slope; the ceiling is 1.0 instead of 0.9.
3. Two new self-tests for the above (the soft-clip test fails on the old code: step 0.193 vs 0.046 unclipped).
4. Removed the committed binaries (`libvocalhifi.so`, `vocal_hifi_selftest`); build from source.
5. `tools/ds_probe.py` + `tools/ds_wrap.cpp`: measurement harness for DolbyStretch (gain law, THD, flatness).

## Not changed (findings)
- `DolbyStretch::Params::stretch` is never set from `Settings`, so the non-stretch branch is unreachable.
- The C ABI and `vp_load_preset` ignore most preset keys (`dolbyStretch`, `compRatio`, `adt*`, `notchDb`, `breathAmount`).
- DolbyStretch boosts quiet signal (upward compression), not "upward expansion"; at the defaults it is -0.5 dB when loud.
- Below 100 Hz its gain modulation produces THD of about -41 to -45 dBc.
